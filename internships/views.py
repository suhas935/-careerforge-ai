from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from resume.models import Resume
from services.claude_service import ask_claude
from .models import InternshipRecommendation


@login_required
def internship_view(request):
    resume = Resume.objects.filter(user=request.user).last()
    last_reco = InternshipRecommendation.objects.filter(user=request.user).last()
    recommendations = []

    if last_reco and last_reco.recommendations_json:
        try:
            recommendations = json.loads(last_reco.recommendations_json)
        except:
            recommendations = []

    if request.method == "POST":
        if not resume:
            messages.error(request, "Please upload your resume first.")
            return redirect("resume_upload")

        target_role = request.POST.get("target_role", "").strip()

        prompt = f"""
You are a career advisor for computer science students in India.
Based on the resume below, recommend exactly 5 internship roles.

Target role preference: {target_role if target_role else 'Not specified, suggest best matches'}

Return ONLY a valid JSON array with exactly 5 objects. No explanation, no markdown, just raw JSON.
Each object must have these exact keys:
- "title": job title (string)
- "company_type": type of company (string, e.g. "Product Startup", "MNC", "Service Company")
- "match_percent": how well resume matches this role (number 0-100)
- "required_skills": list of 4 skills needed (array of strings)
- "missing_skills": list of 2-3 skills the candidate lacks (array of strings)
- "apply_tip": one specific actionable tip to get this internship (string)
- "platforms": list of 2-3 platforms with direct search links as objects with "name" and "url" keys
Example: [{{"name": "Internshala", "url": "https://internshala.com/internships/keyword-internship"}}, {{"name": "Naukri", "url": "https://www.naukri.com/keyword-internship-jobs-in-india"}}, {{"name": "LinkedIn India", "url": "https://www.linkedin.com/jobs/search/?keywords=keyword+intern&location=India"}}, {{"name": "Foundit", "url": "https://www.foundit.in/srp/results?query=keyword+internship"}}, {{"name": "Unstop", "url": "https://unstop.com/internships?search=keyword"}}, {{"name": "Indeed India", "url": "https://in.indeed.com/jobs?q=keyword+internship&l=India"}}]
  Use ONLY these 6 Indian platforms. Pick the 2-3 most relevant ones per role and generate real search URLs by replacing 'keyword' with the actual job title keywords.
Resume:
{resume.extracted_text[:3000]}
"""

        ai_response = ask_claude(prompt, max_tokens=2000)

        # Parse JSON from response
        try:
            # Clean response in case of any markdown
            clean = ai_response.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            recommendations = json.loads(clean.strip())

            InternshipRecommendation.objects.create(
                user=request.user,
                target_role=target_role,
                recommendations_json=json.dumps(recommendations),
            )
        except Exception as e:
            messages.error(
                request, "Could not parse recommendations. Please try again."
            )
            return redirect("internships")

        return redirect("internships")

    return render(
        request,
        "internships/internships.html",
        {
            "resume": resume,
            "recommendations": recommendations,
            "last_reco": last_reco,
        },
    )
