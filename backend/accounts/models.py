from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

def avatar_upload_to(instance, filename):
    return f"avatars/{instance.id}/{filename}"

class User(AbstractUser):
    avatar = models.ImageField(upload_to=avatar_upload_to, null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=120, blank=True)

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen <= timezone.timedelta(minutes=5)
