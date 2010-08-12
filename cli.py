#!/usr/bin/env python
import tty,termios
import sys, os.path
from random import choice
from select import select
from tgdcb.config import *
from tgdcb import mucroombot
from getpass import getpass,getuser
from tgdcb.colors import colorize,notify
from pyxmpp.jabber.muc import MucRoomHandler
from pyxmpp.all import JID,SASLAuthenticationFailed

class MucClient(MucRoomHandler):

    def __init__(self):
        super(MucClient,self).__init__()
        self.nicks = {}
        self.pool = set("cbdgmry")

    def message_received(self, user, stanza):
        body=stanza.get_body()
        if user is None or body is None: return
        frm = user.nick#.decode("utf-8")
        code = self.nicks[frm] if frm in self.nicks else 'U'
        try:
            print colorize(code,frm+':'),body
        except:
            print frm+':',body
        sys.stdout.write("\x1b]2;%s says...\x07"%frm)

    def user_joined(self, user, stanza):
        frm = user.nick#.decode("utf-8")
        if len(self.pool) == 0:
            self.pool = set("cbdgmry") # reset
        self.nicks[frm] = self.pool.pop()
        print colorize(self.nicks[frm],frm),colorize('k',"has joined the room")

    def user_left(self, user, stanza):
        frm = user.nick#.decode("utf-8")
        print colorize(self.nicks[frm],frm),colorize('k',"has left the room")
        self.pool.add(self.nicks[frm])
        del self.nicks[frm]

    def nick_changed(self, user, old_nick, stanza):
        frm = user.nick#.decode("utf-8")
        self.nicks[frm] = self.nicks[old_nick]
        del self.nicks[old_nick]
        print colorize(self.nicks[frm],old_nick),colorize('k',"is now known as"),colorize(self.nicks[frm],frm)
#end
        
class CLIClient(mucroombot.ChatClient):

    def __init__(self, jid, password,nick):
        super(CLIClient,self).__init__(jid,password,nick)
        self.history = ['']
        self.msg_idx = 0

    def got_char(self,c):
        '''Note: doesn't actually work'''
        print "got char:",c
        if len(self.history[self.msg_idx]) == 0:
            if not c in ['\x0d','\x26']:
                self.history[self.msg_idx] += c
        elif c == '\x0d': # enter key
            print "sending:",self.history[self.msg_idx]
            self.muc_state.send_message(self.history[self.msg_idx])
            self.history.insert(0,'')
            self.msg_idx = 0
        elif c == '\x26': # up arrow
            if self.msg_idx < len(self.history)-1:
                self.msg_idx += 1
        elif c == '\x28': # down arrow
            if self.msg_idx > 0:
                self.msg_idx -= 1
        else:
            self.history[self.msg_idx] += c

    def session_started(self):
        self._session_started_helper(MucClient(),JID(ROOM,SERVER))

    def message(self,stanza):
        body=stanza.get_body()
        frm = stanza.get_from().as_utf8().split('@')[0]
        if stanza.get_type()=="headline": return True
        print colorize('g',frm+':'),body
        return True
#end class

mucroombot.setup_localization()

# set terminal to character mode
old_settings = termios.tcgetattr(sys.stdin)
#tty.setcbreak(sys.stdin.fileno())

def loop(c):
    while True:
        stream = c.get_stream()
        if not stream: break
        act = stream.loop_iter(0.5)
        if not act: 
            rr,_,_ = select([sys.stdin],[],[],0)
            if len(rr) == 0:
                c.idle()
            else:
                print "\r", # carriage return
                c.muc_state.send_message(rr[0].readline().rstrip())
                #c.got_char(rr[0].read(1))


if len(sys.argv) == 1:
    nick = getuser()
    print notify('!','y',"Assuming you are %s\nIf this is wrong, pass your nick as the first parameter"%nick)
else:
    nick = sys.argv[1]

if ROOM_TYPE == 'MUC':
    jidname = nick+'@'+DOMAIN
else:
    sys.exit(notify('!','r',"%s is not supported yet"%ROOM_TYPE))

while True:
    c = CLIClient(JID(jidname),getpass(),nick)
    print "Connecting..."
    c.connect()

    try:
        loop(c)
    except SASLAuthenticationFailed:
        print "Authentication failed. Try again."
    except KeyboardInterrupt:
        print "Disconnecting..."
        c.disconnect()
        break
    finally:
        termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old_settings)
termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old_settings)
# vi: sts=4 et sw=4
