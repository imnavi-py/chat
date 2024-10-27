from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify



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
