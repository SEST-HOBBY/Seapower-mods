"""Measure the procedural weather against the climatology targets of the v4 critique.

    python3 integration/environment/tools/measure_procedural_climate.py alpha,bravo,charlie

Needs numpy. Prints model value and reference per metric (ocean cells, 4-degree grid)."""
import sys, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from multiprocessing import Pool
from mno_env import procedural as P, seaice
from mno_env.grid import LatLonGrid
U = dt.timezone.utc
RES = 4.0
G = LatLonGrid(-180.0, -90.0, RES, RES, int(360 / RES), int(180 / RES) + 1)
LAT = np.array([G.lat(j) for j in range(G.ny)]); LON = np.array([G.lon(i) for i in range(G.nx)])
FIELDS = ["msl_pressure_hpa", "wind_u10_ms", "wind_v10_ms", "cloud_fraction_pct", "precip_rate_mm_h", "air_temp_2m_c", "wave_hs_m", "sea_ice_conc_pct"]
SEEDS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["alpha", "bravo", "charlie"]
MONTHS = [1, 4, 7, 10, 2, 8, 9, 3]

def one(args):
    seed, t = args
    out = P._frame(seed, t, G, seaice.edges_on(t, res=RES), P._hours(t) / 6.0)
    return (seed, t.month, np.array([out[f] for f in FIELDS], dtype=np.float32).reshape(len(FIELDS), G.ny, G.nx))

