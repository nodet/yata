"""
Tests for my ToDo app
"""

from yata.models import Task, relativeDueDate, due_date_cmp, next_date, Context, group_by
from yata.test_utils import today, tomorrow, yesterday, flatten
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

    def a_repeating_task(self):
        return Task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W')

    def mark_done_and_get_repeated(self, t):
        self.assertEqual(0, Task.objects.exclude(done__exact = True).count())
        t.mark_done()
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        return tasks[0]
        
    def test_RepeatingWithDueDateGetsADueDate(self):
        t = self.a_repeating_task()
        t.due_date = d = tomorrow()
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.due_date - d).days)
        self.assertTrue(t.start_date == None)
        
    def test_RepeatingWithStartDateGetsAStartDate(self):
        t = self.a_repeating_task()
        t.start_date = d = tomorrow()
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.start_date - d).days)
        self.assertTrue(t.due_date == None)
        
    def test_RepeatingWithStartAndDueDateGetsBoth(self):
        t = self.a_repeating_task()
        t.start_date = y = yesterday()
        t.due_date = d = today()
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.due_date - d).days)
        self.assertEqual(7, (t.start_date - y).days)


        
class TestContext(TestCase):
    def setUp(self):
        c = Context(title = 'Context')
        c.save()

    def test_can_retrieve(self):
        c = Context.objects.get(title__exact = 'Context')
        self.assertEqual(c.title, 'Context')
        self.assertEqual(c.__unicode__(), 'Context')

    def test_task_can_have_a_context(self):
        c = Context.objects.get(title__exact = 'Context')
        t = Task(description = 'a task', context = c)
        self.assertEqual(t.context.title, 'Context')
        
        
        
class TaskHasAPriority(TestCase):
    def test_can_have_positive_priority(self):
        prio = 1
        t = Task(description = "something", priority = 1)
        t.save();
        self.assertEqual(1, Task.objects.filter(priority__gte=1).count())

        
        
class TaskHasImportance(TestCase):

    def setUp(self):
        d = tomorrow()
        self.t1 = Task(description='T1')
        self.t2 = Task(description='T2', due_date=d)
        
    def test_task_is_more_important_if_due_date(self):
        self.assertTrue(self.t1.importance() < self.t2.importance())



class GroupByTest(TestCase):

    def group(self, list):
        return group_by(list, lambda t: t)

    def test_empty_list(self):
        gb = self.group([])
        self.assertEqual([], gb)

    def test_one(self):
        gb = self.group([1])
        self.assertEqual([[1, [1]]], gb)
        self.assertEqual([1], flatten(gb))
        
    def test_two_equal(self):
        gb = self.group([1,1])
        self.assertEqual([[1, [1,1]]], gb)
        self.assertEqual([1,1], flatten(gb))
        
    def test_two_different(self):
        gb = self.group([1,2])
        self.assertEqual([[1, [1]], [2, [2]]], gb)
        self.assertEqual([1,2], flatten(gb))
    
    def test_tasks(self):
        t = Task(description = 'T1')
        list = group_by([t], lambda t: t.importance())
        self.assertEqual(list[0][0], t.importance())
        self.assertEqual(list[0][1], [t])
        self.assertEqual([t], flatten(list))
        