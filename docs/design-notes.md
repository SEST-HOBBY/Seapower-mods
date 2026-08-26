# Design notes — the rules this project learned, and the evidence for each

Every rule here was earned by something breaking, being measured, or being
verified in game. When a rule and a screenshot disagree, the screenshot wins
and the rule gets a new revision — that has happened three times already.

## How the game composes 132 mods

- **Unit files are whole-file overrides.** For `aircraft/`, `vessels/`,
  `submarines/`, `land_units/`, `ammunition/`, `biologic/`, `ui/`, the highest
  mod's copy loads and the rest are *gone* — silently. This is the single most
  important fact in the repo; the Growler pack was inert for days because one
  reorder jumped U.S. Navy 2027 over it, with no error anywhere.
- **`systems/` and `language_*/` merge key-by-key.** Proof: 89 mods ship a
  `systems/sensors.ini` from 8 to 8,141 lines and none deletes the others.
  Language merging is how packs rename other mods' units without owning the file.
- **Paths are case-insensitive** (NTFS). Two mods shipping `Shahed_136_white.ini`
  and `shahed_136_white.ini` are fighting over one file. Every checker case-folds.
- **Asset paths resolve across mods** — a pack can reference another mod's mesh
  folder (the Triton flies the MQ-9 mod's model). This is also a hidden
  dependency the unit-reference checker cannot see.
- **The same unit id defined by two mods can crash the UI** even though file
  overrides collapse cleanly — the plan converter dict-adds unit ids and threw
  on `plaaf_kj-500` (standalone KJ-500 mod vs PLAN Pack, which had absorbed it
  wholesale). Redundant subscriptions are a liability, not a convenience.

## The Tier 0 invariant

Every SEST pack sits above every workshop mod, as one unbroken block, so
reordering anything below is safe by construction. `tools/check_load_order.py`
computes the rules (each pack must outrank every mod sharing an override file)
and adds a structural backstop for stale exports. Negative-tested both ways.

## Loadout geometry — the F-15EX lessons

- **S1/S2 and S5/S6 are the two side rails of ONE inner wing pylon** (left:
  −0.0486 / −0.03743, tank centred between at −0.04308), not two pylons. Same
  again for S7/S9 outboard. Misreading this produced a fit with a missile on
  one face and a bare rail on the other.
- **The rail-allowance rule is at revision three.** Rev 1: any occupied wing
  station cleared the rails. Rev 2: tanks allow AIM-9X only (upstream's
  pattern). Rev 3 (current, in-game verified): a tank or MTW rack restricts
  nothing — rails ride at the pylon flanks above the tank's shoulder; only a
  wide `|WW` store hung ON the wing station itself (GBU-10, B-61, 174B, 424)
  clears them, and per-loadout `RAIL_EXEMPT` overrides even that where the
  user has verified coexistence (the trucks).
- **Each `[WeaponSystemN]` has its own station table.** The same station
  number means different coordinates per table. This mistake was made four
  separate times, including inside the clash-detection tool itself, which once
  reported twenty phantom `d=0.00000` stacks.
- **Position-key offsets are seat corrections per store family.** The AIM-424
  renders with the AGM-88G mesh whose origin rides lower than the AIM-174B's
  on the same key — so it gets its own key rather than moving the shared one.
  Same story for the B-52O's ARRW (`RGM110_Rack`'s −0.009 suits the fat
  AGM-110L, not ARRW) and the Rafale's 424 (the SCALP seat floated it; it
  mounts bare like the 260 now).
- **Meshes are load-bearing.** A tank's model can be exported inside a
  whole-aircraft OBJ whose origin is where the tank sits on *that* airframe —
  substituting it detaches tanks visually. Rack submodels
  (`SubModelsToHide`) must track the fit: the AAMT twin-rack stayed visible on
  fits whose stations had switched to tanks and rendered straight through them.

## Physical ceilings (say no honestly)

- F/A-18E/F: **three external tanks maximum** — one pair of wing tank pylons
  (`fule_tank_point`, stations 27/28) plus centreline. A five-tank request has
  nowhere to hang.
- EA-18G: **two** — the centreline is the EW station, and there is no station
  outboard of 27/28 (`NumberOfStations=28`). "Four tanks flanking the NGJ" is
  not mesh-possible.
- Stations 13/14 look like pylons but carry sead/aam rack meshes; a tank there
  floats in mid-air.

## Replenishment at sea — five gates, and only one of them is obvious

- **The supply system was shipped switched off, and the commented block names
  the WRONG system.** Vanilla's only `[SupplySystem1]` on a hull is commented
  out on `usn_aoe_sacramento.ini` and says `VesselSupplySystem` — a name that
  appears in no working file anywhere and has no localisation. RE-power
  (3605013271), field-tested on 23 ship suppliers, uses
  `SystemName=TruckSupplySystem` with `TargetTypes=Vessel` or `=Submarine` on
  every one, and its bundled reference doc gives the TargetTypes vocabulary as
  "LandUnit", "Vessel" or "Submarine". Derive from what runs, not from what a
  comment promises.
