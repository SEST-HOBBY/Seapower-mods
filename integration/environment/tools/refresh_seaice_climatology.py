"""Recompute the sea-ice extent climatology from NSIDC Sea Ice Index (G02135) monthly CSVs.

Online (needs noaadata.apps.nsidc.org):
    python3 integration/environment/tools/refresh_seaice_climatology.py --download --cache <dir>
Offline, from CSVs already in <dir> (N_01.csv .. N_12.csv, S_01.csv .. S_12.csv):
    python3 integration/environment/tools/refresh_seaice_climatology.py --cache <dir>

Writes integration/environment/data/seaice-climatology-nsidc-g02135.json with medians for
1981-2010 (the NSIDC reference period) and 2016-2025 (the most recent ten complete years,
the default baseline for a 2028-2029 campaign), the per-file SHA-256 and the download time.
Months with a missing or zero extent (the 1987-88 data gap) are excluded.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import statistics
import urllib.request
from pathlib import Path

BASE = "https://noaadata.apps.nsidc.org/NOAA/G02135/{hemi}/monthly/data/{p}_{m:02d}_extent_v4.0.csv"
OUT = Path(__file__).resolve().parents[1] / "data" / "seaice-climatology-nsidc-g02135.json"
PERIODS = {"1981_2010": (1981, 2010), "2016_2025": (2016, 2025)}
# The only months allowed to be missing: NSIDC's December 1987 - January 1988 satellite gap.
KNOWN_GAPS = {(1987, 12), (1988, 1)}


def parse(path: Path) -> dict[int, float]:
    vals = {}
    with open(path, newline="") as fh:
        for row in csv.reader(fh):
            if row and row[0].strip().isdigit():
                v = float(row[4])
                if v > 0:
                    vals[int(row[0])] = v
    return vals


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--download", action="store_true")
    p.add_argument("--out", type=Path, default=OUT)
    a = p.parse_args(argv)
    a.cache.mkdir(parents=True, exist_ok=True)
    doc = {"schema": "mno.environment.seaice-climatology.v1", "provider": "NSIDC",
           "product": "Sea Ice Index (G02135) monthly extent, version 4.0",
           "source_url": "https://noaadata.apps.nsidc.org/NOAA/G02135/",
           "citation": "Fetterer, F., K. Knowles, W. N. Meier, M. Savoie, and A. K. Windnagel. Sea Ice Index, Version 4. NSIDC.",
           "units": "million km2 (extent: area of cells with concentration >= 15 %)",
           "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
           "files": {}, "median": {k: {} for k in PERIODS}, "years_used": {k: {} for k in PERIODS}, "latest": {}}
    for hemi, pre in (("north", "N"), ("south", "S")):
        meds = {k: [] for k in PERIODS}
        used = {k: [] for k in PERIODS}
        latest = []
        for m in range(1, 13):
            f = a.cache / f"{pre}_{m:02d}.csv"
            if a.download:
                urllib.request.urlretrieve(BASE.format(hemi=hemi, p=pre, m=m), f)
            doc["files"][f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
            vals = parse(f)
            for k, (y0, y1) in PERIODS.items():
                missing = [y for y in range(y0, y1 + 1) if y not in vals and (y, m) not in KNOWN_GAPS]
                if missing:
                    raise SystemExit(f"{f.name}: {k} lacks {missing}; not published yet or a damaged file")
                yrs = [v for y, v in vals.items() if y0 <= y <= y1]
                meds[k].append(round(statistics.median(yrs), 2))
                used[k].append(len(yrs))
            y = max(vals)
            latest.append([y, vals[y]])
        for k in PERIODS:
            doc["median"][k][hemi] = meds[k]
            doc["years_used"][k][hemi] = used[k]
        doc["latest"][hemi] = latest
    a.out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(doc["median"], indent=1))


if __name__ == "__main__":
    main()
