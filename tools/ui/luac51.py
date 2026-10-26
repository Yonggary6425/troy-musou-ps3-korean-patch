import struct
class R:
    def __init__(s,b,p): s.b=b; s.p=p
    def u8(s): v=s.b[s.p]; s.p+=1; return v
    def i32(s): v=struct.unpack('>i',s.b[s.p:s.p+4])[0]; s.p+=4; return v
    def u32(s): v=struct.unpack('>I',s.b[s.p:s.p+4])[0]; s.p+=4; return v
    def str_(s):
        n=s.u32(); v=s.b[s.p:s.p+n]; s.p+=n; return v
def func(r):
    f={}
    f['src']=r.str_(); f['line']=r.i32(); f['last']=r.i32()
    f['nups'],f['np'],f['va'],f['ms']=r.u8(),r.u8(),r.u8(),r.u8()
    n=r.i32(); f['code_off']=r.p; f['code']=[r.u32() for _ in range(n)]
    n=r.i32(); ks=[]
    for _ in range(n):
        t=r.u8(); off=r.p
        if t==0: ks.append((t,None,off))
        elif t==1: ks.append((t,r.u8(),off))
        elif t==3: ks.append((t,struct.unpack('>f',r.b[r.p:r.p+4])[0],off)); r.p+=4
        elif t==4: ks.append((t,r.str_(),off))
        else: raise Exception('ktype %d at %x'%(t,off))
    f['k']=ks
    n=r.i32(); f['p']=[func(r) for _ in range(n)]
    n=r.i32(); r.p+=4*n
    n=r.i32()
    for _ in range(n): r.str_(); r.p+=8
    n=r.i32()
    for _ in range(n): r.str_()
    return f
def chunk(b,p):
    assert b[p:p+4]==b'\x1bLua'
    r=R(b,p+12); f=func(r); return f,r.p
OPN="MOVE LOADK LOADBOOL LOADNIL GETUPVAL GETGLOBAL GETTABLE SETGLOBAL SETUPVAL SETTABLE NEWTABLE SELF ADD SUB MUL DIV MOD POW UNM NOT LEN CONCAT JMP EQ LT LE TEST TESTSET CALL TAILCALL RETURN FORLOOP FORPREP TFORLOOP SETLIST CLOSE CLOSURE VARARG".split()
def refs(f,ki):
    out=[]
    for pc,i in enumerate(f['code']):
        op=i&0x3f; A=(i>>6)&0xff; C=(i>>14)&0x1ff; B=(i>>23)&0x1ff; Bx=i>>14
        if OPN[op] in('LOADK','GETGLOBAL','SETGLOBAL'):
            if Bx==ki: out.append((pc,OPN[op],'Bx'))
        elif OPN[op] in ('SETTABLE','GETTABLE','SELF','ADD','SUB','MUL','DIV','MOD','POW','EQ','LT','LE'):
            if B==0x100+ki: out.append((pc,OPN[op],'B'))
            if C==0x100+ki: out.append((pc,OPN[op],'C'))
    return out
