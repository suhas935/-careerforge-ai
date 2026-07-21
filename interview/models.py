
from django.db import models
from django.contrib.auth.models import User


class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_role = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=20, default="Medium")
    questions_json = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.target_role} Interview"
