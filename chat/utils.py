import pytz
import re
import hashlib



def convert_to_tehran_time(utc_dt):
    tehran_tz = pytz.timezone('Asia/Tehran')
    return utc_dt.astimezone(tehran_tz)




def convert_to_ascii(group_name):
    # تبدیل حروف فارسی به معادل‌های انگلیسی
    transliteration_map = {
        'ا': 'a', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ث': 's', 'ج': 'j', 'چ': 'ch', 
        'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'z', 'ر': 'r', 'ز': 'z', 'س': 's', 
        'ش': 'sh', 'ص': 's', 'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 
        'ف': 'f', 'ق': 'gh', 'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm', 'ن': 'n', 
        'و': 'v', 'ه': 'h', 'ی': 'y', 'ئ': 'y',  # 'ئ' به 'y' تبدیل می‌شود
    }
    
    # تبدیل حروف به معادل‌های انگلیسی
    converted_name = ''
    for char in group_name:
        if char in transliteration_map:
            converted_name += transliteration_map[char]
        else:
            converted_name += char  # اگر حروفی در نقشه نباشد، خودش را نگه می‌داریم

    # فقط حروف و اعداد و علامت‌های مجاز را نگه داریم
    return re.sub(r'[^a-zA-Z0-9._-]', '', converted_name)




def generate_private_chat_id(user1, user2):
    # نام کاربری‌ها را مرتب کنید تا اطمینان حاصل کنید که همیشه یک شناسه تولید می‌شود
    chat_id = ''.join(sorted([user1, user2]))
    # از hashlib برای تولید یک شناسه منحصر به فرد استفاده کنید
    return hashlib.sha256(chat_id.encode()).hexdigest()