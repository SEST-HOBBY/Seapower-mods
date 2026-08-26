# SEST Replenishment At Sea

Sea Power ships a complete ship-to-ship replenishment mechanic and leaves it switched off.
This pack turns it on, and — the part that actually matters — makes it *reach* a modern
fleet: 280 modern hulls currently have launchers that **can never be reloaded by anything**,
whatever is tied up alongside.

Built alongside **[RE-power: naval resupply in the missile age](https://steamcommunity.com/sharedfiles/filedetails/?id=3605013271)** (3605013271), which is now subscribed and exported
under `mods-source/`. RE-power settles the one question the data alone could not: the vessel
supply system that actually WORKS in game is `SystemName=TruckSupplySystem` — all 24 of its
field-tested ship suppliers use it, and its bundled reference doc gives the `TargetTypes`
vocabulary as `"LandUnit", "Vessel" or "Submarine"`. The dormant `VesselSupplySystem` name from
vanilla's commented block appears in no working file anywhere, so this pack uses the proven
name (and inherits vanilla's "Ammunition supply" panel label for free). SEST is tier 0: for the
eight hulls both packs touch, this pack forks **RE-power's copy** and replaces only its supply
block; RE-power's merchant-freighter suppliers keep working below.

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
of its 115 hulls could ever be replenished.

And a third problem no mod can fix by tuning: the collection has twelve replenishment-capable
hulls and all but two are Cold War. A 2025 task force had nothing to replenish *from*.

## What the pack does

| Stage | Result |
|---|---|
| **Suppliers** | 10 upstream auxiliaries get a tuned `[SupplySystem1]` |
| **New hulls** | 6 modern replenishment ships, 20 named ships, as **new unit ids** |
| **Metering** | 85 heavy rounds get a counted `SEST_` supply category; 4 rounds repaired |
| **Launchers** | **2003 launchers across 280 modern hulls** made reloadable |

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

| Class | Donor | Ships | Pool | Ceiling |
|---|---|---|---|---|
| **Supply-class T-AOE** | Sacramento (242 m ← 229 m) | Supply · Rainier · Arctic · Bridge | 700 000 | **none** |
| **Lewis and Clark T-AKE** | Kilauea (172 m ← 210 m) | Lewis and Clark · Sacagawea · Amelia Earhart · Washington Chambers | 550 000 | **none** |
| **Henry J. Kaiser T-AO** | Teide (118 m ← 206 m) | Henry J. Kaiser · John Lenthall · Walter S. Diehl · Rappahannock | 80 000 | 2 000 |
| **Mashuu-class AOE** | Sacramento (242 m ← 221 m) | Mashuu · Omi | 250 000 | 5 000 |
| **Tide-class AOR** | Sacramento (242 m ← 201 m) | Tidespring · Tiderace · Tidesurge · Tideforce | 180 000 | 5 000 |
| **Type 901 Fuyu AOE** | Sacramento (242 m ← 241 m) | Hulunhu · Chaganhu | 400 000 | 9 000 |

The Kaiser is the weakest match by a distance — the Teide is the only proper fleet-oiler
silhouette in the collection and it is 88 m short. If a better donor ever appears, it is a
one-line change in `CLONES`.

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

Every supplier — the nine patched hulls, the six clones and HMAS Supply — carries
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

None hard. The pack patches whatever it finds: the nine supplier hulls come from vanilla plus
Euromod Cold War Spanish, and the launcher fix covers 22 mods it detects at build time. The
six new hulls ride vanilla Sacramento/Kilauea and Spanish Teide meshes, so those must stay
enabled. RE-power (3605013271) is optional and complementary.

`data/mod-catalog.json` has no `mods[]` entry for RE-power because it is not in
`data/raw-workshop-list.txt` — if you subscribe to it, add it there and re-export so the
conflict tooling can see it.

## Install

Nothing special: this pack is consolidated into `SEST_Integration` like every other, and the
load order does not change.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1
```

## First-flight checks

These are the things that cannot be settled from the files, in the order worth testing.

1. **The system-name question is settled** — the pack emits `SystemName=TruckSupplySystem`,
   the name all 24 of RE-power's field-tested ship suppliers use. Baseline check: put a
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
   parsed, all 17 suppliers would have failed at once, not just the submarine half. The
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
