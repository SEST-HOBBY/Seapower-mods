C-RAM airburst (INI only)

Assign this effect path to the desired ammunition / existing effect mapping:
effects/explosions/emitters/cram_airburst/cram_airburst.ini

For an ammunition [Particles] override:
HitAirExplosion=effects/explosions/emitters/cram_airburst/cram_airburst.ini
HitAirExplosionClass=

Assigned to usn_cal_20mm via AC Pack/ammunition_overwrite/Original/usn_cal_20mm_OVWR.ini (air hits only). APDS remains unchanged. No DLL or sound is added.
Stock small-flak main smoke: 5 particles, original size/material and 5-6 s lifetime.
Added: 0.10-0.16 s white flash, faint 0.16-0.23 s halo, 10 small cooling embers.
Total maximum emitted particles per burst: 18 (including one invisible carrier).
Additive glow remains visible in daylight, but has much greater contrast at night.
This is not a day/night switch or a dynamic light: it does not illuminate nearby meshes.
Bloom, exposure and camera distance affect the result. No screen-size minimum is forced.
Reference: https://www.youtube.com/shorts/lbon4AFE9as (overview and 0.1 s samples inspected).
INI keys checked against installed public 26651831 and historical public/stable schemas.
Current stable build and in-game day/night appearance have not been tested.
