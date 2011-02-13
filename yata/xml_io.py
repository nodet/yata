from django.db import transaction
from django.utils.html import escape
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

    def handle_repeat(repeat_string):
        if repeat_string == 'Yearly':
            return (1, 'Y')
        if repeat_string == 'Quaterly':
            return (3, 'M')
        if repeat_string == 'Monthly':
            return (1, 'M')
        if repeat_string == 'Biweekly':
            return (2, 'W')
        if repeat_string == 'Weekly':
            return (1, 'W')
            
        match_object = re.match('Every (\d{1,4}) (.).*', repeat_string)
        if match_object is None:
            return (0, '')
        return (match_object.group(1), match_object.group(2).upper())
        
        
    def handle_completed(completed):
        return completed != '0000-00-00'
        
    def handle_task(task):
        repeat = expect_one_of(task, "repeat", handle_repeat, (0,None))
        t = Task(
            description = expect_one_of(task, "title"),
            priority    = expect_one_of(task, "priority", handle_prio, 0),
            start_date  = expect_one_of(task, "startdate", handle_date),
            due_date    = expect_one_of(task, "duedate", handle_date),
            context     = expect_one_of(task, "context", handle_context),
            repeat_nb   = repeat[0],
            repeat_type = repeat[1],
            done        = expect_one_of(task, "completed", handle_completed, False),
            note        = expect_one_of(task, "note"),
        )
        t.save()
        return t

        
    dom = parseString(the_xml)
    return expect_list(dom, "item", handle_task)
    
    
    
def create_tasks_from_file(xml_file_name):
    with open(xml_file_name) as f:
        the_xml = f.read()
        return create_tasks_from_xml(the_xml)
        
        
        
def create_xml_from_tasks(tasks):

    def tag(tag_name, text):
        return '<%s>' % tag_name + escape(text) + '</%s>\n' % tag_name

    def write_title(t):
        return tag("title", t.description)
        
    def write_priority(t):
        if t.priority == 0:
            return ''
        return tag("priority", t.priority_as_string())
        
    def write_date(tag_name, d):
        if d is None:
            return ''
        return tag(tag_name, d.isoformat())
        
    def write_start_date(t):
        return write_date("startdate", t.start_date)

    def write_due_date(t):
        return write_date("duedate", t.due_date)

    def write_context(t):
        if t.context is None:
            return ''
        return tag("context", t.context.title)

    def write_note(t):
        if t.note is None:
            return ''
        return tag("note", t.note)
        
    def write_done(t):
        return tag('completed', '1111-11-11') if t.done else ''    
        
    def write_repeat(t):
    
        if not t.is_repeating():
            return ''
            
        def get_name_for(nb, type):
            dict = {
                'W': 'week',
                'M': 'month',
                'Y': 'year',
            }
            s = dict[type]
            if nb > 1:
                s = '%ss' % s
            return s
        
        s = 'Every %s %s' % (t.repeat_nb, get_name_for(t.repeat_nb, t.repeat_type))
        return tag('repeat', s)
    
    def write_task(t):
        res = ['<item>\n']
        res.append(write_title(t))
        res.append(write_priority(t))
        res.append(write_start_date(t))
        res.append(write_due_date(t))
        res.append(write_context(t))
        res.append(write_note(t))
        res.append(write_repeat(t))
        res.append(write_done(t))
        res.append('</item>\n')
        return ''.join(res)

    res = ["<xml>\n"]
    for t in tasks:
        res.append(write_task(t))
    res.append("</xml>")
    return ''.join(res)








