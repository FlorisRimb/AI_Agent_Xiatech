import asyncio
#from llama_cpp import Llama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
from typing import List, Dict
import re as regex
from dotenv import load_dotenv
import google.generativeai as genai


class RetailInventoryAgent:
    """LLM Agent with MCP tools for retail inventory management."""
    
    def __init__(self, model_path: str):
        #print(f"[Agent] Loading model from {model_path}")
        """self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            verbose=False,
        )"""
        api_key = load_dotenv()
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel("models/gemini-2.5-flash-lite")
        print("[Agent] Model loaded successfully")
    
    async def run_with_tools(self, user_query: str, history: List[Dict] = None) -> str:
        """Run the agent with access to MCP tools."""
        print(f"\n[Agent] User query: {user_query}")
        
        if history is None:
            history = []
        
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
                
                full_prompt = self._build_prompt_with_history(system_prompt, history, user_query)
                
                print("[Agent] Generating response...")
                """response = self.llm(
                    full_prompt,
                    max_tokens=512,
                    temperature=0.7,
                    stop=["User:", "\n\n"],
                )"""
                response = self.llm.generate_content(full_prompt)
                
                assistant_response = response.text.strip()
                print(f"[Agent] LLM Response: {assistant_response}")
                
                tool_call = self._parse_tool_call(assistant_response)
                
                if tool_call:
                    print(f"[Agent] Tool call detected: {tool_call}")
                    tool_name = tool_call['name']
                    tool_args = tool_call['arguments']
                    
                    print(f"[Agent] Calling tool {tool_name} with args {tool_args}")
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    
                    print(f"[Agent] Tool result: {result}")
                    
                    result_text = result.content[0].text if result.content else str(result)
                    
                    final_prompt = self._build_prompt_with_history(system_prompt, history, user_query)
                    final_prompt += f"\n\n[Tool {tool_name} returned the following data]:\n{result_text}\n\nBased on this data, provide a clear and natural answer to the user's question:\n\nAssistant:"
                    
                    final_response = self.llm(
                        final_prompt,
                        max_tokens=256,
                        temperature=0.5,
                        stop=["User:", "TOOL_CALL:", "\n\n"],
                    )
                    
                    return final_response['choices'][0]['text'].strip()
                
                return assistant_response
    
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

To use a tool, respond ONLY with: TOOL_CALL: tool_name(arg1=value1, arg2=value2)

For example:
TOOL_CALL: get_products_soon_out_of_stock(days=5)

When you receive tool results, provide a clear and natural answer based on the data.
Do NOT repeat the TOOL_CALL in your final answer.
Always use tools to gather data before answering.
"""
    
    def _parse_tool_call(self, text: str):
        """Parse tool call from LLM response."""
        if "TOOL_CALL:" not in text:
            return None
        
        try:
            call_str = text.split("TOOL_CALL:")[1].strip()
            tool_name = call_str.split("(")[0].strip()
        
            args_str = call_str.split("(")[1].split(")")[0]
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
                    if value[0] == "[" and value[-1] == "]":
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
            
            return {"name": tool_name, "arguments": args}
        except Exception as e:
            print(f"[Agent] Error parsing tool call: {e}")
            return None