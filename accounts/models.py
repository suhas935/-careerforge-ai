from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    target_role = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=200, blank=True)
    graduation_year = models.CharField(max_length=4, blank=True)
    skills = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
