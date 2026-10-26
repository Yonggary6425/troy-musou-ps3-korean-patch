exec(open('/tmp/claude-0/jpk/wrap.py').read())
ko=json.load(open('/tmp/claude-0/jpk/all_ko.json',encoding='utf-8'))
FIX={'UnlockChapterMessage':'장 선택에서 「<Campaign.SelectedScenario.Name>」을(를) 고를 수 있게 되었습니다.',
     'ItemTutorial[0]':'이 화면에서 {select}을 누르면\\n아이템 구매 화면으로 넘어갑니다.\\n아이템 구매 화면에서 {select}을 누르면\\n아이템 장착 화면으로 돌아갑니다.',
     'ItemTutorial[1]':'아이템은 가지고 있는 클레오스를 써서 구매합니다.',
     '00541X_G10_Patroklos_JP[0]':'신들이시여, 일로스의 무덤으로 가는 길을 보여 주소서.\\n그곳에서 트로이아 무리를 쓸어내겠습니다.',
     '03332X_T08_Ajax_JP[0]':'아킬레우스가 돌아와 원수를 갚으리라.\\n그때까지 너와 네 가문을 저주한다, 프리아모스의 아들아!',
     '03500X_T14_Odysseus_JP[0]':'그대를 이기지 못할지도 모르오, 아마존이여.\\n허나 아킬레우스 앞에서는 어찌 될지 두고 보겠소.'}
LIM={'Scen':360,'Sub':576,'FMV':592}
OUT="/tmp/claude-0/jpk/build/PS3_GAME/USRDIR/PS3/Localization/JPN/"
final={}; changed=0
for jf in sorted(glob.glob(J+'*.ini')):
    n=os.path.basename(jf); c=cat(n)
    raw=open(jf,'rb').read().decode('utf-16-be'); bom=raw.startswith('﻿'); lines=raw.lstrip('﻿').split('\r\n'); sec=None
    for i,l in enumerate(lines):
        if l.startswith('['): sec=l; continue
        if '=' not in l or l.startswith(';'): continue
        k,v=l.split('=',1); key='|'.join((n,sec,k)); t=ko[key]
        if k in FIX: t=FIX[k]
        if c=='UI':
            if sec=='[Help]': t=t.replace('   ','  ')
            elif len(v.split('\\n'))>=2 or max(w(t))>620:
                lim=max(max(w(v)),420)
                if max(w(t))>lim:
                    if '\\n' not in t:
                        words=t.split(' ')
                        for nl in range(2,7):
                            b=balanced(words,lim,nl) if nl<=4 else None
                            if b and b[0]<=lim: t='\\n'.join(b[1]); break
                        else: t=wrap(t,lim)
                    else: t=wrap(t,lim)
        else:
            if max(w(t))>LIM[c]:
                flat=t.replace('\\n',' ').replace('  ',' ')
                words=flat.split(' ')
                for nl,lm in ((2,LIM[c]),(2,620),(3,LIM[c]),(4,LIM[c])):
                    b=balanced(words,lm,nl)
                    if b and b[0]<=lm: t='\\n'.join(b[1]); break
                else: t=wrap(flat,LIM[c])
        if t!=ko[key]: changed+=1
        final[key]=t; lines[i]=k+'='+t
    open(OUT+n,'wb').write((('﻿' if bom else '')+'\r\n'.join(lines)).encode('utf-16-be'))
json.dump(final,open('/tmp/claude-0/jpk/final_ko.json','w'),ensure_ascii=False)
print('changed',changed,'files',len(glob.glob(OUT+'*.ini')))
import collections
print('max lines by cat',{c:max(len(v.split('\\n')) for k,v in final.items() if cat(k.split('|')[0])==c) for c in ['UI','Scen','Sub','FMV']})
# show some subtitle 3+ line cases
for k,v in final.items():
    if cat(k.split('|')[0]) in('Sub','FMV') and len(v.split('\\n'))>=3: print(k, v)
