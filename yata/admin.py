from yata.models import Task
from django.contrib import admin


class TaskAdmin(admin.ModelAdmin):
    list_display = ('todo', 'due_date')
    list_filter = ('todo', 'due_date')

admin.site.register(Task, TaskAdmin)