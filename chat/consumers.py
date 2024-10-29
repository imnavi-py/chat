import base64
from datetime import timezone
import os
import random
from venv import logger
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync







class GroupChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_slug = self.scope['url_route']['kwargs']['group_slug']
        self.user = self.scope['user']
        
        # Adding user to the group
        await self.channel_layer.group_add(
            self.group_slug,
            self.channel_name,
        )
        
        # Unique channel for the user
        self.user_channel_name = f"user-{self.user.username}"
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_slug,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if 'message' in data:
            message = data['message']
            timestamp = self.get_current_time()

            await self.save_message(message, timestamp)

            user_avatar_url = await self.get_user_avatar()

            await self.channel_layer.group_send(
                self.group_slug,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                    'avatar_url': user_avatar_url,
                    'timestamp': timestamp,
                }
            )

        elif 'file' in data:
            file_content = data['file']
            original_filename = data['filename']
            saved_filename = await self.save_file(file_content, original_filename)

            # Save the file path in the database
            await self.save_message('', self.get_current_time(), saved_filename)  # Empty message for file uploads

            # Send file information to the group
            await self.channel_layer.group_send(
                self.group_slug,
                {
                    'type': 'chat_file',
                    'file': f"{settings.MEDIA_URL}{saved_filename}",  # Updated URL for file
                    'filename': saved_filename,
                    'user': self.user.username,
                }
            )
        
        elif data['type'] == 'private_chat_request':
                recipient_username = data['recipient']
                recipient_channel = f"user-{recipient_username}"
                await self.channel_layer.send(
                    recipient_channel,
                    {
                        'type': 'private_chat_notification',
                        'sender': self.user.username,
                        'message': data.get('message', '')
                    }
                )
            
        elif data['type'] == 'user_click':
            target_username = data['username']
            await self.send_notification(target_username)

    @database_sync_to_async
    def get_user_avatar(self):
        # دریافت آواتار کاربر
        if self.user.is_authenticated:
            return self.user.userprofile.avatar.url if self.user.userprofile.avatar else '/static/profiles/default.png'
        return '/static/profiles/default.png'
    
    @database_sync_to_async
    def save_message(self, message, timestamp,file_path=None):
        from .models import Message, Group
        Message.objects.create(
            user=self.user,
            group=Group.objects.get(name=self.group_slug),
            content=message,
            file=file_path,  # Save the file path in the database
            timestamp=timestamp  # ذخیره زمان در پایگاه داده
        )
    
    def get_current_time(self):
        import pytz
        from datetime import datetime
        tehran_tz = pytz.timezone('Asia/Tehran')
        return datetime.now(tehran_tz)


    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        avatar_url = event['avatar_url']
        timestamp = event['timestamp']  # دریافت زمان

        # ارسال پیام به وب‌ساکت
        await self.send(text_data=json.dumps({
            # 'type': 'chat_message',
            'message': message,
            'user': user,
            'avatar_url': avatar_url,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')  # فرمت تاریخ میلادی
        }))

    async def chat_file(self, event):
        file_url = event['file']
        filename = event['filename']
        user = event['user']

        # Send file information to WebSocket
        await self.send(text_data=json.dumps({
            'file': file_url,
            'filename': filename,
            'user': user,
        }))

    
    @database_sync_to_async
    def save_file(self, file_content, original_filename):
        if file_content.startswith('data:'):
            header, file_content = file_content.split(',', 1)

        file_data = base64.b64decode(file_content)

        random_number = str(random.randint(100000, 999999))
        file_extension = os.path.splitext(original_filename)[1]
        filename = f"{random_number}{file_extension}"

        uploads_dir = os.path.join(settings.MEDIA_ROOT, 'static/files')
        os.makedirs(uploads_dir, exist_ok=True)

        file_path = os.path.join(uploads_dir, filename)

        with open(file_path, 'wb') as f:
            f.write(file_data)

        # Return the relative file path for database storage without 'static/files/'
        return f"static/files/{filename}"  # Corrected return value
    


    ## channel pv
    async def get_channel_for_user(self, username):
        # این تابع نام کانال مربوط به کاربر را برمی‌گرداند
        return f"chat-{username}"  # نام کانال کاربر
    


    @database_sync_to_async
    def send_notification(self, target_username):
        target_channel = f"user-{target_username}"
        notification_message = f"{self.user.username} has clicked on your name!"

        # ارسال اعلان به کانال کاربر هدف
        async_to_sync(self.channel_layer.send)(
            target_channel,
            {
                'type': 'notification',
                'message': notification_message,
                'sender': self.user.username
            }
        )

    async def notification(self, event):
        message = event['message']
        sender = event['sender']

        # ارسال پیام اعلان به وب‌ساکت
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message,
            'sender': sender
        }))



class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'private_chat_{self.username}'

        # ملحق شدن به گروه
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = data['sender']
        
        print(f"Received message: {message}")  # این خط برای دیباگینگ اضافه شده است
        print(f"Sender is: {sender}")
        
        # ارسال پیام به گروه
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.username,  # اضافه کردن نام کاربر
                'sender': sender,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))



