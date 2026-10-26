import sys,struct,os; sys.path.insert(0,'/tmp/claude-0/work'); sys.path.insert(0,'/tmp/claude-0/lua'); import cpkg
from scan_scale import find
J="/mnt/user-data/uploads/Troy Musou (Japan)/Troy Musou (Japan)/PS3_GAME/USRDIR/PS3/"
B="/tmp/claude-0/jpk/build/PS3_GAME/USRDIR/PS3/"
SC=0.9
for n in ['UI/Scenes/UI/UI_JPN.lpkg','UI/Scenes/Scenario/Scenario_JPN.lpkg','UI/Scenes/Challenges/Challenges_JPN.lpkg','UI/Scenes/Loading/Loading_JPN.lpkg']:
    d=open(J+n,'rb').read(); u=bytearray(cpkg.unpack(d))
    for start,off,keys in find(bytes(u)):
        assert all(k[2]==b'm_nScale\x00' for k in keys)
        assert abs(struct.unpack('>f',u[off:off+4])[0]-0.8)<1e-5
        u[off:off+4]=struct.pack('>f',SC)
    p,r,k=cpkg.pack_reuse(bytes(u),d); assert cpkg.unpack(p)==bytes(u)
    os.makedirs(os.path.dirname(B+n),exist_ok=True); open(B+n,'wb').write(p); print(n,len(d),len(p))
