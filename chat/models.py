from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='group_members')  # تغییر `related_name`

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
