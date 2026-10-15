from django.urls import path

from . import views

app_name = "homework"

urlpatterns = [
    # Student
    path("", views.assignment_list, name="assignment_list"),
    path("assignment/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("submission/<int:pk>/message/", views.post_message, name="post_message"),
    path("submission/<int:pk>/download/", views.download_submission, name="download_submission"),
    # Teacher
    path("teacher/submissions/", views.submission_list, name="submission_list"),
    path("teacher/submissions/<int:pk>/", views.submission_detail, name="submission_detail"),
    path("teacher/assignments/", views.manage_assignments, name="manage_assignments"),
    path("teacher/assignments/new/", views.assignment_create, name="assignment_create"),
    path("teacher/assignments/<int:pk>/edit/", views.assignment_edit, name="assignment_edit"),
]
