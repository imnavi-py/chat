import base64
from datetime import timezone
import os
import random
import uuid
from venv import logger
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from django.utils.text import slugify
import redis










class GroupChatConsumer(AsyncWebsocketConsumer):



    async def connect(self):
        self.group_slug = self.scope['url_route']['kwargs']['group_slug']
        # Extract Token
        self.token = self.extract_token_from_headers_or_cookies()

        if not self.token:
            await self.close()
            return

        # Identity User With Token
        self.user = await self.get_user_from_token(self.token)

        if self.user is not None:
            print(f"User connected: {self.user.first_name_fa} {self.user.last_name_fa}")
            print("in user superuser ast ya na :", self.user.is_superuser)
            self.group_slug = self.scope['url_route']['kwargs']['group_slug']
            await self.channel_layer.group_add(
                self.group_slug,
                self.channel_name
            )
            await self.accept()
        else:
            print("Invalid token or user not authenticated")
            await self.close()

    

    # DC
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
            print(user_avatar_url)

            # send To Gp
            await self.channel_layer.group_send(
                self.group_slug,
                {
                    'type': 'chat_message',
                    'message': message,
                    # 'firstname': self.user.first_name_fa,
                    # 'lastname': self.user.last_name_fa,
                    'user_name': self.user.first_name_fa + " " + self.user.last_name_fa,
                    'avatar_url': user_avatar_url,
                    'timestamp': timestamp.isoformat(),  # تبدیل شیء datetime به رشته ISO 8601
                    'file': '',
                    'filename': ''
                }
            )


        elif 'file' in data:
            file_content = data['file']
            original_filename = data['filename']
            saved_filename = await self.save_file(file_content, original_filename)
            timestamp = self.get_current_time()
            user_avatar_url = await self.get_user_avatar()

            # Save the file path in the database
            await self.save_message('', self.get_current_time(), saved_filename)  # Empty message for file uploads

            # Send file information to the group
            await self.channel_layer.group_send(
                self.group_slug,
                {
                    'type': 'chat_file',
                    'message': '',
                    'file': f"{settings.MEDIA_URL}{saved_filename}",  # Updated URL for file
                    'filename': saved_filename,
                    'user_name': self.user.first_name_fa + " " + self.user.last_name_fa,
                    'avatar_url': user_avatar_url,
                    'timestamp': timestamp.isoformat(),  # تبدیل شیء datetime به رشته ISO 8601
                    
                }
            )
        
        # TODO 
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
                
        # TODO
        elif data['type'] == 'user_click':
            target_username = data['username']
            await self.send_notification(target_username)

    

    # Handler for Type Message
    async def chat_message(self, event):
        message = event['message'],
        # firstname = event['firstname'] ,
        # lastname = event['lastname'] ,
        user_name = event['user_name'],
        avatar_url = event['avatar_url'],
        timestamp = event['timestamp'],  # دریافت زمان
        file = ''
        filename = ''

        # Send to Socket
        await self.send(text_data=json.dumps({
            # 'type': 'chat_message',
            'message': message[0],
            # 'firstname': firstname,
            # 'lastname': lastname,
            'user_name': user_name[0],
            'avatar_url': avatar_url[0],
            'timestamp': timestamp[0], # فرمت تاریخ میلادی
            'file': file,
            'filename': filename
        }))

    # Handler for Type File
    async def chat_file(self, event):
        file_url = event['file']
        filename = event['filename']
        user_name = self.user.first_name_fa + " " + self.user.last_name_fa,
        avatar_url = event['avatar_url'],
        message = event['message'],
        timestamp = event['timestamp'],  # دریافت زمان

        # Send file information to WebSocket
        await self.send(text_data=json.dumps({
            'file': file_url,
            'filename': filename,
            'user_name': user_name[0],
            'avatar_url': avatar_url[0],
            'message': message[0],
            'timestamp': timestamp[0], # فرمت تاریخ میلادی

        }))

    
    # Save Type File
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
    

    
    ########################################################################## Functions ####################################################################

    # Extract Token Function
    def extract_token_from_headers_or_cookies(self):
        # Check Headers 
        token = None
        for header in self.scope['headers']:
            if header[0] == b'authorization':
                token = header[1].decode().split()[0]  # فرض بر این است که توکن به صورت 'Bearer <TOKEN>' است
                break

        # Check Cookies
        if not token:
            cookies = self.scope.get('cookies', {})
            token = cookies.get('token')  # فرض کنید توکن در کوکی به نام 'token' ذخیره شده باشد

        print(f"Token extracted: {token}")  # پرینت توکن استخراج شده
        return token

    # Find User From Token
    @database_sync_to_async
    def get_user_from_token(self, token):
        from chat.models import BaseUser

        try:
            user = BaseUser.objects.get(token=token)
            print(f"User found with token: {user.first_name_fa} {user.last_name_fa}") 
            return user
        except BaseUser.DoesNotExist:
            print("No user found with the given token") 
            return None
        
    
    # Get Avatar
    @database_sync_to_async
    def get_user_avatar(self):
        if self.user.token:
            return self.user.usr_avatar if self.user.usr_avatar else '/static/profiles/default.png'
        return '/static/profiles/default.png'
    
    # Save Type Message
    @database_sync_to_async
    def save_message(self, message, timestamp,file_path=None):
        from .models import Message, Group
        print(self.group_slug)
        Message.objects.create(
            user=self.user,
            group=Group.objects.get(name=self.group_slug),
            content=message,
            file=file_path,  # Save the file path in the database
            timestamp=timestamp  # ذخیره زمان در پایگاه داده
        )
    
    # Get Time
    def get_current_time(self):
        import pytz
        from datetime import datetime
        tehran_tz = pytz.timezone('Asia/Tehran')
        return datetime.now(tehran_tz)

