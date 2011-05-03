"""
Tests for my ToDo app
"""

from yata.models import Task, relativeDueDate, due_date_cmp, next_date, Context, group_by
from yata.test_utils import today, tomorrow, yesterday, flatten
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
import datetime
import unittest
import sys


class YataTestCase(TestCase):

    def setUp(self):
        # We need a user whenever we create a task, so let's get some
        self.u1 = User.objects.create_user('test1', 'test1@yata.com.invalid', 'test1');
        self.u2 = User.objects.create_user('test2', 'test2@yata.com.invalid', 'test2');
        self.user = authenticate(username='test1', password='test1')
        
    def new_task(self, 
                  description = None, 
                  due_date = None, 
                  start_date = None,
                  repeat_nb = None, 
                  repeat_type = None,
                  repeat_from_due_date = False,
                  context = None,
                  priority = 0,
                  done = False,
                  note = None):
        return Task(user = self.user,
                     description = description, 
                     due_date = due_date, 
                     start_date = start_date,
                     repeat_nb = repeat_nb,
                     repeat_type = repeat_type,
                     repeat_from_due_date = repeat_from_due_date,
                     context = context,
                     priority = priority,
                     done = done,
                     note = note)
        
        
        
class Users_and_authentication(YataTestCase):

    def test_user_authentication(self):
        self.assertTrue(self.user.is_active)
        
    def test_Tasks_created_while_logged_have_user_field_not_null(self):
        task = self.new_task(description = 'description')
        self.assertFalse(task.user is None)
        

class CanCreateATask(YataTestCase):
    def runTest(self):
        somethingToDo = "Something to do"
        t = self.new_task(description = somethingToDo)
        self.assertEqual(t.description, somethingToDo)

        
class CanRetrieveATask(YataTestCase):
    def runTest(self):
        t = self.new_task(description = "something to do")
        t.save()
        t = self.new_task(description = "another thing");
        t.save();
        self.assertEqual(2, Task.objects.all().count())
        self.assertEqual(1, Task.objects.filter(description__startswith="Something to do").count())

        
        
class TaskHasADueDate(YataTestCase):
    def runTest(self):
        aDate = datetime.date(2010,01,19)
        oneDayAfter = tomorrow(aDate)
        oneDayBefore = yesterday(aDate)
        t = self.new_task(description = "something", due_date = aDate)
        self.assertEqual('something, due 2010-01-19', t.__unicode__()) 
        t.save();
        self.assertEqual(1, Task.objects.filter(due_date=aDate).count())
        self.assertEqual(0, Task.objects.filter(due_date__gte=oneDayAfter).count())
        self.assertEqual(0, Task.objects.filter(due_date__lte=oneDayBefore).count())
        self.assertEqual(1, Task.objects.filter(due_date__lte=oneDayAfter).count())
        self.assertEqual(1, Task.objects.filter(due_date__gte=oneDayBefore).count())

class TaskHasLastEdited(YataTestCase):
    def runTest(self):
        t = self.new_task(description = 'something')
        t.save()
        self.assertTrue((t.last_edited - datetime.datetime.now()).seconds <= 1)
        
      
class DueDateCmpTest(TestCase):
    def runTest(self):
        aDate = datetime.date(2010,01,19)
        self.assertEqual( 0, due_date_cmp(aDate, aDate))
        self.assertEqual(-1, due_date_cmp(aDate, tomorrow(aDate)))
        self.assertEqual( 1, due_date_cmp(tomorrow(aDate), aDate))
        self.assertEqual( sys.maxint, due_date_cmp(None, aDate))
        self.assertEqual(-sys.maxint-1, due_date_cmp(aDate, None))
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

        
        
class TaskHasDone(YataTestCase):
    def runTest(self):
        t = self.new_task(description = 'not yet done')
        self.assertEqual(False, t.done)
        t.save()
        self.assertEqual(0, Task.objects.filter(done='True').count())
        t.done = True
        self.assertEqual(0, Task.objects.filter(done='True').count())
        t.save()
        self.assertEqual(1, Task.objects.filter(done='True').count())
        
        
class TaskHasAStartDate(YataTestCase):
    def runTest(self):
        aDate = datetime.date(2010,01,19)
        t = self.new_task(description = "Has a start date", start_date = aDate)
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

        
class MarkingARepeatableTaskCreatesANewCopy(YataTestCase):
    def runTest(self):
        t = self.new_task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W')
        t.save()
        self.assertEqual(1, Task.objects.exclude(done__exact = True).count())
        self.assertEqual(0, Task.objects.filter(done__exact = True).count())
        t.mark_done()
        self.assertEqual(1, Task.objects.exclude(done__exact = True).count())
        self.assertEqual(1, Task.objects.filter(done__exact = True).count())
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        t = tasks[0]
        self.assertEqual(7, (t.due_date - datetime.date.today()).days)
        
class TasksNotRepeatableIfNotCorrectlyDefined(YataTestCase):
    def runTest(self):
        t = self.new_task(description = 'Not really repeatable', repeat_nb = None, repeat_type = 'W')
        t.mark_done()
        t = self.new_task(description = 'Not really repeatable', repeat_nb = 1, repeat_type = None)
        t.mark_done()

        
                
class CheckIsRepeating(YataTestCase):
    def runTest(self):
            self.assertTrue(not self.new_task(repeat_type = 'D'               ).is_repeating())
            self.assertTrue(not self.new_task(repeat_type = 'D', repeat_nb = 0).is_repeating())
            self.assertTrue(not self.new_task(                   repeat_nb = 1).is_repeating())
            self.assertTrue(    self.new_task(repeat_type = 'D', repeat_nb = 1).is_repeating())
        
        
