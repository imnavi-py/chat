import uuid
from django.conf import settings
from django.db import models

from django.utils.text import slugify
from datetime import datetime
from django.utils import timezone




class BaseUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nationalcode = models.CharField(max_length=100, unique=True)  # کد ملی یا شناسه‌های دیگر
    first_name_fa = models.CharField(max_length=50, null=True, blank=True)
    first_name_en = models.CharField(max_length=50, null=True, blank=True)
    last_name_fa = models.CharField(max_length=50, null=True, blank=True)
    last_name_en = models.CharField(max_length=50, null=True, blank=True)
    usr_avatar = models.CharField(max_length=200, null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    token = models.CharField(max_length=128, null=True, blank=True)  # اضافه کردن فیلد توکن
    def __str__(self):
        return self.first_name_fa or self.first_name_en


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)  # نامک گروه
    type = models.CharField(max_length=10, choices=[('public', 'عمومی'), ('private', 'خصوصی')])
    members = models.ManyToManyField(BaseUser, related_name='group_members')  # تغییر به BaseUser
    created_by = models.ForeignKey(BaseUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PrivateGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    members = models.ManyToManyField(BaseUser, related_name='private_group_members')
    created_by = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    target_user = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name="targetuser")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.content if self.content else 'File'}"


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.first_name_fa or self.user.first_name_en


class PrivateMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(BaseUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(BaseUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/private/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    pvgroup = models.ForeignKey(PrivateGroup, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.sender} to {self.recipient}: {self.content if self.content else 'File'}"