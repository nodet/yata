from django.shortcuts import get_object_or_404
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from yata.models import Task, Context
from yata.forms import AddTaskForm

import datetime


def index(request):

    tasks = Task.objects.all(). \
                exclude(done__exact = True)

    contexts_to_display = request.session.get('contexts_to_display', [])
    # Need to ensure something is put in the session so that it's saved.
    request.session['contexts_to_display'] = contexts_to_display
    if len(contexts_to_display):
        tasks = filter(lambda t: t.matches_contexts(contexts_to_display), tasks)

    tasks = filter(lambda t: not t.is_future(), tasks)
    tasks = sorted(tasks, Task.compare_by_due_date)
    
    recently_done = Task.objects.all(). \
                        filter(done__exact = True). \
                        order_by('-last_edited')

    return render_to_response('yata/index.html', {
        'tasks': tasks,
        'tasks_recently_done': recently_done,
    })
    

    
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
