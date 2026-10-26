import sys,json,re,glob,os
sys.path.insert(0,'/tmp/claude-0/work')
from g1n import parse
exec(open('/tmp/claude-0/jpcmp.py').read().split('tot={}')[0])
G=parse(open('/tmp/claude-0/jpk/font/fonts_JP_ko.g1n','rb').read())
f0=G['fonts'][0]
def adv(ch):
    gi=f0['map'][ord(ch)] if ord(ch)<65536 else 0
    return f0['glyphs'][gi][4] if gi else 24
def strip(s):
    s=re.sub(r'<Settings\.ControlSet\.[^>]*>|<Console:[^>]*>','',s)  # button icon ~ 30px
    s=re.sub(r'<[^>]*>','',s)  # variable ~ name 120px
    s=re.sub(r'\{[^}]*\}','',s)
    return s
def w(s):
    best=[]
    for ln in strip(s).split('\\n'):
        t=0
        for ch in ln:
            t+= 30 if ch=='' else 120 if ch=='' else adv(ch)
        best.append(t)
    return best
def cat(n): return 'UI' if n.startswith('UI') else 'Scen' if n.startswith('Scen') else 'FMV' if 'FMV' in n else 'Sub'
