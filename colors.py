c = {
    'k':"[30m",
    'r':"[31m",
    'g':"[32m",
    'y':"[33m",
    'b':"[34m",
    'm':"[35m",
    'c':"[36m",
    'w':"[37m",
    'd':"[39m",
    'x':"[0m",
    'E':"[1m",
    'e':"[22m",
    'N':"[5m",
    'n':"[25m",
    'U':"[4m",
    'u':"[24m",
}

def notify(char, color, str):
    if color[0] in c:
        cc = color[0]
    else:
        cc = 'E'
    return "%s/%s\\%s %s"%(c['E']+c[cc]+c['U'],char,c['x'],str)

def colorize(color,str):
    if not color[0] in c: return str
    code = c[color[0]]
    return ''.join([c['E'],code,str,c['x']])

if __name__ == "__main__":
    print notify('x','r','Big bad stuff happening')
    print notify('?','g','Asking a question')
    print notify('!','y','Warning')
    print notify('i','b','This is informational')
    print colorize('g',"this should be green")
