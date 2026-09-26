# Design notes — the rules this project learned, and the evidence for each

Every rule here was earned by something breaking, being measured, or being
verified in game. When a rule and a screenshot disagree, the screenshot wins
and the rule gets a new revision — that has happened three times already.

## How the game composes 144 mods

- **Unit files are whole-file overrides.** For `aircraft/`, `vessels/`,
  `submarines/`, `land_units/`, `ammunition/`, `biologic/`, `ui/`, the highest
  mod's copy loads and the rest are *gone* — silently. This is the single most
  important fact in the repo; the Growler pack was inert for days because one
  reorder jumped U.S. Navy 2027 over it, with no error anywhere.
- **That rule catches the global tables too, and nobody notices.**
  `ammunition/damage.ini` is not a unit — it is the game's global damage and
  intercept model — but it lives under `ammunition/`, so it obeys the same
  whole-file rule. The Tu-95/AS-15 mod ships a copy built on a pre-0.8.x
  version of that file. It won, and it deleted eight global keys from the whole
  collection: the five `InterceptSizeBonus*`, `InterceptOutOfAltitudePenalty`,
  `InterceptSpeedPenaltyMultiplier`, and `InterceptChanceOutOfAltitudeOverride`
  — the hard 5% ceiling on intercepting a target outside a weapon's altitude
  band. Six of the eight have no per-round override form anywhere in the
  corpus — the five size bonuses and the clamp — so none of the 557
  anti-air-capable rounds could opt out of losing them. The other two,
  `InterceptOutOfAltitudePenalty` and `InterceptSpeedPenaltyMultiplier`, are
  declared per round by 156 and 168 of those rounds; the other 401 and 389
  read the global, which was gone. Counts from `tools/survey_attack_altitudes.py`;
  re-run it after any export or reorder rather than trusting these. That mod
  wanted to change two impact-size values. `SEST_Intercept_Model` restores the
  table; `integration/intercept-model/build_patch.py` records what arming the
  clamp changes and which rounds needed fixing first (the Red Storm SM-6, the
  Korean K-SAM II copied from it, and David's Sling).
  Measured, not observed in game: it was found by diffing the winning copy
  against vanilla, not by anything looking wrong on screen, and the paired
  builds that would show whether the restore changes anything have not been
  run. Check global tables the same way you check units.
- **An absent band is not the same as a zero — an absent *bound* is still
  open.** Three stock AAW missiles (`fr_super-530f`, `pla_pl-2`, `pla_pl-2b`)
  declare no attack-altitude band at all and have always shipped against a
  `damage.ini` where the 5% clamp is live, so a missing band cannot default to
  zero or they would be permanently clamped. That settles the both-absent case
  only. It does not settle the 69 modded rounds that declare *one* side and no
  vanilla file does: an engine may skip the check when neither bound is present
  yet still run it against a defaulted other side. Untested; fire an AMRAAM
  (floor only) and a Roland or Crotale VT-1 (ceiling only) and read the
  percentage.
- **`systems/` and `language_*/` merge key-by-key.** Proof: 89 mods ship a
  `systems/sensors.ini` from 8 to 8,141 lines and none deletes the others.
  Language merging is how packs rename other mods' units without owning the file.
- **Paths are case-insensitive** (NTFS). Two mods shipping `Shahed_136_white.ini`
  and `shahed_136_white.ini` are fighting over one file. Every checker case-folds.
- **Asset paths resolve across mods** — a pack can reference another mod's mesh
  folder (the Triton flies the MQ-9 mod's model). This is also a hidden
  dependency the unit-reference checker cannot see.
- **Two mods defining the same unit id is NOT known to crash anything.** This
  entry used to claim it did, on the `plaaf_kj-500` evidence. That was wrong, and
  the correction cost a mod its subscription: the crash survived unsubscribing the
  second KJ-500 provider and was eventually traced to a mission aircraft with no
  resolvable default loadout (see Working practices). Same-filename overrides
  collapse cleanly — 263 of them do so in this collection every session. Redundant
  subscriptions are still worth pruning for clarity, but not out of fear of this.
- **Terrain is a 1 km grid and not ours to change.** The devs build the world
  from 30 arc-second elevation data (Dev Diary #4), hand-patch chokepoints in
  Photoshop and with an in-engine terrain painter whose stamp textures
  `terrain/terrain.ini` lists but StreamingAssets does not ship. No Workshop
  or GitHub mod touches the heightmap, and the 2021 "(and you!)" promise of
  player terrain editing never became a documented feature. Anything under
  about 1 to 2 km, and everything reclaimed after the data vintage - Fiery
  Cross, Subi, Mischief - is absent by construction; Singapore and the
  Japanese home islands fuse to their mainlands for the same reason.
- **A land unit on water does not sink, it floats at one metre.**
  `terrain.ini` clamps placed land units to `MinHeightForLandUnits=1.0`, and
  `campaigns/britishisles_ports.ini` says outright that a Port "doesn't snap
  to terrain and does not flatten terrain around it" (`SnapToTerrain=False`).
  Vanilla oil rigs, the armed-rig mod, the floating drydock and the FARP mod
  all work at sea on that basis, helo operations included. So the reef bases
  in SEST Indo-Pacific Land Assets render as runways and buildings sitting on
  the sea surface with no ground under them, not as nothing. The only route
  to a visible artificial island is a Port-type unit assembled from the
  modular port meshes with a scaled concrete slab, built like the RAAF bases
  from existing geometry; that is untested in game.

## Three different mod counts, and only one of them is ours

- **Folders on disk is the only count that decides anything.** `mods-source/`, the
  load order and every checker are built from the directories under
  `steamapps\workshop\content\1286220`. A mod with no folder cannot load, so it
  cannot matter, whatever any other number says.
- **Steam keeps its own local list** in `steamapps\workshop\appworkshop_1286220.acf`.
  It normally agrees with the folders. When it does not, the gap is diagnostic: an id
  it tracks with no folder is a download that never landed, and a folder it does not
  track is left over from an unsubscribe. `capture-context.ps1` reports both
  directions, with `NeedsDownload` and `NeedsUpdate`.
- **The Steam UI's subscribed count is server-side and can legitimately be higher
  than both.** Subscribed Collections have no content to download, and an item the
  author delists stays in your subscription count forever. Neither can load, so
  neither belongs in the load order.

Earned twice in one session (20 Sep 2026): the repo reported 138, the Mod Manager
agreed at 138, and Steam said 140. Nothing was wrong. Before chasing a count, say
which of the three you are quoting.

## What an editor round-trip keeps, and the one thing it silently rewrites

Saving a mission in Sea Power's own editor rewrites every section from the editor's
in-memory model. The save is not a diff, so the question is never "did it change the
file" - it is "which of our intent survived the model". Measured on `SEST Banda Front
Lean v2` (`b1c6ee1e` -> `a30a8b04` on the kind-faraday line, three units added, ~90
nudged): 606 insertions against 734 deletions, a net loss of 128 lines while gaining
three units.

Almost all of that is the editor writing only non-default values, and is not loss:

- `MissionType=NoMission` dropped on 74 units - `NoMission` is the default.
- `RadarsActive=False` dropped on 45. Every dropped one was `False` and every
  surviving one is `True`, on whales, airliners, fishing boats and narco subs.
  Absent means off.
- `ActiveSonarsEnabled=False` and `TowedArrayDeployed=False` dropped on 5 each,
  all on the same submarines, all `False`. Same rule.
- `Waypoints` dropped on 19 - **all 19 are formation followers, and all five of
  their leaders kept the route.** A follower's waypoints were only ever a copy of
  its leader's, which is why the dropped strings appeared three at a time.
- `CustomAirGroup=True` dropped on 12, every one of which carried zero aircraft
  entries before and after.
- `123.000` -> `123`, `90.00` -> `90`, `277.02` -> `-85`. Formatting.

One thing is real loss, and it is the one that changes the scenario:

- **`WeaponStatus` does not round-trip.** All 57 `Hold` and all 10 `Tight` came back
  as `Free`, and six units lost the key outright. That is the sanctioned convoys -
  built by `add_sanctioned_shipping.py` to run "dark, dumb, non-reactive" on `Hold`
  behind escorts on `Tight` "so they unmask only when the fleet is engaged" - and
  the whole Allied carrier group, which sat on `Tight` to shadow rather than shoot.
  The Q-ship `wp_ms_mercur_decoy`, whose entire job is holding fire, went weapons
  free. Nothing warned: the unit count was right and preflight resolved every
  reference, because every reference was still valid. Only the intent was gone.

`integration/missions/restore_roe.py` restores it, and `import-mission.ps1` runs it
on every mission it imports, so the fix lands before the commit rather than after.

**"The previous commit" is not a safe reference, and getting that wrong hides exactly
the bug the tool is for.** The first version defaulted to the commit before the most
recent one. Run immediately after the fix was committed, that default pointed at the
flattened save itself - which carries no `Hold` and no `Tight`, so it could restore
none - and printed a reassuring `to restore 0` for a file it had not really checked.
The default is now the newest commit whose copy *still carries restraint*; commits
with none are skipped and named in the output, an explicit `--ref` with none is
refused, and the summary line states how many restrained units the reference holds so
a zero is never mistaken for a pass. A check that cannot fail is not a check.

**A mission that never restrained anyone is information, not a failure.** Four of
the 54 missions at the top of `integration/missions/` (backup copies aside) carry
`Hold` or `Tight`, and the import hook runs the pass on every mission it brings in.
As first written, a history with no restraint in it exited 1, so nearly every import
would have printed "could not settle". It now says that nothing was compared and
why - the mission never set a restrained posture, or every committed copy was
flattened - and exits 0. Only the second case needs a person, and the message names
it.

**Compare by unit identity, not by section name.** Inserting one vessel renumbers
every section after it: `[Taskforce1Vessel5]` was a Flight IIA Burke before this save
and a civilian motor ship after, and a name-keyed diff reports the whole tail as
changed while hiding what actually moved. Align each index family by its `Type`
sequence and skip inserted or deleted runs rather than guessing across them - that is
what `restore_roe.py` does, and it is why it finds 67 units to fix instead of 62.

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
  which set it `False`; across the whole corpus the flag is set `True` on 11
  units and every one is a land SAM TEL. **No vessel anywhere sets it.** This
  is the gate that decides whether the other four matter, and it is why
  RE-power's author reports that anti-ship missiles and torpedoes will not
  replenish.
- **Red Storm Arsenal models every Mk41 cell as its own bare launcher.** So the
  flag is not a deck-canister detail: without it, not one VLS round on any of
  RSA's 103 affected hulls could ever be replenished. Scale surprises are the
  norm — on the 24 Sep 2026 export 2220 launchers on 309 modern hulls are
  affected, 93% of every launcher in the modern collection that actually holds
  a round (2393; the other 173 have a magazine and were always fine). SEST
  Replenishment At Sea reaches 2215 of them on 307 hulls, every one it is
  entitled to touch; the other 5 sit on the Mogami and HMS Ocean, whose own
  packs apply the same transform. Not the handful the Long Beach example
  suggests.
- **"It only changes the block we replace anyway" is a measurement, not an
  assumption.** The pack first forked RE-power's copy of the nine shared
  auxiliary hulls on the ordinary rule — fork the load-order winner, the copy
  the player actually sees — resting on the belief that RE-power's only edit
  to them was the supply block. Diffed, it was not: 26 changed lines on the
  Sacramento alone outside that block, the whole `[OpticalView]` section
  deleted, `ArmorType` dropped `Minor` → `None`, `MaxAccelerationFactor`
  0.21 → 2.4, `LinearDrag` and the acoustic figures retuned, `CavitationSpeed`
  and `Prairie` removed. At tier 0 that republishes every one of them under
  SEST's name. Forking the winner is right when the file is one you are
  *extending*; when you only need one block, fork VANILLA and inherit nothing.
  `tools/check_pack_fidelity.py` proves the result but cannot make this choice
  for you — it only checks the file equals whatever upstream you named.
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
  and friends — 241 bare launchers on 24 modern hulls today, including the
  Meteoro/Arafura's NSM quad launcher and the FREMM and Type 052D anti-ship
  fits. Same trap as the aircraft `[WeaponSystem1Tanker]` blocks. Anything
  sweeping weapon systems must allow the suffix.
- **A section header can carry a comment.** Vanilla writes
  `[Recon_Camera] #Generic recon camera` and Red Storm Arsenal
  `[Type_345] #HHQ-7 FCR`. A parser whose header has to end at `]` skips every
  such section: `check_weapon_employment` read the HQ-7's two-channel command
  radar as no radar at all and blamed the pack's HQ-7 store repair for a
  missing guidance channel. Match `^\[name\][^\n]*`, never `^\[name\]\n`.
- **A "dangling reference" is three different problems, and two of them are
  not references.** Thirteen modern hulls were once skipped for hanging an
  ammunition id nothing defines, at a cost of 77 launchers. Two were not broken
  at all: `DateBased_HWT=0,ger_dm2a4|2035,ger_dm2a5` declares a date-selected
  round and `Ammunition1=DateBased_HWT` reads it — a stock mechanic, vanilla
  submarines included — and the Han's `Ammunition4=` sits past its own
  `NumberOfAmmunitionTypes=3`, so the engine never reads it. Six were a typo
  away from a round the same mod already ships (`usn_rim_162essm` for
  `usn_rim_162a`, `wp_ss-n-27` for `wp_ss_n_27`). Only the last four were
  genuinely missing content. Detect precisely before deciding policy: a
  detector that cannot tell a mechanic from a mistake makes the skip list, and
  the loss, look justified.
- **Fix the reference, never invent the id.** Defining the missing
  `usn_rgm-84.ini` would work and would put SEST tier 0 in front of the real
  file if the mod ever ships it. Repairing the reference inside the copy the
  pack was already forking claims no name at all.
- **Whose defect is it?** The same rule settles systems, stores and weapon
  employment: if an upstream copy of the unit file has the same problem, the
  pack inherited it with the file it forked and can only report it; if nothing
  upstream has it, this repo introduced it and the build fails.
  `check_dependencies` and `check_weapon_employment` both apply it. Without
  that distinction a pack cannot ship a forked hull that carries an upstream
  bug — which is how ten hulls once lost the launcher fix over references that
  were equally broken with or without SEST.
- **`SupplyRange` is nautical miles.** The ini comment says "In miles";
  `language_en/ui.ini:2685` renders it `${SupplyRangeInMiles} nmi.` The UI
  string wins, same as a screenshot wins.
- **Fork the load-order winner, never the first file you find.** Three
  modern hulls (six files with their variants) are shipped by two modern mods
  at once; taking whichever the iteration reaches last forked the LOSING copy
  of `plan_cv_fujian`, which at tier 0 would have replaced the hull the player
  actually sees with a different mod's version. The same trap the ammunition
  side already resolves by rank. A `_variants` file in the hull list is the
  same trap waiting to spring: Nimitz Expanded ships only
  `usn_cvn_nimitz_variants.ini`, and Flight Deck Ops ships that file too and
  outranks it.
- **`errors="replace"` corrupts a whole-file override.** Three upstream files
  are not valid UTF-8 — a stray `0xFF` in Euromod's `usn_rgm-109e5a.ini`
  beside two real NUL bytes, and `0xA0` in both `ger_ffg_f124` sensor labels.
  Reading with `replace` rewrites each as U+FFFD, a silent edit to somebody
  else's file. `errors="surrogateescape"` round-trips them. Pass `newline`
  explicitly too, or a Windows rebuild emits CRLF and diffs the whole pack.
- **Put back the key, not the file.** Restoring two stripped keys by shipping
  the vanilla copy would have reverted the Tu-95 mod's whole rework of
  `wp_ss-n-19` — Power, impact size, the sea-skimming profile — undoing the
  mod's point. Fork the winner and insert the two lines.
- **A hand-written id list is a coverage bug waiting to happen.** The metering
  table started as 38 explicit ids. It caught the dash-named vanilla and
  Euromod rounds and missed Red Storm Arsenal's entire underscore-named
  parallel family — `usn_rgm_109c3` alone sits in 90 launchers. Derived from
  `AmmoPoints`/`Type`/`TargetType` on every build it comes to 87 on the
  24 Sep 2026 export. Same principle as `check_load_order.py` computing its
  rules instead of listing them: nothing to keep in sync, nothing to forget
  when a mod is added.
- **A derived rule still has to reach files it does not own.** Ten of those
  87 rounds are files SEST Collection Fixes or SEST Intercept Model already
  ship, and two packs cannot ship one path. The owner tags its own copy with
  the shared `tag_ammunition()`, and the RAS builder checks both directions —
  every sibling-owned metered round carries exactly the category the rule
  derives, and every `SEST_` category a sibling declares is one the rule still
  selects — so a table and a rule cannot quietly drift apart.
- **Check the LAND units before tagging a round.** The three land suppliers
  stock no accountable categories at all, so tagging a round they service
  removes the only supply path the game ships working. Red Storm Arsenal's
  `usa_tomahawk_launcher` fires `usn_rgm-109b`; eight rounds are excluded from
  metering for exactly this reason.
- **A submerged submarine replenishes. Tested in game, 2026.** The engine
  applies no surfaced-state check, and none can be added: no supply key
  mentions depth, and the one candidate that looked like a lever —
  `EnabledSurfaced` — is cosmetic, appearing only in mesh sections
  (`[Sail_Submerged]`/`[Sail_Surfaced]`, flags, crew figures, hatches) to show
  or hide a model part. Kept enabled as a house rule rather than lost along
  with surfaced rearm; the off switch is dropping `Submarine` from
  `SUPPLIERS`, since the only other submarine-capable supplier in the
  collection is a dock. **The screenshot won again**: the pack shipped saying
  this was unverifiable from files, and the answer was one mission away.
- **`TargetTypes` takes a comma list.** `Vessel,Submarine` parses, proven in
  game. Nothing in vanilla or the exported mods uses a multi-value supply
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
- **Some three hundred forks freeze some three hundred hulls.** Every hull the
  launcher fix touches is a whole-file override of somebody else's file, so an
  upstream update to it is masked until the pack is rebuilt. Rebuild after
  every export (`docs/packaging-and-recovery.md`).

## Working practices

- **Derive, don't invent.** New loadouts clone a donor block the mod's author
  already proved (same stations, hide lists, keys) and swap rounds. Choices
  between candidate rounds are settled by comparison tables (AIM-424 vs 174B,
  the three NSMs, RSA's AIM-120D), not preference.

- **When two rounds are close, precedent and coherence beat the spec sheet.**
  The RAN NSM was first picked on a headline: RSA's `usn_rgm_184a` had
  datalink midcourse where Euromod's `knm_nsm_1a` had radio command, and the
  two are otherwise the same missile (1450 kg, 620 kt, 165.6 nm, 20 nm
  seeker). That one stat cost days. The datalink needed a guidance channel the
  donor mounts never had; the file's terminal approach sat 25 nm outside its
  own 20 nm seeker; its author's header said *"REQUIRES STATS REVISION"* and
  that it has no RC flight stage; and nothing else in the collection fired it.
  The Euromod round is internally coherent and is fired by ten hulls, four of
  them fielded in NFIII. So when two candidates are within noise of each
  other, rank them by: does anything we field already fire it, is its own stat
  block self-consistent, and does the real operator actually buy it — before
  comparing the numbers that look impressive.
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
- **The export must mirror deletions, or the repo lies.** `export-mod-configs.ps1`
  copied files in and pruned unsubscribed mods, but never deleted a file an author
  removed *inside* a mod, so every checker kept resolving against ghosts and passed.
  On 19 Sep 2026 the repo showed Modern US Navy's `usn_ddg_burke_f3.ini` and U.S.
  Navy 2027's `usn_rim-162e.ini` as present while the game logged both as not found.
  The tell is git: a ghost's last commit predates the export that touched its
  neighbours, and a mod folder holds more files than `_export-manifest.csv` says were
  copied (Euromod JMSDF: 43 against 37). The exporter mirrors within each mod now,
  with two guards learned the hard way: `$DestDir` is normalised with `GetFullPath`
  (a literal `..\` made every path miss the keep-set, and the first run deleted 7,876
  of 7,888 exported files), and it refuses to remove more than half of a mod's files
  when that is over 20, because an update retires a handful, never most. Review the
  first mirrored export's deletions in git before committing it, and expect checks
  that only passed on ghosts to go red.
- **A mod renaming its units is the routine failure, not the exception.** Euromod
  JMSDF renamed `jp_sh-60j`/`jp_sh-60k` to `jmsdf_sh-60j`/`jmsdf_sh-60k` on 19 Sep
  2026. Here nothing failed: the ghost `jp_` files kept the Mogami builder, the
  Southern Watch 10 roster and eight loose missions resolving, while the mod's own
  language file named only the `jmsdf_` ids. The retarget is recorded in
  `retarget_units.py`. Porting the builder alone would have been worse than
  nothing: the campaign builder homes a helicopter on the nearest deck that lists
  it, so SW10's two Seahawks would have quietly moved from JS Mogami to the Langgur
  forward strip ashore.
- **A renamed base breaks every patch aliased onto it.** U.S. Navy 2027's Arleigh
  Burkes and its Nimitz, 28 hulls, are `#!alias` patches over Modern US Navy hulls.
  Modern US Navy renamed its Flight III from `usn_ddg_burke_f3` to
  `usn_ddg_burke_f3_125` (v567, 18 Sep 2026) before 2027 caught up, and the game
  died at startup with *KeyNotFoundException 'AirGroup'*: the patch's own
  `[FlightDeck]` asked for the air group the missing base would have supplied, and
  Player.log named the symptom, not the file.
  `tools/check_alias_bases.py` walks every chain through the load order the way the
  game does. Run it after every mirrored export; before the mirror, a deleted base
  kept resolving against its ghost. On the 24 Sep 2026 export all 28 bases resolve
  (2027 now aliases `usn_ddg_burke_f3_125`), so the missions keep the 2027 hulls and
  their `≥119_*` / `≥125_*` loadouts instead of being moved onto plain Modern US
  Navy hulls, which would drop those fits.
- **Anchor Chain has two layering directives, not one.** `#!alias` replaces a whole
  unit; `#!extend` merges a few keys onto the file of the SAME name one rung lower in
  the load order. Ammunition packs lean on it (18 of the PLA AEP pack's 21
  ammunition files on the 24 Sep 2026 export), and an extend breaks exactly the way
  the alias that crashed the game did. Resolving an extend needs the load-order
  *stack*, not the winner: `winning_file` on a same-name target returns the patch
  itself and loops. `refine_civ_traffic.file_stack` returns every copy in order, and
  the checker takes the entry below the patch. Severity follows the file kind: a
  unit file with no base is the startup crash, because the loader cannot build the
  unit, so it fails the check; a round with no base only means that weapon never
  fires, which the game survives, so it is reported and the check still exits zero.
  Anything that reads a round's keys has to walk the same chain. The land-defence
  builder classified a launcher by its round's `TargetType`, `MaxLaunchRange` and
  `MinAttackAltitude` read from the winner alone; once the AEP pack loaded above
  the PLA Land Unit Pack, `pla_hq-19.ini` resolved to an extend stub carrying none
  of the three, the HQ-19 read back as a gun layer, and the Spratly bases gained a
  second BMD section in place of the guns they lacked. `layered_text` in
  `build_land_defence.py` now follows the `#!extend` / `#!alias` chain and takes
  each key from the highest copy that sets it.
- **An aircraft needs a loadout it can actually resolve.** A mission entry with no
  `LoadoutVariant` makes the UI resolve a default at display time; if the winning
  unit file's `AvailableLoadouts` does not list `Default`, there is nothing to
  resolve to and the map panel's converter throws *"An item with the same key has
  already been added. Key: &lt;aircraft id&gt;"* from inside
  `MapPanel.MeasureOverride`. Confirmed on `plaaf_kj-500`, which declares
  `AvailableLoadouts=AEW` yet still carries a `[WeaponSystem1Default]` block, and
  confirmed fixed in game once the variant was made explicit. The editor omits the
  key whenever a loadout was never picked by hand, so
  `integration/missions/fix_loadout_variants.py` re-applies it as step 6b of the
  refresh chain and `preflight` fails on it (negative-tested).

  The lesson beyond the bug: the message named a *unit id*, which sent the hunt
  after duplicate mods for days - one mod was even unsubscribed over it. The id in
  a duplicate-key message is the dictionary KEY, not necessarily a duplicated
  thing. Read the stack: `IniToPlanConverter` inside a measure pass is the UI
  building a plan, not the loader registering units.

  And the lesson after that: the fix has to land in every file the game can
  open, not just the one the tooling refreshes. The refresh chain only ever
  touched the active mission, while the installer deploys every other `.ini`
  under `integration/missions/` too (drafts, older saves, edited chapters,
  scenarios) and the editor opens any of them. The KJ-500 crash was fixed in
  NORTHERN FRONT III FINAL NEWEST and still live in the FINAL, DRAFT and earlier
  copies listed right beside it: 32 aircraft in 9 deployed files on 25 Sep 2026
  (P-8s, KJ-500s, Y-9LGs, A-50s, MiG-25PDs and an E-3A).
  `fix_loadout_variants.py --all --write` sweeps everything the installer deploys,
  and `preflight --all` fails on any aircraft left with the crash while listing
  the older saves' other dangling references for information only. The old
  `<name> backup-<stamp>.ini` snapshots carry the crash too (104 more aircraft) and
  are left as they are: they are no longer deployed, a rewritten snapshot is no
  longer a snapshot, and `install-sest-packs.ps1 -PurgeBackups` removes the copies
  an earlier install put in the game.
- **A hull variant has to be declared, not just present.** The engine pools only
  the first `NumberOfVariants` sections of a `_variants.ini`; a `[VariantN]` block
  past that count is in the file yet unselectable, and a mission naming it gets the
  picker's *"MISSING: &lt;unit&gt; name or squadron reference"*. Murder Hornet's
  winning `usn_cvn_nimitz_2000s_variants.ini` declares 2 and ships 3 (CVN-70,
  *"#Not included atm"*) while AUS DEF asks for `Variant3`. `preflight` checks every
  `VariantReference` against the winning declaration, and `preflight --all` still
  lists AUS DEF's: an override that restores the count was built on another branch
  and withheld after a load hung, and it has not been proven in game since.
  Same carrier, second defect: its Type/class/hull names came solely from the
  deprecated MyGo Super Hornet's language file (line 1, behind a BOM), which was
  unsubscribed on 19 Sep 2026. A unit whose only name provider is on the way out
  gets its section carried verbatim in Collection Fixes (`CARRIED_VESSEL_NAMES`).
  The carry holds the text, not a pointer to the donor: reading the donor at build
  time dies the moment the donor leaves the export, the one case the carry exists
  for. While the donor is present the build compares the two and fails on drift.

- **A missile's guidance profile is a contract with the launcher.** Swapping a
  round into a proven launcher block is not always free: a `MidCourseCorrection`
  of 1 (radio command) or 3 (datalink) needs a guidance channel from an
  associated sensor with `WeaponChannels` above zero, and without one the mount
  never fires — no error, no log line, the ship just holds its missiles.
  `MidCourseCorrection=2` is the exception and is exempt: the wire *is* the
  guidance, and only 12 of 88 wire-guided mounts in the collection associate a
  sensor at all — vanilla's own submarines fire them from sensor-less tubes.
  (An earlier revision of this note said "1 or higher", which the corpus
  disproved.) The provider does not have to be `Type=Targeting`: the PLAN's
  `LJG-346A` is a `DirectedSearch` radar with 64 weapon channels and serves
  perfectly well.
  HMAS Warramunga sat on her NSMs for exactly this reason: the RAN Anzac and
  Hobart inherited Type 23 / F-100 blocks built for vanilla's Harpoon
  (`MidCourseCorrection=0`, no channel needed) and only the `Ammunition=` line
  was swapped to Red Storm Arsenal's datalink NSM. The rule was measured before
  it was believed — across vanilla and all 132 mods, 373 of 373 launcher blocks
  firing an MCC=3 round associate a sensor, and the only four that did not were
  ours. The round's own author wires every hull that fires it the same way.
  Three louder-looking suspects were adversarially refuted first and left
  alone: `MinAttackAltitude` degrades accuracy rather than vetoing launch, a
  terminal-approach distance beyond seeker range is that author's house style
  and flies fine, and the launcher geometry is byte-identical to a working
  donor. Check what a round demands of its mount, not just whether the ids
  resolve — `preflight` sees a resolvable reference either way.

- **A launcher is only a launcher inside its radar's search radius.** A TEL
  that fires through `ExternalGuidingSystems` looks for that system within its
  `ExternalGuidingSystemSearchRadius` — 0.5 nm for vanilla and Red Storm
  Arsenal launchers, 0.8 nm for the PLA pack and SAM Pack, 2 nm for NASAMS,
  5 nm for the S-400 mod — and outside it the mount never fires, with no error.
  The land-defence builder measures every battery's ring against the tightest
  radius in it and checks, from the files, that the radar it stands up actually
  provides the named system; a Patriot TEL from Red Storm Arsenal wants
  `AN/MPQ-65` and the SAM Pack radar provides `AN/MPQ-65_mi`, so the two mods'
  halves cannot be mixed however plausible the ids look.
- **An analyser and a generator must share one taxonomy or the pass is not
  idempotent.** The defence builder classifies what a site already has from
  the units' own files (gun, SHORAD, medium, area, BMD, search radar by the
  longest AAW round and its minimum engagement altitude). Its doctrine lists
  once filed a Vulcan under SHORAD and a Shilka-M4 (which carries Strela)
  under guns; each re-run then read those units back as the other layer and
  added another. Ring candidates are now filtered through the same classifier
  that reads them back, and `--catalog` names anything misfiled.
- **Hand-placed ships need the land mask too.** The land units go through the mask, so nobody
  checked the vessels: the Darwin surface group had been parked on the Tiwi Islands and a US
  destroyer on Palawan since the showcase was written. The generator now refuses to write a
  mission with a vessel ashore. A warship must also clear a 6 nm halo, since a position can be
  a water cell and still be a beach the group cannot manoeuvre in; a merchant only has to be on
  water, because a ferry legitimately starts alongside.

- **Gates before every push:** `check_load_order`, `check_dependencies`,
  `preflight` (every reference the missions make), `check_station_clash`,
  `check_weapon_employment` (every weapon can actually be fired by the mount
  carrying it), `check_stale_phrases` (retired claims, such as the pre-reveal
  AIM-424's, kept out of every builder, README and emitted file),
  `check_pack_fidelity` (every SEST Replenishment file is its upstream plus
  only the lines the pack inserts), full pack rebuilds. All exit non-zero;
  all have been
  negative-tested — the employment gate against both bugs it was built from,
  the stripped NSM datalink association and the GBU-53's 200 ft release band.
