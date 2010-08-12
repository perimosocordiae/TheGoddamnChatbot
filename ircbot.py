#!/usr/bin/env python
import re,sys
from config import *
from colors import colorize,notify

class ChatClient(object):

    def __init__(self, bot, nick, password=None):
        self.nick = nick
        self.bot = bot
        self.password = password

    def connect(self):
        print notify('i','m',"Connecting to %s on port %d..."%(MUC_SERVER,PORT))
        sock = self.bot.sock
        sock.connect((MUC_SERVER,PORT))
        if self.password:
            sock.send("PASS %s\r\n"%self.password)
        sock.send("NICK %s\r\n"%self.nick)
        sock.send("USER %s %s * :%s\r\n"%(self.nick,MUC_SERVER,self.nick))
        sock.send("JOIN %s\r\n"%MUC_ROOM)

    def loop(self):
        data = ''
        while True:
            data += self.bot.sock.recv(1024)
            lines = data.split("\n")
            data = lines.pop() # in case the last line was incomplete
            for l in lines:
                self._handle(l.rstrip())
    
    def disconnect(self,msg='disconnecting'):
        self.bot.sock.send("PART %s :%s\r\n"%(MUC_ROOM,msg))
        self.bot.sock.send("QUIT\r\n")

    def _handle(self,data):
        splitat = data.find(' ')
        frm,msg = data[:splitat], data[splitat+1:]
        if frm == 'PING':
            return self.bot.sock.send("PONG %s\r\n"%msg)
        frm = frm.split('!')[0][1:] # frm is originally ":nick!nick@addr"
        for regex,handler in self.bot.handlers.iteritems():
            m = regex.match(msg)
            if m:
                handler(frm,*m.groups())
                break
        else:
            print "nh>",data

#end class

def main(client_maker):
    ''' pass a function that constructs a client (subclass of ChatClient)'''
    c = client_maker()
    c.connect()
    try:
        c.loop()
    except KeyboardInterrupt:
        print "Disconnecting..."
        c.disconnect()
    except Exception, e:
        print e
        c.disconnect('Agh, YASD!')
    return False

