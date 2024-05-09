from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import httpx

class Message(BaseModel):
    msg: str

app = FastAPI()

logging_services = [
    "http://logging_service1:8000",
    "http://logging_service2:8000",
    "http://logging_service3:8000"
]

@app.post("/log")
async def log_message(message: Message):
    service_url = random.choice(logging_services)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{service_url}/log", json=message.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

@app.get("/logs")
async def get_messages():
    service_url = random.choice(logging_services)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{service_url}/logs")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
