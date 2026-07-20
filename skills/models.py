
from django.db import models
from django.contrib.auth.models import User


class SkillGapAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_role = models.CharField(max_length=200)
    current_skills = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    recommendations_json = models.TextField(blank=True)
    overall_readiness = models.IntegerField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.target_role} Gap Analysis"
