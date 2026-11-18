"""Layered environment: regional real tiles > global real grid > procedural fallback. BUILD-TESTED.

A campaign needs a value for every field, everywhere, at every time. Real snapshots cover a
window of days and (for regional tiles) a box; ERA5 through Open-Meteo has no sea ice. The
composite asks each real layer in order and uses its value only when the point is inside that
layer's grid and time window and the layer has the field; otherwise it falls through to the
next layer and finally to the seeded procedural field (whose sea ice follows the NSIDC
climatology). Every sample says which layer each field came from, so the UI can label data
as REAL (reanalysis/forecast) or PROCEDURAL.
"""
from __future__ import annotations

from dataclasses import dataclass

from .clock import MnoEnvState
from .geo import wrap_lon


@dataclass(frozen=True)
class CompositeSample:
    values: dict
    sources: dict   # field -> layer label


def _inside(state: MnoEnvState, lat: float, lon: float) -> bool:
    g = state.grid
    if not g.lat_min - 1e-9 <= lat <= g.lat(g.ny - 1) + 1e-9:
        return False
    if g.global_lon:
        return True
    off = wrap_lon(lon - g.lon_min) % 360.0
    return off <= (g.nx - 1) * g.lon_step + 1e-9


class MnoEnvComposite:
    def __init__(self, layers: list[tuple[str, MnoEnvState]], fallback: tuple[str, MnoEnvState]):
        self.layers = list(layers)
        self.fallback = fallback

    def sample(self, campaign_seconds: int, lat: float, lon: float, names=None) -> CompositeSample:
        fb_label, fb = self.fallback
        wanted = list(names) if names else list(dict.fromkeys([n for _, s in self.layers for n in s.fields] + fb.fields))
        values, sources = {}, {}
        for label, st in self.layers:
            todo = [n for n in wanted if n not in values and n in st.fields]
            if not todo or not _inside(st, lat, lon):
                continue
            s = st.sample(campaign_seconds, lat, lon, todo)
            if s.stale:
                continue
            for n in todo:
                if s.values[n] is not None or n.startswith("wave_"):  # no wave value over land is a real answer
                    values[n] = s.values[n]
                    sources[n] = label
        rest = [n for n in wanted if n not in values and n in fb.fields]
        if rest:
            s = fb.sample(campaign_seconds, lat, lon, rest)
            for n in rest:
                values[n] = s.values[n]
                sources[n] = fb_label
        return CompositeSample(values, sources)
