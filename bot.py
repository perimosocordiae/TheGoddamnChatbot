#!/usr/bin/env python
import sys
import os.path
from config import *
from colors import notify
import mucroombot, ircbot
from pyxmpp.all import JID
from chatbot import MucChatBot,IrcChatBot
from getpass import getpass,getuser
from pyxmpp.jabber.muc import MucRoomHandler

class Client(mucroombot.ChatClient):

    def session_started(self):
        self._session_started_helper(MucChatBot(BOT_NAME),JID(MUC_ROOM,MUC_SERVER))

    def message(self,stanza):
        return True

#end class

if __name__ == '__main__':
    mucroombot.setup_localization()
    if ROOM_TYPE == 'MUC':
        if len(sys.argv) == 1:
            nick = getuser()
            print notify('i','y',"Assuming you are "+nick)
            print notify('i','y',"If this is wrong, pass your nick as the first parameter")
        else:
            nick = sys.argv[1]
        jidname = nick+'@'+DOMAIN
        while mucroombot.main(lambda: Client(JID(jidname),getpass(),BOT_NAME)): pass
    elif ROOM_TYPE == 'IRC':
        while ircbot.main(lambda: ircbot.ChatClient(IrcChatBot(BOT_NAME),BOT_NAME)): pass
        
# vi: sts=4 et sw=4
