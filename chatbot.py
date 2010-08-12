from config import *
from time import time
from os import path, system
import keywords, cmds, tasks
from pyxmpp.jabber.muc import *
from getpass import getpass,getuser
from colors import colorize, notify
import re, locale, codecs, pickle, socket
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

        self.send(msg)
        for task in tasks.tasklist:
            self.send(task(self,body))
        return True

    def send(self,msg):
        raise NotImplementedError('Need to override "send" function from GenericChatBot')
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
        return GenericChatBot.message_received(self,frm,body)

    def send(self,msg):
        if msg:
            try: print colorize('g',"me:"),msg
            except: print "me:",decode(msg)
            self.room_state.send_message(msg)

    def user_joined(self, user, stanza): pass
#        greetings = [
#'Nice to see you, %s','Hey %s! Where\'s my money?','Oh... it\'s %s again',
#'Finally, %s! These people are so inane!','Greetings, %s!', 'What up, %s?',
#'Ah, my old enemy: %s', 'You come here often, %s?','G\'day, %s']
#        usr = decode(user.nick)
#        if usr != self.name:
#            self.send(choice(greetings)%usr)

    def nick_changed(self, user, old_nick, stanza):
        if decode(old_nick) == self.name:
            self.name = decode(user.nick)

    def user_left(self, user, stanza): pass
#        usr = decode(user.nick)
#        if usr == self.name:
#            msg = "Hasta la vista, babies!"
#        else:
#            msg = "So long, and thanks for all the fish, %s."%usr
#        self.send(msg)
#end

class IrcChatBot(GenericChatBot):

    def __init__(self, nick):
        super(IrcChatBot,self).__init__(nick)
        self.sock = socket.socket()
        self.responder = None # MarkovChain(PidginLogs('~/.purple/logs/irc/'))
        self.handlers = {
            re.compile("PRIVMSG\s+%s\s+:(.*)"%MUC_ROOM) : self.room_msg,
            re.compile("JOIN\s+:(.*)") : self.join,
            re.compile("PART\s+(.*)") : self.part,
            re.compile("QUIT\s+:(.*)") : self.quit,
            re.compile("MODE\s+(\S+)\s+:(.*)") : self.mode,
            re.compile("NOTICE\s+(\S+)\s+:(.*)") : self.notice,
            re.compile("(\d+)\s+(.+?)\s+:(.*)") : self.numeric,
            re.compile("PRIVMSG\s+%s\s+:(.*)"%nick) : self.priv_msg,
        }

    def send(self,msg,nick=MUC_ROOM):
        if not msg: return
        for line in msg.split("\n"):
            self.sock.send("PRIVMSG %s :%s\r\n"%(nick,line))

##### Handlers #######

    def room_msg(self,frm,msg):
        return GenericChatBot.message_received(self,frm,msg)

    def priv_msg(self,frm,msg):
        print frm,"> me:",msg

    def notice(self,frm,to,msg):
        print notify('i','m',"Notice to %s: %s"%(to,msg))

    def numeric(self,frm,nums,data,msg):
        print ">>>",msg

    def join(self,frm,channel):
        print notify('i','m',frm+' joined '+channel)

    def part(self,frm,channel):
        print notify('i','m',frm+' left '+channel)

    def quit(self,frm,msg):
        print notify('i','m',frm+' '+msg)

    def mode(self,frm,usr,msg):
        print notify('i','m',"%s sets mode: %s"%(usr,msg))

#end class

