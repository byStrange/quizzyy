import random
import json
from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, Http404, JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone

from main.models import Exam, Student, ExamAttempt, Question, Option, Answer


# Create your views here.


def index_view(request):
    if request.user.is_authenticated:
        exams = Exam.objects.filter(is_public=True)
        return render(request, "exam/exam_index.html", {"exams": exams})
    else:
        return HttpResponseForbidden()


def exam_overview_view(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    return render(request, "exam/exam_overview.html", {"exam": exam})


def exam_join_view(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    current_time = timezone.now()  # Get the current time in UTC
    print(current_time)
    if current_time <= exam.schedule:
        return redirect("exam:exam_overview", exam_id=exam_id)

    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        try:
            student = Student.objects.get(username=username)
            student_attempts = ExamAttempt.objects.filter(student=student, exam=exam)
            if student_attempts.exists():
                messages.error(request, "You have already passed this exam")
                return redirect("exam:exam_join", exam_id=exam_id)
            request.session["current_user_username"] = student.username
            question_group = exam.question_group
            question_group_questions = list(question_group.question_set.all())
            random_questions = random.sample(question_group_questions, exam.quantity)
            exam_attempt = ExamAttempt(exam=exam, student=student)
            exam_attempt.save()
            for question in random_questions:
                exam_attempt.questions.add(question)
            return redirect("exam:exam_view", exam_id=exam_id)
        except Student.DoesNotExist:
            messages.error(request, "student does not exist with this username")
            return redirect("exam:exam_join", exam_id=exam_id)

    return render(request, "exam/exam_join.html", {"exam": exam})


def exam_view(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Http404()
    
    student_username = request.session["current_user_username"]
    student = Student.objects.get(username=student_username)
    student_exam = student.examattempt_set.first()
    if request.method == "POST":
        student_exam.submitted = True
        student_exam.save()
        return redirect(
            "exam:results",
            exam_id=student_exam.exam.id,
            attempt_id=student_exam.id
        )
    return render(
        request, "exam/exam.html", {"exam": exam, "student_exam": student_exam}
    )


def check_answer_view(request, exam_id, attempt_id):
    if request.method == "POST":
        data = json.loads(request.body)
        question_id = str(data.get("question_id"))
        option_id = int(data.get("option_id"))
        student_username = request.session["current_user_username"]
        student = Student.objects.get(username=student_username)
        exam_attempt= ExamAttempt.objects.get(id=attempt_id)
        question = Question.objects.get(id=question_id)
        option = Option.objects.get(id=option_id)
        if Answer.objects.filter(student=student, question=question).exists():
            return JsonResponse({"error": "student answered this question already"})
        answer = Answer.objects.create(student=student, question=question, answer=option)
        if question.question_answer.id == option_id:
            exam_attempt.score += 1
            exam_attempt.save()
            print("FOuND TRUE, ", exam_attempt.score)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})


def exam_results(request, exam_id, attempt_id):
    exam = Exam.objects.get(id=exam_id)
    attempt = ExamAttempt.objects.get(id=attempt_id)
    student_username = request.session["current_user_username"]
    student = Student.objects.get(username=student_username)
    answers = Answer.objects.filter(student=student, question__in=attempt.questions.all())
    return render(request, "exam/results.html", {"result": attempt, "answers": answers })
