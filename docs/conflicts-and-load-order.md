# Conflicts, Dependencies, and Load Order

Analysis of the 109-mod subscription list of 2026-08-23 (`data/raw-workshop-list.txt`). The published collection (3812390790) is now 149 items: the 148 Workshop mods in `data/load-order.tokens.txt` plus the pack; that file and `data/mod-catalog.json` are current. Everything here is derived from the mod authors' own descriptions plus platform-overlap analysis, adversarially cross-checked against the raw list; claims that are inference rather than author statement are marked as such. File-level confirmation (duplicate unit/weapon IDs, colliding vanilla overrides) needs the actual mod configs — see `tools/export-mod-configs.ps1`.

**Priority model used throughout:** the Mod Manager list is top-priority-first — when two mods touch the same file, **the higher-listed mod wins**. Every author instruction in this collection ("put X ABOVE my mods", "place above any other PLA-related mods", "need on the top") is phrased in these terms.

## 1. Action items

### Deprecated mods (unsubscribe candidates)

| Mod | Why | Caveat before removing |
|---|---|---|
| [DEPRECATED] E-7A Wedgetail (Pog Frog) | Marked deprecated by its author | **KEEP (revised 2026-08-23): SEST_RAAF_Bases depends on it** (Williamtown AEW&C wing) |
| [DEPRECATED] S-70B-2 Seahawk (Pog Frog) | Marked deprecated by its author | **KEEP (revised 2026-08-23): SEST_RAN_Fleet and SEST_RAAF_Bases depend on it** (LHD air groups, Townsville) |
| [DEPRECATED] F-35C (MyGo) | Integrated into **Modern US Navy** | **F-35C Alt. Loadouts (Prof_CH4OS) explicitly targets this mod** — retarget it first. **Modern US Airbase** also lists an F-35C among its aircraft; if that references this standalone (rather than bundling its own), it breaks too. Verify both |
| [DEPRECATED] F/A-18E/F Super Hornet (MyGo) | Integrated into **Modern US Navy** | **Murder Hornet's target F/A-18E/F mod is unconfirmed** (its author names no target) — identify it before removing this. **Modern US Airbase** lists an F/A-18F with the same caveat as above |

Done 20 Sep 2026: both MyGo mods were unsubscribed and pruned (`data/mod-catalog.json`). F-35C Alt. Loadouts was kept, because SEST_F-35C_JATM is built from it. SEST_Growler_NGJ_MALICE retired the Growler (2020s), whose only provider was the MyGo F/A-18E/F, and rebased its wing-tank donor onto US Naval Aviation.

### Redundant duplicates (pick one)

- **Deck-ops mods** — **Flight Deck Ops** is the *renamed continuation* of the Air Deck Operations upgrade ("Formerly, the FDO was known as the Air deck operations upgrade"). **ADO – Nimitz (2000s)** by a different author reads like an *application* of that upgrade to the Nimitz — it may depend on FDO rather than compete with it; verify before treating the pair as pick-one. Whichever is kept, test against **Nimitz Expanded**'s eight hulls, not just the vanilla Nimitz (they almost certainly clone the same Nimitz data both deck mods override). *(4 Oct 2026: both are kept. Southern Watch places a unit from each (`docs/campaign-coverage.md`), and both are in collection 3812390790.)*

### Missing / manual dependencies — verify installed

- **SeaLifter** is named as required by: A-10A, Su-25, Mi-8 T/TV, B-2 Spirit, and Type 003/004 CVN (A-10C presumed via A-10A) — **and it is not in the subscription list.** It also needs a manual preloader install ("Subscribing isn't enough"). If those mods currently load fine in-game, it's installed; otherwise this is the first thing to fix.
- **Anchor Chain** is subscribed ✔ but is a chainloader that "will not function on its own" — its documented install steps must have been completed. Required by B-2 Spirit, Type 003/004 CVN, and any code-level mod.
- **Euromod – Main Pack** is subscribed ✔ — its addons depend on it: explicitly stated by 5 of the 8 in this list (Nordic, Dutch, German, British, Cold War Spanish), inferred for the other 3 (Italian, JMSDF, Modern Spanish).
- **Modern US Navy** is subscribed ✔ — required by the Ford-class CVN (as of its 2026-08-11 update) for its F-35/F-18/MH-60 air wing.
- **F-15C** — Modern US Airbase lists one; no subscribed mod provides one. Either the airbase bundles its aircraft or the reference is unsatisfied. Verify at file level.

## 2. Conflict watchlist (needs file-level confirmation)

