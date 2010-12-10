#!/usr/bin/env python
import re
import os.path
from sys import argv, exit
from time import sleep
from tgdcb.config import *
from pyxmpp.all import JID
from urllib2 import urlopen
from tgdcb import mucroombot
from random import choice,random
from getpass import getuser,getpass
from tgdcb.markov import MarkovChain
from BeautifulSoup import BeautifulSoup
from tgdcb.colors import colorize,notify
from pyxmpp.jabber.muc import MucRoomHandler

class MucClient(MucRoomHandler):

    def __init__(self,parent):
        super(MucClient,self).__init__()
        self.parent = parent

    def message_received(self, user, stanza):
        body=stanza.get_body()
        if user is None or body is None: return
        print user.nick+':',body
        response = self.parent.autorespond(body,rate=0.1)
        if response:
            sleep(random())
            self.room_state.send_message(response)

#end

# return list of lines in (dtime,nick,body) form
def parse_shakespeare(pages,character=None):
    lines = []
    for page in pages:
        soup = BeautifulSoup(page)
        for e in (a for a in soup('a') if a.has_key('name')):
            if e.b:
                lines.append(['0',e.b.text,'']) # first elem is a fake datetime
            elif len(lines) > 0:
                lines[-1][2] += ' '+e.text
    if character:
        lines = filter(lambda l: l[1].lower() == character.lower(), lines)
    assert len(lines) > 0
    return lines

class ShakespeareClient(mucroombot.ChatClient):

    def __init__(self, jid, password, pages, character):
        super(ShakespeareClient,self).__init__(jid,password,character)
        self.responder = MarkovChain(parse_shakespeare(pages,self.nick if self.nick != 'will' else None))

    def session_started(self):
        self._session_started_helper(MucClient(self),JID(ROOM,SERVER))

    def autorespond(self,body,rate=0.2):
        if random() > rate: return None
        return self.responder.get(body)
        
    def message(self,stanza):
        body=stanza.get_body()
        frm = stanza.get_from().as_utf8().split('@')[0]
        print stanza.get_type()
        if stanza.get_type()=="headline": return True
        print colorize('g',frm+':'),body
        sleep(random())
        response = self.autorespond(body,1.0)
        return Message(to_jid=stanza.get_from(),
                       from_jid=stanza.get_to(),
                       stanza_type=stanza.get_type(),
                       subject=stanza.get_subject(),
                       body=response)

#end class

def main():
    if len(argv) < 3:
        print notify('!','r',"Usage: %s <name> <shakespeare_play(s)>"%argv[0])
        print notify('i','y',"<name> - character name, 'will' for all chars")
        print notify('i','y',"<play(s)> - 1+ plays (on shakespeare.mit.edu)")
        exit(1)
    if not DOMAIN or ROOM_TYPE != 'MUC':
        print notify('!','r',"Error: Only MUC rooms are supported")
        exit(2)
    # use 'will' to grab all characters
    nick = argv[1]
    pages = (urlopen('http://shakespeare.mit.edu/%s/full.html'%play.lower()) \
                for play in argv[2:])
    jidname = getuser()+'@'+DOMAIN
    mucroombot.setup_localization()
    mk_bot = lambda: ShakespeareClient(JID(jidname),getpass(),pages,nick)
    while mucroombot.main(mk_bot): pass

if __name__ == '__main__':
    main()
# vi: sts=4 et sw=4
