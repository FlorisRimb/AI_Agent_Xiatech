from fastapi import FastAPI
import uvicorn

app = FastAPI()
from db.init_db import init_db
from api.router import router
from core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"greeting": "Hello world", "project": settings.PROJECT_NAME}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.on_event("startup")
async def on_startup():
    await init_db()

if __name__ == "__main__":
    uvicorn.run(app)