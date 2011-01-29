"""
Tests for my ToDo app
"""

from yata.models import Task, relativeDueDate, due_date_cmp, next_date
from yata.test_utils import today, tomorrow, yesterday
from django.test import TestCase
import datetime
import unittest


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
        self.assertEqual('in 2 days', relativeDueDate(aDate, tomorrow(tomorrow(aDate))))
        self.assertEqual('in 6 days', relativeDueDate(aDate, aDate + datetime.timedelta(6)))
        self.assertEqual('in 1 week', relativeDueDate(aDate, aDate + datetime.timedelta(7)))
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
        
        
class TaskHasAStartDate(TestCase):
    def runTest(self):
        aDate = datetime.date(2010,01,19)
        t = Task(description = "Has a start date", start_date = aDate)
        t.save()
        self.assertEqual(1, Task.objects.filter(start_date__gte = aDate).count())
        self.assertEqual(0, Task.objects.filter(start_date__lt = aDate).count())
        
        
class TestRepetitionDate(TestCase):
     def runTest(self):
        self.assertEqual(datetime.date(2011,7,15), next_date(datetime.date(2011,7,12), 3, 'D'))
        self.assertEqual(datetime.date(2011,7,26), next_date(datetime.date(2011,7,12), 2, 'W'))
        self.assertEqual(datetime.date(2011,9,12), next_date(datetime.date(2011,7,12), 2, 'M'))
        self.assertEqual(datetime.date(2013,7,12), next_date(datetime.date(2012,7,12), 1, 'Y'))
        # test with carry from D to M, from D to Y
        self.assertEqual(datetime.date(2011,8,2), next_date(datetime.date(2011,7,30), 3, 'D'))
        self.assertEqual(datetime.date(2012,1,1), next_date(datetime.date(2011,12,2), 30, 'D'))
        # Adding months
        self.assertEqual(datetime.date(2011,10,15), next_date(datetime.date(2011,7,15), 3, 'M'))
        self.assertEqual(datetime.date(2011,3,28), next_date(datetime.date(2011,2,28), 1, 'M'))
        self.assertEqual(datetime.date(2011,2,28), next_date(datetime.date(2011,1,31), 1, 'M'))
        self.assertEqual(datetime.date(2012,1,15), next_date(datetime.date(2011,12,15), 1, 'M'))

        
class MarkingARepeatableTaskCreatesANewCopy(TestCase):
    def runTest(self):
        t = Task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W')
        self.assertEqual(0, Task.objects.exclude(done__exact = True).count())
        t.mark_done()
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        t = tasks[0]
        self.assertEqual(7, (t.due_date - datetime.date.today()).days)
        
class TasksNotRepeatableIfNotCorrectlyDefined(TestCase):
    def runTest(self):
        t = Task(description = 'Not really repeatable', repeat_nb = None, repeat_type = 'W')
        t.mark_done()
        t = Task(description = 'Not really repeatable', repeat_nb = 1, repeat_type = None)
        t.mark_done()

        
                
class CheckIsRepeating(TestCase):
    def runTest(self):
            self.assertTrue(not Task(repeat_type = 'D'               ).is_repeating())
            self.assertTrue(not Task(repeat_type = 'D', repeat_nb = 0).is_repeating())
            self.assertTrue(not Task(                   repeat_nb = 1).is_repeating())
            self.assertTrue(    Task(repeat_type = 'D', repeat_nb = 1).is_repeating())
        
        
class DatesForTasksCreatedFromRepeating(TestCase):

    def aTask(self):
        return Task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W')

    def check(self, t):
        self.assertEqual(0, Task.objects.exclude(done__exact = True).count())
        t.mark_done()
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        return tasks[0]
        
    def test_RepeatingWithDueDateGetsADueDate(self):
        t = self.aTask()
        t.due_date = d = tomorrow()
        t = self.check(t)
        self.assertEqual(7, (t.due_date - d).days)
        self.assertTrue(t.start_date == None)
        
    def test_RepeatingWithStartDateGetsAStartDate(self):
        t = self.aTask()
        t.start_date = d = tomorrow()
        t = self.check(t)
        self.assertEqual(7, (t.start_date - d).days)
        self.assertTrue(t.due_date == None)
        
    def test_RepeatingWithStartAndDueDateGetsBoth(self):
        t = self.aTask()
        t.start_date = y = yesterday()
        t.due_date = d = today()
        t = self.check(t)
        self.assertEqual(7, (t.due_date - d).days)
        self.assertEqual(7, (t.start_date - y).days)


        
        
        
        