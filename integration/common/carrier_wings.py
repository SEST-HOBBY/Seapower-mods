"""Authored 2028 Ford air wing shared by default and variant overrides.

This is SEST's mission configuration, not a claim about an actual deployed CVW.
Sixteen F-35Cs replace part of the Hornet allocation; the wing stays at 70
against 90 hangar places, leaving room for the mission's airborne aircraft.
"""
import re

FORD_TYPES = {"usn_cvn_ford", "usn_cvn_gerald_r_ford"}
FORD_WING = [
    ("usn_fa-18e", "Squadron1", 12),
    ("usn_fa-18e", "Squadron2", 12),
    ("usn_fa-18f", "Squadron2", 12),
    ("usn_f-35c", "Squadron10", 16),
    ("usn_ea-18g", "Squadron1", 6),
    ("usn_e-2d", "Squadron4", 4),
    ("usn_mh-60r", "Squadron1", 8),
]


def ford_lines():
    grouped = {}
    for uid, squadron, count in FORD_WING:
        grouped.setdefault(uid, []).append(f"{squadron},{count}")
    return "\n".join(uid + "=" + "|".join(picks) for uid, picks in grouped.items()) + "\n"


def modern_ford_group(text, uid, variants=False):
    """Replace only air-group rows; keep hull art, flags and variant metadata."""
    if uid not in FORD_TYPES:
        return text
    found = 0
    chunks = []
    for chunk in re.split(r"(?=^\[)", text, flags=re.M):
        match = re.match(r"^\[([^]\n]+)\]", chunk)
        name = match[1] if match else ""
        eligible = name == "AirGroup" if not variants else name == "Default" or bool(re.fullmatch(r"Variant\d+", name))
        if eligible:
            if not variants:
                chunk = "[AirGroup]\n" + ford_lines() + "\n"
            else:
                chunk = re.sub(r"^usn_[^=\n]+=[^\n]*\n?", "", chunk, flags=re.M)
                chunk = re.sub(r"^CustomAirGroup=[^\n]*\n?", "", chunk, flags=re.M)
                chunk = chunk.rstrip() + "\nCustomAirGroup=True\n" + ford_lines() + "\n"
            found += 1
        chunks.append(chunk)
    if not found:
        raise SystemExit(f"{uid}: no {'variant' if variants else 'AirGroup'} sections to modernise")
    return "".join(chunks)
