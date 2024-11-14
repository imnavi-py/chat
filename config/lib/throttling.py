from rest_framework.throttling import SimpleRateThrottle, BaseThrottle
from django.core.cache import cache
from config.lib.setting import APP_KEY
import time

class CustomUserThrottle(BaseThrottle):

    def get_client_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def allow_request(self, request, view):
        # ALLOW APP_KEY TOKEN
        if request.COOKIES.get('token') == APP_KEY:
            return True
        
        # ip = request.META.get('REMOTE_ADDR')
        ip= self.get_client_ip(request)
        # print("user ip",ip)
        # now = time.time()
        # history = cache.get(ip, [])

        # Ensure the user is authenticated
        # if not request.user.is_authenticated:
        #     return False

        # Get the user's national_code
        # national_code = request.user.national_code
        # print("user Throttle ip", ip)
        now = time.time()
        history = cache.get(ip, [])

        # Remove requests older than an hour
        history = [timestamp for timestamp in history if now - timestamp < 1]

        if len(history) >= 15:  # Limit number requests per seconds
            # Block the user for 1 hour
            print(f'blocked_{ip}')
            cache.set(f'blocked_{ip}', True, timeout=3600)
            return False

            # Check if the user is blocked
        if cache.get(f'blocked_{ip}'):
            return False


        # Add current request timestamp to history
        history.append(now)
        cache.set(ip, history, timeout=3600)
        return True