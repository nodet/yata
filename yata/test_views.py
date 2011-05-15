from django.core.urlresolvers import reverse
from django.test import TestCase
from yata.models import Task, Context, relativeDueDate, due_date_cmp, next_date
from yata.test_utils import today, tomorrow, yesterday, flatten
from yata.test_models import YataTestCase
import datetime
import time
from django.test.client import Client


def get_tasks(response):
    return flatten(response.context['tasks'])

def get_contexts(response):
    # get the contexts in the menu, remove the first two items, 
    # return the first element of each of the remaining pairs
    return [p[0] for p in response.context['menus'][0][2][2:]]

    
class MainViewTestBase(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "something to do")
        t.save()
        t = self.new_task(description = "something else", due_date = datetime.date(2011,01,19))
        t.save()
        t = self.new_task(description = "another thing", due_date = datetime.date(2010,01,19));
        t.save();
        
class MainViewTest(MainViewTestBase):        
    def runTest(self):
        response = self.client.get('/yata/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))
        
      
class MainViewHasTasksSorted(MainViewTestBase):
    def runTest(self):
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))
        self.assertEqual(sorted(tasks, Task.compare), tasks)
        
class MainViewShowsOnlyNotDoneTasks(MainViewTestBase):
    def setUp(self):
        MainViewTestBase.setUp(self)
        t = self.new_task(description = "Already done", done = True)
        t.save()
        t = self.new_task(description = "Another that's done", done = True)
        t.save()
    def runTest(self):
        response = self.client.get('/yata/')
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

            
class MainViewDoesNotShowTasksNotStartedTest(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "something to do now", start_date=today())
        t.save()
        # Something in the future. Not just tomorrow, in case the test is run around midnight...
        t = self.new_task(description = "something to do in two days", start_date = tomorrow(tomorrow()))
        t.save()
    def runTest(self):
        response = self.client.get('/yata/')
        self.assertEqual(response.status_code, 200)
        tasks = get_tasks(response)
        self.assertEqual(1, len(tasks))
        
       
