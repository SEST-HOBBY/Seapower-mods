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