- **No surfaced-state gate exists in the data, and none exists in the engine
  either.** No supply key mentions depth, RE-power's submarine suppliers carry
  none, and ui.ini has only the generic "Replenishment unavailable." string.
  That left it an in-game question, and the 2026 test answered it the unwelcome
  way: a SUBMERGED submarine replenishes. `EnabledSurfaced` (90 occurrences)
  looked like the lever and is not — it appears only in `[Sail_Submerged]` /
  `[Sail_Surfaced]` mesh sections, swapping the conning-tower model. So there
  is no data-side fix: the choice is `TargetTypes=...,Submarine` or no
  submarine resupply at all. This pack keeps it and makes surfacing a house
  rule.
- **A round has to clear five gates.** `TargetTypes` vs the receiver's
  `UnitType`; then `SupplyRange`/`MaxOwnVelocity`/`MaxTargetVelocity`/
  `MaxTargets`; then the round's `AmmoPoints` against the supplier's
  `MaxAmmoPoints`; then `SupplyCategory` against the supplier's
  `AccountableAmmunitionCategory_N`; then the receiving launcher.
- **Omitting `MaxAmmoPoints` removes the size cap entirely.** That is not an
  oversight — `tgt_ammo_depot_small` comments it out deliberately, which is the
  only reason the depot can reload an SA-5 (21000 points) that a truck capped
  at 200 cannot. It is the cleanest lever for "ammunition ship vs fleet oiler".
- **A launcher with no magazine can never be reloaded.** `Ammunition=` with no
  `AssociatedMagazine=` needs `ReloadableWithoutMagazine=True` or it is
  one-shot forever. Vanilla states it on the Long Beach's Mk141 canisters,
  which set it `False`; across the whole corpus the flag appears on 11 units
  and every one is a land SAM TEL. **No vessel anywhere sets it.** This is the
  gate that decides whether the other four matter, and it is why RE-power's
  author reports that anti-ship missiles and torpedoes will not replenish.
- **Red Storm Arsenal models every Mk41 cell as its own bare launcher.** So the
  flag is not a deck-canister detail: without it, not one VLS round on any of
  RSA's 103 affected hulls could ever be replenished. Scale surprises are the norm
  — 2083 launchers on 276 hulls are affected, which is 96% of every launcher in
  the modern collection that actually holds a missile (2176; the other 93 have
  a magazine and were always fine). The fix reaches 2078 of them on 274 hulls -
  every one it is entitled to touch; the other 5 sit on hulls owned by sibling
  SEST packs. Not the handful the Long Beach example suggests.
- **"It only changes the block we replace anyway" is a measurement, not an
  assumption.** This pack forked RE-power's copy of the nine shared auxiliary
  hulls on the ordinary rule — fork the load-order winner, the copy the player
  actually sees — resting on the belief that RE-power's only edit to them was
  the supply block. Diffed, it was 142 lines outside that block: the whole
  `[OpticalView]` section deleted, `ArmorType` dropped `Minor` → `None`,
  `MaxAccelerationFactor` 0.21 → 2.4, `LinearDrag` and the acoustic figures
  retuned, `CavitationSpeed` and `Prairie` removed. At tier 0 that republishes
  every one of them under SEST's name. Forking the winner is right when the
  file is one you are *extending*; when you only need one block, fork VANILLA
  and inherit nothing. `tools/check_pack_fidelity.py` proves the result but
  cannot make this choice for you — it only checks the file equals whatever
  upstream you named.
- **A cloned hull inherits its donor's whole combat system, not just its
  shape.** The replenishment clones were donor plus a supply block and nothing
  else, so a 2017 Chinese and a 2017 British replenishment ship each sailed
  with a Mk29 NATO Sea Sparrow launcher, two Phalanx, an SPS-40 and an
  AN/SLQ-32 — a US Navy 1970s fit, on the wrong navy — and a 2006 MSC ship
  carried twin 3″/50 mounts. Picking a donor on hull length answers "what does
  it look like"; it says nothing about what it *is*. The fix is a refit table
  that rewrites `SystemName` inside system sections and `Ammunition1` inside
  magazine sections and touches nothing else, because `Mount`, `Collider`,
  `Gun` and `Container` all name geometry that exists only in the donor mesh.
