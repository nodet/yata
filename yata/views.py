from django.template import Context, loader
from django.http import HttpResponse
from yata.models import Task

def index(request):
    tasks = sorted(Task.objects.all(), Task.compare_by_due_date)
    t = loader.get_template('yata/index.html')
    c = Context({
        'tasks': tasks,
    })
    return HttpResponse(t.render(c))