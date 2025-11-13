from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("upload_resume/", views.upload_resume, name="upload_resume"),
    path("suggestions/", views.ai_job_suggestions, name="ai_suggestions"),
<<<<<<< HEAD
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile_field, name='update_profile_field'),
=======
 feature/Myprofile
    path('profile/', views.profile_view, name='profile'),


    main
>>>>>>> 8bd9ce9d5dd54921b57d01b5e6094e507393bd95

    # Bookmarks & applications
    path("bookmark/<int:job_id>/", views.bookmark_job, name="bookmark_job"),
    path("bookmarks/", views.my_bookmarks, name="my_bookmarks"),
    path("apply/<int:job_id>/", views.apply_job, name="apply_job"),
    path("applications/", views.my_applications, name="my_applications"),
]

