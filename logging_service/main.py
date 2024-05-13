from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hazelcast
import os
import consul

class Message(BaseModel):
    msg: str

app = FastAPI()

consul_host = os.getenv("CONSUL_HOST", "consul")
consul_client = consul.Consul(host=consul_host)

def get_consul_config(key):
    index, data = consul_client.kv.get(key)
    if data is None:
        raise Exception(f"Key {key} not found in Consul")
    return data['Value'].decode()

container_name = os.getenv("SERVICE_CONTAINER_NAME", "consul")
hazel_host = get_consul_config(f"hazelcast/{container_name}")
hazel_port = get_consul_config("hazelcast/port")
hazel_map_name = get_consul_config("hazelcast/map_name")

hz = hazelcast.HazelcastClient(
    cluster_members=[f"{hazel_host}:{hazel_port}"]
)
distributed_map = hz.get_map(hazel_map_name).blocking()

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
