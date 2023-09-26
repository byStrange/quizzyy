from django.shortcuts import redirect
from django.urls import path
from main.views import (
    dashboard_view,
    student_groups_view,
    exams_view,
    question_groups_view,
    student_group_view,
    student_view,
    question_group_view,
    question_view,
    question_add,
    exam_view,
    devices_view,
    device_view,
    device_login_view,
)


app_name = "main"

urlpatterns = [
    path("", lambda request: redirect("main:student_groups"), name="index"),
    path("students/", student_groups_view, name="student_groups"),
    path("students/<int:student_group_id>/", student_group_view, name="student_group"),
    path(
        "students/<int:student_group_id>/<uuid:student_id>/",
        student_view,
        name="student",
    ),
    path("exams/", exams_view, name="exams"),
    path("exams/<uuid:exam_id>/", exam_view, name="exam"),
    path("questions/", question_groups_view, name="question_groups"),
    path(
        "questions/<int:question_group_id>", question_group_view, name="question_group"
    ),
    path("questions/<int:question_group_id>/add", question_add, name="question_add"),
    path(
        "questions/<int:question_group_id>/<uuid:question_id>/",
        question_view,
        name="question",
    ),
    path("devices/", devices_view, name="devices"),
    path("devices/<uuid:device_id>/", device_view, name="device"),
    path(
        "devices/<uuid:device_id>/auth/login/", device_login_view, name="device_login"
    ),
]
