"""One-time source extraction from Natural Earth lowres, included in local pyogrio test data.
Natural Earth public-domain coastline outlines; runtime viewer does not depend on pyogrio.
"""
import json
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
src=Path('/opt/pyvenv/lib/python3.13/site-packages/pyogrio/tests/fixtures/naturalearth_lowres/naturalearth_lowres.shp')
out=Path(__file__).resolve().parents[1]/'data'/'coastlines.json'
if not src.exists(): raise SystemExit('Natural Earth source not available')
gdf=gpd.read_file(src)
lines=[]
for geo in gdf.geometry:
    if geo is None: continue
    polys=[geo] if isinstance(geo,Polygon) else list(geo.geoms) if isinstance(geo,MultiPolygon) else []
    for poly in polys:
        pts=[[round(x,2),round(y,2)] for x,y in poly.simplify(0.25,preserve_topology=True).exterior.coords]
        if len(pts)>3: lines.append(pts)
out.write_text(json.dumps({'source':'Natural Earth lowres (public domain); pyogrio fixture','polygons':lines},separators=(',',':')))
print(out,'polygons:',len(lines))
