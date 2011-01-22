from django.template import Context, loader
from django.http import HttpResponse
from yata.models import Task

def index(request):
    tasks = sorted(Task.objects.all().exclude(done__exact = True), Task.compare_by_due_date)
    recently_done = Task.objects.all().filter(done__exact = True).order_by('last_edited')
    t = loader.get_template('yata/index.html')
    c = Context({
        'tasks': tasks,
        'tasks_recently_done': recently_done,
    })
    return HttpResponse(t.render(c))