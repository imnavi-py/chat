import pika
import uuid
from config.lib.setting import RABBITMQ_CONF

class RabbitMQClient:
    def __init__(self, host=RABBITMQ_CONF['host'], user=RABBITMQ_CONF['user'], password=RABBITMQ_CONF['pass'], port=RABBITMQ_CONF['port']):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username=user, password=password)  # استفاده از اعتبارنامه
        ))
        self.channel = self.connection.channel()
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, data, routing_key):
        self.channel.queue_declare(queue=routing_key, durable=True)
        self.response = None
        self.corr_id = str(uuid.uuid4())  # تولید یک شناسه یکتا برای هر پیام
        # ارسال پیام به RabbitMQ
        self.channel.basic_publish(
            exchange='',
            routing_key=routing_key,  # صفی که پیام به آن ارسال می‌شود
            properties=pika.BasicProperties(
                correlation_id=self.corr_id,
                delivery_mode=2  # پیام پایدار
            ),
            body=data,
        )

    def close(self):
        self.connection.close()