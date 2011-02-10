from django.test import TestCase
from yata.models import Task, Context, relativeDueDate, due_date_cmp, next_date
from yata.test_utils import today, tomorrow, yesterday, flatten
import datetime
import time
from django.test.client import Client


def get_tasks(response):
    return flatten(response.context['tasks'])
    
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
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))
        
      
class MainViewHasTasksSorted(MainViewTest):
    def runTest(self):
        c = Client()
        response = c.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))
        self.assertEqual(sorted(tasks, Task.compare), tasks)
        
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
        tasks = get_tasks(response)
        for t in tasks:
            self.assertFalse(t.done)


def have_same_elements(it1, it2):
    if len(it1) != len(it2):
        return False
    for t1, t2 in zip(it1, it2):
        if t1 != t2:
            return False
    return True

            
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
        tasks = get_tasks(response)
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
        self.assertEqual(0, len(get_tasks(response)))

class MarkNotDoneTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do", done = True)
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/1/mark_not_done/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(1, len(get_tasks(response)))

        
class AddTaskViewTest(TestCase):
    def test_get(self):
        response = Client().get('/yata/add_task/')
        self.assertEqual(response.status_code, 200)
        
    def test_post(self):
        desc = 'The created task'
        prio = 0
        sdate = today()
        ddate = tomorrow()
        repeat_nb = 1
        repeat_type = 'W'
        note = 'the note...'
        response = Client().post('/yata/add_task/', {
            'description': desc,
            'priority': prio,
            'start_date': sdate,
            'due_date': ddate,
            'repeat_nb': repeat_nb,
            'repeat_type': repeat_type,
            'note': note
        })
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(desc, t.description)
        self.assertEqual(prio, t.priority)
        self.assertEqual(sdate, t.start_date)
        self.assertEqual(ddate, t.due_date)
        self.assertEqual(repeat_nb, t.repeat_nb)
        self.assertEqual(repeat_type, t.repeat_type)
        self.assertEqual(note, t.note)
        
    def test_post_only_required_fields(self):
        desc = 'The created task'
        prio = 0
        sdate = today()
        ddate = tomorrow()
        repeat_nb = 1
        repeat_type = 'W'
        note = 'the note...'
        response = Client().post('/yata/add_task/', {
            'description': desc,
            'priority': prio
        })
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(desc, t.description)
        self.assertEqual(0, t.priority)
        self.assertEqual(None, t.start_date)
        self.assertEqual(None, t.due_date)
        self.assertEqual(None, t.repeat_nb)
        self.assertEqual(None, t.repeat_type)
        self.assertEqual('', t.note)
        
        
        
class EditViewTest(TestCase):
    def setUp(self):
        t = Task(description = "something to do")
        t.save()
    def runTest(self):
        c = Client()
        response = c.get('/yata/1/edit/')
        self.assertEqual(200, response.status_code)
        
        ndesc = 'new description'
        prio = 0
        sdate = yesterday()
        ddate = tomorrow()
        nb = 2
        type = 'W'
        done = True
        note = 'the note...'
        response = Client().post('/yata/1/edit/', {
            'description': ndesc,
            'priority': prio,
            'start_date': sdate,
            'due_date': ddate,
            'repeat_nb': nb,
            'repeat_type': type,
            'done': done,
            'note': note
        })
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(ndesc, t.description)
        self.assertEqual(prio, t.priority)
        self.assertEqual(sdate, t.start_date)
        self.assertEqual(ddate, t.due_date)
        self.assertEqual(nb, t.repeat_nb)
        self.assertEqual(type, t.repeat_type)
        self.assertEqual(note, t.note)

class UrlForActionIsProvidedToEditView(TestCase):
    def setUp(self):
        t = Task(description = "UrlForActionIsProvidedToEditView")
        t.save()
    def runTest(self):
        c = Client()
        url = '/yata/1/edit/'
        response = c.get(url)
        self.assertEqual(url, response.context['action'])
       
       
