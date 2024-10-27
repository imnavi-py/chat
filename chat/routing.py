from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<group_slug>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
    # path('ws/chat/private/<str:username>/', consumers.PrivateChatConsumer.as_asgi()),
    re_path(r'ws/chat/private/(?P<username>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
    
]
