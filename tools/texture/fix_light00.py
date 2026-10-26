import sys; sys.path.insert(0,'/tmp/claude-0/work')
import cpkg,g1t
from PIL import Image
from restyle import draw
from build_ui import put
J="/mnt/user-data/uploads/Troy Musou (Japan)/Troy Musou (Japan)/PS3_GAME/USRDIR/PS3/CommonMasterPackage.cpkg"
B="/tmp/claude-0/jpk/build/PS3_GAME/USRDIR/PS3/CommonMasterPackage.cpkg"
jo=open(J,'rb').read(); bo=open(B,'rb').read()
d=bytearray(cpkg.unpack(bo)); T={t['name']:t for t in g1t.scan(bytes(d))}
im=g1t.decode(bytes(d),T['Light00']).convert('RGBA'); orig=im.copy()
items=[((0,0,150,28),'보조 목표',1),((151,0,256,28),'주 목표',1),
 ((0,28,190,56),'고유 아이템',1),((191,28,245,56),'구르기',3),
 ((0,79,143,111),'보조 목표',1),((151,79,248,111),'클레오스',1),
 ((0,112,157,140),'후 무기 던지기',6),((157,112,256,140),'기절 공격',1),
 ((0,140,80,168),'집중 공격',1),((80,140,183,168),'동작',3),((183,140,256,168),'연계',6),
 ((0,168,80,196),'빠른 공격',1),((80,168,186,196),'구르기 공격',3),
 ((0,196,131,224),'도끼·곤봉·검',1),((132,196,160,224),'창',1),
 ((0,224,122,256),'보상 합계',1),((123,224,248,256),'전체 진행도',3)]
HS={'집중 공격':0.78,'기절 공격':0.78,'빠른 공격':0.78,'연계':0.78,'후 무기 던지기':0.78,'구르기':0.78,'구르기 공격':0.78,'동작':0.85}
REF={'동작':(0,140,80,168),'연계':(0,140,80,168)}
for box,text,pad in items:
    tmp=orig.copy()
    if text in REF:
        r=orig.crop(REF[text]); W=box[2]-box[0]
        tile=Image.new('RGBA',(W,r.height),(0,0,0,0)); x=0
        while x<W: tile.paste(r,(x,0)); x+=r.width
        tmp.paste(tile,box[:2])
    draw(tmp,box,text,align='left',pad=pad,track=0.02,hscale=HS.get(text))
    im.paste(tmp.crop(box),box[:2])
put(d,T['Light00'],im)
p,r,n=cpkg.pack_reuse(bytes(d),bo); assert cpkg.unpack(p)==bytes(d)
open(B,'wb').write(p); print('cmp',len(p),r,n)
bg=Image.new('RGBA',im.size,(60,60,80,255)); bg.alpha_composite(g1t.decode(bytes(d),T['Light00']).convert('RGBA'))
bg.convert('RGB').resize((768,768),Image.LANCZOS).save('/tmp/claude-0/lp/light00_ko.png')
