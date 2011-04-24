from yata.models import Task
from django.db import connection, transaction

#
# pm shell
# from yata import update_db
# update_db.addLastEditedColumn()
#


#
# It would be nice that these scripts do not change the
# last_edited timestamp...
#

def runQueryAndSaveAll(query):
    cursor = connection.cursor()
    cursor.execute(query)
    for t in Task.objects.all():
        t.save()
        
      
def addLastEditedColumn():
    runQueryAndSaveAll('alter table "yata_task" add column "last_edited" datetime')

def addStartDateColumn():
    runQueryAndSaveAll('alter table "yata_task" add column "start_date" date')
    
def addRepeatColumns():
    #runQueryAndSaveAll('alter table "yata_task" add column "repeat_nb" integer unsigned')
    runQueryAndSaveAll('alter table "yata_task" add column "repeat_type" varchar(1)')

def addContextColumn():
    runQueryAndSaveAll('alter table "yata_task" add column "context_id" integer')
    
def addNoteColumn():
    runQueryAndSaveAll('alter table "yata_task" add column "note" text')
    
def addPrioColumn():
    #runQueryAndSaveAll('alter table "yata_task" add column "priority" integer')
    runQueryAndSaveAll('alter table "yata_task" modify column "priority" smallint NOT NULL')

def addRepeatFromDDColumn():
    runQueryAndSaveAll('alter table "yata_task" add column "repeat_from_due_date" boolean NOT NULL default 0')
    
    
    