from django.urls import path
from . import views

urlpatterns = [
    # routes will be added here in later phases
    path("", views.interview_view, name="interview"),
    path("chat/", views.chat_view, name="interview_chat"),
]
