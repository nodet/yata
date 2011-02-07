from django.db import transaction
from xml.dom.minidom import parseString
from yata.models import Task, Context
import re
import datetime


@transaction.commit_on_success
def create_tasks_from_xml(the_xml):

    def getText(nodelist):
        rc = []
        for node in nodelist.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def expect_one_of(task, tag_name, f = None, default = None):
        list = task.getElementsByTagName(tag_name)
        if len(list) > 1:
            raise Exception, "Only one '%s' tag allowed!" % tag_name
        if not list:
            return default
        text = getText(list[0])
        return f(text) if f else text
            
    def expect_list(node, tag_name, f):
        list = node.getElementsByTagName(tag_name)
        return [f(item) for item in list]

        
    def handle_date(s):
        if s is '':
            return None
        match_object = re.match('(\d{4})-(\d{2})-(\d{2})', s)
        year = match_object.group(1)
        month = match_object.group(2)
        day = match_object.group(3)
        return datetime.date(int(year), int(month), int(day))
        
    def handle_prio(p):
        for pair in Task.PRIO_CHOICES:
            if (p == pair[1]):
                return pair[0]

    def handle_context(context_name):
        if context_name is '':
            return None
        contexts = Context.objects.filter(title__exact = context_name)
        if contexts.exists():
            c = contexts[0]
        else:
            c = Context(title = context_name)
            c.save()
        return c

    def handle_completed(completed):
        return completed != '0000-00-00'
        
    def handle_task(task):
        Task(
            description = expect_one_of(task, "title"),
            priority    = expect_one_of(task, "priority", handle_prio, 0),
            start_date  = expect_one_of(task, "startdate", handle_date),
            due_date    = expect_one_of(task, "duedate", handle_date),
            context     = expect_one_of(task, "context", handle_context),
            done        = expect_one_of(task, "completed", handle_completed, False),
            note        = expect_one_of(task, "note"),
        ).save()

        
    dom = parseString(the_xml)
    expect_list(dom, "item", handle_task)
    
    
    
def create_tasks_from_file(xml_file_name):
    with open(xml_file_name) as f:
        the_xml = f.read()
        create_tasks_from_xml(the_xml)