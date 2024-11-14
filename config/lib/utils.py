# create by: ayoub taneh (2024-08-07)
from rest_framework.serializers import ValidationError
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.utils import timezone
from types import SimpleNamespace
from config import settings
import datetime, jdatetime, json
import json
from decimal import Decimal
from uuid import UUID
from django.core.files import File
from django.db.models import QuerySet, Model
from django.utils.timezone import is_naive, make_aware
from datetime import datetime, date, time




def cbool(value):
    # create by: ayoub taneh (2024-08-07)
    """
    If the string is sent, it converts all to lowercase letters and returns True if any of the following options, otherwise it returns False.
    """
    if isinstance(value, str):
        value = value.lower()

    if value in ['true', 'yes', '1']:
        return True
    
    return False



def safe_to_dict(obj):
    # create by: ayoub taneh (2024-09-26)

    if isinstance(obj, dict):
        return obj

    if hasattr(obj, '_meta'):
        return model_to_dict(obj)

    if isinstance(obj, SimpleNamespace):
        return obj.__dict__

    try:
        return json.loads(json.dumps(obj, cls=DjangoJSONEncoder))
    except (TypeError, ValueError) as e:
        print(f'!!! safe_to_dict `DjangoJSONEncoder` ERROR: {str(e)} !!!')
        return {}



def mask_word(word, start=3, end=3, star=3, symbol='*'):
    # create by: ayoub taneh (2024-08-07)
    """
    Masks a portion of the input word while keeping the beginning and end visible.

    Parameters:
    word (str): The word to be masked.
    start (int): The number of characters to keep visible at the start of the word. Default is 3.
    end (int): The number of characters to keep visible at the end of the word. Default is 3.
    star (int): The number of masking characters (symbols) to insert in the middle of the word. Default is 3.
    symbol (str): The character used for masking. Default is '*'.

    Returns:
    str: The masked word where the middle part is replaced with the masking character.

    Example:
    >>> mask_word('abcdefghij')
    'abc***hij'

    >>> mask_word('abcdefghij', start=2, end=2, star=4)
    'ab****ij'

    >>> mask_word('abcdef', start=2, end=2)
    'ab***ef'
    
    >>> mask_word('short', start=2, end=2)
    'sh***rt'
    
    >>> mask_word('short', start=2, end=3)
    'sh***ort'
    """
    if len(word) <= start + end:
        return symbol * len(word)
    return word[:start] + symbol * star + word[-end:]



def date_to_unix(input_date=None, calendar_type='gregorian'):
    # create by: ayoub taneh (2024-08-07)
    """ 
    Example :
        print( date_to_unix() )
        print( date_to_unix([2024, 7, 30, 12], 'gregorian') )
        print( date_to_unix([1403, 5, 9, 12, 0, 0], 'jalali') )
    
    Output:
        1722336124
        1722328200
        1722328200
    """
    if input_date is None:
        # Use the current time if no date is provided
        current_time = timezone.now()
    else:
        try:
            # Fill empty values ​​with 0
            input_date = list(input_date) + [0] * (6 - len(input_date))
            current_time = datetime.datetime(*input_date)
            
            if calendar_type == 'gregorian':
                if isinstance(input_date, (list, tuple)) and len(input_date) == 6:
                    current_time = datetime.datetime(*input_date)
                else:
                    raise ValidationError(_('For Gregorian dates, the input must be a list or tuple of 6 integers.'))
            elif calendar_type == 'jalali':
                if isinstance(input_date, (list, tuple)) and len(input_date) == 6:
                    jalali_date = jdatetime.datetime(*input_date)
                    gregorian_date = jalali_date.togregorian()
                    current_time = datetime.datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day, gregorian_date.hour, gregorian_date.minute, gregorian_date.second)
                else:
                    raise ValidationError(_('For Jalali dates, the input must be a list or tuple of 6 integers.'))
            else:
                raise ValidationError(_('calendar_type must be "gregorian" or "jalali".'))
        except:
            raise ValidationError(_('The submitted format is incorrect. (The correct format is [2024, 7, 30, 12, 0, 0])'))
    
    return int(current_time.timestamp())



