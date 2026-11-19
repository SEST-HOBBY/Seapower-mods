"""MnoEnvMissionAdapter: environment sample -> native Sea Power mission weather. BUILD-TESTED.

The conversions below are DOCUMENTED HEURISTICS, not calibrations. Sea Power's SeaState
accepts 0-12 (MissionFileInformation.ini), which is not the WMO 0-9 sea-state code; nobody
has yet measured which wave height the game draws for each value. Until a PC test records
that (ENV-PC-PLAYTEST.md, test W5), `sea_state_from_hs` uses the WMO code 3700 bands for 0-9
and never writes 10-12. Nothing here changes unit speed, sensors or damage.
"""
from __future__ import annotations

import dataclasses
import math

from .mission_ini import CLOUDS, WIND_DIRECTIONS, WeatherState, patch

# WMO code table 3700 (state of the sea): upper bound of significant wave height, metres.
WMO_3700_UPPER_M = [0.0, 0.1, 0.5, 1.25, 2.5, 4.0, 6.0, 9.0, 14.0]
RAIN_MM_H = 0.2         # measurable rain (WMO "light" starts at a trace; 0.2 avoids drizzle noise)
SNOW_TEMP_C = 0.5       # precipitation at or below this 2 m temperature is shown as snow
STORM_RISK = 0.6        # derived convective risk needed for a thunderstorm stage (plus Overcast)
FOG_VIS_KM = 1.0        # WMO fog definition: visibility below 1 km
FOG_MAX_PRECIP_MM_H = 0.5  # heavier precipitation explains low visibility: rain or snow, not fog
FOG_MAX_WIND_MS = 13.0     # fog does not persist in a gale
FOG_HOLD_SAMPLES = 2       # after the start, Fog changes only when the new value holds this many samples


def sea_state_from_hs(hs_m: float | None) -> int:
    if hs_m is None:
        return 4  # the game's documented default
    for code, upper in enumerate(WMO_3700_UPPER_M):
        if hs_m <= upper:
            return code
    return 9


def clouds_from_fraction(pct: float | None) -> str:
    """Oktas = round(fraction x 8); 0 Clear ... 7-8 Overcast. The game's cloud presets are
    named, not measured, so the order is the only thing relied on."""
    if pct is None:
        return "Scattered"
    oktas = max(0, min(8, round(pct / 100 * 8)))
    return CLOUDS[min(oktas, 7)]


def wind_direction(u: float | None, v: float | None) -> str | None:
    """Direction the wind blows FROM, to the nearest of the eight points."""
    if u is None or v is None or math.hypot(u, v) < 0.5:
        return None
    frm = (math.degrees(math.atan2(-u, -v)) + 360) % 360
    return WIND_DIRECTIONS[int((frm + 22.5) // 45) % 8]


def snowing(values: dict) -> bool:
    """Precipitation falling as snow: the snowfall field when present (at least half the
    precipitation), otherwise air temperature at or below SNOW_TEMP_C."""
    rate = values.get("precip_rate_mm_h") or 0.0
    if rate < RAIN_MM_H:
        return False
    sf = values.get("snowfall_rate_mm_h")
    if sf is not None:
        return sf >= 0.5 * rate
    temp = values.get("air_temp_2m_c")
    return temp is not None and temp <= SNOW_TEMP_C


def foggy(values: dict) -> bool:
    """Fog is visibility below 1 km that is not explained by precipitation, in light enough wind
    for fog to persist (judged on the final, possibly mixed-source values)."""
    vis = values.get("visibility_km")
    if vis is None or vis >= FOG_VIS_KM:
        return False
    rate = values.get("precip_rate_mm_h") or 0.0
    u, v = values.get("wind_u10_ms"), values.get("wind_v10_ms")
    wind = math.hypot(u, v) if u is not None and v is not None else 0.0
    return rate < FOG_MAX_PRECIP_MM_H and wind < FOG_MAX_WIND_MS


def native_state(values: dict, *, initial: bool) -> WeatherState:
    clouds = clouds_from_fraction(values.get("cloud_fraction_pct"))
    rate = values.get("precip_rate_mm_h") or 0.0
    wet = rate >= RAIN_MM_H
    is_snow = snowing(values)
    snow = bool(initial and is_snow)
    risk = values.get("convective_risk_idx")
    storm = bool(risk is not None and risk >= STORM_RISK and clouds == "Overcast" and wet and not is_snow)
    return WeatherState(clouds=clouds, sea_state=sea_state_from_hs(values.get("wave_hs_m")),
                        rain=wet and not is_snow, fog=foggy(values), thunderstorm=storm, snow=snow,
                        wind=wind_direction(values.get("wind_u10_ms"), values.get("wind_v10_ms")))


def mission_weather_plan(state, campaign_seconds: int, lat: float, lon: float, duration_s: int = 4 * 3600,
                         step_s: int = 1800) -> list[tuple[int, WeatherState]]:
    """Sample at the battle position over the mission's planned duration. Consecutive equal
    states are dropped, so a steady day writes no triggers at all."""
    plan = []
    last = None
    fog_now, pending = None, 0
    for t in range(0, duration_s + 1, step_s):
        s = native_state(state.sample(campaign_seconds + t, lat, lon).values, initial=(t == 0))
        if fog_now is None:
            fog_now = s.fog
        elif s.fog != fog_now:  # fog hysteresis: no flicker from a single sample
            pending += 1
            if pending >= FOG_HOLD_SAMPLES:
                fog_now, pending = s.fog, 0
        else:
            pending = 0
        if s.fog != fog_now:
            s = dataclasses.replace(s, fog=fog_now)
        if t and s == last:
            continue
        plan.append((t, s))
        last = s
    return plan


def apply_plan(mission_text: str, plan: list[tuple[int, WeatherState]], **kw):
    """Write a plan into a generated mission in one patch: [Environment] gets the t=0 state,
    each later state becomes one timed trigger."""
    if not plan or plan[0][0] != 0:
        raise ValueError("plan must start at t=0")
    kw.setdefault("title_prefix", "")
    kw.setdefault("stage_label", "MNO ENV weather")
    return patch(mission_text, [s for _, s in plan], times=[t for t, _ in plan[1:]], **kw)
