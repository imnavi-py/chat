import pytz

def convert_to_tehran_time(utc_dt):
    tehran_tz = pytz.timezone('Asia/Tehran')
    return utc_dt.astimezone(tehran_tz)