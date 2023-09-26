from django.urls import path
from exam.views import (
    index_view,
    exam_overview_view,
    exam_join_view,
    exam_view,
    check_answer_view,
    exam_results
)

app_name = "exam"

urlpatterns = [
    path("", index_view, name="index"),
    path("exams/<uuid:exam_id>/", exam_overview_view, name="exam_overview"),
    path("exams/<uuid:exam_id>/join/", exam_join_view, name="exam_join"),
    path("exam/<uuid:exam_id>/", exam_view, name="exam_view"),
    path(
        "exam/<uuid:exam_id>/<uuid:attempt_id>/", check_answer_view, name="check_answer"
    ),
    path("exam/<uuid:exam_id>/<uuid:attempt_id>/results/", exam_results, name="results")
]