def unix_to_gregorian_date(unix_timestamp, pattern=None):
    # create by: ayoub taneh (2024-08-07)
    """ 
    Example:
        print( unix_to_gregorian_date(unix_time) )
    
    Output:
        2024-07-30 14:51:39
    """
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    
    return dt.strftime(pattern)



def unix_to_jalali_date(unix_timestamp, pattern=None):
    # create by: ayoub taneh (2024-08-07)
    """ 
    Example:
        print( unix_to_jalali_date(unix_time) )
    
    Output:
        1403-05-09 14:51:39
    """
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    
    return jdt.strftime(pattern)



def calculate_datetime_passed(start_date, end_date=None):
    # create by: ayoub taneh (2024-08-07)
    """
    Calculate the time passed between two dates.
    
    Parameters:
    - start_date (datetime): The starting date.
    - end_date (datetime, optional): The ending date. If not provided, the current date and time is used.
    
    Returns:
    - list of dicts: Each dict contains 'value' and 'unit' representing the time passed in years, months, days, hours, minutes, and seconds.
    
    Example:
        start_date = datetime.datetime(2023, 1, 1, 10, 30, 0)
        result = calculate_time_passed(start_date)
        print(result)
    -----------------------------------------
        [
            {'value': 0, 'unit': 'year(s)'},
            {'value': 1, 'unit': 'month(s)'},
            {'value': 2, 'unit': 'day(s)'},
            {'value': 21, 'unit': 'hour(s)'},
            {'value': 8, 'unit': 'minute(s)'},
            {'value': 21, 'unit': 'second(s)'}
        ]
    """
    
    # Use the current date and time if end_date is not provided
    if end_date is None:
        end_date = datetime.datetime.now()
    
    # Calculate the time difference between the two dates
    time_difference = end_date - start_date
    
    time_passed_parts = []
    
    years = time_difference.days // 365
    time_passed_parts.append({'value': years, 'unit': _('year(s)')})
    
    # Adjust remaining days after accounting for years
    days_remaining = time_difference.days - (years * 365)
    
    months = days_remaining // 30
    time_passed_parts.append({'value': months, 'unit': _('month(s)')})
    
    days_remaining -= months * 30
    time_passed_parts.append({'value': days_remaining, 'unit': _('day(s)')})
    
    hours = time_difference.seconds // 3600
    time_passed_parts.append({'value': hours, 'unit': _('hour(s)')})
    
    # Adjust remaining seconds after accounting for hours
    seconds_remaining = time_difference.seconds - (hours * 3600)
    
    minutes = seconds_remaining // 60
    time_passed_parts.append({'value': minutes, 'unit': _('minute(s)')})
    
    seconds = seconds_remaining % 60
    time_passed_parts.append({'value': seconds, 'unit': _('second(s)')})
    
    return time_passed_parts



def parse_unix_time_to_gregorian(unix_timestamp):
    # create by: ayoub taneh (2024-08-07)
    """ 
    Example:
        print( parse_unix_time_to_gregorian(1690732299) )
    
    Output:
        {
        'year': 2023,
        'month': 7,
        'day': 30,
        'hour': 14,
        'minute': 51,
        'second': 39,
        'day_status': 'afternoon',
        'weekday': 'Sunday',
        'time_passed': [
            {'value': 1, 'unit': 'year(s)'},
            {'value': 1, 'unit': 'month(s)'},
            {'value': 2, 'unit': 'day(s)'},
            {'value': 21, 'unit': 'hour(s)'},
            {'value': 8, 'unit': 'minute(s)'},
            {'value': 21, 'unit': 'second(s)'}
        ]
    }
    """
    # Convert string to datetime object
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    
    # Determine the part of the day
    if 0 <= dt.hour < 6:
        day_status = _('night')
    elif 6 <= dt.hour < 12:
        day_status = _('morning')
    elif 12 <= dt.hour < 18:
        day_status = _('afternoon')
    else:
        day_status = _('evening')
        
    return {
        'year':         dt.year,
        'month':        dt.month,
        'day':          dt.day,
        'hour':         dt.hour,
        'minute':       dt.minute,
        'second':       dt.second,
        'day_status':   day_status,
        'weekday':      dt.strftime('%A'),
        'time_passed':  calculate_datetime_passed(dt)
    }



