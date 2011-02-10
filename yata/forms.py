from django import forms
from django.forms.extras.widgets import SelectDateWidget
from yata.models import Task, Context

class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
    description = forms.CharField(widget=forms.TextInput(attrs={'size':'100'}))
        
class AddContextForm(forms.ModelForm):
    class Meta:
        model = Context
        
class UploadXMLForm(forms.Form):
    file  = forms.FileField()