- **A mesh section's `SystemName` is decorative — measure before assuming a
  link.** Vanilla's `[SPS_40]` mesh block carries `SystemName=SPS-40` beside
  its `Mesh=` line, which looks like the pairing a refit must keep consistent.
  It is not: across every vanilla vessel, of the mesh sections a sensor
  actually mounts, **757 carry no `SystemName` at all**, 129 carry a matching
  one, and 11 carry one that disagrees — the Ticonderoga's SPS-55 mounts a mesh
  labelled `usn_cg_ticonderoga_sps_55`, a mesh name, and the Ivan Rogov's three
  Palm Fronds mount meshes labelled `Nav_Radar`. The link the engine uses is
  `Mount=`, pointing at the section by name.
- **A `_variants` file in a hull list is a load-order trap waiting to spring.**
  `modern_hulls()` globbed every `*.ini` in a mod's `vessels/`, variants
  included. A variants file holds hull numbers, flags and service dates - no
  `[WeaponSystem]` can appear in one - so it never needed to be there. What it
  did instead was put a load-order LOSER in the list: Nimitz Expanded ships
  exactly three files, of which the only vessel entry is
  `usn_cvn_nimitz_variants.ini`, and Flight Deck Ops ships that same file and
  outranks it 17 to 38. Nothing shipped wrong, because the transform finds
  nothing to change in a variants file - the pack was one behaviour change away
  from forking the loser, the defect that cost `plan_cv_fujian`. Filter the
  list to what the transform can actually act on, and the trap cannot arm.
- **A "dangling reference" is three different problems, and two of them are
  not references.** Thirteen modern hulls were being skipped for hanging an
  ammunition id nothing defines, at a cost of 77 launchers. Two were not broken
  at all: `DateBased_HWT=0,ger_dm2a4|2035,ger_dm2a5` declares a date-selected
  round and `Ammunition1=DateBased_HWT` reads it — a stock mechanic, nineteen
  declarations across the collection — and the Han's `Ammunition4=` sits past
  its own `NumberOfAmmunitionTypes=3`, so the engine never reads it. Six were a
  typo away from a round the same mod already ships (`usn_rim_162essm` for
  `usn_rim_162a`, `wp_ss-n-27` for `wp_ss_n_27`). Only the last four were
  genuinely missing content. Detect precisely before deciding policy: a
  detector that cannot tell a mechanic from a mistake makes the skip list, and
  the loss, look justified.
- **Fix the reference, never invent the id.** Defining the missing
  `usn_rgm-84.ini` would work and would put SEST tier 0 in front of the real
  file if the mod ever ships it. Repairing the reference inside the copy the
  pack was already forking claims no name at all.
- **Whose broken reference is it?** The same rule settles systems and stores:
  if an upstream unit file also names the unresolvable id, the pack inherited
  it with the file it forked and can only report it; if nothing upstream names
  it, this repo introduced it and the build fails. Without that distinction a
  pack cannot ship a forked hull that carries an upstream bug — which is how
  ten hulls lost the launcher fix over references that were equally broken with
  or without SEST.
- **A missile launcher's `SystemName` carries GEOMETRY; a gun's and a sensor's
  do not.** `[MK29]` declares eight `AttachmentPosition` entries and
  `[HQ-10_24]` twenty-four — mesh-relative coordinates for where each round is
  drawn on the mount. Swapping one launcher name for another therefore renders
  the rounds at a different launcher's coordinates on a mount that has the old
  number of rails. Refit a launcher through its MAGAZINE instead: the Type 901
  fires HQ-10 from a Mk29. `[MK15]` and `[Type_730]` are rates, arcs and
  effects with no geometry at all, so guns swap freely.
- **Half a swap is worse than none.** Give a hull a Type 730 and leave its
  magazine on `usn_cal_20mm` and it has a CIWS with nothing to fire. Anything
  that changes a weapon has to change its round in the same table row, which is
  why the refit keys the two together rather than listing them apart.
- **Ships carry loadouts too, and their launchers hide in the suffix.** A
  header regex matching only `[WeaponSystemN]` silently skips
  `[WeaponSystem6AntiShip]`, `[WeaponSystem4Strike]`, `[WeaponSystem12Late]`
  and friends — 245 bare launchers on 24 modern hulls, including the
  Meteoro/Arafura's NSM quad launcher and the FREMM and Type 052D anti-ship
  fits. Same trap as the aircraft `[WeaponSystem1Tanker]` blocks. Anything
  sweeping weapon systems must allow the suffix.
- **`SupplyRange` is nautical miles.** The ini comment says "In miles";
  `language_en/ui.ini:2685` renders it `${SupplyRangeInMiles} nmi.` The UI
  string wins, same as a screenshot wins.
- **Fork the load-order winner, never the first file you find.** Six vessel
  files are shipped by two modern mods at once; taking whichever the iteration
  reaches last forked the LOSING copy of `plan_cv_fujian`, which at tier 0
  would have replaced the hull the player actually sees with a different mod's
  version. The same trap the ammunition side already resolves by rank.
