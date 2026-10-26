import sys,struct,json
sys.path.insert(0,'/tmp/claude-0/work')
import numpy as np
from g1n import parse
import hangul
from hangul import Style
SRC="/mnt/user-data/uploads/Troy Musou (Japan)/Troy Musou (Japan)/PS3_GAME/USRDIR/PS3/TrojanMusou/Fonts/fonts_JP.g1n"
hangul.STYLES['j0']=Style(font='NotoSerifKR[wght].ttf',weight=900,cell=30,top=2,bot=25,bold=0,pad=1,outline=1,shadow=(1,1),shblur=0.6,shalpha=0.5,kind='outline',gap=1)
hangul.STYLES['j3']=Style(font='NanumGothic-ExtraBold.ttf',weight=None,cell=44,top=5,bot=38,bold=0,pad=2,outline=1,shadow=(1,2),shblur=0.8,shalpha=1.0,kind='bevel',gap=1)
def rend(ch,key):
    idx=hangul.render(ch,key)
    if idx is None: return None
    if key=='j0':
        f=idx>=8; idx=idx.copy(); idx[f]=8+np.rint((idx[f]-8)*7/6).astype(int)
    return idx
def pack4(idx):
    h,w=idx.shape; st=(w+1)//2; buf=bytearray()
    for y in range(h):
        row=list(idx[y])+[0]*(st*2-w)
        buf+=bytes((row[i]<<4)|row[i+1] for i in range(0,st*2,2))
    return buf
def build(chars,out):
    d=open(SRC,'rb').read(); g=parse(d)
    gdata=bytearray(d[g['gdata']:]); fonts=[]
    for fi,f in enumerate(g['fonts']):
        m=list(f['map']); ents=[list(e) for e in f['glyphs']]
        if fi in (0,3):
            key='j0' if fi==0 else 'j3'
            tmpl=ents[m[ord('あ')]] if fi==0 else ents[m[ord('兵')]]
            H=tmpl[1]
            for ch in chars:
                if m[ord(ch)]: continue
                idx=rend(ch,key)
                if idx is None: continue
                h,w=idx.shape; off=len(gdata); gdata+=pack4(idx)
                adv=max(1,w-(1 if fi==0 else 2))
                m[ord(ch)]=len(ents); ents.append([w,h,0,h,adv,tmpl[5],tmpl[6],tmpl[7],off])
            # ASCII space
            if not m[32]:
                sw=9 if fi==0 else 12
                off=len(gdata); gdata+=pack4(np.zeros((H,2),int))
                m[32]=len(ents); ents.append([2,H,0,H,sw,tmpl[5],tmpl[6],tmpl[7],off])
        fonts.append((m,ents))
    hdr_end=0x3c+g['npal']*64
    o=bytearray(d[:hdr_end]); offs=[]; body=bytearray()
    for m,ents in fonts:
        offs.append(hdr_end+len(body)); body+=struct.pack('>65536H',*m)
        for e in ents: body+=struct.pack('>8BI',*[v&0xff for v in e[:8]],e[8])
    gd=hdr_end+len(body); o+=body+gdata
    struct.pack_into('>I',o,0x08,len(o)); struct.pack_into('>I',o,0x0c,offs[0]); struct.pack_into('>I',o,0x14,gd)
    struct.pack_into('>%dI'%len(offs),o,0x20,*offs)
    open(out,'wb').write(o); print('size',len(o),'glyphs',[len(e) for _,e in fonts])
if __name__=='__main__':
    chars=open('/tmp/claude-0/jpk/chars.txt',encoding='utf-8').read()
    chars=''.join(c for c in chars if c not in '\n\\<>{} ' and ord(c)<65536)
    build(chars,'/tmp/claude-0/jpk/font/fonts_JP_ko.g1n')
