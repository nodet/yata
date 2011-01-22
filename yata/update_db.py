from yata.models import Task
from django.db import connection, transaction

#
# pm shell
# from yata import update_db
# update_db.addLastEditedColumn()
#
        
def addLastEditedColumn():
    cursor = connection.cursor()
    cursor.execute('alter table "yata_task" add column "last_edited"')
    for t in Task.objects.all():
        t.save()
        
