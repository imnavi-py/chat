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
from asgiref.sync import sync_to_async
from django.utils.text import slugify






class GroupChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("alireza")
        self.group_slug = self.scope['url_route']['kwargs']['group_slug']
        
        # بررسی کاربر از scope
        self.user = self.scope['user']
        # print(self.scope)
        # print(self.user)

        if self.user.is_authenticated:
            print("User is connected:", self.user.username)
            await self.channel_layer.group_add(
                self.group_slug,
                self.channel_name
            )
            await self.accept()
            return

        # اگر کاربر احراز هویت نشده باشد، بررسی توکن در هدر
        self.token = self.extract_token_from_headers(self.scope['headers'])
        print("check from header")
        
        if not self.token:
            # اگر توکن در هدر موجود نبود، بررسی کوکی
            token = "e158683f3b006d332a05678729e6ce2f709ecad9"
            self.token = token
            # self.scope['cookies'].get('auth_token')
        
        # احراز هویت کاربر با توکن
        self.user = await self.get_user_from_token(self.token) if self.token else None
        
        if self.user is not None:
            print("User is connected:", self.user.username)
            await self.channel_layer.group_add(
                self.group_slug,
                self.channel_name
            )
            await self.accept()
        else:
            print("Invalid token or no token provided")
            await self.close()

    def extract_token_from_headers(self, headers):
        for header in headers:
            if header[0].decode("utf-8") == "authorization":
                return header[1].decode().replace("Token", "").strip()
        return None

    @sync_to_async
    def get_user_from_token(self, token):
        from rest_framework.authtoken.models import Token
        try:
            user_token = Token.objects.get(key=token)
            return user_token.user
        except Token.DoesNotExist:
            return None

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
        self.user = self.scope['user']

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

        if 'message' in data:

            
            message = data['message']
            sender = data['sender']
            recipient = data['recipient']  # Assuming you send recipient info with the message
            user_avatar_url = await self.get_user_avatar()
            timestamp = self.get_current_time()
            # print(f"recipient user: {recipient}")
            # print(f"Received message: {message}")  # این خط برای دیباگینگ اضافه شده است
            # print(f"Sender is: {sender}")
            # print(data)
            recipientuser = await self.get_user(recipient)
            await self.save_private_message(message,timestamp, recipientuser)
            # ارسال پیام به گروه
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.username,  # اضافه کردن نام کاربر
                    'sender': sender,
                    'recipient': recipient,
                    'avatar_url': user_avatar_url,
                }
            )


            # ارسال اعلان به کانال اعلان‌ها
            await self.channel_layer.group_send(
                f'notifications_{recipient}',
                {
                    'type': 'receive_notification',
                    'message': message,
                    'sender': sender,
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
    @database_sync_to_async
    def get_user(self, username):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.get(username=username)


    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        user_avatar_url = await self.get_user_avatar()


        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'avatar_url': user_avatar_url,
        }))




    async def private_message(self, event):
        message = event['message']
        sender = event['sender']
        recipient = event['recipient']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'type': 'private_message',
        }))
        
        # Here you can add the code to notify the recipient (if they are not connected)
        await self.send_notification(recipient)

    async def send_notification(self, recipient):
        # Send notification logic to the user here
        # This could be an alert or a WebSocket message depending on your implementation
        await self.channel_layer.group_send(
            f'notification_{recipient}',  # Group name for notifications
            {
                'type': 'user_notification',
                'message': f'You have a new message from {self.username}.',
            }
        )

    async def user_notification(self, event):
        message = event['message']
        # Here you would send the notification to the user, perhaps via WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message,
        }))

    @database_sync_to_async
    def get_user_avatar(self):
        # دریافت آواتار کاربر
        if self.user.is_authenticated:
            return self.user.userprofile.avatar.url if self.user.userprofile.avatar else '/static/profiles/default.png'
        return '/static/profiles/default.png'
    
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
    
    def get_current_time(self):
        import pytz
        from datetime import datetime
        tehran_tz = pytz.timezone('Asia/Tehran')
        return datetime.now(tehran_tz)
    
    # @database_sync_to_async
    # def save_message(self, message, timestamp,file_path=None):
    #     from .models import Message, Group

    #     # پیدا کردن یا ایجاد گروه
    #     group, created = Group.objects.get_or_create(name=self.room_group_name)
    
    #     Message.objects.create(
    #         user=self.user,
    #         group=Group.objects.get(name=self.room_group_name),
    #         content=message,
    #         file=file_path,  # Save the file path in the database
    #         timestamp=timestamp  # ذخیره زمان در پایگاه داده
    #     )


    @database_sync_to_async
    def save_private_message(self, message, timestamp, recipient_user, file_path=None):
        from .models import PrivateMessage, Group

        slug = slugify(self.room_group_name)
        group = Group.objects.filter(name=self.room_group_name, slug=slug).first()
        
        # اگر گروه وجود ندارد، آن را ایجاد می‌کنیم
        if not group:
            group = Group.objects.create(
                name=self.room_group_name,
                slug=slug,
                type='public',  # نوع گروه را مشخص کنید، مثلاً عمومی یا خصوصی
                created_by=self.user  # به عنوان کاربری که پیام می‌فرستد، گروه را ایجاد می‌کند
            )
            group.members.add(self.user)  # افزودن ایجاد کننده به اعضای گروه
        
        PrivateMessage.objects.create(
            sender=self.user,
            recipient=recipient_user,
            content=message if not file_path else '',
            file=file_path,
            timestamp=timestamp,
            group=Group.objects.get(name=group),
        )






class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'notifications_{self.username}'
        
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
        sender = data['sender']
        recipient = data['recipient']
        test = data['test']

        result = ""
        if test == 'akbar':
            result = "hello"
            # ارسال پیام hello به کاربر خاص
            await self.send_to_all_users(result)
        else:
            result = "no key"

        # ارسال پیام به گروه
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'receive_notification',
                'message': message,
                'sender': sender,
                'recipient': recipient,
                'test': result
            }
        )

    async def receive_notification(self, event):
        message = event.get("message")
        sender = event.get("sender")
        recipient = event.get("recipient", None)  # استفاده از get برای جلوگیری از خطا
        test = event.get("test")
        if recipient:
            await self.send(text_data=json.dumps({
                "message": message,
                "sender": sender,
                "recipient": recipient,
                "test": test
            }))

    async def send_to_all_users(self, message):
        # ارسال پیام به همه کاربران
        await self.channel_layer.group_send(
            'notifications',  # نام گروه عمومی
            {
                'type': 'receive_notification',
                'message': message,
                'sender': 'system',  # یا نام دیگر برای فرستنده
                'test': 'hello'  # یا هر مقداری که لازم است
            }
        )