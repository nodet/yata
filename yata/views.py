from django.shortcuts import get_object_or_404
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from yata.models import Task
from yata.forms import AddTaskForm

import datetime


def index(request):

    tasks = Task.objects.all()
    tasks = tasks.exclude(done__exact = True)
    tasks = filter(lambda t: not t.is_future(), tasks)
    tasks = sorted(tasks, Task.compare_by_due_date)

    recently_done = Task.objects.all()
    recently_done = recently_done.filter(done__exact = True)
    recently_done = recently_done.order_by('-last_edited')

    t = loader.get_template('yata/index.html')
    c = Context({
        'tasks': tasks,
        'tasks_recently_done': recently_done,
    })
    return HttpResponse(t.render(c))
    

    
def mark_done(request, task_id, b = True):
    t = get_object_or_404(Task, pk=task_id)
    t.mark_done(b)
    return HttpResponseRedirect(reverse('yata.views.index'))


def edit_or_add(request, task_id = None):
    t = get_object_or_404(Task, pk=task_id) if task_id else None
    if request.method == 'POST':
        form = AddTaskForm(request.POST, instance=t)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/yata/')
    else:
        form = AddTaskForm(instance = t)
        
    # Either the form was not valid, or we've just created it
    dic = {'form': form}
    if task_id:
        dic['id'] = t.id
    return render_to_response('yata/edit.html', dic, 
        context_instance=RequestContext(request))
    
def add_task(request):
    return edit_or_add(request)
 
def edit(request, task_id):
    return edit_or_add(request, task_id)
