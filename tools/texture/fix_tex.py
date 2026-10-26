import sys,io; sys.path.insert(0,'/tmp/claude-0/work')
import numpy as np
from PIL import Image
import cpkg, g1t
from restyle import replace, boxes
from build_ui import put
J="/mnt/user-data/uploads/Troy Musou (Japan)/Troy Musou (Japan)/PS3_GAME/USRDIR/PS3/"
B="/tmp/claude-0/jpk/build/PS3_GAME/USRDIR/PS3/"
prev=[]
# --- LocalizedCommon: Pause_Title redraw on JP layout
jo=open(J+'LocalizedCommonPackage_JPN.cpkg','rb').read()
d=bytearray(cpkg.unpack(open(B+'LocalizedCommonPackage_JPN.cpkg','rb').read())); dj=cpkg.unpack(jo)
T={t['name']:t for t in g1t.scan(bytes(d))}; TJ={t['name']:t for t in g1t.scan(dj)}
im=g1t.decode(dj,TJ['Pause_Title']).convert('RGBA'); src=im.copy()
items=[((69,7,143,44),'장비','center',(10,205)),((327,7,401,44),'구매','center',(225,505)),
       ((273,54,419,88),'목표','center',(225,505)),((230,107,459,144),'기술','center',(225,505)),
       ((262,152,426,190),'옵션','center',(225,505)),((278,203,408,238),'시스템','center',(225,505)),
       ((1,48,177,76),'최단 클리어 시간','right',(0,180)),((53,106,176,133),'최다 클레오스','right',(0,180)),
       ((48,164,178,191),'최다 격파 수','right',(0,180)),((49,222,177,249),'현재 기록','right',(0,180))]
for b,t,al,sp in items: replace(im,src,b,t,align=al,span=sp,size=0.8 if t=='목표' else 1.0)
put(d,T['Pause_Title'],im); prev.append(im)
p,r,n=cpkg.pack_reuse(bytes(d),jo); assert cpkg.unpack(p)==bytes(d); open(B+'LocalizedCommonPackage_JPN.cpkg','wb').write(p); print('loc',len(p),r,n)
# --- LocalizedUIGameMode: Main_BG labels, Title_Parts logo
jo=open(J+'LocalizedUIGameModePackage_JPN.mpkg','rb').read()
d=bytearray(cpkg.unpack(open(B+'LocalizedUIGameModePackage_JPN.mpkg','rb').read())); dj=cpkg.unpack(jo)
T={t['name']:t for t in g1t.scan(bytes(d))}; TJ={t['name']:t for t in g1t.scan(dj)}
mk=g1t.decode(bytes(d),T['Main_BG']).convert('RGBA'); mj=g1t.decode(dj,TJ['Main_BG']).convert('RGBA')
reg=(0,360,600,400); mk.paste(mj.crop(reg),reg[:2]); src=mk.copy()
lb=boxes(src,region=(0,366,600,400),jx=8,jy=1,minarea=15); print('MainBG label boxes',lb)
for b,t in zip(lb,['최단 클리어 시간','최다 클레오스','최다 격파 수']):
    replace(mk,src,b,t,align='left',span=(b[0],b[0]+175))
put(d,T['Main_BG'],mk); prev.append(mk.crop((0,300,600,420)))
tk=g1t.decode(bytes(d),T['Title_Parts']).convert('RGBA'); tj=g1t.decode(dj,TJ['Title_Parts']).convert('RGBA')
out=tj.copy(); reg=(600,0,1024,160); out.paste(tk.crop(reg),reg[:2])
put(d,T['Title_Parts'],out); prev.append(out)
p,r,n=cpkg.pack_reuse(bytes(d),jo); assert cpkg.unpack(p)==bytes(d); open(B+'LocalizedUIGameModePackage_JPN.mpkg','wb').write(p); print('ui',len(p),r,n)
for i,pv in enumerate(prev):
    bg=Image.new('RGBA',pv.size,(110,90,60,255)); bg.alpha_composite(pv); bg.convert('RGB').save(f'/tmp/claude-0/jpk/fix_{i}.png')
