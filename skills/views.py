# Create your views here.
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from httpx import request
from resume.models import Resume
from services.claude_service import ask_claude
from .models import SkillGapAnalysis


@login_required
def skill_gap_view(request):
    resume = Resume.objects.filter(user=request.user).last()
    last_analysis = SkillGapAnalysis.objects.filter(user=request.user).last()
    analysis = None

    if last_analysis and last_analysis.recommendations_json:
        try:
            analysis = {
                "target_role": last_analysis.target_role,
                "overall_readiness": last_analysis.overall_readiness,
                "current_skills": json.loads(last_analysis.current_skills),
                "missing_skills": json.loads(last_analysis.missing_skills),
                "recommendations": json.loads(last_analysis.recommendations_json),
            }
        except:
            analysis = None

    if request.method == "POST":
        if not resume:
            messages.error(request, "Please upload your resume first.")
            return redirect("resume_upload")

        target_role = request.POST.get("target_role", "").strip()
        if not target_role:
            messages.error(request, "Please enter a target role.")
            return redirect("skill_gap")

        prompt = f"""
You are a technical career advisor for computer science students in India.
Analyze the skill gap between this resume and the target role.

Target Role: {target_role}

Return ONLY a valid JSON object. No explanation, no markdown, just raw JSON.
The object must have these exact keys:
- "overall_readiness": percentage ready for the role (number 0-100)
- "current_skills": list of skills the candidate already has relevant to this role (array of strings)
- "missing_skills": list of skills they are missing for this role (array of strings)
- "recommendations": list of 5 skill objects to learn, each with:
  - "skill": skill name (string)
  - "priority": "High", "Medium", or "Low" (string)
  - "reason": why this skill is important for the role (string)
  - "resource": one free learning resource with name and url as object with "name" and "url" keys
    Example: {{"name": "freeCodeCamp", "url": "https://www.freecodecamp.org"}}
  - "time_to_learn": estimated time (string, e.g. "2 weeks", "1 month")

Resume:
{resume.extracted_text[:3000]}
"""

        ai_response = ask_claude(prompt, max_tokens=2000)

        try:
            clean = ai_response.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            result = json.loads(clean.strip())

            SkillGapAnalysis.objects.create(
                user=request.user,
                target_role=target_role,
                overall_readiness=result.get("overall_readiness", 0),
                current_skills=json.dumps(result.get("current_skills", [])),
                missing_skills=json.dumps(result.get("missing_skills", [])),
                recommendations_json=json.dumps(result.get("recommendations", [])),
            )

            return redirect("skill_gap")

        except Exception as e:
            messages.error(request, "Could not analyze skill gap. Please try again.")
            return redirect("skill_gap")

    prefill_role = request.GET.get("role", "")
    return render(
    request,
    "skills/skill_gap.html",
    {
        "resume": resume,
        "analysis": analysis,
        "last_analysis": last_analysis,
        "prefill_role": prefill_role,
    },
)
