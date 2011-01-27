from django import forms
from django.forms.extras.widgets import SelectDateWidget
from yata.models import Task

class AddTaskForm(forms.Form):
    description = forms.CharField(max_length=200)
    start_date = forms.DateField(required=False)
    #due_date = forms.DateField(widget=SelectDateWidget())
    due_date = forms.DateField(required=False)
    repeat_nb = forms.IntegerField(required=False, min_value=1)
    repeat_type = forms.ChoiceField(required=False, choices = Task.REPEAT_CHOICES)
