import re, subprocess, gc
import keywords, cmds, tasks
from os import getpid
from math import modf
from time import time,localtime,strftime
from psutil import get_process_list
from random import choice,randint
from urllib import quote_plus
from urllib2 import urlopen
from cthulhu import blargltext
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparse
from dateutil.relativedelta import relativedelta
from htmlunescape import unescape_to_fixed_point as unescape
from twython.twython import Twython

def backticks(cmd):
    '''emulate perl/ruby's `cmd` style'''
    return subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True).communicate()[0]

def cmd_uptime(obj,frm,txt):
    etime = backticks('ps -p %d -o etime'%getpid()).split()[1]
    m = re.match(r'(?:(\d+)-)?(?:(\d\d):)?(\d\d):(\d\d)',etime)
    if not m: return "Strangely formatted uptime: "+etime
    days,hrs,mins,secs = [int(x) if x else 0 for x in m.groups()]
    td = timedelta(days,secs,0,0,mins,hrs)
    fmtstr = "I've been online for %s hours, %s minutes, and %s seconds"
    return fmtstr % tuple(str(td).split(':'))

def cmd_reload(obj,frm,txt):
    try:
        reload(keywords)
    except Exception,e:
        return "Keywords reload failed: %s"%e
    obj.keywords = keywords.keywords
    try:
        reload(cmds)
    except Exception,e:
        return "Commands reload failed: %s"%e
    obj.commands = cmds.commands
    try:
        reload(tasks)
    except Exception,e:
        return "Tasks reload failed: %s"%e
    return "Locked and loaded"

def cmd_calc(obj,frm,txt):
    match = re.match(".*calc\s+(.*)",txt)
    if not match: return "Usage: !calc <math_expr>"
    calc_str = match.group(1)
    # check for disallowed chars
    if re.search("[^0-9\.\(\)<>x\+\-\*/%\^\|&\s]",calc_str):
        return "I can only calculate math expressions!"
    # check for overly large exponents
    exp = re.search("\*\*\s*(\d+)",calc_str)
    if exp and int(exp.group(1)) > 100:
        return "Nice try. Smaller exponent, please!"
    try:
        return str(eval(calc_str))
    except: pass
        
def cmd_art(obj,frm,txt):
    match = re.match(".*art\s+([^\s.,\n]+)",txt)
    if not match: return "Usage: !art <name>"
    art_name = match.group(1)
    try:
        out = backticks('figlet -f banner '+art_name).rstrip().replace(' ','_')
    except:
        return "Hmm, does my host have figlet installed?"
    return "\n"+out
    
def cmd_map(obj,frm,txt):
    match = re.match(".*map\s+(.+)",txt)
    if not match: return "Usage: !map <query>"
    loc = quote_plus(match.group(1))
    return "http://maps.google.com/maps?q=%s"%loc

def cmd_trends(obj,frm,txt):
    json = Twython().getCurrentTrends()
    trends = [v['name'] for v in json['trends'].values()[0]]
    return "Current twitter trends:\n"+', '.join(trends)

def cmd_twitstat(obj,frm,txt):
    match = re.match(".*status\s+(\w+)",txt)
    if not match: return "Usage: !status <twitter_name>"
    try:
        json = Twython().showUser(screen_name=match.group(1))
        return "Twitter status for %s:\n%s"%(match.group(1),json['status']['text'])
    except Exception, e:
        return "Error getting twitter status for %s: %s"%(match.group(1),e)

def cmd_shutup(obj,frm,txt):
    obj.respond = False
    return "Zipping my lips"

def cmd_enable(obj,frm,txt):
    if not obj.respond:
        obj.respond = True
        return "I'm baaaaack!"
    else:
        return "I was already able to talk, but thanks anyway"

def cmd_weather(obj,frm,txt):
    match = re.match(".*weather\s+(\d+)",txt)
    if not match: return "Usage: !weather <zip_code>"
    url = 'http://www.google.com/ig/api?weather=%s'%match.group(1)
    xml = urlopen(url).readline()
    cond = re.search("<current_conditions>(.*)<\/current_conditions>",xml).group(1)
    c,t,_,h,_,w = re.findall('\"(.*?)\"',cond)
    t = int(t)
    r = int(h[-3:-1])
    heat_idx = -42.379 + 2.04901523*t + 10.14333127*r - 0.22475541*t*r - 0.00683783*t*t - 0.05481717*r*r + 0.00122874*t*t*r + 0.00085282*t*r*r - 1.99e-6*t*t*r*r
    return "Current weather: %s, %d degrees.\n%s\n%s\nHeat Index: %d degrees"%(c,t,h,w,heat_idx)

def cmd_news(obj,frm,txt):
    url = 'http://www.google.com/ig/api?news'
    xml = urlopen(url).readline()
    headlines = map(unescape,re.findall('<title data=\"(.*?)\"',xml)[1:])
    headlines.insert(0,"Your top news stories, %s:"%frm)
    return "\n".join(headlines)

def get_quote(page):
    rating = 0
    while True:
        m = re.match('<p class="quote">.*\+<\/a>\((\d+)\).*<p class="qt">(.*)<br \/>',page.readline())
        if m:
            rating = int(m.group(1))
            break
        elif page.readline() == '': 
            return rating,None #EOF
    quote = [m.group(2)]
    while True:
        l = page.readline().rstrip()
        quote.append(l.split('<')[0]) #omg hax
        if l.endswith("</p>"): break
    return rating,[unescape(q) for q in quote]