class MainViewMenusTests(TestCase):

    # menus  ::=  [ menu ]
    # menu   ::=  [ title, selected_value, menu_list ]
    # menu_list ::=  [ item ]
    # item      ::=  ( display,  URL )

    def setUp(self):
        c1 = Context(title = 'C1')
        c1.save()
        c2 = Context(title = 'C2')
        c2.save()
        self.c = Client()
        self.response = self.c.get('/yata/')

    def get_menus(self):
        return self.response.context['menus']

    def get_menu(self, i):
        return self.get_menus()[i]

    def test_has_menus(self):
        self.assertTrue(not self.get_menus() is None)
        
    def test_has_context_menu(self):
        expected = [ 'Context to display', 'All', [
            ('All', '/yata/context/show/all/'),
            ('None', '/yata/context/show/none/'),
            ('C1', '/yata/context/show/1/'),
            ('C2', '/yata/context/show/2/'),
        ]]
        self.assertEqual(expected, self.get_menu(0))
        
    def test_has_future_menu(self):
        expected = [ 'Future tasks', 'Hide', [
            ('Show', '/yata/future/show/'),
            ('Hide', '/yata/future/hide/'),
        ]]
        self.assertEqual(expected, self.get_menu(1))
        
    def test_has_done_menu(self):
        expected = [ 'Tasks done', 'Not done', [
            ('Not done', '/yata/done/yes/'), 
            ('Done', '/yata/done/no/'),
            ('All', '/yata/done/all/'),
        ]]
        self.assertEqual(expected, self.get_menu(2))
        
        
class FilterTaskByContextSetup(TestCase):        

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
        
    def ask_for_contexts(self, contexts):
        session = self.client.session
        session['contexts_to_display'] = contexts
        session.save()


        
