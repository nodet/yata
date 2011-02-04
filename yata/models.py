import unittest
import datetime
import calendar
import re
from django.db import models
from xml.dom.minidom import parseString
import copy


class Task(models.Model):

    REPEAT_CHOICES = (
        ('D', 'day'),
        ('W', 'week'),
        ('M', 'month'),
        ('Y', 'year'),
    )

    description = models.CharField(max_length = 200)
    context = models.ForeignKey('Context', null = True, blank = True)
    start_date = models.DateField(null = True, blank = True)
    due_date = models.DateField(null = True, blank = True)
    repeat_nb = models.PositiveIntegerField(null = True, blank = True)
    repeat_type = models.CharField(max_length = 1, choices = REPEAT_CHOICES, null = True, blank = True)
    done = models.BooleanField()
    last_edited = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        s = self.description
        if self.due_date:
            s = '%s, due %s' % (s, self.relative_due_date())
        if self.is_repeating():
            if self.repeat_nb > 1:
                s = '%s, repeating every %s %ss' % (s, self.repeat_nb, self.repeat_choice(self.repeat_type))
            else:
                s = '%s, repeating every %s' % (s, self.repeat_choice(self.repeat_type))
        return s

    def relative_due_date(self):
        if self.due_date:
            return relativeDueDate(datetime.date.today(), self.due_date)
        return ''
    # When ordering for relative_due_date, use 'due_date' instead
    relative_due_date.admin_order_field = 'due_date'

    def is_future(self):
        if self.start_date:
            return self.start_date >= datetime.date.today()
        return False

    def is_repeating(self):
        return self.repeat_type and self.repeat_nb

    def matches_contexts(self, contexts):
        if not len(contexts):
            # Matching against nothing is always ok
            return True
        if not self.context:
            # If we don't have a context, we must find '' in the list
            return '' in contexts
        return self.context.title in contexts
        
    def can_start_now(self):
        return not self.is_future()
        
    @staticmethod
    def repeat_choice(choice):
        for pair in Task.REPEAT_CHOICES:
            if pair[0] == choice:
                return pair[1]
                
                
    def mark_done(self, b = True):
        if b and self.is_repeating():
            new_task = copy.copy(self)

            if self.start_date:
                new_task.start_date = next_date(self.start_date, self.repeat_nb, self.repeat_type)
            if not self.start_date or self.due_date:
                d = datetime.date.today()
                if self.due_date and (self.due_date > d):
                    d = self.due_date
                new_task.due_date = next_date(d, self.repeat_nb, self.repeat_type)

            new_task.save()
        self.done = b
        self.save()
        
        
    @staticmethod
    def compare_by_due_date(t1, t2):
        return due_date_cmp(t1.due_date, t2.due_date)
                
    
def due_date_cmp(t1, t2):
    if t1 == None and t2 == None:
        return 0;
    if t1 == None:
        return 1
    if t2 == None:
        return -1
    return (t1 - t2).days
    
        
def relativeDueDate(origin, theDate):
    "Returns a string representing theDate relative to origin (i.e. 'Today', 'In 3 days', ...)"
    nbDays = (theDate - origin).days
    if nbDays == -1:
        return 'Yesterday'
    elif nbDays == 0:
        return 'Today'
    elif nbDays == 1:
        return 'Tomorrow'
    elif nbDays >= 2 and nbDays <= 6:
        return 'in %s days' % nbDays
    elif nbDays == 7:
        return 'in 1 week'
    if theDate.year == origin.year:
        return theDate.strftime("%b %d")
    else:
        return theDate.isoformat()


def _next_date_end_of_month(year, month, day):
    year = year + (month - 1) / 12
    month = (month - 1) % 12 + 1
    range = calendar.monthrange(year, month)[1]
    if range < day:
        day = range
    return datetime.date(year, month, day)
        
def next_date(aDate, nb, repetition_type):
    if repetition_type == 'W':
        repetition_type = 'D'
        nb = 7 * nb
    if repetition_type == 'D':
        return aDate + datetime.timedelta(nb)
    elif repetition_type == 'M':
        return _next_date_end_of_month(aDate.year, aDate.month + nb, aDate.day)
    elif repetition_type == 'Y':
        return _next_date_end_of_month(aDate.year + nb, aDate.month, aDate.day)        
        
        
        
class Context(models.Model):

    title = models.CharField(max_length = 20)

    def __unicode__(self):
        return self.title
        
        
        

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
        
    def handle_title(title):
        return getText(title.childNodes)

    def handle_task(task):
        title = task.getElementsByTagName("title")[0]
        ddate = task.getElementsByTagName("duedate")[0]
        t = Task(description = handle_title(title),
                  due_date = handle_duedate(ddate))
        t.save()

    def handle_tasks(tasks):
        for t in tasks:
            handle_task(t)

    dom = parseString(the_xml)
    tasks = dom.getElementsByTagName("item")
    handle_tasks(tasks)