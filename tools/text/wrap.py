exec(open('/tmp/claude-0/jpk/widths.py').read())
def lw(s): return w(s)[0]
def balanced(words,limit,n):
    # split words into n lines minimizing max width (n<=3), brute force
    import itertools
    best=None
    L=len(words)
    for cuts in itertools.combinations(range(1,L),n-1):
        idx=(0,)+cuts+(L,)
        lines=[' '.join(words[idx[i]:idx[i+1]]) for i in range(n)]
        m=max(lw(x) for x in lines)
        if best is None or m<best[0]: best=(m,lines)
    return best
def wrap(s,limit,maxl=None):
    out=[]
    for para in s.split('\\n'):
        if lw(para)<=limit: out.append(para); continue
        words=para.split(' ')
        res=None
        for n in range(2,min(6,len(words))+1):
            b=balanced(words,limit,n) if len(words)<=24 or n<=3 else None
            if b and b[0]<=limit: res=b[1]; break
        if res is None:
            # greedy fallback
            res=[];cur=''
            for wd in words:
                t=(cur+' '+wd).strip()
                if lw(t)>limit and cur: res.append(cur); cur=wd
                else: cur=t
            res.append(cur)
        out+=res
    return '\\n'.join(out)
