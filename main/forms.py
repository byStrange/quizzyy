from django import forms
from main.models import Exam

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = "__all__"
        exclude = ("created_at", "update_at")