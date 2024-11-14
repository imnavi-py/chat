# دیکشنری برای نگهداری پیش شماره‌های کارت و نام بانک‌ها
BANK_PREFIXES = {
    "603799": "بانک ملی ایران",
    "589210": "بانک سپه",
    "627648": "بانک توسعه صادرات",
    "627961": "بانک صنعت و معدن",
    "603770": "بانک کشاورزی",
    "628023": "بانک مسکن",
    "627760": "پست بانک ایران",
    "502908": "بانک توسعه تعاون",
    "627412": "بانک اقتصاد نوین",
    "622106": "بانک پارسیان",
    "502229": "بانک پاسارگاد",
    "639599": "بانک قوامین",
    "627488": "بانک کارآفرین",
    "621986": "بانک سامان",
    "639346": "بانک سینا",
    "639607": "بانک سرمایه",
    "504706": "بانک شهر",
    "502806": "بانک شهر",
    "502938": "بانک دی",
    "603769": "بانک صادرات",
    "610433": "بانک ملت",
    "627353": "بانک تجارت",
    "585983": "بانک تجارت",
    "589463": "بانک رفاه",
    "627381": "بانک انصار",
    "639370": "بانک مهر اقتصاد",
    "507677": "موسسه اعتباری نور",
    "628157": "موسسه اعتباری توسعه",
    "505801": "موسسه اعتباری کوثر",
    "606256": "موسسه اعتباری ملل (عسکریه)",
    "606373": "بانک قرض الحسنه مهرایرانیان"
}

def is_valid_card_number(card_number):
    """
    بررسی می‌کند که آیا شماره کارت 16 رقمی است، نام بانک را بازمی‌گرداند و اعتبارسنجی شماره کارت را انجام می‌دهد.
    """
    # بررسی 16 رقمی بودن شماره کارت
    if len(card_number) != 16:
        return False, None

    # بررسی شروع با اعداد 4، 5 یا 6
    if card_number[0] not in ('4', '5', '6'):
        return False, None

    # بررسی پیش شماره کارت و نام بانک
    bank_name = BANK_PREFIXES.get(card_number[:6], "نامشخص")

    total_sum = 0

    # الگوریتم لوهان (Luhn Algorithm) برای بررسی اعتبار کارت
    for i in range(16):
        digit = int(card_number[i])

        # اگر در موقعیت فرد هستیم (index از 0 شروع می‌شود، پس i+1 در نظر گرفته می‌شود)
        if (i + 1) % 2 != 0:
            digit *= 2
            # اگر عدد بیشتر از 9 شد، 9 واحد از آن کم می‌کنیم
            if digit > 9:
                digit -= 9

        # اعداد در موقعیت زوج به همان شکل باقی می‌مانند (ضرب در 1)
        total_sum += digit

    # بررسی بخش‌پذیری بر 10
    is_valid = total_sum % 10 == 0
    return is_valid, bank_name