from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app_llm.agent import RetailInventoryAgent
import asyncio
import os

app = FastAPI(title="LLM Agent API")

agent = None

history: List[dict] = []

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.on_event("startup")
async def startup():
    global agent
    print("[Agent] Initializing agent...")

    model_path = "/app/qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf"

    # Check if file exists and get size
    if os.path.exists(model_path):
        file_size = os.path.getsize(model_path)
        print(f"[Agent] Model file found: {model_path}")
        print(f"[Agent] Model file size: {file_size / (1024**3):.2f} GB")
    else:
        print(f"[Agent] ERROR: Model file not found at {model_path}")
        return

    try:
        agent = RetailInventoryAgent(model_path)
        print("[Agent] Agent ready")
    except Exception as e:
        print(f"[Agent] ERROR loading model: {e}")
        import traceback
        traceback.print_exc()

@app.post("/agent/query", response_model=QueryResponse)
async def query_agent_post(request: QueryRequest):
    try:
        asyncio.create_task(run_query(request.query))
        return QueryResponse(response="Executing query...")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.post("/agent/restock", response_model=QueryResponse)
async def restock_agent_post():
    try:
        restock_query = "Based of the daily sales, determine the products that will run out of stock in the next 7 days. After identifying them, place orders to restock each products with its sufficient amount to last a least one week"
        asyncio.create_task(run_query(restock_query))
        return QueryResponse(response="Executing restock query...")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy", "agent_loaded": agent is not None}

async def run_query(user_query: str):
    print("\n" + "="*60)
    response = await agent.run_with_tools(user_query)
    print(f"\n[Final Answer] {response}")
    print("="*60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)