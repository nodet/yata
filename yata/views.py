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
            sdate = form.cleaned_data['start_date']
            ddate = form.cleaned_data['due_date']
            repeat_nb = form.cleaned_data['repeat_nb']
            repeat_type = form.cleaned_data['repeat_type']
            Task(description = desc, start_date = sdate, due_date = ddate, repeat_nb = repeat_nb, repeat_type = repeat_type).save()
            return HttpResponseRedirect('/yata/')
    else:
        form = AddTaskForm()
        
    # Either the form was not valid, or we've just created it
    return render_to_response('yata/add_task.html', {
        'form': form,
    }, context_instance=RequestContext(request))
 
 
def edit(request, task_id):
    t = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        form = AddTaskForm(request.POST)    # A form bound to the POST data
        if form.is_valid():
            t.description = form.cleaned_data['description']
            t.start_date = form.cleaned_data['start_date']
            t.due_date = form.cleaned_data['due_date']
            t.repeat_nb = form.cleaned_data['repeat_nb']
            t.repeat_type = form.cleaned_data['repeat_type']
            t.save()
            return HttpResponseRedirect('/yata/')
    else:
        data = {'description': t.description,
                'start_date': t.start_date,
                'due_date': t.due_date,
                'repeat_nb': t.repeat_nb,
                'repeat_type': t.repeat_type}
        form = AddTaskForm(data)
        
    # Either the form was not valid, or we've just created it
    return render_to_response('yata/edit.html', {
        'form': form,
        'id': t.id
    }, context_instance=RequestContext(request))
