# create by: ayoub taneh (2024-08-07)
from celery import shared_task
from django.core.cache import cache
import time
import random
from .log.rabbitMQ_conf import RabbitMQClient
import json


@shared_task
def generate_data():
    # create by: ayoub taneh (2024-08-07)
    data = 'این داده در سلری تولید و در کش ذخیره شده و اکنون از ردیس خوانده میشود.'
    time.sleep(5)
    cache.set('my_data', data, timeout=100) # timeout اعمال نیمی شود، بعدا بررسی شود
    return data

def generate_cache(mobile):
    # time.sleep(3)
    # print("Data chached successfully.")

    # code = str(random.randrange(10000, 99999))
    code= "12345"
    created_at = int(time.time())
    expired_at = int(time.time() + 60 * 2)  # 2 min
    # mobile = serializer.data['mobile']

    data = {'code': code,
            'mobile': mobile,
            'time_expired': expired_at,
            'time_create': created_at
            }
    cache.set('sms_code', data)
    print('cache data in task.py is ',data)

    return True




def store_log(level, message, user, action, ip_address, request, instance, extra_data, additional_info, queue_name = 'log'):
    """
    Sends log data to a RabbitMQ queue for storage.

    Args:
        level (str): The severity level of the log (e.g., 'INFO', 'ERROR').
        message (str): The message content of the log.
        user (User): The user object related to the action. Must have an 'id' attribute.
        action (str): A description of the user action being logged.
        ip_address (str): The IP address from where the action originated.
        request (dict): The details of the HTTP request (headers, body, etc.).
        instance (dict): Data about the model instance affected by the action (e.g., object details).
        extra_data (dict): Any extra information related to the log.
        additional_info (dict): Additional details to be logged (optional).
        queue_name (str, optional): The RabbitMQ queue name where the log will be sent. Defaults to 'log'.
        timestamp_request (time): The timestamp of the request
    
    Returns:
        None

    Example usage:
        store_log('INFO', 'User logged in', user, 'login', '192.168.1.1', request_data, instance_data, extra_data, additional_info)
    """
    rabbit_client = RabbitMQClient()
    newUser = vars(user)
    newUser['id'] = str(newUser['id'])
    data = json.dumps({
            "level":level,
            "message":message,
            "user":vars(user),
            "action":action,
            "ip_address":ip_address,
            "request":request,
            "instance":instance,
            "additional_info":additional_info,
            "timestamp_request": time.time()
            })
    rabbit_client.call(level, data, queue_name)
    rabbit_client.close()

