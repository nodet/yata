from yata.models import Task
from django.contrib import admin
from django import forms
from django.contrib.auth.models import User



class TaskAdmin(admin.ModelAdmin):
    list_display = ('description', 'relative_due_date', 'last_edited')
    list_filter = ('description', 'due_date')
    
admin.site.register(Task, TaskAdmin)



#admin.site.register(Task)