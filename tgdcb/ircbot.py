#!/usr/bin/env python
import re,sys,socket
from config import *
from colors import colorize,notify

class ChatClient(object):

    def __init__(self, nick, password=None):
        self.nick = nick
        self.password = password
        self.sock = socket.socket()
        self.handlers = {
            re.compile("PRIVMSG\s+%s\s+:(.*)"%ROOM) : self.room_msg,
            re.compile("JOIN\s+:(.*)") : self.join,
            re.compile("PART\s+(.*)") : self.part,
            re.compile("QUIT\s+:(.*)") : self.quit,
            re.compile("MODE\s+(\S+)\s+:(.*)") : self.mode,
            re.compile("NOTICE\s+(\S+)\s+:(.*)") : self.notice,
            re.compile("(\d+)\s+(.+?)\s+:(.*)") : self.numeric,
            re.compile("PRIVMSG\s+%s\s+:(.*)"%nick) : self.priv_msg,
        }

    def send(self,msg,nick=ROOM):
        if not msg: return
        for line in (x for x in msg.split("\n") if len(x) > 0):
            self.sock.send("PRIVMSG %s :%s\r\n"%(nick,line))

    ##### Handlers (override these) #######

    def room_msg(self,frm,msg):
        print frm,"> room:",msg

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

    def connect(self):
        print notify('i','m',"Connecting to %s on port %d..."%(SERVER,PORT))
        sock = self.sock
        sock.connect((SERVER,PORT))
        if self.password:
            sock.send("PASS %s\r\n"%self.password)
        sock.send("NICK %s\r\n"%self.nick)
        sock.send("USER %s %s * :%s\r\n"%(self.nick,SERVER,self.nick))
        sock.send("JOIN %s\r\n"%ROOM)

    def loop(self):
        data = ''
        while True:
            data += self.sock.recv(1024)
            lines = data.split("\n")
            data = lines.pop() # in case the last line was incomplete
            for l in lines:
                self._handle(l.rstrip())
    
    def disconnect(self,msg='disconnecting'):
        self.sock.send("PART %s :%s\r\n"%(ROOM,msg))
        self.sock.send("QUIT\r\n")

    def _handle(self,data):
        splitat = data.find(' ')
        frm,msg = data[:splitat], data[splitat+1:]
        if frm == 'PING':
            return self.sock.send("PONG %s\r\n"%msg)
        frm = frm.split('!')[0][1:] # frm is originally ":nick!nick@addr"
        for regex,handler in self.handlers.iteritems():
            m = regex.match(msg)
            if m:
                handler(frm,*m.groups())
                break
        else:
            print "nh>",data

#end class

def main(client_maker):
    ''' pass a function that constructs a client (subclass of ircbot.ChatClient)'''
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

