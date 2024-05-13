from fastapi import FastAPI
from pydantic import BaseModel
import pika
import threading
import time

app = FastAPI()

messages = []

def connect_to_rabbitmq():
    max_retries = 10
    wait_time = 1

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()
            channel.queue_declare(queue='message_queue')
            print("Connected to RabbitMQ")
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Connection failed, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2
            else:
                print("Failed to connect to RabbitMQ after several attempts.")
                raise e

connection, channel = connect_to_rabbitmq()

def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")
    messages.append(body.decode())

def start_consuming():
    channel.basic_consume(queue='message_queue', on_message_callback=callback, auto_ack=True)
    print("Started consuming messages from RabbitMQ")
    channel.start_consuming()

thread = threading.Thread(target=start_consuming)
thread.start()

@app.get("/messages")
def get_messages():
    return {"messages": messages}