| Area | Mods involved | Risk |
|---|---|---|
| **Three Fujian carriers** | Type 003/004 (ManeuverWarfare) · Chinese Navy PLAN (ltjgbeam) · Fujian CV-18 (八一of军魂) | Three separate Type 003s. If unit IDs differ you just get three Fujians in the menu (clutter); if any share IDs or override the same files, they collide. Recommend picking a primary — CV-18 (八一of军魂) pairs with the same author's Modern PLAN Systems |
| **Modern US weapons** | Dingtools Weapon Pack · U.S. Navy 2027 Capabilities · Murder Hornet · (B-52H + B-52G AGM-86 for ALCM data) | Three mods define/redefine AIM-9X / AIM-120D-class weapons, and both B-52 mods carry AGM-86-family data. Duplicate weapon IDs or contradictory values likely — the #1 thing to scan when configs land |
| **Chinese PL-series AAMs** | J-20 · J-10C · J-16A · JH-7A · J-50 · Flanker-derivative mods (4+ authors) | Same duplicate-weapon-ID exposure as the US row: each fighter mod likely ships its own PL-8/PL-10/PL-12/PL-15 definitions |
| **Russian R-series AAMs** | Su-57 · MiG-35 · Su-30SM2 · Flanker Family (4 authors) | Each likely ships its own R-73/R-77/R-37M-family definitions |
| **Three Tu-95 mods** | Tu-95 w/ AS-15 · Tu-95MS X-101 · Tu-95K-22 | The first two both add Tu-95MS variants; the AS-15 mod also makes **global munition edits** ("VeryLarge impact size") that can bleed into every other mod's weapons — including the K-22's Kh-22 |
| **MH-60-family from four sources** | MH-60R standalone (2154545636) · United States Naval Aviation (misaka) · Modern US Navy · ADO-Nimitz | Up to four MH-60 definitions. Menu clutter at best, ID collisions at worst |
| **Nimitz deck stack** | Nimitz Expanded · ADO-Nimitz · Flight Deck Ops | Three mods touch Nimitz-class data: eight cloned hulls plus two deck-ops overrides. Whether FDO's elevators/taxi paths apply to (or fight with) the expanded hulls is unverified |
| **Global value patches** | Ground Upgrade: SPAA · U.S. Navy 2027 · Tu-95 AS-15 munition edits | Mods that edit shared/vanilla data rather than adding units — their relative list positions silently decide final values |
| **Land air defense** | SAM Pack · THAAD · PLA Land Unit Pack · Ground Upgrade: SPAA · French Army Vehicles (SAMP/T NG) | Multiple sources of land AD units/values; check for the same real-world system defined twice |
| **Flanker airframes across six mods** | Flanker Family (MyGo) · Su-30SM2 · Su-27UBK · J-11 · J-11BS · J-16A | Different variants, likely compatible — but watch for shared weapon/sensor definitions carried by each |
| **Sea Lynx from up to three sources** | Sea Lynx (petrouvis01) · French Helicopter Package (French Navy Lynx likely) · Euromod German (Super Sea Lynx Mk88A on F123) | Same helicopter family from multiple authors; scan for duplicate unit/weapon definitions |

## 3. Recommended mod order (top = highest priority; entries listed in intended top-to-bottom order)

