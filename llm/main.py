from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app_llm.agent import RetailInventoryAgent
import asyncio

app = FastAPI(title="LLM Agent API")

agent = None

history: List[dict] = []

queries = [
    "Which products are likely to run out of stock in the next 3 days?",
    #"Now that you have the list of products soon to be out of stock, get the current stock level for the 1st product on that list.",
    #"Get the daily sales data for the product over the past 3 days.",
    "Now that you have identified the products soon to be out of stock, order 200 units of each product to restock.",
]

class QueryResponse(BaseModel):
    response: str

class HistoryResponse(BaseModel):
    history: List[dict]

@app.on_event("startup")
async def startup():
    global agent
    print("[API] Initializing agent...")
    agent = RetailInventoryAgent("/app/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    print("[API] Agent ready")

@app.get("/agent/query", response_model=QueryResponse)
async def query_agent():
    try:
        asyncio.create_task(run_queries())
        return QueryResponse(response="Executing queries...")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/agent/history", response_model=HistoryResponse)
async def get_history():
    return HistoryResponse(history=history)

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_loaded": agent is not None}

async def run_queries():
    for query in queries:
        print("\n" + "="*60)
        response = await agent.run_with_tools(query, history)
        history.append({"query": query, "response": response})
        print(f"\n[Final Answer] {response}")
        print(history)
        print("="*60)

    history.clear()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)