def parse_unix_time_to_Jalali(unix_timestamp):
    # create by: ayoub taneh (2024-08-07)
    """ 
    Example:
        print( parse_unix_time_to_Jalali(1690732299) )
    
    Output:
        {
        'year': 2023,
        'month': 7,
        'day': 30,
        'hour': 14,
        'minute': 51,
        'second': 39,
        'day_status': 'afternoon',
        'weekday': 'Sunday',
        'time_passed': [
            {'value': 1, 'unit': 'year(s)'},
            {'value': 1, 'unit': 'month(s)'},
            {'value': 2, 'unit': 'day(s)'},
            {'value': 21, 'unit': 'hour(s)'},
            {'value': 8, 'unit': 'minute(s)'},
            {'value': 21, 'unit': 'second(s)'}
        ]
    }
    """
    # Convert unix timestamp to Gregorian datetime
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    
    # Convert Gregorian datetime to Jalali datetime
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    
    # Determine the part of the day
    if 0 <= dt.hour < 6:
        day_status = _('night')
    elif 6 <= dt.hour < 12:
        day_status = _('morning')
    elif 12 <= dt.hour < 18:
        day_status = _('afternoon')
    else:
        day_status = _('evening')
        
    return {
        'year':       jdt.year,
        'month':      jdt.month,
        'day':        jdt.day,
        'hour':       jdt.hour,
        'minute':     jdt.minute,
        'second':     jdt.second,
        'day_status': day_status,
        'weekday':    dt.strftime('%A'),
        'time_passed': calculate_datetime_passed(dt)
    }



class UnixTimestampField(serializers.DateTimeField):
    # create by: V.MRP (2024-07-07)
    # update by: ayoub taneh (2024-09-07)
    def to_representation(self, value):
        """Convert a DateTime value to Unix timestamp.
        
        Example:
            Input: datetime.datetime(2024, 9, 19, 12, 0, 0) = 2024-09-19T12:00:00
            Output: 1695110400
        
        Args:
            value (datetime.datetime): The DateTime object to convert.

        Returns:
            int: The Unix timestamp.
        """
        if value is None:
            return None
        # Convert the datetime object to Unix timestamp
        return int(value.timestamp())

    def to_internal_value(self, data):
        """Convert a Unix timestamp or DateTime string to a DateTime value.
        
        Example:
            Input (Unix timestamp): 1695110400
            Output: datetime.datetime(2024, 9, 19, 12, 0, 0) = 2024-09-19T12:00:00
            
            Input (DateTime string): "2024-09-19T12:00:00Z"
            Output: datetime.datetime(2024, 9, 19, 12, 0, 0) = 2024-09-19T12:00:00
            
            Input (DateTime string): "2024-09-19 14:30:00"
            Output: datetime.datetime(2024, 9, 19, 12, 0, 0) = 2024-09-19T12:00:00
        
        Args:
            data (int or str): The Unix timestamp or DateTime string to convert.

        Returns:
            datetime.datetime: The DateTime object.

        Raises:
            serializers.ValidationError: If the input format is invalid.
        """
        if data is None:
            return None
        
        
        if isinstance(data, datetime.datetime):
            # If the input is already a DateTime object, return it directly.
            return data
        
        try:
            # Attempt to convert the input to a Unix timestamp.
            timestamp = int(data)
            return datetime.datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            # Attempt to parse the input as an ISO 8601 formatted DateTime string.
            try:
                # Handle ISO 8601 format with optional timezone offset
                return datetime.datetime.fromisoformat(data.replace('Z', '+00:00'))
            except ValueError:
                # Handle various date formats if needed
                try:
                    return datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise serializers.ValidationError("Invalid timestamp or date format")



