import re
import ircbot
import keywords, cmds, tasks
from time import strftime
from random import choice
from config import LOGDIR
from colors import colorize, notify
from markov import PidginLogs, MarkovChain
from os.path import expanduser, join as join_path
from pyxmpp.jabber.muc import *

def decode(string):
    r = repr(string)
    return r[r.find("'")+1:r.rfind("'")]

class GenericChatBot(object):

    def __init__(self,name,log):
        self.name = name
        self.log = log
        if log:
            self.logfile = join_path(expanduser(LOGDIR),
                              '.'.join((name,strftime("%d%b%Y_%H"),'log')))
        self.keywords = keywords.keywords
        self.commands = cmds.commands
        self.greetings = keywords.greetings
        self.respond = True
    
    def write_log(self,frm,body):
        with open(self.logfile,'a') as log:
            print >>log, '\t'.join((strftime("%H:%M:%S"),frm,body))

    def message_received(self,frm,body):
        print colorize('k',frm+':'),body
        if self.log:
            self.write_log(frm,body)

        msg = None
        cmd_match = re.match("(?:%s\s*[:,;:->]+\s*|!)(\w+)"%self.name,body)
        if cmd_match:
            cmd_name = cmd_match.group(1).lower()
            if cmd_name in self.commands:
                cmd = self.commands[cmd_name]
                try:
                    msg = cmd(self,frm,body)
                except Exception, e:
                    print notify('!','r',"Error processing command: "+cmd_name)
                    print e
        elif self.respond:
            msgs = [self.keywords[kw](frm,body) for kw in self.keywords \
                                                       if kw in body]
            if len(msgs) > 0:
                msg = choice(msgs)
        msgs = [msg]
        msgs.extend(task(self,body) for task in tasks.tasklist)
        return filter(None,msgs)

    def user_joined(self, who):
        print colorize('y',who), "joined the room"
        if self.log:
            self.write_log(who,"***joined")
        if self.respond and who != self.name:
            return choice(self.greetings) % who

#end


class MucChatBot(GenericChatBot,MucRoomHandler):

    def __init__(self, nick, log=False):
        GenericChatBot.__init__(self,nick,log)
        MucRoomHandler.__init__(self,nick)
        self.responder = MarkovChain(PidginLogs('~/.purple/logs/jabber/'))

    def message_received(self, user, stanza):
        body=stanza.get_body()
        if user is None or body is None: return
        frm = decode(user.nick)
        if frm == self.name: return
        body = body.strip().lower()
        for msg in GenericChatBot.message_received(self,frm,body):
            self.send(msg)

    def send(self,msg):
        try: print colorize('g',"me:"),msg
        except: print "me:",decode(msg)
        self.room_state.send_message(msg)

    def user_joined(self, user, stanza):
        if not user: return
        frm = decode(user.nick)
        self.send(GenericChatBot.user_joined(self,frm))

    def user_left(self, user, stanza): pass
    
    def nick_changed(self, user, old_nick, stanza):
        if decode(old_nick) == self.name:
            self.name = decode(user.nick)

class IrcChatBot(GenericChatBot,ircbot.ChatClient):

    def __init__(self, nick, log=False):
        GenericChatBot.__init__(self,nick,log)
        ircbot.ChatClient.__init__(self,nick)
        self.responder = None

    def room_msg(self,frm,msg):
        for msg in GenericChatBot.message_received(self,frm,msg):
            self.send(msg)

    def priv_msg(self,frm,msg):
        for msg in GenericChatBot.message_received(self,frm,msg):
            self.send(msg,frm)

    def join(self,frm,channel):
        self.send(GenericChatBot.user_joined(self,frm))
