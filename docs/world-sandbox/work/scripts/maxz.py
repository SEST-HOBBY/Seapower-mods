import sys,os,re
res=[]
for root in sys.argv[1:]:
    for dp,dn,fn in os.walk(root):
        for f in fn:
            if not f.endswith('.ini'): continue
            p=os.path.join(dp,f)
            try: txt=open(p,encoding='utf-8',errors='replace').read()
            except: continue
            if 'MapCenterLatitude' not in txt: continue
            mz=0;mx=0;lz=None;lx=None
            for i,line in enumerate(txt.splitlines(),1):
                m=re.match(r'RelativePositionInNM=([-\d.]+),[^,]*,([-\d.]+)',line)
                if m:
                    x=abs(float(m.group(1)));z=abs(float(m.group(2)))
                    if z>mz: mz=z;lz=i
                    if x>mx: mx=x;lx=i
            res.append((mz,lz,mx,lx,p))
res.sort(reverse=True)
for r in res[:8]: print('maxz %.0f @%s  maxx %.0f @%s  %s'%r)
print('---by x')
res.sort(key=lambda r:-r[2])
for r in res[:5]: print('maxz %.0f @%s  maxx %.0f @%s  %s'%r)
