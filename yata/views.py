from django.shortcuts import get_object_or_404
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from yata.models import Task, Context
from yata.forms import AddTaskForm, AddContextForm

import datetime


def index(request):

    def get_context_list():
        l = []
        l.append(('All', '/yata/context/show/all/'))
        l.append(('None', '/yata/context/show/none/'))
        for c in Context.objects.all():
            l.append((c.title, '/yata/context/show/%s/' % c.id))
        return l
        
    contexts_to_display = request.session.get('contexts_to_display', [])
    # Need to ensure something is put in the session so that it's saved.
    request.session['contexts_to_display'] = contexts_to_display

    tasks = [t for t in Task.objects.all().exclude(done__exact = True)
                if t.matches_contexts(contexts_to_display)
                if t.can_start_now()]
    tasks.sort(Task.compare_by_due_date)
    
    recently_done = Task.objects.all(). \
                        filter(done__exact = True). \
                        order_by('-last_edited')

    return render_to_response('yata/index.html', {
        'tasks': tasks,
        'contexts': get_context_list(),
        'tasks_recently_done': recently_done,
    })
    
    

def select_context_helper(request, contexts):
    s = request.session
    s['contexts_to_display'] = contexts
    s.modified = True
    s.save()
    return HttpResponseRedirect(reverse('yata.views.index'))
    
def select_context(request, context_id):
    c = get_object_or_404(Context, pk=context_id)
    return select_context_helper(request, [c.title])
    
def select_context_all(request):
    return select_context_helper(request, [])

def select_context_none(request):
    return select_context_helper(request, [''])

    
    
def mark_done(request, task_id, b = True):
    t = get_object_or_404(Task, pk=task_id)
    t.mark_done(b)
    return HttpResponseRedirect(reverse('yata.views.index'))

    
def edit(request, task_id = None):
    t = get_object_or_404(Task, pk=task_id) if task_id else None
    if request.method == 'POST':
        form = AddTaskForm(request.POST, instance=t)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/yata/')
    else:
        form = AddTaskForm(instance = t)
        
    # Either the form was not valid, or we've just created it
    d = {'form': form}
    if task_id:
        # The template needs the id to decide if the form's action
        # is .../add_task or .../{{id}}/edit
        d['id'] = t.id
        action = reverse(edit, args=[task_id])
    else:
        action = reverse(edit)
    d['action'] = action
    return render_to_response('yata/edit.html', d, 
        context_instance=RequestContext(request))

        
def edit_context(request, id = None):
    c = get_object_or_404(Context, pk=id) if id else None
    if request.method == 'POST':
        form = AddContextForm(request.POST, instance=c)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/yata/')
    else:
        form = AddContextForm(instance = c)
        
    # Either the form was not valid, or we've just created it
    d = {'form': form}
    if id:
        # The template needs the id to decide if the form's action
        # is .../add_task or .../{{id}}/edit
        d['id'] = c.id
        action = reverse(edit_context, args=[id])
    else:
        action = reverse(edit_context)
    d['action'] = action
    return render_to_response('yata/edit.html', d, 
        context_instance=RequestContext(request))
