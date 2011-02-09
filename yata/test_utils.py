
import datetime

        
def today():
    return datetime.date.today()
        
def tomorrow(aDate = datetime.date.today()):
    return aDate + datetime.timedelta(1)

def yesterday(aDate = datetime.date.today()):
    return aDate - datetime.timedelta(1)

def flatten(list):
    'Flatten a list of pairs (value, [items])'
    result = []
    for l in list:
        for i in l[1]:
            result.append(i)
    return result
        