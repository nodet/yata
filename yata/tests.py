"""
Tests for my ToDo app
"""

import datetime
import time
from yata.models import Task, relativeDueDate, due_date_cmp, next_date
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

        
        
def today():
    return datetime.date.today()
        
def tomorrow(aDate = datetime.date.today()):
    return aDate + datetime.timedelta(1)

def yesterday(aDate = datetime.date.today()):
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
        # Ensure enough time between saves so they have different last_edited date/time
        time.sleep(0.05)
        t = Task(description = "Another that's done", done = True)
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        tasks = response.context['tasks']
        for t in tasks:
            self.assertFalse(t.done)


def have_same_elements(it1, it2):
    if len(it1) != len(it2):
        return False
    for t1, t2 in zip(it1, it2):
        if t1 != t2:
            return False
    return True

            
class MainViewHasListOfDoneTasks(MainViewHasListOfNotDoneTasks):
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        tasks_recently_done = response.context['tasks_recently_done']
        for t in tasks_recently_done:
            self.assertTrue(t.done)
        sorted_tasks = sorted(tasks_recently_done, key = lambda task: task.last_edited, reverse = True)
        self.assertTrue(have_same_elements(sorted_tasks, tasks_recently_done))
        
        
class MarkDoneTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do")
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/1/mark_done', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(0, len(response.context['tasks']))
        self.assertEqual(1, response.context['tasks_recently_done'].count())

class MarkNotDoneTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do", done = True)
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/1/mark_not_done', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(1, len(response.context['tasks']))
        self.assertEqual(0, response.context['tasks_recently_done'].count())
        
        
class TaskHasAStartDate(TestCase):
    def runTest(self):
        aDate = datetime.date(2010,01,19)
        t = Task(description = "Has a start date", start_date = aDate)
        t.save()
        self.assertEqual(1, Task.objects.filter(start_date__gte = aDate).count())
        self.assertEqual(0, Task.objects.filter(start_date__lt = aDate).count())
        
        
class MainViewDoesNotShowTasksNotStartedTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do now")
        t.save()
        # Something in the future. Not just tomorrow, in case the test is run around midnight...
        t = Task(description = "something to do in two days", start_date = tomorrow(tomorrow()))
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        self.assertEqual(response.status_code, 200)
        tasks = response.context['tasks']
        self.assertEqual(1, len(tasks))
        
        
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

        
class AddTaskViewTest(TestCase):
    def runTest(self):
        desc = 'The created task'
        sdate = today()
        ddate = tomorrow()
        repeat_nb = 1
        repeat_type = 'W'
        response = Client().post('/yata/add_task/', {
            'description': desc,
            'start_date': sdate,
            'due_date': ddate,
            'repeat_nb': repeat_nb,
            'repeat_type': repeat_type
        })
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(desc, t.description)
        self.assertEqual(sdate, t.start_date)
        self.assertEqual(ddate, t.due_date)
        self.assertEqual(repeat_nb, t.repeat_nb)
        self.assertEqual(repeat_type, t.repeat_type)
        
                
class CheckIsRepeating(TestCase):
    def runTest(self):
            self.assertTrue(not Task(repeat_type = 'D'               ).is_repeating())
            self.assertTrue(not Task(repeat_type = 'D', repeat_nb = 0).is_repeating())
            self.assertTrue(not Task(                   repeat_nb = 1).is_repeating())
            self.assertTrue(    Task(repeat_type = 'D', repeat_nb = 1).is_repeating())
        
        
class RepeatingWithDueDateGetsADueDate(TestCase):
    def runTest(self):
        d = tomorrow()
        t = Task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W', due_date = d)
        self.assertEqual(0, Task.objects.exclude(done__exact = True).count())
        t.mark_done()
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        t = tasks[0]
        self.assertEqual(7, (t.due_date - d).days)
        self.assertTrue(t.start_date == None)
        
class RepeatingWithStartDateGetsAStartDate(TestCase):
    def runTest(self):
        d = tomorrow()
        t = Task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W', start_date = d)
        self.assertEqual(0, Task.objects.exclude(done__exact = True).count())
        t.mark_done()
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        t = tasks[0]
        self.assertEqual(7, (t.start_date - d).days)
        self.assertTrue(t.due_date == None)
        
class RepeatingWithStartAndDueDateGetsBoth(TestCase):
    def runTest(self):
        y = yesterday()
        d = today()
        t = Task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W', start_date = y, due_date = d)
        self.assertEqual(0, Task.objects.exclude(done__exact = True).count())
        t.mark_done()
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        t = tasks[0]
        self.assertEqual(7, (t.due_date - d).days)
        self.assertEqual(7, (t.start_date - y).days)

        
        
class EditViewTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do")
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/1/edit')
        self.assertEqual(301, response.status_code)
        
        ndesc = 'new description'
        sdate = yesterday()
        ddate = tomorrow()
        nb = 2
        type = 'W'
        done = True
        response = Client().post('/yata/1/edit/', {
            'description': ndesc,
            'start_date': sdate,
            'due_date': ddate,
            'repeat_nb': nb,
            'repeat_type': type,
            'done': done
        })
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(ndesc, t.description)
        self.assertEqual(sdate, t.start_date)
        self.assertEqual(ddate, t.due_date)
        self.assertEqual(nb, t.repeat_nb)
        self.assertEqual(type, t.repeat_type)
        