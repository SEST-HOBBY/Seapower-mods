# SEST Replenishment At Sea

Sea Power ships a complete ship-to-ship replenishment mechanic and leaves it switched off.
This pack turns it on, and — the part that actually matters — makes it *reach* a modern
fleet: **276 modern hulls** carry launchers that **can never be reloaded by anything**,
whatever is tied up alongside.

Built alongside **[RE-power: naval resupply in the missile age](https://steamcommunity.com/sharedfiles/filedetails/?id=3605013271)** (3605013271), which is now subscribed and exported
under `mods-source/`. RE-power settles the one question the data alone could not: the vessel
supply system that actually WORKS in game is `SystemName=TruckSupplySystem` — all 23 of its
field-tested ship suppliers use it, and its bundled reference doc gives the `TargetTypes`
vocabulary as `"LandUnit", "Vessel" or "Submarine"`. The dormant `VesselSupplySystem` name from
vanilla's commented block appears in no working file anywhere, so this pack uses the proven
name (and inherits vanilla's "Ammunition supply" panel label for free).

SEST is tier 0, so for the nine hulls both packs touch, whatever this pack ships is what the
player gets. It therefore forks **vanilla**, not RE-power. That is a reversal: it forked
RE-power first, on the ordinary rule of forking the copy the player actually sees, and on the
belief that RE-power's only change to those hulls was the supply block. Measured, that is not
true — outside the supply block RE-power changes **142 lines** across the nine, and not
cosmetically. It deletes the whole `[OpticalView]` section, drops the Sacramento's `ArmorType`
from `Minor` to `None`, raises `MaxAccelerationFactor` from 0.21 to 2.4, retunes `LinearDrag`
and the acoustic figures, and removes `CavitationSpeed` and `Prairie`. Forking that copy meant
re-publishing every one of those edits at tier 0 under this pack's name, on hulls whose only
reason to be here is a supply block. So: vanilla hull, SEST supply block, nothing else
inherited. RE-power keeps its own hulls — its fourteen merchant-freighter suppliers are
untouched by this pack and keep working below.

## Why RE-power's ships still can't pass an anti-ship missile

RE-power's own description says it: *"Most guns and AA missiles can be replenished without
any issue, but most Anti-ship missiles and torpedoes cannot."* There are **two** reasons for
that and uncommenting the Sacramento's supply block fixes neither.

**1. The category gate.** Ammunition that declares `SupplyCategory=X` can only be handed over
by a supplier that lists `AccountableAmmunitionCategory_N=X,<count>`. Guns and point-defence
SAMs declare no category, so they flow freely — which is exactly the half that works today.
Every Harpoon, every ship torpedo and every SS-N-12/19/22 declares one. Vanilla stocks those
categories on *flight decks* only, so `SovietAdvancedASM` is a total orphan: stocked by zero
suppliers anywhere in vanilla or in the 131 exported mods.

**2. The launcher gate.** A launcher fed by an `AssociatedMagazine=` refills when its magazine
does. A launcher holding a bare `Ammunition=` — a sealed canister, a deck rail, a fixed tube —
is one-shot forever unless it carries `ReloadableWithoutMagazine=True`. Vanilla spells this
out on the Long Beach's Mk141 Harpoon canisters, which set it `False`. Across vanilla and all
131 exported mods that flag appears on exactly **11 units and every one is a land SAM TEL**. No vessel
anywhere sets it.

Gate 2 is far more expensive than it looks. **Red Storm Arsenal models every Mk41 cell as its
own launcher with a bare `Ammunition=` line**, so without this pack not one VLS round on any
of the 103 hulls (of its 115) that carry one could ever be replenished.

#### The scale of gate 2

Across the 736 vessel files in the 27 modern mods the builder reads, there are **7 251**
launcher sections. Sorting them by how they are fed:

| | Launchers | |
|---|---:|---|
| No `Ammunition=` at all | 5 075 | guns fed from a magazine, decoy dispensers, empty loadout stubs — not affected |
| `Ammunition=` **and** an `AssociatedMagazine=` | 93 | reloads today, exactly as vanilla intends |
| **Bare `Ammunition=`, no magazine, no flag** | **2 083** | **one-shot forever** |

So of the launchers that actually hold a missile, **2 083 of 2 176 — 96% — cannot be
replenished by anything**. They sit on 276 hulls:

| Mod | Hulls | Launchers |
|---|---:|---:|
| Red Storm Arsenal | 103 | 1 185 |
| PLAN Pack | 25 | 275 |
| Modern US Navy | 48 | 200 |
| Russian Navy 21 | 12 | 117 |
| Euromod — Modern German Navy | 17 | 52 |
| Euromod — Modern British Navy | 11 | 37 |
| Euromod — Modern Dutch Navy | 7 | 35 |
| Euromod — Modern Italian Navy | 6 | 34 |
| *18 further mods* | 47 | 148 |

The distribution is long-tailed and the tail is where the damage is. 17 hulls carry a single
affected launcher; RSA's arsenal ships `usn_aem_nathan_hale` and `usn_aem_james_madison` carry
**68 and 50** — each one an eight-cell Mk41 module holding `Ammunition=usn_rgm_109b3` and no
magazine, so the Nathan Hale's 544 Tomahawk cells are, without this pack, a single magazine
that empties once and never fills. The Type 052D and Type 055 variants carry 26–30 apiece.

This pack flags **2 078 launchers on 274 of those hulls — every one it is entitled to touch**.
The remaining 5 sit on three hulls owned by sibling SEST packs (`js_ffg_mogami`,
`rn_lph_ocean`, `usn_ddg-1000_cps`), which apply the same fix in their own builders.
2 078 + 5 = 2 083. The headline "2 080 launchers across 292 hulls" adds the 10 upstream
suppliers and 8 clones this pack also writes, which between them contribute 2 more; a
supplier's own point defence is nearly always magazine-fed already.

### The broken store references

Getting to full coverage meant dealing with 13 hulls the builder used to skip because they hang
an ammunition id nothing in the collection defines. Skipping them cost 77 launchers — including
the Kansas-class's 20 ESSM cells — over a reference that is broken with or without this pack.
Three things were wrong, and they were three different things:

**Two were not broken at all.** `DateBased_HWT` is a stock mechanic, not a store: a file
declares `DateBased_HWT=0,ger_dm2a4|2035,ger_dm2a5` and then writes `Ammunition1=DateBased_HWT`,
so the name resolves to whichever round the scenario date selects. Nineteen declarations across
the collection use it, vanilla submarines included — `integration/allied-fixes` had already
recorded this and the replenishment builder did not know. And the Han's torpedo room declares
`NumberOfAmmunitionTypes=3` while listing four, so its `Ammunition4=wp_ss-n-15` is text the
engine never reads. Both hulls were being skipped over a reference that does not exist.

**Six were a typo away from a round the same mod already ships**, and are now repaired in the
copy this pack was forking anyway — the shape `integration/allied-fixes` established for the
P-8's `usn_agm-84g`. Fix the *reference*; never invent the id, because claiming a name upstream
may yet ship would put SEST tier 0 in front of the real thing:

| Hull | Mod | Wrote | Meant |
|---|---|---|---|
| `usn_cg_kansas_late` | Red Storm Arsenal | `usn_rim_162essm` | `usn_rim_162a` |
| `wp_skr_admiral_gorshkov_m_rsa` | Red Storm Arsenal | `wp_ss-n-27` | `wp_ss_n_27` |
| `plan_ddg_type051m` | Red Storm Arsenal | `plan_hhq-7a` | `plan_hq_7` |
| `plan_ffg_type_054_rsa` | Red Storm Arsenal | `pla_hq-7` | `plan_hq_7` |
| `rn_type23`, `plan_ddg_luda_typ_051` | Modern RN, PLAN | `usn_rgm-84` | `usn_rgm-84d` |
| `rnn_ddg_zeven` | Euromod Dutch | `ita_cal_127mm_vulcano` | `leo_cal_127mm_vulcano` |

Each of those launchers previously had **no round at all** in game. The Harpoon target is
vanilla's Block 1C deliberately, so that repair cannot depend on a mod staying subscribed.

**Four are genuinely missing content and are left alone** — but the hulls are now patched
anyway, because a broken reference is no reason to withhold the launcher fix from the rest of
the ship. `wp_deploy_mine` (Dutch Van Galen) has no counterpart: the only mines in the
collection are Spanish. `plan_f3200a` (Fujian) is declared with `Ammunition1_Count=0`, a
placeholder for a weapon the mod has not shipped. And RSA's nine `_spawner_usa_*` /
`_spawner_wp_*` ids follow the `ship_spawner_usv` pattern — an ammunition file of
`Type=Fueltank` carrying `OnHitGroundSpawn=<land unit>` — which RSA references and never
ships; writing them would be authoring that mod's landing mechanic. `check_dependencies` now
reports all ten at every run without failing, on the same rule it uses for system names: a
reference an upstream unit file also carries is upstream's, one this repo introduced is ours
and still fails the build.

And a third problem no mod can fix by tuning: the collection has twelve replenishment-capable
hulls and all but two are Cold War. A 2025 task force had nothing to replenish *from*.

## What the pack does

| Stage | Result |
|---|---|
| **Suppliers** | 10 upstream auxiliaries get a tuned `[SupplySystem1]` |
| **New hulls** | 8 modern replenishment ships — 5 BLUE, 3 RED — 25 named ships, as **new unit ids** |
| **Metering** | 85 heavy rounds get a counted `SEST_` supply category; 4 rounds repaired |
| **Refit** | every clone's donor-era radars, EW and guns retuned to its own navy and decade |
| **Repairs** | 6 broken upstream ammunition references fixed — launchers that had no round |
| **Launchers** | **2080 launchers made reloadable** — 2078 on 274 modern hulls, every one it can reach |

### The suppliers

`MaxAmmoPoints` is the size gate: a round costing more than it is refused outright, and
**omitting the key means no cap at all** — which is exactly how vanilla lets
`tgt_ammo_depot_small` reload an SA-5 that a truck capped at 200 cannot touch. Reference
costs: RAM 126–150 · ESSM 500–700 · Mk46/Mk54/MU90 460–728 · VL-ASROC 1217 · Harpoon 1725 ·
SM-2MR 1400–1768 · Tomahawk 4350 · Mk48 ADCAP 4695 · SS-N-12 7740 · NSM / SM-6 IB 8000 ·
Onyx 5000 · SM-3 9000 · Zircon 10000 · SS-N-22 12300 · SS-N-19 Granit 21000.

| Hull | Nation | Pool | Ceiling | Range | Speed | Stocks |
|---|---|---|---|---|---|---|
| Sacramento AOE | US | 600 000 | **none** | 1.0 nmi | 13/16 kn | Harpoon 40 · AirTorpedo 60 · ALWT 24 · LandAttack 24 · LongRangeSAM 32 |
| **Algol T-AKR** *(sealift, not RAS)* | US (MSC) | 500 000 | **none** | 0.5 nmi | **8/12 kn** | Harpoon 40 · AirTorpedo 48 · ALWT 24 · LandAttack 32 · LongRangeSAM 32 |
| Kilauea AE | US | 500 000 | **none** | 1.0 nmi | 13/16 kn | Harpoon 60 · AirTorpedo 90 · ALWT 40 · **Nuclear_ASW 4** · LandAttack 40 · LongRangeSAM 60 |
| Boris Chilikin AOR | Soviet | 200 000 | 13 000 | 0.5 nmi | 13/16 kn | **SovietAdvancedASM 24** · AirTorpedo 40 · LandAttack 16 |
| Don tender | Soviet | 150 000 | 8 000 | 0.3 nmi | 5/8 kn | SovietAdvancedASM 12 · AirTorpedo 30 · LandAttack 12 |
| **HMAS Supply AOR** *(SEST RAN Fleet)* | Australia | 160 000 | 8 000 | 0.5 nmi | 12/16 kn | Harpoon 16 · AirTorpedo 24 · LandAttack 8 · LongRangeSAM 16 |
| Teide oiler | Spain | 120 000 | 2 000 | 0.5 nmi | 12/16 kn | Harpoon 16 · AirTorpedo 24 · ALWT 8 |
| T2 oiler | US | 60 000 | 2 000 | 0.5 nmi | 13/16 kn | Harpoon 8 · AirTorpedo 16 |
| Kazbek tanker | Soviet | 60 000 | 2 000 | 0.5 nmi | 13/16 kn | AirTorpedo 16 |
| Sealift Pacific T-AOT | US (MSC) | 40 000 | 2 000 | 0.5 nmi | 13/16 kn | AirTorpedo 8 |
| Delvar | Iran | 15 000 | 2 000 | 0.3 nmi | 8/12 kn | AirTorpedo 4 · Harpoon 2 |

The Algol is the one entry that is **not** `Role=RAS` — it is `Role=Transport`, an MSC fast
sealift Ro-Ro. It sits in the uncapped top tier on its own merits: at **288 m it is the longest
hull in this table**, longer than the Sacramento, with 31 cargo slots of military materiel, and
strategic sealift is exactly the thing that moves the heaviest items. It will pass a Granit at
21 000 like the ammunition ships. What it lacks is a replenishment rig, and that is where the
cost sits instead of in a ceiling: **45 points/sec against an AOE's 120, and 8 kn on a hull that
makes 33.** It carries anything, slowly, very nearly stopped.

Boris Chilikin's 13 000 ceiling is threaded deliberately between SS-N-22 Moskit (12 300) and
SS-N-19 Granit (21 000) — Granit's angled below-deck silos genuinely are not reloadable at
sea. Kazbek gets no `SovietAdvancedASM` line on purpose: every round in that category costs
7740 or more, so the 2000 ceiling blocks it anyway and a stocked-but-unreachable category is
just a dead line in the supply panel.

### The new modern hulls

New unit ids cloned from vanilla donors — the donors are untouched and both ships coexist,
exactly as `integration/ran-fleet` does it. Donors are picked on hull length, because the
mesh is what the player sees.

| Bloc | Class | Donor | Ships | Pool | Ceiling |
|---|---|---|---|---|---|
| BLUE | **Supply-class T-AOE** | Sacramento (242 m ← 229 m) | Supply · Rainier · Arctic · Bridge | 700 000 | **none** |
| BLUE | **Lewis and Clark T-AKE** | Kilauea (172 m ← 210 m) | Lewis and Clark · Sacagawea · Amelia Earhart · Washington Chambers | 550 000 | **none** |
| BLUE | **Henry J. Kaiser T-AO** | Teide (118 m ← 206 m) | Henry J. Kaiser · John Lenthall · Walter S. Diehl · Rappahannock | 80 000 | 2 000 |
| BLUE | **Mashuu-class AOE** | Sacramento (242 m ← 221 m) | Mashuu · Omi | 250 000 | 5 000 |
| BLUE | **Tide-class AOR** | Sacramento (242 m ← 201 m) | Tidespring · Tiderace · Tidesurge · Tideforce | 180 000 | 5 000 |
| RED | **Type 901 Fuyu AOE** | Sacramento (242 m ← 241 m) | Hulunhu · Chaganhu | 400 000 | 9 000 |
| RED | **Type 903A Fuchi AOR** | Boris Chilikin (162 m ← 178 m) | Taihu · Chaohu · Honghu · Luomahu | 220 000 | 5 000 |
| RED | **Project 23130 Akademik Pashin** | Kazbek (145 m ← 130 m) | Akademik Pashin | 90 000 | 2 000 |

The Kaiser is the weakest match by a distance — the Teide is the only proper fleet-oiler
silhouette in the collection and it is 88 m short. If a better donor ever appears, it is a
one-line change in `CLONES`.

**The bloc split is why the last two exist.** Before them the modern half of this table was
five BLUE hulls and one Chinese one, and RED's only other choices were the Boris Chilikin, the
Kazbek and the Don — all Cold War. A RED task force in 2025 had a supply ship; it did not have
a modern one. The bloc also rides in the mission editor: the `Type=` line reads
`Replenishment (BLUE)` or `Replenishment (RED)`, so the eight group into two adjacent blocks
in the unit list instead of scattering through *Fleet Auxiliary*.

The Fuchi and the Pashin are **unarmed**, and that is not an oversight. Their donors carry no
weapon mounts, the refit rule below forbids adding geometry that is not in the donor mesh, and
both real ships are unarmed too — the Pashin has provision for two AK-630 that were never
fitted. Give them an escort.

### The refit

A clone is its donor plus a supply block, and for five of the eight that donor is a 1960s
Sacramento. Left alone, a 2017 Chinese replenishment ship sails with an SPS-40, a NATO Sea
Sparrow launcher and an AN/SLQ-32 — a US Navy fit twenty years older than the ship, on the
wrong navy. So each clone's systems are retuned to its own flag and decade:

| Bloc | Ship | Search | EW | Point defence |
|---|---|---|---|---|
| BLUE | Supply T-AOE | AN/SPS-49(V)5 · AN/SPQ-9B | SLQ-32A · SLQ-32(V)6 | Phalanx 1B · **ESSM** in the Mk29 |
| BLUE | Lewis and Clark T-AKE | AN/SPQ-9B | SLQ-32A | Phalanx 1B · **Mk110 57 mm** replacing the 3″/50s |
| BLUE | Henry J. Kaiser T-AO | AN/SPQ-9B | — | Bofors 40 mm **L/70** replacing the L/60 |
| BLUE | Mashuu AOE | OPS-48 · OPS-20 | **NOLQ-2** | Phalanx 1B · ESSM |
| BLUE | Tide AOR | **Artisan Type 997** · SharpEye | **Thales UAT** · Type 1048 | Phalanx 1B · **Sea Ceptor** in the Mk29 |
| RED | Type 901 Fuyu | **Type 382 · Type 364 · Type 347G** | **RJZ-726** | **Type 730 ×2** (30 mm magazine) · **HQ-10** in the Mk29 |
| RED | Type 903A Fuchi | Type 364 | — | unarmed |
| RED | Project 23130 | MR-760 | — | unarmed |

**The rule is retune, never restructure.** Exactly three keys are ever rewritten: `SystemName`
inside a `[SensorSystemN]` or `[WeaponSystemN]` section, and `Ammunition1` inside a
`[WeaponMagazine*]` section. `Mount`, `Collider`, `Container`, `Gun`, `FiringArcs` and every
mesh section stay the donor's, because those name geometry that exists in the donor model and
nowhere else. A refit therefore changes what a system *does*, never what it looks like — the
Type 901 still shows Phalanx barrels while shooting like a Type 730. That is the same trade the
donor choice already makes.

Half-swaps are the trap, and the table is what closes it: giving the Type 901 a Type 730
without moving its magazine from `usn_cal_20mm` to `plan_cal_30mm` would have left it with a
CIWS and nothing to fire. Both live on one row.

**Missile launchers keep their `SystemName` and are refitted through the magazine instead.**
That is the one exception to "a SystemName is behaviour", and it is not obvious: `[MK29]`
declares eight `AttachmentPosition` entries and `[HQ-10_24]` declares twenty-four, and those
are mesh-relative coordinates for where each round is *drawn* on the mount. Swapping the Type
901's Mk29 to an HQ-10 launcher — the obvious move — would have rendered twenty-four missiles
at another launcher's geometry on a box with eight rails. So the Type 901 fires HQ-10 *from a
Mk29*, and the Tide fires Sea Ceptor from one. Guns and sensors carry no such geometry —
`[MK15]` and `[Type_730]` are rates, arcs and effects — and swap freely.

**Every slot is a preference list, not a name**, and the builder picks the first entry your
collection actually defines. The good radars live in Red Storm Arsenal, Euromod, the PLAN packs
and Russian Navy 21; hard-coding one would silently break the ship for anyone not running that
mod. Every list ends in a name **vanilla itself** carries, so the floor is always reachable —
and the build log prints the arrow it took for each ship, which is the only way to see whether
a slot got what it asked for or fell through to the tail.

### The metering

Every modern VLS round in the collection — SM-2/3/6, ESSM, RAM, Tomahawk, LRASM, NSM, Kalibr,
Onyx, Zircon, YJ-18 — carries **no** `SupplyCategory`. Turn the supply system on and stop
there and a single 600 000-point pool hands out 138 Tomahawks with nothing rationing them.
So the heavy ones get one of two new categories. **Which rounds those are is derived from the
data on every build, not hand-listed** — a hand-written list looked reviewable and was wrong:
it caught the dash-named vanilla and Euromod ids and missed Red Storm Arsenal's entire
underscore-named parallel family, where `usn_rgm_109c3` alone sits in 90 launchers. A round is
metered when **all** of these hold:

- some vessel carries it;
- `Type=Missile` — torpedoes and ASROC stay commodity ordnance, and the ones worth counting
  already carry vanilla's `AirTorpedo` or `ALWT`;
- `TargetType` is `ASuW` → **`SEST_LandAttack`**, or `AAW` → **`SEST_LongRangeSAM`**.
  `TargetType=ASW` is a stand-off ASW round (SS-N-14/16) and stays free;
- `AmmoPoints > 2000` — above
  everything meant to top up anywhere — VL-ASROC 1217, SM-2MR 1400–1768, Harpoon 1725, Exocet
  and YJ-83 1675, ESSM 500–700, RAM 126–150, every gun and CIWS round — and below the cheapest
  strike and area rounds (Otomat-family 2422, SM-2ER 4080, Tomahawk 4350);
- it declares no `SupplyCategory` already — vanilla's own six categories win;
- **no aircraft hangs it on a station, directly or via an `#!alias` descendant** — an alias
  file inherits the tag from its target, so a parent is only taggable if its whole family is
  clear. (Today this excludes nothing: every real conflict turns out to be a land unit.);
- **no land unit carries it** — the three land suppliers stock no categories at all, so
  tagging a round they service takes away the one supply path the game already ships working.
  Red Storm Arsenal's `usa_tomahawk_launcher` fires `usn_rgm-109b`, which is exactly why that
  round is left free.

Lookups are **case-insensitive** (the game runs on NTFS; the Visby hangs `swe_RBS15_mk4`, the
file is `swe_rbs15_mk4.ini`) and alias chains are resolved before judging a round.

That comes to **85 rounds** today (56 land-attack, 29 area-SAM) and 8 deliberate exclusions,
all of them land-battery rounds. The builder prints four deterministic audit lists on every
run — metered, excluded (with the reason), heavy uncategorised rounds nothing carries, and the
**63 ship/sub-carried missiles with no usable `AmmoPoints`** anywhere in their alias chain.
Those 63 cost nothing and can never be metered; inventing prices for them would change every
magazine that holds them, so they are reported and left to their upstream mods.

Four rounds also get two stripped keys put back. The two lines are inserted into the copy the
game actually loads, **not** a wholesale revert to vanilla: `3395022688`'s `wp_ss-n-19` differs
from vanilla by 118 lines, and reverting it would quietly undo that mod's entire point
(Power 137→82, ImpactSize VeryLarge→Large, the sea-skimming profile). Only the missing
`AmmoPoints` and `SupplyCategory` lines move; `tools/check_pack_fidelity.py` proves every other
byte matches upstream.

| Round | Restores | Stripped by |
|---|---|---|
| `usn_rgm-84d` | 1725 / Harpoon | Mogami-class Frigate (3456859157) |
| `usn_agm-84d` | 1350 / Harpoon | 3430135740 |
| `wp_ss-n-12` | 7740 / SovietAdvancedASM | Tu-95 with AS-15 (3395022688) |
| `wp_ss-n-19` | 21000 / SovietAdvancedASM | Tu-95 with AS-15 (3395022688) |

`usn_rgm-84d` matters most: the whole Euromod Harpoon Block II tree aliases it, so today that
entire family costs zero points and carries no category at all.

## Speed, range and units

`SupplyRange` is **nautical miles**, not statute — the ini comment says "In miles" but
`language_en/ui.ini:2685` renders it `Supply range: ${SupplyRangeInMiles} nmi.`

`MaxOwnVelocity` is 13 kn for blue-water hulls, not the commented template's 6. Real underway
replenishment runs at a base course and speed of 12–16 kn; 6 kn is not RAS, it is an alongside
transfer. 13 sits **below** the top speed of every blue-water supplier here (Sacramento 26,
Kilauea 20, Boris Chilikin 16, Sealift Pacific 16, T2 14, Kazbek 14, Don 18), so replenishing
costs the task force its speed of advance and is a real tactical decision. Receivers get 3 kn
more headroom, preserving the supplier<receiver relationship the vanilla template already has
at 6/10, so an escort settling onto station does not abort the transfer on a momentary
overspeed. Two hulls are clamped because 13 would be above their top speed: Teide and HMAS Supply,
both 12 kn. The Delvar (8) and the Don tender (5) sit *below* their hull speed of 11 and 18
on purpose — a 64 m coastal auxiliary and a Project 310 submarine tender do alongside work,
not underway RAS.

## Submarines, and the surfacing question

Every supplier — the ten patched hulls, the eight clones and HMAS Supply — carries
`TargetTypes=Vessel,Submarine`, so a boat can rearm from whatever it reaches, with each
supplier's own ceiling, pool, categories, range and speed gates deciding what actually moves:
an oiler passes a surfaced boat its torpedo-class rounds while Kalibr-class weapons need an
ammunition ship, exactly as for surface receivers. No combatant gains a supply system.
`Submarine` as a value is field-proven — RE-power's Don tender and Sealift Pacific run it —
but always alone; the two-value `Vessel,Submarine` list rides on the only multi-value
precedent in the corpus (`Aircraft,Helicopter` on the KC-130s) and is test 1 on the checklist.

**TESTED IN GAME, 2026: a submerged submarine DOES replenish.** The engine applies no
surfaced-state check of its own. This was the pack's one open blocker and it resolved the
unwelcome way: there is no data-side fix, because no supply key anywhere mentions depth or
surface state, RE-power's own submarine suppliers carry no such key, and `language_en/ui.ini`
offers only the generic `Replenishment unavailable.` string. The one candidate that looked
like a lever — `EnabledSurfaced`, 90 occurrences — turned out to be cosmetic: it appears
*only* in `[Sail_Submerged]` / `[Sail_Surfaced]` mesh sections, 45 pairs, swapping the
conning-tower model. It gates nothing.

**Decision: underwater resupply is left enabled, as a house rule rather than a mechanic.**
Surface your boats. This is a deliberate choice to keep the capability rather than lose
surfaced rearm along with it, and it is revisitable — dropping `Submarine` from
`SUPPLIERS` in `integration/common/ras.py` closes it completely, because RE-power's only
other submarine-capable unit is `nv_pt_boats_docks_small`, a dock, where a boat *should*
rearm. All 14 of its merchant suppliers are `TargetTypes=Vessel` and cannot touch a
submarine. So the at-sea case is entirely ours to give or withhold.

What this pack will NOT do is fake the restriction by rewriting every submarine.

## Dependencies

None hard. The pack patches whatever it finds: the ten supplier hulls come from vanilla plus
Euromod Cold War Spanish, and the launcher fix covers 22 mods it detects at build time. The
eight new hulls ride vanilla Sacramento / Kilauea / Boris Chilikin / Kazbek and Spanish Teide
meshes, so those must stay enabled. RE-power (3605013271) is optional and complementary.

The refit is the one part that is **built against your collection rather than shipped fixed**.
Its preference lists resolved to Red Storm Arsenal, Euromod, Modern US Navy, the PLAN packs and
Russian Navy 21 on this build; disable one of those and *rebuild* and the affected slots fall
back to a vanilla system instead. Disable one *without* rebuilding and that slot names a system
the game cannot find — so re-run the builder after changing your subscriptions, which is what
`tools/check_dependencies.py` now checks for: it resolves every `SystemName` the packs ship and
fails on any this repo introduced that nothing defines.

RE-power now has a `mods[]` entry in `data/mod-catalog.json` (`re-power-resupply`) and is
exported under `mods-source/3605013271/`, so the conflict tooling sees it.

## Install

Nothing special: this pack is consolidated into `SEST_Integration` like every other, and the
load order does not change.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1
```

## First-flight checks

These are the things that cannot be settled from the files, in the order worth testing.

1. **The system-name question is settled** — the pack emits `SystemName=TruckSupplySystem`,
   the name all 23 of RE-power's field-tested ship suppliers use. Baseline check: put a
   Sacramento and a depleted escort in a mission, use the per-unit `Stores=` key
   (`Depleted | Few | Medium | Full`) to create a real deficit, and confirm the supply panel
   appears and transfers run.
2. **Does an Mk141 canister actually refill now?** This is the whole point of stage 4. A
   Mogami (Harpoon, 1725) or a Hobart (NSM, 8000) inside 0.5 nmi of HMAS Supply at 12 kn
   should take its anti-ship rounds back. HMAS Supply's ceiling is 8000 precisely so it
   clears the NSM its own fleet carries.
3. **`TargetTypes=Vessel,Submarine` as a two-value list — PROVEN in game.** Every supplier
   carries it and it parses: submarines and surface ships both receive. RE-power only ever
   uses one value per hull, so this was the riskiest line in the pack — if the comma had not
   parsed, all 19 suppliers would have failed at once, not just the submarine half. The
   fallback is no longer needed, but for the record it was two `[SupplySystemN]` blocks per
   hull, one per target type.
4. **Whether a category-tagged round also charges the points pool** is unknown — the
   flight-deck side runs the two ledgers independently, but there is no working supplier-side
   example. The numbers are safe under either reading; the *feel* will differ.
5. **`AmmoLoadSpeed` is per-target by inference**, from the vanilla `MaxTargets` comment
   "(same speed per target)". If it turns out to be divided among targets, every `MaxTargets=2`
   hull halves in throughput and the rates want roughly doubling.

## In-game test checklist

These cannot be run from the repo — the game is Windows-side. Until they pass, treat the
submarine half and the metering economy as provisional.

1. Surfaced submarine replenishes from an oiler (basic rounds only).
2. Heavy round rejected by an oiler's 2000-point ceiling.
3. The same round transfers from an AOR / ammunition ship whose ceiling admits it.
4. Don-class tender replenishes a surfaced boat.
5. At least one modern clone (T-AOE / T-AKE / Mashuu / Tide / Type 901) supplies.
6. ~~Periscope, shallow, deep and very-deep depth all refuse replenishment.~~ **FAILED — tested, a submerged boat replenishes. No engine-side depth check exists. Accepted as a house rule; see above.**
7. A boat diving mid-transfer stops the transfer by the next `UpdateDelay` tick. *(Expected to fail for the same reason — untested.)*
8. No ordnance-point or category deduction after a rejection or interruption.
9. Out-of-range and over-speed both refuse replenishment.
10. A bare (canister/tube) launcher and a magazine-fed launcher both refill.
11. An ordinary combatant with no supply system cannot supply anything.
12. Land-launcher resupply (Ural/M923/depot) and aircraft deck rearming are unaffected.

Tests 6–8 double as the verdict on the surfacing blocker above: if 6 fails, the engine does
not gate depth and the restriction cannot be provided from data.

## Known gaps

- **13 modern hulls are deliberately left alone.** They name a store nothing in the
  collection defines, and shipping a tier-0 copy would make SEST the owner of somebody
  else's dangling reference — which `tools/check_dependencies.py` fails on by design. The
  builder prints the list on every run; today it is `ae_ssk_s80_plus` (`DateBased_HWT`),
  `plan_cv_type_003` (`plan_f3200a`), `plan_ddg_luda_typ_051` and `rn_type23` (`usn_rgm-84`),
  `plan_ddg_type051m` (`plan_hhq-7a`), `plan_ffg_type_054_rsa` (`pla_hq-7`), `plan_ssn_han`
  (`wp_ss-n-15`), `rnn_ddg_zeven` (`ita_cal_127mm_vulcano`), `rnn_ffg_Van_Galen`
  (`wp_deploy_mine`), `usn_cg_kansas_late` (`usn_rim_162essm`), `wp_skr_admiral_gorshkov_m_rsa`
  (`wp_ss-n-27`), and `usn_lha_tripoli` / `wp_bdk_ivan_rogov_90` (amphibious `_spawner_` ids).
- **No shore-side counterpart.** All 40 vanilla `port_*.ini` objects and every dock have zero
  supply keys, and no mod adds a land supply source.
- **A carrier still cannot rearm its air wing at sea.** There is no way to top up a
  `FlightDeck_` magazine from a supplier. A task force can refill its VLS and not its
  squadrons — an asymmetry you will notice.
- **No mission-scope override.** Only the `FlightDeck_` family can be overridden per mission,
  so tuning a leaner or richer supplier means editing `integration/common/ras.py` and
  rebuilding.

## Rebuilding

```bash
python3 integration/replenishment/build_patch.py
```

Validates before writing a byte: every supplier hull and clone donor exists, no clone id
collides with an upstream unit, every tagged round resolves and hangs on no aircraft, every
restoration is still needed, and no path is one another SEST pack already owns.

The tuning table lives in `integration/common/ras.py` and is shared with
`integration/ran-fleet/build_fleet.py` (HMAS Supply, plus the launcher fix for all seven RAN
hulls) and `integration/jmsdf-mogami/build_patch.py` (the Mogami's Mk141 canisters). Those
packs own those files, and two packs shipping different bytes at one path is an unconditional
consolidation failure — so the transform is imported, never duplicated.
