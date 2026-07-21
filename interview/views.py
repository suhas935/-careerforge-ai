import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from resume.models import Resume
from services.claude_service import ask_claude
from .models import InterviewSession


@login_required
def interview_view(request):
    resume = Resume.objects.filter(user=request.user).last()
    last_session = InterviewSession.objects.filter(user=request.user).last()
    questions = []

    if last_session and last_session.questions_json:
        try:
            questions = json.loads(last_session.questions_json)
        except:
            questions = []

    if request.method == "POST":
        if not resume:
            messages.error(request, "Please upload your resume first.")
            return redirect("resume_upload")

        target_role = request.POST.get("target_role", "").strip()
        difficulty = request.POST.get("difficulty", "Medium")

        if not target_role:
            messages.error(request, "Please enter a target role.")
            return redirect("interview")

        prompt = f"""
You are a senior technical interviewer at a top tech company in India.
Generate exactly 10 interview questions for a {target_role} position.
Difficulty level: {difficulty}

Return ONLY a valid JSON array of 10 question objects. No explanation, no markdown, just raw JSON.
Each object must have these exact keys:
- "question": the interview question (string)
- "category": one of "Technical", "DSA", "HR", "System Design" (string)
- "difficulty": one of "Easy", "Medium", "Hard" (string)
- "answer": a detailed model answer (string)
- "tip": one tip on how to answer this confidently in an interview (string)

Mix the categories: at least 4 Technical, 2 DSA, 2 HR, 2 System Design questions.

Resume context:
{resume.extracted_text[:2000]}
"""

        ai_response = ask_claude(prompt, max_tokens=3000)

        try:
            clean = ai_response.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            questions = json.loads(clean.strip())

            InterviewSession.objects.create(
                user=request.user,
                target_role=target_role,
                difficulty=difficulty,
                questions_json=json.dumps(questions),
            )

            return redirect("interview")

        except Exception as e:
            messages.error(request, "Could not generate questions. Please try again.")
            return redirect("interview")

    prefill_role = request.GET.get("role", "")
    return render(
        request,
        "interview/interview.html",
        {
            "resume": resume,
            "questions": questions,
            "last_session": last_session,
            "prefill_role": prefill_role,
        },
    )

@login_required
def chat_view(request):
    resume = Resume.objects.filter(user=request.user).last()
    last_session = InterviewSession.objects.filter(user=request.user).last()

    if request.method == 'POST':
        import json
        mode = request.POST.get('mode', 'qa')
        user_message = request.POST.get('message', '').strip()
        history = request.POST.get('history', '[]')
        role = request.POST.get('role', 'Software Developer')

        try:
            chat_history = json.loads(history)
        except:
            chat_history = []

        if mode == 'mock':
            system = f"""You are a strict but helpful technical interviewer at a top Indian tech company.
You are interviewing the candidate for a {role} position.
- Ask ONE interview question at a time
- After the candidate answers, give brief feedback (2-3 lines): what was good, what was missing
- Then ask the next question
- Mix Technical, DSA, HR, and System Design questions
- Keep feedback concise and constructive
- Start by introducing yourself and asking the first question"""
        else:
            system = f"""You are an expert interview coach helping a computer science student in India prepare for placements.
- Answer any question about interview preparation, coding, system design, HR questions
- Give practical, actionable advice
- Keep answers concise and focused
- Use examples where helpful
Resume context: {resume.extracted_text[:1000] if resume else 'Not provided'}"""

        messages_list = []
        for h in chat_history:
            messages_list.append({"role": h['role'], "content": h['content']})
        messages_list.append({"role": "user", "content": user_message})

        from groq import Groq
        import os
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system}] + messages_list,
            max_tokens=1000,
        )
        ai_reply = response.choices[0].message.content

        from django.http import JsonResponse
        return JsonResponse({'reply': ai_reply})

    return render(request, 'interview/chat.html', {
        'last_session': last_session,
        'resume': resume,
    })