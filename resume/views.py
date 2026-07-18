

# Create your views here.
import PyPDF2
import io
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resume
from services.claude_service import ask_claude


def extract_text_from_pdf(file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        text = ""
    return text.strip()


@login_required
def resume_upload_view(request):
    resume = Resume.objects.filter(user=request.user).last()

    if request.method == "POST":
        uploaded_file = request.FILES.get("resume")
        if not uploaded_file:
            messages.error(request, "Please select a PDF file.")
            return redirect("resume_upload")

        if not uploaded_file.name.endswith(".pdf"):
            messages.error(request, "Only PDF files are allowed.")
            return redirect("resume_upload")

        # Extract text
        extracted_text = extract_text_from_pdf(uploaded_file)
        if not extracted_text:
            messages.error(
                request, "Could not extract text from PDF. Try another file."
            )
            return redirect("resume_upload")

        # Ask Claude to analyze
        prompt = f"""
You are an expert resume reviewer and career coach.
Analyze the following resume and return your response in this EXACT format:

SCORE: [number 0-100]
STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]
WEAKNESSES:
- [weakness 1]
- [weakness 2]
- [weakness 3]
FEEDBACK:
[2-3 paragraphs of detailed, actionable feedback]

Resume text:
{extracted_text}
"""
        ai_response = ask_claude(prompt, max_tokens=1500)

        # Parse Claude's response
        score = 0
        strengths = ""
        weaknesses = ""
        feedback = ""

        lines = ai_response.split("\n")
        section = None
        feedback_lines = []
        strength_lines = []
        weakness_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    score = int("".join(filter(str.isdigit, line.split("SCORE:")[1])))
                except:
                    score = 70
            elif line == "STRENGTHS:":
                section = "strengths"
            elif line == "WEAKNESSES:":
                section = "weaknesses"
            elif line == "FEEDBACK:":
                section = "feedback"
            elif line.startswith("-") and section == "strengths":
                strength_lines.append(line[1:].strip())
            elif line.startswith("-") and section == "weaknesses":
                weakness_lines.append(line[1:].strip())
            elif section == "feedback" and line:
                feedback_lines.append(line)

        strengths = "\n".join(strength_lines)
        weaknesses = "\n".join(weakness_lines)
        feedback = "\n".join(feedback_lines)

        # Reset file pointer and save
        uploaded_file.seek(0)
        resume_obj = Resume.objects.create(
            user=request.user,
            file=uploaded_file,
            extracted_text=extracted_text,
            ai_feedback=feedback,
            score=score,
            strengths=strengths,
            weaknesses=weaknesses,
        )

        return redirect("resume_result", pk=resume_obj.pk)

    return render(request, "resume/upload.html", {"resume": resume})


@login_required
def resume_result_view(request, pk):
    try:
        resume = Resume.objects.get(pk=pk, user=request.user)
    except Resume.DoesNotExist:
        messages.error(request, "Resume not found.")
        return redirect("resume_upload")

    # Score color
    if resume.score >= 75:
        score_color = "text-green-400"
    elif resume.score >= 50:
        score_color = "text-yellow-400"
    else:
        score_color = "text-red-400"

    strengths = [s for s in resume.strengths.split("\n") if s.strip()]
    weaknesses = [w for w in resume.weaknesses.split("\n") if w.strip()]

    return render(
        request,
        "resume/result.html",
        {
            "resume": resume,
            "score_color": score_color,
            "strengths": strengths,
            "weaknesses": weaknesses,
        },
    )
