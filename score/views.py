import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from resume.models import Resume
from skills.models import SkillGapAnalysis
from tracker.models import Application
from roadmap.models import LearningRoadmap
from services.claude_service import ask_claude
from .models import PlacementScore


@login_required
def score_view(request):
    # Gather all user data
    resume = Resume.objects.filter(user=request.user).last()
    skill_analysis = SkillGapAnalysis.objects.filter(user=request.user).last()
    applications = Application.objects.filter(user=request.user)
    roadmap = LearningRoadmap.objects.filter(user=request.user).last()
    last_score = PlacementScore.objects.filter(user=request.user).last()

    score_data = None
    if last_score and last_score.breakdown_json:
        try:
            score_data = {
                "overall_score": last_score.overall_score,
                "resume_score": last_score.resume_score,
                "skills_score": last_score.skills_score,
                "activity_score": last_score.activity_score,
                "readiness_level": last_score.readiness_level,
                "breakdown": json.loads(last_score.breakdown_json),
                "action_plan": json.loads(last_score.action_plan_json),
            }
        except:
            score_data = None

    if request.method == "POST":
        # Build context for Claude
        resume_text = resume.extracted_text[:1500] if resume else "No resume uploaded"
        resume_score = resume.score if resume else 0
        skill_readiness = skill_analysis.overall_readiness if skill_analysis else 0
        target_role = skill_analysis.target_role if skill_analysis else "Not specified"
        total_apps = applications.count()
        offers = applications.filter(status="offer").count()
        interviews = applications.filter(status="interview").count()
        has_roadmap = "Yes" if roadmap else "No"

        prompt = f"""
You are a placement readiness evaluator for computer science students in India.
Evaluate this student's placement readiness based on all available data.

DATA:
- Resume Score: {resume_score}/100
- Skill Gap Readiness: {skill_readiness}% for {target_role}
- Total Applications: {total_apps}
- Interviews Received: {interviews}
- Offers Received: {offers}
- Learning Roadmap Created: {has_roadmap}
- Resume Summary: {resume_text[:500]}

Return ONLY a valid JSON object. No explanation, no markdown, just raw JSON.
The object must have these exact keys:
- "overall_score": overall placement readiness 0-100 (number)
- "resume_score": resume quality score 0-100 (number)
- "skills_score": skills readiness score 0-100 (number)
- "activity_score": job search activity score 0-100 (number)
- "readiness_level": one of "Not Ready", "Getting Started", "On Track", "Almost There", "Placement Ready" (string)
- "breakdown": list of 4 category objects each with:
  - "category": name (string)
  - "score": score 0-100 (number)
  - "status": "Good", "Average", or "Needs Work" (string)
  - "comment": one line feedback (string)
- "action_plan": list of 5 prioritized action items each with:
  - "priority": number 1-5
  - "action": what to do (string)
  - "impact": "High", "Medium", or "Low" (string)
  - "timeframe": how long it will take (string)
"""

        ai_response = ask_claude(prompt, max_tokens=2000)

        try:
            clean = ai_response.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            result = json.loads(clean.strip())

            PlacementScore.objects.create(
                user=request.user,
                overall_score=result.get("overall_score", 0),
                resume_score=result.get("resume_score", 0),
                skills_score=result.get("skills_score", 0),
                activity_score=result.get("activity_score", 0),
                readiness_level=result.get("readiness_level", ""),
                breakdown_json=json.dumps(result.get("breakdown", [])),
                action_plan_json=json.dumps(result.get("action_plan", [])),
            )
            return redirect("placement_score")

        except Exception as e:
            messages.error(request, "Could not calculate score. Please try again.")
            return redirect("placement_score")

    return render(
        request,
        "score/score.html",
        {
            "resume": resume,
            "skill_analysis": skill_analysis,
            "applications": applications,
            "roadmap": roadmap,
            "score_data": score_data,
            "last_score": last_score,
            "total_apps": applications.count(),
            "offers": applications.filter(status="offer").count(),
            "interviews": applications.filter(status="interview").count(),
        },
    )
