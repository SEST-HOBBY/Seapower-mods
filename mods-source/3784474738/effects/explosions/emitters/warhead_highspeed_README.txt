Conventional high-speed air hits
================================
Three native INI effects: warhead_highspeed_small / medium / large.
Each folder contains its named root INI. Use the root, not an individual emitter.

AC Pack ammunition_overwrite, existing [Particles] section:
HitEffectSpeedThreshold=5800
HighSpeedHitAirExplosion=effects/explosions/emitters/warhead_highspeed_medium/warhead_highspeed_medium.ini

MultiStageMissiles selects this effect for an actual air hit
when missile speed + hit-object speed reaches 5800 knots; directions are ignored.
This is visual tuning, not physical relative speed or a special BMD-only rule.
Native lower-speed effects and all damage/guidance values remain unchanged.
Without the plugin the INI visual can still be used through HitAirExplosion,
but the speed-based switch is unavailable. No additional DLL is installed.

Sizes use existing in-game WarheadData.Power as a visual grouping only, not kg:
small <=12; medium >12 through 30; large >30. No nuclear or ASW assignment.
Small: 106 visible burst particles; medium: 174; large: 370; plus one carrier.
Short warm flash, 0.4-0.75 s fire billows, decelerating fragments, gray smoke
1.6-3.8 s and debris up to 4.4 s. World-space particles; no extra audio/light.
Large includes 310 glowing sparks (up to 2.6 s) and 24 mesh fragments.
Large spark minimum screen size is 0.0004 for distant readability.

SM-3/PAC-3 retain their existing kinetic effects. Euromod remains unchanged.
SM-6C has only a dormant overwrite on this installation: its large-effect
assignment is prepared, but its missing base ammunition is not created here.
Restart Sea Power after editing ammunition/resource INIs.
Visual preview and actual interceptions still need an in-game check.
