from django.test import TestCase, TransactionTestCase
from yata.models import Task, Context
from yata.xml_io import create_tasks_from_xml, create_xml_from_tasks
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
        seen_exception = False
        try:
            create_tasks_from_xml(the_xml)
        except:
            seen_exception = True
        self.assertTrue(seen_exception)
        self.assertEqual(0, Task.objects.all().count())

        
    def test_import_two_tasks_with_same_context(self):
        the_xml = """
<xml>
<item><title>T1</title><context>C1</context></item>
<item><title>T2</title><context>C1</context></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(1, Context.objects.all().count())

    def test_import_two_tasks_one_done(self):
        the_xml = """
<xml>
<item><title>T1</title><completed>0000-00-00</completed></item>
<item><title>T2</title><completed>2011-12-31</completed></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        not_done = Task.objects.filter(done=False)
        self.assertEqual(1, not_done.count())
        self.assertEqual('T1', not_done[0].description)
        
        
    def test_import_prios(self):
        the_xml = """
<xml>
<item><title>T1</title><priority>Top</priority></item>
<item><title>T2</title><priority>High</priority></item>
<item><title>T3</title><priority>Medium</priority></item>
<item><title>T4</title><priority>Low</priority></item>
<item><title>T5</title><priority>Negative</priority></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        not_done = Task.objects.filter(done=False)
        self.assertEqual(5, not_done.count())
        self.assertEqual( 3, Task.objects.get(description__exact='T1').priority)
        self.assertEqual( 2, Task.objects.get(description__exact='T2').priority)
        self.assertEqual( 1, Task.objects.get(description__exact='T3').priority)
        self.assertEqual( 0, Task.objects.get(description__exact='T4').priority)
        self.assertEqual(-1, Task.objects.get(description__exact='T5').priority)
    
    def test_import_empty_due_date(self):
        the_xml = """
<xml>
<item><title>T1</title><duedate></duedate></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(1, Task.objects.all().count())
    
    def test_import_empty_context(self):
        the_xml = """
<xml>
<item><title>T1</title><context></context></item>
</xml>
"""
        create_tasks_from_xml(the_xml)
        self.assertEqual(0, Context.objects.all().count())
    
    def test_no_repeated_field(self):
        the_xml = """
<xml>
<item><title>T1</title><title>T2</title></item>
</xml>
"""
        seen_exception = False
        try:
            create_tasks_from_xml(the_xml)
        except:
            seen_exception = True
        self.assertTrue(seen_exception)
        self.assertEqual(0, Task.objects.all().count())
    
        
        
        
        
        
        
        
class XMLTransactions(TransactionTestCase):        
    def test_import_rollback_if_error(self):
        the_xml = """
<xml>
<item><title>T1</title></item>
<item><title>T2</title><duedate>11-11-11</duedate></item>
</xml>
"""
        try:
            create_tasks_from_xml(the_xml)
        except:
            pass
        self.assertEqual(0, Task.objects.all().count())
                
                
                

                
class XmlExportTest(TestCase):
    def test_export_empty(self):
        the_xml = """<xml>
</xml>"""
        s = create_xml_from_tasks([])
        self.assertEqual(the_xml, s)


    def test_export_one_task(self):
        the_xml = """<xml>
<item>
<title>t1</title>
<priority>Top</priority>
<startdate>2011-02-01</startdate>
<duedate>2011-03-28</duedate>
<context>C2</context>
<note>Django
Python</note>
</item>
</xml>"""
        c = Context(title = 'C2')
        t = Task(
            description = 't1',
            priority = 3,
            start_date = datetime.date(2011,2,1),
            due_date = datetime.date(2011,3,28),
            context = c,
            note = 'Django\nPython'
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)

    def test_export_not_much_info(self):
        the_xml = """<xml>
<item>
<title>t1</title>
</item>
</xml>"""
        t = Task(
            description = 't1',
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)
        
    def test_xml_round_trip(self):
        the_xml = """<xml>
<item>
<title>Change password</title>
<priority>Top</priority>
<startdate>2011-02-01</startdate>
<duedate>2011-03-28</duedate>
<context>C2</context>
<note>Django
Python</note>
</item>
</xml>"""
        out = create_xml_from_tasks(create_tasks_from_xml(the_xml))
        self.assertEqual(the_xml, out)
        
        
    def test_export_done(self):
        the_xml = """<xml>
<item>
<title>t1</title>
<completed>1111-11-11</completed>
</item>
</xml>"""
        t = Task(
            description = 't1',
            done = True
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)
        