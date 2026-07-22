from django.urls import path
from . import views

urlpatterns = [
    # routes will be added here in later phases
    path("", views.tracker_view, name="tracker"),
    path("add/", views.add_application, name="add_application"),
    path('quick-add/', views.quick_add, name='quick_add'),
    path("update/<int:pk>/", views.update_status, name="update_status"),
    path("delete/<int:pk>/", views.delete_application, name="delete_application"),
    path("edit/<int:pk>/", views.edit_application, name="edit_application"),
]
