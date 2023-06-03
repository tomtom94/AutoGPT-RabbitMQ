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
threads = []

class AutoGPT_RabbitMQ:  
    def __init__(self):
        if self.required_info_set():
            print(Fore.GREEN + "RabbitMQ plugin loaded!")
        else:
            print(Fore.RED + "RabbitMQ plugin not loaded, because not all the environmental variables were set in the env configuration file.")
            os._exit(1)
        self.connection1 = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        self.connection2 = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        self.channel1 = self.connection1.channel()
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
    
    def commandUnauthorized(self, feedback):
        return "This command was not authorized by the user. Do not try it again. Here is the provided feedback: " + feedback

    def messagesToSend(self, message: Message):
        self.channel2.queue_declare(queue=QUEUE_TO_SEND_MESSAGE)
        self.channel2.basic_publish(exchange='', routing_key=QUEUE_TO_SEND_MESSAGE, body=json.dumps(message))
    
    def ack_message(self, delivery_tag):
        if self.channel1.is_open:
            self.channel1.basic_ack(delivery_tag)
        else:
            pass
    
    def start_consumer(self):
        self.channel1.queue_declare(queue=QUEUE_TO_RECEIVE_MESSAGE)
        def callback(channel, method_frame, header_frame, body):
            delivery_tag = method_frame.delivery_tag
            cb = functools.partial(self.ack_message, delivery_tag)
            self.connection1.add_callback_threadsafe(cb)
            userReply.append(body.decode())
        self.channel1.basic_consume(queue=QUEUE_TO_RECEIVE_MESSAGE, on_message_callback=callback)
        t = threading.Thread(target = self.channel1.start_consuming)
        t.start()
        threads.append(t)
        print(Fore.GREEN + "RabbitMQ has just started consuming")
    
    def check_negative_response(self, response):
        response.lower() in ["no", "nope", "n", "negative"]
    
    def close(self):
        if len(self.channel1.consumer_tags) > 0:
            self.channel1.stop_consuming()
        if len(self.channel2.consumer_tags) > 0:
            self.channel2.stop_consuming()
        
        for thread in threads:
            thread.join()

        if self.channel1.is_open:
            self.channel1.queue_delete(QUEUE_TO_RECEIVE_MESSAGE)
        if self.channel2.is_open:
            self.channel2.queue_delete(QUEUE_TO_SEND_MESSAGE)

        if self.connection1.is_open:
            self.connection1.close()
        if self.connection2.is_open:
            self.connection2.close()
