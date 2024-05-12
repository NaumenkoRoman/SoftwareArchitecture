from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import httpx
import pika
import consul
import os
import time

class Message(BaseModel):
    msg: str

print(f"[FACADE] INFO: Starting FastAPI app...", flush=True, end="")
app = FastAPI()
print(" Started!")

consul_host = os.getenv("CONSUL_HOST", "consul")
consul_client = consul.Consul(host=consul_host)

def get_service(service_name):
    services = consul_client.health.service(service_name)[1]
    healthy_services = [service for service in services if service['Checks'][0]['Status'] == 'passing']
    if not healthy_services:
        raise Exception(f"No healthy {service_name} instances found")
    service = random.choice(healthy_services)
    address = service['Service']['Address']
    port = service['Service']['Port']
    print(f"Retrieved {service_name} address: http://{address}:{port}")
    return f"http://{address}:{port}"


def get_consul_config(key):
    index, data = consul_client.kv.get(key)
    if data is None:
        raise Exception(f"Key {key} not found in Consul")
    return data['Value'].decode()

def connect_to_rabbitmq():
    max_retries = 10
    wait_time = 1

    rabbitmq_host = get_consul_config("rabbitmq/host")
    rabbitmq_queue = get_consul_config("rabbitmq/queue")

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=rabbitmq_host,
                heartbeat=600,
                blocked_connection_timeout=300
            ))
            channel = connection.channel()
            channel.queue_declare(queue=rabbitmq_queue)
            print("[FACADE] INFO: Connected to RabbitMQ")
            return connection, channel, rabbitmq_queue
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"[FACADE] INFO: Connection failed, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2
            else:
                print("[FACADE] ERROR: Failed to connect to RabbitMQ after several attempts.")
                raise e

print(f"[FACADE] INFO: Connecting to RabbitMQ...", flush=True, end="")
connection, channel, rabbitmq_queue = connect_to_rabbitmq()
print(" Connected!")

@app.post("/log")
async def log_message(message: Message):
    try:
        logging_service_url = get_service("logging-service")
        print(f"[FACADE] INFO: Logging mst to: {logging_service_url}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{logging_service_url}/log", json=message.dict())
            response.raise_for_status()

        channel.basic_publish(exchange='',
                              routing_key=rabbitmq_queue,
                              body=message.msg)
        return response.json()
    except Exception as e:
        print(f"[FACADE] ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_messages():
    try:
        logging_service_url = get_service("logging-service")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{logging_service_url}/logs")
            response.raise_for_status()
        logging_messages = response.json()["messages"]

        messages_service_url = get_service("messages-service")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{messages_service_url}/messages")
            response.raise_for_status()
        messages = response.json()["messages"]

        all_messages = logging_messages + messages
        return {"messages": all_messages}
    except Exception as e:
        print(f"[FACADE] ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
