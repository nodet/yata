from django.shortcuts import get_object_or_404
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from yata.models import Task, Context
from yata.forms import AddTaskForm, AddContextForm, UploadXMLForm
from yata.xml_io import create_tasks_from_xml, create_xml_from_tasks

import datetime


def index(request):

    def context_menu():
        l = []
        l.append(('All', '/yata/context/show/all/'))
        l.append(('None', '/yata/context/show/none/'))
        for c in Context.objects.all():
            l.append((c.title, '/yata/context/show/%s/' % c.id))
        return l

    def context_menu_displayed(contexts_to_display):
        # Specify which context is actually displayed
        if len(contexts_to_display) == 0:
            return 'All'
        elif contexts_to_display[0] is '':
            return 'None'
        else:
            return contexts_to_display[0]

    contexts_to_display = request.session.get('contexts_to_display', [])
    # Need to ensure something is put in the session so that it's saved.
    request.session['contexts_to_display'] = contexts_to_display


    def future_tasks_menu():
        return (('Show', '/yata/future/show/'), 
                 ('Hide', '/yata/future/hide/'))
                 
    def future_tasks_menu_displayed(b):
        return 'Show' if b else 'Hide'
        
    show_future_tasks = request.session.get('show_future_tasks', False)
    # Need to ensure something is put in the session so that it's saved.
    request.session['show_future_tasks'] = show_future_tasks

    
    tasks = [t for t in Task.objects.all().exclude(done__exact = True)
                if t.matches_contexts(contexts_to_display)
                if show_future_tasks or t.can_start_now()]
    tasks.sort(Task.compare)
    
    recently_done = Task.objects.all(). \
                        filter(done__exact = True). \
                        order_by('-last_edited')

    return render_to_response('yata/index.html', {
        'tasks': tasks,
        'contexts': context_menu(),
        'context_displayed': context_menu_displayed(contexts_to_display),
        'future_tasks_menu': future_tasks_menu(),
        'future_tasks_menu_selected': future_tasks_menu_displayed(show_future_tasks),
        'tasks_recently_done': recently_done,
    })
    
    

def _select_context_helper(request, contexts):
    s = request.session
    s['contexts_to_display'] = contexts
    s.modified = True
    s.save()
    return HttpResponseRedirect(reverse('yata.views.index'))
    
def select_context(request, context_id):
    c = get_object_or_404(Context, pk=context_id)
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
    
    
def mark_done(request, task_id, b = True):
    t = get_object_or_404(Task, pk=task_id)
    t.mark_done(b)
    return HttpResponseRedirect(reverse('yata.views.index'))



def _edit_any_form(request, the_class, the_form_class, view_func, delete_func, id = None):
    c = get_object_or_404(the_class, pk=id) if id else None
    if request.method == 'POST':
        form = the_form_class(request.POST, instance=c)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/yata/')
    else:
        form = the_form_class(instance = c)
        
    # Either the form was not valid, or we've just created it
    return render_to_response('yata/edit.html', {
        'form': form, 
        'action': reverse(view_func, args=[id] if id else None),
        'delete': reverse(delete_func, args=[id]) if id else None
    }, context_instance=RequestContext(request))

    
def edit(request, task_id = None):
    return _edit_any_form(request, Task, AddTaskForm, edit, delete_task, task_id)

        
def edit_context(request, id = None):
    return _edit_any_form(request, Context, AddContextForm, edit_context, delete_context, id)


def delete_context(request, id):
    c = get_object_or_404(Context, pk=id)
    # in next Django version, use on_delete on the context FK in Task
    # and remove this code
    for t in Task.objects.filter(context = c):
        t.context = None
        t.save()
    c.delete()
    return HttpResponseRedirect(reverse('yata.views.index'))

def delete_task(request, id):
    t = get_object_or_404(Task, pk=id)
    t.delete()
    return HttpResponseRedirect(reverse('yata.views.index'))

    
    
    
    
def xml_import(request):
    if request.method == 'POST':
        form = UploadXMLForm(request.POST, request.FILES)
        if form.is_valid():
            create_tasks_from_xml(request.FILES['file'].read())
            return HttpResponseRedirect(reverse('yata.views.index'))
    else:
        form = UploadXMLForm()
    return render_to_response('yata/xml_import.html', {
        'form': form,
        'action': reverse(xml_import),
    }, context_instance=RequestContext(request))

def xml_export(request):
    the_xml = create_xml_from_tasks(Task.objects.all())
    response = HttpResponse(the_xml, mimetype="text/xml")
    response['Content-Disposition'] = 'attachment; filename=yata.xml'
    return response
    