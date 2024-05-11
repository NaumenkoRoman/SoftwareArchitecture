from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import httpx
import pika
import time

class Message(BaseModel):
    msg: str

app = FastAPI()

logging_services = [
    "http://logging_service1:8000",
    "http://logging_service2:8000",
    "http://logging_service3:8000"
]

messages_services = [
    "http://messages_service1:8000",
    "http://messages_service2:8000"
]

def connect_to_rabbitmq():
    max_retries = 10
    wait_time = 1 

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='message_queue')
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
        service_url = random.choice(logging_services)
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{service_url}/log", json=message.dict())
            response.raise_for_status()

        channel.basic_publish(exchange='',
                              routing_key='message_queue',
                              body=message.msg)

        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_messages():
    try:
        service_url = random.choice(logging_services)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{service_url}/logs")
            response.raise_for_status()
        logging_messages = response.json()["messages"]

        service_url = random.choice(messages_services)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{service_url}/messages")
            response.raise_for_status()
        messages = response.json()["messages"]

        return {"messages": messages, "logging_messages": logging_messages}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
