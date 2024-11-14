# create by: ayoub taneh (2024-08-07)
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
import requests, logging, random


class SMS:
    # create by: ayoub taneh (2024-08-07)
    default_driver = 'niazpardaz'

    @staticmethod
    def send(mobile, message):  # done : 1403.02.11
        if SMS.default_driver == 'niazpardaz':
            return SMS.send_niazpardaz(mobile, message)


    @staticmethod
    def send_niazpardaz(mobile, message):  # done : 1403.02.11
        try:
            url = "http://login.niazpardaz.ir/api/v1/RestWebApi/SendBatchSms"
            data = {
                'userName': 't.09111715366',
                'password': 'ciu#143',
                'fromNumber': '10009611',
                'toNumbers': mobile,
                'messageContent': message,
                'isFlash': False,
                'sendDelay': 0
            }
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
            response.raise_for_status()  # Check for HTTP errors
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logging.error(f"Error sending SMS via niazpardaz: {e}")
            return {"success": False, "error": str(e)}



def verify_code(cache_name, input_code):
    
    stored_code = cache.get(f'sms_code_{cache_name}')
    print("stored_code",stored_code)
    
    if stored_code is None:
        return False, _("Code has expired or does not exist.")

    if stored_code == input_code:
        return True, _("Code is valid.")
    
    return False, _("Invalid code.")

def get_sms_cache_code(input_code):
    return cache.get(f'sms_code_{input_code}')


def generate_and_store_code_in_cache(cache_name):

    code = f"{random.randint(100000, 999999)}"
    
    # برای کش یک فایل جدا ساخته شود
    cache.set(f'sms_code_{cache_name}', str(code), timeout=300)
    
    try:
        pass
        # send code
        # ----------------------------------------------------------
    except:
        #save error in loge and send notification for admin
        pass
    
    return code
