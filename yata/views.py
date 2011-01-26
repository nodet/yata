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

    
def add_task(request):
    if request.method == 'POST':            # The form has been submitted
        form = AddTaskForm(request.POST)    # A form bound to the POST data
        if form.is_valid():
            # Create the task
            desc = form.cleaned_data['description']
            ddate = form.cleaned_data['due_date']
            Task(description = desc, due_date = ddate).save()
            return HttpResponseRedirect('/yata/')
    else:
        form = AddTaskForm()
        
    return render_to_response('yata/add_task.html', {
        'form': form,
    }, context_instance=RequestContext(request))
 