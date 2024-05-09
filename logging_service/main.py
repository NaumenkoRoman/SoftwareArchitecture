from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hazelcast
import os

class Message(BaseModel):
    msg: str

app = FastAPI()

hz_host = os.getenv("HZ_HOST", "localhost")
hz = hazelcast.HazelcastClient(
    cluster_members=[f"{hz_host}:5701"]
)
distributed_map = hz.get_map("distributed-map").blocking()

@app.post("/log")
def log_message(message: Message):
    try:
        distributed_map.put(message.msg, message.msg)
        print(f"Logged: {message.msg}")
        return {"message": f"Logged: {message.msg}"}
    except Exception as e:
        print(f"Error logging message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/logs")
def get_messages():
    try:
        messages = distributed_map.values()
        return {"messages": list(messages)}
    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
