# SEST JMSDF Mogami

Gives the Mogami-class frigate its real JMSDF air group. The standalone mod embarks a USN
SH-2F Seasprite; this patch replaces it with an **SH-60K** and adds both JMSDF Seahawks
(`jmsdf_sh-60k`, `jmsdf_sh-60j` from Euromod JMSDF) to `AircraftSupported`, keeping the SH-2F
for compatibility. With Euromod JMSDF's Asahi/Atago/Maya, the Mogami completes the modern
JMSDF surface line, and one Seahawk id now serves a Mogami and a Maya deck alike.

Euromod JMSDF renamed its Seahawks from `jp_sh-60k`/`jp_sh-60j` to the `jmsdf_` ids on
19 Sep 2026, and its language file names only the new ones. If
`mods-source/3695809489/aircraft/` still shows `jp_sh-60*.ini`, those are leftovers of an
export that predates the exporter's deletion mirror; the next `tools\export-mod-configs.ps1`
run removes them.

**Requires:** Mogami-class Frigate mod · Euromod JMSDF (+ Euromod Main).
**Order:** above the Mogami-class Frigate mod.
**Rebuild:** `python3 integration/jmsdf-mogami/build_patch.py`
