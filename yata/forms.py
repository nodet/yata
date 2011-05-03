from django import forms
from django.forms.extras.widgets import SelectDateWidget
from yata.models import Task, Context

class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ('user',)
        
    description = forms.CharField(widget=forms.TextInput(attrs={'size':'100', 'id':'focused'}))
    note        = forms.CharField(widget=forms.Textarea(attrs={'cols':'81', 'rows':'10'}),
                                   required=False)
        
class AddContextForm(forms.ModelForm):
    class Meta:
        model = Context
    title = forms.CharField(widget=forms.TextInput(attrs={'size':'50', 'id':'focused'}))
        
class UploadXMLForm(forms.Form):
    file  = forms.FileField()
