#!/usr/bin/env python
import sys,re
import os.path
import mucroombot
from config import *
from pyxmpp.all import JID
from random import choice,random
from colors import colorize,notify
from getpass import getuser,getpass
from markov import PidginLogs, MarkovChain
from pyxmpp.jabber.muc import MucRoomHandler

class MucClient(MucRoomHandler):

    def __init__(self,parent):
        super(MucClient,self).__init__()
        self.parent = parent

    def message_received(self, user, stanza):
        body=stanza.get_body()
        if user is None or body is None: return
        print user.nick+':',body
        response = self.parent.autorespond(body)
        if response:
            self.room_state.send_message(response)

#end
        
class CloneClient(mucroombot.ChatClient):

    def __init__(self, jid, password, nick):
        super(CloneClient,self).__init__(jid,password,nick)
        self.responder = MarkovChain(PidginLogs('~/.purple/logs/jabber/%s/'%jid.as_utf8(),select_nick=nick))

    def session_started(self):
        self._session_started_helper(MucClient(self),JID(MUC_ROOM,MUC_SERVER))

    def autorespond(self,body):
        if (not self.nick in body) and random() < 0.6: return None
        r = self.responder.get(body)
        rr = repr(r)
        if rr[rr.find("'")+1:rr.rfind("'")] != r or len(r.split()) < 2: return None
        return r
        
    def message(self,stanza):
        body=stanza.get_body()
        frm = stanza.get_from().as_utf8().split('@')[0]
        if stanza.get_type()=="headline": return True
        print colorize('g',frm+':'),body
        response = self.autorespond(body)
        return Message(to_jid=stanza.get_from(),
                       from_jid=stanza.get_to(),
                       stanza_type=stanza.get_type(),
                       subject=stanza.get_subject(),
                       body=response)

#end class

if len(sys.argv) != 2:
    print notify('!','r',"Usage: %s <nick_to_clone>"%sys.argv[0])
    sys.exit(1)

nick = sys.argv[1]
jidname = getuser()+'@'+DOMAIN

mucroombot.setup_localization()
while mucroombot.main(lambda: CloneClient(JID(jidname),getpass(),nick)): pass
# vi: sts=4 et sw=4

