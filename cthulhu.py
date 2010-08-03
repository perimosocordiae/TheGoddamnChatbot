'''A port of the web-based "zalgo text generator"'''

from random import choice,randint

zalgo_up = [u'\u030d', u'\u030e', u'\u0304', u'\u0305', u'\u033f', u'\u0311',
            u'\u0306', u'\u0310', u'\u0352', u'\u0357', u'\u0351', u'\u0307',
            u'\u0308', u'\u030a', u'\u0342', u'\u0343', u'\u0344', u'\u034a',
            u'\u034b', u'\u034c', u'\u0303', u'\u0302', u'\u030c', u'\u0300',
            u'\u0301', u'\u030b', u'\u030f', u'\u0312', u'\u0313', u'\u0314',
            u'\u033d', u'\u0309', u'\u033e', u'\u0346', u'\u031a']
 
zalgo_down = [u'\u0316', u'\u0317', u'\u0318', u'\u0319', u'\u031c', u'\u031d',
              u'\u031e', u'\u031f', u'\u0320', u'\u0324', u'\u0325', u'\u0326',
              u'\u0329', u'\u032a', u'\u032b', u'\u032c', u'\u032d', u'\u032e',
              u'\u032f', u'\u0330', u'\u0331', u'\u0332', u'\u0333', u'\u0339',
              u'\u033a', u'\u033b', u'\u033c', u'\u0345', u'\u0347', u'\u0348',
              u'\u0349', u'\u034d', u'\u034e', u'\u0353', u'\u0323']
    
zalgo_mid = [u'\u0315', u'\u031b', u'\u0340', u'\u0341', u'\u0358', u'\u0321',
             u'\u0322', u'\u0327', u'\u0328', u'\u0334', u'\u0335', u'\u0336',
             u'\u034f', u'\u035c', u'\u035d', u'\u035e', u'\u035f', u'\u0360',
             u'\u0362', u'\u0338', u'\u0337', u'\u0361', u'\u0489']
 
def blargltext(text,amt=3,mid=True,high=False,low=False):
    assert mid or high or low
    assert amt > 0
    blargl = []
    for c in list(text):
        blargl.append(c)
        if 32 < ord(c) < 127:
            for _ in xrange(randint(1,amt)):
                if mid:  blargl.append(choice(zalgo_mid))
                if high: blargl.append(choice(zalgo_up))
                if low:  blargl.append(choice(zalgo_down))
    return u''.join(blargl)


