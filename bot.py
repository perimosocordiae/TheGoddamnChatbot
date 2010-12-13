#!/usr/bin/env python
"""bot.py - Primary script for running the chatbot"""
import sys
import os.path
from tgdcb import mucroombot, ircbot
from getpass import getpass,getuser
from optparse import OptionParser
from pyxmpp.all import JID
from tgdcb.colors import notify
from tgdcb.config import BOT_NAME,ROOM,SERVER,ROOM_TYPE
from tgdcb.chatbot import MucChatBot,IrcChatBot
from pyxmpp.jabber.muc import MucRoomHandler

class MucClient(mucroombot.ChatClient):
    def session_started(self): 
        self._session_started_helper(MucChatBot(BOT_NAME),JID(ROOM,SERVER))
    def message(self,stanza):
        return True

def parse_args():
    op = OptionParser(description=__doc__)

    if ROOM_TYPE == 'MUC':
        if not 'DOMAIN' in globals() or not DOMAIN:
            op.error("Must supply a domain, edit 'config' to set up")
        op.add_option('-u', '--username', default=getuser(),
                        help='default='+getuser())
    op.add_option('-l', '--log', action='store_true', help='turn on logging')
    op.add_option('-n', '--nick', default=BOT_NAME, 
                    help='bot nickname, default='+BOT_NAME)
    opts, args = op.parse_args()
    return opts

def main_muc(opts):
    jid = JID(opts.username+'@'+DOMAIN)
    mkbot = lambda: MucClient(jid, getpass(), opts.nick, opts.log)
    while mucroombot.main(mkbot): pass

def main_irc(opts):
    mkbot = lambda: IrcChatBot(opts.nick, log=opts.log)
    while ircbot.main(mkbot): pass

if __name__ == '__main__':
    mucroombot.setup_localization()
    opts = parse_args()
    if ROOM_TYPE == 'MUC':
        main_muc(opts)
    elif ROOM_TYPE == 'IRC':
        main_irc(opts)
    else:
        print notify('!','r',"Invalid ROOM_TYPE: '%s'"%ROOM_TYPE)
        
# vi: sts=4 et sw=4
