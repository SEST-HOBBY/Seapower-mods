import os,re,math,sys,collections
ROOT=sys.argv[1]
anchors={'Yulin':(18.22,109.55),'Guam':(13.5,144.8),'Kola':(69.1,33.4),'Bodo':(67.27,14.36),'DiegoGarcia':(-7.31,72.41),'Djibouti':(11.6,43.15),'Souda':(35.49,24.12)}
def gc(a,b):
    la1,lo1=map(math.radians,a);la2,lo2=map(math.radians,b)
    d=math.acos(min(1,math.sin(la1)*math.sin(la2)+math.cos(la1)*math.cos(la2)*math.cos(lo1-lo2)))
    return math.degrees(d)*60
hits=collections.defaultdict(list)
for r,_,fs in os.walk(ROOT):
  for f in fs:
    if not f.endswith('.ini'):continue
    p=os.path.join(r,f);clat=clon=None;sec=None;typ=None;tline=0
    lines=open(p,encoding='utf-8',errors='replace').read().splitlines()
    for l in lines:
        if l.startswith('MapCenterLatitude='):clat=float(l.split('=')[1].split()[0])
        if l.startswith('MapCenterLongitude='):clon=float(l.split('=')[1].split()[0])
    if clat is None:continue
    for i,l in enumerate(lines,1):
        m=re.match(r'\[((Taskforce\d|Neutral)(LandUnit|Vessel|Submarine|Aircraft|Helicopter)\d+)\]',l)
        if m:sec=m.group(1);kind=m.group(3);typ=None;continue
        if l.startswith('['):sec=None
        if sec and l.startswith('Type='):typ=l.split('=',1)[1].strip();tline=i
        if sec and re.match(r'RelativePositionIn[Nn][Mm]=',l):
            v=l.split('=',1)[1].split('/')[0].split(',')
            try:x=float(v[0]);z=float(v[2])
            except:continue
            lat=clat+z/60;lon=clon+x/60
            for k,a in anchors.items():
                d=gc((lat,lon),a)
                if d<60:hits[k].append((round(d),kind,typ,os.path.relpath(p,ROOT)+':'+str(tline)))
for k,v in hits.items():
    c=collections.Counter((h[1],h[2]) for h in v)
    print(k,len(v));
    for (kind,t),n in c.most_common(8):
        ex=[h[3] for h in v if h[2]==t][0]
        print('   ',kind,t,n,ex)
