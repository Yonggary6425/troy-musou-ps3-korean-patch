import os,re,glob
J="/mnt/user-data/uploads/Troy Musou (Japan)/Troy Musou (Japan)/PS3_GAME/USRDIR/PS3/Localization/JPN/"
E="/tmp/claude-0/chk/o/PS3_GAME/USRDIR/PS3/Localization/ENG/"
def kv(p):
    t=open(p,'rb').read().decode('utf-16-be').lstrip('﻿'); sec=None; out=[]
    for l in t.split('\r\n'):
        if l.startswith('['): sec=l
        elif '=' in l and not l.startswith(';'): k,v=l.split('=',1); out.append((sec,k,v))
    return out
tot={}
for jf in sorted(glob.glob(J+'*.ini')):
    n=os.path.basename(jf); ef=E+n.replace('JPN.ini','ENG.ini')
    cat='UI' if n.startswith('UI') else 'Scen' if n.startswith('Scen') else 'FMV' if 'FMV' in n else 'Sub'
    j=kv(jf); e=kv(ef)
    jk=[(s,re.sub(r'_JP(?=\[)','',k)) for s,k,v in j]; ek=[(s,k) for s,k,v in e]
    same=len(set(jk)&set(ek))
    t=tot.setdefault(cat,[0,0,0,0]); t[0]+=len(j); t[1]+=len(e); t[2]+=same; t[3]+= (jk==ek)
    if cat in('Sub',) and jk!=ek: print('Sub mismatch',n,len(j),len(e),same)
for c,v in tot.items(): print(c,'JP lines',v[0],'EN lines',v[1],'key-matched',v[2],'files same order',v[3])
