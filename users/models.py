from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_img = models.CharField(max_length=1000, default='')
    otp = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"