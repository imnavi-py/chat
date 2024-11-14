DATABASES = {
     'default': {
             # mysql or mariadb
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'chatuuid',
             'USER': 'root',
             'PASSWORD': '',
             'HOST': 'localhost',
             'PORT': '3306',
             'OPTIONS': {
                'charset': 'utf8mb4',  # استفاده از utf8mb4
                'init_command': "SET NAMES 'utf8mb4'",  # تنظیم نام‌ها به utf8mb4
             },
         }     
}