"""Sensor-weather brief: plain lines from a SensorEnv, grouped by section. BUILD-TESTED, planning product.

Every line is "TAG [Section]: text". TAG is GAME (what Sea Power itself applies, quoted from its files),
REAL-WORLD (a planning note the simulator does not model) or UNTESTED (a per-mission [Sonar] value
nothing writes until the owner's PC test passes). Sections: Sonar, Radar, EO/IR, Air ops.
"""
from __future__ import annotations

from .sensors import SensorEnv


def _fmt_db(d: dict) -> str:
    return ", ".join(f"{k} {v:.1f}" for k, v in d.items())


def brief_lines(env: SensorEnv, data_class: str = "PROCEDURAL") -> list[str]:
    i = env.items
    get = i.get
    out = []
    # --- Sonar
    ss = i["game_sea_state"].value
    out.append(f"GAME [Sonar]: SeaState {ss}; passive ambient {i['game_ambient_db'].value:.0f} dB ({i['game_ambient_db'].note}).")
    cz = i["convergence_zones"]
    cz_txt = "none" if cz.value is None else (f"about {cz.value[0]:.0f} and {cz.value[1]:.0f} nm" if isinstance(cz.value, tuple) else "unknown")
    out.append(f"REAL-WORLD [Sonar]: convergence zones {cz_txt} ({cz.note}). The game uses 30/60 nm wherever depth > 3000 ft.")
    out.append(f"REAL-WORLD [Sonar]: mixed layer about {i['mixed_layer_m'].value} m, layer {i['layer'].value}; surface duct carries "
               f"sound above about {3 * i['duct_cutoff_hz'].value:.0f} Hz. The game computes its own layer.")
    out.append(f"REAL-WORLD [Sonar]: absorption {i['absorption_db_km'].value:.2f} dB/km at 3.5 kHz ({i['absorption_db_km'].note}).")
    if get("ice_noise"):
        out.append(f"REAL-WORLD [Sonar]: {i['ice_noise'].value}.")
    if get("biologics"):
        out.append(f"REAL-WORLD [Sonar]: {i['biologics'].value}.")
    # --- Radar
    rh = i["radar_horizon_km"].value
    out.append(f"REAL-WORLD [Radar]: standard horizon from a 20 m antenna {rh['sea_skimmer_5m']:.0f} km to a sea-skimmer, "
               f"{rh['ship_25m']:.0f} km to a ship's mast.")
    ed = i["evap_duct_m"]
    if ed.value is None:
        out.append(f"REAL-WORLD [Radar]: evaporation duct: {ed.note}.")
    elif ed.value == 0:
        out.append("REAL-WORLD [Radar]: no evaporation duct (moist air over cooler water).")
    else:
        trap = get("evap_duct_traps_above_ghz")
        bands = "X band and above extended" if trap is not None and trap.value < 10 else "mainly Ku/Ka extended"
        out.append(f"REAL-WORLD [Radar]: evaporation duct about {ed.value:.0f} m: {bands} against low targets (low confidence).")
    sbd = i["surface_duct_likelihood"].value
    out.append(f"REAL-WORLD [Radar]: surface-based duct on about {100 * sbd:.0f} % of days this season"
               + ("; radar and ESM can reach far beyond the horizon." if sbd >= 0.25 else "."))
    if get("subrefraction"):
        out.append("REAL-WORLD [Radar]: sub-refraction possible (moist air over cooler water): radar horizon shortened.")
    sc = i["sea_clutter_db"].value
    out.append(f"REAL-WORLD [Radar]: sea clutter X band {sc['X_0.3deg']:.0f} dB at 0.3 deg, {sc['X_3deg']:.0f} dB at 3 deg; "
               f"S band {sc['S_1deg']:.0f} dB at 1 deg.")
    rl = i["rain_loss_20km_2way_db"].value
    if rl["X"] >= 0.1:
        out.append(f"REAL-WORLD [Radar]: 20 km of this rain costs (two way) {_fmt_db(rl)} dB; SATCOM fade {_fmt_db(i['satcom_fade_db'].value)} dB.")
    mp = i["multipath_x"].value
    out.append(f"REAL-WORLD [Radar]: X-band multipath against a 5 m target: first lobe peak near {mp['R1_km']:.0f} km; "
               f"sea reflection {mp['rho_0.115deg']:.2f} at the horizon.")
    # --- EO/IR
    vis = i["visibility_km"].value
    if vis is not None:
        out.append(f"GAME [EO/IR]: visibility {vis:.1f} km" + (" - Fog" if vis < 1 else "") + f" [{data_class}].")
    if get("dust"):
        out.append("REAL-WORLD [EO/IR]: dust haze: visual and laser ranges suffer more than IR.")
    out.append(f"REAL-WORLD [EO/IR]: IR range x{i['ir_range_factor_lwir'].value:.2f} LWIR, x{i['ir_range_factor_mwir'].value:.2f} MWIR "
               f"against a temperate clear day.")
    m = i["moon"].value
    night = i["sun_alt_deg"].value < -12
    nv = i["night_vision"].value
    out.append(f"REAL-WORLD [EO/IR]: moon {m['illum_pct']} % {'waxing' if m['waxing'] else 'waning'}, altitude {m['alt_deg']:.0f} deg"
               + (f", about {m['lux']:.2g} lux: night vision {nv}" if night else "; daylight or twilight") + ".")
    # --- Air ops
    cb = i["cloud_base_m"].value
    out.append(f"REAL-WORLD [Air ops]: ceiling {'about ' + str(cb) + ' m' if cb is not None else 'unlimited'}; carrier recovery "
               f"{i['carrier_case'].value}.")
    out.append(f"GAME [Air ops]: helicopters may not launch above each ship's MaxLandingSeaState (sea state now {ss}) when "
               f"'Restrict air ops by sea state' is on.")
    # --- Untested [Sonar] suggestions
    sug = [f"BaseAmbientOceanNoise {i['ambient_suggest_db'].value:.0f}", f"RainNoise {i['rain_noise_suggest_db'].value:.0f}",
           f"XLayer {i['layer_loss_suggest_db'].value[0]:.0f}/{i['layer_loss_suggest_db'].value[1]:.0f} dB",
           f"AbsorptionFactor {i['absorption_suggest'].value:.2f}"]
    if get("sofar_suggest_m"):
        sug.append(f"SofarAxisDepthM {i['sofar_suggest_m'].value}")
    if get("cz_disable_suggest"):
        sug.append("MinDepthForConvergenceZones 20000 (no zones)")
    if get("layer_disabled_suggest"):
        sug.append("LayerDisabled True")
    out.append("UNTESTED [Sonar override]: " + "; ".join(sug) + ".")
    return out
