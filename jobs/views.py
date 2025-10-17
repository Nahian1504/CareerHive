from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .scraper import get_jobs
from .models import Job, Bookmark, Application, Resume
from .utils import resume_parser

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
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("jobs:home")
    else:
        form = UserCreationForm()
    return render(request, "jobs/signup.html", {"form": form})


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
