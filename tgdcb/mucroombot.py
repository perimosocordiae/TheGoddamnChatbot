#!/usr/bin/env python
import sys, locale, codecs
from colors import colorize,notify
from pyxmpp.streamtls import TLSSettings
from pyxmpp.jabber.muc import MucRoomManager
from pyxmpp.jabber.client import JabberClient
from pyxmpp.all import JID,SASLAuthenticationFailed

class ChatClient(JabberClient):

    def __init__(self, jid, password, nick):
        self.nick = nick
        self.jid = jid if jid.resource else JID(jid.node, jid.domain, "Robot-"+self.nick)
        tls = TLSSettings(require=True, verify_peer=False)
        JabberClient.__init__(self, self.jid, password, disco_name="chatbot", disco_type="user", tls_settings=tls, auth_methods=['sasl:PLAIN'])
        self.disco_info.add_feature("jabber:iq:version")

    def message(self,stanza):
        raise NotImplementedError('Need to override "message" callback function')

    def session_started(self):
        raise NotImplementedError('Need to override "session_started" callback function')

    def _session_started_helper(self,bot,muc_jid):
        '''Pass this an instance of your bot (that subclasses MucRoomHandler) and a MUC room JID'''
        JabberClient.session_started(self)
        self.stream.set_iq_get_handler("query","jabber:iq:version",self.get_version)
        self.stream.set_message_handler("normal",self.message)

        self.muc_manager = MucRoomManager(self.stream)
        self.muc_state = self.muc_manager.join(muc_jid,self.nick,bot,history_maxchars=0)
        self.muc_manager.set_handlers()

    def get_version(self,iq):
        iq=iq.make_result_response()
        q=iq.new_query("jabber:iq:version")
        q.newTextChild(q.ns(),"name",self.nick)
        q.newTextChild(q.ns(),"version","1.0")
        self.stream.send(iq)
        return True

    def print_roster_item(self,item):
        name = item.name if item.name else item.jid
        print '  %s (group%s: %s)' % (name, '' if len(item.groups) == 1 else 's', ','.join(item.groups))

    def roster_updated(self,item=None):
        if not item:
            print colorize('U',"My roster:")
            for item in self.roster.get_items():
                self.print_roster_item(item)
        else:
            print "Roster item updated:"
            self.print_roster_item(item)

#end class

def setup_localization():
    locale.setlocale(locale.LC_CTYPE,"")
    encoding = locale.getlocale()[1]
    if not encoding:
        encoding = "us-ascii"
    writer = codecs.getwriter(encoding)
    sys.stdout = writer(sys.stdout,errors="replace")
    sys.stderr = writer(sys.stderr,errors="replace")

def main(client_maker):
    ''' pass a function that constructs a client (subclass of ChatClient)'''
    c = client_maker()
    c.connect()
    try:
        c.loop(1)
    except SASLAuthenticationFailed:
        print notify('!','r',"Authentication failed. Try again.")
        return True
    except KeyboardInterrupt:
        print "Disconnecting..."
        c.disconnect()
    return False

