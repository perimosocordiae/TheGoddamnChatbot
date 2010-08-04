#!/usr/bin/env python

import subprocess, re
from itertools import chain

grep = subprocess.Popen('grep import *.py',stdout=subprocess.PIPE,shell=True)
filt = re.compile(r'\:\s*(?:from|import)\s+(.+?)(?:\s+import|\s*$)')
imports = (re.search(filt,i) for i in grep.communicate()[0].splitlines())
imports = set(chain.from_iterable(re.split(r'\s*,\s*',i.group(1)) for i in imports if i))

def try_import(i):
	try:
		__import__(i)
	except ImportError,e:
		return e

missing = set(str(e) for e in (try_import(i) for i in imports) if e)

if len(missing) == 0:
	print 'All dependencies satisfied!'
else:
	print 'The following packages were not found:'
	for m in sorted(missing):
		print '  ',m[m.rfind(' ')+1:]
