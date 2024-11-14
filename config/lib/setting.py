LANGUAGE_CODE = 'fa-ir'
LANGUAGES = [
    ('en', 'English'),
    ('fa', 'Farsi'),
]


TIME_ZONE = 'Asia/Tehran'

CORS_ALLOW_HEADERS = [
    'bizid',
    'roleid',
]

REST_FRAMEWORK = {
    
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'config.lib.authentication.TokenAuthentication',
    ],
    
    'DEFAULT_PERMISSION_CLASSES': [
        'config.lib.permissions.IsAuthenticated',  # IsAuthenticated | AllowAny
    ],
    
    'DEFAULT_THROTTLE_CLASSES': [
        'config.lib.throttling.CustomUserThrottle',
    ],
    
    'DEFAULT_THROTTLE_RATES': {
        'custom_user': '10/second',  # Set your desired rate limit here
    },
    
    'DEFAULT_PAGINATION_CLASS': 'config.lib.pagination.PageNumberPagination',
    'PAGE_SIZE': 10000,
    'MAX_PAGE_SIZE': 10000,
    'CURRENT_PAGE_NAME': 'current_page',
    'PAGE_SIZE_QUERY_PARAM': 'page_size',
    'TOTAL_PAGES_QUERY_PARAM': 'total_pages',
    
    'EXCEPTION_HANDLER': 'config.lib.exception_handler.custom_exception_handler' 
}


AUTH_TOKEN_VALIDITY = 144000             # by second (token expire time)
TOKEN_UPDATE_TIME = True               # update token expire time on every request
TOKEN_REFRESH = False                   # token refresh on every request


BIZ = {
    'max_allowed_creation': 1
}


VERSION = {
    'this_version': 2,
    'allowed_version': 1,
}


REDIS_CONFIG = {
    'host': '172.40.11.10',
    # 'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
    'password': '',
    'decode_responses': True
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'TIMEOUT': None,
        'LOCATION': f"redis://{REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # 'PASSWORD': env.REDIS_CONFIG['password'],
            'DECODE_RESPONSES': REDIS_CONFIG['decode_responses'],
        }
    }
}


API = {
    
    # in server
    'user_url': 'https://demo.nargil.co/usr/base-user/user-summery/',
    'user_var': 'user_ids',

    'biz_url': 'https://demo.nargil.co/biz/summary/',
    'biz_var': 'ids',
    
    'user_permission_url': 'https://demo.nargil.co/hcm/permission/user-permissions/',
    'user_permission_var': 'user_id',
    
    'permission_url': 'https://demo.nargil.co/hcm/permission/',
    'permission_var': 'permissions',

    'position_url': 'https://demo.nargil.co/hcm/position/summary/',
    'position_var': 'position_ids',

    'user_employee_url': 'https://demo.nargil.co/hcm/employee/brif/',
    'user_employee_var': ''
}

AUTH_USER_MODEL = 'chatapp.BaseUser'
APP_KEY = 'APPKEYroGfjjwmvRZDaOvInKjgqxsuRYlrM9H3bS61JMtqPUD4rzNfryN6ES0B0wCYz27f1497428ca4161a7a00ea62f41fe85'


CUSTOM_MIDDLEWARE = [
    'config.lib.middlewares.RequestMiddleware', #for log request    
    'config.lib.middlewares.ErrorLoggingMiddleware', #for log error
]

RABBITMQ_CONF = {
    'host' :'172.40.18.3',
    'user' :'backend',
    'pass' :'pAss',
    'port' :'5672',
}