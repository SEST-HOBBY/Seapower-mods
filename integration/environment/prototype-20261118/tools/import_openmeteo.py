"""Optional Open-Meteo historical / forecast API sampling adapter for MNO data pipeline.
Writes source-provenanced UTC point observations, not a high-res global raster.
Do not use the free API for redistributed commercial data without checking terms.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

REGIONS = {
    # Deliberately SMALL request grids for prototyping; atmospheric grid coverage is sparse.
    'south-atlantic': (-65,-38,-75,25),
    'weddell': (-75,-54,-66,-8),
    'ross': (-81,-59,155,199),
    'indian-ocean': (-58,-16,35,105),
    'arctic': (62,84,-80,45),
}
VARIABLES = ('cloud_cover','precipitation','wind_speed_10m','wind_direction_10m','pressure_msl')

def make_grid(region: str, rows: int, cols: int):
    if rows<2 or cols<2 or rows*cols>48:raise ValueError('Station sample limit: 2..48; use GRIB pipeline for production grids')
    s,n,w,e=REGIONS[region]
    return [(round(s+(n-s)*j/(rows-1),3),round(((w+(e-w)*i/(cols-1)+180)%360)-180,3)) for j in range(rows) for i in range(cols)]

def make_url(latitude,longitude,start,end,mode):
    base='https://archive-api.open-meteo.com/v1/archive' if mode=='archive' else 'https://api.open-meteo.com/v1/forecast'
    params={'latitude':latitude,'longitude':longitude,'hourly':','.join(VARIABLES),
            'wind_speed_unit':'ms','cell_selection':'sea','timezone':'UTC'}
    if mode=='archive':params.update({'start_date':start,'end_date':end})
    else:params.update({'start_date':start,'end_date':end})
    return base+'?'+urllib.parse.urlencode(params)

def parse_response(payload,lat,lon,mode):
    """Normalises the API units, flags missing rather than inventing values."""
    if payload.get('error'):raise ValueError('Open-Meteo error: '+str(payload.get('reason')))
    hour=payload.get('hourly',{})
    times=hour.get('time')
    if not isinstance(times,list) or not times:raise ValueError('missing hourly timestamps')
    units=payload.get('hourly_units',{})
    expected={'wind_speed_10m':'m/s','pressure_msl':'hPa','precipitation':'mm','cloud_cover':'%','wind_direction_10m':'°'}
    for key in VARIABLES:
        if len(hour.get(key,[]))!=len(times):raise ValueError(f'{key} lacks aligned timestamp values')
        if units.get(key)!=expected[key]:raise ValueError(f'{key} unexpected unit {units.get(key)}; expected {expected[key]}')
    readings=[]
    for i,t in enumerate(times):
        values={}
        for field in VARIABLES:
            x=hour[field][i]
            values[field]=float(x) if x is not None and math.isfinite(float(x)) else None
        readings.append({'source_time_utc':t+'Z' if len(t)==16 else t,'values':values})
    return {'request_lat':lat,'request_lon':lon,'source_grid_lat':payload.get('latitude'),'source_grid_lon':payload.get('longitude'),
            'readings':readings}

def convert(payloads,mode,start,end,region):
    return {'schema':'mno.env.observations.v0.1',
            'source':{'provider':'Open-Meteo Historical Weather API' if mode=='archive' else 'Open-Meteo Forecast API',
                      'mode':'historical_reanalysis' if mode=='archive' else 'latest_forecast',
                      'request_start_date':start,'request_end_date':end,'region':region,
                      'licence_warning':'Confirm Open-Meteo API access and downstream redistribution/commercial terms before shipping any data',
                      'attribution':'https://open-meteo.com/',
                      'notes':'sparse samples only; not globally gridded and not a ship-routing product'},
            'stations':payloads}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=('archive','forecast'),default='archive')
    p.add_argument('--start',default=None)
    p.add_argument('--end',default=None)
    p.add_argument('--region',choices=sorted(REGIONS),default='south-atlantic')
    p.add_argument('--rows',type=int,default=3)
    p.add_argument('--cols',type=int,default=4)
    p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'data'/'openmeteo_observations.json')
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    if a.start is None: a.start = '2025-09-14' if a.mode=='archive' else dt.datetime.now(dt.timezone.utc).date().isoformat()
    if a.end is None: a.end = '2025-09-16' if a.mode=='archive' else (dt.date.fromisoformat(a.start)+dt.timedelta(days=3)).isoformat()
    if dt.date.fromisoformat(a.end)<dt.date.fromisoformat(a.start):p.error('end date before start')
    points=make_grid(a.region,a.rows,a.cols)
    urls=[make_url(lat,lon,a.start,a.end,a.mode) for lat,lon in points]
    if a.dry_run:
        print('NO NETWORK REQUESTS; example API URLs:')
        for u in urls[:4]:print(u)
        print('Total locations:',len(urls),'Mode:',a.mode)
        return
    stations=[]
    for i,(location,url) in enumerate(zip(points,urls)):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'MNO-GCO-env-prototype/0.1'})
            with urllib.request.urlopen(req,timeout=30) as res:
                raw=json.load(res)
            stations.append(parse_response(raw,location[0],location[1],a.mode))
            print(i+1,'/',len(points),'retrieved',location)
        except Exception as ex:
            print('FAIL:',location,str(ex))
            raise SystemExit('Aborting rather than silently mixing incomplete location samples')
        if i<len(urls)-1:time.sleep(0.6)
    data=convert(stations,a.mode,a.start,a.end,a.region)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2),encoding='utf-8')
    print('Saved',a.output,'; point observations only. No global extrapolation performed.')
if __name__=='__main__':main()
