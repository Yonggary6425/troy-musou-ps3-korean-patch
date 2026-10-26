import json,re,glob,os
J="/mnt/user-data/uploads/Troy Musou (Japan)/Troy Musou (Japan)/PS3_GAME/USRDIR/PS3/Localization/JPN/"
OUT="/tmp/claude-0/jpk/build/PS3_GAME/USRDIR/PS3/Localization/JPN/"
os.makedirs(OUT,exist_ok=True)
src=json.load(open('/tmp/claude-0/tr/src.json',encoding='utf-8'))
ko=json.load(open('/tmp/claude-0/tr/ko_full.json',encoding='utf-8'))
fmv=json.load(open('/tmp/claude-0/jpk/fmv_ko.json',encoding='utf-8'))
idx={(e['file'],'['+e['sec']+']',e['key']):e['id'] for e in src}
TAG={'{’}':'’','{‘}':'‘','{—}':'—','{…}':'…','{™}':'™'}
def conv(s):
    for a,b in TAG.items(): s=s.replace(a,b)
    return s
miss=[]; n=0; allko={}
for jf in sorted(glob.glob(J+'*.ini')):
    name=os.path.basename(jf); en=name.replace('JPN.ini','ENG.ini')
    raw=open(jf,'rb').read(); t=raw.decode('utf-16-be'); bom=t.startswith('﻿'); body=t.lstrip('﻿')
    lines=body.split('\r\n'); sec=None
    for i,l in enumerate(lines):
        if l.startswith('['): sec=l; continue
        if '=' not in l or l.startswith(';'): continue
        k,v=l.split('=',1)
        if 'FMV' in name:
            nv=fmv[f'{name}|{k}']
        else:
            ek=re.sub(r'_JP(?=\[)','',k)
            id_=idx.get((en,sec,ek))
            if id_ is None: miss.append((name,sec,k)); continue
            nv=conv(ko[str(id_)])
        lines[i]=k+'='+nv; n+=1; allko[(name,sec,k)]=nv
    out=('﻿' if bom else '')+'\r\n'.join(lines)
    open(OUT+name,'wb').write(out.encode('utf-16-be'))
print('replaced',n,'missing',len(miss),miss[:5])
json.dump({'|'.join(k):v for k,v in allko.items()},open('/tmp/claude-0/jpk/all_ko.json','w'),ensure_ascii=False)
chars=sorted(set(''.join(allko.values())))
open('/tmp/claude-0/jpk/chars.txt','w',encoding='utf-8').write(''.join(chars))
print('distinct chars',len(chars))
