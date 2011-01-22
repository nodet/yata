"""
Tests for my ToDo app
"""

import datetime
from yata.models import Task, relativeDueDate, due_date_cmp
from django.test import TestCase
from django.test.client import Client


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

        
        
        
def tomorrow(aDate):
    return aDate + datetime.timedelta(1)

def yesterday(aDate):
    return aDate - datetime.timedelta(1)
        
        
class TaskHasADueDate(TestCase):
    def runTest(self):
        aDate = datetime.date(2010,01,19)
        oneDayAfter = tomorrow(aDate)
        oneDayBefore = yesterday(aDate)
        t = Task(description = "something", due_date = aDate)
        self.assertEqual('something, due 2010-01-19', t.__unicode__()) 
        t.save();
        self.assertEqual(1, Task.objects.filter(due_date=aDate).count())
        self.assertEqual(0, Task.objects.filter(due_date__gte=oneDayAfter).count())
        self.assertEqual(0, Task.objects.filter(due_date__lte=oneDayBefore).count())
        self.assertEqual(1, Task.objects.filter(due_date__lte=oneDayAfter).count())
        self.assertEqual(1, Task.objects.filter(due_date__gte=oneDayBefore).count())

class TaskHasLastEdited(TestCase):
    def runTest(self):
        t = Task(description = 'something')
        t.save()
        self.assertTrue((t.last_edited - datetime.datetime.now()).seconds <= 1)
        
      
class DueDateCmpTest(TestCase):
    def runTest(self):
        aDate = datetime.date(2010,01,19)
        self.assertEqual( 0, due_date_cmp(aDate, aDate))
        self.assertEqual(-1, due_date_cmp(aDate, tomorrow(aDate)))
        self.assertEqual( 1, due_date_cmp(tomorrow(aDate), aDate))
        self.assertEqual( 1, due_date_cmp(None, aDate))
        self.assertEqual(-1, due_date_cmp(aDate, None))
        self.assertEqual( 0, due_date_cmp(None, None))
        

      
class GetRelativeDateTest(TestCase):
    def runTest(self):
        aDate = datetime.date(2011,01,19)
        self.assertEqual('Today', relativeDueDate(aDate, aDate))
        self.assertEqual('Tomorrow', relativeDueDate(aDate, tomorrow(aDate)))
        self.assertEqual('Yesterday', relativeDueDate(aDate, yesterday(aDate)))
        self.assertEqual('In 2 days', relativeDueDate(aDate, tomorrow(tomorrow(aDate))))
        self.assertEqual('In 6 days', relativeDueDate(aDate, aDate + datetime.timedelta(6)))
        self.assertEqual('In 1 week', relativeDueDate(aDate, aDate + datetime.timedelta(7)))
        self.assertEqual('Jan 27', relativeDueDate(aDate, aDate + datetime.timedelta(8)))
        self.assertEqual('Jan 10', relativeDueDate(aDate, aDate - datetime.timedelta(9)))
        self.assertEqual('2010-12-31', relativeDueDate(aDate, aDate - datetime.timedelta(19)))

        
        
class TaskHasDone(TestCase):
    def runTest(self):
        t = Task(description = 'not yet done')
        self.assertEqual(False, t.done)
        t.save()
        self.assertEqual(0, Task.objects.filter(done='True').count())
        t.done = True
        self.assertEqual(0, Task.objects.filter(done='True').count())
        t.save()
        self.assertEqual(1, Task.objects.filter(done='True').count())
        
        
class MainViewTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do")
        t.save()
        t = Task(description = "something else", due_date = datetime.date(2011,01,19))
        t.save()
        t = Task(description = "another thing", due_date = datetime.date(2010,01,19));
        t.save();
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        tasks = response.context['tasks']
        self.assertEqual(3, len(tasks))
        
      
class MainViewHasTasksSortedByEarliestDueDateTest(MainViewTest):
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(3, len(tasks))
        self.assertEqual(sorted(tasks, Task.compare_by_due_date), tasks)
        
class MainViewHasListOfNotDoneTasks(MainViewTest):
    def setUp(self):
        t = Task(description = "Already done", done = True)
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        tasks = response.context['tasks']
        for t in tasks:
            self.assertFalse(t.done)
        
class MainViewHasListOfDoneTasks(MainViewHasListOfNotDoneTasks):
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        tasks_recently_done = response.context['tasks_recently_done']
        for t in tasks_recently_done:
            self.assertTrue(t.done)
        