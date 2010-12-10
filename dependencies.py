#!/usr/bin/env python

import re
from itertools import chain
from subprocess import Popen, PIPE

def try_import(i):
    try:
        __import__(i)
    except ImportError,e:
        return e

def main():
    grep = Popen('grep import *.py',stdout=PIPE,shell=True)
    filt = re.compile(r'\:\s*(?:from|import)\s+(.+?)(?:\s+import|\s*$)')
    imports = (filt.search(i) for i in grep.communicate()[0].splitlines())
    imports = chain(*(re.split(r'\s*,\s*',i.group(1)) for i in imports if i))
    missing = set(str(e) for e in (try_import(i) for i in set(imports)) if e)
    if len(missing) != 0:
        report(missing)
    else:
        patch_pyxmpp()

def report(missing):
    print 'The following packages were not found:'
    for m in sorted(missing):
        print '  ',m[m.rfind(' ')+1:]

def patch_pyxmpp():
    print 'All dependencies satisfied!'
    import pyxmpp
    path = pyxmpp.__path__[0]
    sed_base = "sudo sed -i'.bak' -e's/class \(%s\)\:/class \1(object):/' %s/"
    Popen((sed_base+"client.py")%('Client',path),shell=True).communicate()
    Popen((sed_base+"jabber/muc.py")%('MucRoomHandler',path),
            shell=True).communicate()
    print 'pyxmpp classes patched'

if __name__ == '__main__':
    main()
