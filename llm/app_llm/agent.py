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
        """Save agent interaction to database history (not local_history)."""
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

    async def run_with_tools(self, user_query: str) -> str:
        """Run the agent with access to MCP tools."""
        print(f"\n[Agent] User query: {user_query}")

        local_history: List[dict] = []

        # Add user query to history at the start
        current_exchange = {
            "query": user_query,
            "response": "",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        server_params = StdioServerParameters(
            command="python",
            args=["mcp/server.py"],
        )

        if local_history:
            print(f"[Agent] Conversation history ({len(local_history)} items):")
            for idx, item in enumerate(local_history):
                query_preview = item.get('query', '')[:80] if item.get('query') else 'N/A'
                response_preview = item.get('response', '')[:80] if item.get('response') else 'N/A'
                print(f"  [{idx+1}] Q: {query_preview}...")
                print(f"      A: {response_preview}...")
        else:
            print("[Agent] No conversation history")

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

What is the FIRST step? Call ONE tool.
Assistant:"""
                    else:
                        # Add tool results to prompt
                        full_prompt = self._build_prompt_with_history(system_prompt, local_history, user_query)

                        # Build a clear summary of completed actions
                        if tool_results_context:
                            full_prompt += "\n\n=== ACTIONS COMPLETED SO FAR ===\n"
                            action_num = 1
                            for ctx in tool_results_context:
                                if ctx['name'] == 'reasoning':
                                    continue
                                full_prompt += f"{action_num}. Called {ctx['name']}"
                                if 'args' in ctx:
                                    full_prompt += f" with {ctx['args']}"
                                full_prompt += f"\n   Result: {ctx['result'][:200]}\n"
                                action_num += 1
                            full_prompt += "=== END OF COMPLETED ACTIONS ===\n"

                            full_prompt += "\n\nIMPORTANT: Review the actions above. Do NOT repeat them. What is the NEXT NEW action needed, or say [DONE] if everything is complete?\n\nAssistant:"

                        print(f"[Agent] Generating response (iteration {current_iteration + 1})...)")
                    response = self.llm(
                        full_prompt,
                        max_tokens=256,
                        temperature=0.5,
                        stop=["[DONE]", "\n\n\n"],
                    )

                    current_response = response['choices'][0]['text'].strip()

                    # Empty response when ai stop generating
                    if not current_response:
                        print("[Agent] Empty response, stopping process...")
                        break

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

                            # Save to local history
                            current_exchange["response"] = final_response
                            local_history.append(current_exchange)

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

                        # Add to context with args for transparency
                        tool_results_context.append({
                            "name": tool_name,
                            "result": result_text,
                            "args": tool_args
                        })

                    # Check if this was the final iteration (had [DONE])
                    if "[DONE]" in current_response:
                        print("[Agent] Agent signaled completion with [DONE] after tool execution")
                        # Don't save again - already saved before tool execution

                        # Save to local history
                        current_exchange["response"] = explanation
                        local_history.append(current_exchange)

                        return explanation

                    current_iteration += 1

                if current_iteration >= max_iterations:
                    print("[Agent] Max iterations reached")

                final_response = self._clean_response(current_response) if current_response else "No response generated."

                # Save to local history
                current_exchange["response"] = final_response
                local_history.append(current_exchange)

                return final_response

    def _build_prompt_with_history(self, system_prompt: str, history: List[Dict], current_query: str) -> str:
        """Construire le prompt avec l'historique."""
        prompt = system_prompt + "\n\n"
        if history:
            prompt += "Conversation History:\n"
            for item in history:
                prompt += f"User: {item['query']}\n"
                prompt += f"Assistant: {self._clean_response(item['response'])}\n"
            prompt += "\n"
        prompt += f"Current Task: {current_query}\n"
        return prompt

    def _build_system_prompt(self, tools):
        """Build system prompt with available tools."""
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])

        return f"""You are a retail inventory assistant. Available tools:

{tools_desc}

RULES:
1. NEVER make up SKU values - use actual data from tools
2. NEVER call the same tool twice with the same arguments
3. Call ONE information tool at a time to gather data
4. You CAN call order_product multiple times in ONE response
5. Brief explanation before tool calls
6. Say [DONE] when complete

EXAMPLE:
Checking products needing restock.
TOOL_CALL: soon_out_of_stock_products(days=5)

(Gets SKU-0018, qty 166)

Placing order for SKU-0018.
TOOL_CALL: order_product(sku="SKU-0018", quantity=166)

[DONE]
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