class FilterTasksByContext(FilterTaskByContextSetup):
    def test_default_is_to_show_all_contexts(self):
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))
        
    def test_session(self):
        self.ask_for_contexts(['C1'])
        self.assertEqual('C1', self.client.session['contexts_to_display'][0])

    def test_show_all_contexts(self):
        self.ask_for_contexts([])
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))
    
    def test_show_one_contexts(self):
        self.ask_for_contexts(['C1'])
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(1, len(tasks))
        for t in tasks:
            self.assertEqual('C1', t.context.title)
    
    def test_show_two_contexts(self):
        self.ask_for_contexts(['C1', 'C2'])
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(2, len(tasks))
        for t in tasks:
            self.assertTrue(t.context.title in ['C1','C2'])
    
    def test_show_no_context(self):
        self.ask_for_contexts([''])
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(1, len(tasks))
        for t in tasks:
            self.assertEqual(None, t.context)

    def test_show_one_and_no(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(2, len(tasks))
        for t in tasks:
            self.assertTrue(t.context == None or t.context.title == 'C2')
    
    def test_context_to_show_is_persistent(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/')
        # A second call to check if the setting was stored
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
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
    

class EditViewHasDeleteButton(FilterTaskByContextSetup):
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
        



        
class SelectContextTests(FilterTaskByContextSetup):    
    
    def test_select_one_context(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/context/show/1/', follow=True)
        tasks = get_tasks(response)
        for t in tasks:
            self.assertTrue(t.context.title == 'C1')
    
    def test_select_all_contexts(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/context/show/all/', follow=True)
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))
    
    def test_select_no_context(self):
        self.ask_for_contexts(['', 'C2'])
        response = self.client.get('/yata/context/show/none/', follow=True)
        tasks = get_tasks(response)
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
        
        
class HideOrShowFutureTasksSetup(TestCase):
    def setUp(self):
        t = Task(description = "Not future")
        t.save()
        t = Task(description = "Future", start_date = tomorrow(tomorrow()))
        t.save()
        self.client = Client()
        # Make sure we call the view first so that it saves a session
        self.client.get('/yata/')
        
    def ask_for_future(self, show_future_tasks):
        session = self.client.session
        session['show_future_tasks'] = show_future_tasks
        session.save()
        
        
class HideOrShowFutureTasks(HideOrShowFutureTasksSetup):
    def test_default_is_to_hide_future_tasks(self):
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(1, len(tasks))
        self.assertEqual(None, tasks[0].start_date)
        
    def test_view_is_given_future_tasks_menu(self):
        c = Client()
        url = '/yata/'
        response = c.get(url)
        expected = (('Show', '/yata/future/show/'), 
                    ('Hide', '/yata/future/hide/'))
        self.assertEqual(expected, response.context['future_tasks_menu'])
    
    def test_session(self):
        self.ask_for_future(True)
        self.assertEqual(True, self.client.session['show_future_tasks'])

    def test_show_future_tasks(self):
        self.ask_for_future(True)
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual('Show', response.context['future_tasks_menu_selected'])
        self.assertEqual(2, len(tasks))
    

class ShowFutureTasksMenuTests(HideOrShowFutureTasksSetup):    
    
    def test_show_future_tasks(self):
        self.ask_for_future(False)
        response = self.client.get('/yata/future/show/', follow=True)
        self.assertEqual('Show', response.context['future_tasks_menu_selected'])
        self.assertEqual(2, len(get_tasks(response)))
            
    def test_hide_future_tasks(self):
        self.ask_for_future(False)
        response = self.client.get('/yata/future/hide/', follow=True)
        self.assertEqual('Hide', response.context['future_tasks_menu_selected'])
        self.assertEqual(1, len(get_tasks(response)))
            
            
class HideOrShowTasksDone(TestCase):
    def setUp(self):
        t = Task(description = "Not done")
        t.save()
        t = Task(description = "Done", done = True)
        t.save()
        self.client = Client()
        # Make sure we call the view first so that it saves a session
        self.client.get('/yata/')
        
    def test_default_is_to_hide_tasks_done(self):
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(1, len(tasks))
        self.assertFalse(tasks[0].done)
        
    def test_view_is_given_tasks_done_menu(self):
        c = Client()
        url = '/yata/'
        response = c.get(url)
        expected = (('Not done', '/yata/done/yes/'), 
                    ('Done', '/yata/done/no/'),
                    ('All', '/yata/done/all/'),
        )
        self.assertEqual(expected, response.context['tasks_done_menu'])
    
    def ask_for_done(self, done):
        session = self.client.session
        session['show_tasks_done'] = done
        session.save()

    def test_session(self):
        self.ask_for_done('All')
        self.assertEqual('All', self.client.session['show_tasks_done'])

    def test_show_tasks_done(self):
        self.ask_for_done('Done')
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual('Done', response.context['tasks_done_menu_selected'])
        self.assertEqual(1, len(tasks))
        self.assertTrue(tasks[0].done)
        
    def test_show_tasks_not_done(self):
        self.ask_for_done('Not done')
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual('Not done', response.context['tasks_done_menu_selected'])
        self.assertEqual(1, len(tasks))
        self.assertFalse(tasks[0].done)
        
    def test_show_all_tasks(self):
        self.ask_for_done('All')
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual('All', response.context['tasks_done_menu_selected'])
        self.assertEqual(2, len(tasks))
        
    
class AddTaskHasDefaultContext(TestCase):
    def setUp(self):
        self.c1 = Context(title = 'C1')
        self.c1.save()
        self.c2 = Context(title = 'C2')
        self.c2.save()
        self.client = Client()
        # Make sure we call the view first so that it saves a session
        self.client.get('/yata/')

    def ask_for_contexts(self, contexts):
        session = self.client.session
        session['contexts_to_display'] = contexts
        session.save()
        
    def test_default_is_empty(self):
        response = self.client.get('/yata/add_task/')
        self.assertFalse('context' in response.context['form'].initial.keys())

    def test_get_default_context(self):
        self.ask_for_contexts(['C2'])
        response = self.client.get('/yata/add_task/')
        self.assertEqual(self.c2, response.context['form'].initial['context'])

    def test_no_default_if_several_selected(self):
        self.ask_for_contexts(['C1','C2'])
        response = self.client.get('/yata/add_task/')
        self.assertFalse('context' in response.context['form'].initial.keys())
        
    def test_no_default_if_none(self):
        self.ask_for_contexts([])
        response = self.client.get('/yata/add_task/')
        self.assertFalse('context' in response.context['form'].initial.keys())

    def test_no_default_if_all(self):
        self.ask_for_contexts([''])
        response = self.client.get('/yata/add_task/')
        self.assertFalse('context' in response.context['form'].initial.keys())
                        