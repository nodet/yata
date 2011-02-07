from django.test import TestCase
from yata.models import Task, Context
from yata.xml_io import create_tasks_from_xml
import datetime
import re

        
class XmlImportTest(TestCase):
    def test_import_one_task(self):
        the_xml = """
<xml>
<item>
<title>Change password</title>
<startdate>2011-02-01</startdate>
<duedate>2011-03-28</duedate>
<context>C2</context>
<note>Django
Python</note>        
</item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(1, Task.objects.all().count())
        t = Task.objects.all()[0]
        self.assertEqual('Change password', t.description)
        self.assertEqual(datetime.date(2011,02,01), t.start_date)
        self.assertEqual(datetime.date(2011,03,28), t.due_date)
        self.assertEqual('C2', t.context.title)
        self.assertFalse(re.match(r'Django\nPython', t.note) is None) 
        
    def test_import_two_tasks(self):
        the_xml = """
<xml>
<item><title>T1</title></item>
<item><title>T2</title></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(2, Task.objects.all().count())
        
    def test_import_missing_title(self):
        the_xml = """
<xml>
<item></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(1, Task.objects.all().count())
        t = Task.objects.all()[0]
        self.assertEqual('[No title]', t.description)
        
    def test_import_two_tasks_with_same_context(self):
        the_xml = """
<xml>
<item><title>T1</title><context>C1</context></item>
<item><title>T2</title><context>C1</context></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(1, Context.objects.all().count())
        