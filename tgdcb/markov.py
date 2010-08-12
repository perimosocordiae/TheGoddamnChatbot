"""Provides routines for generating different responses to incoming messages"""

# disclaimer: not my code. borrowed this from... someone

import os,re,random
from glob import glob
from datetime import datetime

class BaseResponse(object):
    """Defines the interface from which all 'response' objects must inherit"""

    def get(self,scnname,msg):
        """Get a response to an incoming instant message"""
        raise NotImplementedError


class Echo(BaseResponse):
    """Echos the incoming message back to the user"""

    @staticmethod
    def get(scnname,msg):
        return msg

class MarkovChain(BaseResponse):
    """
    Generates a response to a user message using markov chain text generation
    For this basic implementation, all previous messages sent by the user are
    used to seed the markov chain.
    """

    _precision=None

    def __init__(self, ConvoRecords, precision=2):
        """
        ConvoRecords is a list of tuples in the form of (datetime,screenname,message)
        """
        #print ConvoRecords #TODO: think about filtering on username here (r[1])
        self._buildmap(ConvoRecords, precision)
        self._precision=precision

    def _buildmap(self, records, precision):
        wordmap={}
        for r in records:
            words=r[2].lower().split()
            self._addSentenceToMap(wordmap, words, precision)
                
        self.wordmap=wordmap

    def addWords(self, words):
        if not hasattr(words,'__iter__'):
            words = words.split()
        self._addSentenceToMap(self.wordmap, words, self._precision)

    @staticmethod
    def _addSentenceToMap(wordmap, words, precision):
        words=[None,]*precision+words
        for i in xrange(0,len(words)-precision):
            wordmap.setdefault(tuple(words[i:i+precision]),[]).append(words[i+precision])
        wordmap.setdefault(tuple(words[-precision:]),[]).append(None)


    def get(self,msg):
        resp=[None,]*self._precision
        newword=random.choice(self.wordmap[tuple(resp[-self._precision:])])
        while newword:
            newword=random.choice(self.wordmap[tuple(resp[-self._precision:])])
            resp.append(newword)
        return ' '.join([w for w in resp if w])

# -------------- ----------- -------------- -------------- ------------ ---------- ----------
"""
A set of functions for retrieving previous instant message conversations.
All functions return an interable whose items are tuples in the form of:
(date/time,screenname,message)
"""

recordre=re.compile(r'^\((\d\d?\:\d\d\:\d\d(\s+[A|P]M)?)\)\s+(.*?)\:\s+(.*)\s*$', re.I|re.L)

def PidginLogs(LogDir,select_nick=None):
    """Returns all conversations by parsing Pidgin log files"""
    LogDir = os.path.expanduser(LogDir)
    while True:
        logfiles = glob(LogDir+'*.txt')
        if len(logfiles) > 0: break
        LogDir += ('*'+os.sep)
    messages = []
    for f in logfiles:
        messages.extend(parselog(f,select_nick))
    return messages

def parselog(logf,select_nick):
    doy = os.path.basename(logf).split('.')[0]
    for rec in open(logf).readlines()[1:]:
        t=_ParsePidginRecord(rec,doy)
        if t and select_nick and select_nick == t[1]:
            yield t
        #elif not _IsSystemMessage(rec):
        #    print "malformed log record '%s'"%rec
        #    raise ValueError("malformed log record '%s' in file '%s'"%(rec,logf))

def _ParsePidginRecord(recordtext,dayofyear):
    m=recordre.search(recordtext.strip())
    if not m: return
    tod,isampm,scrnname,msg=m.groups()
    if isampm:
        dtime=datetime.strptime('%s %s'%(dayofyear,tod), '%Y-%m-%d %I:%M:%S %p')    
    else:
        dtime=datetime.strptime('%s %s'%(dayofyear,tod), '%Y-%m-%d %H:%M:%S')
    return (dtime,scrnname,msg,)

_SysMsgSuffixes=[
    'has signed off.',
    'has signed on.',
    'logged out.',
    'logged in.',
    'is no longer idle.',
    'has become idle.',
    'has gone away.',
    'is no longer away.',
    'entered the room.',
    'left the room.',
    ]

def _IsSystemMessage(recordtext):
    recordtext=recordtext.strip()
    for sfx in _SysMsgSuffixes:
        if recordtext.endswith(sfx):
            return True
    return False
