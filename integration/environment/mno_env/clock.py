"""MnoEnvClock and MnoEnvState: campaign-UTC sampling of a snapshot. BUILD-TESTED.

Rules (environment rules version in mno_env.RULES_VERSION):
- Campaign UTC, as whole seconds since 1970-01-01T00:00:00Z, is the only simulation clock.
  The PC wall clock is never read here.
- The source time for a campaign time is campaign_time - offset_seconds (an analogue
  mapping). For historical replay, `analogue_offset()` builds the offset so that the
  calendar date and time of day line up; 29 February in a leap campaign year (2028) maps to
  28 February of a non-leap source year.
- Between two frames, scalar fields interpolate linearly with an exact rational weight;
  categorical fields (sea_ice_type_code) take the earlier frame. Outside the frames the
  value holds at the nearest frame and the sample is flagged stale.
- Results round to 4 decimals so that two machines produce the same bytes.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import dataclass, field
from fractions import Fraction

from .grid import LatLonGrid, bilinear
from .snapshot import field_values, utc

EPOCH = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
CATEGORICAL = {"sea_ice_type_code"}
EXTINCTION = {"visibility_km"}  # interpolated as 1/visibility (extinction), not linearly
EXT_MIN_VIS_KM = 0.05


def to_seconds(t: dt.datetime) -> int:
    if t.tzinfo is None:
        raise ValueError("campaign time must be timezone-aware UTC")
    delta = t.astimezone(dt.timezone.utc) - EPOCH
    if delta.microseconds:
        raise ValueError("campaign time must be whole seconds")
    return delta.days * 86400 + delta.seconds


def from_seconds(s: int) -> dt.datetime:
    return EPOCH + dt.timedelta(seconds=int(s))


def analogue_source_time(campaign: dt.datetime, source_year: int) -> dt.datetime:
    """Same month, day and time of day in source_year (29 Feb -> 28 Feb if needed)."""
    day = campaign.day
    if campaign.month == 2 and day == 29:
        try:
            dt.date(source_year, 2, 29)
        except ValueError:
            day = 28
    return campaign.replace(year=source_year, day=day)


def analogue_offset(campaign_start: dt.datetime, source_year: int) -> int:
    """Fixed offset (seconds) that maps the campaign start onto the same calendar instant
    in source_year. The offset then stays fixed for the whole campaign, so time runs
    continuously (a campaign that crosses 29 Feb 2028 stays one day ahead afterwards)."""
    return to_seconds(campaign_start) - to_seconds(analogue_source_time(campaign_start, source_year))


@dataclass
class MnoEnvClock:
    """Campaign clock. advance() and set() are the only mutators; preview() never mutates."""

    campaign_seconds: int
    paused: bool = False
    history: list = field(default_factory=list)

    def advance(self, seconds: int) -> int:
        if seconds < 0:
            raise ValueError("campaign time does not run backwards; load a save instead")
        if not self.paused:
            self.campaign_seconds += int(seconds)
        return self.campaign_seconds

    def set(self, seconds: int, reason: str) -> None:
        """Used only by save loading; recorded so a reload is auditable."""
        self.history.append((self.campaign_seconds, int(seconds), reason))
        self.campaign_seconds = int(seconds)

    def preview(self, ahead_seconds: int) -> int:
        """Time to show in a forecast scrub. Pure: does not change the campaign clock."""
        if ahead_seconds < 0:
            raise ValueError("forecast scrub looks ahead only")
        return self.campaign_seconds + int(ahead_seconds)


@dataclass(frozen=True)
class Sample:
    values: dict
    frame_before: int
    frame_after: int
    weight: Fraction
    stale: bool
    source_seconds: int


class MnoEnvState:
    """Read-only view of one validated snapshot under one campaign mapping."""

    def __init__(self, snapshot: dict, offset_seconds: int | None = None):
        self.snapshot = snapshot
        self.grid = LatLonGrid.from_dict(snapshot["grid"])
        self.offset = snapshot["campaign_mapping"]["offset_seconds"] if offset_seconds is None else int(offset_seconds)
        self.frame_seconds = [to_seconds(utc(f["valid_utc"])) for f in snapshot["times"]]
        self.fields = list(snapshot["fields"])
        self._cache: dict = {}

    def _values(self, frame: int, name: str):
        key = (frame, name)
        if key not in self._cache:
            if len(self._cache) > 64:  # bounded: about 64 decoded slices at most
                self._cache.clear()
            self._cache[key] = field_values(self.snapshot, frame, name)
        return self._cache[key]

    def bracket(self, source_seconds: int) -> tuple[int, int, Fraction, bool]:
        fs = self.frame_seconds
        if source_seconds <= fs[0]:
            return 0, 0, Fraction(0), source_seconds < fs[0]
        if source_seconds >= fs[-1]:
            return len(fs) - 1, len(fs) - 1, Fraction(0), source_seconds > fs[-1]
        lo, hi = 0, len(fs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if fs[mid] <= source_seconds:
                lo = mid
            else:
                hi = mid
        return lo, hi, Fraction(source_seconds - fs[lo], fs[hi] - fs[lo]), False

    def _extinction(self, frame: int, name: str):
        """Visibility as extinction (1/km), so interpolation keeps fog instead of averaging it away."""
        key = (frame, name, "ext")
        if key not in self._cache:
            self._cache[key] = [None if v is None else 1.0 / max(EXT_MIN_VIS_KM, v) for v in self._values(frame, name)]
        return self._cache[key]

    def sample(self, campaign_seconds: int, lat: float, lon: float, names=None) -> Sample:
        src = int(campaign_seconds) - self.offset
        a, b, w, stale = self.bracket(src)
        out = {}
        for name in names or self.fields:
            fill = self.snapshot["fields"][name].get("fill_value")
            ext = name in EXTINCTION
            get = self._extinction if ext else self._values
            va = bilinear(self.grid, get(a, name), lat, lon, None if ext else fill)
            if name in CATEGORICAL or b == a or w == 0:
                v = va
            else:
                vb = bilinear(self.grid, get(b, name), lat, lon, None if ext else fill)
                v = None if va is None or vb is None else va + float(w) * (vb - va)
            if ext and v is not None:
                v = min(100.0, 1.0 / max(1e-6, v))
            out[name] = None if v is None else round(v, 4)
        return Sample(out, a, b, w, stale, src)


def digest_samples(samples) -> str:
    """Stable digest of a sequence of Samples (for replay/fast-forward determinism proofs)."""
    h = hashlib.sha256()
    for s in samples:
        h.update(json.dumps([s.source_seconds, s.frame_before, s.frame_after, str(s.weight), s.stale, s.values],
                            sort_keys=True, separators=(",", ":")).encode())
    return h.hexdigest()
