"""
ASGI config for chatapp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat import consumers
from chat.routing import websocket_urlpatterns
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path("ws/chat/<str:group_slug>/", consumers.GroupChatConsumer.as_asgi()),
                # path("ws/private_chat/<str:username>/", consumers.PrivateChatConsumer.as_asgi()),
            ]
        )
    ),
})
