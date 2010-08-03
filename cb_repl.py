#!/usr/bin/env python

from cmds import commands
from getpass import getuser

uname = getuser()
print """Enter a command at the prompt
    !cmds will print a list of available commands
    Ctrl-C or Ctrl-D (EOF) to quit
    Note that not all commands will work outside of chat"""

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
    
