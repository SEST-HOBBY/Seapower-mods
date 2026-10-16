# Workshop refresh, 16 October 2026

Capture `b08670c0` on `chore/workshop-refresh-20261016`, taken from the deploy
build `c948bc9a` after Steam updated the Euromod packs overnight. Merged into
`feature/workshop-update-20261016` and rebuilt.

## 1. What changed upstream

The update check lists eleven mods. Four of them (3775128499, 3776340577,
3780118683, 3781062859) are the CR-stripped mods the inventory gate already
reports; their export did not change. Seven changed:

| Mod | Change | Effect on SEST |
|---|---|---|
| Euromod - Modern US Navy (3390330875) v.617 | 2024 Ticonderoga/Bunker Hill rebuilt as `#!alias` of the 2004 hull with SPQ-9B, Nulka, Bushmasters and two IRST directors; a new `usn_cg_bunker_hill_vls_2024_late` | The flight deck is inherited from the 2004 hull. SEST's seven Ticonderoga CombatSystems overwrites already extend this hull with no keys. Nothing to change. |
| Euromod - Modern British Navy (3599752717) v.72 | Apache AH.1 `raac_ah_mk_1`, HMS Ocean 2009 `rn_lph_ocean_09` carrying it, two rocket-pod materials and `animations_usa_ah-64a` | No file path or unit id is shared with any other mod or with vanilla, so no clash with the AH-64 Apache mod or SEST's Apaches. Cross-deck and replenishment now cover Ocean 2009. |
| Euromod - Main Pack (3629144864) | `is_shafrir_2` renamed `isaf_shafrir_2`; sensor tweaks | SEST references neither name. |
| Euromod - South Korea Navy (3789208859) | KDDX now a playable vessel `ko_kddx`; L-SAM round; `ko_ciws-II` | Cross-deck and replenishment cover the KDDX; replenishment gives the L-SAM its supply keys. The intercept model's K-SAM II file follows the update. |
| Spanish Navy Mod (Cold War) (3630495619) | Santa María on the OHP long-hull model, new ESM, SH-60B airgroups; Príncipe de Asturias elevator; aircraft and several hulls trimmed to aliases of vanilla | Every Santa María and Baleares launcher is now magazine-fed, so SEST Replenishment's overrides for `ae_ffg_santa_maria`, `ae_ffg_santa_maria_late` and `ae_ffg_baleares` have nothing left to fix and are dropped. `es_ffg_baleares`, the alias base, is vanilla. |
| US Naval Aviation (3737267013) | USMC F-35B squadrons and names | None. |
| PLAAF Aircraft Pack (3812111085) | J-16D and small PL-series round edits | None. |

## 2. Checks

`check_mod_conflicts.py` on the four Euromod/Spanish packs: each shares files
only with SEST packs and loses them all, correct as placed. The Korea pack's
`[MK15A]` contest with the Royal Australian Defence Forces mod is not new.

Gates: 11 of 12 pass; `check_inventory` fails on the same four CR-stripped
mods as before. Campaign tests 196 pass, tool tests 105 pass. The campaign
missions did not change.

## 3. Second capture, 16 October (473805ea)

The PC re-ran the capture block on the same branch name; the block reset it to
the morning capture and added the new export on top, so the push was a plain
fast-forward. Eight mods changed:

| Mod | Change | Effect on SEST |
|---|---|---|
| Anduril Maritime Drones (3819522350), Saronic Corsair ASV (3766210676) | Steelfin interceptor (`usn_steelfin`, `usn_steelfin_boat`), a Kraken K5 and a Corsair carrying it; renamed vessels in every language | The shared Steelfin files are byte-identical in each mod, so load order does not matter. |
| YF-23 (3796349767), Anduril Fury (3804868806), MV-75 Cheyenne II (3810611344) | A `Steelfin` loadout with `usn_steelfin_air` (identical in all three); the YF-23 and Fury files re-saved with new line endings, about ten real lines each; MV-75 material files | None of the three names the `Steelfin` loadout, so the picker would read MISSING TEXT, including in SEST missions that place the YF-23, Fury and MV-75 (`check_campaign_coverage`). SEST Collection Fixes now names it "Steelfin (air-defence interceptor)". SEST ships no copy of these aircraft, so the loadout reaches the game untouched. |
| Euromod - South Korea Navy (3789208859) | CIWS-II radar and Goalkeeper on the KDDX and FFG-828; `ships/non/ddh_975` removed | SEST Replenishment's KDDX and FFG-828 follow the new fits. |
| Spanish Navy Mod (Modern) (3731208477) | Álvaro de Bazán, Cristóbal Colón and Juan Carlos I fits; Juan Carlos deck park | SEST Replenishment follows; RAN Fleet's Hobart and Canberra, built on these hulls, take the new model position and deck park. |
| Dynamic Campaign Mod (3813157776) | Three new sample campaigns; East Asia 1985 extended | See below. |

`check_dynamic_campaign.py` learned its force and patrol keys from the first
sample campaign by name. The new `atlantic_1972_hold_the_gap` sorts ahead of
`east_asia_1985` and puts no `hold` on a patrol, so the world campaign's six
submarine patrols failed the check. East Asia 1985 and the new Pacific 1985
both still use `hold` on patrols; the checker now reads every sample. The
world campaign itself is unchanged.

Gates: 11 of 12 pass (`check_inventory`, the same four mods). Campaign tests
196 pass, tool tests 105 pass.

Next time the capture block should get a fresh branch name from a session;
reusing one works only while that branch's last capture is the deployed one.
