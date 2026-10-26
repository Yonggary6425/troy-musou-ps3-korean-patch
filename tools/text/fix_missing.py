import re
exec(open('/tmp/claude-0/jpk/widths.py').read())
P="/tmp/claude-0/jpk/build/PS3_GAME/USRDIR/PS3/Localization/JPN/UIStringsJPN.ini"
raw=open(P,'rb').read().decode('utf-16-be'); bom=raw.startswith('﻿'); lines=raw.lstrip('﻿').split('\r\n')
NEW={('[Title]','ViolenceMessage'):'이 게임에는 출혈 표현이 담겨 있습니다.\\n출혈 효과를 끄면 피가 보이지 않습니다.\\n출혈 효과를 켤지 끌지 고르십시오.\\n(옵션 > HUD 설정에서도 바꿀 수 있습니다.)',
     ('[Skills]','ScenItem_05.Description0'):'장을 마칠 때마다\\n아이템을 하나 얻는다.',
     ('[Extras]','Gallery.Art048'):'에키드나 콘셉트',('[Extras]','Gallery.Art049'):'에리뉘스 콘셉트',('[Extras]','Gallery.Art050'):'음유시인 콘셉트'}
sec=None; done=0
for i,l in enumerate(lines):
    if l.startswith('['): sec=l; continue
    if '=' in l:
        k,v=l.split('=',1)
        if (sec,k) in NEW: lines[i]=k+'='+NEW[(sec,k)]; done+=1; print(k,w(NEW[(sec,k)]))
print('done',done)
open(P,'wb').write((('﻿' if bom else '')+'\r\n'.join(lines)).encode('utf-16-be'))
