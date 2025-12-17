import asyncio
from llama_cpp import Llama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
from typing import List, Dict
import re as regex
import json
from httpx import AsyncClient
from datetime import datetime, timezone
import os

FASTAPI_BASE_URL = os.getenv("FASTAPI_URL", "http://back:8000/api")


class RetailInventoryAgent:
    """LLM Agent with MCP tools for retail inventory management."""

    def __init__(self, model_path: str):
        print(f"[Agent] Loading model from {model_path}")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=8192,
            n_threads=8,
            n_gpu_layers=0,
            verbose=False,
        )
        print("[Agent] Model loaded successfully")

    async def _save_to_history(self, response: str, history_type: str):
        """Save agent interaction to history."""
        try:
            async with AsyncClient() as client:
                history_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "response": response,
                    "type": history_type
                }
                await client.post(f"{FASTAPI_BASE_URL}/agent", json=history_data)
        except Exception as e:
            print(f"[History] Error saving to history: {e}")

    def _clean_response(self, text: str) -> str:
        """Remove TOOL_CALL lines from response text."""
        import re
        # Remove any line that contains TOOL_CALL or looks like a function call
        lines = text.split('\n')
        cleaned_lines = [
            line for line in lines
            if 'TOOL_CALL:' not in line and not re.match(r'^\s*[a-zA-Z_]\w*\(.*\)\s*$', line)
        ]
        cleaned = '\n'.join(cleaned_lines)
        # Remove [DONE] marker
        cleaned = cleaned.replace("[DONE]", "")
        # Remove extra blank lines
        cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)
        return cleaned.strip()

    async def run_with_tools(self, user_query: str, history: List[Dict] = None) -> str:
        """Run the agent with access to MCP tools."""
        print(f"\n[Agent] User query: {user_query}")

        if history:
            print(f"[Agent] Conversation history ({len(history)} items):")
            for idx, item in enumerate(history):
                print(f"  [{idx+1}] Q: {item['query'][:80]}...")
                print(f"      A: {item['response'][:80]}...")
        else:
            print("[Agent] No conversation history")

        server_params = StdioServerParameters(
            command="python",
            args=["mcp/server.py"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_response = await session.list_tools()
                available_tools = [t.name for t in tools_response.tools]

                print(f"[Agent] Available tools: {available_tools}")

                system_prompt = self._build_system_prompt(tools_response.tools)

                # Track all tool results for context
                tool_results_context = []

                # Allow up to 5 tool calls in a chain
                max_iterations = 20
                current_iteration = 0
                current_response = None

                while current_iteration < max_iterations:
                    # Build prompt with history and tool results
                    if current_iteration == 0:
                        # First iteration: merge system prompt with user query for better reasoning
                        full_prompt = f"""{system_prompt}

Task: {user_query}

Think step-by-step:
1. What information do I need to gather first?
2. What tools should I call to get that information?
3. Once I have the data, what actions should I take?

Explain your action then call the appropriate tool(s):
Assistant:"""
                    else:
                        # Add tool results to prompt
                        full_prompt = self._build_prompt_with_history(system_prompt, history, user_query)
                        for tool_ctx in tool_results_context:
                            full_prompt += f"\n\n[Tool {tool_ctx['name']} returned]:\n{tool_ctx['result']}"
                        full_prompt += "\n\nBased on this data, decide if you need to call another tool or provide a final answer:\n\nAssistant:"

                    print(f"[Agent] Generating response (iteration {current_iteration + 1})...")
                    response = self.llm(
                        full_prompt,
                        max_tokens=1024,
                        temperature=0.7,
                        stop=["User:", "\n\n"],
                    )

                    current_response = response['choices'][0]['text'].strip()
                    print(f"[Agent] LLM Response: {current_response}")

                    # Parse all tool calls from the response FIRST
                    tool_calls = self._parse_tool_calls(current_response)

                    # Check if agent signaled completion (only after checking for tool calls)
                    if "[DONE]" in current_response:
                        # If there are tool calls, execute them first before marking as done
                        if tool_calls:
                            print(f"[Agent] {len(tool_calls)} tool call(s) detected (with [DONE])")
                        else:
                            print("[Agent] Agent signaled completion with [DONE]")
                            final_response = self._clean_response(current_response)
                            await self._save_to_history(final_response, "answer")
                            return final_response

                    # If no tool calls and no [DONE], continue to next iteration for more reasoning
                    if not tool_calls:
                        print("[Agent] No tool calls detected, continuing reasoning...")
                        tool_results_context.append({
                            "name": "reasoning",
                            "result": current_response
                        })
                        current_iteration += 1
                        continue

                    # Save the explanation to history BEFORE executing tools
                    explanation = self._clean_response(current_response)
                    if explanation:  # Only save if there's actual text after cleaning
                        await self._save_to_history(explanation, "answer")

                    # Execute all tool calls
                    print(f"[Agent] {len(tool_calls)} tool call(s) detected")
                    for idx, tool_call in enumerate(tool_calls):
                        print(f"[Agent] Tool call {idx + 1}/{len(tool_calls)}: {tool_call}")
                        tool_name = tool_call['name']
                        tool_args = tool_call['arguments']

                        print(f"[Agent] Calling tool {tool_name} with args {tool_args}")
                        result = await session.call_tool(tool_name, arguments=tool_args)

                        # Parse the MCP result
                        if result.content:
                            combined_results = []
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    try:
                                        combined_results.append(json.loads(content_item.text))
                                    except:
                                        pass
                            result_text = json.dumps(combined_results, indent=2)
                        else:
                            result_text = str(result)

                        print(f"[Agent] Tool result (parsed): {result_text[:200]}...")

                        # Add to context
                        tool_results_context.append({
                            "name": tool_name,
                            "result": result_text
                        })

                    # Check if this was the final iteration (had [DONE])
                    if "[DONE]" in current_response:
                        print("[Agent] Agent signaled completion with [DONE] after tool execution")
                        # Don't save again - already saved before tool execution
                        return explanation

                    current_iteration += 1

                # If we exhausted iterations, return last response
                print("[Agent] Max iterations reached")
                final_response = self._clean_response(current_response) if current_response else "Max iterations reached without completion"
                await self._save_to_history(final_response, "answer")
                return final_response

    def _build_prompt_with_history(self, system_prompt: str, history: List[Dict], current_query: str) -> str:
        """Construire le prompt avec l'historique."""
        prompt = system_prompt + "\n\n"

        for item in history:
            prompt += f"User: {item['query']}\n\n"
            prompt += f"Assistant: {item['response']}\n\n"

        prompt += f"User: {current_query}\n\nAssistant:"

        return prompt

    def _build_system_prompt(self, tools):
        """Build system prompt with available tools."""
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])

        return f"""You are a helpful retail inventory management assistant. You have access to the following tools:

{tools_desc}

IMPORTANT FORMAT: Explain your action, then call tool(s) on the NEXT line(s):

CORRECT example:
I will get the current stock levels to identify low stock items.
TOOL_CALL: get_products_stock_levels()

WRONG example (don't repeat):
TOOL_CALL: get_products_stock_levels()
I will get the current stock levels...
TOOL_CALL: get_products_stock_levels()

When creating multiple orders:
I will be creating orders for the 3 lowest stocked items.
TOOL_CALL: order_product(sku="SKU-0001", quantity=50)
TOOL_CALL: order_product(sku="SKU-0002", quantity=50)
TOOL_CALL: order_product(sku="SKU-0003", quantity=50)

Call tools step-by-step:
1. First, gather information (like get_products_stock_levels)
2. Wait for the results
3. Then based on those results, call action tools (like order_product)

When you have COMPLETELY finished your task, end with [DONE] on a NEW line.
"""

    def _parse_tool_calls(self, text: str) -> List[Dict]:
        """Parse multiple tool calls from LLM response."""
        tool_calls = []

        # Find all TOOL_CALL entries using regex pattern (works across lines and multiple on same line)
        # Pattern now handles both with and without parentheses
        import re
        pattern = r'TOOL_CALL:\s*([a-zA-Z_][a-zA-Z0-9_]*)(?:\(([^)]*)\))?'
        matches = re.finditer(pattern, text)

        for match in matches:
            try:
                tool_name = match.group(1).strip()
                args_str = match.group(2).strip() if match.group(2) else ""
                args = {}

                if args_str:
                    for arg in args_str.split(","):
                        if not arg.strip():
                            continue

                        key, value = arg.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        try:
                            args[key] = json.loads(value)
                            continue
                        except:
                            pass

                        value = value.strip("'\"")
                        if value and value[0] == "[" and value[-1] == "]":
                            args_str_fixed = regex.sub(r"'([^']*)'", r'"\1"', value)
                            try:
                                args[key] = json.loads(args_str_fixed)
                                continue
                            except:
                                pass

                        try:
                            args[key] = int(value)
                            continue
                        except:
                            pass

                        args[key] = value

                tool_calls.append({"name": tool_name, "arguments": args})
            except Exception as e:
                print(f"[Agent] Error parsing tool call from match '{match.group(0)}': {e}")
                continue

        return tool_calls

    def _parse_tool_call(self, text: str):
        """Parse tool call from LLM response (deprecated - use _parse_tool_calls)."""
        calls = self._parse_tool_calls(text)
        return calls[0] if calls else None