from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .scraper import get_jobs
from .models import Job, Bookmark, Application

@login_required
def home(request):
    query = request.GET.get("search", "")
    location_filter = request.GET.get("location", "")
    source_filter = request.GET.get("source", "")
    sort_by = request.GET.get("sort", "title")  # default sort by title
    page_number = request.GET.get("page", 1)

    jobs = []
    if query:
        jobs = get_jobs(query, location_filter or "remote")

        # Save scraped jobs to DB (avoid duplicates by link)
        for job in jobs:
            Job.objects.get_or_create(
                title=job["title"],
                company=job.get("company", "N/A"),
                location=job.get("location", "N/A"),
                link=job["link"],
                source=job["source"],
            )

    # Query DB for filtering & sorting
    jobs_qs = Job.objects.all()
    if query:
        jobs_qs = jobs_qs.filter(title__icontains=query)
    if location_filter:
        jobs_qs = jobs_qs.filter(location__icontains=location_filter)
    if source_filter:
        jobs_qs = jobs_qs.filter(source__icontains=source_filter)

    jobs_qs = jobs_qs.order_by(sort_by)

    paginator = Paginator(jobs_qs, 25)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "jobs/home.html",
        {"page_obj": page_obj, "query": query, "location_filter": location_filter, "source_filter": source_filter, "sort_by": sort_by},
    )

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("jobs:home")
    else:
        form = UserCreationForm()
    return render(request, "jobs/signup.html", {"form": form})

@login_required
def bookmark_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    Bookmark.objects.get_or_create(user=request.user, job=job)
    messages.success(request, "Job bookmarked!")
    return redirect("jobs:home")

@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, "jobs/bookmarks.html", {"bookmarks": bookmarks})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    application, created = Application.objects.get_or_create(user=request.user, job=job)
    if created:
        messages.success(request, f'"{job.title}" marked as applied!')
    else:
        messages.info(request, f'You have already marked "{job.title}" as applied.')
    return redirect("jobs:home")

@login_required
def my_applications(request):
    apps = Application.objects.filter(user=request.user)
    return render(request, "jobs/applications.html", {"applications": apps})
