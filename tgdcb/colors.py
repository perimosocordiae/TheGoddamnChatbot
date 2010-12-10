COLORS = {
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

def notify(char, color, string):
    if color[0] in COLORS:
        cc = color[0]
    else:
        cc = 'E'
    return "%s/%s\\%s %s"%(COLORS['E']+COLORS[cc]+COLORS['U'],
                           char,COLORS['x'],string)

def colorize(color,string):
    if not color[0] in COLORS: return string
    code = COLORS[color[0]]
    return ''.join([COLORS['E'],code,string,COLORS['x']])

if __name__ == "__main__":
    print notify('x','r','Big bad stuff happening')
    print notify('?','g','Asking a question')
    print notify('!','y','Warning')
    print notify('i','b','This is informational')
    print colorize('g',"this should be green")