def cmd_bash(obj,frm,txt):
    match = re.match(".*bash\s*(\d*)",txt)
    min_rating = int(match.group(1)) if match.group(1) != '' else 1000
    if min_rating > 10000: min_rating = 10000
    url = 'http://bash.org/?random1'
    page = urlopen(url)
    while True:
        try:
            rating,quote = get_quote(page)
        except: continue # invalid quote, just try again
        if not quote:
            page = urlopen(url) # got to the end, load another page
        elif rating >= min_rating: # enforce the min rating
            return "\n".join(quote)
 
def cmd_cmds(obj,frm,txt):
    return "Available commands: "+', '.join(['!'+k for k in sorted(commands.iterkeys())])

def cmd_lmgtfy(obj,frm,txt):
    match = re.match(".*?lmgtfy\s+(.+)",txt)
    if not match: return "Usage: !lmgtfy <query>"
    return "http://lmgtfy.com/?q="+quote_plus(match.group(1))

def cmd_parrot(obj,frm,txt):
    match = re.match(".*?parrot\s+(.+)",txt)
    if not match: return "Usage: !parrot <text>"
    return match.group(1)

def cmd_random(obj,frm,txt):
    match = re.match(".*?random\s+(.+)",txt)
    if not match: return "Usage: !random <number/range>"
    input = [s for s in re.split('[^\d-]+',match.group(1)) if len(s) > 0]
    if 0 < len(input) < 3:
        num1 = int(input[0])
        num2 = int(input[1]) if len(input) == 2 else 0
        return randint(num1,num2) if num1 <= num2 else randint(num2,num1)
    else:
        return choice(input)

def cmd_calendar(obj,frm,txt):
    out = backticks('calendar').rstrip()
    return "Notable events on/around today's date:\n"+out

def cmd_timecalc(obj,frm,txt):
    match = re.match(".*t(?:ime)?calc\s+(.+)",txt)
    if not match: return "Usage: !timecalc <expression>"
    expr = match.group(1)
    nowtime = ':'.join(map(str,localtime()[3:5]))
    expr = expr.replace('now',nowtime)
    for time in re.finditer("(\d+(?:\:\d+)?)\s*([PpAa][Mm])?",expr):
        tstr,nums,ampm = time.group(0,1,2)
        snums = nums.split(':')
        hrs = float(snums[0]) + ( float(snums[1])/60. if len(snums) == 2 else 0 )
        if ampm and ampm[0] in ['p','P']:
            hrs += 12
        if str(hrs) != tstr:
            try: float(tstr) # ZOMG hax
            except:
                expr = expr.replace(tstr,str(hrs),1)
    print 'sending to cmd_calc: '+expr
    res = cmd_calc(obj,frm,'!calc '+expr)
    frac, itg = modf(float(res))
    return "%d:%02d"%(itg,int(abs(frac)*60))

def cmd_gc(obj,frm,txt):
    g = gc.collect()
    return "%d garbages collected."%g

def cmd_rusage(obj,frm,txt):
    pyprocs = (p for p in get_process_list() if len(p.cmdline) >1 and 'python' in p.cmdline[0])
    pname = 'bot.py' if obj else 'cb_repl.py' # DIRRRRRTY
    thisproc = [ p for p in pyprocs if pname in p.cmdline[1] ][0]
    usertime = thisproc.get_cpu_times()[0]
    pcpu = thisproc.get_cpu_percent()
    mem,unit = thisproc.get_memory_info()[0],'b'
    for u in ['kb','mb','gb']:
        if mem / 1024.0 > 1:
            mem /= 1024.0
            unit = u
        else: break
    pmem = thisproc.get_memory_percent()
    return "\n".join(["Resource usage stats",
                      "User time: %.3f secs"%usertime,
                      #"CPU usage: %.3f%%"%pcpu,
                      "RAM usage: %.3f %s (%.3f%% of total)"%(mem,unit,pmem)])

def cmd_countdown(obj,frm,txt):
    match = re.match(".*?countdown\s+(.+)",txt)
    if not match: return "Usage: !countdown <date/time>"
    try:
        until = dateparse(match.group(1))
    except: return "Couldn't parse '%s' as a date"%match.group(1)
    delta = relativedelta(until,datetime.now())
    dstr = str(delta)[14:-1]
    prep = ' until ' if delta.seconds >= 0 else ' since '
    return re.sub('(\w+)=[\+-]?(\d+)',r'\2 \1',dstr)+prep+str(until)

def cmd_cthulhu(obj,frm,txt):
    match = re.match(".*?blargl\s+(.+)",txt)
    if not match: return "Usage: !blargl <text>"
    return blargltext(match.group(1))

def cmd_roll(obj,frm,txt):
    match = re.match(".*?roll\s+(\d+)d(\d+)",txt)
    if not match: return "Usage: !roll <number>d<sides>"
    n,s = map(int,match.groups())
    roll = sum(randint(1,s) for _ in xrange(n))
    an = 'an' if (str(roll)[0] == '8' or roll == 18) else 'a'
    return "%s rolled %s %d." % (frm,an,roll)

commands = {
    'gc': cmd_gc,
    'map': cmd_map,
    'calc': cmd_calc,
    'news': cmd_news,
    'roll': cmd_roll,
    'blargl': cmd_cthulhu,
    'lmgtfy': cmd_lmgtfy,
    'parrot': cmd_parrot,
    'quotes': cmd_bash,
    'random': cmd_random,
    'reload': cmd_reload,
    'resume': cmd_enable,
    'rusage': cmd_rusage,
    'shutup': cmd_shutup, 'quiet': cmd_shutup,
    'status': cmd_twitstat,
    'trends': cmd_trends,
    'uptime': cmd_uptime,
    'weather': cmd_weather,
    'calendar': cmd_calendar,
    'commands': cmd_cmds, 'triggers': cmd_cmds,
    'countdown': cmd_countdown,
    'timecalc': cmd_timecalc, 'tcalc': cmd_timecalc,
}

