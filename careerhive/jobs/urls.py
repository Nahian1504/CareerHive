from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("upload_resume/", views.upload_resume, name="upload_resume"),
    path('profile/update/', views.update_profile_field, name='update_profile_field'),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("bookmark/<int:job_id>/", views.bookmark_job, name="bookmark_job"),
    path("bookmarks/", views.my_bookmarks, name="my_bookmarks"),
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("applications/", views.my_applications, name="my_applications"),
    path("suggestions/", views.ai_job_suggestions, name="ai_suggestions"),
    path('profile/', views.profile_view, name='profile'),
    path('resumes/', views.resumes_view, name='resumes'),
]

