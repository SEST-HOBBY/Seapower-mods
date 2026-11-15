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

- **SeaLifter** is named as required by: A-10A, Su-25, Mi-8 T/TV, B-2 Spirit, and Type 003/004 CVN (A-10C presumed via A-10A), and it is not in the subscription list. **It is not needed:** on 19 Oct 2026 the PC, with no SeaLifter at all, showed the B-2, A-10A, Su-25, Mi-8 and Type 003 in the encyclopedia with their models. The requirement dates from those mods' early-game descriptions; the manual part of the old install was Anchor Chain's preloader, which SETUP installs.
- **Anchor Chain** is subscribed ✔ but is a chainloader that "will not function on its own" — its documented install steps must have been completed. Required by B-2 Spirit, Type 003/004 CVN, and any code-level mod.

  **On the public beta (Build 261026, 28 Oct 2026) no code mod loads.** Two causes are established. First, the Workshop preloader looks for the chainloader in the game's list of mod directories before the beta's `FileManager` has registered the Workshop folders, so it finds none and nothing after it runs (the symptom is in `docs/workshop-refresh-20261028-review.md`, section 1). Second, once a chainloader does run, upstream Anchor Chain 1.1.0's `LoadPlugins` keeps a plugin whose entry point threw in its pending set and retries it without bound: its no-progress branch logs an abort but does not stop. GPT found this in the 31 Oct 2026 launch log of its earlier test bootstrap (PR #53), which printed AutomaticSAR's "Loaded." line 351 times; which plugin threw is not proven, because the first BepInEx log was overwritten. A bounded fork of Anchor Chain (each plugin started at most once, the loop stopped when nothing progresses) and an inert bootstrap (pinned to Build 261026 and the original preloader's hash, waiting for the Workshop registration, off until an explicit enable flag) are in `integration/beta-anchorchain/`. Both are source-only test candidates: the pack does not ship them and SETUP does not install them.
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
1. **Loaders** — Anchor Chain and its preloader. These change no unit data, so they can't lose a file conflict; top placement is convention (repo recommendation, not an author instruction).
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

Nothing was changed for this note. Options, for the player to choose:
1. leave the YF-23 its author's own round (the state until 14 Oct, and the
   catalog's position from when the YF-23 gained it upstream until then);
2. give the YF-23 SEST's round, so every AIM-424 in the collection flies
   alike - a whole-file override of `usaf_yf-23_black_widow_ii.ini`, stations
   15-16 only, which then has to follow every YF-23 update;
3. give SEST's round a real AIM-424 mesh (`aim-424.obj` or the YF-23's
   `yf23_aim424`) in place of the AGM-88G - wants an in-game look first, since
   the last change to that model block made the missile fall back to a RIM-7.
The APKWS Redback draft cites the AIM-424 as a precedent; it should name
which of these it means.

**Decision (13 Oct 2026, the player): option 1**, the YF-23 to keep its
author's round. Replaced the same day.

**Then (13 Oct 2026, the player; never merged, replaced on 14 Oct): every
AIM-424 to fly U.S. Navy 2027's flight model, no 3D model changes yet.** Built
on `feature/aim424-usn2027-flight-model`: SEST's round was to take U.S. Navy
2027's `[Guidance]` key for key (`FLIGHT` in that branch's
`integration/common/aim424.py`), and SEST Collection Fixes was to lay the same
keys over the YF-23's round with an `#!extend`
(`ammunition_overwrite/yf23_aim424_internal_FlightModel_SEST.ini`). Each round
was to keep its own model, warhead and effects. The branch is not merged and
should not be: the 14 Oct decision below replaces it.

**Which played before 14 Oct, and which is closest to the real missile.** U.S.
Navy 2027 (load order 21) outranks US Naval Aviation (73), so the `usn_aim-424`
in game was U.S. Navy 2027's flight figures on US Naval Aviation's
`aim-424.obj` model (U.S. Navy 2027 points at that asset). Against what the
Navy published (680 kg, 4.11 m, 34.3 cm, "in excess of 250" NM, a solid motor
read as two-stage, blast-fragmentation) - speed and seeker are not public, so
the rest is estimate:
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