#########################################################################################################################################################





class PrivateChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'{self.username}'

        # Get Token
        self.token = self.extract_token_from_headers_or_cookies()

        if not self.token:
            await self.close()
            return

        self.user = await self.get_user_from_token(self.token)

        if self.user is not None:
            print(f"Private User is : {self.user.first_name_fa} {self.user.last_name_fa}")

            self.username = self.scope['url_route']['kwargs']['username']
            await self.channel_layer.group_add(
                self.username,
                self.channel_name
            )
            await self.accept()
        else:
            print("Invalid token or user not authenticated")
            await self.close()


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
            sender = self.user.first_name_fa + self.user.last_name_fa
            # print(sender)
            # sender = "admin"
            recipient = data['recipient']  # Assuming you send recipient info with the message
            # print(recipient)
            # recipient = "user"

            user_avatar_url = await self.get_user_avatar()
            timestamp = self.get_current_time()
            # print(f"recipient user: {recipient}")
            # print(f"Received message: {message}")  # این خط برای دیباگینگ اضافه شده است
            # print(f"Sender is: {sender}")
            # print(data)
            recipientuser = await self.get_user_from_uuid(recipient)
            await self.save_private_message(message,timestamp, recipientuser)
            # ارسال پیام به گروه
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.username,  # اضافه کردن نام کاربر
                    'sender': sender,
                    'recipient': recipientuser.first_name_fa +" "+ recipientuser.last_name_fa,
                    'avatar_url': user_avatar_url,
                }
            )
            print(recipientuser)


            # ارسال اعلان به کانال اعلان‌ها
            await self.channel_layer.group_send(
                f'notifications_{recipient}',
                {
                    'type': 'receive_notification',
                    'message': message,
                    'sender': sender,
                    'recipient': recipientuser
                }
            )

        elif 'file' in data:
            file_content = data['file']
            original_filename = data['filename']
            saved_filename = await self.save_file(file_content, original_filename)
            sender = self.user.first_name_fa + self.user.last_name_fa,
            recipient = data['recipient'] 


            print("in recipient: " , recipient)

            recipientuser = await self.get_user_from_uuid(recipient)

            print("in recipientuser: ", recipientuser)

            user_avatar_url = await self.get_user_avatar()
            # Save the file path in the database
            await self.save_message('', self.get_current_time(), saved_filename,)  # Empty message for file uploads

            # Send file information to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_file',
                    'file': f"{settings.MEDIA_URL}{saved_filename}",  # Updated URL for file
                    'filename': saved_filename,
                    'sender': self.user.first_name_fa + self.user.last_name_fa,
                    'recipientuser': recipientuser.first_name_fa + recipientuser.last_name_fa,
                    'avatar_url': user_avatar_url,

                }
            )

    
    
    # Handler for Type File
    async def chat_file(self, event):
        
        file_url = event['file']
        filename = event['filename']
        sender = self.user.first_name_fa + self.user.last_name_fa
        recipientuser = event['recipientuser']
        user_avatar_url = await self.get_user_avatar()


        # Send To Socket
        await self.send(text_data=json.dumps({
            'type': 'chat_file',
            'file': file_url,
            'filename': filename,
            'recipientuser': recipientuser,
            'sender' : sender,
            'avatar_url': user_avatar_url
        }))

    # Save Type Message
    @database_sync_to_async
    def save_message(self, message, timestamp, file_path=None):
        from .models import PrivateMessage, PrivateGroup

        # Find PV
        private_group = PrivateGroup.objects.get(name=self.room_group_name)
        # Find Sender
        sender = self.user 
        # Find Recipient
        recipient = private_group.target_user 
        # Save Message
        PrivateMessage.objects.create(
            sender=sender,
            recipient=recipient,
            content=message,
            file=file_path,  # مسیر فایل
            timestamp=timestamp,  # زمان پیام
            pvgroup=private_group  # اشاره به گروه خصوصی
        )

        
    # Handler for Type Message
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        user_avatar_url = await self.get_user_avatar()
        recipient = event['recipient']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'avatar_url': user_avatar_url,
            'recipient': recipient
        }))

        

    # Handler for Type File
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
    

    # Save Message & File
    @database_sync_to_async
    def save_private_message(self, message, timestamp, recipient_user, file_path=None):
        from .models import PrivateMessage
        from chat.models import PrivateGroup
        slug = slugify(self.room_group_name)
        group = PrivateGroup.objects.filter(name=self.room_group_name, slug=slug).first()
        
        # if not Exist , Create It first
        if not group:
            group = PrivateGroup.objects.create(
                name=self.room_group_name,
                slug=slug,
                # type='public',  # نوع گروه را مشخص کنید، مثلاً عمومی یا خصوصی
                created_by=self.user,  # به عنوان کاربری که پیام می‌فرستد، گروه را ایجاد می‌کند
                target_user = recipient_user
            )
            group.members.add(self.user)  # افزودن ایجاد کننده به اعضای گروه
            group.members.add(recipient_user)  # افزودن ایجاد کننده به اعضای گروه
        
        PrivateMessage.objects.create(
            sender=self.user,
            recipient=recipient_user,
            content=message if not file_path else '',
            file=file_path,
            timestamp=timestamp,
            pvgroup=PrivateGroup.objects.get(name=group),
        )


