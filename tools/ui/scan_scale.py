import sys,re; sys.path.insert(0,'/tmp/claude-0/work'); sys.path.insert(0,'/tmp/claude-0/lua'); import cpkg
from luac51 import *
def walk(f,path=()):
    yield f,path
    for n,p in enumerate(f['p']): yield from walk(p,path+(n,))
def find(u):
    res=[]
    for m in re.finditer(rb'\x1bLua',u):
        f,end=chunk(u,m.start())
        for g,path in walk(f):
            ks=[k[1] for k in g['k']]
            if any(isinstance(k,bytes) and k.startswith(b'<SubtitleLogic:Text>') for k in ks):
                for ki,k in enumerate(g['k']):
                    if k[0]==3 and abs(k[1]-0.8)<1e-6:
                        rr=refs(g,ki)
                        keys=[]
                        for pc,op,w in rr:
                            i=g['code'][pc]; B=(i>>23)&0x1ff
                            keys.append((op,w,g['k'][B-0x100][1] if B>=0x100 else B))
                        res.append((m.start(),k[2],keys))
    return res
if __name__=='__main__':
    for f in sys.argv[1:]:
        u=cpkg.unpack(open(f,'rb').read())
        for r in find(u): print(f.split('/')[-1],hex(r[0]),hex(r[1]),r[2])