**Now (14 Oct 2026, the player): every AIM-424 flies SEST's own flight
model on SEST's own 3D model block.** This replaces both 13 Oct decisions.
SEST's round, `sest_aim-424` in `integration/common/aim424.py`, is not
changed: its figures are the right-hand column of the table above, on the
AGM-88G stand-in. SEST Collection Fixes lays it over every other AIM-424 id
with one Anchor Chain `#!extend` per id in `ammunition_overwrite/`, the folder
the Euromod Anchorchain Expansion (3784474738) patches 90 rounds from
(`usn_rim-161*_OVWR.ini` among them). `build_aim424` in
`integration/collection-fixes/build_patch.py` reads every value from
`aim424.py` when the pack is built, so the stubs cannot drift from SEST's
round. Each stub sets:
- SEST's `[Guidance]`, all 54 keys: motor, loft, datalink and terminal
  handover, seeker, agility, envelope, flight time, ECCM;
- SEST's model block: every key of `[Models]`, `[Colliders]` and `[col_main]`,
  and the four encyclopedia camera keys of `[General]`. That block is US
  Naval Aviation's `usn_agm-88g` key for key; the build checks it on every run;
- the round's own effect positions, moved to `0,0,-0.04`, where US Naval
  Aviation's AGM-88G puts all three of its effects. The effects themselves
  stay the author's.

A fifth AIM-424 file came in with the 13 Oct export: the FQ-44 Fury's
`fury_aim424` (3804868806), a copy of the YF-23's round (same figures, a
0.25 s drop) on a copy of its mesh. It is covered too. Positions are from
`data/load-order.preview.txt`; carriers are the winning aircraft files.

| Id | Round the stub lands on | Carried by (loadout: stations) | Stub file | Keeps of its own |
|---|---|---|---|---|
| `usn_aim-424` | U.S. Navy 2027's (3606774881, 15th), which outranks US Naval Aviation's (3737267013, 67th) | F/A-18E, F/A-18F, F/A-18F Block III (`MH_CAP_424`: 32-33, `MH_LRAAM`: 30-33, `MH_PenetratorLRAAM`: 30-31; SEST Growler NGJ+MALICE's forks win these files); F-35C (`AirToAirInterceptLongRange`, `AirToAirLRAAM`, `AirToAirLRAAMclean`: 5-6; SEST F-35C JATM's fork); ROK F-35A, Euromod-South Korea Navy (`AirToAirInterceptLongRange`: 5-6) | `usn_aim-424_OVWR.ini`, the name of U.S. Navy 2027's own overwrite of this round, so it replaces it (below) | warhead (fragmentation, Power 20, Pk 1.02, 15 m fuze), mass 680, AmmoPoints 1010, signature, effects (SAM booster plume, a sustainer plume from 31 s), name; `RangeGate=2` and `SizeGate=1.1`, seeker gating keys SEST's round does not set and an extend cannot remove |
| `yf23_aim424_internal` | YF-23 Black Widow II's (3796349767, 164th), the only copy | YF-23 (`AirToAirIntercept`: 15-16, internal) | `yf23_aim424_internal_SEST.ini` | warhead (type 0, Power 23, Pk 0.85, fuze distance 40), mass 680.4, AmmoPoints 2000, signature, effects (its own 58 s motor plume), name |
| `fury_aim424` | the FQ-44 Fury's (3804868806, 73rd), the only copy | FQ-44 Interceptor, `usn_fury_interceptor` (`AirToAirIntercept`: 5, 6, 15, 16) | `fury_aim424_SEST.ini`; also `ResourcesMeshRotation=0,0,0` in place of the author's `0,0,45`, which turned his own mesh | as the YF-23's, with its own motor plume and smoke trail, and its `[Sounds]` |

