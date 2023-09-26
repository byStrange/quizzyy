from django.db import models
from django.contrib.auth import get_user_model
import uuid


# Create your models here.


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class QuestionGroup(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name


class Question(UUIDMixin):
    question = models.CharField(max_length=500)
    options = models.ManyToManyField("Option", related_name="question_options")
    question_answer = models.ForeignKey(
        "Option", on_delete=models.CASCADE, blank=True, null=True
    )
    group = models.ForeignKey("QuestionGroup", on_delete=models.CASCADE)

    def __str__(self):
        return self.question


class Option(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name


class Answer(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)  # student
    question = models.ForeignKey("Question", on_delete=models.CASCADE)  # question
    answer = models.ForeignKey("Option", on_delete=models.CASCADE)  # option

    class Meta:
        unique_together = ("student", "question")

    def __str__(self):
        return self.student.full_name


class StudentGroup(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name


class Student(UUIDMixin):
    full_name = models.CharField(max_length=254)
    username = models.CharField(max_length=254, unique=True)
    group = models.ForeignKey("StudentGroup", on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Exam(UUIDMixin, TimestampMixin):
    title = models.CharField(max_length=254)
    is_page = models.BooleanField(default=False)
    shuffle = models.BooleanField(default=False)
    question_group = models.ForeignKey("QuestionGroup", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=20)
    is_public = models.BooleanField(default=False)
    schedule = models.DateTimeField()
    duration = models.IntegerField(default=60) # in minutes

    def __str__(self):
        return self.title


class ExamAttempt(UUIDMixin, TimestampMixin):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE)
    questions = models.ManyToManyField("Question")
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student} attempted {self.exam} at {self.created_at}"

    class Meta:
        ordering = ("-created_at",)


class Device(UUIDMixin, TimestampMixin):
    name = models.CharField(max_length=254)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class DeviceSession(UUIDMixin, TimestampMixin):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True
    )
    device = models.ForeignKey("Device", on_delete=models.CASCADE)
    device_info = models.JSONField(null=True, blank=True)
    session_key = models.CharField(max_length=254)

    def __str__(self) -> str:
        return "Session of " + self.device.name

    class Meta:
        ordering = ("-created_at",)