0. **SEST Integration Pack** — above everything, Anchor Chain included (`data/load-order.tokens.txt` is the canonical order; run `set-mod-order.ps1` or the pack's SETUP rather than ordering by hand).
1. **Loaders** — Anchor Chain (+ SeaLifter via its preloader). These change no unit data, so they can't lose a file conflict; top placement is convention (repo recommendation, not an author instruction).
2. **Weapon/system databases and land-unit frameworks** — SAM Pack (author: "top of TOE") · PLA Land Unit Pack (author: "above any other PLA-related mods" — so it precedes Modern PLAN Systems, which is PLA-related) · Dingtools Weapon Pack (author: "above any of my mods") · U.S. Navy 2027 Capabilities (directly above Euromod; see *U.S. Navy 2027 above Euromod* below) · Euromod Main Pack (recommendation) · Modern PLAN Systems (recommendation).
3. **Patch/override mods** — F-35C Alt. Loadouts · Murder Hornet · B-52G AGM-86 loadouts · **Tu-95 AS-15** (here, not with the aircraft: its global munition edits make it a value patch) · Flight Deck Ops · ADO-Nimitz · Ground Upgrade: SPAA — each above the mods it modifies. **Caveat:** a patch that edits weapons a tier-2 database also defines must be promoted *above* that database to take effect — U.S. Navy 2027 against Dingtools Weapon Pack, which sits directly above it in tier 2, is the concrete case to test.
4. **Core faction packs** — Modern US Navy · United States Naval Aviation · all Euromod addons · Chinese Navy · Russian Navy 21 · the three submarine packs · carriers and amphibs (Ford, Nimitz Expanded, Kuznetsov, Liaoning, the chosen Fujian, Type 071, CDG pack).
5. **Individual units** — all standalone aircraft, helicopters, UAVs, land systems, and the Civil Aircraft Mod (self-contained). Within this tier, order only matters between mods flagged in section 2.
6. **Airbases last** — Modern US Airbase · Modern Russian Airbase · Modern Chinese Airbase. Placed at the bottom so any overlapping files they carry lose to the aircraft mods they draw from (which only need to be *installed* to be referenced — list position doesn't affect resolvability, only file conflicts).

Explicit author instructions always win over this scaffold. The tier-2 and tier-3 sequences above are deliberate; elsewhere within a tier, order rarely matters unless two mods appear together in the section 2 watchlist.

## 4. Integration roadmap (what to build in this repo)

1. **File-level conflict scan** *(first, once configs land)* — script that indexes every mod's INI sections and reports duplicate unit names, duplicate weapon/sensor definitions, and files overriding the same vanilla path. Turns section 2 from "watchlist" into a fix list. Priority targets: US missile IDs, PL-series, R-series, MH-60s, the three Fujians, the Nimitz deck stack, and whether Modern US Airbase bundles or references its aircraft.
2. **Compatibility patches** — retarget F-35C Alt. Loadouts at Modern US Navy's F-35C; identify Murder Hornet's actual target and do the same; patch Modern US Airbase's aircraft references if needed — then the two deprecated MyGo mods can actually be unsubscribed. *(Done 20 Sep 2026: both were unsubscribed; see the note under section 1.)*
3. **Custom loadouts** — new loadout variants built cross-mod, e.g. RAAF F-35A with JSM, P-8A with LRASM, B-1B with LRASM, Su-30SM2 maritime-strike fits, Kuznetsov air wing from the Flanker Family, standardized Fujian air wing.
4. **Upgrade variants** — "202X refit" versions of existing hulls (VLS/sensor upgrades) using Euromod / Modern PLAN Systems / Dingtools weapon databases as parts bins.
5. **SEST integration pack** — done: shipped as one meta-mod folder (`integration/dist/SEST_Integration`) and published as Workshop item 3812461539, with its dependencies in collection 3812390790.

## 5. Known limitations of this analysis

- Descriptions were truncated in the source paste; some dependency or load-order instructions may exist that aren't captured here.
- "Overlap" ≠ confirmed conflict — confirmation requires the mod files.
- The top-priority-first reading of the Mod Manager comes from the authors' consistent phrasing, not from engine documentation; the file scan and in-game testing settle it definitively.
- Workshop mods update; deprecation/integration status is as of 2026-08-23.


## U.S. Navy 2027 above Euromod

Euromod and U.S. Navy 2027 both ship seven of the same files, and Euromod used to sit above it, so
Euromod's copies won:

```
usn_rim-116c   usn_rim-162a   usn_rim-174a   usn_rim-66m-2   usn_rim-66m-5
usn_ssq-53h    usn_ssq-62g
```

Those are the fleet's RAM, ESSM, SM-6 and both SM-2 variants — the core of every US ship's air
defence. Three of them (**RAM, SM-2MR, SM-2ER**) ship from Euromod **without `ApplyKinematics`**,
so they were flying the legacy model, while Navy 2027 sets it `True` with a full modern key set
(drag coefficient, boost and sustainer, CEP, attack-altitude band).

Navy 2027's are also internally consistent with each other in a way Euromod's are not: Navy 2027's
shipboard `usn_rim-174a` and air-launched `usn_aim-174b` are both 2650 kts, the same missile in two
mountings. Euromod's `usn_rim-174a` is 3600 kts, so the SM-6 was faster from a ship than from a jet.

**Navy 2027 now sits above Euromod.** Euromod remains above all six of its own addons (German,
Dutch, Scandinavian, British, Italian, JMSDF — all at #30 or below), so its documented requirement
is unaffected, and the LMVLS and IRCPS Modern US Navy's Zumwalt draws on are Euromod-only ids that no ordering
can take away.

**The trade-off, stated plainly:** this is a *consistency* win, not a straight upgrade. Navy 2027's
SM-6 is slower and shorter-legged than Euromod's (2650 kts / 230 nm against 3600 / 260), and its
ESSM is slower but slightly longer-ranged. What you gain is the modern flight model on RAM and both
SM-2s, and a fleet whose missiles agree with each other. To reverse it, move `3606774881` back below
`3629144864` in `data/load-order.tokens.txt` and re-run `set-mod-order.ps1`.

## Four AIM-424s, two flight models (13 Oct 2026)

The player noted that the YF-23 mod's AIM-424 is a different model and flies
a different profile from SEST's. Both are true, and neither file overrides
the other: they have different ids, so the game loads both and a player
sees two rounds named AIM-424 that do not behave alike.

| | YF-23 Black Widow II (3796349767) `yf23_aim424_internal` | SEST `sest_aim-424` (`integration/common/aim424.py`) |
|---|---|---|
| Model | the mod's own mesh, `assets/models/ammunition/yf23_aim424/`, and its own motor effect | the AGM-88G mesh, a rendering stand-in kept because it is proven to load |
| Motor | one long burn: 58 s at 2.9 g, no sustainer | 4 s boost at 20 g, then a 20 s sustainer at 4.5 g |
| Loft | 30 degrees to 85,000 ft | 30 degrees to 150,000 ft, terminal loft on |
| Terminal phase | local terminal only; seeker 20 NM active, 12 NM passive; approach from 17 NM | datalink to terminal; seeker 40 NM active, 80 NM passive; approach from 36 NM |
| Agility | 16 degrees/s, 25 g | 28 degrees/s, 25 g |
| Envelope | 3-255 NM, 600 s flight, targets to 105,000 ft | 2-290 NM, 400 s flight, targets to 150,000 ft |
| Warhead | type 0, Power 23, Pk 0.85 | fragmentation, Power 48, Pk 0.98 |
| Carried by | the YF-23 only (stations 15-16, internal) | F-35A (RAAF), F-35C, F-16CM, F-15EX, EA-18G, the Super Hornets, Rafale F5 |

The other two AIM-424 files share one id, `usn_aim-424`: US Naval Aviation
(3737267013, which ships the `aim-424.obj` mesh) and U.S. Navy 2027
(3606774881, which points at that mesh). Whichever ranks higher in the load
order wins that id; they differ again (1,600 against 2,650 knots top speed,
250 against 350 NM). All four are 680 kg, as the Navy's fact file says.

Nothing is changed for this note. Options, for the player to choose:
1. leave the YF-23 its author's own round (the current state, and the
   catalog's position since the YF-23 gained it upstream);
2. give the YF-23 SEST's round, so every AIM-424 in the collection flies
   alike - a whole-file override of `usaf_yf-23_black_widow_ii.ini`, stations
   15-16 only, which then has to follow every YF-23 update;
3. give SEST's round a real AIM-424 mesh (`aim-424.obj` or the YF-23's
   `yf23_aim424`) in place of the AGM-88G - wants an in-game look first, since
   the last change to that model block made the missile fall back to a RIM-7.
The APKWS Redback draft cites the AIM-424 as a precedent; it should name
which of these it means.

**Decision (13 Oct 2026, the player): option 1.** The YF-23 keeps its
author's round.

**Then (13 Oct 2026, the player): U.S. Navy 2027's flight model for every
AIM-424, no 3D model changes yet.** On `feature/aim424-usn2027-flight-model`:
SEST's round takes U.S. Navy 2027's `[Guidance]` key for key (`FLIGHT` in
`integration/common/aim424.py`), and SEST Collection Fixes lays the same keys
over the YF-23's round with an `#!extend`
(`ammunition_overwrite/yf23_aim424_internal_FlightModel_SEST.ini`, read by the
Anchor Chain preloader). The table above shows the figures before that change.
Each round keeps its own model, warhead and effects, so the YF-23 still fires
its author's round on its own mesh; option 3 (a real mesh for SEST's round) is
still open.

**Which plays, and which is closest to the real missile.** U.S. Navy 2027
(load order 21) outranks US Naval Aviation (73), so the `usn_aim-424` in game
is U.S. Navy 2027's flight figures on US Naval Aviation's `aim-424.obj` model
(U.S. Navy 2027 points at that asset). Against what the Navy published (680
kg, 4.11 m, 34.3 cm, "in excess of 250" NM, a solid motor read as two-stage,
blast-fragmentation) - speed and seeker are not public, so the rest is
estimate:
- US Naval Aviation's own figures are the least plausible: 1,600 knots
  (the same-diameter AIM-174B is 2,650 in the collection), a 15-degree loft,
  exactly 250 NM. Its model is the best: the real shape.
- U.S. Navy 2027's are the most plausible of the mods': 2,650 knots, a
  45-degree loft to about 148,000 ft, datalink and retargeting; 350 NM is
  above the published floor - optimistic, not contradicted.
- The YF-23's are approximations by its author's own description: one 58 s
  burn, a 20 NM seeker.
- SEST's follows the fact file and is aligned key for key with U.S. Navy
  2027's AIM-174B, so it sits with U.S. Navy 2027's; its weakness is the
  AGM-88G model (option 3 above).
Maintenance, from the repo's exports: US Naval Aviation is a team mod (Sea
Power China Test Group and Euromod), the largest (264 exported files) and the
most often changed (15 exports); U.S. Navy 2027 is one author, changed its
AIM-424 most recently (10 Oct 2026), and is fragile by construction (alias
patches over Modern US Navy hulls); the YF-23 is the smallest (4 exports).
