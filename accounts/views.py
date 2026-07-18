
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "accounts/register.html")

        user = User.objects.create_user(
            username=username, email=email, password=password1
        )
        Profile.objects.create(user=user)
        login(request, user)
        messages.success(request, f"Welcome to CareerForge, {username}!")
        return redirect("dashboard")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    return render(request, "dashboard/dashboard.html", {"profile": profile})
