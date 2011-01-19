from yata.models import Task
from django.contrib import admin


class TaskAdmin(admin.ModelAdmin):
    list_display = ('description', 'due_date')
    list_filter = ('description', 'due_date')

admin.site.register(Task, TaskAdmin)