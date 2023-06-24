from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser



# Create your models here.
class Chat(models.Model):
    chat_name = models.CharField(max_length=20, unique=True)
    chat_creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.chat_name

class Message(models.Model):
    chat_name = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    user_name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class User(AbstractUser):
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friend')