class RepeatingTasksTests(YataTestCase):

    def a_repeating_task(self):
        return self.new_task(description = 'Repeatable', repeat_nb = 1, repeat_type = 'W')

    def mark_done_and_get_repeated(self, t):
        self.assertEqual(0, Task.objects.exclude(done__exact = True).count())
        t.mark_done()
        tasks = Task.objects.exclude(done__exact = True)
        self.assertEqual(1, tasks.count())
        return tasks[0]

class DatesForTasksCreatedFromRepeating(RepeatingTasksTests):
        
    def test_RepeatingWithDueDateGetsADueDate(self):
        t = self.a_repeating_task()
        t.due_date = d = tomorrow()
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.due_date - datetime.date.today()).days)
        self.assertTrue(t.start_date == None)
        
    def test_RepeatingWithStartDateGetsAStartDate(self):
        t = self.a_repeating_task()
        t.start_date = d = tomorrow()
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.start_date - datetime.date.today()).days)
        self.assertTrue(t.due_date == None)
        
    def test_RepeatingWithStartAndDueDateGetsBoth(self):
        t = self.a_repeating_task()
        t.start_date = y = yesterday()
        t.due_date = d = today()
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.due_date - d).days)
        self.assertEqual(1, (t.due_date - t.start_date).days)

    def test_RepeatingWithStartAndDueDateOverdue(self):
        t = self.a_repeating_task()
        t.start_date = y = yesterday(yesterday())
        t.due_date = d = yesterday()
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.due_date - datetime.date.today()).days)
        self.assertEqual(1, (t.due_date - t.start_date).days)


class DatesForTasksRepeatingFromDueDate(RepeatingTasksTests):

    def a_task_repeating_from_due_date(self):
        return self.new_task(description = 'Repeating from due_date', 
                              repeat_nb = 1, 
                              repeat_type = 'W', 
                              due_date = datetime.date(2010,04,23),
                              repeat_from_due_date = True)
    
    def test_TasksUsuallyDontRepeatFromDueDate(self):
        t = self.new_task(description = 'A task');
        self.assertFalse(t.repeat_from_due_date);
        
    def test_RepeatingWithDueDateGetsADueDate(self):
        t = self.a_task_repeating_from_due_date()
        old_due_date = t.due_date
        t = self.mark_done_and_get_repeated(t)
        self.assertEqual(7, (t.due_date - old_due_date).days)
    



        
        
class TestContext(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        c = Context(title = 'Context')
        c.save()

    def test_can_retrieve(self):
        c = Context.objects.get(title__exact = 'Context')
        self.assertEqual(c.title, 'Context')
        self.assertEqual(c.__unicode__(), 'Context')

    def test_task_can_have_a_context(self):
        c = Context.objects.get(title__exact = 'Context')
        t = self.new_task(description = 'a task', context = c)
        self.assertEqual(t.context.title, 'Context')
        
        
        
class TaskHasAPriority(YataTestCase):
    def test_can_have_positive_priority(self):
        prio = 1
        t = self.new_task(description = "something", priority = 1)
        t.save();
        self.assertEqual(1, Task.objects.filter(priority__gte=1).count())

        
        
class TaskHasImportance(YataTestCase):

    def setUp(self):
        YataTestCase.setUp(self)
        d = tomorrow()
        self.t1 = self.new_task(description='T1')
        self.t2 = self.new_task(description='T2', due_date=d)
        
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
        
        
        
class CSS_class_test(TestCase):

    def setUp(self):
        self.overdue   = Task(description = "t1", due_date = yesterday())
        self.very_soon = Task(description = 't2', due_date = today())
        self.soon      = Task(description = 't3', due_date = today() + datetime.timedelta(10))
        self.later     = Task(description = 't3', due_date = today() + datetime.timedelta(30))

        self.high   = Task(description = "high",   priority = 2)
        self.medium = Task(description = 'medium', priority = 1)
        self.low    = Task(description = 'low',    priority = 0)
        
    def test_due_date_css_classes_for_overdue(self):
        self.assertTrue(self.overdue.is_overdue())
        self.assertFalse(self.very_soon.is_overdue())
        self.assertFalse(self.soon.is_overdue())

    def test_due_date_css_classes_for_very_soon(self):
        self.assertFalse(self.overdue.is_due_very_soon())
        self.assertTrue(self.very_soon.is_due_very_soon())
        self.assertFalse(self.soon.is_due_very_soon())

    def test_due_date_css_classes_for_soon(self):
        self.assertFalse(self.overdue.is_due_soon())
        self.assertFalse(self.very_soon.is_due_soon())
        self.assertTrue(self.soon.is_due_soon())

    def test_due_date_css_class(self):
        self.assertEqual('date-overdue',   self.overdue.css_due_date_class())
        self.assertEqual('date-very-soon', self.very_soon.css_due_date_class())        
        self.assertEqual('date-soon',      self.soon.css_due_date_class())        
        self.assertEqual('date-soon',      self.soon.css_due_date_class())        
        self.assertEqual('',               self.later.css_due_date_class())        
    
    def test_prio_css_class(self):
        self.assertEqual('prio-high',   self.high.css_prio_class())
        self.assertEqual('prio-medium', self.medium.css_prio_class())
        self.assertEqual('',            self.low.css_prio_class())
    
    
