# create by: ayoub taneh (2024-08-07)

class FaToEn:
    # create by: ayoub taneh (2024-08-07)
    def __init__(self):
        # یک دیکشنری گسترده‌تر برای نگهداری معادل‌های حروف
        self.dictionary = {
            "ا": "a",
            "ب": "b",
            "پ": "p",
            "ت": "t",
            "ث": "s",
            "ج": "j",
            "چ": "ch",
            "ح": "h",
            "خ": "kh",
            "د": "d",
            "ذ": "z",
            "ر": "r",
            "ز": "z",
            "ژ": "zh",
            "س": "s",
            "ش": "sh",
            "ص": "s",
            "ض": "z",
            "ط": "t",
            "ظ": "z",
            "ع": "a",
            "غ": "gh",
            "ف": "f",
            "ق": "gh",
            "ک": "k",
            "گ": "g",
            "ل": "l",
            "م": "m",
            "ن": "n",
            "و": "v",
            "ه": "h",
            "ی": "i"
        }

    def translate(self, persian_text):
        english_text = ""
        for char in persian_text:
            english_text += self.dictionary.get(char, '')
        return english_text

