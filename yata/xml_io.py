from yata.models import Task, Context
from xml.dom.minidom import parseString
import re
import datetime


def create_tasks_from_xml(the_xml):

    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def handle_date(ddate):
        s = getText(ddate.childNodes)
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

    def handle_context(context):
        context_name = getText(context.childNodes)
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

    def handle_title(note):
        return getText(note.childNodes)

    def handle_notes(notes):
        if notes:
            return handle_context(notes[0])
        else:
            return None

    def handle_task(task):
        titles = task.getElementsByTagName("title")
        sdates = task.getElementsByTagName("startdate")
        ddates = task.getElementsByTagName("duedate")
        contexts = task.getElementsByTagName("context")
        notes = task.getElementsByTagName("note")
        t = Task(description = handle_titles(titles),
                  start_date = handle_dates(sdates),
                  due_date = handle_dates(ddates),
                  context = handle_contexts(contexts),
                  note = handle_notes(notes))
        t.save()

    def handle_tasks(tasks):
        for t in tasks:
            handle_task(t)

    dom = parseString(the_xml)
    tasks = dom.getElementsByTagName("item")
    handle_tasks(tasks)
    