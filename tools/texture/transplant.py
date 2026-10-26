# 유럽판 한글패치의 텍스처를 일본판 묶음 파일로 옮겨 심습니다.
# 일본판과 유럽판은 텍스처 이름·크기·형식이 같으므로, 유럽판에서 한글로 바뀐 텍스처만 그대로 복사합니다.
# 일본판 배치가 다른 텍스처(Pause_Title, Main_BG, Title_Parts)는 이후 fix_tex.py가 다시 그립니다.
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import cpkg,g1t
JP=sys.argv[1]      # 일본판 원본 .../USRDIR/PS3/
EUO=sys.argv[2]     # 유럽판 원본 .../USRDIR/PS3/
EUK=sys.argv[3]     # 유럽판 한글패치 결과 .../USRDIR/PS3/
OUT=sys.argv[4]     # 결과 .../USRDIR/PS3/
PAIRS=[('LocalizedCommonPackage_JPN.cpkg','LocalizedCommonPackage_ENG.cpkg'),
       ('LocalizedUIGameModePackage_JPN.mpkg','LocalizedUIGameModePackage_ENG.mpkg')]
for jn,en in PAIRS:
    jo=open(JP+jn,'rb').read(); j=bytearray(cpkg.unpack(jo))
    eo=cpkg.unpack(open(EUO+en,'rb').read()); ek=cpkg.unpack(open(EUK+en,'rb').read())
    TJ={t['name']:t for t in g1t.scan(bytes(j))}; TO={t['name']:t for t in g1t.scan(eo)}; TK={t['name']:t for t in g1t.scan(ek)}
    n=0
    for name,tk in TK.items():
        to=TO.get(name); tj=TJ.get(name)
        if not to or not tj: continue
        kraw=ek[tk['dataoff']:tk['dataoff']+tk['datalen']]
        if kraw==eo[to['dataoff']:to['dataoff']+to['datalen']]: continue   # 유럽판에서 안 바뀐 텍스처
        if (tj['w'],tj['h'],tj['fmt'],tj['datalen'])!=(tk['w'],tk['h'],tk['fmt'],tk['datalen']): continue
        j[tj['dataoff']:tj['dataoff']+tj['datalen']]=kraw; n+=1
    p,r,c=cpkg.pack_reuse(bytes(j),jo); assert cpkg.unpack(p)==bytes(j)
    os.makedirs(OUT,exist_ok=True); open(OUT+jn,'wb').write(p); print(jn,'textures',n)
