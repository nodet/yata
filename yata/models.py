import unittest
import datetime
from django.db import models


class Task(models.Model):
    description = models.CharField(max_length=200)
    due_date = models.DateField(null=True,blank=True)
    done = models.BooleanField()
    
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
        return 'In %s days' % nbDays
    elif nbDays == 7:
        return 'In 1 week'
    if theDate.year == origin.year:
        return theDate.strftime("%b %d")
    else:
        return theDate.isoformat()

        
