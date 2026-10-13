import sys, re, math
def gc(a,b):
    la1,lo1=map(math.radians,a); la2,lo2=map(math.radians,b)
    d=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 2*math.asin(math.sqrt(min(1,d)))*3440.065
for path in sys.argv[1:]:
    sec=None; pts={}; centre=[None,None]
    with open(path,encoding='utf-8',errors='replace') as f:
        for line in f:
            if line.startswith('[PlottingTable]'): sec='PT'; continue
            if line.startswith('['): sec=line.strip()[1:-1]; continue
            if line.startswith('Payload='): continue
            if line.startswith('MapCenterLatitude='): centre[0]=float(line.split('=')[1])
            if line.startswith('MapCenterLongitude='): centre[1]=float(line.split('=')[1])
            m=re.match(r'GeoPosition=([-\d.]+),([-\d.]+)',line)
            if m and sec and re.match(r'(Taskforce\d|Neutral)(LandUnit|Vessel|Submarine|Aircraft|Helicopter|Biologic)\d+$',sec):
                pts[sec]=(float(m.group(1)),float(m.group(2)))
    P=list(pts.values())
    mx=0;pair=None
    for i in range(len(P)):
        for j in range(i+1,len(P)):
            d=gc(P[i],P[j])
            if d>mx: mx=d;pair=(P[i],P[j])
    dc=[gc(tuple(centre),p) for p in P]
    print(path.split('/')[-1], 'units',len(P),'centre',centre,'maxspread %.0f'%mx,pair,'dist-from-centre min %.0f max %.0f'%(min(dc),max(dc)))
