from __future__ import with_statement
from random import choice,randint
from urllib2 import urlopen
from contextlib import closing
from BeautifulSoup import BeautifulSoup
from htmlunescape import unescape
import re

# simple, keyword-based retorts
def anagrammer(frm,txt):
    return txt.replace("anagram","nag a ram")
def cake(frm,txt):
    return "The cake is a lie!"
def your_mom(frm,txt):
    if '\u' in frm: return None
    post_is = txt[txt.rfind(' is '):]
    if len(post_is) == 0 or \
        '?' in post_is or "\n" in post_is or '. ' in post_is:
        return None
    mom = choice(['MOM','DAD','FACE','DOG','GRANDMOTHER','IMAGINARY FRIEND'])
    return "%s's %s%s"%(frm,mom,post_is)
def charris(frm,txt):
    return "PORK CHOP"
def frown(frm,txt):
    return "@%s: turn that frown upside down! :P"%frm
def xkcd(frm,txt):
    return "http://xkcd.com/%d/"%randint(1,751)
def drop_tables(frm,txt):
    return "%s'0; DROP TABLE users;--"%frm
def sparta(frm,txt):
    return "No, %s, THIS\nIS\nSPARTA!"%frm
def legion(frm,txt):
    return "We are Legion"
def orly(frm,txt):
    return "yarly!"
def vim_save(frm,txt):
    if txt.rstrip() != ':w': return None
    lines = randint(10000,20000)
    chars = randint(1200000,2000000)
    return '"chat.txt" %dL, %dC written'%(lines,chars)

def chkurl(frm,txt):
    match = re.search("https?://\S+",txt)
    if not match: return None
    url = match.group(0).replace('>','')
    try:
        with closing(urlopen(url)) as page:
            page_type = page.headers.gettype()
            if page_type != 'text/html':
                return "Link points to a file of type: "+page_type
            title = BeautifulSoup(page.read()).title.text
    except KeyboardInterrupt:
        return "screw you guys"
    except Exception, e:
        return "couldn't open page: %s"%e
    try:
        title = re.sub('\s+',' ',unescape(title))
    except: pass
    if title:
        return "link points to: '%s'"%title
    else:
        return "couldn't get the title for: %s"%url

#master list! be sure to add any new keywords to this!
keywords = {#' is ': your_mom,
            'anagram': anagrammer,
            #'cake': cake,
            #'charris': charris,
            #':(': frown,
            #'xkcd': xkcd, 'raptor': xkcd,
            #'database': drop_tables,
            'this is madness': sparta,
            'we are legion': legion,
            #' orly?': orly,
            ':w': vim_save,
            'http': chkurl,
}
