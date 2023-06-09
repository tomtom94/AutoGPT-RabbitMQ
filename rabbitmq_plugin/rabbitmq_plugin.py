import os
import pika
import json
import functools
from typing import TypedDict
import threading
from colorama import Fore, init
init(autoreset=True)

class Message(TypedDict):
    role: str
    content: str

userReply = []

def run_consumer(self):
    connection1 = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=0))
    channel1 = connection1.channel()
    channel1.queue_declare(queue=QUEUE_TO_RECEIVE_MESSAGE)
    def callback(channel, method_frame, header_frame, body):
        delivery_tag = method_frame.delivery_tag
        channel.basic_ack(delivery_tag)
        if body.decode() in ["SIGTERM_FROM_SERVICE", "SIGTERM_FROM_AUTOGPT"]:
            if body.decode() == "SIGTERM_FROM_SERVICE":
                self.close("SIGTERM_FROM_SERVICE")
            channel1.stop_consuming()
            channel1.queue_delete(QUEUE_TO_RECEIVE_MESSAGE)
            connection1.close()
        else:
            userReply.append(body.decode())
    channel1.basic_consume(queue=QUEUE_TO_RECEIVE_MESSAGE, on_message_callback=callback)
    channel1.start_consuming()

class AutoGPT_RabbitMQ:  
    def __init__(self):
        if self.required_info_set():
            print(Fore.GREEN + "RabbitMQ plugin loaded!")
        else:
            print(Fore.RED + "RabbitMQ plugin not loaded, because not all the environmental variables were set in the env configuration file.")
            os._exit(1)
        self.connection2 = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=0))
        self.channel2 = self.connection2.channel()
        self.start_consumer()
    
    def required_info_set(self):
        global RABBITMQ_HOST
        RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
        CHAT_MESSAGES_ENABLED = os.getenv("CHAT_MESSAGES_ENABLED")
        global QUEUE_TO_RECEIVE_MESSAGE
        QUEUE_TO_RECEIVE_MESSAGE = os.getenv("QUEUE_TO_RECEIVE_MESSAGE")
        global QUEUE_TO_SEND_MESSAGE
        QUEUE_TO_SEND_MESSAGE = os.getenv("QUEUE_TO_SEND_MESSAGE")
        return RABBITMQ_HOST and CHAT_MESSAGES_ENABLED == "True" and QUEUE_TO_RECEIVE_MESSAGE and QUEUE_TO_SEND_MESSAGE
    
    def command_convert_to_pdf(self, feedback):
        return "This command is been made just for fun, no action executed. Here is the provided feedback: " + feedback

    def send_message(self, message: Message):
        self.channel2.queue_declare(queue=QUEUE_TO_SEND_MESSAGE)
        self.channel2.basic_publish(exchange='', routing_key=QUEUE_TO_SEND_MESSAGE, body=json.dumps(message))
    
    def start_consumer(self):
        t = threading.Thread(target = run_consumer, args=(self,))
        t.start()
        print(Fore.GREEN + "RabbitMQ has just started consuming")
    
    def check_negative_response(self, response):
        return response.lower() in ["no", "nope", "n", "negative"]
    
    def close(self, kill_code):
        self.send_message(Message(role="SYSTEM", content=kill_code))
        self.channel2.stop_consuming()
        self.channel2.queue_delete(QUEUE_TO_SEND_MESSAGE)
        self.connection2.close()
