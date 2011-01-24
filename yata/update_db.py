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
    
