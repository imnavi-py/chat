from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model







class GroupChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_slug = self.scope['url_route']['kwargs']['group_slug']
        self.user = self.scope['user']

        await self.channel_layer.group_add(
            self.group_slug,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # ترک گروه
        await self.channel_layer.group_discard(
            self.group_slug,
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
                self.group_slug,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                    'avatar_url': user_avatar_url,
                }
            )
        
        elif 'file' in data:
            file_content = data['file']
            filename = data['filename']
            # ارسال فایل به گروه
            if file_content is not None and filename is not None:
            # ارسال فایل به گروه
                await self.channel_layer.group_send(
                    self.group_slug,
                    {
                        'type': 'chat_file',
                        'file': file_content,
                        'filename': filename,
                        'user': self.user.username,
                    }
                )
            else:
                # مدیریت خطا در صورت عدم وجود 'file' یا 'filename'
                print("Error: File or filename not provided.")

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
            group=Group.objects.get(slug=self.group_slug),  # یا روش دیگری برای دریافت گروه
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


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'private_{self.username}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # دریافت آواتار کاربر
        user_avatar_url = await self.get_user_avatar()

        # ارسال پیام به گروه خصوصی
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.scope['user'].username,
                'avatar_url': user_avatar_url
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        avatar_url = event['avatar_url']

        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'avatar_url': avatar_url,
        }))

    @database_sync_to_async
    def get_user_avatar(self):
        # دریافت آواتار کاربر از مدل UserProfile
        if self.scope['user'].is_authenticated:
            return self.scope['user'].userprofile.avatar.url if self.scope['user'].userprofile.avatar else '/static/profiles/default.png'
        return '/static/profiles/default.png'