############################################################################# Function ##############################################################################


    # Extract Token Function
    def extract_token_from_headers_or_cookies(self):
        
        token = None
        # Check Headers
        for header in self.scope['headers']:
            if header[0] == b'authorization':
                token = header[1].decode().split()[0]  # فرض بر این است که توکن به صورت 'Bearer <TOKEN>' است
                break

        # Check Cookies
        if not token:
            cookies = self.scope.get('cookies', {})
            token = cookies.get('token')  # فرض کنید توکن در کوکی به نام 'token' ذخیره شده باشد

        print(f"Token extracted: {token}")  # پرینت توکن استخراج شده
        return token

    # Find token From Token
    @database_sync_to_async
    def get_user_from_token(self, token):
        from chat.models import BaseUser

        try:
            # جستجوی کاربر با استفاده از توکن
            user = BaseUser.objects.get(token=token)
            print(f"User found with token: {user.first_name_fa} {user.last_name_fa}")  # پرینت نام کاربر
            return user
        except BaseUser.DoesNotExist:
            print("No user found with the given token")  # پرینت زمانی که کاربر یافت نشود
            return None
        
    # Get Time
    def get_current_time(self):
        import pytz
        from datetime import datetime
        tehran_tz = pytz.timezone('Asia/Tehran')
        return datetime.now(tehran_tz)
    

    # Here you can add the code to notify the recipient (if they are not connected)
    # await self.send_notification(recipient)

    # TODO
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

    # TODO
    async def user_notification(self, event):
        message = event['message']
        # Here you would send the notification to the user, perhaps via WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message,
        }))


    # Get Avatar
    @database_sync_to_async
    def get_user_avatar(self):
        # دریافت آواتار کاربر
        if self.user:
            print("url avatar", self.user.userprofile.avatar)
            return self.user.usr_avatar if self.user.usr_avatar else '/static/profiles/default.png'
        return '/static/profiles/default.png'
    

    # Find User From UUID
    @database_sync_to_async
    def get_user_from_uuid(self, uuid):
        from chat.models import BaseUser

        try:
            user = BaseUser.objects.get(id=uuid)
            print(f"User found with token: {user.first_name_fa} {user.last_name_fa}")  # پرینت نام کاربر
            return user
        except BaseUser.DoesNotExist:
            print("No user found with the given token")  # پرینت زمانی که کاربر یافت نشود
            return None


