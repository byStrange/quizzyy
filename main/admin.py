from django.contrib import admin

from main.models import (
    QuestionGroup,
    Question,
    Answer,
    Exam,
    Option,
    Student,
    StudentGroup,
    ExamAttempt,
    Device,
    DeviceSession,
)


admin.site.register(QuestionGroup)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Exam)
admin.site.register(Option)
admin.site.register(StudentGroup)
admin.site.register(Student)
admin.site.register(ExamAttempt)
admin.site.register(DeviceSession)
admin.site.register(Device)
# Register your models here.
