from yata.models import Task
from django.contrib import admin
from django import forms
from django.contrib.auth.models import User



class TaskAdmin(admin.ModelAdmin):
    list_display = ('description', 'start_date', 'relative_due_date', 'done', 'repeat_nb', 'repeat_type', 'last_edited')
    list_filter = ('description', 'start_date', 'due_date', 'done')
    
admin.site.register(Task, TaskAdmin)



#admin.site.register(Task)