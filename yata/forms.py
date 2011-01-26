from django import forms


class AddTaskForm(forms.Form):
    description = forms.CharField(max_length=200)
