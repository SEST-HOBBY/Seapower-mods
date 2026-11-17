"""Route evaluation for GCO logistics previews. BUILD-TESTED (offline), not wired into GCO.

A route is a list of (lat, lon) waypoints. Each leg is sampled along the great circle at no
more than 10 NM. The ship advances through campaign time as it goes, so each sample reads
the environment at the time the ship would be there. Results are bounded and explained:

    hours  = sum(step_nm / (speed_kn x min(ice factor, sea factor)))
    fuel   = fuel_per_nm x distance x (1 + min(0.25, 0.5 x mean speed loss))

`blocked` is set (and evaluation stops) on land (coarse Natural Earth mask; samples within
port_radius_nm of the first or last point are exempt, since ports sit on the coast), an ice-shelf
polygon, or ice the ship's capability cannot enter. These are game-rule previews, not
navigation advice, and they change nothing in a campaign until wired and PC-tested.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .geo import default_land_mask, great_circle_nm, sample_leg
from .ice import ACCESS_SPEED, access, hs_speed_factor, nearest_berg, worst

MAX_FUEL_PENALTY = 0.25


@dataclass
class RouteResult:
    distance_nm: float = 0.0
    hours: float = 0.0
    fuel: float = 0.0
    worst_access: str = "open"
    peak_ice_pct: float = 0.0
    peak_hs_m: float = 0.0
    blocked: str | None = None
    blocked_at: tuple | None = None
    hazards: list = field(default_factory=list)
    samples: int = 0
    notes: list = field(default_factory=list)


def evaluate(points, state, depart_seconds: int, *, speed_kn: float, capability: str = "none",
             fuel_per_nm: float = 1.0, shelves=(), bergs=(), land_mask=None, max_step_nm: float = 10.0,
             port_radius_nm: float = 15.0) -> RouteResult:
    if len(points) < 2:
        raise ValueError("a route needs two or more points")
    if speed_kn <= 0:
        raise ValueError("speed must be positive")
    land = land_mask or default_land_mask()
    r = RouteResult()
    t = float(depart_seconds)
    loss_weighted = 0.0
    bergs_now = []
    if bergs:
        bergs_now = [p for p in (b.predict(state, depart_seconds) for b in bergs) if p]
    for leg, (a, b) in enumerate(zip(points, points[1:])):
        pts = sample_leg(tuple(a), tuple(b), max_step_nm)
        for k, (p0, p1) in enumerate(zip(pts, pts[1:])):
            step = great_circle_nm(p0, p1)
            for p in ((p1,) if k else (p0, p1)):
                near_port = min(great_circle_nm(p, tuple(points[0])), great_circle_nm(p, tuple(points[-1]))) <= port_radius_nm
                if land.is_land(*p) and not near_port:
                    r.blocked, r.blocked_at = "land", p
                    return r
                for s in shelves:
                    if s.contains(*p):
                        r.blocked, r.blocked_at = f"ice shelf: {s.name}", p
                        return r
            v = state.sample(int(t), p1[0], p1[1], ["sea_ice_conc_pct", "wave_hs_m"]).values if hasattr(state, "sample") else {}
            ice, hs = v.get("sea_ice_conc_pct"), v.get("wave_hs_m")
            acc = access(ice, capability) if "sea_ice_conc_pct" in v else "open"
            r.worst_access = worst(r.worst_access, acc)
            r.peak_ice_pct = max(r.peak_ice_pct, ice or 0.0)
            r.peak_hs_m = max(r.peak_hs_m, hs or 0.0)
            r.samples += 1
            if acc == "blocked":
                r.blocked, r.blocked_at = f"sea ice {ice:.0f}% beyond '{capability}' capability", p1
                return r
            factor = min(ACCESS_SPEED[acc], hs_speed_factor(hs))
            r.distance_nm += step
            r.hours += step / (speed_kn * factor)
            t += step / (speed_kn * factor) * 3600
            loss_weighted += step * (1 - factor)
            if bergs_now:
                nb = nearest_berg(p1, bergs_now)
                if nb and nb[0] <= nb[1]["hazard_radius_nm"] and nb[1]["berg_id"] not in [h["berg_id"] for h in r.hazards]:
                    r.hazards.append({"berg_id": nb[1]["berg_id"], "distance_nm": round(nb[0], 1),
                                      "hazard_radius_nm": nb[1]["hazard_radius_nm"], "at": [round(p1[0], 3), round(p1[1], 3)]})
    mean_loss = loss_weighted / r.distance_nm if r.distance_nm else 0.0
    r.fuel = fuel_per_nm * r.distance_nm * (1 + min(MAX_FUEL_PENALTY, 0.5 * mean_loss))
    r.distance_nm, r.hours, r.fuel = round(r.distance_nm, 1), round(r.hours, 2), round(r.fuel, 1)
    r.notes.append("game-rule preview; land mask is Natural Earth low resolution")
    return r
