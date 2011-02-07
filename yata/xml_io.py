from django.db import transaction
from xml.dom.minidom import parseString
from yata.models import Task, Context
import re
import datetime


@transaction.commit_on_success
def create_tasks_from_xml(the_xml):

    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def handle_date(ddate):
        s = getText(ddate.childNodes)
        if s is '':
            return None
        match_object = re.match('(\d{4})-(\d{2})-(\d{2})', s)
        year = match_object.group(1)
        month = match_object.group(2)
        day = match_object.group(3)
        return datetime.date(int(year), int(month), int(day))
        
    def handle_dates(ddates):
        if ddates:
            return handle_date(ddates[0])
        else:
            return None
        
    def handle_title(title):
        return getText(title.childNodes)

    def handle_titles(titles):
        if titles:
            return handle_title(titles[0])
        else:
            return '[No title]'

    def handle_prio(prio):
        p = getText(prio.childNodes)
        for pair in Task.PRIO_CHOICES:
            if (p == pair[1]):
                return pair[0]

    def handle_prios(prios):
        if prios:
            return handle_prio(prios[0])
        else:
            return 0

    def handle_context(context):
        context_name = getText(context.childNodes)
        if context_name is '':
            return None
        contexts = Context.objects.filter(title__exact = context_name)
        if contexts.exists():
            c = contexts[0]
        else:
            c = Context(title = context_name)
            c.save()
        return c

    def handle_contexts(contexts):
        if contexts:
            return handle_context(contexts[0])
        else:
            return None

    def handle_note(note):
        return getText(note.childNodes)
            
    def handle_notes(notes):
        if notes:
            return handle_note(notes[0])
        else:
            return None

    def handle_completed(completed):
        return getText(completed.childNodes) != '0000-00-00'
        
    def handle_completeds(completeds):
        if completeds:
            return handle_completed(completeds[0])
        else:
            return False

    def handle_task(task):
        titles = task.getElementsByTagName("title")
        prios = task.getElementsByTagName("priority")
        sdates = task.getElementsByTagName("startdate")
        ddates = task.getElementsByTagName("duedate")
        contexts = task.getElementsByTagName("context")
        notes = task.getElementsByTagName("note")
        completeds = task.getElementsByTagName("completed")
        t = Task(description = handle_titles(titles),
                  priority = handle_prios(prios),
                  start_date = handle_dates(sdates),
                  due_date = handle_dates(ddates),
                  context = handle_contexts(contexts),
                  done = handle_completeds(completeds),
                  note = handle_notes(notes))
        t.save()

    def handle_tasks(tasks):
        for t in tasks:
            handle_task(t)

    dom = parseString(the_xml)
    tasks = dom.getElementsByTagName("item")
    handle_tasks(tasks)
    
    
    
def create_tasks_from_file(xml_file_name):
    with open(xml_file_name) as f:
        the_xml = f.read()
        create_tasks_from_xml(the_xml)