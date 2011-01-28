
import datetime

        
def today():
    return datetime.date.today()
        
def tomorrow(aDate = datetime.date.today()):
    return aDate + datetime.timedelta(1)

def yesterday(aDate = datetime.date.today()):
    return aDate - datetime.timedelta(1)
