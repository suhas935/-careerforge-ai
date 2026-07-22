from django.db import models
from django.contrib.auth.models import User

class PlacementScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    overall_score = models.IntegerField(default=0)
    resume_score = models.IntegerField(default=0)
    skills_score = models.IntegerField(default=0)
    activity_score = models.IntegerField(default=0)
    readiness_level = models.CharField(max_length=50, blank=True)
    breakdown_json = models.TextField(blank=True)
    action_plan_json = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Score: {self.overall_score}"