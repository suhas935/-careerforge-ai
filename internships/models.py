from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class InternshipRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_role = models.CharField(max_length=200, blank=True)
    recommendations_json = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Internship Reco ({self.generated_at.date()})"
