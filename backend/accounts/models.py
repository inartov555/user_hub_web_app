from django.contrib.auth.models import AbstractUser
from django.db import models

def avatar_upload_to(instance, filename):
    return f"profiles/{instance.id}/{filename}"

class User(AbstractUser):
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=64, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
