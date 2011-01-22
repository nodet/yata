from django.template import Context, loader
from django.http import HttpResponse
from yata.models import Task

def index(request):
    tasks = Task.objects.all()
    t = loader.get_template('yata/index.html')
    c = Context({
        'tasks': tasks,
    })
    return HttpResponse(t.render(c))