U.S. Navy 2027 patches its own `usn_aim-424` with
`ammunition_overwrite/usn_aim-424_OVWR.ini`: a multi-stage block (the
Euromod Anchorchain Expansion's keys) whose `Stage1Mesh=aim-424` names a part
of the `aim-424.obj` model, with a 31 s smokeless motor plume and motor audio.
That block does not fit the AGM-88G model, and in what order two extends of
one id apply has not been seen, so the SEST stub takes that file's name and
replaces it. The file's camera and `Resources*` keys repeat the round's own
values; the build checks that, and stops if the file changes.

What `build_aim424` stops on, so nothing changes silently: an AIM-424 file
joining or leaving the export; a round's winning copy moving to another mod;
a round gaining or losing any key the stub sets; a key a round sets in a laid
section that SEST's round does not (an extend cannot remove a key, and
`RangeGate`, `SizeGate` and the Fury's `ResourcesMeshRotation` are the only
three recorded, each with its reason); another mod extending one of the ids;
U.S. Navy 2027's overwrite changing; SEST's model block no longer reading as
US Naval Aviation's `usn_agm-88g`.

Option 2 (a whole-file YF-23 override) is not needed: the round is
overridden, and the YF-23's aircraft file stays its author's. Option 3 (a
real mesh for SEST's round) is still open; since the stubs read `aim424.py`,
a change to SEST's model block now changes all four ids at once. Each id's
encyclopedia name and description stay its own mod's; none of the other
three quotes a flight figure.

**Not demonstrated in game:**
- that these stubs apply at all. SEST has not shipped an
  `ammunition_overwrite/` file before, and none has been seen in game, least
  of all one that sets `[Models]` keys. The Euromod Anchorchain Expansion
  (`usn_aim-120d_OVWR.ini` and others) and U.S. Navy 2027 ship such files.
  The 13 Oct PC capture lists AnchorChain.Preloader 1.0.0 loaded
  (`docs/workshop-refresh-20261013-review.md`, section 5). Without the
  preloader none of the three stubs applies, and each round flies and looks
  as its author shipped it;
- that a SEST Collection Fixes file of the same name replaces U.S. Navy 2027's
  `usn_aim-424_OVWR.ini` (the rule `STALE_OVERWRITES` relies on, also not seen).
  If it does not, both extends land on `usn_aim-424` and the stage block
  sits over the AGM-88G;
- the RIM-7 risk. SEST's own round once fell back to the `usn_rim-7`
  asset-bundle stand-in, a short fat Sea Sparrow, after one extra key
  (`ResourcesMeshScale`) in its model block (the note in `aim424.py`). The
  stubs carry SEST's block key for key and the build refuses a model key it
  does not know, but a block assembled by `#!extend` from base keys plus
  overwrite keys has not been seen to render the same as one written whole.
  A Sea Sparrow under the YF-23, the Fury or a Super Hornet's 424 fit is
  this risk: bring back Player.log;
- the effects' timing. The YF-23's and the Fury's motor effects run 58 s
  (`Duration=58` in their effect files), for their author's single burn;
  SEST's motor burns 4 s then 20 s, so on those two rounds the plume outlasts
  the motor. On `usn_aim-424` the sustainer plume starts at 31 s, after SEST's
  motor has stopped. The effects were left as the authors' on purpose; only
  the positions moved, because they belong to the mesh.

Where to look: Southern Watch D6 Long Reach and SEST Banda - Black Widow
Debut field YF-23s on `AirToAirIntercept` (two `yf23_aim424_internal` each);
the Super Hornets' MH CAP 424, MH Interceptor 424 and MH Penetrator 424 fits
carry `usn_aim-424`.

**Licence (23 Oct 2026): a known exception.** The YF-23's and the Fury's
`LICENSE.txt` (RSG, maintainer AlpineStatic; in the export since 5 Oct) let
a compatibility patch add content alongside the mod but not override its
material. The `yf23_aim424_internal` and `fury_aim424` extends above do
override it. The owner recorded them as a known exception on 23 Oct rather
than ask RSG or drop them (`docs/workshop-refresh-20261023-review.md`,
section 4). If RSG asks, those two ids come out of the AIM-424 build and the
rounds fly as their author shipped them. `usn_aim-424` (U.S. Navy 2027, US
Naval Aviation) is not covered by that licence.

## Enemy missile models, 15 Nov 2026

Some enemy rounds were cloned by their mod from another weapon and left on that weapon's
model. The one the player sees first is in Sulu Line 01, The Island Road: the two Peykaaps'
Nasir, the only enemy missile in that mission, flies as the game's AGM-84 Harpoon. SEST
Collection Fixes now draws sixteen such rounds with a model of their own family. Each model
is already shipped by another mod, or by the game, and a round of that type already uses it.

**How.** There is one `#!extend` per id, in
`integration/collection-fixes/SEST_Collection_Fixes/ammunition_overwrite/<id>_SEST.ini`.
Line 1 is `#!extend ammunition/<id>.ini`. Then come comment lines, one `[Models]` block and,
where the new mesh's nozzle sits elsewhere, a `[Particles]` block of effect positions only.
0.9.2 applies these itself, with no preloader:
- the game registers every modifier file of every layer and reads the extends before the base;
- the first value of a key wins, so only the keys the stub sets change;
- a blank `ResourcesMeshForLaunch` or `ResourcesMeshCanister` is skipped, so no stage part is drawn.

The 14 Nov Player.log shows the game's registry holding all 243 of the pack's extend and
prepend files, the three AIM-424 stubs in this folder among them. Nothing at runtime measures
the mesh, so each round keeps its author's flight model, seeker, warhead, signature, effects
and name. `build_missile_models` in `integration/collection-fixes/build_patch.py` writes the
files from `MISSILE_MODELS`; `tools/consolidate_packs.py` copies them into
`integration/dist/SEST_Integration/ammunition_overwrite/` (19 files with the three AIM-424
stubs).

| Id | Round the stub lands on | Was drawn as | Now drawn as (model block from) | Positions moved | Fielded |
|---|---|---|---|---|---|
| `ir_nasir` | Red Storm Arsenal (3413868677) | the game's AGM-84 Harpoon | the game's YJ-8 (C-801) body in Red Storm Arsenal's own YJ-83 paint (its `plan_yj83k.ini`); no booster, no launch part | all three to `0,0,-0.029`, the YJ-8's sustainer nozzle (the game's `plan_yj-8.ini`) | Sulu Line 01, 02, 04, 05; Southern Watch |
| `pla_yj-18` | PLAN Submarines (3594891803) | the stock Tomahawk | Modern PLAN Systems' YJ-18 (`plan_yj-18.ini`), torpedo-tube capsule for 2.9 s | underwater trail `0,0,-0.045` | Sulu Line 07 (Type 039C); Southern Watch 04, 10, 11, C1; Southern Reach 09, 11; Tasman Shield 01, 02, 03, 05, 09 |
| `wp_ss-n-27a` | Russian Submarines (3468260539) | the stock Tomahawk, mod paint | Russian Navy 21's 3M-54 Kalibr (`rfn_3m54.ini`), launch stage for 2 s | booster `0,0,-0.06` | Southern Reach 02, 04, 06, 07, 10; Southern Watch 09; Tasman Shield 08, 09 (Akula) |
| `pla_hq-10` | Type 003/004 carriers (3486502935) | the stock SA-N-5 Grail (Strela-2M) | Modern PLAN Systems' HQ-10 (`plan_hq-10.ini`) | - | Southern Watch D6 (Type 004) |
| `wp_9m317ma` | BUK-M3 (3564792549) | the SA-N-7 (9M38) | Russian Navy 21's 9M317M (`rfn_9m317m.ini`) | - | Southern Watch O7 (Buk-M3) |
| `wp_as-15`, `wp_as-15_antiship`, `wp_as-15_antiship_nuclear`, `wp_as-15_nuclear` | Tu-95 With AS-15 (3395022688) | the stock Tomahawk | the TU-160 mod's Kh-55 (3509329205 `KH-55.ini`), carriage part for 2 s | - | Southern Watch 08 (Tu-95MS) |
| `plan_pl-10` | Chinese Navy (PLAN) (3417801942) | the stock AA-8 Aphid (R-60) | the carrier mod's PL-10 (3486502935 `plaaf_pl-10.ini`) | booster and in-flight `0,0,-0.015` | Southern Watch 08, D6 (J-15A) |
| `plan_pl-15` | Chinese Navy (PLAN) (3417801942) | the stock AA-7 Apex (R-24) | the carrier mod's PL-15 (3486502935 `plaaf_pl-15.ini`) | booster and in-flight `0,0,-0.022` | Southern Watch 08, D6 (J-15A) |
| `plaaf_yj-83` | JH-7A (3526982088) | the mod's own KD-88 body (`KH-31/kd88.obj`) | Modern PLAN Systems' YJ-83 (`plan_yj-83.ini`) | in-flight `0,0,-0.0345` (the booster effect is None, so its position stays) | Southern Watch 08, D6 (JH-7A) |
| `pla_yj-83` | PLAN Submarines (3594891803), which beats 3486502935's identical copy | the stock YJ-8, an older missile with no intake | Modern PLAN Systems' YJ-83 (`plan_yj-83.ini`), without its ship-launch part (only J-15s carry it) | - | Southern Reach 09; Tasman Shield 04, 07, 09, 11; Southern Watch 11, C2, 08, D6 |
| `usn_rum-139c` | Euromod Main (3629144864) | the stock RUR-5 ASROC | the game's RUM-139A VL-ASROC (`usn_rum-139a.ini`) | - | Red Line O2 (enemy), 03 (neutral): JMSDF Maya |
| `plaaf_aspide-1a` | PLAAF Aircraft Pack (3812111085) | an AIM-7 root (`weapons/usn_aim-7`) no 0.9.2 file uses | the game's Aspide (`it_aspide_1.ini`) | booster `0,0,-0.0275` | Southern Watch 08, D6 (J-8B) |
| `plan_hy-1ja` | Chinese Navy (PLAN) (3417801942) | a Styx root (`weapons/wp_ss-n-2`) no 0.9.2 file uses | the game's HY-1 from the Silkworm collection (`plan_hy-1j.ini`) | booster `0,0.000098,-0.011548`, in-flight `0,0,-0.043` | Southern Watch 06, 11 (Luda 051DT) |

The Nasir is now the right family and shape, but noticeably bigger than the Harpoon it
replaces: the YJ-8 has about 1.6 times its side area, and a real C-704 (about 3.3 m) is
smaller than a Harpoon. No scale is set, by design (below).

**What the build stops on**, so nothing changes silently:
- the round's winning copy moving away from the recorded mod (paths compared without regard
  to case);
- that copy being an alias, extend or prepend itself, or any file in the load order naming
  the round in a `#!` header line;
- a mod shipping a file of the stub's name;
- the round's own `[Models]` `Resources*` or `[Particles]` position keys differing from what
  is recorded (`was`);
- its `[Models]` setting a mesh transform, stage or submodel key the new mesh would inherit;
- its setting `ResourcesMaterialFolder` when the entry does not;
- a position the entry moves that the round does not set;
- a laid value no longer matching the donor's file;
- the material the game reads not being the donor's own copy;
- an id in both `MISSILE_MODELS` and `AIM424_ROUNDS`;
- any entry setting a `Scale` key;
- any round the game reads (whole files, aliases, and every extend or prepend, SEST's own
  included) setting a `ResourcesMesh`, `ResourcesMeshForLaunch`, `ResourcesMeshCanister` or
  `ResourcesMeshForDebris` `Position`, `Rotation` or `Scale` key while drawn from a root an
  entry uses.

The last two guards exist because the loader hands every round of a root the same cached
template and writes those keys onto it, so a transform on one round moves, turns or scales
every other round of that root. A scale on the Nasir would also shrink the game's YJ-8 and
Red Storm Arsenal's YJ-82, YJ-83A, YJ-83K and YJ-83KH. Today no round sets one on these roots.

**Left alone, with reasons:**
- `jp_aam-3` (F-2A 'Viper Zero', 3755769170): drawn as the game's AIM-9L in its author's
  own Type 90 paint. No AAM-3 model exists in 0.9.2 or any mod. The Sidewinder is the same
  class and size; the other built-in short-range missiles are less alike.
- `jp_aam-4`: drawn as the game's AIM-7M in its author's paint. The AAM-4 has the Sparrow's
  layout at about its size, and no AAM-4 model exists.
- `wp_3m-25` Meteorit (3587091564; THE REDFOR MOD's copy is the same): drawn as the game's
  SS-N-12 Sandbox, a root the game itself uses. No Meteorit model exists, and the Sandbox is
  the same bureau's heavy supersonic cruise missile, the nearest built-in one.
- `plaaf_ld-8a` and `plaaf_ld-8a_s` (3812111085): anti-radiation missiles, which their author
  describes as derived from the PL-15 airframe, so the PL-15 body is their own. The J-20
  mod's `ld-8a.obj` has no clipped-fin internal-bay version for the `_s` round.
- No mesh scale for the Nasir. The YJ-8 body stays about 40% longer than a real C-704 rather
  than set `ResourcesMeshScale` on a shared template.

**Held back: the KD-88 pair.** `pla_kd-88` (the carrier mod's, 3486502935) and `plaaf_kd-88`
(SEST's own whole file, from 3486502935's) both fly as the stock AM39 Exocet. The model to lay
is the PLAAF Aircraft Pack's (3812111085) `kd-88.obj`. But the J-10C (3481228992) and JH-7A
(3526982088) mods both ship `assets/models/ammunition/KD-88/` and outrank it, and the game's
file index ignores case, so a `kd-88.obj` of theirs would replace that mesh. The export has no
binaries. On the PC, list `3481228992\assets\models\ammunition\KD-88` and
`3526982088\assets\models\ammunition\KD-88` under the workshop folder. If neither has a
`kd-88.obj`, or its hash matches 3812111085's, add `pla_kd-88` to `MISSILE_MODELS` (the
entry is written out above `MISSILE_MODELS_DEFERRED` in the builder). Then lay the same
`[Models]` keys and `InFlightEffectPosition=0,0,-0.0345` in the `plaaf_kd-88` block of the
builder's `main()`.

**Still wrong after this, for later** (the overrides do not touch them):
- Southern Watch 02: the 039B's `plan_yj-18` flies the whole flight as the torpedo capsule.
  The PLA & PLAN & PLAAF AEP (3789188689) extends it with `ResourcesMesh=torpedo`.
- Sulu Line 07, Tasman Shield 09 and 11: the 052D's `plan_yj-18a` and `plan_yj-20` fly as
  their `launch` parts. The AEP extends set `ResourcesMesh=launch`.
- `pla_df-21c`: the AEP extend sets `ResourcesMesh=dummy`.
- Not fired by an enemy in any campaign, so not in this release; the same table can take
  them later: Red Storm Arsenal's `ir_kowsar`, `ir_cm_90`, `plan_c_802` and `plan_yj_7`
  share the Nasir's Harpoon block (for `plan_c_802` the natural model is Red Storm Arsenal's
  own `plan_yj_82` block). SEST Replenishment's own `plan_yj18` and `plan_yj18_sub` are drawn
  as the Tomahawk.
- `tools/check_dependencies.py` does not open `ammunition_overwrite/`. Every donor is already
  a required mod where its rounds are fielded (each campaign's REQUIRED-MODS).

**Not demonstrated in game.** The model files are not in the export, and the YJ-18, 3M-54,
9M317M, KD-88, PL-10, PL-15, YJ-83K, Aspide, Kh-55, HQ-10 and HY-1JA meshes do not appear in
the captured logs. On the PC:
- The Island Road should log `LoadMaterialFromFile(weapons/plan_yj-8/plan_yj_83_mat.ini)`
  and no `weapons/usn_agm-84/plan_yj83_mat.ini`. The Nasir should be a C-801-style body
  (cruciform mid-body wings and tail fins) in YJ-83 paint, with no booster and the plume at
  the tail. If the plume floats behind the tail or sits inside it, set all three positions
  to `0,0,-0.0345`.
- If the AEP's own `YJ-18.obj` differs from Modern PLAN Systems', use the `yj-18_ac.obj`
  root for `pla_yj-18` instead.
- The fallback for `wp_9m317ma` is `weapons/wp_sa-n-12/wp_sa-n-12` with `wp_sa-n-12_mat`.
- US ships' RUM-139A stay the RUR-5 (Euromod Main replaces the game's `usn_rum-139a.ini`),
  so the Maya's RUM-139C is the only VL-ASROC drawn with the game's model.
- What each symptom means:
  - a plume with no body: the root did not load;
  - several parts drawn over each other: the `ResourcesMesh` name was not found in the
    root, so the whole root became the main mesh;
  - a white body: a material or texture is missing.

  `[Debug] WriteLogToFile=True` in `usersettings.ini` writes "Could not load weapon resource"
  and "OBJ file not found at path" to the session `.html` log. If an entry misbehaves, revert
  that one entry or switch it to its fallback.