if __name__ == "__main__":
    jobs = [(s, dt.datetime(2029, m, d, h, tzinfo=U)) for s in SEEDS for m in MONTHS for d in (2, 9, 16, 23) for h in (0, 12)]
    with Pool(8) as pool:
        res = pool.map(one, jobs)
    lf = np.array(P._land_nodes(G)).reshape(G.ny, G.nx)
    ocean = ~lf
    by = {m: np.stack([r[2] for r in res if r[1] == m]) for m in MONTHS}
    I = {f: k for k, f in enumerate(FIELDS)}
    def box(m, f, la0, la1, lo0, lo1, fn=np.mean, mask=None):
        a = by[m][:, I[f]]
        rows = (LAT >= la0) & (LAT <= la1)
        lo = LON % 360
        if lo0 <= lo1: cols = (LON >= lo0) & (LON <= lo1)
        else: cols = (LON >= lo0) | (LON <= lo1)
        sel = np.zeros((G.ny, G.nx), bool); sel[np.ix_(rows, cols)] = True; sel &= ocean
        if mask is not None: sel &= mask
        return float(fn(a[:, sel]))
    def zon(m, f, lat, fn=np.mean):
        j = int(np.argmin(abs(LAT - lat)))
        return float(fn(by[m][:, I[f], j, ocean[j]]))
    mmd = 24
    R = {}
    R["rain mm/d zonal ocean Jan 2N/6N/10N"] = [round(zon(1, "precip_rate_mm_h", x) * mmd, 1) for x in (2, 6, 10)] , "ITCZ 6-10"
    R["rain mm/d zonal ocean Jul 6N/10N/14N"] = [round(zon(7, "precip_rate_mm_h", x) * mmd, 1) for x in (6, 10, 14)], "ITCZ 6-10"
    R["rain mm/d zonal ocean Jan 42/46/50N"] = [round(zon(1, "precip_rate_mm_h", x) * mmd, 1) for x in (42, 46, 50)], "~5-6 (3-4 zonal 40-60)"
    R["rain mm/d zonal ocean Jul 46/50N"] = [round(zon(7, "precip_rate_mm_h", x) * mmd, 1) for x in (46, 50)], "2-3"
    R["rain mm/d zonal ocean Jan/Jul 46/50S"] = [round(zon(m, "precip_rate_mm_h", x) * mmd, 1) for m in (1, 7) for x in (-46, -50)], "3-4"
    R["rain NPac 40-52N 160E-140W Jan"] = round(box(1, "precip_rate_mm_h", 40, 52, 160, -140) * mmd, 1), "5-7"
    R["rain Azores 30-40N 40-20W Jan"] = round(box(1, "precip_rate_mm_h", 30, 40, -40, -20) * mmd, 1), "2-3"
    R["wet frac 44-56N ocean Jan (>0.1mm/h)"] = round(box(1, "precip_rate_mm_h", 44, 56, -180, 180, fn=lambda a: (a > 0.1).mean()), 2), "0.2-0.4"
    R["rain SPCZ 8-20S 160E-150W Jan/Jul"] = [round(box(m, "precip_rate_mm_h", -20, -8, 160, -150) * mmd, 1) for m in (1, 7)], "6-9 / 4-5"
    R["rain warm pool 10S-10N 95-150E Jan/Jul"] = [round(box(m, "precip_rate_mm_h", -10, 10, 95, 150) * mmd, 1) for m in (1, 7)], "8-10"
    R["rain SE Pac 10-20S 120-90W Jan"] = round(box(1, "precip_rate_mm_h", -20, -10, -120, -90) * mmd, 2), "0.5-2"
    R["rain BoB 8-20N 82-95E Jul"] = round(box(7, "precip_rate_mm_h", 8, 20, 82, 95) * mmd, 1), "10-15"
    allr = np.mean([np.average(by[m][:, I["precip_rate_mm_h"]][:, ocean & (by[m][:, I["sea_ice_conc_pct"]].mean(0) < 15)].mean(0)) for m in (1, 4, 7, 10)]) * mmd
    R["ocean mean rain mm/d"] = round(float(allr), 2), "2.9-3.0"
    for m in (1, 7):
        R[f"u10 zonal ocean m{m} 38/42/46/50/54/58S"] = [round(zon(m, "wind_u10_ms", -x), 1) for x in (38, 42, 46, 50, 54, 58)], "peak 8-9 at 50-52S, ~7 at 58S"
    R["MSLP zonal ocean 62-66S Jan/Jul"] = [round(zon(m, "msl_pressure_hpa", -64), 1) for m in (1, 7)], "985-988"
    R["MSLP std 60S / 50S Jul"] = [round(float(np.mean(by[7][:, I["msl_pressure_hpa"], int(np.argmin(abs(LAT + x)))].std(0))), 1) for x in (60, 50)], "~10"
    R["MSLP zonal ocean 30S Jan/Jul"] = [round(zon(m, "msl_pressure_hpa", -30), 1) for m in (1, 7)], "1016-18 / 1020-22"
    R["Arabian Sea Jul U,V,spd,Hs"] = [round(box(7, f, 8, 20, 55, 72), 1) for f in ("wind_u10_ms", "wind_v10_ms")] + [round(box(7, "wave_hs_m", 8, 20, 55, 72), 1)], "U +8-10, V +3-5, Hs 3-4"
    R["BoB Jul U,V"] = [round(box(7, f, 8, 20, 82, 95), 1) for f in ("wind_u10_ms", "wind_v10_ms")], "U +6-8"
    R["Timor Sea Jan u (5-15S 110-140E)"] = round(box(1, "wind_u10_ms", -15, -5, 110, 140), 1), "+3-5"
    R["MSLP zonal ocean Jan 50/54/58/62N"] = [round(zon(1, "msl_pressure_hpa", x), 1) for x in (50, 54, 58, 62)], "1004-08 at 50N, min near 60"
    R["MSLP 32W Jan 38/46/54/62N"] = [round(box(1, "msl_pressure_hpa", x - 2, x + 2, -36, -28), 1) for x in (38, 46, 54, 62)], "min 58-64N ~997-1003; 46N ~1012+"
    R["Aleutian 48-60N 160E-150W Jan/Jul"] = [round(box(m, "msl_pressure_hpa", 48, 60, 160, -150), 1) for m in (1, 7)], "1000-02 / 1009-12"
    R["Azores 30-40N 40-20W Jan P"] = round(box(1, "msl_pressure_hpa", 30, 40, -40, -20), 1), "1020-22"
    R["NAtl 60W-10W Jan u 46/54/62N"] = [round(box(1, "wind_u10_ms", x - 2, x + 2, -60, -10), 1) for x in (46, 54, 62)], "positive 5-8"
    R["45N30W Jan P, Hs"] = [round(box(1, f, 43, 47, -34, -26), 1) for f in ("msl_pressure_hpa", "wave_hs_m")], "1015 / 3.5-4"
    ice = {m: by[m][:, I["sea_ice_conc_pct"]] for m in MONTHS}
    hs80 = np.concatenate([by[m][:, I["wave_hs_m"]][ice[m] >= 80] for m in MONTHS])
    R["Hs under ice>=80: median,max"] = [round(float(np.median(hs80)), 2), round(float(hs80.max()), 2)], "~0"
    R["cloud zonal ocean 26S/22S/26N/30N (Jan)"] = [round(zon(1, "cloud_fraction_pct", x)) for x in (-26, -22, 26, 30)], "50-60"
    R["cloud SE Pac Sc 10-20S 120-90W / 25-35S 110-90W Jul"] = [round(box(7, "cloud_fraction_pct", -20, -10, -120, -90)), round(box(7, "cloud_fraction_pct", -35, -25, -110, -90))], "70-80"
    R["cloud zonal ocean 50-58N / 54-62S Jan"] = [round(zon(1, "cloud_fraction_pct", 54)), round(zon(1, "cloud_fraction_pct", -58))], "80-90 / 85-90"
    cl = np.mean([by[m][:, I["cloud_fraction_pct"]][:, ocean].mean() for m in (1, 4, 7, 10)])
    R["global ocean cloud (unweighted)"] = round(float(cl), 1), "68-70"
    R["cloud std 45N30W Jan"] = round(float(by[1][:, I["cloud_fraction_pct"], int(np.argmin(abs(LAT - 44))), int(np.argmin(abs(LON + 32)))].std()), 1), "20-25"
    R["u10 zonal ocean Jul 2S/10S/14S/18S/22S"] = [round(zon(7, "wind_u10_ms", -x), 1) for x in (2, 10, 14, 18, 22)], "-3..-5 eq; one max 6-7 at 10-18S"
    R["warm pool u Jan/Jul"] = [round(box(m, "wind_u10_ms", -10, 10, 95, 150), 1) for m in (1, 7)], "|u|<2-3"
    R["v10 zonal ocean 42N/44N Jan, 42S Jul"] = [round(zon(1, "wind_v10_ms", 42), 1), round(zon(1, "wind_v10_ms", 46), 1), round(zon(7, "wind_v10_ms", -42), 1)], "|v|<=1.2"
    spd = {m: np.hypot(by[m][:, I["wind_u10_ms"]], by[m][:, I["wind_v10_ms"]]) for m in MONTHS}
    def bspd(m, la0, la1, fn=np.mean):
        rows = (LAT >= la0) & (LAT <= la1)
        sel = np.zeros((G.ny, G.nx), bool); sel[rows] = True; sel &= ocean
        return float(fn(spd[m][:, sel]))
    R["SO 45-60S scalar wind Jan/Jul"] = [round(bspd(m, -60, -45), 1) for m in (1, 7)], "9-11 / 11-12"
    R["NH 40-60N scalar wind Jan"] = round(bspd(1, 40, 60), 1), "10-11"
    R["30S calm frac(<2) / mean"] = [round(bspd(m, -30, -30, lambda a: (a < 2).mean()), 2) for m in (1, 7)] + [round(bspd(1, -30, -30), 1)], "0.05-0.1 / 5-6"
    allspd = np.concatenate([spd[m][:, ocean & (ice[m].mean(0) < 15)].ravel() for m in (1, 4, 7, 10)])
    R["global ocean wind mean / frac<2"] = [round(float(allspd.mean()), 2), round(float((allspd < 2).mean()), 3)], "7.3-7.5 / ~0.05"
    hs = np.concatenate([by[m][:, I["wave_hs_m"]][:, ocean & (ice[m].mean(0) < 15)].ravel() for m in (1, 4, 7, 10)])
    R["ocean Hs median/p99"] = [round(float(np.median(hs)), 2), round(float(np.percentile(hs, 99)), 1)], "~2 / ~7"
    R["row speed 82/86/90N (mean)"] = [round(float(spd[1][:, int(np.argmin(abs(LAT - x)))].mean()), 1) for x in (82, 86, 90)], "smooth"
    def pt(m, f, la, lo):
        return round(float(by[m][:, I[f], int(np.argmin(abs(LAT - la))), int(np.argmin(abs(LON - lo)))].mean()), 1)
    R["T Arctic Aug 84N150W / 88N"] = [pt(8, "air_temp_2m_c", 84, -150), pt(8, "air_temp_2m_c", 88, 0)], "-1..0"
    R["T North Pole Feb"] = pt(2, "air_temp_2m_c", 90, 0), "-30..-35"
    R["T 45N30W Sep/Feb"] = [pt(9, "air_temp_2m_c", 44, -32), pt(2, "air_temp_2m_c", 44, -32)], "19 / 13-14"
    R["T 26N56E Sep/Jan"] = [pt(9, "air_temp_2m_c", 26, 56), pt(1, "air_temp_2m_c", 26, 56)], "32-34 / 22-24"
    R["T 15N140E Sep/Feb"] = [pt(9, "air_temp_2m_c", 16, 140), pt(2, "air_temp_2m_c", 16, 140)], "28.5 / 26-27"
    R["T 55N165W Sep/Jan"] = [pt(9, "air_temp_2m_c", 56, -164), pt(1, "air_temp_2m_c", 56, -164)], "8-9 / 0"
    R["T 65S summer Jan / winter Jul"] = [round(zon(1, "air_temp_2m_c", -66), 1), round(zon(7, "air_temp_2m_c", -66), 1)], "~0 / -10..-15"
    for k, (v, tgt) in R.items():
        print(f"{k:48s} {str(v):40s} target {tgt}")
