from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Application


@login_required
def tracker_view(request):
    applications = Application.objects.filter(user=request.user)

    # Count by status
    stats = {
        "total": applications.count(),
        "applied": applications.filter(status="applied").count(),
        "shortlisted": applications.filter(status="shortlisted").count(),
        "interview": applications.filter(status="interview").count(),
        "offer": applications.filter(status="offer").count(),
        "rejected": applications.filter(status="rejected").count(),
    }

    # Group by status for kanban
    kanban = {
        "applied": applications.filter(status="applied"),
        "shortlisted": applications.filter(status="shortlisted"),
        "interview": applications.filter(status="interview"),
        "offer": applications.filter(status="offer"),
        "rejected": applications.filter(status="rejected"),
    }

    return render(
        request,
        "tracker/tracker.html",
        {
            "applications": applications,
            "stats": stats,
            "kanban": kanban,
        },
    )


@login_required
def add_application(request):
    if request.method == "POST":
        company = request.POST.get("company", "").strip()
        role = request.POST.get("role", "").strip()
        location = request.POST.get("location", "").strip()
        status = request.POST.get("status", "applied")
        notes = request.POST.get("notes", "").strip()
        job_url = request.POST.get("job_url", "").strip()

        if not company or not role:
            messages.error(request, "Company and Role are required.")
            return redirect("tracker")

        Application.objects.create(
            user=request.user,
            company=company,
            role=role,
            location=location,
            status=status,
            notes=notes,
            job_url=job_url,
        )
        messages.success(request, f"Application to {company} added!")
        return redirect("tracker")

    return redirect("tracker")


@login_required
def update_status(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Application.STATUS_CHOICES):
            app.status = new_status
            app.save()
    return redirect("tracker")


@login_required
def delete_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == "POST":
        app.delete()
        messages.success(request, "Application deleted.")
    return redirect("tracker")


@login_required
def edit_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == "POST":
        app.company = request.POST.get("company", app.company).strip()
        app.role = request.POST.get("role", app.role).strip()
        app.location = request.POST.get("location", app.location).strip()
        app.status = request.POST.get("status", app.status)
        app.notes = request.POST.get("notes", app.notes).strip()
        app.job_url = request.POST.get("job_url", app.job_url).strip()
        app.save()
        messages.success(request, "Application updated!")
    return redirect("tracker")

@login_required
def quick_add(request):
    if request.method == 'POST':
        company = request.POST.get('company', '').strip()
        role = request.POST.get('role', '').strip()
        job_url = request.POST.get('job_url', '').strip()

        if company and role:
            # Check if already exists
            existing = Application.objects.filter(
                user=request.user,
                company=company,
                role=role
            ).first()

            if existing:
                messages.warning(request, f'Already tracking {role} at {company}!')
            else:
                Application.objects.create(
                    user=request.user,
                    company=company,
                    role=role,
                    job_url=job_url,
                    status='applied',
                )
                messages.success(request, f'✅ {role} at {company} added to tracker!')

    return redirect('internships')