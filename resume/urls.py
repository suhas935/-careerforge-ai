from django.urls import path
from . import views
from accounts.views import dashboard_view


urlpatterns = [
    # routes will be added here in later phases
    path("", dashboard_view, name="dashboard"),
    path("resume/", views.resume_upload_view, name="resume_upload"),
    path("resume/result/<int:pk>/", views.resume_result_view, name="resume_result"),
]