- **`errors="replace"` corrupts a whole-file override.** Three upstream files
  are not valid UTF-8 — a stray `0xFF` in Euromod's `usn_rgm-109e5a.ini`
  beside two real NUL bytes, and `0xA0` in both `ger_ffg_f124` sensor labels.
  Reading with `replace` rewrites each as U+FFFD, a silent edit to somebody
  else's file. `errors="surrogateescape"` round-trips them. Pass `newline`
  explicitly too, or a Windows rebuild emits CRLF and diffs the whole pack.
- **Put back the key, not the file.** Restoring two stripped keys by shipping
  the vanilla copy would have reverted 118 lines of `wp_ss-n-19` — Power,
  impact size, the sea-skimming profile — undoing the mod's whole point. Fork
  the winner and insert the two lines.
- **A hand-written id list is a coverage bug waiting to happen.** The metering
  table started as 38 explicit ids. It caught the dash-named vanilla and
  Euromod rounds and missed Red Storm Arsenal's entire underscore-named
  parallel family — `usn_rgm_109c3` alone sits in 90 launchers. Derived from
  `AmmoPoints`/`Type`/`TargetType` on every build it comes to 80. Same
  principle as `check_load_order.py` computing its rules instead of listing
  them: nothing to keep in sync, nothing to forget when a mod is added.
- **Check the LAND units before tagging a round.** The three land suppliers
  stock no accountable categories at all, so tagging a round they service
  removes the only supply path the game ships working. Red Storm Arsenal's
  `usa_tomahawk_launcher` fires `usn_rgm-109b`; eight rounds are excluded from
  metering for exactly this reason.
- **A submerged submarine replenishes. Tested in game, 2026.** The engine
  applies no surfaced-state check, and none can be added: no supply key
  mentions depth, and the one candidate that looked like a lever —
  `EnabledSurfaced`, 90 occurrences — is cosmetic, appearing only in
  `[Sail_Submerged]`/`[Sail_Surfaced]` mesh sections (45 pairs) to swap the
  conning-tower model. Kept enabled as a house rule rather than lost along
  with surfaced rearm; the off switch is dropping `Submarine` from
  `SUPPLIERS`, since the only other submarine-capable supplier in the
  collection is a dock. **The screenshot won again**: the pack shipped saying
  this was unverifiable from files, and the answer was one mission away.
- **`TargetTypes` takes a comma list.** `Vessel,Submarine` parses, proven in
  game. Nothing in vanilla or the 131 exported mods uses a multi-value supply
  target list — RE-power picks one per hull — so this was the pack's riskiest
  single line: had the comma not parsed, all 19 suppliers would have failed
  at once, not just the submarine half.
- **Adding a `SupplyCategory` can only ever restrict.** A round that had none
  was unrestricted commodity ordnance; tagging it makes it unreplenishable by
  every supplier that does not stock the category — flight decks included. So
  tag only rounds no aircraft carries, and re-check that on every build: a
  future mod hanging one on a pylon turns a balance choice into a regression.
- **A stocked category the size gate blocks is a dead line.** Kazbek gets no
  `SovietAdvancedASM` because the cheapest round in it costs 7740 against a
  2000 ceiling. Keep the two gates consistent per hull or the supply panel
  advertises ordnance that can never move.

## Working practices

- **Derive, don't invent.** New loadouts clone a donor block the mod's author
  already proved (same stations, hide lists, keys) and swap rounds. Choices
  between candidate rounds are settled by comparison tables (AIM-424 vs 174B,
  the three NSMs, RSA's AIM-120D), not preference.
- **New WEAPONS rebase on the closest proven weapon, minimum deltas.** The
  AGR-30 built from the Apache M282 froze the game through three guidance
  recipes; a key-by-key diff against working pod rockets showed dozens of
  template differences, unbisectable by iteration. Rebasing on dts_apkws-ii
  (a proven in-pod, lofting rocket) with five changed lines fixed it on the
  first try. Survey precedent before combining features: no container in the
  collection holds a GuidanceType=3 round, and the engine apparently agrees.
- **Everything is generated.** Packs rebuild from `build_*.py` with loud
  guards (`exit` on count mismatches, donors changing, keys already present).
  Mission edits that must survive editor round-trips are idempotent passes in
  the refresh chain, not one-off file edits — the sanctioned fleet and the
  NFIII reinforcements re-apply themselves after every import.
- **Upstream moves under you.** A shadowed file can receive author updates the
  override hides — USNA's buddy-tanker fit landed in a file the Growler pack
  owns and was ported the same day. After any export, diff what changed and
  check it against pack donors.
- **Gates before every push:** `check_load_order`, `check_dependencies`,
  `preflight` (every reference the missions make), `check_station_clash`,
  full pack rebuilds. All exit non-zero; all have been negative-tested.
