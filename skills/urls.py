from django.urls import path
from . import views

urlpatterns = [
    # routes will be added here in later phases
    path("", views.skill_gap_view, name="skill_gap"),
]
