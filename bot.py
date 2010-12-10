#!/usr/bin/env python
import sys
import os.path
from tgdcb.config import BOT_NAME,ROOM,SERVER,DOMAIN,ROOM_TYPE
from pyxmpp.all import JID
from tgdcb.colors import notify
from getpass import getpass,getuser
from tgdcb import mucroombot, ircbot
from pyxmpp.jabber.muc import MucRoomHandler
from tgdcb.chatbot import MucChatBot,IrcChatBot

class MucClient(mucroombot.ChatClient):
    def session_started(self):
        self._session_started_helper(MucChatBot(BOT_NAME),JID(ROOM,SERVER))
    def message(self,stanza):
        return True

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
        while mucroombot.main(lambda: MucClient(JID(jidname),getpass(),BOT_NAME)): pass
    elif ROOM_TYPE == 'IRC':
        while ircbot.main(IrcChatBot): pass
        
# vi: sts=4 et sw=4
