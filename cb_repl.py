#!/usr/bin/env python

import readline
from tgdcb.cmds import commands
from getpass import getuser

uname = getuser()
print """Enter a command at the prompt
    TAB complete to find commands
    Ctrl-C or Ctrl-D (EOF) to quit
    Note that not all commands will work outside of chat"""

def complete(text, state):
    for cmd in (c for c in commands.iterkeys() if c.startswith(text)):
        if not state:
            return cmd
        else:
            state -= 1

readline.parse_and_bind('tab: complete')
readline.set_completer(complete)

while True:
    try:
        txt = raw_input('>> ')
        cmd = txt.split()[0]
        if cmd[0] is '!': cmd = cmd[1:]
        print commands[cmd](None,uname,txt) # no ChatBot object to pass
    except (EOFError, KeyboardInterrupt):
        print '' # newline to move past the prompt
        break
    except AttributeError:
        print "Sorry, !%s does not work outside the chat context"%cmd
    except KeyError, e:
        print "Couldn't process input:",e
    
