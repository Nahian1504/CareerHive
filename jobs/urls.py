from django.urls import path
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("upload_resume/", views.upload_resume, name="upload_resume"),

    # Bookmarks & applications
    path("bookmark/<int:job_id>/", views.bookmark_job, name="bookmark_job"),
    path("bookmarks/", views.my_bookmarks, name="my_bookmarks"),
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("applications/", views.my_applications, name="my_applications"),
]