"""Sensor-weather brief: a few plain lines from a SensorEnv. BUILD-TESTED, planning product.

Every line is tagged GAME (what Sea Power itself applies, quoted from its files) or REAL-WORLD (a
planning note the simulator does not model). Suggested per-mission [Sonar] values are shown as
UNTESTED; nothing here changes a mission.
"""
from __future__ import annotations

from .sensors import SensorEnv


def brief_lines(env: SensorEnv, data_class: str = "PROCEDURAL") -> list[str]:
    i = env.items
    out = []
    ss = i["game_sea_state"].value
    out.append(f"GAME: SeaState {ss}; passive ambient {i['game_ambient_db'].value:.0f} dB ({i['game_ambient_db'].note}).")
    vis = i["visibility_km"].value
    if vis is not None:
        out.append(f"GAME: visibility {vis:.1f} km" + (" - Fog" if vis < 1 else "") + f" [{data_class}].")
    cz = i["convergence_zones"]
    cz_txt = "none" if cz.value is None else (f"about {cz.value[0]:.0f} and {cz.value[1]:.0f} nm" if isinstance(cz.value, tuple) else "unknown")
    out.append(f"REAL-WORLD: convergence zones {cz_txt} ({cz.note}). The game uses 30/60 nm wherever depth > 3000 ft.")
    out.append(f"REAL-WORLD: mixed layer about {i['mixed_layer_m'].value} m, layer {i['layer'].value}; surface duct carries "
               f"sound above about {3 * i['duct_cutoff_hz'].value:.0f} Hz. The game computes its own layer.")
    ed = i["evap_duct_m"]
    if ed.value is None:
        out.append(f"REAL-WORLD: evaporation duct: {ed.note}.")
    elif ed.value == 0:
        out.append("REAL-WORLD: no evaporation duct (moist air over cooler water).")
    else:
        trap = i.get("evap_duct_traps_above_ghz") if hasattr(i, "get") else None
        bands = "X band and above extended" if trap is not None and trap.value < 10 else "mainly Ku/Ka extended"
        out.append(f"REAL-WORLD: evaporation duct about {ed.value:.0f} m: {bands} against sea-skimmers (low confidence).")
    ra = i["rain_atten_db_km"].value
    if ra["X"] > 0.001:
        out.append(f"REAL-WORLD: rain loss one way X {ra['X']:.2f}, Ku {ra['Ku']:.2f}, Ka {ra['Ka']:.2f} dB/km; S/C negligible.")
    out.append(f"REAL-WORLD: IR range x{i['ir_range_factor_lwir'].value:.2f} LWIR, x{i['ir_range_factor_mwir'].value:.2f} MWIR vs a temperate clear day.")
    m = i["moon"].value
    night = i["sun_alt_deg"].value < -12
    out.append(f"REAL-WORLD: moon {m['illum_pct']} % {'waxing' if m['waxing'] else 'waning'}, altitude {m['alt_deg']:.0f} deg"
               + (f", about {m['lux']:.2g} lux" if night else "") + ("; night" if night else "; daylight or twilight") + ".")
    cb = i["cloud_base_m"].value
    if cb is not None:
        out.append(f"REAL-WORLD: ceiling about {cb} m ({i['cloud_base_m'].confidence} confidence).")
    sug = (f"UNTESTED [Sonar] suggestion: BaseAmbientOceanNoise {i['ambient_suggest_db'].value:.0f}, "
           f"RainNoise {i['rain_noise_suggest_db'].value:.0f}, XLayer {i['layer_loss_suggest_db'].value[0]:.0f}/{i['layer_loss_suggest_db'].value[1]:.0f} dB.")
    out.append(sug)
    return out
