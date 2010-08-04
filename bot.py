#!/usr/bin/env python
import sys
import os.path
import mucroombot
from config import *
from colors import notify
from pyxmpp.all import JID
from chatbot import ChatBot
from getpass import getpass,getuser
from pyxmpp.jabber.muc import MucRoomHandler

class Client(mucroombot.ChatClient):

    def session_started(self):
        self._session_started_helper(ChatBot('chatbot'),JID(MUC_ROOM,MUC_SERVER))

    def message(self,stanza):
        return True

#end class

if __name__ == '__main__':
    if len(sys.argv) == 1:
        nick = getuser()
        print notify('i','y',"Assuming you are "+nick)
        print notify('i','y',"If this is wrong, pass your JID as the first parameter")
    else:
        nick = sys.argv[1]
    jidname = nick+'@'+DOMAIN
    mucroombot.setup_localization()
    while mucroombot.main(lambda: Client(JID(jidname),getpass(),'chatbot')): pass

# vi: sts=4 et sw=4
