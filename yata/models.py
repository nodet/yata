import unittest
import datetime
import calendar
from django.db import models


class Task(models.Model):
    description = models.CharField(max_length=200)
    start_date = models.DateField(null=True,blank=True)
    due_date = models.DateField(null=True,blank=True)
    done = models.BooleanField()
    last_edited = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        if self.due_date:
            return '%s, due %s' % (self.description, self.relative_due_date())
        return self.description

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