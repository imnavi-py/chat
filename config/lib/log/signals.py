# myproject/signals.py
from django.db.models.signals import post_save, pre_delete
from django.forms.models import model_to_dict
from django.dispatch import Signal
from django.dispatch import receiver
from uuid import UUID
from ..middlewares import get_current_request
from .rabbitMQ_conf import RabbitMQClient
from ..utils import SafeJSONEncoder, find_ip_address
import time, json

###################################################################################################################tet

pre_delete_signal = Signal()

def push(data):
    rabbit_client = RabbitMQClient()
    rabbit_client.call(data, 'log')
    rabbit_client.close()


@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    """
    سیگنال برای لاگ کردن پس از ذخیره شدن هر مدلی.
    """
    request = get_current_request() 
    new_instance = model_to_dict(instance)
    try:
        new_instance['id'] = instance.id
    except:
        new_instance['id'] = None
    
        # تبدیل UUIDها به رشته
    for key, value in new_instance.items():
        if isinstance(value, UUID):
            new_instance[key] = str(value)
            
    log_data = json.dumps({
        'level': 'INFO' if request else 'CRITICAL',
        'message': f"{'Created' if created else 'Updated'} record in {sender.__name__}",
        'user': {
            'id': str(request.user.id) if request and request.user.is_authenticated else None,
            'username': request.user.username if request and request.user.is_authenticated else 'Anonymous',
            'first_name_fa': request.user.first_name_fa if request and request.user.is_authenticated else None,
            'last_name_fa': request.user.last_name_fa if request and request.user.is_authenticated else None,
            'first_name_en': request.user.first_name_en if request and request.user.is_authenticated else None,
            'last_name_en': request.user.last_name_en if request and request.user.is_authenticated else None,
            'national_code': request.user.national_code if request and request.user.is_authenticated else None
        },
        'action': 'CREATE' if created else 'UPDATE',
        'ip_address': find_ip_address(request) if request else None,
        'request': {
            'method': request.method if request else None,
            'path': request.get_full_path() if request else None,
            'headers': dict(request.headers) if request else None,
            'body': dict(request.POST) if request else None,
            'query_params': dict(request.GET) if request else None
        },
        'instance': new_instance,  # داده‌های آخرین نسخه از مدل
        'additional_info': {
            "app_label": sender._meta.app_label,
            "model": sender.__name__
        },
        "timestamp_request": time.time()
    }, cls=SafeJSONEncoder)
    push(log_data)
        
        # LogEntry.objects.create(**log_data)


@receiver(pre_delete_signal)
def log_pre_delete(sender, instance, **kwargs):
    """
    سیگنال برای لاگ کردن قبل از حذف شدن هر رکورد.
    """
    request = get_current_request()
    new_instance = model_to_dict(instance)
    try:
        new_instance['id'] = instance.id
    except:
        new_instance['id'] = None
    
        # تبدیل UUIDها به رشته
    for key, value in new_instance.items():
        if isinstance(value, UUID):
            new_instance[key] = str(value)
               
    log_data = json.dumps(
        {
        'level': 'WARNING' if request else 'CRITICAL',
        'message': f'Deleted record in {sender.__name__}',
        'user': {
            'id': str(request.user.id) if request and request.user.is_authenticated else None,
            'username': request.user.username if request and request.user.is_authenticated else 'Anonymous',
            'first_name_fa': request.user.first_name_fa if request and request.user.is_authenticated else None,
            'last_name_fa': request.user.last_name_fa if request and request.user.is_authenticated else None,
            'first_name_en': request.user.first_name_en if request and request.user.is_authenticated else None,
            'last_name_en': request.user.last_name_en if request and request.user.is_authenticated else None,
            'national_code': request.user.national_code if request and request.user.is_authenticated else None
        },
        'action': 'DELETE',
        'ip_address': request.META.get('REMOTE_ADDR') if request else None,
        'request': {
            'method': request.method if request else None,
            'path': request.get_full_path() if request else None,
            'headers': dict(request.headers) if request else None,
            'body': dict(request.POST) if request else None,
            'query_params': dict(request.GET) if request else None
        },
        'instance': new_instance,  # داده‌های رکورد حذف شده
        'additional_info': {
            "app_label": sender._meta.app_label,
            "model": sender.__name__
        },
        "timestamp_request": time.time()
    },cls=SafeJSONEncoder
    )
    push(log_data)
    
    
@receiver(pre_delete)
def log_pre_delete_signal_handler(sender, instance, **kwargs):
    pre_delete_signal.send(sender, instance=instance)