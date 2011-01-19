"""
Tests for my ToDo app
"""

import datetime
from yata.models import Task
from django.test import TestCase


class CanCreateATask(TestCase):
    def runTest(self):
        somethingToDo = "Something to do"
        t = Task(description = somethingToDo)
        self.assertEqual(t.description, somethingToDo)

        
class CanRetrieveATask(TestCase):
    def runTest(self):
        t = Task(description = "something to do")
        t.save()
        t = Task(description = "another thing");
        t.save();
        self.assertEqual(2, Task.objects.all().count())
        self.assertEqual(1, Task.objects.filter(description__startswith="Something to do").count())

class TaskHasADueDate(TestCase):
    def runTest(self):
        aDate = datetime.date(2011,01,19)
        oneDayAfter = aDate + datetime.timedelta(1)
        oneDayBefore = aDate - datetime.timedelta(1)
        t = Task(description = "something", due_date = aDate)
        t.save();
        self.assertEqual(1, Task.objects.filter(due_date=aDate).count())
        self.assertEqual(0, Task.objects.filter(due_date__gte=oneDayAfter).count())
        self.assertEqual(0, Task.objects.filter(due_date__lte=oneDayBefore).count())
        self.assertEqual(1, Task.objects.filter(due_date__lte=oneDayAfter).count())
        self.assertEqual(1, Task.objects.filter(due_date__gte=oneDayBefore).count())
        