"""Layered environment: regional real tiles > global real grid > procedural fallback. BUILD-TESTED.

A campaign needs a value for every field, everywhere, at every time. Real snapshots cover a
window of days and (for regional tiles) a box; ERA5 through Open-Meteo has no sea ice. The
composite asks each real layer in order, finest first. Where a layer covers the point and time
it is used; where it does not, the next layer is used, and finally the seeded procedural field
(whose sea ice follows the NSIDC climatology).

Seams are feathered so weather does not jump: inside the outer `feather_deg` of a regional
tile, and in the last `feather_h` hours of a layer's time window, the layer's value is blended
linearly with the value from the layers beneath it. Every sample reports, per field, the layer
that contributed most, so the UI can label data as REAL (reanalysis/forecast) or PROCEDURAL.
"""
from __future__ import annotations

from dataclasses import dataclass

from .clock import MnoEnvState
from .geo import wrap_lon

DIRECTIONAL = {"wave_dir_deg"}   # never averaged linearly
NO_VALUE_IS_ANSWER = ("wave_",)  # no wave value over land is a real answer, not a gap


@dataclass(frozen=True)
class CompositeSample:
    values: dict
    sources: dict   # field -> layer label with the largest weight


def _edge_weight(state: MnoEnvState, lat: float, lon: float, feather_deg: float) -> float:
    """1 well inside the layer's grid, falling linearly to 0 at its border; 0 outside."""
    g = state.grid
    lat_hi = g.lat(g.ny - 1)
    if not g.lat_min - 1e-9 <= lat <= lat_hi + 1e-9:
        return 0.0
    d = min(lat - g.lat_min, lat_hi - lat)
    if not g.global_lon:
        off = wrap_lon(lon - g.lon_min) % 360.0
        span = (g.nx - 1) * g.lon_step
        if off > span + 1e-9:
            return 0.0
        d = min(d, off, span - off)
    if feather_deg <= 0:
        return 1.0
    return max(0.0, min(1.0, d / feather_deg))


def _time_weight(state: MnoEnvState, campaign_seconds: int, feather_s: float) -> float:
    """1 inside the layer's window, falling to 0 over its last feather_s seconds (a handover to
    the coarser layer beneath); 0 outside the window."""
    src = campaign_seconds - state.offset
    first, last = state.frame_seconds[0], state.frame_seconds[-1]
    if src < first or src > last:
        return 0.0
    if feather_s <= 0:
        return 1.0
    return max(0.0, min(1.0, (last - src) / feather_s))


class MnoEnvComposite:
    def __init__(self, layers: list, fallback: tuple[str, object], feather_deg: float = 1.0, feather_h: float = 12.0):
        """layers: (label, state) or (label, state, feather_space, feather_time), finest first.
        Feathering is off unless asked for: contiguous chunks of one dataset need none."""
        self.layers = [(l[0], l[1], *(l[2:4] if len(l) >= 4 else (False, False))) for l in layers]
        self.fallback = fallback
        self.feather_deg = feather_deg
        self.feather_s = feather_h * 3600.0

    def _layer_weight(self, i: int, campaign_seconds: int, lat: float, lon: float) -> float:
        label, st, f_space, f_time = self.layers[i]
        w = _edge_weight(st, lat, lon, self.feather_deg if f_space else 0.0)
        if w == 0.0:
            return 0.0
        return w * _time_weight(st, campaign_seconds, self.feather_s if f_time else 0.0)

    def _value(self, i: int, campaign_seconds: int, lat: float, lon: float, name: str):
        """(value, {label: weight}) from layer i downwards."""
        if i >= len(self.layers):
            label, fb = self.fallback
            if name not in fb.fields:
                return None, {}
            return fb.sample(campaign_seconds, lat, lon, [name]).values[name], {label: 1.0}
        label, st = self.layers[i][:2]
        w = self._layer_weight(i, campaign_seconds, lat, lon) if name in st.fields else 0.0
        if w <= 0.0:
            return self._value(i + 1, campaign_seconds, lat, lon, name)
        mine = st.sample(campaign_seconds, lat, lon, [name]).values[name]
        if mine is None and not name.startswith(NO_VALUE_IS_ANSWER):
            return self._value(i + 1, campaign_seconds, lat, lon, name)
        if w >= 1.0 or mine is None or name in DIRECTIONAL:
            if w >= 0.5 or mine is None:
                return mine, {label: 1.0}
            return self._value(i + 1, campaign_seconds, lat, lon, name)
        below, src = self._value(i + 1, campaign_seconds, lat, lon, name)
        if below is None:
            return mine, {label: 1.0}
        mix = {k: v * (1 - w) for k, v in src.items()}
        mix[label] = mix.get(label, 0.0) + w
        return round(w * mine + (1 - w) * below, 4), mix

    def sample(self, campaign_seconds: int, lat: float, lon: float, names=None) -> CompositeSample:
        fb = self.fallback[1]
        wanted = list(names) if names else list(dict.fromkeys([n for l in self.layers for n in l[1].fields] + list(fb.fields)))
        values, sources = {}, {}
        for n in wanted:
            v, mix = self._value(0, campaign_seconds, lat, lon, n)
            values[n] = v
            if mix:
                sources[n] = max(mix.items(), key=lambda kv: kv[1])[0]
        return CompositeSample(values, sources)
