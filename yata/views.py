from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, loader, RequestContext

from yata.models import Task, Context, group_by
from yata.forms import AddTaskForm, AddContextForm, UploadXMLForm
from yata.xml_io import create_tasks_from_xml, create_xml_from_tasks

import datetime


@login_required
def index(request):

    def build_context_menu(chosen):
        l = []
        l.append(('All', reverse('yata.views.select_context_all')))
        l.append(('None', reverse('yata.views.select_context_none')))
        for c in Context.objects.filter(user = request.user):
            l.append((c.title, reverse('yata.views.select_context', args=[c.id,])))
        return [ 'Context to display', chosen, l ]

    def context_menu_displayed(contexts_to_display):
        # Specify which context is actually displayed
        if len(contexts_to_display) == 0:
            return 'All'
        elif contexts_to_display[0] == '':
            return 'None'
        else:
            return contexts_to_display[0]

    contexts_to_display = request.session.get('contexts_to_display', [])
    # Need to ensure something is put in the session so that it's saved.
    request.session['contexts_to_display'] = contexts_to_display
    
    def build_future_menu(chosen):
        return [ 'Future tasks', chosen, [
                    ('Hide', reverse('hide-future-tasks')),
                    ('Show', reverse('show-future-tasks')),
        ]]

    def future_tasks_menu_displayed(b):
        return 'Show' if b else 'Hide'

    show_future_tasks = request.session.get('show_future_tasks', False)
    # Need to ensure something is put in the session so that it's saved.
    request.session['show_future_tasks'] = show_future_tasks


    def build_done_menu(chosen):
        return [ 'Tasks done', chosen, [
                    ('Active', reverse('show-active-tasks')),
                    ('Done', reverse('show-done-tasks')),
                    ('All', reverse('show-all-tasks')),
        ]]

    def show_task(t, show_tasks_done):
        if show_tasks_done == 'All':
            return True
        return t.done == (show_tasks_done == 'Done')

    show_tasks_done = request.session.get('show_tasks_done', 'Active')
    request.session['show_tasks_done'] = show_tasks_done

    tasks = [t for t in Task.objects.for_user(request.user)
                if show_task(t, show_tasks_done)
                if t.matches_contexts(contexts_to_display)
                if show_future_tasks or t.can_start_now()]
    tasks.sort(Task.compare)
    tasks = group_by(tasks, lambda t:
        'Importance %s' % t.importance()
    )

    the_context_menu = build_context_menu(context_menu_displayed(contexts_to_display))
    the_future_menu  = build_future_menu(future_tasks_menu_displayed(show_future_tasks))
    the_done_menu    = build_done_menu(show_tasks_done)

    footers = [ [
        (reverse('add-task'),    'Add task'),
        (reverse('add-context'), 'Add context'),
    ], [
        ('/admin/yata/task',  'Admin'),
        (reverse('yata.views.xml_import'), 'Import tasks...'),
        (reverse('yata.views.xml_export'), 'Export tasks...'),
        ('/yata/accounts/logout/', 'Logout'),
    ] ]
    
    return render_to_response('yata/index.html', {
        'tasks': tasks,
        'menus': [the_context_menu, the_future_menu, the_done_menu],
        'footers': footers,
    })



def _select_context_helper(request, contexts):
    s = request.session
    s['contexts_to_display'] = contexts
    s.modified = True
    s.save()
    return HttpResponseRedirect(reverse('yata.views.index'))

def select_context(request, context_id):
    c = get_object_or_404(Context, pk=context_id)
    if c.user != request.user:
        raise Http404
    return _select_context_helper(request, [c.title])

def select_context_all(request):
    return _select_context_helper(request, [])

def select_context_none(request):
    return _select_context_helper(request, [''])


def show_future_tasks(request, b):
    s = request.session
    s['show_future_tasks'] = b
    s.modified = True
    s.save()
    return HttpResponseRedirect(reverse('yata.views.index'))


def show_tasks_done(request, b):
    s = request.session
    s['show_tasks_done'] = b
    s.modified = True
    s.save()
    return HttpResponseRedirect(reverse('yata.views.index'))


def mark_done(request, id, b = True):
    t = get_object_or_404(Task, pk=id)
    if t.user != request.user:
        raise Http404
    t.mark_done(b)
    return HttpResponseRedirect(reverse('yata.views.index'))



def _edit_any_form(request, the_class, the_form_class, view_func, delete_func, id = None):
    c = get_object_or_404(the_class, pk=id) if id else None
    if c and c.user != request.user:
        raise Http404
    if request.method == 'POST':
        form = the_form_class(request.POST, instance=c)
        if form.is_valid():
            the_object = form.save(commit=False)
            the_object.user = request.user
            the_object.save()
            return HttpResponseRedirect(reverse('yata.views.index'))
    else:
        form = the_form_class(instance = c)

    # Either the form was not valid, or we've just created it
    return render_to_response('yata/edit.html', {
        'form': form,
        'action': reverse(view_func, args=[id] if id else None),
        'delete': reverse(delete_func, args=[id]) if id else None
    }, context_instance=RequestContext(request))


def edit_task(request, id = None):

    # An 'AddTaskForm' that additionally can provide a default value
    # for the context when it makes sense
    # see http://stackoverflow.com/questions/4235883/
    #     django-testing-test-the-initial-value-of-a-form-field/4249407#4249407
    class AddTaskFormWithInitial(AddTaskForm):
        def __init__(self, *args, **kwargs):
            initial = kwargs.get('initial', {})
            c = request.session.get('contexts_to_display')
            if c and len(c) == 1 and c[0] != '':
                initial['context'] = Context.objects.get(title__exact=c[0])
            kwargs['initial'] = initial
            super(AddTaskFormWithInitial, self).__init__(*args, **kwargs)

    return _edit_any_form(request, Task, AddTaskFormWithInitial, edit_task, delete_task, id)


def edit_context(request, id = None):
    return _edit_any_form(request, Context, AddContextForm, edit_context, delete_context, id)


def delete_context(request, id):
    c = get_object_or_404(Context, pk=id)
    if c.user != request.user:
        raise Http404
    
    # in next Django version, use on_delete on the context FK in Task
    # and remove this code
    for t in Task.objects.for_user(request.user).filter(context = c):
        t.context = None
        t.save()
    c.delete()
    return HttpResponseRedirect(reverse('yata.views.index'))

def delete_task(request, id):
    t = get_object_or_404(Task, pk=id)
    if t.user != request.user:
        raise Http404
    t.delete()
    return HttpResponseRedirect(reverse('yata.views.index'))





@login_required
def xml_import(request):
    if request.method == 'POST':
        form = UploadXMLForm(request.POST, request.FILES)
        if form.is_valid():
            create_tasks_from_xml(request.user, request.FILES['file'].read())
            return HttpResponseRedirect(reverse('yata.views.index'))
    else:
        form = UploadXMLForm()
    return render_to_response('yata/xml_import.html', {
        'form': form,
        'action': reverse(xml_import),
    }, context_instance=RequestContext(request))

def xml_export(request):
    the_xml = create_xml_from_tasks(Task.objects.for_user(request.user))
    response = HttpResponse(the_xml, mimetype="text/xml")
    response['Content-Disposition'] = 'attachment; filename=yata.xml'
    return response

    

def edit_user(request, id = None):
    #return _edit_any_form(request, Context, AddUserForm, edit_user, delete_user, id)
    return _edit_any_form(request, Context, UserCreationForm, edit_user, None, id)

def delete_user(request, id):
    pass
