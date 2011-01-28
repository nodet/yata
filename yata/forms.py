from django import forms
from django.forms.extras.widgets import SelectDateWidget
from yata.models import Task

class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task