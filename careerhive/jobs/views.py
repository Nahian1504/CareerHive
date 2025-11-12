import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .scraper import get_jobs
from .models import Job, Bookmark, Application, Resume
from .utils import resume_parser
from .ai_helper import suggest_jobs
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

# Home view with resume skill-based job matching
@login_required
def home(request):
    query = request.GET.get("search", "")
    location_filter = request.GET.get("location", "")
    source_filter = request.GET.get("source", "")
    sort_by = request.GET.get("sort", "title")
    page_number = request.GET.get("page", 1)

    # Get all uploaded resumes for the user
    user_resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")

    # Collect all skills from user's resumes
    resume_skills = []
    for resume in user_resumes:
        if resume.extracted_skills:
            resume_skills += resume.extracted_skills.split(",")

    # Scrape jobs if query exists
    if query:
        jobs = get_jobs(query, location_filter or "remote")
        for job in jobs:
            Job.objects.get_or_create(
                title=job["title"],
                company=job.get("company", "N/A"),
                location=job.get("location", "N/A"),
                link=job["link"],
                source=job["source"],
            )

    # Filter jobs from DB
    jobs_qs = Job.objects.all()
    if query:
        jobs_qs = jobs_qs.filter(title__icontains=query)
    if location_filter:
        jobs_qs = jobs_qs.filter(location__icontains=location_filter)
    if source_filter:
        jobs_qs = jobs_qs.filter(source__icontains=source_filter)

    jobs_qs = jobs_qs.order_by(sort_by)

    # Annotate jobs with matching skills and highlight flag
    jobs_with_skills = []
    for job in jobs_qs:
        matching_skills = [skill for skill in resume_skills if skill.lower() in job.title.lower()]
        highlight = bool(matching_skills)
        jobs_with_skills.append({
            "job": job,
            "matching_skills": matching_skills,
            "highlight": highlight
        })

    # Pagination
    paginator = Paginator(jobs_with_skills, 25)
    page_obj = paginator.get_page(page_number)

    return render(request, "jobs/home.html", {
        "page_obj": page_obj,
        "query": query,
        "location_filter": location_filter,
        "source_filter": source_filter,
        "sort_by": sort_by,
        "resume_skills": resume_skills,
        "user_resumes": user_resumes,
    })


# Signup view
def signup(request):
    class InlineUserCreationForm(UserCreationForm):
        email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
        class Meta:
            model = User
            fields = ("username", "email", "password1", "password2")

    if request.method == "POST":
        form = InlineUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            messages.success(request, "Account created successfully!")
            return redirect("jobs:home")
    else:
        form = InlineUserCreationForm()

    return render(request, "jobs/signup.html", {"form": form})


# Login view
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('jobs:home')  # your home page
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


# Bookmark job
@login_required
def bookmark_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    Bookmark.objects.get_or_create(user=request.user, job=job)
    messages.success(request, "Job bookmarked!")
    return redirect("jobs:home")


# View bookmarks
@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, "jobs/bookmarks.html", {"bookmarks": bookmarks})


# Mark job as applied
@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    application, created = Application.objects.get_or_create(user=request.user, job=job)
    if created:
        messages.success(request, f'"{job.title}" marked as applied!')
    else:
        messages.info(request, f'You have already marked "{job.title}" as applied.')
    return redirect("jobs:home")


# View applications
@login_required
def my_applications(request):
    apps = Application.objects.filter(user=request.user)
    return render(request, "jobs/applications.html", {"applications": apps})


# Upload resume and extract skills
@login_required
def upload_resume(request):
    extracted_skills = []
    uploaded_file_url = None
    file_type = None  

    if request.method == "POST" and request.FILES.get("resume_file"):
        resume_file = request.FILES["resume_file"]

        # Save uploaded resume
        resume_obj = Resume.objects.create(user=request.user, file=resume_file)
        uploaded_file_url = resume_obj.file.url
        file_path = resume_obj.file.path

        # Determine file type
        if resume_file.name.lower().endswith(".pdf"):
            file_type = "pdf"
        elif resume_file.name.lower().endswith(".docx"):
            file_type = "docx"

        try:
            # Extract skills from resume
            skills = resume_parser.parse_resume(file_path)
            resume_obj.extracted_skills = ",".join(skills)
            resume_obj.save()
            extracted_skills = skills
            messages.success(request, f"Resume uploaded! Extracted skills: {', '.join(skills)}")
        except Exception as e:
            messages.error(request, f"Error parsing resume: {e}")

    # Get all uploaded resumes for the user
    user_resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")

    return render(request, "jobs/upload_resume.html", {
        "extracted_skills": extracted_skills,
        "uploaded_file_url": uploaded_file_url,
        "file_type": file_type,
        "user_resumes": user_resumes,
    })


# AI-based Job Suggestions view
@login_required
def ai_job_suggestions(request):
    user_resumes = Resume.objects.filter(user=request.user)
    all_skills = []

    for resume in user_resumes:
        if resume.extracted_skills:
            all_skills += [s.strip() for s in resume.extracted_skills.split(",")]
    
    if not all_skills:
        return render(request, "jobs/suggestions.html", {
            "ai_suggestions": [],
            "resume_feedback": ["No skills found in your uploaded resumes. Please upload a resume first."],
            "skills": [],
        })

    ai_suggestions = suggest_jobs(all_skills)

    return render(request, "jobs/suggestions.html", {
        "ai_suggestions": ai_suggestions,
    })


# Profile view
@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST" and "resume" in request.FILES:
        uploaded_file = request.FILES["resume"]
        resume_instance = Resume.objects.create(user=user, file=uploaded_file)

        file_path = os.path.join(settings.MEDIA_ROOT, resume_instance.file.name)

        try:
            skills = resume_parser.parse_resume(file_path)

            resume_instance.extracted_skills = ", ".join(skills)
            resume_instance.save()

            messages.success(request, f"Resume uploaded and skills extracted successfully!")
        except Exception as e:
            messages.error(request, f"Error parsing resume: {e}")

    latest_resume = Resume.objects.filter(user=user).order_by("-uploaded_at").first()

    return render(request, "jobs/profile.html", {
        "user": user,
        "resume": latest_resume,
    })


# AJAX handler for inline edits
@login_required
def update_profile_field(request):
    import json
    if request.method == "POST":
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")
        user = request.user

        try:
            if field == "first_name":
                user.first_name = value
            elif field == "last_name":
                user.last_name = value
            elif field == "email":
                user.email = value
            elif field == "password":
                if len(value) < 8:
                    return JsonResponse({"success": False, "error": "Password must be at least 8 characters."})
                user.password = make_password(value)
            else:
                return JsonResponse({"success": False, "error": "Invalid field"})
            
            user.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})

# Forgot Password View
def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        try:
            user = User.objects.get(username=username, email=email)
            request.session["reset_user_id"] = user.id
            return redirect("jobs:reset_password") 
        except User.DoesNotExist:
            messages.error(request, "No account found with that username and email.")
            return redirect("jobs:forgot_password")  
    return render(request, "jobs/forgot_password.html")

# Reset Password View
def reset_password(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        messages.error(request, "Unauthorized access.")
        return redirect("login")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")
        else:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully! Please login.")
            request.session.pop("reset_user_id", None)
            return redirect("login")

    return render(request, "jobs/reset_password.html")

# Resume view
@login_required
def resumes_view(request):
    user_resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')

    return render(request, 'jobs/resumes.html', {
        'user_resumes': user_resumes
    })