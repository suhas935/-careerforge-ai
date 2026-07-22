from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("offer", "Offer"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    applied_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    job_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company} - {self.role} ({self.status})"

    class Meta:
        ordering = ["-updated_at"]
