import json

from django import template
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, JsonResponse, Http404, HttpResponseNotAllowed
from django.template.defaulttags import register
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.db import IntegrityError

from user_agents import parse as user_agent_parse


from main.models import (
    Student,
    StudentGroup,
    QuestionGroup,
    Exam,
    ExamAttempt,
    Question,
    Option,
    DeviceSession,
    Device,
)
from main.forms import ExamForm
from main.helpers import generate_token

User = get_user_model()


@register.filter(name="parse")
def parse(value, key):
    try:
        # Parse the JSON string into a Python dictionary
        json_data = json.loads(value)

        # Check if the key exists in the dictionary
        if key in json_data:
            return json_data[key]
        else:
            return None  # Return None if the key is not found
    except (json.JSONDecodeError, TypeError):
        return None  # Handle invalid JSON or non-string input gracefully


@register.simple_tag
def active_link(request: HttpRequest, view_name: str) -> str:
    current_url = request.path
    target_url = reverse(view_name)

    if current_url == target_url:
        return "active"
    else:
        return ""


# Create your views here.


@staff_member_required
def dashboard_view(request):
    return


@staff_member_required
def student_groups_view(request):
    if request.method == "POST":
        data = request.POST
        if data.get("name"):
            student_group = StudentGroup.objects.create(name=data.get("name"))
            return redirect("main:student_group", student_group_id=student_group.id)
        else:
            return redirect("main:student_group")
    student_groups = StudentGroup.objects.prefetch_related("student_set").all()
    return render(request, "student_groups.html", {"student_groups": student_groups})


@staff_member_required
def student_group_view(request, student_group_id):
    student_group = StudentGroup.objects.get(id=student_group_id)
    if request.method == "POST":
        data = request.POST
        name: str = data.get("name")
        if name:
            username = name.strip().lower().replace(" ", "")
            try:
                student = Student.objects.create(
                    full_name=name, group=student_group, username=username
                )
            except IntegrityError:
                messages.error(request, "this username has already taken")
                return redirect("main:student_group", student_group_id=student_group_id)
            return redirect(
                "main:student", student_group_id=student_group.id, student_id=student.id
            )
        else:
            return redirect("main:student_group", student_group_id=student_group.id)

    student_groups = StudentGroup.objects.prefetch_related("student_set").all()
    return render(
        request,
        "student_group.html",
        {"student_group": student_group, "student_groups": student_groups},
    )


@staff_member_required
def student_view(request, student_group_id, student_id):
    student_group = StudentGroup.objects.get(id=student_group_id)
    student = student_group.student_set.get(id=student_id)
    student_groups = StudentGroup.objects.prefetch_related("student_set").all()
    attempts = ExamAttempt.objects.filter(student=student)
    # return render(
    #     request,
    #     "student.html",
    #     {
    #         "student_groups": student_groups,
    #         "student_group": student_group,
    #         "student": student,
    #     },
    # )

    return render(
        request,
        "student.html",
        {
            "student_groups": student_groups,
            "student_group": student_group,
            "student": student,
            "attempts": attempts
        },
    )


@staff_member_required
def exams_view(request):
    if request.method == "POST":
        print(request.POST)
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            return redirect("main:exam", exam_id=exam.id)
        else:
            return JsonResponse({"error": form.errors.as_text()})

    exams = Exam.objects.all()
    question_groups = QuestionGroup.objects.all()
    return render(
        request, "exams.html", {"exams": exams, "question_groups": question_groups}
    )


@staff_member_required
def exam_view(request, exam_id):
    exams = Exam.objects.all()
    exam = exams.get(id=exam_id)
    attempts = ExamAttempt.objects.filter(exam=exam)

    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            exam = form.save()
            return redirect("main:exam", exam_id=exam.id)
        else:
            return JsonResponse({"error": form.errors.as_text()})
    question_groups = QuestionGroup.objects.all()
    return render(
        request,
        "exam.html",
        {
            "exams": exams,
            "exam": exam,
            "question_groups": question_groups,
            "attempts": attempts,
        },
    )


@staff_member_required
def question_groups_view(request):
    if request.method == "POST":
        data = request.POST
        if data.get("name"):
            question_group = QuestionGroup.objects.create(name=data.get("name"))
            return redirect("main:question_group", question_group_id=question_group.id)
        else:
            return redirect("main:question_groups")
    question_groups = QuestionGroup.objects.prefetch_related("question_set").all()
    return render(request, "question_groups.html", {"question_groups": question_groups})


