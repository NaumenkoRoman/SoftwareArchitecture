from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hazelcast
import consul
import os

class Message(BaseModel):
    msg: str

def get_consul_config(key):
    consul_host = os.getenv("CONSUL_HOST", "consul")
    consul_client = consul.Consul(host=consul_host)
    index, data = consul_client.kv.get(key)
    if data is None:
        raise Exception(f"Key {key} not found in Consul")
    return data['Value'].decode()

print(f"[LOGGING] INFO: Starting FastAPI app...", flush=True, end="")
app = FastAPI()
print(" Started!")

print(f"[LOGGING] INFO: Connecting to Hazelcast...", flush=True, end="")
hz_config = get_consul_config("hazelcast/config")
hz = hazelcast.HazelcastClient(cluster_name=hz_config)
distributed_map = hz.get_map("default").blocking()
print(" Connected!")

@app.post("/log")
def log_message(message: Message):
    try:
        distributed_map.put(message.msg, message.msg)
        return {"message": f"Logged: {message.msg}"}
    except Exception as e:
        print(f"[LOGGING] ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
def get_messages():
    try:
        messages = distributed_map.values()
        return {"messages": list(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
