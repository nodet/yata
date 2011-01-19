from django.db import models
import unittest

# Create your models here.

class Task(models.Model):
    description = models.CharField(max_length=200)
    due_date = models.DateField(null=True)
    
    def __unicode__(self):
        return self.description

