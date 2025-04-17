from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    profile_bio = models.TextField(blank=True)
    facebook_link = models.URLField(blank=True)
    profile_image = models.ImageField(
        upload_to='profiles/', blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