####################################################################################################################################################################



class NotificationConsumer(AsyncWebsocketConsumer):
    # Online User's List
    online_users = {}

    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'{self.username}'

        # استخراج توکن از هدر یا کوکی
        self.token = self.extract_token_from_headers_or_cookies()

        if not self.token:
            await self.close()
            return

        # احراز هویت کاربر با استفاده از توکن و بازیابی اطلاعات او
        self.user = await self.get_user_from_token(self.token)

        if self.user is not None:
            print(f"User connected: {self.user.first_name_fa} {self.user.last_name_fa}")

            # ذخیره UUID و توکن کاربر در لیست آنلاین‌ها
            self.user_uuid = str(self.user.id)
            self.user_namefa= str(self.user.last_name_fa)  # فرض کنید UUID کاربر در `user.uuid` ذخیره شده است
            NotificationConsumer.online_users[self.user_uuid] = {'channel_name': self.channel_name, 'lastname': self.user_namefa}

            await self.channel_layer.group_add(
                self.username,
                self.channel_name
            )

            # تایید اتصال سوکت
            await self.accept()

            # ارسال لیست آنلاین‌ها پس از تایید اتصال
            await self.update_online_users()

        else:
            print("Invalid token or user not authenticated")
            await self.close()

    async def disconnect(self, close_code):
        # حذف UUID کاربر از لیست آنلاین‌ها هنگام قطع ارتباط
        if hasattr(self, 'user_uuid'):
            del NotificationConsumer.online_users[self.user_uuid]

        # ارسال به روز رسانی لیست آنلاین‌ها به کاربران متصل
        await self.update_online_users()

        # ارسال پیام به بقیه کاربران که کاربر از سوکت قطع شده است
        await self.send_to_all_users(f'{self.user.first_name_fa} {self.user.last_name_fa} has disconnected.')

        # حذف کاربر از گروه
        await self.channel_layer.group_discard(
            self.username,
            self.channel_name
        )

    

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = self.user.first_name_fa + " " + self.user.last_name_fa
        recipient = data['recipient']
        title = data['title']
        

        result = ""
        rec_id = None  # مقدار پیش‌فرض برای rec_id

        if title == 'private_msg':
            result = "pv"
            # بررسی اینکه recipient یک UUID معتبر است
            try:
                # تبدیل recipient به UUID برای بررسی صحت آن
                recipient_uuid = uuid.UUID(recipient)
                rec_id = str(recipient_uuid)  # تبدیل UUID به رشته
            except ValueError:
                # اگر recipient قابل تبدیل به UUID نباشد، rec_id را None نگه می‌داریم
                rec_id = None
            
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
                'title': result,
                'avatar_url': await self.get_user_avatar(),
                'rec_id':rec_id
            }
        )



