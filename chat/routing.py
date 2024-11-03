from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r'cht/ws/chat/(?P<group_slug>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
    # path('ws/chat/private/<str:username>/', consumers.PrivateChatConsumer.as_asgi()),
    # re_path(r'ws/chat/private/(?P<username>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
    re_path(r'cht/ws/private_chat/(?P<username>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
    # re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    # path('ws/private_chat/<str:username>/', consumers.PrivateChatConsumer.as_asgi()),
    re_path(r'cht/ws/notifications/(?P<username>\w+)/$', consumers.NotificationConsumer.as_asgi()),  # سوکت برای اعلان‌ها
    
    
]
