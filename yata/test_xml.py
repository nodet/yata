from django.test import TestCase, TransactionTestCase
from yata.models import Task, Context
from yata.test_models import YataTestCase
from yata.xml_io import create_tasks_from_xml, create_xml_from_tasks
import datetime
import re



class YataXmlTestCase(YataTestCase):

    def create_tasks_from_xml(self, the_xml):
        return create_tasks_from_xml(self.user, the_xml)


        
class XmlImportTest(YataXmlTestCase):

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
<repeat>Every 1 week</repeat>
</item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        self.assertEqual(1, Task.objects.all().count())
        t = Task.objects.all()[0]
        self.assertEqual('Change password', t.description)
        self.assertEqual(datetime.date(2011,02,01), t.start_date)
        self.assertEqual(datetime.date(2011,03,28), t.due_date)
        self.assertEqual('C2', t.context.title)
        self.assertFalse(re.match(r'Django\nPython', t.note) is None)
        self.assertEqual(1, t.repeat_nb)
        self.assertEqual('W', t.repeat_type)
        
    def test_import_two_tasks(self):
        the_xml = """
<xml>
<item><title>T1</title></item>
<item><title>T2</title></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        self.assertEqual(2, Task.objects.all().count())
        
    def test_import_missing_title(self):
        the_xml = """
<xml>
<item></item>
</xml>
"""
        seen_exception = False
        try:
            self.create_tasks_from_xml(the_xml)
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
        self.create_tasks_from_xml(the_xml)
        self.assertEqual(1, Context.objects.all().count())

    def test_import_two_tasks_one_done(self):
        the_xml = """
<xml>
<item><title>T1</title><completed>0000-00-00</completed></item>
<item><title>T2</title><completed>2011-12-31</completed></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
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
        self.create_tasks_from_xml(the_xml)
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
        self.create_tasks_from_xml(the_xml)
        self.assertEqual(1, Task.objects.all().count())
    
    def test_import_empty_context(self):
        the_xml = """
<xml>
<item><title>T1</title><context></context></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        self.assertEqual(0, Context.objects.all().count())
    
    def test_no_repeated_field(self):
        the_xml = """
<xml>
<item><title>T1</title><title>T2</title></item>
</xml>
"""
        seen_exception = False
        try:
            self.create_tasks_from_xml(the_xml)
        except:
            seen_exception = True
        self.assertTrue(seen_exception)
        self.assertEqual(0, Task.objects.all().count())
    
    def test_repeat_yearly(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Yearly</repeat></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(1, t.repeat_nb)
        self.assertEqual('Y', t.repeat_type)
        
    def test_repeat_quaterly(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Quaterly</repeat></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(3, t.repeat_nb)
        self.assertEqual('M', t.repeat_type)
        
    def test_repeat_monthly(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Monthly</repeat></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(1, t.repeat_nb)
        self.assertEqual('M', t.repeat_type)
        
    def test_repeat_biweekly(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Biweekly</repeat></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(2, t.repeat_nb)
        self.assertEqual('W', t.repeat_type)
        
    def test_repeat_weekly(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Weekly</repeat></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(1, t.repeat_nb)
        self.assertEqual('W', t.repeat_type)
        self.assertFalse(t.repeat_from_due_date)
        
    def test_repeat_from_due_date(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Weekly</repeat><repeat_from_due_date>Yes</repeat_from_due_date></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(1, t.repeat_nb)
        self.assertEqual('W', t.repeat_type)
        self.assertTrue(t.repeat_from_due_date)
        
    def test_xml_can_have_shortened_repeat_from_due_date(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Weekly</repeat><repeat_from_due_date /></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(1, t.repeat_nb)
        self.assertEqual('W', t.repeat_type)
        self.assertTrue(t.repeat_from_due_date)
        
    def test_repeat_from_due_date_can_be_No(self):
        the_xml = """
<xml>
<item><title>T1</title><repeat>Weekly</repeat><repeat_from_due_date>No</repeat_from_due_date></item>
</xml>
"""
        self.create_tasks_from_xml(the_xml)
        all = Task.objects.all()
        self.assertEqual(1, all.count())
        t = all[0]
        self.assertEqual(1, t.repeat_nb)
        self.assertEqual('W', t.repeat_type)
        self.assertFalse(t.repeat_from_due_date)
        
        
        
class XMLTransactions(TransactionTestCase):        
    def test_import_rollback_if_error(self):
        the_xml = """
<xml>
<item><title>T1</title></item>
<item><title>T2</title><duedate>11-11-11</duedate></item>
</xml>
"""
        try:
            self.create_tasks_from_xml(the_xml)
        except:
            pass
        self.assertEqual(0, Task.objects.all().count())
                
                
                

                
class XmlExportTest(YataXmlTestCase):
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
<repeat>Every 1 week</repeat>
<repeat_from_due_date>Yes</repeat_from_due_date>
</item>
</xml>"""
        c = self.new_context(title = 'C2')
        t = self.new_task(
            description = 't1',
            priority = 3,
            start_date = datetime.date(2011,2,1),
            due_date = datetime.date(2011,3,28),
            context = c,
            note = 'Django\nPython',
            repeat_nb = 1,
            repeat_type = 'W',
            repeat_from_due_date = True
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)

    def test_export_not_much_info(self):
        the_xml = """<xml>
<item>
<title>t1</title>
</item>
</xml>"""
        t = self.new_task(
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
        out = create_xml_from_tasks(self.create_tasks_from_xml(the_xml))
        self.assertEqual(the_xml, out)
        
        
    def test_export_done(self):
        the_xml = """<xml>
<item>
<title>t1</title>
<completed>1111-11-11</completed>
</item>
</xml>"""
        t = self.new_task(
            description = 't1',
            done = True
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)
        
    def test_export_repeat_day(self):
        the_xml = """<xml>
<item>
<title>t1</title>
<repeat>Every 2 days</repeat>
</item>
</xml>"""
        t = self.new_task(
            description = 't1',
            repeat_nb = 2,
            repeat_type = 'D'
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)
        
    def test_export_repeat_week(self):
        the_xml = """<xml>
<item>
<title>t1</title>
<repeat>Every 2 weeks</repeat>
</item>
</xml>"""
        t = self.new_task(
            description = 't1',
            repeat_nb = 2,
            repeat_type = 'W'
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)
        
    def test_export_repeat_month(self):
        the_xml = """<xml>
<item>
<title>t1</title>
<repeat>Every 3 months</repeat>
</item>
</xml>"""
        t = self.new_task(
            description = 't1',
            repeat_nb = 3,
            repeat_type = 'M'
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)
        
    def test_export_repeat_year(self):
        the_xml = """<xml>
<item>
<title>t1</title>
<repeat>Every 1 year</repeat>
</item>
</xml>"""
        t = self.new_task(
            description = 't1',
            repeat_nb = 1,
            repeat_type = 'Y'
        )
        s = create_xml_from_tasks([t])
        self.assertEqual(the_xml, s)
