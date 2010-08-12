import re
from random import random
from config import BOT_NAME
from colors import colorize

def autorespond(obj,body):
    obj.responder.addWords(body)
    if (not obj.name in body) and random() < 0.95: return None
    r = obj.responder.get(body)
    rr = repr(r)
    if rr[rr.find("'")+1:rr.rfind("'")] != r: return None
    blacklist = [BOT_NAME,'!','spawn']
    if len(r.split()) < 2 or any(w in r for w in blacklist): return None
    print colorize('b',"autoresponse:"),rr
    return r

def spelling(obj,body): pass
# here there be dead code
'''
    if not hasattr(obj,'dictionary'):
        obj.dictionary = set([w.rstrip().lower() for w in open('/usr/share/dict/words').readlines()])
    misspelled = [ w for w in re.split('\W+',body) if not (w in obj.dictionary or len(w) == 0) ]
    if len(misspelled) > 0:
        print "misspellings:",misspelled
    return "Looks like you misspelled "+', '.join(misspelled)
'''

# add to this list to add tasks
tasklist = [] #[autorespond]
