from django.shortcuts import get_object_or_404
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from yata.models import Task

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
    t.done = b
    t.save()
    return HttpResponseRedirect(reverse('yata.views.index'))
