
# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="resumes/")
    extracted_text = models.TextField(blank=True)
    ai_feedback = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Resume ({self.uploaded_at.date()})"
