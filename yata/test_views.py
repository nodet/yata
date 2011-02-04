from django.test import TestCase
from yata.models import Task, Context, relativeDueDate, due_date_cmp, next_date, create_tasks_from_xml
from yata.test_utils import today, tomorrow, yesterday
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
        
       
class MarkDoneTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do")
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/1/mark_done/', follow=True)
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
        response = c.get('/yata/1/mark_not_done/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(1, len(response.context['tasks']))
        self.assertEqual(0, response.context['tasks_recently_done'].count())

        
class AddTaskViewTest(TestCase):
    def test_get(self):
        response = Client().get('/yata/add_task/')
        self.assertEqual(response.status_code, 200)
        
    def test_post(self):
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
        
        
class EditViewTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do")
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/1/edit/')
        self.assertEqual(200, response.status_code)
        
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

class UrlForActionIsProvidedToEditView(TestCase):
    def setUp(self):
        t = Task(description = "UrlForActionIsProvidedToEditView")
        t.save()
    def runTest(self):
        c = Client()
        url = '/yata/1/edit/'
        response = c.get(url)
        self.assertEqual(url, response.context['action'])
        
        
        
class FilterTasksByContext(TestCase):
    def setUp(self):
        c1 = Context(title = 'C1')
        c1.save()
        c2 = Context(title = 'C2')
        c2.save()
        t = Task(description = "In no context")
        t.save()
        t = Task(description = "In context 'C1'", context = c1)
        t.save()
        t = Task(description = "In context 'C2'", context = c2)
        t.save()
        self.client = Client()
        # Make sure we call the view first so that it saves a session
        self.client.get('/yata/')
        
    def test_default_is_to_show_all_contexts(self):
        response = self.client.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(3, len(tasks))
        
    def ask_for_contexts(self, contexts):
        session = self.client.session
        session['contexts_to_display'] = contexts
        session.save()
        
    def test_session(self):
        self.ask_for_contexts(['C1'])
        self.assertEqual('C1', self.client.session['contexts_to_display'][0])

    def test_show_all_contexts(self):
        self.ask_for_contexts([])
        response = self.client.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(3, len(tasks))
    
    def test_show_one_contexts(self):
        self.ask_for_contexts(['C1'])
        response = self.client.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(1, len(tasks))
        for t in tasks:
            self.assertEqual('C1', t.context.title)
    
    def test_show_two_contexts(self):
        self.ask_for_contexts(['C1', 'C2'])
        response = self.client.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(2, len(tasks))
        for t in tasks:
            self.assertTrue(t.context.title in ['C1','C2'])
    
    def test_show_no_context(self):
        self.ask_for_contexts([''])
        response = self.client.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(1, len(tasks))
        for t in tasks:
            self.assertEqual(None, t.context)

    def test_show_one_and_no(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(2, len(tasks))
        for t in tasks:
            self.assertTrue(t.context == None or t.context.title == 'C2')
    
    def test_context_to_show_is_persistent(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/')
        # A second call to check if the setting was stored
        response = self.client.get('/yata/')
        tasks = response.context['tasks']
        self.assertEqual(2, len(tasks))
        for t in tasks:
            self.assertTrue(t.context == None or t.context.title == 'C2')

    def test_view_is_given_list_of_contexts(self):
        c = Client()
        url = '/yata/'
        response = c.get(url)
        expected = [('All', '/yata/context/show/all/'), 
            ('None', '/yata/context/show/none/'), 
            (u'C1', '/yata/context/show/1/'), 
            (u'C2', '/yata/context/show/2/')]
        self.assertEqual(expected, response.context['contexts'])
    

class EditViewHasDeleteButton(FilterTasksByContext):
    def test_delete_context(self):
        response = self.client.post('/yata/context/2/delete/', follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(1, Context.objects.all().count())
        self.assertEqual('C1', Context.objects.get(pk = 1).title)
        
        # We've just deleted a task!
        self.assertEqual(3, Task.objects.all().count())

    def test_delete_task(self):
        response = self.client.post('/yata/task/2/delete/', follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(2, Task.objects.all().count())
        for t in Task.objects.all():
            self.assertNotEqual("In context 'C1'", t.description)
        



        
class SelectContextTests(FilterTasksByContext):    
    
    def test_select_one_context(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/context/show/1/', follow=True)
        tasks = response.context['tasks']
        for t in tasks:
            self.assertTrue(t.context.title == 'C1')
    
    def test_select_all_contexts(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/context/show/all/', follow=True)
        tasks = response.context['tasks']
        self.assertEqual(3, len(tasks))
    
    def test_select_no_context(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/context/show/none/', follow=True)
        tasks = response.context['tasks']
        for t in tasks:
            self.assertFalse(t.context)

            
class AddContextViewTest(TestCase):
    def runTest(self):
        title = 'New context'
        response = Client().post('/yata/context/add/', {
            'title': title,
        })
        all = Context.objects.all()
        self.assertEqual(1, all.count())
        c = all[0]
        self.assertEqual(title, c.title)
        
        
class XmlImportTest(TestCase):
    def test_import_one_task(self):
        the_xml = """
<xml>
<item>
<title>Change password</title>
<duedate>2011-03-28</duedate>
</item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(1, Task.objects.all().count())
        t = Task.objects.all()[0]
        self.assertEqual('Change password', t.description)
        self.assertEqual(datetime.date(2011,03,28), t.due_date)
        
        
        