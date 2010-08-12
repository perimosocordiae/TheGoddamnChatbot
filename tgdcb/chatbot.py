import ircbot
from config import *
from time import time
from os import path, system
import keywords, cmds, tasks
from pyxmpp.jabber.muc import *
from getpass import getpass,getuser
from colors import colorize, notify
import re, locale, codecs, pickle
from random import choice,randint,shuffle
from markov import PidginLogs, MarkovChain

def decode(str):
    r = repr(str)
    return r[r.find("'")+1:r.rfind("'")]

class GenericChatBot(object):

    def __init__(self,name):
        self.name = name
        self.keywords = keywords.keywords
        self.commands = cmds.commands
        self.respond = True
    
    def message_received(self,frm,body):
        print colorize('k',frm+':'),body

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

        msgs = [msg]
        msgs.extend(task(self,body) for task in tasks.tasklist)
        return filter(None,msgs)
#end

class MucChatBot(GenericChatBot,MucRoomHandler):

    def __init__(self, nick):
        super(MucChatBot,self).__init__(nick)
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

    def user_joined(self, user, stanza): pass
    def user_left(self, user, stanza): pass
    
    def nick_changed(self, user, old_nick, stanza):
        if decode(old_nick) == self.name:
            self.name = decode(user.nick)

class IrcChatBot(GenericChatBot,ircbot.ChatClient):

    def __init__(self):
        GenericChatBot.__init__(self,BOT_NAME)
        ircbot.ChatClient.__init__(self,BOT_NAME)
        self.responder = None # MarkovChain(PidginLogs('~/.purple/logs/irc/'))

    def room_msg(self,frm,msg):
        for msg in GenericChatBot.message_received(self,frm,msg):
            self.send(msg)

    def priv_msg(self,frm,msg):
        for msg in GenericChatBot.message_received(self,frm,msg):
            self.send(msg,frm)

