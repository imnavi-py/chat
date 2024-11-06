from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from datetime import datetime
from django.utils import timezone





class Group(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)  # نامک گروه
    type = models.CharField(max_length=10, choices=[('public', 'عمومی'), ('private', 'خصوصی')])
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_members')  # تغییر `related_name`
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # ایجاد نامک از نام گروه
        if not self.slug:
            self.slug = slugify(self.name)  # یا می‌توانی از یک روش دیگری برای تولید نامک استفاده کنی
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class PrivateGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='private_group_members')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="creator")
    target_user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="targetuser")
    pv_url = models.CharField(max_length=100,null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # پر کردن pv_url به‌طور خودکار
        # if not self.pv_url:
        #     if self.target_user and self.created_by:
        #         if self.target_user.username == self.created_by.username:
        #             self.pv_url = self.created_by.username  # اگر target_user برابر با created_by باشد
        #         else:
        #             self.pv_url = self.target_user.username  # در غیر این صورت به target_user.username اختصاص می‌دهیم

        # # ذخیره‌سازی مدل با مقداردهی به pv_url
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content if self.content else 'File'}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username
    


class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/private/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    # group = models.ForeignKey(Group, on_delete=models.CASCADE)
    pvgroup = models.ForeignKey(PrivateGroup, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sender.username} to {self.recipient.username}: {self.content if self.content else 'File'}"