def question_group_view(request, question_group_id):
    question_group = QuestionGroup.objects.get(id=question_group_id)
    question_groups = QuestionGroup.objects.prefetch_related("question_set").all()

    return render(
        request,
        "question_group.html",
        {"question_groups": question_groups, "question_group": question_group},
    )


@staff_member_required
def question_view(request, question_group_id, question_id):
    question_group = get_object_or_404(QuestionGroup, id=question_group_id)
    question = get_object_or_404(Question, id=question_id, group=question_group)

    if request.method == "POST":
        print("ppost")
        data = request.POST
        if "question" in data and "option" in data and "answer" in data:
            # Update the question text
            question.question = data["question"]

            # Update options
            updated_options = data.getlist("option")
            existing_options = list(question.options.all())  # Retrieve options again

            for i, option_text in enumerate(updated_options):
                if i < len(existing_options):
                    # Update existing option
                    existing_option = existing_options[i]
                    existing_option.name = option_text
                    existing_option.save()
                else:
                    # Create new option
                    new_option = Option(name=option_text)
                    new_option.save()
                    question.options.add(new_option)
            else:
                existing_options = list(question.options.all())
            # Update the correct answer
            answer_index = int(data["answer"])
            if 0 <= answer_index < len(existing_options):
                question.question_answer = existing_options[answer_index]
                # Handle the case where the answer index is out of bounds
                # You might want to add error handling here

            # Save the updated question
            question.save()
            print("question updated", question)
            return redirect(
                "main:question",
                question_group_id=question_group_id,
                question_id=question.id,
            )

            # Redirect to a success page or return a JSON response indicating success
            # You may customize this part based on your application's needs
        else:
            messages.error(
                request,
                "question or options are missing, or you did not choose an answer",
            )
            return redirect("main:question_add", question_group_id=question_group_id)
    # Rest of your code for rendering the question details

    question_groups = QuestionGroup.objects.prefetch_related("question_set").all()

    return render(
        request,
        "question.html",
        {
            "question_groups": question_groups,
            "question_group": question_group,
            "question": question,
        },
    )


@staff_member_required
def question_add(request, question_group_id):
    question_group = QuestionGroup.objects.get(id=question_group_id)
    if request.method == "POST":
        data = request.POST
        if "question" in data and "option" in data and "answer" in data:
            question = Question(question=data.get("question"), group=question_group)
            question.save()
            answer_index = int(data.get("answer"))
            for i, option_text in enumerate(data.getlist("option")):
                option = Option.objects.create(name=option_text)
                question.options.add(option)
                if i == answer_index:
                    question.question_answer = option
            question.save()
        else:
            messages.error(
                request, "question, options are missing or you did not choose an answer"
            )
            return redirect("main:question_group", question_group_id=question_group_id)
    question_groups = QuestionGroup.objects.prefetch_related("question_set").all()
    return render(
        request,
        "add_question.html",
        {"question_groups": question_groups, "question_group": question_group},
    )


@staff_member_required
def devices_view(request):
    if request.method == "POST":
        data = request.POST
        if data.get("name"):
            device = Device.objects.create(name=data.get("name"))
            return redirect("main:device", device_id=device.id)
        else:
            messages.error(request, "name field is required")
            return redirect("main:devices")
    devices = Device.objects.all()

    return render(request, "devices.html", {"devices": devices})


@staff_member_required
def device_view(request, device_id):
    devices = Device.objects.all()
    device = devices.prefetch_related("devicesession_set").get(id=device_id)

    return render(request, "device.html", {"devices": devices, "device": device})


def device_login_view(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    USER_AGENT = request.META.get("HTTP_USER_AGENT")
    client_ip = request.META.get("REMOTE_ADDR")
    print(USER_AGENT)
    user_agent_info = user_agent_parse(USER_AGENT)
    _browser = user_agent_info.browser.family
    _os = user_agent_info.os.family
    _device = user_agent_info.device.family

    session_info = {
        "browser": _browser,
        "os": _os,
        "device": _device,
        "ip_addr": client_ip,
        "general": str(user_agent_info),
    }
    session_info = json.dumps(session_info)
    session_key = generate_token()
    session = DeviceSession(
        device=device, session_key=session_key, device_info=session_info
    )
    session.save()
    user = User.objects.create(username=str(session.id))
    session.user = user
    session.save()
    login(request, user)
    return render(request, "login_success.html", {"session": session})
