from fastapi import FastAPI
from pymongo import MongoClient
import uvicorn

app = FastAPI()


def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    return db


@app.get("/")
def read_root():
    db = get_database()
    return {"message": "Hello World"}