class MarkDoneTest(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "something to do")
        t.save()
    def runTest(self):
        response = self.client.get('/yata/')
        self.assertTrue('/yata/task/1/mark_done/' in response.content)
        response = self.client.get('/yata/task/1/mark_done/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(0, len(get_tasks(response)))

class MarkNotDoneTest(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "something to do", done = True)
        t.save()
    def runTest(self):
        # Show all the tasks...
        response = self.client.get('/yata/done/all/', follow=True)
        # ... else tests below would fail!
        self.assertTrue('/yata/task/1/mark_not_done/' in response.content)
        response = self.client.get('/yata/task/1/mark_not_done/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(1, len(get_tasks(response)))


class AddTaskViewTest(YataTestCase):

    def test_get(self):
        response = self.client.get('/yata/task/new/')
        self.assertEqual(response.status_code, 200)
        
    def test_post(self):
        desc = 'The created task'
        prio = 0
        sdate = today()
        ddate = tomorrow()
        repeat_nb = 1
        repeat_type = 'W'
        note = 'the note...'
        response = self.client.post('/yata/task/new/', {
            'description': desc,
            'priority': prio,
            'start_date': sdate,
            'due_date': ddate,
            'repeat_nb': repeat_nb,
            'repeat_type': repeat_type,
            'note': note
        })
        self.assertEqual(response.status_code, 302)   # Redirect
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
        response = self.client.post('/yata/task/new/', {
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
        
        
        
class EditViewTest(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "something to do")
        t.save()
        
    def test_edit_view_saves_the_changes(self):
        c = self.client
        response = c.get('/yata/')
        self.assertTrue('/yata/task/1/edit/' in response.content)
        response = c.get('/yata/task/1/edit/')
        self.assertEqual(200, response.status_code)
        
        ndesc = 'new description'
        prio = 0
        sdate = yesterday()
        ddate = tomorrow()
        nb = 2
        type = 'W'
        done = True
        note = 'the note...'
        response = c.post('/yata/task/1/edit/', {
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
        
    def test_edit_view_returns_404_for_incorrect_user(self):
        self.client.login(username='test2', password='test2')
        response = self.client.get('/yata/task/1/edit/')
        self.assertEqual(response.status_code, 404)
    
        
        

class UrlForActionIsProvidedToEditView(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "UrlForActionIsProvidedToEditView")
        t.save()
    def runTest(self):
        c = self.client
        url = '/yata/task/1/edit/'
        response = c.get(url)
        self.assertEqual(url, response.context['action'])
       
def get_menus(response):
    return response.context['menus']

def get_menu(response, i):
    return get_menus(response)[i]

def get_menu_selection(response, i):
    return get_menus(response)[i][1]
       
class MainViewMenusTests(YataTestCase):

    # menus  ::=  [ menu ]
    # menu   ::=  [ title, selected_value, menu_list ]
    # menu_list ::=  [ item ]
    # item      ::=  ( display,  URL )

    def setUp(self):
        YataTestCase.setUp(self)
        c1 = self.new_context(title = 'C1')
        c1.save()
        c2 = self.new_context(title = 'C2')
        c2.save()
        self.response = self.client.get('/yata/')

    def test_has_menus(self):
        self.assertTrue(not get_menus(self.response) is None)
        
    def test_has_context_menu(self):
        expected = [ 'Context to display', 'All', [
            ('All', '/yata/context/show/all/'),
            ('None', '/yata/context/show/none/'),
            ('C1', '/yata/context/show/1/'),
            ('C2', '/yata/context/show/2/'),
        ]]
        self.assertEqual(expected, get_menu(self.response, 0))
        
    def test_has_future_menu(self):
        expected = [ 'Future tasks', 'Hide', [
            ('Hide', '/yata/future/hide/'),
            ('Show', '/yata/future/show/'),
        ]]
        self.assertEqual(expected, get_menu(self.response, 1))
        
    def test_has_done_menu(self):
        expected = [ 'Tasks done', 'Active', [
            ('Active', '/yata/done/no/'), 
            ('Done', '/yata/done/yes/'),
            ('All', '/yata/done/all/'),
        ]]
        self.assertEqual(expected, get_menu(self.response, 2))
        
        
class FilterTaskByContextSetup(YataTestCase):        

    def setUp(self):
        YataTestCase.setUp(self)
        c1 = self.new_context(title = 'C1')
        c1.save()
        c2 = self.new_context(title = 'C2')
        c2.save()
        t = self.new_task(description = "In no context")
        t.save()
        t = self.new_task(description = "In context 'C1'", context = c1)
        t.save()
        t = self.new_task(description = "In context 'C2'", context = c2)
        t.save()
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


class EditViewHasDeleteButton(FilterTaskByContextSetup):
    def test_delete_context(self):
        response = self.client.post('/yata/context/2/delete/', follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(1, Context.objects.all().count())
        self.assertEqual('C1', Context.objects.get(pk = 1).title)
        
        # We've just deleted a task!
        self.assertEqual(3, Task.objects.all().count())

    def test_cant_delete_others_context(self):
        # Log as another user
        self.client.login(username='test2', password='test2')
        # check can't delete first user's context
        response = self.client.post('/yata/context/2/delete/', follow = True)
        self.assertEqual(response.status_code, 404)
        
    def test_delete_task(self):
        response = self.client.post('/yata/task/2/delete/', follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template.name, 'yata/index.html')
        self.assertEqual(2, Task.objects.all().count())
        for t in Task.objects.all():
            self.assertNotEqual("In context 'C1'", t.description)
        
    def test_cant_delete_others_task(self):
        # Log as another user
        self.client.login(username='test2', password='test2')
        # check can't delete first user's context
        response = self.client.post('/yata/task/2/delete/', follow = True)
        self.assertEqual(response.status_code, 404)
        



        
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

            
class AddContextViewTest(YataTestCase):
    def test_can_create_context_with_view(self):
        title = 'New context'
        response = self.client.post('/yata/context/add/', {
            'title': title,
        })
        all = Context.objects.all()
        self.assertEqual(1, all.count())
        c = all[0]
        self.assertEqual(title, c.title)
        
        
class HideOrShowFutureTasksSetup(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "Not future")
        t.save()
        t = self.new_task(description = "Future", start_date = tomorrow(tomorrow()))
        t.save()
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
        
    def test_session(self):
        self.ask_for_future(True)
        self.assertEqual(True, self.client.session['show_future_tasks'])

    def test_show_future_tasks(self):
        self.ask_for_future(True)
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual('Show', get_menu_selection(response, 1))
        self.assertEqual(2, len(tasks))
    

class ShowFutureTasksMenuTests(HideOrShowFutureTasksSetup):    
    
    def test_show_future_tasks(self):
        self.ask_for_future(False)
        response = self.client.get('/yata/future/show/', follow=True)
        self.assertEqual('Show', get_menu_selection(response, 1))
        self.assertEqual(2, len(get_tasks(response)))
            
    def test_hide_future_tasks(self):
        self.ask_for_future(False)
        response = self.client.get('/yata/future/hide/', follow=True)
        self.assertEqual('Hide', get_menu_selection(response, 1))
        self.assertEqual(1, len(get_tasks(response)))
            
            
class HideOrShowTasksDone(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        t = self.new_task(description = "Active")
        t.save()
        t = self.new_task(description = "Done", done = True)
        t.save()
        # Make sure we call the view first so that it saves a session
        self.client.get('/yata/')
        
    def test_default_is_to_hide_tasks_done(self):
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(1, len(tasks))
        self.assertFalse(tasks[0].done)
        
    def ask_for_done(self, done):
        session = self.client.session
        session['show_tasks_done'] = done
        session.save()

    def test_session(self):
        self.ask_for_done('All')
        self.assertEqual('All', self.client.session['show_tasks_done'])

    def test_show_tasks_done(self):
        response = self.client.get('/yata/done/yes/', follow=True)
        tasks = get_tasks(response)
        self.assertEqual('Done', get_menu_selection(response, 2))
        self.assertEqual(1, len(tasks))
        self.assertTrue(tasks[0].done)
        
    def test_show_tasks_not_done(self):
        response = self.client.get('/yata/done/no/', follow=True)
        tasks = get_tasks(response)
        self.assertEqual('Active', get_menu_selection(response, 2))
        self.assertEqual(1, len(tasks))
        self.assertFalse(tasks[0].done)
        
    def test_show_all_tasks(self):
        response = self.client.get('/yata/done/all/', follow=True)
        tasks = get_tasks(response)
        self.assertEqual('All', get_menu_selection(response, 2))
        self.assertEqual(2, len(tasks))
        
    
class AddTaskHasDefaultContext(YataTestCase):
    def setUp(self):
        YataTestCase.setUp(self)
        self.c1 = self.new_context(title = 'C1')
        self.c1.save()
        self.c2 = self.new_context(title = 'C2')
        self.c2.save()
        # Make sure we call the view first so that it saves a session
        self.client.get('/yata/')

    def ask_for_contexts(self, contexts):
        session = self.client.session
        session['contexts_to_display'] = contexts
        session.save()
        
    def test_default_is_empty(self):
        response = self.client.get('/yata/task/new/')
        self.assertFalse('context' in response.context['form'].initial.keys())

    def test_get_default_context(self):
        self.ask_for_contexts(['C2'])
        response = self.client.get('/yata/task/new/')
        self.assertEqual(self.c2, response.context['form'].initial['context'])

    def test_no_default_if_several_selected(self):
        self.ask_for_contexts(['C1','C2'])
        response = self.client.get('/yata/task/new/')
        self.assertFalse('context' in response.context['form'].initial.keys())
        
    def test_no_default_if_none(self):
        self.ask_for_contexts([])
        response = self.client.get('/yata/task/new/')
        self.assertFalse('context' in response.context['form'].initial.keys())

    def test_no_default_if_all(self):
        self.ask_for_contexts([''])
        response = self.client.get('/yata/task/new/')
        self.assertFalse('context' in response.context['form'].initial.keys())


        
class CheckForURLsInFooter(YataTestCase):

    def setUp(self):
        YataTestCase.setUp(self)
        self.response = self.client.get('/yata/')

    def test_for_URLs_in_footer(self):
        self.assertTrue('<a href="/yata/task/new/">Add task</a>' in self.response.content)
        self.assertTrue('<a href="/yata/context/add/">Add context</a>' in self.response.content)
        self.assertTrue('<a href="/admin/yata/task">Admin</a>' in self.response.content)
        self.assertTrue('<a href="/yata/xml/import/">Import tasks...</a>' in self.response.content)
        self.assertTrue('<a href="/yata/xml/export/">Export tasks...</a>' in self.response.content)


class LoginViews(YataTestCase):

    def test_exists_login_view(self):
        response = self.client.get('/yata/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_exists_logout_view(self):
        response = self.client.get('/yata/accounts/logout/')
        self.assertEqual(response.status_code, 200)

    def test_main_view_requires_login(self):
        # Create a new client: self.client is logged in...
        response = Client().get('/yata/', follow=True)
        self.assertEqual(response.redirect_chain, [(u'http://testserver/yata/accounts/login/?next=/yata/',302)])
    
        

class MainViewShowsOnlyItemsFromCurrentUser(MainViewTestBase):
    def setUp(self):
        MainViewTestBase.setUp(self)
        # Items owned by u2, while the current user is u1
        Task(user = self.u2, description = 'belongs to u2').save()
        Context(user = self.u2, title = 'incorrect context').save()

    def test_show_only_tasks_from_user(self):
        all_users = Task.objects.all()
        for_user = Task.objects.filter(user = self.u1).all()
        self.assertEqual(all_users.count(), for_user.count() + 1)
        
        response = self.client.get('/yata/')
        tasks = get_tasks(response)
        self.assertEqual(3, len(tasks))

    def test_show_only_contexts_from_user(self):
        all_users = Context.objects.all()
        for_user = Context.objects.filter(user = self.u1).all()
        self.assertEqual(all_users.count(), for_user.count() + 1)
        
        response = self.client.get('/yata/')
        contexts = get_contexts(response)
        self.assertFalse('incorrect context' in contexts)
        