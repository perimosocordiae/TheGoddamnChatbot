import sys
#sys.path.insert(0,'/gscuser/ccarey/chatbot/lib/python2.5/site-packages')
import re, locale, codecs, pickle
import keywords, cmds, tasks
from time import time
from os import path, system
from getpass import getpass,getuser
from random import choice,randint,shuffle
from pyxmpp.jabber.muc import *
from colors import colorize, notify
from markov import PidginLogs, MarkovChain

def decode(str):
    r = repr(str)
    return r[r.find("'")+1:r.rfind("'")]

class ChatBot(MucRoomHandler):

    def __init__(self,name):
        super(ChatBot,self).__init__()
        self.name = name
        self.keywords = keywords.keywords
        self.commands = cmds.commands
        self.respond = True
        self.responder = MarkovChain(PidginLogs('/gscuser/ccarey/.purple/logs/jabber/ccarey@chat.gsc.wustl.edu/'))
    
    def message_received(self, user, stanza):
        body=stanza.get_body()
        if user is None or body is None: return
        frm = decode(user.nick)
        if frm == self.name: return
        print colorize('k',frm+':'),body
        body = body.strip().lower()

        msg = None
        cmd_match = re.match("(?:%s\s*[:,;:->]+\s*|!)(\w+)"%self.name,body)
        if cmd_match:
            cmd_name = cmd_match.group(1).lower()
            if cmd_name in self.commands:
                cmd = self.commands[cmd_name]
                try:
                    msg = cmd(self,frm,body)
                except Exception, e:
                    print notify('!','r',"Error processing command: %s"%cmd_name)
                    print e
        elif self.respond:
            msgs = [self.keywords[kw](frm,body) for kw in self.keywords if kw in body]
            if len(msgs) > 0:
                msg = choice(msgs)

        self.send(msg)
        for task in tasks.tasklist:
            self.send(task(self,body))
            
        return True

    def send(self,msg):
        if msg:
            try: print colorize('g',"me:"),msg
            except: print "me:",decode(msg)
            self.room_state.send_message(msg)

    def user_joined(self, user, stanza): pass
        #greetings = ['Nice to see you, %s','Hey %s! Where\'s my money?','Oh... it\'s %s again',
        #             'Finally, %s! These people are so inane!','Greetings, %s!', 'What up, %s?',
        #             'Ah, my old enemy: %s', 'You come here often, %s?','G\'day, %s']
        #usr = decode(user.nick)
        #if usr != self.name:
        #    self.room_state.send_message(choice(greetings)%usr)

    def nick_changed(self, user, old_nick, stanza):
        if decode(old_nick) == self.name:
            self.name = decode(user.nick)

    def user_left(self, user, stanza): pass
        #usr = decode(user.nick)
        #if usr == self.name:
        #    msg = "Hasta la vista, babies!"
        #else:
        #    msg = "So long, and thanks for all the fish, %s."%usr
        #self.room_state.send_message(msg)

#end
