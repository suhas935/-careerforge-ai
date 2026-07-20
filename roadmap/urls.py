from django.urls import path
from . import views

urlpatterns = [
    # routes will be added here in later phases
    path("", views.roadmap_view, name="roadmap"),
]
