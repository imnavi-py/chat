from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model







class GroupChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.user = self.scope['user']

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # ترک گروه
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if 'message' in data:
            message = data['message']

            # ذخیره‌سازی پیام در پایگاه داده
            await self.save_message(message)
        
            # فراخوانی تابع همزمان برای دریافت آواتار کاربر
            user_avatar_url = await self.get_user_avatar()

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                    'avatar_url': user_avatar_url,
                }
            )
        
        if 'file' in data:
            file_content = data['file']
            filename = data['filename']
            # ارسال فایل به گروه
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_file',
                    'file': file_content,
                    'filename': filename,
                    'user': self.user.username,
                }
            )

    @database_sync_to_async
    def get_user_avatar(self):
        # دریافت آواتار کاربر
        if self.user.is_authenticated:
            return self.user.userprofile.avatar.url if self.user.userprofile.avatar else '/static/profiles/default.png'
        return '/static/profiles/default.png'
    
    @database_sync_to_async
    def save_message(self, message):
        from .models import Message, Group
        # ذخیره‌سازی پیام در پایگاه داده
        Message.objects.create(
            user=self.user,
            group=Group.objects.get(name=self.group_name),  # یا روش دیگری برای دریافت گروه
            content=message
        )
    



    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        avatar_url = event['avatar_url']

        # ارسال پیام به وب‌ساکت
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'user': user,
            'avatar_url': avatar_url,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # فرمت تاریخ میلادی
        }))

    async def chat_file(self, event):
        file_content = event['file']
        filename = event['filename']
        user = event['user']

        # ارسال فایل به وب‌ساکت
        await self.send(text_data=json.dumps({
            'file': file_content,
            'filename': filename,
            'user': user,
        }))


    
    

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        avatar_url = event['avatar_url']

        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'avatar_url': avatar_url,
            
        }))




