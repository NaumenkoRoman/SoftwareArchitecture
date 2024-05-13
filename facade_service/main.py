from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import httpx
import pika
import time
import os
import consul

class Message(BaseModel):
    msg: str

app = FastAPI()

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

# Message queue name
rabbitmq_queue = get_consul_config("rabbitmq/queue")


def connect_to_rabbitmq():
    max_retries = 10
    wait_time = 1 

    rabbitmq_host = get_consul_config("rabbitmq/host")

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            channel.queue_declare(queue=rabbitmq_queue)
            print("Connected to RabbitMQ!")
            break
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Connection failed, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2 
            else:
                print("Failed to connect to RabbitMQ after several attempts.")
                raise e
    return connection, channel

connection, channel = connect_to_rabbitmq()

@app.post("/log")
async def log_message(message: Message):
    try:
        service_url = get_service("logging-service")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{service_url}/log", json=message.dict())
            response.raise_for_status()

        channel.basic_publish(exchange='',
                              routing_key=rabbitmq_queue,
                              body=message.msg)

        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_messages():
    try:
        service_url = get_service("logging-service")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{service_url}/logs")
            response.raise_for_status()
        logging_messages = response.json()["messages"]

        service_url = get_service("messages-service")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{service_url}/messages")
            response.raise_for_status()
        messages = response.json()["messages"]

        return {"messages": messages, "logging_messages": logging_messages}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
