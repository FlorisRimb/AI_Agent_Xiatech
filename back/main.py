from fastapi import FastAPI
import uvicorn

from connect_database import get_database


app = FastAPI()

@app.get("/")
async def root():
    return {"greeting":"Hello world"}


if __name__ == "__main__":
    get_database()
    uvicorn.run(app, host="0.0.0.0", port=8000)