############################################################################## Function #############################################################################

    async def update_online_users(self):
        # ارسال لیست UUID کاربران آنلاین همراه با توکن‌ها و تعداد کاربران آنلاین
        online_users = []
        for user_uuid, data in NotificationConsumer.online_users.items():
            online_users.append({
                'uuid': user_uuid,
                'lastname': data['lastname']
            })

        # تعداد کاربران آنلاین
        online_count = len(NotificationConsumer.online_users)

        # ارسال پیام به تمام کاربران متصل
        await self.channel_layer.group_send(
            self.username,  # ارسال به گروه مربوط به این کاربر
            {
                'type': 'send_online_users',
                'online_users': online_users,
                'online_count': online_count
            }
        )

    async def send_online_users(self, event):
        # این متد به تمام کاربرانی که به گروه متصل هستند، داده‌های آنلاین را ارسال می‌کند
        await self.send(text_data=json.dumps({
            'online_users': event['online_users'],
            'online_count': event['online_count']
        }))

    @database_sync_to_async
    def get_user_avatar(self):
        # دریافت آواتار کاربر
        if self.user:
            print("url avatar", self.user.userprofile.avatar)
            return self.user.usr_avatar if self.user.usr_avatar else '/static/profiles/default.png'
        return '/static/profiles/default.png'


    async def receive_notification(self, event):
        message = event.get("message")
        sender = event.get("sender")
        recipient = event.get("recipient", None)  # استفاده از get برای جلوگیری از خطا
        title = event.get("title")
        user_avatar_url = await self.get_user_avatar()

        # تبدیل رشته rec_id به UUID در سمت گیرنده
        rec_id = uuid.UUID(event.get("rec_id")) if event.get("rec_id") else None

        if recipient:
            rec_id_str = str(event.get("rec_id"))
            await self.send(text_data=json.dumps({
                "message": message,
                "sender": sender,
                "recipient": recipient,
                "title": title,
                "avatar_url": user_avatar_url,
                "rec_id": rec_id_str  # ارسال UUID به عنوان rec_id
            }))

    async def send_to_all_users(self, message):
        # ارسال پیام به همه کاربران
        await self.channel_layer.group_send(
            'notifications',  # نام گروه عمومی
            {
                'type': 'receive_notification',
                'message': message,
                'sender': 'system',  # یا نام دیگر برای فرستنده
                'title': 'hello'  # یا هر مقداری که لازم است
            }
        )



    def extract_token_from_headers_or_cookies(self):
        # بررسی هدر 'authorization' برای استخراج توکن
        token = None
        for header in self.scope['headers']:
            if header[0] == b'authorization':
                token = header[1].decode().split()[0]  # فرض بر این است که توکن به صورت 'Bearer <TOKEN>' است
                break

        # اگر توکن از هدر پیدا نشد، از کوکی‌ها جستجو می‌کنیم
        if not token:
            cookies = self.scope.get('cookies', {})
            token = cookies.get('token')  # فرض کنید توکن در کوکی به نام 'token' ذخیره شده باشد

        print(f"Token extracted: {token}")  # پرینت توکن استخراج شده
        return token

    @database_sync_to_async
    def get_user_from_token(self, token):
        from chat.models import BaseUser

        try:
            # جستجوی کاربر با استفاده از توکن
            user = BaseUser.objects.get(token=token)
            print(f"User found with token: {user.first_name_fa} {user.last_name_fa}")  # پرینت نام کاربر
            return user
        except BaseUser.DoesNotExist:
            print("No user found with the given token")  # پرینت زمانی که کاربر یافت نشود
            return None

    @database_sync_to_async
    def mark_online(self):
        # ذخیره کانال کاربر در مجموعه آنلاین‌ها در Redis
        redis_client = redis.StrictRedis(host='172.40.11.10', port=6379, db=0, decode_responses=True)
        redis_client.sadd('online_users', self.channel_name)  # اضافه کردن کانال به مجموعه آنلاین‌ها

    @database_sync_to_async
    def get_online_users_from_redis(self):
        # دریافت لیست کاربران آنلاین از Redis
        redis_client = redis.StrictRedis(host='172.40.11.10', port=6379, db=0, decode_responses=True)
        online_users = redis_client.smembers('online_users')  # اعضای مجموعه آنلاین‌ها
        return list(online_users)

    @database_sync_to_async
    def get_online_user_count(self):
        # شمارش تعداد کاربران آنلاین در Redis
        redis_client = redis.StrictRedis(host='172.40.11.10', port=6379, db=0, decode_responses=True)
        online_user_count = redis_client.scard('online_users')  # تعداد اعضای مجموعه آنلاین‌ها
        return online_user_count
    

###################################################################################################################################################################

