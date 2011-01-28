from django.test import TestCase
from yata.models import Task, relativeDueDate, due_date_cmp, next_date
import datetime
import time
from django.test.client import Client


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
        
        
