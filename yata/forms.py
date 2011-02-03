from django import forms
from django.forms.extras.widgets import SelectDateWidget
from yata.models import Task, Context

class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        
class AddContextForm(forms.ModelForm):
    class Meta:
        model = Context
        