# def letters_to_unidecode(name):
#     name = str(name).lower().strip()
#     name = re.sub(r'\-', '', slugify(unidecode(name)))
#     username = name
#     counter = 1
#     while models.User.objects.filter(username=username).exists():
#         username = name + str(counter)
#         counter += 1
#     return username


# class base64:
    
#     @staticmethod
#     def convert_image_to_base64(image_file):
#         with open(image_file.name, 'rb') as f:
#             image_data = f.read()
#         encoded_data = base64.b64encode(image_data).decode('utf-8')
#         return encoded_data
class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle Decimal conversion to float
        if isinstance(obj, Decimal):
            return float(obj)
        
        # Handle UUID conversion to string
        if isinstance(obj, UUID):
            return str(obj)
        
        # Handle Django FieldFile (and other file-like objects)
        if isinstance(obj, File):
            return obj.url if obj else None
        
        # Handle datetime conversion (aware and naive datetime handling)
        if isinstance(obj, datetime):
            if is_naive(obj):
                obj = make_aware(obj)
            return obj.isoformat()
        
        # Handle date conversion
        if isinstance(obj, date):
            return obj.isoformat()
        
        # Handle time conversion
        if isinstance(obj, time):
            return obj.isoformat()
        
        # Handle Django QuerySet conversion to list
        if isinstance(obj, QuerySet):
            return list(obj)
        
        # Handle Django Model conversion to dict (if __dict__ is available)
        if isinstance(obj, Model):
            return obj.__dict__
        
        # Handle sets (convert to list)
        if isinstance(obj, set):
            return list(obj)
        
        # Handle bytes (convert to string using UTF-8)
        if isinstance(obj, bytes):
            return obj.decode('utf-8')


def find_ip_address(request):
    """Extracts the IP address from the request."""
    # Check if request is a dictionary
    if isinstance(request, dict):
        # print('Request is a dictionary')
        headers = request.get('headers', {})
        # Extract IP address from X-Real-Ip or X-Forwarded-For headers
        ip_address = headers.get('X-Real-Ip') or headers.get('X-Forwarded-For')
    else:
        # print('Request is an HttpRequest')
        # Standard case where request is an HttpRequest
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            # print('IP found in X-Forwarded-For')
            # If multiple IPs exist, take the first one
            ip_address = ip_address.split(',')[0]
        else:
            # print('Using REMOTE_ADDR')
            # Otherwise, use REMOTE_ADDR to get the IP
            ip_address = request.META.get('REMOTE_ADDR')
                    
    # print(f"!!! ip_address: {ip_address}")    
    return ip_address
            

def remove_fields_from_request(request, field_names, remove_for_superuser=False):
    """
    Function to remove specified fields from the request data and return modified data,
    depending on whether user modifications are allowed for superusers.

    :param request: The HTTP request object containing request.data.
    :param field_names: A list of field names to be removed from request.data.
    :param remove_for_superuser: Boolean indicating if fields should be removed for superusers.
    :return: The modified request.data without the specified fields, based on superuser settings.
    """
    data = request.data.copy()
    
    if request.user.is_superuser and not remove_for_superuser:
        return data
    
    for field_name in field_names:
        if field_name in data:
            del data[field_name]
    return data


def custom_converter(o):
    if isinstance(o, UUID):
        return str(o)
    elif isinstance(o, SimpleNamespace):
        return o.__dict__
    raise TypeError

def get_position(user, biz_id, role_id):
    data_dict = json.loads(json.dumps(user, default=custom_converter))
    position_ids = []
    if data_dict['user_permissions']:
        user_permissions = data_dict['user_permissions']
        for perm_group in user_permissions:
            if biz_id in perm_group:
                for permission in perm_group[biz_id]:
                    if permission['business']['id'] == biz_id:
                        for position in permission['positions']:
                            if position['role']['id'] == role_id:
                                position_ids.append(position['id'])
    return position_ids