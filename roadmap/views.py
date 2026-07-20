
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from resume.models import Resume
from services.claude_service import ask_claude
from .models import LearningRoadmap


@login_required
def roadmap_view(request):
    resume = Resume.objects.filter(user=request.user).last()
    last_roadmap = LearningRoadmap.objects.filter(user=request.user).last()
    roadmap = None

    if last_roadmap and last_roadmap.roadmap_json:
        try:
            roadmap = {
                "target_role": last_roadmap.target_role,
                "duration_weeks": last_roadmap.duration_weeks,
                "weeks": json.loads(last_roadmap.roadmap_json),
            }
        except:
            roadmap = None

    if request.method == "POST":
        if not resume:
            messages.error(request, "Please upload your resume first.")
            return redirect("resume_upload")

        target_role = request.POST.get("target_role", "").strip()
        duration_weeks = int(request.POST.get("duration_weeks", 8))

        if not target_role:
            messages.error(request, "Please enter a target role.")
            return redirect("roadmap")

        prompt = f"""
You are a technical career coach for computer science students in India.
Create a week-by-week learning roadmap for this student to become a {target_role}.

Duration: {duration_weeks} weeks

Return ONLY a valid JSON array of week objects. No explanation, no markdown, just raw JSON.
Each week object must have these exact keys:
- "week": week number (number)
- "title": theme for the week (string, e.g. "Python Fundamentals")
- "goal": what they should achieve by end of week (string)
- "tasks": list of 3-4 specific daily tasks (array of strings)
- "resource": one primary free resource with "name" and "url" keys
- "milestone": what they should build or complete as proof of learning (string)

Resume (to personalize based on existing skills):
{resume.extracted_text[:2000]}

Target Role: {target_role}
"""

        ai_response = ask_claude(prompt, max_tokens=3000)

        try:
            clean = ai_response.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            weeks = json.loads(clean.strip())

            LearningRoadmap.objects.create(
                user=request.user,
                target_role=target_role,
                duration_weeks=duration_weeks,
                roadmap_json=json.dumps(weeks),
            )

            return redirect("roadmap")

        except Exception as e:
            messages.error(request, "Could not generate roadmap. Please try again.")
            return redirect("roadmap")

    prefill_role = request.GET.get("role", "")
    return render(
        request,
        "roadmap/roadmap.html",
        {
            "resume": resume,
            "roadmap": roadmap,
            "last_roadmap": last_roadmap,
            "prefill_role": prefill_role,
        },
    )
