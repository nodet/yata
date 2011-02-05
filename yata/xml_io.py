from yata.models import Task
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

    def handle_duedate(ddate):
        s = getText(ddate.childNodes)
        match_object = re.match('(\d{4})-(\d{2})-(\d{2})', s)
        year = match_object.group(1)
        month = match_object.group(2)
        day = match_object.group(3)
        return datetime.date(int(year), int(month), int(day))
        
    def handle_duedates(ddates):
        if ddates:
            return handle_duedate(ddates[0])
        else:
            return None
        
    def handle_title(title):
        return getText(title.childNodes)

    def handle_titles(titles):
        if titles:
            return handle_title(titles[0])
        else:
            return '[No title]'

    def handle_task(task):
        titles = task.getElementsByTagName("title")
        ddates = task.getElementsByTagName("duedate")
        t = Task(description = handle_titles(titles),
                  due_date = handle_duedates(ddates))
        t.save()

    def handle_tasks(tasks):
        for t in tasks:
            handle_task(t)

    dom = parseString(the_xml)
    tasks = dom.getElementsByTagName("item")
    handle_tasks(tasks)
    