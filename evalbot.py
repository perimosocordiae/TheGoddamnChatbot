#!/usr/bin/env python
import sys,re,subprocess
from tgdcb.config import *
from pyxmpp.all import JID
from getpass import getuser,getpass
from tgdcb import mucroombot,ircbot
from tgdcb.colors import colorize,notify
from pyxmpp.jabber.muc import MucRoomHandler

class EvalRoomHandler(MucRoomHandler):
    def message_received(self, user, stanza):
        body=stanza.get_body()
        if user is None or body is None: return
        print user.nick+':',body
        response = evalmsg(body)
        if response:
            self.room_state.send_message(response)

class MucEvalClient(mucroombot.ChatClient):

    def session_started(self):
        self._session_started_helper(EvalRoomHandler(),JID(ROOM,SERVER))

    def message(self,stanza):
        body=stanza.get_body()
        frm = stanza.get_from().as_utf8().split('@')[0]
        if stanza.get_type()=="headline": return True
        print colorize('g',frm+':'),body
        response = evalmsg(body)
        return Message(to_jid=stanza.get_from(),
                       from_jid=stanza.get_to(),
                       stanza_type=stanza.get_type(),
                       subject=stanza.get_subject(),
                       body=response)

class IrcEvalClient(ircbot.ChatClient):
    def room_msg(self,frm,msg):
        self.send(evalmsg(msg))
    def priv_msg(self,frm,msg):
        self.send(evalmsg(msg),frm)
#end class

if len(sys.argv) != 2:
    print notify('!','r',"Usage: %s <language>"%sys.argv[0])
    sys.exit(1)

print notify('!','y',"WARNING: this evalbot is NOT SECURE. Arbitrary code \
*will* be executed!")
lang = sys.argv[1]
BOT_NAME = lang+'_bot'

def runpipe(exe,input_str):
    p = subprocess.Popen(exe,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,shell=True)
    return p.communicate(input_str)[0].rstrip()

def evalmsg(msg):
    m = re.match("%s(?:_bot)?[>:\-,]\s+(.+)"%lang,msg)
    if not m: return
    to_eval = m.group(1).encode('ascii','ignore')
    try:
        if lang == 'python':
            return str(eval(to_eval))
        elif lang == 'perl':
            to_eval = to_eval.replace('/','\/').replace('`','')
            return runpipe('perl','print (%s),"\\n"'%to_eval)
        elif lang == 'ruby':
            to_eval = to_eval.replace('/','\/').replace('`','')
            return runpipe('ruby','puts (%s)'%to_eval)
        elif lang == 'haskell':
            return runpipe('ghci -v0',to_eval)
            
        return "%s(%s)"%(lang,to_eval)
    except Exception, e:
        return str(e)

mucroombot.setup_localization()
if ROOM_TYPE == 'MUC':
    jidname = getuser()+'@'+DOMAIN
    mk_client = lambda: MucEvalClient(JID(jidname),getpass(),BOT_NAME)
    while mucroombot.main(mk_client): pass
elif ROOM_TYPE == 'IRC':
    mk_client = lambda: IrcEvalClient(BOT_NAME)
    while ircbot.main(mk_client): pass
# vi: sts=4 et sw=4

