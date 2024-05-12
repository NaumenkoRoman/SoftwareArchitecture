from fastapi import FastAPI
from pydantic import BaseModel
import pika
import threading
import time
import consul
import os

app = FastAPI()

messages = []

def get_consul_config(key):
    consul_host = os.getenv("CONSUL_HOST", "consul")
    consul_client = consul.Consul(host=consul_host)
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
            print("[MESSAGING] INFO: Connected to RabbitMQ")
            return connection, channel, rabbitmq_queue
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"[MESSAGING] INFO: Connection failed, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2
            else:
                print("[MESSAGING] ERROR: Failed to connect to RabbitMQ after several attempts.")
                raise e

print(f"[MESSAGING] INFO: Connecting to RabbitMQ...", flush=True, end="")
connection, channel, rabbitmq_queue = connect_to_rabbitmq()
print(" Connected!")

def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")
    messages.append(body.decode())

def start_consuming():
    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)
    print("Started consuming messages from RabbitMQ")
    channel.start_consuming()

thread = threading.Thread(target=start_consuming)
thread.start()

@app.get("/messages")
def get_messages():
    return {"messages": messages}
