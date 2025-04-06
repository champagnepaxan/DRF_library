from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    profile_picture = models.URLField(blank=True)
    favorite_genres = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.username

    @property
    def followers_count(self):
        return self.subscribers.count()

    @property
    def following_count(self):
        return self.subscriptions.count()
