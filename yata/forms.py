from django import forms
from django.forms.extras.widgets import SelectDateWidget

class AddTaskForm(forms.Form):
    description = forms.CharField(max_length=200)
    due_date = forms.DateField(widget=SelectDateWidget())
