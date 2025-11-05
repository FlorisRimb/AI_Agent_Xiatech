import asyncio
from llama_cpp import Llama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json


class RetailInventoryAgent:
    """LLM Agent with MCP tools for retail inventory management."""
    
    def __init__(self, model_path: str):
        print(f"[Agent] Loading model from {model_path}")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            verbose=False,
        )
        print("[Agent] Model loaded successfully")
    
    async def run_with_tools(self, user_query: str, previous_response: str) -> str:
        """Run the agent with access to MCP tools."""
        print(f"\n[Agent] User query: {user_query}")
        
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
                full_prompt = f"{system_prompt}\n\nPrevious answer: {previous_response}\n\nUser: {user_query}\n\nAssistant:"
                
                print("[Agent] Generating response...")
                response = self.llm(
                    full_prompt,
                    max_tokens=512,
                    temperature=0.7,
                    stop=["User:", "\n\n"],
                )
                
                assistant_response = response['choices'][0]['text'].strip()
                print(f"[Agent] LLM Response: {assistant_response}")
                
                tool_call = self._parse_tool_call(assistant_response)
                
                if tool_call:
                    print(f"[Agent] Tool call detected: {tool_call}")
                    tool_name = tool_call['name']
                    tool_args = tool_call['arguments']
                    
                    print(f"[Agent] Calling tool {tool_name} with args {tool_args}")
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    
                    print(f"[Agent] Tool result: {result}")
                    
                    final_prompt = f"{full_prompt}\n\nTool result:{result.content}\n\nProvide a natural response to the user:\n\nAssistant:"
                    
                    final_response = self.llm(
                        final_prompt,
                        max_tokens=256,
                        temperature=0.5,
                        stop=["User:", "\n\n"],
                    )
                    
                    return final_response['choices'][0]['text'].strip()
                
                return assistant_response
    
    def _build_system_prompt(self, tools):
        """Build system prompt with available tools."""
        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])
        
        return f"""You are a helpful retail inventory management assistant. You have access to the following tools:

{tools_desc}

To use a tool, respond with: TOOL_CALL: tool_name(arg1=value1, arg2=value2)

For example:
TOOL_CALL: get_products_soon_out_of_stock(days=5)

You will probably always need to use tools to answer user queries effectively, don't answer won't you don't have enough information and use tools.

And when answering, summarize information with what previous informations and tool results you have."""
    
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
                    key, value = arg.split("=")
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    
                    try:
                        value = int(value)
                    except:
                        pass
                    
                    args[key] = value
            
            return {"name": tool_name, "arguments": args}
        except:
            return None


async def main():
    agent = RetailInventoryAgent("/app/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    
    queries = [
        "Which products are likely to run out of stock in the next 3 days?",
        "Using the previous information, get the current stock level for the product on the list of products soon to be out of stock.",
        "Using the current stock level, get the daily sales data for the product over the past 3 days.",
        "Using the previous information, order a sufficient quantity of the 1st product to restock and last for at least a week.",
    ]
    
    response = ""
    for query in queries:
        print("\n" + "="*60)
        response = await agent.run_with_tools(query, response)
        print(f"\n[Final Answer] {response}")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(main())