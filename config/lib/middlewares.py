from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .log.rabbitMQ_conf import RabbitMQClient
from .utils import SafeJSONEncoder, find_ip_address
import json, time


def push(data):
    rabbit_client = RabbitMQClient()
    rabbit_client.call(data, 'log')
    rabbit_client.close()


class MaintenanceMiddleware:
    """
    MIDDLEWARE = [
        .
        .
        .
        'config.custo_lib.MaintenanceMiddleware',                     # Maintenance
    ]
    """
    
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        # Check settings for update mode
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Get the user from the request
            user = request.user
            # If the user is not authenticated or is not a superuser, return a JSON response
            if not user.is_authenticated or not user.is_superuser:
                return JsonResponse({"detail": _("We are updating, please be patient.")}, status=503)
        
        response = self.get_response(request)
        return response



class TokenAuthMiddleware:
    
    def __init__(self, get_response):
        
        self.get_response = get_response


    def __call__(self, request):
        token = request.COOKIES.get('token')
        if token:
            request.META['HTTP_AUTHORIZATION'] = f'Token {token}'
        response = self.get_response(request)
        return response
    
    

import threading

_thread_locals = threading.local()

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request  # ذخیره ریکوئست در یک متغیر محلی
        response = self.get_response(request)
        return response

def get_current_request():
    return getattr(_thread_locals, 'request', None)




class ErrorLoggingMiddleware:
    """
    Middleware برای لاگ‌گیری خطاهای به کاربر بازگردانده شده و ذخیره آن‌ها در دیتابیس.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        body = request.body.decode('utf-8', errors='ignore')
        
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {"data":body}
        # پیش از پردازش درخواست
        response = self.get_response(request)

        # پس از پردازش درخواست
        if response.status_code >= 300:  # بررسی کدهای خطا (4xx و 5xx)
            self.log_error(request, response, body)

        return response

    def log_error(self, request, response, body):
        log_data = json.dumps({
            'level': 'ERROR',  # سطح لاگ را به ERROR تنظیم می‌کنیم
            'message': 'Error response from the server',  # پیام لاگ
            'user': {
            'id': str(request.user.id) if request.user.is_authenticated else None,
            'username': request.user.username if request.user.is_authenticated else 'Anonymous',
            'first_name_fa': request.user.first_name_fa if request.user.is_authenticated else None,
            'last_name_fa': request.user.last_name_fa if request.user.is_authenticated else None,
            'first_name_en': request.user.first_name_en if request.user.is_authenticated else None,
            'last_name_en': request.user.last_name_en if request.user.is_authenticated else None,
            'national_code': request.user.national_code if request.user.is_authenticated else None
            },
            'action': request.method,  # عمل لاگ را به ERROR تنظیم می‌کنیم
            'ip_address': find_ip_address(request) if request else None,
            'request': {
                'method': request.method,
                'path': request.get_full_path(),
                'headers': dict(request.headers),
                'body': body,
                'body': dict(request.POST),
                'query_params': dict(request.GET)
            },
            'instance': {
                'status_code': response.status_code,
                'content': response.content.decode('utf-8', errors='ignore'),
            },
            'additional_info': {
                "path": request.path,
                "method": request.method,
            },
            "timestamp_request": time.time()
        },cls=SafeJSONEncoder)
        push(log_data)