DATABASES = {
     'default': {
             # mysql or mariadb
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'chat',
             'USER': 'root',
             'PASSWORD': 'aVt3.tdOUr]5j@2sz',
             'HOST': 'dev3.nargil.co',
             'PORT': '3306',
             'OPTIONS': {
                'charset': 'utf8mb4',  # استفاده از utf8mb4
                'init_command': "SET NAMES 'utf8mb4'",  # تنظیم نام‌ها به utf8mb4
             },
         }     
}