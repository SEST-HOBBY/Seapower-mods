# Interoperability Report

What compatibility work exists in this collection, and what each decision rests on.

Generated from the builders themselves — every claim below is traceable to a file, a
comment or a recorded observation. Where a decision has no recorded justification it is
marked **UNSTATED** rather than given a plausible-sounding one.


**16 packs · 339 decisions · 121 files touched · 130 recorded limits**


## What the decisions rest on

| Authority | Decisions | Share | What it means |
|---|---:|---:|---|
| File semantics | 101 | 30% | Follows from the engine's override/merge rules — not a preference |
| UNSTATED | 57 | 17% | No recorded justification. The audit gap. |
| Upstream donor | 55 | 16% | Cloned from a block the mod's own author shipped and proved |
| In-game observation | 46 | 14% | Someone looked at it running — screenshots, visual checks |
| Engine precedent | 33 | 10% | Matched to what the engine/collection already does elsewhere |
| Real-world spec | 19 | 6% | Real aircraft or weapon performance figures |
| Comparison | 13 | 4% | Candidates compared on stated criteria before choosing |
| Player directive | 10 | 3% | The player asked for it explicitly |
| Author mandate | 5 | 1% | The upstream author's stated load-order requirement |

## Packs


### `f-15ex-revamp`

Adds ten cross-mod loadouts and six extra squadrons to dingtools' F-15 EX Eagle II by shipping a regenerated whole-file copy of its aircraft ini — so weapons that live in other subscribed mods (Dingtools Weapon Pack, Murder Hornet's AIM-174B, a SEST-authored AIM-424 riding US Naval Aviation's AGM-88G mesh) can be hung on the jet, while repairing upstream's mirror-symmetry and pod-height defects and keeping the file rebasable onto upstream updates.


**Files (9)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII.ini` | overrides | 3636386513 — F-15 EX Eagle II (dingtool… | It is the only mod in mods-source/ that ships this filename (`find . -iname usaf_f-15ex_SEII*.ini` returns only 3636386513/ plus this pack's own copy… |
| `SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII_squadr…` | overrides | 3636386513 — F-15 EX Eagle II (dingtool… | Same sole provider. build_squadrons() docstring: "Complete replacement usaf_f-15ex_SEII_squadrons.ini (whole-file override)" — upstream's two Kadena … |
| `SEST_F-15EX_Revamp/ammunition/sest_aim-424.ini` | adds | 3737267013 — United States Naval Aviati… | New SEST-namespaced id (no `sest_aim-424` exists anywhere in mods-source), so it adds rather than overrides. Mesh donor chosen because the [Models] b… |
| `SEST_F-15EX_Revamp/language_en/aircraft_names.ini` | merges | 3636386513 — F-15 EX Eagle II (dingtool… | language_*/ merges key-by-key, so only the new keys need shipping — but the builder still rebuilds from upstream's file and keeps upstream's own line… |
| `SEST_F-15EX_Revamp/language_cn/aircraft_names.ini` | merges | 3636386513 — F-15 EX Eagle II (dingtool… | Same builder path with lang="cn"; the Chinese Squadron1/2 names and callsigns are preserved rather than overwritten with English, per the same docstr… |
| `SEST_F-15EX_Revamp/language_en/loadout_names.ini` | merges | 3636386513 — F-15 EX Eagle II (dingtool… | Built by appending a `# ---------- SEST Revamp ----------` block of ten keys to upstream's file; all ten in-game names are prefixed "SEST " so a play… |
| `SEST_F-15EX_Revamp/language_cn/loadout_names.ini` | merges | 3636386513 — F-15 EX Eagle II (dingtool… | Same append; the ten Chinese loadout names (e.g. `Malice6=SEST 马利斯截击 (6x AIM-424)`) are authored by this pack, not taken from any donor. |
| `SEST_F-15EX_Revamp/language_en/ammunition_names.ini` | merges | none — written by integration/common/ai… | Only the single `sest_aim-424=` encyclopedia entry is shipped; language files merge key-by-key so no other mod's ammunition names are displaced. |
| `SEST_F-15EX_Revamp/_info.ini` | adds | none — INFO_INI literal in build_patch.… | Mod Manager metadata. Its Description names the dependency chain and the placement rule: "Requires the F-15SE (F-15EX) mod and Dingtools Weapon Pack;… |

**Decisions (30)** — In-game observation 10, File semantics 6, UNSTATED 4, Engine precedent 3, Comparison 2, Player directive 2, Upstream donor 1, Real-world spec 1, Author mandate 1


- **Ship a full regenerated copy of upstream's aircraft ini rather than a partial file, and require the pack to sit ABOVE the F-15EX mod in the Mod Manager.**  
  *File semantics* — README Install step 2: "place SEST F-15EX Revamp ABOVE the F-15EX mod (the patch carries a full modified copy of aircraft/usaf_f-15ex_SEII.ini, and the higher-listed mod wins the file)". Backed by docs/design-notes.md: "Unit files are whole-file overrides ... the highest mod's copy loads and the rest are *gone* — silently." data/load-ord…
  
  Effect: All 14 upstream loadouts plus the 10 SEST ones appear in the loadout menu (AvailableLoadouts now lists 24 keys). If the pack is ranked below the F-15EX mod it silently does nothing.
  
  If the donor changes: If dingtools updates the mod, the override hides his changes until mods-source/ is re-exported and build_patch.py re-run; the builder exits on any moved anchor ("AvailableLoadouts line not …

- **Clone upstream's own StrikeJSOW 6-station pattern for the new SEST_AntiShipLRASM6 rather than invent a carriage layout.**  
  *Upstream donor* — README: "6× AGM-158C-3 LRASM (surge fit, mirrors the JSOW 6-station pattern)". Verified against mods-source/3636386513/aircraft/usaf_f-15ex_SEII.ini:523-529 — [WeaponSystem2StrikeJSOW] uses Station1-4 |JDAM32 plus Station13/14 |WW; the new block uses the identical six stations and keys with dts_agm-158c-3 substituted. Upstream's own [Wea…
  
  Effect: A 6× LRASM anti-ship surge fit alongside upstream's 4× AntiShip.
  
  If the donor changes: If upstream renames or re-lays StrikeJSOW the pattern is no longer a live donor, but the pack's copy keeps working; the ammo/position-key validators fail loudly if dts_agm-158c-3 or JDAM32/…

- **Drop a Harpoon/AGM-84 fit from the planned additions.**  
  *Comparison* — README: "the Harpoon fit was dropped - LRASM and Quicksink cover anti-ship far better and the AGM-84 added nothing".
  
  Effect: No AGM-84 loadout on the F-15EX; anti-ship is LRASM (standoff) or GBU-31 Quicksink (close).
  
  If the donor changes: n/a — nothing shipped.

- **Validate every referenced ammunition id against ALL of mods-source (including _vanilla) rather than a hand-picked donor list, so no single mod becomes a hard dependency for an id several mo…**  
  *In-game observation* — build_patch.py step 3 comment: "Search ALL of mods-source (incl. _vanilla), not a hand-picked donor list: usn_aim-174b ships in four mods and dts_gbu-31 in three, so a narrow list turns 'any provider present' into a hard dependency on one specific mod (unsubscribing Murder Hornet failed this build)." Confirmed: usn_aim-174b.ini exists in…
  
  Effect: The AIM-174B fits work with any subscribed provider of usn_aim-174b, not only Murder Hornet.
  
  If the donor changes: If every provider of an id is unsubscribed the build exits with "unresolved ammunition ids: [...]" instead of shipping a loadout that would show an empty station in game.

- **Give the AIM-424 its own belly seat key (M424Positions / M424WPositions) instead of reusing the AIM-174B's shared AGM key.**  
  *In-game observation* — build_patch.py step 1b: "It shares stations 11-14 with the AIM-174B, whose AGM key (0,-0.002,0) seats IT flush - but the 424 renders with the AGM-88G mesh, whose origin rides lower, and in game it hung visibly below the CFT pylon. Raising the shared key would unseat the 174, so the 424 gets its own, 0.0015 higher." Generated file lines 2…
  
  Effect: MALICE rounds sit flush on the fuselage instead of floating below the conformal pylon; AIM-174B carriage is unchanged.
  
  If the donor changes: Keys are injected after upstream's AGMPositions line; the build exits if "M424Positions already defined upstream - re-check".

- **Add SEST174Positions=0,-0.001,0 as a dedicated seat for the belly AIM-174B rather than using the stock |AGM key.**  
  *In-game observation* — build_patch.py: "SEST174 seats the belly AIM-174B: |AGM raised 0.001 to sit flush with the fuselage (in-game call)."
  
  Effect: The four fuselage AIM-174Bs on BigStick174/ER and Truck174 sit flush.
  
  If the donor changes: Pack-local key; harmless if the loadouts are removed.

- **Fill both slots of the four fuselage dual racks with explicit single-segment seat keys (SESTR-OR/OL/FR/FL/AR/AL) instead of relying on |MTH's two-segment key.**  
  *Engine precedent* — build_patch.py step 1c: "|MTH's two pipe segments (x +/-0.0022, y -0.0025, z -0.01) are the rack's two slots; segment assignment per station is engine-internal, so every round gets an explicit single-segment seat instead: SESTR-OR/OL put the S11-14 rounds in the outboard slots, and the four free fuselage stations 18/19/22/23 are offset i…
  
  Effect: AAMT120Tanks and AAMT260Tanks show 8 belly rounds in real rack slots (16 missiles total with the 8 wing rounds).
  
  If the donor changes: Keys are pack-local; if upstream moves stations 18/19/22/23 the offsets become wrong silently (only the position-key existence check is automated, not the geometry).

- **Set SESTR-AR/AL rotations to -2,0,0 on the assumption that seat rotations ADD to the station's rotation.**  
  ***UNSTATED*** — build_patch.py step 1c, self-flagged: "Rotations: S13/14 carry the station's +3 pitch natively; their partners S22/23 sit on +5 stations, so -2 nets +3 (assuming seat rotations ADD to the station's; if in game they lean the other way the engine replaces, and AR/AL want 3,0,0 instead)." No in-game confirmation is recorded either way.
  
  Effect: If the assumption is wrong the four aft rack rounds lean 2 degrees nose-down instead of 3 nose-up.
  
  If the donor changes: Two lines in build_patch.py; nothing else depends on them.

- **Fix an earlier wrong SESTR-FR/FL z offset that had been read off the wrong station row.**  
  *File semantics* — Inline comment on the generated key: "SESTR-FRPositions=-0.0082,-0.0055,0.0335 # S19 z is -0.0335 like S18 (S20 owns 0.003 - the first cut used the wrong row and pushed this round aft)". Confirmed in upstream hardpoint table: Station18/19 z=-0.0335, Station20/21 z=0.003.
  
  Effect: The two forward rack rounds sit in the rack rather than displaced aft.
  
  If the donor changes: Pack-local.

- **Rail-allowance rule, revision three: a tank or an |MTW rack on the wing station restricts the inner-pylon side rails not at all; only a wide |WW store hung ON the wing station clears them.**  
  *In-game observation* — build_patch.py: "The rule, third revision, each step forced by in-game evidence. ... The first revision stripped every rail whenever the wing station carried anything but an MTW rack. Then MaliceER flew all four rails armed with AIM-260 beside three tanks and the user confirmed it looks right - the rails hold stores at the pylon's flanks…
  
  Effect: MaliceER/BigStick174ER keep 4× AIM-260 on the inner rails beside three tanks; loadouts hanging AIM-174B/AIM-424 on S16/17 get their rails cleared automatically.
  
  If the donor changes: clear_rails_under_wing_station() strips offenders and verify_rails_under_wing_station() then exits ("shares the wing pylon with Station16/17"), so a future edit cannot reintroduce the clip …

- **Exempt Truck174 and MaliceTruck from the rail rule so their side rails stay armed above an underslung |WW round.**  
  *Player directive* — build_patch.py: "The trucks fly their side rails armed ABOVE the underslung round - user call, same in-game-verified coexistence as MaliceER's rails-beside-tank." Implemented as `RAIL_EXEMPT = {(t, r) for t in ("MaliceTruck", "Truck174") for r in (1, 2, 5, 6)}`.
  
  Effect: The two 8-round trucks also carry 4× AIM-260 on the inner rails.
  
  If the donor changes: One set literal; removing it makes the guard strip those rails on the next build.

- **Lower the inner-pylon side rails (stations 1/2/5/6) by exactly 0.0007 so they sit level with the outer-pylon missiles — correcting an earlier 0.005 drop.**  
  *In-game observation* — build_patch.py SIDE_RAIL_DROP block: "CORRECTED. The first attempt dropped these 0.005 on the reasoning that they sat above the wing station (-0.0063) where the tank pylon attaches. That was an inference about the model, not a measurement, and it was too aggressive: the report was that ONE missile sat higher than the OTHERS, a relative d…
  
  Effect: Wing AAMs render at one height instead of one group riding visibly high.
  
  If the donor changes: lower_side_rails() asserts both wings move together, all four end at the same height, and none reaches the tank pylon at Station17's y, exiting otherwise. Only [WeaponSystem1] is touched "W…

- **Leave the side-rail rotations (0,0,±90) alone.**  
  *Engine precedent* — README: "The rotations were checked and left alone. 0,0,±90 on paired flanking rails is the dominant convention across the collection (F/A-18E/F, A-10C, Mi-8, F-104, Tornado IDS), and plan_j-15a uses byte-identical values — S1+S5 = 0,0,90, S2+S6 = 0,0,-90. Only the Tornado ADV rolls such pairs oppositely." Upstream file confirms Station1…
  
  Effect: None — deliberate non-change.
  
  If the donor changes: n/a

- **Repair AirToAirIntercept's asymmetric outer pylons by changing Station10 to match Station9 (AIM-9X → AIM-260), not the reverse.**  
  *Engine precedent* — build_patch.py symmetry comment: "Station10 is the stale half, not Station9: it reads plain `dts_aim-9x` with no position key, which is the Default/AirToAir pattern, while every other wing-rail missile in this loadout carries the `|120` rail offset." Plus the survey of upstream's own fits: "Every other fit in the mod pairs those two stat…
  
  Effect: AirToAirIntercept becomes a clean 12× AIM-260 (was 11 + 1 AIM-9X).
  
  If the donor changes: README notes the alternative is available: "If you would rather keep a short-range pair, flipping it the other way is a one-line change in SYMMETRY_FIXES." fix_symmetry() exits if the targe…

- **Scope every symmetry edit to a named section rather than doing a file-wide replace.**  
  *File semantics* — build_patch.py: "Both edits are scoped to a named section: `Station10=dts_aim-9x` is CORRECT in 18 other loadouts, so a blind file-wide replace would have rewritten every one of them." The builder additionally exits if the target string appears more than once in the section.
  
  Effect: Only AirToAirIntercept changes; the other 18 fits keep their Sidewinders.
  
  If the donor changes: n/a

- **Mirror upstream's duplicate Station4 to the left wing (x +0.0486 → −0.0486).**  
  *File semantics* — build_patch.py: "Stations 2, 3 and 4 sit at the IDENTICAL point x=+0.0486 - 'Right Wing pylon outer' plus TWO 'Right Wing pylon bottom'. There is no left-hand pylon-bottom station at all ... Nothing in WeaponSystem1 uses them today, so this is a latent trap rather than a live bug". Verified in the upstream hardpoint table (Station2/3/4 a…
  
  Effect: None today (no shipped loadout uses S3/S4 in WeaponSystem1); makes the pair usable for future fits.
  
  If the donor changes: README records the deliberate non-fix: "that 'pylon bottom' still shares a point with 'pylon outer' on each side — is upstream's geometry, and correcting it would mean inventing a vertical …

- **Move the AAQ-33 and AAQ-13 pod stations (26/27) to the pair's mean height with matched z, and delete their symmetry-guard exemption.**  
  *In-game observation* — SYMMETRY_FIXES comment: "the delta is 0.0035 (~24 cm) - an order of magnitude more than the pods' ~5 cm diameter difference justifies. The AAQ-33 hung visibly lower than the AAQ-13 on every strike fit. Both now sit at the pair's mean height and the same z; the targeting pod keeps 0.0004 (~3 cm) extra drop for its larger diameter." Commit…
  
  Effect: Targeting and navigation pods sit as a coherent pair on every strike fit.
  
  If the donor changes: Two SYMMETRY_FIXES entries; the build exits if upstream edits those lines.

- **Make the build fail on any mismatched mirror pair, checked PER weapon system, with only stations 16/17 exempt.**  
  *File semantics* — check_symmetry() docstring: "Each [WeaponSystemN] block owns its own station table, and a loadout named [WeaponSystemN<Name>] indexes into THAT table - conflating them produces a page of false positives, because Station3 means 'right wing pylon bottom' in WeaponSystem1 and 'right bottom aft' in WeaponSystem2." Echoed in design-notes.md: …
  
  Effect: No shipped loadout can hang a store on one wing with nothing opposite.
  
  If the donor changes: Guard only; removing it does not change the built file.

- **Keep the AAMT twin-rack mesh VISIBLE on the three-tank trucks and fill all eight belly slots (16 missiles, 3 tanks).**  
  *Player directive* — build_patch.py AAMT120Tanks comment: "The AAMT rack mesh stays VISIBLE (user call: the fuselage racks are the look) and each of the four belly racks is FILLED with two real rounds." Its SubModelsToHide omits AAMT, unlike every other new fit.
  
  Effect: AAMT120Tanks / AAMT260Tanks show the fuselage racks loaded rather than a hidden rack with floating rounds.
  
  If the donor changes: Adding AAMT back to SubModelsToHide would re-hide the racks; design-notes.md warns "Rack submodels (SubModelsToHide) must track the fit: the AAMT twin-rack stayed visible on fits whose stat…

- **Restore both AAMT truck+fuel fits to 16 rounds after an interim cut to 12, seating the wing tanks flush on the normal WT seat instead of slinging them low.**  
  *In-game observation* — Builder comment: "per wing, two rails flanking the tank pylon (S1/S5 left, S2/S6 right) with the tank FLUSH on the normal WT seat between them - the classic F-15 tank-between-rails picture - plus two on the outer pylon (S7-S10), which sits 0.013+ outboard of the tank and never contested it. The earlier clip came entirely from slinging th…
  
  Effect: Both long-range trucks carry 16 AAMs plus three 610 gal tanks with no visual clipping.
  
  If the donor changes: The SESTWTF override key was deleted; tanks now ride upstream's own WT key, so an upstream WT change moves them.

- **Ship the AIM-424 MALICE as a peer of the AIM-174B, aligned key-for-key against U.S. Navy 2027's usn_aim-174b, with a named list of deliberate deltas.**  
  *Comparison* — integration/common/aim424.py: "Aligned to usn_aim-174b as shipped by U.S. Navy 2027 Capabilities (3606774881) - the version that actually wins the load order in this collection, and the card the MALICE gets compared against in game. Same explicit-drag flight model, same 150,000 ft loft ceiling, same fragmentation warhead class, same data…
  
  Effect: MALICE fits trade 26 nm of reach for a 40 nm active / 80 nm passive seeker and a full anti-emitter mode; the two encyclopedia cards are directly comparable.
  
  If the donor changes: If U.S. Navy 2027 is unsubscribed or reordered, the 174B card the MALICE was balanced against changes (four mods ship usn_aim-174b with different stats) — the alignment silently stops holdi…

- **Keep DragCoefficient explicit at 3.6 rather than -1.**  
  *In-game observation* — aim424.py: "THIS KEY MUST STAY EXPLICIT: at -1 the engine back-solves 8.14 from the airframe and the missile loses roughly a third of its reach." Repeated inline: "DragCoefficient=3.6 // explicit - a -1 here back-solves to 8.14 and kills the reach".
  
  Effect: The MALICE actually reaches its advertised 290 nm.
  
  If the donor changes: Single line in the shared module; affects all four packs that ship the missile.

- **Remove ResourcesMeshScale and keep the [Models] block byte-identical to US Naval Aviation's usn_agm-88g.**  
  *In-game observation* — aim424.py: "REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the missile stopped rendering as an AARGM-ER afterwards - the model block falls back to AssetBundleMesh=usn_rim-7, a short fat Sea Sparrow, which is exactly what showed up under the wing. The [Models] block below is now byte-identical to US Naval Aviatio…
  
  Effect: The MALICE renders as an AARGM-ER rather than a Sea Sparrow.
  
  If the donor changes: Requires 3737267013 United States Naval Aviation to stay subscribed for assets/models/ammunition/agm-88/agm-88g.obj; without it "the game falls back to the RIM-7 asset-bundle stand-in, same…

- **Write byte-identical copies of ammunition/sest_aim-424.ini and the partial language_en/ammunition_names.ini from four different SEST packs instead of factoring the missile into one pack.**  
  *File semantics* — integration/common/aim424.py docstring: "All four SEST packs that carry MALICE fits write identical copies of ammunition/sest_aim-424.ini and a partial language_en/ammunition_names.ini - identical same-path files are a safe overlap whichever pack sits higher in the Mod Manager." Confirmed: the same file is emitted by f-15ex-revamp, rafal…
  
  Effect: Any one of those packs alone gives a working MALICE; installing several cannot produce a version conflict.
  
  If the donor changes: All copies must be regenerated together — an edit to common/aim424.py that is not followed by rebuilding every pack leaves divergent same-path files, and then load order would decide which …

- **Replace the squadron file with eight squadrons, keeping upstream's two byte-identical at index 1 and 2 and reusing the two shipped liveries in rotation for the six added units.**  
  *Real-world spec* — F15EX_SQUADRONS comment: "Upstream defines two squadrons - the 44th and 67th FS at Kadena ... A mission that wants more than two distinct F-15EX units has nothing to reference, so this adds the type's other announced operators. The mod ships only those two skins, so the added squadrons reuse them in rotation and differ by identity and ca…
  
  Effect: Missions can field eight distinct F-15EX units; SEST RAAF Bases populates seven Australian bases with them. Squadrons 3-8 wear one of the two Kadena paints.
  
  If the donor changes: build_squadrons() exits if upstream's Squadron1/2 livery changes ("upstream Squadron{i} livery changed ... rebase this patch") or if upstream stops defining exactly two squadrons. If this p…

- **Invent callsigns (Bench, Probe, Redhawk, Griffin, Minuteman, Talon) for the six added squadrons.**  
  ***UNSTATED*** — README states this plainly rather than justifying it: "Callsigns for the added units (Bench, Probe, Redhawk, Griffin, Minuteman, Talon) are flavour, not documented radio callsigns. The squadron designations and basings are real."
  
  Effect: Radio traffic for the six added units uses invented callsigns.
  
  If the donor changes: Four-tuple entries in F15EX_SQUADRONS; changing them changes the merged Callsigns= line only.

- **Author ten Chinese loadout names in LOADOUT_NAMES["cn"] (e.g. "SEST 马利斯截击 (6x AIM-424)").**  
  ***UNSTATED*** — No comment or source is recorded for the Chinese loadout strings — in contrast to build_aircraft_names(), which is explicitly careful with upstream's existing Chinese text ("kept verbatim - including the Chinese ones - so nothing already translated is replaced by English text").
  
  Effect: Chinese-language players see these ten fits under translated names of unverified quality.
  
  If the donor changes: Dict literal in build_patch.py; merged into language_cn so it displaces nothing upstream.

- **Pick per-loadout ReadyUpTime values of 25 / 30 / 35 minutes for the new fits.**  
  ***UNSTATED*** — No comment explains the choice. Upstream's own values are 15 (AirToAirIntercept), 30 (StrikeJSOW, AntiShip, AAMT120); the new blocks use 35 (SEST_AntiShipLRASM6, Truck174, MaliceTruck, both AAMT*Tanks), 25 (Quicksink) and 30 (BigStick174/ER, Malice6, MaliceER). CoolDownTime is uniformly 60, matching upstream.
  
  Effect: Turnaround time before a sortie varies by 10 minutes across the new fits with no recorded basis.
  
  If the donor changes: Literal values in NEW_SECTIONS.

- **Use the outer wing pylons in the ER fits because they render regardless of load.**  
  *In-game observation* — BigStick174ER comment: "The outer wing pylons are baked into the airframe model and render whether or not they carry anything, so use them: AMRAAM on the pylon2 inner stations, AIM-9X outboard of them on the outermost pair." (Note the README's older description of BigStick174ER — "outer wing pylons removed entirely" — no longer matches t…
  
  Effect: The ER fits carry 2× AIM-120D-3 and 2× AIM-9X for self-escort instead of leaving visible pylons empty.
  
  If the donor changes: n/a

- **Keep the Dingtools Weapon Pack above all dingtools mods, per the author.**  
  *Author mandate* — data/mod-catalog.json, 3760871384: load_order = "Author: 'Put this mod ABOVE any of my mod' (B-52H, F-15EX, B-1B, SAAB AEW&C)"; 3636386513 carries the same note "Keep Dingtools Weapon Pack ABOVE all dingtools mods". README Install: "Keep Dingtools Weapon Pack above everything of dingtools' as usual." Load-order tokens place 3760871384 at…
  
  Effect: The AIM-260 / AIM-120D-3 rounds in every new loadout resolve to the weapon pack's versions.
  
  If the donor changes: Ordering only; if the F-15EX mod outranks the weapon pack the same loadouts silently use dingtools' aircraft-bundled stats instead.

**Must stay subscribed**

- 3636386513 — F-15 EX Eagle II (dingtools). The base aircraft and the source of every file this pack rebuilds. Without it the pack overrides nothing and there is no F-15EX; build_patch.py cannot even run (it reads mods-source/3636…
- 3760871384 — Dingtools Weapon Pack (dingtools). Supplies the dts_ rounds every new loadout uses (aim-120d-3_w, aim-260/_w, aim-9x, gbu-31, agm-158c-3, anaaq-33, anaaq-13). Must sit ABOVE the F-15EX mod per the author; several ids…
- 3430135740 — F/A-18 Murder Hornet with AIM-174B (Cropgun). Named in _info.ini as the AIM-174B source, but NOT a hard dependency: the builder validates ids against all of mods-source and usn_aim-174b is also shipped by 3426791311,…
- 3737267013 — United States Naval Aviation (misaka). Hard asset dependency for the AIM-424: ResourcesFolder=assets/models/ammunition/agm-88/ resolves into this mod. Unsubscribe it and the MALICE renders as the usn_rim-7 Sea Sparro…
- 3606774881 — U.S. Navy 2027 Capabilities mod (Prof_CH4OS). Balance reference rather than runtime dependency: the AIM-424's flight model is aligned key-for-key against the usn_aim-174b this mod ships, chosen because it "actually w…
- Vanilla — usaf_tank_610_f-15 (the 610 gal tank; NEW_SECTIONS header: "The 610 gal tank is vanilla"), validated via mods-source/_vanilla/original.
- Downstream: SEST RAAF Bases (integration/raaf-bases) consumes Squadron3-8 of this pack; data/mod-catalog.json lists SEST_F-15EX_Revamp in its build_after.

**Known limits**

- Only two liveries exist in the upstream mod, so the six added squadrons reuse 44_fs.jpg / 67_fs.jpg in rotation: "The mod ships only those two skins, so the added squadrons reuse them in rotation and differ by identity and callsi…
- Side rails S1/2/5/6 are identical in every loadout and cannot be given different heights from each other: "All four are identical in every loadout - same y, same |120 key, net -0.00050. They cannot sit at different heights from e…
- Any side-rail drop beyond the measured 0.0007 is explicitly refused as guesswork: "Dropping further is guesswork until somebody who can see the model says the whole group is too high."
- Upstream's "pylon bottom" stations still share a point with "pylon outer" on each wing; left uncorrected because "correcting it would mean inventing a vertical offset that can't be verified from the model".
- The AIM-424's visual size cannot be changed from the ini: "The visual renders at the shared usn_rim-7 mesh's native size, same as usn_agm-88g, and cannot be resized from the ini (ResourcesMeshScale, the one candidate key, breaks …
- AIM-424 reach is deliberately capped below the AIM-174B: "MaxLaunchRange 290 vs 316 nm - it has to fit inside an F-35 weapons bay."
- SESTR-AR/AL rotation is an untested assumption about whether seat rotations add to or replace the station's rotation.
- Rack slot assignment is opaque to the ini: "segment assignment per station is engine-internal", which is why every round gets an explicit single-segment seat.
- StrikeNuke's single B61 on one wing station is left asymmetric on purpose (SYMMETRY_EXEMPT = {(16,17)}) — "Upstream's choice, and a real single weapon carry is a thing."
- Callsigns for the six added squadrons are acknowledged flavour, not documented radio callsigns.
- The README's BigStick174ER description ("outer wing pylons removed entirely") is stale relative to the shipped block, which loads Stations 7-10; the builder comment is the accurate source.
- The builder comment "dts_gbu-31 in three" mods is now four in the current export (3741944366, 3553116604, 3760871384, 3652097318) — harmless drift, since validation scans all of mods-source rather than the count.

### `growler-ngj-malice`

Three EA-18G identifiers and three APG-79 Super Hornets are shipped by four different Workshop mods that whole-file-override each other; this pack rebases each identifier on whichever donor currently wins the canonical load order, gives the legacy Growler the AN/ALQ-249 NGJ set the other two already had, adds shared AIM-424 MALICE / AIM-260 fits across all six airframes, and repairs the geometry and fuel defects (floating tanks, stores on the NGJ pylon, a 4500-lb tank, an unreachable RAAF squadron) that the overrides expose.


**Files (18)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `aircraft/usn_ea-18g.ini` | overrides | 3606774881 — U.S. Navy 2027 Capabilitie… | Four mods ship aircraft/usn_ea-18g.ini (3426791311, 3606774881, 3430135740, 3737267013). Navy 2027 sits highest in data/load-order.tokens.txt (line 1… |
| `aircraft/usn_ea-18g_2020s.ini` | overrides | 3426791311 — [DEPRECATED] Boeing F/A-18… | Sole shipper of this filename in mods-source; no competition. It already carries the NGJ implementation, so build_growler() runs with upgrade_ngj=Fal… |
| `aircraft/usn_ea-18g_2020.ini` | overrides | 3737267013 — United States Naval Aviati… | Sole shipper of this filename. Also already NGJ-equipped, so it goes through the same upgrade_ngj=False guard path. |
| `aircraft/usn_fa-18f_blk3.ini` | overrides | 3606774881 — U.S. Navy 2027 Capabilitie… | Shipped by 3426791311, 3606774881, 3430135740 and 3737267013; Navy 2027 is highest in the canonical order. build_super_hornet() docstring: 'Every Nav… |
| `aircraft/usn_fa-18f.ini` | overrides | 3606774881 — U.S. Navy 2027 Capabilitie… | Same four-way contest, same winner. Included because it has 'the same radar class and station layout' as the Block III (build_super_hornet docstring). |
| `aircraft/usn_fa-18e.ini` | overrides | 3606774881 — U.S. Navy 2027 Capabilitie… | Navy 2027 wins the file; but because this pack shadows it wholesale, USNA's newer buddy-tanker content would vanish, so port_tanker_fit() re-lifts [W… |
| `aircraft/usn_ea-18g_squadrons.ini` | overrides | 3430135740 — F/A-18 Murder Hornet with … | Shipped by 3426791311, 3430135740 and 3737267013; Murder Hornet is highest (line 22 vs 35 and 59) AND is the mod that actually painted the RAAF liver… |
| `aircraft/usn_fa-18f_squadrons.ini` | overrides | 3430135740 — F/A-18 Murder Hornet with … | Same three-way contest, same winner; it owns the [Squadron10] RAAF entry being retired (guard: 'if not m or "raaf_f18f.png" not in m.group(0): sys.ex… |
| `aircraft/usn_fa-18f_blk3_squadrons.ini` | overrides | 3430135740 — F/A-18 Murder Hornet with … | Same contest and winner; NumberOfSquadrons=7→8 with a new [Squadron8] Nation=Australia. Guard refuses to proceed if upstream adds its own: 'if "raaf"… |
| `ammunition/usn_tank_610_f-18.ini` | overrides | 3426791311 — [DEPRECATED] Boeing F/A-18… | Three mods ship it — 3426791311 (order line 35), 3737267013 (59) and 3413868677 Red Storm Arsenal (139, deliberately bottom-of-order). F/A-18E/F's co… |

*…and 8 more.*

**Decisions (29)** — In-game observation 8, Upstream donor 7, File semantics 4, Engine precedent 3, UNSTATED 3, Comparison 2, Player directive 2


- **Rebase each of the six airframe files on whichever donor mod currently wins the canonical Mod Manager order, rather than on a single preferred mod.**  
  *File semantics* — build_patch.py docstring: 'The three Growler identifiers in the installed collection come from three different Workshop mods. This builder deliberately rebases each identifier on the file that currently wins the user's canonical load order, then adds SEST loadouts without changing the original choices.' Cross-checked against data/load-or…
  
  Effect: The player keeps every upstream edit that was already winning (Navy 2027's Growler and Super Hornets, F/A-18E/F's 2020s, USNA's 2020) and simply gains loadouts on top; no upstream mod's wor…
  
  If the donor changes: If a donor is unsubscribed the pack's shipped copy keeps loading, so the aircraft still exists — but it is frozen at the donor's exported state and can no longer be rebuilt (build_patch.py …

- **Pack must sit ABOVE U.S. Navy 2027 Capabilities, F/A-18E/F and US Naval Aviation in the Mod Manager, as part of an unbroken SEST block at the top.**  
  *In-game observation* — tools/check_load_order.py docstring: 'Move anything above it and the patch silently stops applying - no error, no warning, it just quietly does nothing. That is exactly what happened when U.S. Navy 2027 was moved above Euromod: it jumped over SEST_Growler_NGJ_MALICE at the same time, and the Growler pack went inert.' Restated in docs/des…
  
  Effect: With the order wrong, none of the NGJ/MALICE loadouts appear at all — the failure mode is invisible, not an error.
  
  If the donor changes: Order is enforced by tools/check_load_order.py, which computes the rules from shared filenames rather than a hand-maintained list, so a newly-subscribed mod shipping any of these files is c…

- **Replace the legacy Growler's two ALQ-99 sensor systems and their mesh blocks with a single AN/ALQ-249 system plus the NGL-LB and ALQ-249 pod meshes, cloned from the mod that already had the…**  
  *Upstream donor* — upgrade_legacy_growler() rewrites NumberOfSensorSystems=7→6, substitutes '[SensorSystem5] #AN/ALQ-249 … Mount=ALQ-249', re-indexes GPS 7→6, swaps 'ALQ-99=ALQ-99\nALQ-99_C=ALQ-99_C' for 'NGL-LB=NGL-LB\nALQ-249=ALQ-249', and emits mesh blocks byte-identical to 3426791311/aircraft/usn_ea-18g_2020s.ini lines 633-641 ('Mesh=ngllb' / 'Mesh=alq…
  
  Effect: usn_ea-18g gains a working Next Generation Jammer (400 km, PeakPower 75 kW) and the visible NGJ pods in place of 1970s ALQ-99 pods; all three modern Growlers now behave alike.
  
  If the donor changes: The mesh assets live in 3426791311's (and Red Storm Arsenal's) assets/models/vechicle/aircraft/ea-18g/ folder — asset paths resolve across mods, so unsubscribing F/A-18E/F while keeping RSA…

- **Ship the AN/ALQ-249 sensor definition in the pack's own systems/sensors.ini rather than depending on a donor mod to define it.**  
  *File semantics* — tools/check_mod_conflicts.py: 'The proof for systems/ is that 89 mods ship systems/sensors.ini ranging from 8 lines to 8141. If the winner replaced the file, an 8-line one would delete every sensor in the game. It does not, and SEST_Growler_NGJ_MALICE's own 11-line sensors.ini adds the AN/ALQ-249 without removing anything.' Values verifi…
  
  Effect: The jammer resolves for every Growler even if the mod that originally defined it moves or is disabled, and its numbers are unchanged from the established implementation — 'this patch change…
  
  If the donor changes: Safe: merge semantics mean this file cannot delete other mods' sensors and other mods' copies cannot delete it.

- **Never substitute a fuel-tank id between airframes — each SEST fit uses whatever wing tank that airframe's own loadouts already hang on stations 27/28 (detect_wing_tank), defaulting to usn_t…**  
  *In-game observation* — detect_wing_tank docstring: 'substituting a mesh from a different aircraft's model leaves the tanks visibly low and detached, because the mesh origin is wherever the tank sits on that other model. So the SEST fits copy whatever the airframe already flies.' History block: 'Round 1 (earlier session): swapping fits TO f-18_fuletank made the…
  
  Effect: Tanks render seated on the pylon on every airframe; the Growlers keep usaf_tank_610_f-15 / usn_tank_610_f-18 and the Super Hornets keep usn_tank_1200_f-18.
  
  If the donor changes: Detection is dynamic — if an upstream author changes which tank his fits carry, the next rebuild follows him automatically.

- **Reject the original 'station geometry is tuned around each airframe's own tank mesh' theory, and instead re-mesh usn_tank_610_f-18 to render the vanilla F-15C 610 gal tank.**  
  *In-game observation* — TANK MESH HISTORY block: 'Round 2 (in-game reports on the 2020/2020s Growlers and the E tanker): f-18_fuletank hung low ON ITS OWN airframes too, and seat offsets of 0.0015 then 0.003 produced no visible change. Stations 27/28 carry IDENTICAL coordinates on all four airframes, so the coupling theory cannot hold - the truth is simpler: f-…
  
  Effect: Wing tanks on the 2020/2020s Growlers and the F/A-18E tanker sit flush under the pylon instead of riding low; fuel data untouched.
  
  If the donor changes: Guarded: 'if old not in text: sys.exit("usn_tank_610_f-18: upstream Models block changed - re-check the re-mesh")' — an upstream model-block edit stops the build rather than silently shippi…

- **Override usn_tank_1200_f-18 to put Fuel back to 1800 (from Murder Hornet's 4500), changing nothing else in the file.**  
  *In-game observation* — TANK_OVERRIDE header: 'Only Fuel changes, 4500 -> 1800, which is what both the genuine Hornet tank (usn_tank_610_f-18) and the vanilla F-15 610 gal tank carry. 4500 was giving the fits that used it 2.5x the external fuel of the ones that did not, which is why NGJ MALICE showed ~1433 nm against the SEAD fits' ~860.' README: 'That closes t…
  
  Effect: Every external tank across all six airframes now carries the same 1800; the MALICE fits stop out-ranging the SEAD fits by 2.5x. Overall Super Hornet range with tanks drops accordingly.
  
  If the donor changes: This is a whole-file override of a Murder Hornet ammunition file — if the pack is disabled or outranked, 4500 returns; if Murder Hornet updates the tank's mesh block the override silently k…

- **One pylon convention for the Growler: fuselage = AMRAAM, inboard = fuel, mid-wing = NGJ pods and nothing else, outboard = heavy stores; enforced at build time.**  
  *In-game observation* — Builder comment block: 'The ALQ-249 and NGL-LB pod meshes are baked into the airframe at that pylon and cannot be moved from the ini - they are submodels with no Position key. So anything hung there intersects them, which is what the AGM-88G pair on stations 13/14 was doing. It was never the fuel tanks: those are on the inboard pylon, a …
  
  Effect: Growler weapons no longer render through the jamming pods.
  
  If the donor changes: The check runs over ALL loadouts in the file, upstream's included, so a donor update that re-introduces a mid-wing store breaks the build loudly instead of shipping a visual clash.

- **Accept that the Growler outboard pylon is a single pair (stations 3/4) and re-cut Murder Hornet's four- and six-AGM SEAD fits so they differ by fuel instead of by weapon count.**  
  *Engine precedent* — Comment: 'CONSEQUENCE: the outboard pylon is a SINGLE PAIR, stations 3 and 4. Under this convention a Growler carries TWO heavy weapons, not four or six. The four- and six-AGM fits cannot exist as such, and are re-cut below to differ by fuel instead of by weapon count.' GROWLER_FIT_PLAN re-cuts MurderHornetSEADHeavy ('clean SEAD: 2x AGM-…
  
  Effect: Three upstream SEAD fits lose stores — a Growler now carries at most two AARGM-ER. Direct nerf to the Growler's anti-radiation payload, taken deliberately for visual correctness.
  
  If the donor changes: apply_pylon_convention() rewrites only loadouts named in GROWLER_FIT_PLAN and prints a line whenever a fit's store count changes ('{loadout} - {before} -> {after} stores: {why}'); loadouts …

- **Upstream loadouts that hide fule_tank_point while mounting a wing tank get that entry stripped from their hide list (fix_floating_tanks), and SEST fits are checked for the same mistake (ver…**  
  *Upstream donor* — fix_floating_tanks docstring: 'Several upstream fits hide fule_tank_point - the WING tank attachment - while mounting tanks on stations 27/28, so the tanks float unattached. Upstream's own external-fuel ("EF") loadouts show the correct pattern: tanks on 27/28 with the point left visible.' verify_tank_points restricts itself on principle:…
  
  Effect: Wing tanks render attached to their pylon in every affected upstream fit, not floating in mid-air.
  
  If the donor changes: Purely additive to the hide-list logic and re-derived each build; if upstream fixes it themselves the pass simply finds nothing (it prints the count of repaired loadouts).

- **'NGJ Long Range' carries two wing tanks and leaves the centreline empty — and is added to every Growler, superseding an earlier three-tank centreline version.**  
  *In-game observation* — LONG_RANGE comment: 'The centreline is the EW station, not a wet one - in game the third tank sat inside the Growler's centre jamming equipment (user screenshot). And "either side of the NGJ" cannot be four tanks: the model carries exactly ONE pair of wing tank pylons (fule_tank_point, stations 27/28), the airframes end at NumberOfStatio…
  
  Effect: All three Growlers get a max-persistence jamming fit (2 tanks, 2 AIM-260, no ARMs); the requested four-tank version was refused as not mesh-possible.
  
  If the donor changes: Independent of donors; verify_station_geometry() refuses to emit a fit that references a station the airframe does not define.

- **Block III MALICE is a clone of Murder Hornet's Interceptor block with AIM-174B → sest_aim-424, applied to all three APG-79 Super Hornets.**  
  *Upstream donor* — BLOCK_III_LOADOUT header: 'Counter-air / anti-emitter fit based on the proven Murder Hornet Interceptor station geometry. MALICE replaces the four AIM-174Bs.' Verified against 3606774881/aircraft/usn_fa-18f_blk3.ini [WeaponSystem1MurderHornetInterceptor]: identical SubModelsToHide string, same Station1/2 AIM-9X, same 30-33 quad, same Sta…
  
  Effect: F/A-18E, F and F Block III gain a four-MALICE counter-air fit that hangs exactly where the author's proven AIM-174B fit hangs.
  
  If the donor changes: verify_station_geometry() fails the build if any station used is not defined in the donor's WeaponSystem1 table, so a donor re-layout is caught.

- **Derive SEST_Intercept260 (8x AIM-260) by cloning the in-game-verified MALICE block and swapping every AIM-424 and AIM-120D3 for dts_aim-260.**  
  *Upstream donor* — derive_intercept260 docstring: 'A pure AIM-260 CAP fit, cloned from the in-game-verified MALICE block. Same stations, same tank, same SubModelsToHide - only the rounds change.' Guarded per round: 'if n == 0: sys.exit(f"{source_name}: donor no longer carries {old}")'. Commit 01e98d9 'Super Hornets: Intercept (8x AIM-260) on all three airf…
  
  Effect: Eight AIM-260 JATM plus wingtip Sidewinders, selectable under any squadron — 'which on the F/A-18F includes 1 SQN RAAF - that is the RAAF kitout.'
  
  If the donor changes: Requires dts_aim-260 from Dingtools Weapon Pack (3760871384); without it the stations reference a missing round.

- **In the ER/Escort fuel-heavy fits, delete stations 32/33 when the wing pylons go wet.**  
  *In-game observation* — derive_hornet_escorts comment: 'S32/33 (x +/-0.0328) sit 0.0003 from the wing tank stations 27/28 (x +/-0.0331) - in game those AIM-260 rode ON the fuel pylon, inside the tank. With the wing pylons wet they must go: the ER fit is 6x AIM-260 + 2x AIM-9X + 3 tanks.' Docstring also states the ceiling: 'Three external tanks is this airframe'…
  
  Effect: SEST_Intercept260ER trades two JATM for two wing tanks (6 + 3 tanks); SEST_Escort260 drops two more for the long-legged CAP. The user's five-tank request was refused honestly.
  
  If the donor changes: Self-contained; guard 'if er.count(wing_tank) < 3: sys.exit("escort fit failed to gain its wing tanks")'.

- **Derive SEST_SEAD260 for the 2020-family Growlers by cloning the airframe's own [SEAD] fit and upgrading whatever ARM/AMRAAM generation it carries to AGM-88G + AIM-260.**  
  *Upstream donor* — derive_sead260 docstring: 'cloned from the airframe's own [SEAD] fit (the legacy Growler's reshaped MurderHornetSEADHeavyTanks already IS this fit, so it is skipped rather than duplicated under a second name)' and 'Adaptive: each airframe's SEAD carries its own era of rounds… require that at least one swap actually landed so a silently-e…
  
  Effect: The 2020 and 2020s Growlers get one best-of SEAD fit; usn_ea-18g does not, because its re-cut MurderHornetSEADHeavyTanks is already that fit.
  
  If the donor changes: Output confirms it: usn_ea-18g_2020(.s).ini list SEST_SEAD260, usn_ea-18g.ini does not.

- **Swap the AGM-84N Harpoons out of the Super Hornets' anti-ship fits for b-2_lrasm.**  
  *Upstream donor* — replace_harpoons docstring: 'MurderHornetAntiShip and MH_AntiShipEF are the only fits on these airframes still carrying Harpoon. b-2_lrasm already flies from this airframe in MH_LRASM, so the substitution needs no geometry change - the stations involved (30-33) are the same ones that carry the AIM-174B.' Fails closed: 'if n == 0: sys.exi…
  
  Effect: Every Super Hornet anti-ship fit fires LRASM instead of a 1970s Harpoon — a straight capability upgrade the player did not opt into per-fit.
  
  If the donor changes: b-2_lrasm is supplied by 3480965706 (B-2 Spirit) / 3607989779 (F-35C Alt. Loadouts); unsubscribe both and these fits lose their round. Note the mod that already used it (MH_LRASM) has the s…

- **Port US Naval Aviation's buddy-tanker fit onto the F/A-18E verbatim (E-model only), because this pack shadows the file it arrived in.**  
  *Upstream donor* — port_tanker_fit docstring: 'USNA's 2026-08-25 update added a Tanker loadout to usn_fa-18e - a D-704 buddy refuelling store on the centreline (probe-and-drogue, transferable external fuel) with two wing tanks. This pack shadows that file wholesale, so without porting it the update would silently vanish. The blocks are lifted verbatim from…
  
  Effect: The F/A-18E keeps its buddy-tanker role (Station29=usn_d-704|FT_Center, [AerialRefuelingTanker] TankerSystems=ProbeAndDrogue) despite being overridden.
  
  If the donor changes: Guarded twice — 'USNA tanker blocks not found - upstream changed again' and 'Tanker already declared - drop this port' (so the port self-retires if Navy 2027 ever adds its own).

- **Two AIM-260 were injected into the ported Tanker fit's stations 11/12.**  
  ***UNSTATED*** — port_tanker_fit: block = m.group(0).replace('Station2=usn_aim-9x\n', 'Station2=usn_aim-9x\nStation11=dts_aim-260\nStation12=dts_aim-260\n', 1), with only a mechanical guard ('tanker AIM-260 injection failed') and no recorded rationale — the docstring says the blocks are 'lifted verbatim', which this one deliberately is not.
  
  Effect: The buddy tanker flies armed with two JATM the mod author did not give it.
  
  If the donor changes: Also makes the ported fit dependent on Dingtools' dts_aim-260, which USNA's original was not.

- **Flag, but do not change, other large stores parked as close to a fuel tank as the one confirmed clash — threshold 0.0181 separation AND >= 468 kg.**  
  *Comparison* — CLASH_SEPARATION/CLASH_MASS comment: 'Bar for flagging stores that sit close to a fuel tank: same separation or closer than the AGM-88G case, AND at least as heavy. Both halves matter - distance alone flags 20 per airframe, because Murder Hornet routinely parks SDBs (93 kg) beside the tanks and those are fine.' report_tank_clearance docs…
  
  Effect: No gameplay change; the pack declines to 'fix' upstream fits it has not seen in game.
  
  If the donor changes: Masses are read live out of mods-source ammunition files, so the report re-derives itself against whatever is subscribed.

- **Repair Murder Hornet's broken RAAF Growler squadron: NumberOfSquadrons=5→6 so Squadron6 becomes selectable, and Nation=US→Australia.**  
  *Engine precedent* — build_raaf_squadrons docstring: 'The EA-18G file declares NumberOfSquadrons=5 and defines Squadron6 - the RAAF one sits past the declared count and is unselectable, the same defect the F-22 mod had (declares 7, defines 1)' and 'That squadron flies Nation=US - an Australian-liveried Growler under a US flag.' Verified in 3430135740/aircraf…
  
  Effect: A RAAF-liveried Growler squadron the player could not select becomes selectable under the Australian flag.
  
  If the donor changes: Depends on Murder Hornet staying subscribed for raaf_f18g.png (the texture is not in this pack); replace_once() fails the build if the donor's count line or the livery/Nation pair changes.

- **Use the literal string Nation=Australia rather than Murder Hornet's Nation=AUS.**  
  *Engine precedent* — build_raaf_squadrons docstring: 'Nation becomes "Australia" - the string the RAAF F-35A mod and the RAN fleet already use.' Confirmed in integration/ran-fleet/SEST_RAN_Fleet/vessels/ran_ffh_anzac_variants.ini ('Nation=Australia', multiple). The deleted Murder Hornet [Squadron10] used 'Nation=AUS'.
  
  Effect: Australian units across the collection group under one nation string instead of two spellings.
  
  If the donor changes: Local to this pack's three squadron files.

- **1 SQN RAAF flies the F/A-18F Block III, and Murder Hornet's plain-F RAAF squadron is deleted outright; 6 SQN flies the Growler, both forward-based Townsville.**  
  *Player directive* — build_raaf_squadrons: '1 SQN RAAF flies the BLOCK III, not the plain F (user call: if the RAAF operates US Super Hornets, they operate the improved jet). The plain F's RAAF squadron - Murder Hornet's Squadron10, its last - is deleted outright so the un-upgraded F stops appearing under Australia.' Basing is also marked as the user's: '6 S…
  
  Effect: Australia fields Block III Super Hornets and Growlers only; the plain F disappears from the Australian roster.
  
  If the donor changes: Guarded: the build aborts if [Squadron10] is no longer the raaf_f18f.png entry, or if upstream adds its own RAAF squadron to the Block III file.

- **The new Block III RAAF squadron gets no livery lines — default Block III paint under the Australian flag.**  
  *Player directive* — Comment: 'No livery lines: raaf_f18f.png was painted for the plain F's texture set and the user called the fallback - default Block III paint under the Australian flag. The squadron identity comes from Nation plus the language name key.' Commit e215a68 'Block III RAAF squadron flies default paint'.
  
  Effect: 1 SQN Block III jets wear US Navy paint with an Australian flag rather than a mis-mapped RAAF texture.
  
  If the donor changes: No texture dependency at all for this squadron.

- **Ship one shared AIM-424 MALICE definition (integration/common/aim424.py) rather than a pack-local variant, with the flight model aligned key-for-key to Navy 2027's AIM-174B.**  
  *Comparison* — common/aim424.py: 'Aligned to usn_aim-174b as shipped by U.S. Navy 2027 Capabilities (3606774881) - the version that actually wins the load order in this collection, and the card the MALICE gets compared against in game', followed by an explicit ledger of intentional deltas ('MaxLaunchRange 290 vs 316 nm - it has to fit inside an F-35 we…
  
  Effect: MALICE is a peer of the AIM-174B, not a strictly better round, and behaves identically whichever SEST pack is loaded highest.
  
  If the donor changes: Changing it changes six packs at once; the F-35C, RAAF F-35A, F-15EX, Rafale and F-16CM packs write the same bytes.

- **Keep DragCoefficient explicit on the AIM-424 and do not scale its mesh.**  
  *In-game observation* — common/aim424.py: 'THIS KEY MUST STAY EXPLICIT: at -1 the engine back-solves 8.14 from the airframe and the missile loses roughly a third of its reach.' And: 'REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the missile stopped rendering as an AARGM-ER afterwards - the model block falls back to AssetBundleMesh=usn…
  
  Effect: MALICE keeps its stated reach and renders as an AARGM-ER instead of a Sea Sparrow.
  
  If the donor changes: The [Models] block is byte-identical to USNA's usn_agm-88g; if USNA is unsubscribed the missile falls back to the RIM-7 asset-bundle stand-in, 'same as the modded AARGM-ERs themselves do'.

- **Every transformation fails the build loudly rather than shipping a silent no-op: exact-count replacements, donor-token assertions, station-definition checks, and duplicate-key refusal.**  
  *File semantics* — replace_once(): 'expected one match, found {count}'; extend_loadouts(): 'loadout keys already exist: {clashes}'; inject_loadouts(): 'expected one WeaponMagazines marker'; verify_station_geometry(): 'loadout uses undefined stations {missing}'; verify_ammunition() pre-checks sest_aim-424, usn_aim-120d3, usn_aim-9x, usn_tank_610_f-18, usn_t…
  
  Effect: None directly — it is why a donor update cannot quietly produce a half-applied aircraft file.
  
  If the donor changes: Rebuild after every mod export is the intended workflow ('After any export, diff what changed and check it against pack donors').

- **Chinese loadout names are the English strings verbatim; no other language_cn keys are shipped.**  
  ***UNSTATED*** — LOADOUT_NAMES['cn'] duplicates LOADOUT_NAMES['en'] exactly (e.g. 'SEST_MaliceNGJ': 'SEST NGJ MALICE (2x AIM-424)' in both), and language_cn/ contains only loadout_names.ini — no ammunition_names.ini, so a Chinese-locale player sees no AIM-424 encyclopedia entry. No comment anywhere explains either choice.
  
  Effect: Chinese-locale players get English loadout names and an unnamed MALICE round.
  
  If the donor changes: Trivially fixable in LOADOUT_NAMES and common/aim424.py.

- **ReadyUpTime/CoolDownTime of 25/60 (Growler fits) and 30/60 (Block III fits) were chosen for the new loadouts.**  
  ***UNSTATED*** — The literals appear only in GROWLER_LOADOUTS / LONG_RANGE_LOADOUT / BLOCK_III_LOADOUT with the engine's own inline gloss ('// minutes to refuel and rearm before takeoff') and no rationale. 25/60 happens to match 3426791311/aircraft/usn_ea-18g_2020s.ini's single ReadyUpTime/CoolDownTime pair, and 30/60 exists among the Hornets' upstream v…
  
  Effect: SEST fits impose a specific turnaround/maintenance penalty relative to upstream fits that mostly declare none on these two donor files.
  
  If the donor changes: Pure constants in the builder.

- **README.md is out of date relative to the builder on three points and the builder is authoritative.**  
  *File semantics* — README still advertises a 'NGJ MALICE Heavy — 4x AIM-424 MALICE' loadout and 'adds both MALICE fits', but GROWLER_KEYS = ['SEST_MaliceNGJ'] only. README says NGJ Long Range 'is added only where a centreline station exists. usn_ea-18g has Station29; the 2020 and 2020s Growlers do not, and the build skips them' — superseded by the builder'…
  
  Effect: None in game; a reviewer following the README will look for a loadout that does not exist and mis-state why the Long Range fit is limited.
  
  If the donor changes: Documentation-only; the generated pack is correct.

**Must stay subscribed**

- 3606774881 — U.S. Navy 2027 Capabilities mod (Prof_CH4OS): donor for usn_ea-18g, usn_fa-18f_blk3, usn_fa-18f, usn_fa-18e, and the usn_aim-174b card the AIM-424 is balanced against. Must stay subscribed AND below this pack; docs/s…
- 3426791311 — [DEPRECATED] Boeing F/A-18E/F Super Hornet (MyGo): sole donor for usn_ea-18g_2020s, source of the NGJ pod meshes (assets/models/vechicle/aircraft/ea-18g/: ngllb, alq249_open) that the legacy Growler upgrade points at…
- 3737267013 — United States Naval Aviation (misaka): sole donor for usn_ea-18g_2020; ships usn_agm-88g whose mesh the AIM-424 renders with (fallback is the usn_rim-7 Sea Sparrow stand-in); sole source in mods-source of usn_aim-120…
- 3430135740 — F/A-18 Murder Hornet with AIM-174B (Cropgun): donor for all three squadron files, painter of raaf_f18g.png / raaf_f18f.png (textures are NOT shipped by this pack), author of the Interceptor geometry the Block III MAL…
- 3760871384 — Dingtools Weapon Pack: supplies dts_aim-260, used by every SEST fit on all six airframes (and injected into the ported Tanker fit).
- 3480965706 — B-2 Spirit / 3607989779 — F-35C Lightning II Alt. Loadouts: supply b-2_lrasm, which now replaces the Harpoon in the Super Hornets' anti-ship fits.
- 3606134711 — Custom Loadout Editor: named in port_tanker_fit as how usn_d-704 resolves for the buddy-tanker store (a vanilla copy also exists in mods-source/_vanilla/original/ammunition/).
- Load-order mandate: SEST Growler NGJ + MALICE above U.S. Navy 2027 Capabilities, F/A-18E/F and US Naval Aviation, inside the unbroken SEST_Integration block at the top (data/load-order.tokens.txt line 8); enforced by tools/check_…

**Known limits**

- EA-18G external fuel ceiling is TWO tanks: one pair of wing pylons (fule_tank_point, stations 27/28) and no station outboard of them (NumberOfStations=28); the centreline is the EW station and in game a third tank rendered inside…
- F/A-18E/F ceiling is THREE tanks (27/28 plus centreline); the requested five-tank fit 'has nowhere to hang the other two'.
- The Growler's outboard pylon is a single pair (stations 3/4), so a Growler carries two heavy weapons, not four or six. Murder Hornet's four- and six-AGM SEAD fits were re-cut to differ by fuel — an accepted payload nerf.
- ALQ-249 and NGL-LB are submodels with no Position key: they cannot be moved from the ini, so the mid-wing pylon is permanently unusable for stores.
- f-18_fuletank is a submesh of fa-18e.obj and carries the whole aircraft's origin, so it rides low under every pylon on every airframe; seat offsets of 0.0015 and 0.003 both produced no visible change in game. The only clean fix a…
- Upstream fits that park LRASM, AIM-174B, GBU-31 or JSOW as close to a tank as the confirmed AGM-88G clash are reported by report_tank_clearance but deliberately left alone: 'Those are upstream's and are not changed - they are fla…
- The RAAF liveries this pack claims (raaf_f18g.png) live in Murder Hornet, not in the pack; the Block III RAAF squadron deliberately ships no livery at all and flies default paint.
- Chinese localisation is nominal: language_cn/loadout_names.ini repeats the English strings and there is no language_cn/ammunition_names.ini, so the AIM-424 has no Chinese encyclopedia entry.
- _info.ini pins ApproximateVersion=0.8.2; the pack is a snapshot of donors exported into mods-source and must be rebuilt after every mod export ('Upstream moves under you').
- README.md and docs/setup-runbook.md still describe a 'NGJ MALICE Heavy (4x AIM-424)' loadout that the builder does not emit, and describe NGJ Long Range as gated on a Station29 centreline, which the builder explicitly superseded.

### `f-35c-jatm`

Three mods (deprecated MyGo F-35C, F-35C Alt. Loadouts, US Naval Aviation) all ship `aircraft/usn_f-35c.ini` and only the top one loads, so the Gerald R. Ford JSF air wing's 24 F-35Cs silently lose one mod's entire loadout set; this pack ships a fourth, higher-ranked copy that merges both surviving loadout sets (20 + 8 = 28) and adds three AIM-260 JATM / AIM-424 MALICE fits on top.


**Files (6)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `aircraft/usn_f-35c.ini` | merges | 3607989779 — F-35C Lightning II Alt. Lo… | Three subscribed mods ship this exact filename: 3508978375 [DEPRECATED] Lockheed Martin F-35C Lighting II (859 lines, 9 loadouts), 3607989779 Alt. Lo… |
| `ammunition/sest_aim-424.ini` | adds | New id under the `sest_` namespace. Fli… | Four subscribed mods ship `usn_aim-174b.ini` (3426791311, 3430135740, 3606774881, 3737267013). aim424.py picks 3606774881 explicitly: 'Aligned to usn… |
| `language_en/loadout_names.ini` | merges | 3607989779 — F-35C Lightning II Alt. Lo… | The base file is Alt. Loadouts', so its loadout-name file is the matching one. 43 lines out. |
| `language_cn/loadout_names.ini` | merges | 3737267013 — United States Naval Aviati… | Builder comment: 'Alt. Loadouts ships English only; fall back to US Naval Aviation for any other language so its names are not lost by the override.'… |
| `language_en/ammunition_names.ini` | adds | None — authored in integration/common/a… | Language files merge key-by-key, so a one-key file adds the encyclopedia entry without owning any other mod's names. aim424.py: 'All four SEST packs … |
| `_info.ini` | adds | None — pack metadata | Declares `ApproximateVersion=0.8.2` and the load-order instruction: 'Place ABOVE F-35C Alt. Loadouts, US Naval Aviation, the deprecated MyGo F-35C, a… |

**Decisions (26)** — File semantics 6, Upstream donor 6, UNSTATED 6, In-game observation 5, Comparison 1, Engine precedent 1, Author mandate 1


- **Rebase the whole-file override on F-35C Alt. Loadouts (20 loadouts) rather than US Naval Aviation (9), after establishing that neither file is a superset of the other.**  
  *Comparison* — Commit 9b93f7b 'Merge both F-35C loadout sets instead of overriding one with the other': 'The pack was built on US Naval Aviation's F-35C and sits above F-35C Alt. Loadouts, so its whole-file override silently removed the 19 loadouts only Alt. Loadouts defines (AirToAirJATM, SEADJATM, the AGM-158C/D heavy fits, the JSOW/GBU/QCSK families…
  
  Effect: The Ford's F-35C flights keep all 20 Alt. Loadouts fits (JATM, SEAD, AGM-158C/D heavy, JSOW/GBU/QCSK families) AND all 8 USNA basics (Ferry, AirToAir, Strike, StrikeLongRange, StrikePrecisi…
  
  If the donor changes: If Alt. Loadouts is unsubscribed, the pack still ships the file but ~14 of the base loadouts reference stores only that mod provides (usn_aim-260a, usn_aim-9xb2+, usn_aim-120d-3, usn_gbu-53…

- **Harvest USNA's 8 unique loadout sections into the Alt. Loadouts base instead of accepting the loss, because a unit ini is a whole-file override.**  
  *File semantics* — build_patch.py step 2: '# Carry over the loadouts only US Naval Aviation defines. The two F-35C files share just one loadout key, so neither is a superset: Alt. Loadouts brings the JATM/SEAD/JSOW/QCSK families, USNA brings the basics (AirToAir, AntiShip, Ferry, CAS, Strike...). Whole-file override means whichever we ship is ALL the playe…
  
  Effect: Adds Ferry / AirToAir / Strike / StrikeLongRange / StrikePrecision / AntiShip / AntiShipHeavy / CAS to the picker.
  
  If the donor changes: The carried sections reference USNA stores (usn_jsm, usn_jsm_land, usn_gbu-31v1, usn_aim-120d3, usn_f-35_gun_pod); unsubscribing USNA breaks those eight fits.

- **When harvesting USNA's AntiShip loadout, take only the FIRST [WeaponSystem1AntiShip] section — USNA ships an exact duplicate of it.**  
  *Upstream donor* — build_patch.py: '# USNA ships an exact duplicate [WeaponSystem1AntiShip] (the second copy lacks ReadyUpTime) - take the FIRST, more complete section only, or the merge would define the loadout twice.' Verified against the donor: a duplicate-heading scan of mods-source/3737267013/aircraft/usn_f-35c.ini returns exactly ['[WeaponSystem1Anti…
  
  Effect: AntiShip carries the ReadyUpTime/CoolDownTime the fuller copy has, and the merged file has no duplicate section for the engine to resolve arbitrarily.
  
  If the donor changes: If USNA fixes its own duplicate, the harvest still works (the regex simply finds one section). No breakage either way.

- **Validate every carried USNA section against THIS airframe's hardpoint table before writing, and abort if a position key is missing.**  
  *File semantics* — build_patch.py: '# Validate the carried sections against THIS airframe's hardpoints: every position key they use must exist in the Alt. Loadouts file.' followed by `sys.exit(f"carried loadouts need position keys this airframe lacks: {unknown}")`. Backed by docs/design-notes.md: 'Each [WeaponSystemN] has its own station table. The same st…
  
  Effect: Carried fits seat their stores where the base file's geometry says, not where USNA's did. Independently checked here: the two donors' [WeaponSystem1] tables are identical (12/12 stations, s…
  
  If the donor changes: If a future USNA update adds a loadout using a position key Alt. Loadouts lacks, the build fails loudly rather than shipping a floating store.

- **Source the AIM-260 from the Dingtools Weapon Pack (`dts_aim-260` for bay stations, `dts_aim-260_w` for wing stations) rather than from Alt. Loadouts' own `usn_aim-260a`.**  
  *Upstream donor* — README: 'The AIM-260 comes from the **Dingtools Weapon Pack** (`dts_aim-260` internal, `dts_aim-260_w` external, matching dingtools' own internal/external carriage convention on the F-15EX).' Verified: `mods-source/3760871384/ammunition/dts_aim-260_w.ini` is a two-key alias file — `#!alias ammunition/dts_aim-260.ini` plus `DropDuration=0…
  
  Effect: Externally-carried AIM-260s rail-launch immediately; bay-carried ones eject first. Note the base file's own AirToAirJATM fit still fires `usn_aim-260a`, so two AIM-260 definitions coexist i…
  
  If the donor changes: If Dingtools Weapon Pack is unsubscribed all three SEST loadouts lose their stores (dts_aim-260 is also shipped by 3636386513 F-15 EX Eagle II, which sits at line 78, below SEST_Integration…

- **Clone the Intercept260 SubmodelsToHide list verbatim from a fit the donor's own author already proved, rather than composing one.**  
  *Upstream donor* — Intercept260 ships `SubmodelsToHide=wing_pyl_inner,wing_pyl_outer,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right` — character-for-character the list on Alt. Loadouts' own `[WeaponSystem1AirToAirAMRAAM]` (mods-source/3607989779/aircraft/usn_f-35c.ini line 341), which is likewise a 6-internal-AAM + 2-wingtip-AIM-9X fit. Malice4…
  
  Effect: Pylons and BRU-61 racks disappear on the clean fits, so the stealth loadouts render as a clean-winged aircraft.
  
  If the donor changes: Submodel names come from the airframe mesh; an airframe-mod update that renames a submodel would leave visible empty pylons. Not guarded by the builder.

- **Keep `pyl_l`/`pyl_r` VISIBLE on Intercept260Beast even though every other beast-style fit hides them.**  
  *Upstream donor* — Inline comment: '# pyl_l/pyl_r are the WINGTIP launch rails and [WeaponSystem2Intercept260Beast] puts AIM-9X on the wingtip stations, so they must stay visible or the missiles float unattached.' Donor corroboration: Alt. Loadouts labels `Station1=-0.074247,... //Wing tip Left` / `Station2=... //Wing tip Right` in [WeaponSystem2], and its…
  
  Effect: Wingtip AIM-9X sit on their rails instead of floating in mid-air on the 10-missile beast fit.
  
  If the donor changes: Independent of donor state; the fix lives in this pack's own generated section.

- **Give the external AIM-260s their own position keys, split per pylon pair — `AAM260IPositions=0,0.0025,0.0035` (inner, WS2 stations 3/4) and `AAM260OPositions=0,0.0025,0.002` (outer, 5/6) — …**  
  *In-game observation* — Four tuning commits, each recording what was seen: ee7d97c 'Both F-35 patches now inject an AAM260Positions offset key (up 0.005, forward 0.008 model units, ~7cm per 0.001)... correcting the low/aft hang the user screenshotted on the RAAF F-35A beast fit'; a3d140d 'First guess overshot - missiles clipped into the pylons. Halved the verti…
  
  Effect: The four wing-pylon AIM-260s on the beast fit hang flush on their pylons instead of low and aft or clipped into them.
  
  If the donor changes: The keys are injected into the base file's [WeaponSystem2] by regex; if Alt. Loadouts restructures that section the builder exits with 'could not inject AAM260 position keys into [WeaponSys…

- **Mount the two AIM-424 MALICE on internal bay stations 7/8 and the two AIM-260 on stations 3/4 for the Malice424 fit.**  
  *Upstream donor* — Builder comment: '# Full-stealth counter-air/SEAD fit: two AIM-424 MALICE on the big bay stations (7/8, where JSM/JDAM go) plus two AIM-260 on the bay door rails.' Verified: the base file annotates `Station7=-0.013479,-0.009066,0.032776 //Bomb` / `Station8=... //Bomb`, and the carried USNA fits use exactly those two — `Strike` puts `usn_…
  
  Effect: A fully internal 2×MALICE + 2×AIM-260 fit — no external stores, signature stays clean, 290 nm reach from inside the bay.
  
  If the donor changes: Station geometry is inherited from the base file; a donor change to the bay table would move the stores.

- **Build the AIM-424 MALICE as a new `sest_` id rather than editing any existing missile, and ship byte-identical copies from every pack that uses it.**  
  *File semantics* — integration/common/aim424.py: 'All four SEST packs that carry MALICE fits write identical copies of ammunition/sest_aim-424.ini and a partial language_en/ammunition_names.ini - identical same-path files are a safe overlap whichever pack sits higher in the Mod Manager.' Enforced by tools/consolidate_packs.py ('identical bytes -> keep one …
  
  Effect: A new encyclopedia entry appears; no existing missile's stats are changed for any other mod's aircraft.
  
  If the donor changes: Self-contained — the ini is authored here, so nothing upstream can remove it.

- **Align the MALICE flight model key-for-key with `usn_aim-174b`, keeping only deliberate deltas, after the missile lost a side-by-side comparison in the encyclopedia.**  
  *In-game observation* — Commit 9b6b2fa: 'Side by side in the encyclopedia the MALICE lost on every line that matters: 185 nm against 316, 179.6 nm on the flight-path chart against 258, a smaller warhead, a smaller blast radius, and worse hit chances across all six target classes.' Preceded by f147057, which recorded the earlier failure: 'Reported in game as wea…
  
  Effect: MALICE is a genuine 290 nm shot with a 40 nm active / 80 nm passive seeker and full anti-emitter mode, but turns at 28 deg/s vs the AIM-260's 40 — it out-reaches everything carryable intern…
  
  If the donor changes: The comparison basis is 3606774881's copy of usn_aim-174b; if that mod updates its 174B or drops below another 174B provider in the order, the two cards no longer sit on the same assumption…

- **Keep `DragCoefficient=3.6` explicit rather than the engine default of -1.**  
  *In-game observation* — aim424.py: 'THIS KEY MUST STAY EXPLICIT: at -1 the engine back-solves 8.14 from the airframe and the missile loses roughly a third of its reach.' Commit 9b6b2fa: 'The root cause was DragCoefficient=-1. That is not "default drag" - it tells the engine to back-solve the coefficient from the airframe, and on the AARGM-ER body it solved 8.14…
  
  Effect: The MALICE actually achieves its advertised 290 nm instead of ~185 nm.
  
  If the donor changes: Self-contained. Note the motor was simultaneously retuned from ~287 to ~170 G.s 'because with honest drag the old impulse would have overshot the 174B outright'.

- **Keep the [Models] block byte-identical to USNA's `usn_agm-88g` and never add keys to it — specifically, no `ResourcesMeshScale`.**  
  *In-game observation* — aim424.py: '# REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the missile stopped rendering as an AARGM-ER afterwards - the model block falls back to AssetBundleMesh=usn_rim-7, a short fat Sea Sparrow, which is exactly what showed up under the wing. The [Models] block below is now byte-identical to US Naval Aviat…
  
  Effect: The MALICE renders as an AARGM-ER at AGM-88G size rather than as a Sea Sparrow.
  
  If the donor changes: Hard-bound to 3737267013: without US Naval Aviation the `ResourcesFolder=assets/models/ammunition/agm-88/` path does not resolve and the missile falls back to the `usn_rim-7` asset-bundle s…

- **Accept that the MALICE cannot be visually resized, and record the finding in the collider comment so the search is not repeated.**  
  *Engine precedent* — aim424.py [col_main]: '# This Scale is the HIT COLLIDER box, not the visual - every ammunition ini in the collection carries it under [col_main] and none has a model-size key. The visual renders at the shared usn_rim-7 mesh's native size, same as usn_agm-88g, and cannot be resized from the ini.' Commit 705057b: 'The AIM-424's apparent AG…
  
  Effect: The MALICE looks like an AGM-88G — larger than an AIM-260 — with no way to shrink it.
  
  If the donor changes: Ceiling of the engine/mesh, not a donor dependency.

- **Take Mass=467 straight from the airframe donor.**  
  *Upstream donor* — `Mass=467` in sest_aim-424.ini matches `Mass=467` in mods-source/3737267013/ammunition/usn_agm-88g.ini exactly — the AGM-88G whose airframe and mesh the MALICE rides.
  
  Effect: Bay-carriage weight and aircraft loadout mass match the real donor airframe.
  
  If the donor changes: Static value; a USNA change to its AGM-88G would not propagate (the value is literal in aim424.py).

- **Set AmmoPoints=2600 for the MALICE.**  
  ***UNSTATED*** — No comment, commit message or design note explains the figure. It sits between the two rounds the file is otherwise derived from (usn_aim-174b 2500 in 3606774881, usn_agm-88g 2850 in 3737267013), which is suggestive but nowhere recorded. FLAG.
  
  Effect: Sets the missile's supply-system 'price' — how much of a magazine/resupply budget each MALICE consumes.
  
  If the donor changes: n/a — literal in this pack.

- **Keep the three loadout display strings byte-identical to the RAAF F-35A pack's, and comma-free.**  
  *File semantics* — build_patch.py LOADOUT_NAMES comment: '# NOTE: [LoadoutNames] keys are global across mods; the RAAF pack defines Intercept260/Intercept260Beast/Malice424 too, so the strings here are kept identical to that pack's (whichever pack wins load order, both aircraft read correctly). Keep display strings comma-free.' Verified: integration/raaf-f…
  
  Effect: Both the F-35C and the RAAF F-35A show the same names for the shared loadout keys, whichever pack sits higher.
  
  If the donor changes: If either pack's strings drift, `consolidate_packs.py` fails the build rather than shipping a silent mismatch.

- **Validate every Station reference in the new and carried sections against ALL of mods-source rather than against a named donor list.**  
  *File semantics* — build_patch.py step 4: '# all of mods-source (incl. _vanilla): most stores have several providers, and a narrow donor list would hard-bind the build to one of them'. Concretely true here — `usn_aim-9x` is shipped by seven subscribed mods (3426791311, 3430135740, 3508978375, 3514484654, 3606774881, 3737267013, 3758320372).
  
  Effect: No empty pylons from a typo'd or vanished store id; the build refuses to write 'unresolved ammunition ids'.
  
  If the donor changes: The check is deliberately loose: it proves *some* mod provides each store, not that the winning copy is the intended one.

- **Ship a language_cn file at all, based on USNA's, so Chinese names survive.**  
  *File semantics* — build_patch.py: '# Alt. Loadouts ships English only; fall back to US Naval Aviation for any other language so its names are not lost by the override.' Caveat worth flagging for the reviewer: docs/design-notes.md establishes that '`systems/` and `language_*/` merge key-by-key', so USNA's own language_cn would NOT have been lost by this pa…
  
  Effect: Chinese players see translated names for the 8 carried USNA fits and the 3 SEST fits.
  
  If the donor changes: If USNA is unsubscribed the copied base text still ships from this pack.

- **Declare ApproximateVersion=0.8.2.**  
  *In-game observation* — Commit 673e50b: 'Every SEST pack declared ApproximateVersion=0.6.8 against a 0.8.x game. That check requires MAJOR and MINOR to match, so all seven packs were failing it. Now 0.8.2, matching the rebase sources.'
  
  Effect: The pack stops being flagged as version-incompatible by the Mod Manager.
  
  If the donor changes: Needs a bump on each game minor-version release; not automated.

- **Place the pack above every mod it touches, as part of the repo-wide Tier 0 block.**  
  *Author mandate* — _info.ini and README both state: 'Place ABOVE F-35C Alt. Loadouts, US Naval Aviation, the deprecated MyGo F-35C, and Modern US Navy.' Also honours the Dingtools author's own mandate recorded in data/mod-catalog.json — load_order: "Author: 'Put this mod ABOVE any of my mod'". Verified in data/load-order.tokens.txt: SEST_Integration line 8…
  
  Effect: The merged 31-loadout F-35C is the copy the game actually loads.
  
  If the donor changes: If any of those mods is dragged above SEST_Integration, this pack becomes silently inert — no error is shown.

- **US Naval Aviation now ships its own `ammunition/usn_aim-424.ini` ('AIM-424 LRAAM', 195 nm, Mass=680, its own `aim-424.obj` mesh and `assets/models/ammunition/aim-424/aim-424_mat.ini`) — the…**  
  ***UNSTATED*** — `mods-source/3737267013/ammunition/usn_aim-424.ini` exists in the current export (asset dir timestamped 2026-08-23 22:03). Grepping build_patch.py, integration/common/aim424.py, the README, docs/design-notes.md and docs/mod-catalog.md for `usn_aim-424` returns nothing. This is exactly the case docs/design-notes.md warns about — 'Upstream…
  
  Effect: Two different AIM-424s appear in the encyclopedia with the same real-world designation and very different stats (290 nm vs 195 nm). No id collision, so nothing breaks, but the pack's 'what-…
  
  If the donor changes: n/a — a divergence to be resolved, not a dependency.

- **README documentation is stale against the builder it describes.**  
  ***UNSTATED*** — integration/f-35c-jatm/README.md still carries a section headed 'Why the base is US Naval Aviation's F-35C' ('This patch is a fourth override based on USNA's file') and a rebuild note 'Regenerates from `mods-source/3737267013`' — both superseded by commit 9b93f7b, which made 3607989779 the base. Its loadout table also lists pre-705057b i…
  
  Effect: None in game — but a reviewer reading only the README would attribute the override to the wrong donor.
  
  If the donor changes: n/a

- **Two dead constants remain in the builder from the pre-merge design.**  
  ***UNSTATED*** — `VANILLA = ROOT / "mods-source" / "_vanilla" / "original"` (build_patch.py line 22) and the 7-line `DUP_ANTISHIP` block (line 116) are never referenced anywhere in the file — `grep -n DUP_ANTISHIP -r integration/` matches only its own definition. DUP_ANTISHIP encoded the old 'strip USNA's duplicate AntiShip section' approach that the har…
  
  Effect: None — they do not reach the output.
  
  If the donor changes: n/a

- **ReadyUpTime values of 15 / 25 / 20 minutes for Intercept260 / Intercept260Beast / Malice424.**  
  ***UNSTATED*** — No comment or commit explains the numbers. They do coincide with USNA's own pattern for comparable fits (AirToAir ReadyUpTime=15, StrikePrecision=25, Strike=20), which is consistent with the project's 'Derive, don't invent' rule, but that derivation is nowhere recorded. FLAG.
  
  Effect: How long an F-35C flight spends rearming before it can launch on each fit.
  
  If the donor changes: n/a — literal in this pack.

- **The pack's airframe mesh dependency is inherited and undocumented.**  
  ***UNSTATED*** — The generated aircraft/usn_f-35c.ini keeps the donor's `ResourcesFolder=assets/models/vechicle/aircraft/f-35/` + `ResourcesRoot=f-35c.obj` (lines 746-747). In the current export only 3508978375 ([DEPRECATED] Lockheed Martin F-35C Lighting II) and 3413868677 (Red Storm Arsenal, deliberately placed last at line 139) provide that path — nei…
  
  Effect: None today, but unsubscribing the deprecated MyGo F-35C — which the catalog lists as an 'Unsubscribe candidate' — could leave the Ford's F-35Cs without a model.
  
  If the donor changes: The dependency comes from the donors, not from this pack; it survives any rebuild and is not covered by any builder guard.

**Must stay subscribed**

- 3607989779 — F-35C Lightning II Alt. Loadouts (Prof_CH4OS): the base file's donor. Must stay subscribed for the ~14 base loadouts that fire its own ammunition (usn_aim-260a, usn_aim-9xb2+, usn_aim-120d-3, usn_gbu-53, usn_gbu-31v4…
- 3737267013 — United States Naval Aviation (misaka): supplies the AGM-88G mesh path (assets/models/ammunition/agm-88/usn_agm-88g_mat.ini) the AIM-424 MALICE renders through — without it the missile falls back to the usn_rim-7 Sea …
- 3760871384 — Dingtools Weapon Pack (dingtools): supplies dts_aim-260 and dts_aim-260_w. Without it (or 3636386513 F-15 EX Eagle II, which ships identical copies) all three SEST loadouts have no stores. Author mandate recorded in …
- 3606774881 — U.S. Navy 2027 Capabilities mod (Prof_CH4OS): not a runtime dependency, but the AIM-424's flight model is aligned key-for-key to ITS copy of usn_aim-174b, chosen because it wins the load order (line 17, above the oth…
- 3461044389 — Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies): the consumer. Its vessels/usn_cvn_ford_jsf.ini carries `usn_f-35c=Squadron1,24`, which is why this airframe was patched at all.
- 3508978375 — [DEPRECATED] Lockheed Martin F-35C Lighting II: undocumented mesh dependency inherited from both donors — the only mod in the current export providing assets/models/vechicle/aircraft/f-35/f-35c.obj. Catalog lists it …

**Known limits**

- The AIM-424 MALICE cannot be visually resized: 'The visual renders at the shared usn_rim-7 mesh's native size, same as usn_agm-88g, and cannot be resized from the ini (ResourcesMeshScale, the one candidate key, breaks the model)'…
- MaxLaunchRange is capped at 290 nm rather than the AIM-174B's 316 — a deliberate ceiling, 'it has to fit inside an F-35 weapons bay'.
- MaxTurnRate 28 deg/s vs the AIM-260's 40 — the MALICE 'out-reaches everything you can carry internally but loses the endgame knife fight' (commit f147057). Accepted so the JATM stays worth carrying.
- language_cn covers only the 8 carried USNA loadout keys plus the 3 SEST keys; the 20 Alt. Loadouts keys have no Chinese names because that mod is English-only. Non-en/cn languages get no loadout_names.ini at all (the builder `con…
- language_en/ammunition_names.ini is English-only — Chinese players see the raw `sest_aim-424` id in the encyclopedia.
- The builder's carry-over guard validates position KEYS only ('every position key they use must exist in the Alt. Loadouts file'), not station numbers or coordinates. It happens to be safe here — the two donors' [WeaponSystem1] ta…
- Two AIM-260 definitions coexist on this airframe: the base file's own AirToAirJATM/SEADJATM fits fire Alt. Loadouts' `usn_aim-260a` while the three SEST fits fire dingtools' `dts_aim-260`. Not reconciled.
- The pack overrides `aircraft/usn_f-35c.ini` wholesale, so any future upstream edit by Alt. Loadouts or USNA to that file is invisible until someone re-runs build_patch.py — docs/design-notes.md: 'Upstream moves under you. A shado…

### `adf-persistent-isr`

Adds the RAAF's MQ-4C Triton as a brand-new, purely additive unit id (`raaf_mq-4c_triton`) by cloning the MQ-9 Reaper mod's long-wing MQ-9 ER airframe and re-skinning it as an unarmed HALE maritime ISR jet — deliberately avoiding any whole-file override so the donor mod, and every other mod, keeps its own units intact while the Triton borrows the donor's mesh, materials, gear animation and MTS-B sensor cross-mod.


**Files (6)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `integration/adf-persistent-isr/SEST_ADF_Persistent_…` | adds | 3503670861 — General Atomics MQ-9 Reape… | build_pack.py docstring: "cloned from the MQ-9 Reaper mod's MQ-9 ER airframe (the collection's only long-wing UAV mesh)". Verified against data/mod-c… |
| `integration/adf-persistent-isr/SEST_ADF_Persistent_…` | adds | 3503670861 — General Atomics MQ-9 Reape… | Structural keys are copied verbatim from the donor's squadrons file (`SerialnumberReferences=Modex,Right_Outer_Wing_Modex,Left_Rudder_Modex,Right_Rud… |
| `integration/adf-persistent-isr/SEST_ADF_Persistent_…` | adds | Pattern donor: 3602046770 — Boeing P-8 … | Builder comment: "Pattern follows the P-8A's AN/APY-10 with a full-circle scan and inverse-SAR classification modes folded into gain." Two mods ship … |
| `integration/adf-persistent-isr/SEST_ADF_Persistent_…` | adds | none (original text) | language_*/ files merge key-by-key across mods (docs/design-notes.md: "`systems/` and `language_*/` merge key-by-key… Language merging is how packs r… |
| `integration/dist/SEST_Integration/systems/sensors.i…` | merges | n/a — produced by tools/consolidate_pac… | The consolidator section-merges the pack's [AN/ZPY-3] with SEST_Growler_NGJ_MALICE's [AN/ALQ-249] under a "# ---- from SEST_ADF_Persistent_ISR ----" … |
| `integration/adf-persistent-isr/SEST_ADF_Persistent_…` | adds | none | Mod Manager metadata; `ApproximateVersion=0.6.8`. The consolidator takes max() of component versions, so the dist pack carries 0.8.2 from SEST_RAAF_B… |

**Decisions (25)** — UNSTATED 7, File semantics 6, Real-world spec 6, Upstream donor 4, Engine precedent 2


- **Ship the Triton as a NEW unit id and file name rather than overriding or editing any MQ-9 file, so the donor mod stays untouched and both fleets coexist.**  
  *File semantics* — build_pack.py docstring: "It is a NEW unit id: the MQ-9 mod is untouched and must stay installed — meshes, materials, the gear animation file and the MTS-B sensor definition resolve from it cross-mod. Everything else resolves from vanilla; the pack ships its own AN/ZPY-3 sensor definition." Confirmed: `find mods-source -iname '*mq-4*' -o…
  
  Effect: Australia gains an MQ-4C in the mission editor alongside the unmodified USAF MQ-9A/MQ-9 ER; nothing the MQ-9 mod ships is lost or shadowed.
  
  If the donor changes: Unsubscribing 3503670861 leaves a unit definition pointing at meshes, materials, the gear animation file and AN/AAS-52_Visual that no longer exist; a Triton would spawn broken. Nothing else…

- **Rebase on aircraft/usaf_mq-9_er.ini (the long-wing ER) rather than the MQ-9A or any other airframe in the collection.**  
  *Engine precedent* — Docstring: "(the collection's only long-wing UAV mesh)". Cross-checked against data/mod-catalog.json: the only UAV-type mods are 3503670861 MQ-9 Reaper, 3601891050 Small and Medium-Sized UAV Series (WIP, Orlan/RQ-7 class) and two Shahed-136 mods; no Global Hawk/RQ-4 exists in the 132-mod catalog.
  
  Effect: The Triton renders as a 20 m-span MQ-9 ER — recognisably a HALE-ish UAV, but visibly smaller than the real 39.9 m aircraft.
  
  If the donor changes: If a real RQ-4/MQ-4C mesh mod is ever added, the whole pack should be rebased onto it; the current pack is inseparable from the MQ-9 mesh.

- **Reuse two donor slices verbatim (the [Main Systems] flight-control surface table, and the entire [Mesh definitions]→EOF tail: submodels, materials, effects, sounds, colliders) and hand-auth…**  
  *Upstream donor* — build_pack.py main(): "# Donor slices reused verbatim: control surfaces + the whole mesh/effects/sounds/colliders tail. Identity, flight model, sensors and weapons are ours." Implemented by extract() which `sys.exit(f"donor layout changed: {start_marker!r} not found in {DONOR}")` if either marker moves. Matches the repo rule in docs/desi…
  
  Effect: Aileron/elevator/rudder animation, damage model, LODs and colliders behave exactly as the author's proven MQ-9 ER does.
  
  If the donor changes: A donor-mod update that renames the `[---------- Main Systems ----------]`, `[---------- Sensor Systems ----------]` or `[---------- Mesh definitions----------]` banners makes the build exi…

- **Convert the turboprop donor into a jet by deleting the prop declarations instead of deleting the prop meshes: strip `PropsIdle=`/`PropsInFlight=` and the `General_2=Prop` / `General_3=prop_…**  
  *File semantics* — Builder comment: "# --- Triton: a jet — drop the prop declarations (undeclared submodels are never instantiated), strip the prop-idle keys and swap in vanilla jet audio". Verified in the output: SEST_ADF_Persistent_ISR/aircraft/raaf_mq-4c_triton.ini [Submodels] lists only `General_1=Glass` and `General_4=blk30` while `Mesh=Prop_blk30` / …
  
  Effect: No spinning pusher prop or prop disc renders on the Triton; it flies as a clean jet.
  
  If the donor changes: Purely internal to the generated file; a donor rename of the Prop submodels trips the guard.

- **Swap the donor's turboprop audio for vanilla jet audio: EngineAudioClip TurboPropP3-COrion → audio/aircraft/TF30, Exhaust turboprop_far → jet_rear_1, Far turboprop_far → jet_far_1.**  
  ***UNSTATED*** — No recorded justification for these three specific vanilla clips — the only comment is "swap in vanilla jet audio" (build_pack.py). The choice of TF30 (an F-14/F-111 afterburning turbofan sample) for a 39.7 kN AE 3007H high-bypass turbofan has no note. The clips are vanilla, so nothing hard-depends on them.
  
  Effect: The Triton sounds like a jet rather than a P-3-style turboprop.
  
  If the donor changes: None — vanilla audio paths, unaffected by mod subscriptions.

- **Re-engine the unit as a single 39.7 kN turbofan: EngineIntakeArea 13.3 (donor's prop-diameter value) → 1.6, donor's `PerEngineMaxPower=671000` (turboprop marker) replaced by `PerEngineMaxTh…**  
  *Real-world spec* — Emitted with inline comment `PerEngineMaxThrust=39700 //Newtons - RR AE 3007H turbofan` (the MQ-4C's actual engine, ~8,900 lbf). Donor values for comparison are in mods-source/3503670861/aircraft/usaf_mq-9_er.ini:37 (`EngineIntakeArea=13.3 // Propellor diameter value used`) and :71.
  
  Effect: Jet acceleration and altitude behaviour instead of a turboprop's; the engine type key change is what makes the game treat it as a jet.
  
  If the donor changes: Self-contained in the pack's own file.

- **Give it real MQ-4C performance rather than donor MQ-9 numbers: Ceiling 56,500 ft (donor 50,000), CruiseAltitude 53,000 ft (donor 25,000), EmptyMass 6,781 kg (donor 2,223), MaxFuel 7,390 kg …**  
  *Real-world spec* — Inline comment on the cruise line: `SpeedAndRange_Cruise=310,9430 // 8,200 nmi ferry range / 24+ hours on station`. Altitude band list is also widened to `Altitudes=200,1000,5000,15000,30000,45000,56000` vs the donor's 45,000 ft top.
  
  Effect: The Triton orbits far above SAM and fighter reach for most scenarios and can stay up for the whole mission — the 'persistent' half of the pack name.
  
  If the donor changes: Self-contained.

- **Declare the real 39.9 m wingspan even though the rendered mesh is 20 m, and document the mismatch instead of faking the span.**  
  *Real-world spec* — `WingSpan=39.9 //meters (mesh is the 20 m MQ-9 - accepted stand-in)`; README first-flight check: "visually undersized (20 m mesh vs 39.9 m real span)"; the in-game description ends "(Flies the collection's MQ-9 ER mesh as an accepted stand-in.)"
  
  Effect: Parking/handling footprint and any span-derived calculation use the true figure; the visual model stays small.
  
  If the donor changes: Self-contained; the honesty note is in the unit description players read.

- **Detune the airframe's agility below the donor: PitchGain 0.8→0.6, VelocityGain 0.1036→0.06, HeadingGain 2→1.5, YawRateLimit 130→30, MaxRollForHeading 35→25, MaxRollRate 80→25, MaxG 5→2.5, M…**  
  ***UNSTATED*** — No comment on any of these keys in build_pack.py's TRITON_HEAD; donor values are at mods-source/3503670861/aircraft/usaf_mq-9_er.ini:41-58. Physically consistent with a heavier long-span HALE airframe, but nothing records that reasoning or any in-game check of it.
  
  Effect: Wide, slow turns — the Triton cannot manoeuvre out of trouble; it also affects whether the AI holds a clean orbit.
  
  If the donor changes: Self-contained.

- **Carry no weapons at all: one Hardpoint weapon system with `NumberOfStations=0`, and a SubModelsToHide list covering every one of the donor's 14 weapon-furniture submodels (pylons, rails, LA…**  
  *Upstream donor* — HIDE_WEAPON_FURNITURE with comment "# Every MQ-9 weapon-furniture submodel — both units fly clean", validated at build time: `for sub in HIDE_WEAPON_FURNITURE.split(","): if not re.search(rf"^Weapon_\d+={re.escape(sub)}\s*$", donor, re.M): problems.append(f"donor no longer declares weapon submodel {sub!r}")`. The weapons block itself car…
  
  Effect: No stores can be loaded and no empty pylons/rails render — the aircraft is a pure sensor platform whose only offensive contribution is the datalinked track picture.
  
  If the donor changes: If the donor mod renames or removes any weapon submodel, the build fails loudly rather than shipping an aircraft with visible orphan pylons.

- **ReadyUpTime=20 min / CoolDownTime=45 min for the single default loadout.**  
  ***UNSTATED*** — Emitted with only unit comments (`// in minutes`). The donor's [WeaponSystem1Default] carries no ReadyUp/CoolDown values at all (mods-source/3503670861/aircraft/usaf_mq-9_er.ini:220), and vanilla civ_707 uses 0/30 — neither is cited as the source of 20/45.
  
  Effect: Sets turnaround: 20 min to launch, 45 min unavailable after landing, so a base with 2-3 airframes can only just sustain a continuous orbit.
  
  If the donor changes: Self-contained.

- **Ship the pack's own [AN/ZPY-3] radar definition rather than reusing an existing sensor name, patterned on the P-8's AN/APY-10 block.**  
  *Engine precedent* — SYSTEMS_INI comment: "Multi-Function Active Sensor: the MQ-4C's belly-mounted 360-degree AESA maritime surveillance radar. Pattern follows the P-8A's AN/APY-10 with a full-circle scan and inverse-SAR classification modes folded into gain." Key-for-key the block mirrors 3602046770 Boeing P-8 Poseidon's [AN/APY-10] (same order Kind/Type/Ha…
  
  Effect: The Triton carries a distinct radar the collection did not have; nothing else's sensors change.
  
  If the donor changes: The radar definition travels with the pack — no upstream mod needs to stay installed for it. Removing the pack removes both unit and sensor cleanly.

- **Give the ZPY-3 full-circle, look-down-only coverage: `ViewArcs=-180,180|-85,3`, Role=Surface, CanDetectLandTargets/CanDetectPeriscope=True, HasDataLink=True, zero target/weapon channels.**  
  *Real-world spec* — Inline comments: `ViewArcs=-180,180|-85,3 // belly array: everything below the horizon, all bearings` and `HasDataLink=True // BAMS exists to feed the surface picture to the force`. The pattern donor's P-8 array is forward-biased (`ViewArcs=-120,120|-60,15`), so the 360° arc is a deliberate MFAS-specific change, not a copy.
  
  Effect: One orbiting Triton builds a task-force-wide surface and periscope picture on all bearings; with TargetChannels=0/WeaponChannels=0 it can never guide a weapon — it is a finder only. It is a…
  
  If the donor changes: Self-contained.

- **Set the ZPY-3's actual numbers below the APY-10 template: MaxRange 430 km (P-8 mod: 470), Gain 60 dB (61), PeakPower 900 kW (1300), RangeResolution 90 m (110), plus IdentificationTime=25 wh…**  
  ***UNSTATED*** — No comment or table records how 430/60/900/90/25 were derived; the block comment claims "inverse-SAR classification modes folded into gain" yet the emitted Gain (60) is lower than the P-8 template's (61). `IdentificationTime=25` appears exactly once in the whole vanilla sensors.ini (line 121, on an unrelated system, commented "How much t…
  
  Effect: Detection reach ~430 km against surface contacts and a 25 s ESM identification delay for anyone classifying the emitter; both are balance-relevant numbers a reviewer cannot trace to a sourc…
  
  If the donor changes: Self-contained.

- **Take the EO/IR turret from the donor mod cross-mod (`SystemName=AN/AAS-52_Visual`) instead of vanilla's AdvancedOptics, and validate at build time that the donor still defines it.**  
  *Upstream donor* — Sensor block comment "#MTS-B EO/IR turret (resolves from the MQ-9 mod)"; MQ9_SYSTEMS = ["AN/AAS-52_Visual"] checked by check_systems() against mods-source/3503670861/systems/sensors.ini, which defines it at line 35 (VIDRangeMultiplier=12.5 / MaxRangeMultiplier=7.5 / NightVisionLevel=1). Note: build_pack.py's VANILLA_SYSTEMS list still va…
  
  Effect: The Triton gets the MQ-9's proven long-range EO/IR VID performance instead of a generic optics fit.
  
  If the donor changes: Unsubscribing 3503670861 removes the turret definition as well as the mesh — a second reason the donor must stay installed.

- **Give the turret arcs `ViewArcs=-180,180|-90,20` (full-circle, straight down to 20° up).**  
  ***UNSTATED*** — No comment on the arc values. They are not the donor's (its cockpit visual is `ViewArcs=-150,150|-25,91`, mods-source/3503670861/aircraft/usaf_mq-9_er.ini:142). Vanilla's nearest idiom is `ViewArcs=-180,180|-90,1`, used by usn_a-6e, usn_ra-5c and wp_mig-25rb — close but not identical, and not cited.
  
  Effect: The ball can look at anything below the aircraft on any bearing plus a little above the horizon.

- **Take ELINT and RWR from vanilla (AircraftELINT, AircraftRWR) and verify both exist before emitting.**  
  *Upstream donor* — VANILLA_SYSTEMS = ["AdvancedOptics", "AircraftELINT", "AircraftRWR"] checked against mods-source/_vanilla/original/systems/sensors.ini (present at lines 565 and 525). The donor MQ-9 ER itself uses AircraftELINT for its SensorSystem5, so this follows the airframe author's own choice.
  
  Effect: Passive ELINT/RWR fit modelling the ZLQ-1 — the aircraft can listen without emitting.
  
  If the donor changes: Vanilla definitions; no mod dependency.

- **AI Role=MaritimePatrol,Recon,ESM and UnitScoreValue=4 (donor: Role=AEW,ESM, UnitScoreValue=1).**  
  ***UNSTATED*** — No comment in TRITON_HEAD and no note in the README beyond restating the value ("AI role | `MaritimePatrol,Recon,ESM`"). Neither the role-token change nor the 1→4 score bump has a recorded basis.
  
  Effect: Determines which AI tasking the Triton accepts, and makes killing one worth four times the donor MQ-9 in mission scoring.

- **Signature raised from the donor's Meager to RCS=Small / IRSignature=Small.**  
  *Real-world spec* — Inline comments: `IRSignature=Small // single high-bypass turbofan` and `RCS=Small // blended composite airframe, smaller return than a fighter`. Donor is `IRSignature=Meager` / `RCS=Meager` (mods-source/3503670861/aircraft/usaf_mq-9_er.ini:28-30). In vanilla's aircraft set the bands used are Meager (3 files) < Small (19) < SemiSmall (54…
  
  Effect: The Triton is a slightly EASIER radar/IR target than the small MQ-9 it borrows the mesh from — deliberately findable, matching the README framing "An emitting, findable, but far-seeing plat…

- **CarrierCapable=False (the donor MQ-9 ER is CarrierCapable=True).**  
  ***UNSTATED*** — No comment records the change; donor value at mods-source/3503670861/aircraft/usaf_mq-9_er.ini:4. Correct for a 39.9 m HALE aircraft, but nothing states it.
  
  Effect: The Triton cannot be based on a carrier — it must fly from the land bases the RAAF Bases pack stations it at.

- **Two squadrons only — `MQ-4C No. 9 SQN` and `MQ-4C Det Tindal` — both Nation=Australia, both keeping the donor's 42nd ATKS gray livery texture.**  
  *Real-world spec* — NAMES_INI: "operated by No. 9 Squadron RAAF from Edinburgh with forward detachments at Tindal". The livery reuse is acknowledged rather than hidden in the README first-flight checks: "It uses the donor's 42nd ATKS gray livery with the Australian flag." Donor's 5-squadron table (42_ATKS/65_SOS/147_AW/162_AW/174_ATKS, all Nation=US) is cut…
  
  Effect: Two selectable RAAF squadrons under the Australian flag, wearing USAF gray. Consumed downstream: integration/raaf-bases/build_pack.py stations `("raaf_mq-4c_triton", "Squadron1,3")` at Edin…
  
  If the donor changes: The livery texture lives in the donor mod's assets/textures/mq-9/ — losing the donor loses the skin as well as the mesh.

- **Reference the donor's gear animation file (`AnimationFile_1=animations_usaf_uav_mq-9`) cross-mod and hard-fail the build if it disappears.**  
  *File semantics* — check_systems(): `if not (MQ9_MOD / "animations" / "animations_usaf_uav_mq-9.ini").exists(): problems.append("MQ-9 mod animation file missing: animations_usaf_uav_mq-9")`. Rests on the repo rule in docs/design-notes.md: "Asset paths resolve across mods — a pack can reference another mod's mesh folder (the Triton flies the MQ-9 mod's mode…
  
  Effect: Gear retraction/extension animates using the donor's rig.
  
  If the donor changes: Donor removal breaks the animation reference along with everything else.

- **Declare the MQ-9 mod dependency in prose and enforce it at build time, because the repo's automated dependency checker cannot see it.**  
  *File semantics* — Running `python3 tools/check_dependencies.py` reports: "SEST_ADF_Persistent_ISR / standalone - needs nothing but the base game" — false, and exactly the blind spot docs/design-notes.md warns about. The checker only derives OVERRIDE (pack ships a file a mod provides) and REFERENCE (loadout hangs a store / roster names a unit) dependencies…
  
  Effect: None directly, but it is the difference between a player being warned and a player getting an invisible/broken aircraft.
  
  If the donor changes: If the MQ-9 mod is unsubscribed, nothing in the automated gate chain will catch it — only the README and the in-game result.

- **Treat the pack as order-insensitive and document it as 'place below the MQ-9 Reaper mod' even though it actually ships at the top of the order.**  
  *File semantics* — README install step 2: "Place it **below** the MQ-9 Reaper mod in the Mod Manager (additive — it only adds a new unit, so ordering is forgiving)"; same wording in _info.ini. In practice the pack is consolidated into SEST_Integration, which data/load-order.tokens.txt pins first ("INVARIANT: every SEST_* pack sits above every workshop mod"…
  
  Effect: None — but the README instruction contradicts the shipped order and would mislead anyone installing the standalone folder.
  
  If the donor changes: n/a

- **Generate everything from build_pack.py with fail-loud donor validation, never hand-edit the pack.**  
  *File semantics* — Every donor-dependent step exits non-zero on drift: extract() on missing banners, the Weapon_N submodel loop, check_systems() for the three vanilla + one MQ-9 sensor definitions and the animation ini, and the post-rewrite prop/audio assertion. README: "Validates the MQ-9 ER donor layout, every hidden submodel, the vanilla and MQ-9 sensor…
  
  Effect: None directly; it is what keeps a Workshop update from silently degrading the unit.
  
  If the donor changes: A donor update that moves a banner or renames a submodel breaks the BUILD, not the game — the failure surfaces at rebuild time.

**Must stay subscribed**

- 3503670861 General Atomics MQ-9 Reaper (author MyGo!!!!!鼓手椎名立希) — MANDATORY and hard. Supplies the hull mesh and materials (`ResourcesFolder=assets/models/vechicle/aircraft/mq-9/`, `ResourcesRoot=mq-9.obj`, `mq-9_mat.ini`), the l…
- Vanilla base game — `[AircraftELINT]` and `[AircraftRWR]` in systems/sensors.ini, and the audio clips audio/aircraft/TF30, jet_rear_1, jet_far_1. No mod needed.
- No dependency on the P-8 mods: 3602046770 Boeing P-8 Poseidon is only the design template for the AN/ZPY-3 block. The pack emits its own copy, so unsubscribing the P-8 mod changes nothing here.
- Downstream consumers (not dependencies of this pack, but they break if it is removed): integration/raaf-bases/build_pack.py rosters `raaf_mq-4c_triton` at Edinburgh (Squadron1,3) and Tindal (Squadron2,2) — data/mod-catalog.json r…

**Known limits**

- Mesh scale: the aircraft renders at the donor's 20 m span against a declared 39.9 m — stated in the file itself (`WingSpan=39.9 //meters (mesh is the 20 m MQ-9 - accepted stand-in)`), in the README, and in the player-visible unit…
- Livery: USAF 42nd ATKS gray with an Australian flag decal — no Australian texture exists in the donor mod and the pack ships no assets (tools/check_dependencies.py header: "The packs ship 99 files and every one is a .ini - not a …
- Mesh/texture references are unverifiable at build time: tools/export-mod-configs.ps1 copies only text files (`.ini, .txt, .json, .cfg, .xml, ...`), so mods-source/3503670861 contains 32 .ini files and no textures directory at all…
- The MQ-9 dependency is invisible to the repo's automated gate: tools/check_dependencies.py prints "SEST_ADF_Persistent_ISR / standalone - needs nothing but the base game". Only build_pack.py's own check_systems() and the README r…
- Dead validation / stale doc: build_pack.py still checks vanilla for `AdvancedOptics` and the README lists it as a dependency, but the emitted unit never references it (it uses the donor's AN/AAS-52_Visual).
- Stale README claim: "the SEST RAAF Bases rebuild stations it at Edinburgh, Tindal, Woomera and Learmonth" — integration/raaf-bases/build_pack.py rosters the Triton only at Edinburgh and Tindal; Woomera's and Learmonth's airgroups…
- Install-order wording in README/_info.ini ("place below the MQ-9 Reaper mod") is the reverse of where the pack actually ships (inside SEST_Integration at position #1, above 3503670861 at #75). Harmless because the pack overrides …
- The pack derives the Triton from the *unpatched* donor file in mods-source/, not from the copy SEST_Allied_Fixes overrides (that pack ships its own usaf_mq-9_er.ini with AGR-30 pods). The two never interact because the Triton is …
- Balance numbers with no recorded derivation: the AN/ZPY-3's 430 km / Gain 60 / 900 kW / 25 s IdentificationTime, the flight-model gain reductions, UnitScoreValue=4, Role token list, ReadyUpTime=20/CoolDownTime=45, and the MTS-B V…

### `raaf-f-35a-jatm`

Adds four future-arsenal loadouts (AIM-260 JATM x3, AIM-424 MALICE x1) and an F-35C-standard EW suite to Greene's RAAF F-35A by regenerating that mod's whole aircraft file from source, so the override that carries the new fits also carries every loadout, station table and sensor reference upstream already shipped.


**Files (5)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `/home/user/Seapower-mods/integration/raaf-f-35a-jat…` | overrides | 3514484654 — "RAAF F-35A Lighting II" (… | It is the only mod in mods-source/ that ships aircraft/raaf_f-35a.ini (find over mods-source returns 3514484654 only); the catalog lists its sole ove… |
| `/home/user/Seapower-mods/integration/raaf-f-35a-jat…` | adds | flight model rebased on usn_aim-174b as… | New id, no upstream file to displace. Two donors, each chosen for a stated reason: for the flight model, "Aligned to usn_aim-174b as shipped by U.S. … |
| `/home/user/Seapower-mods/integration/raaf-f-35a-jat…` | merges | 3514484654 — "RAAF F-35A Lighting II" (… | language_*/ files merge key-by-key, but the builder still rebases on upstream's own loadout_names.ini (`src_names = UPSTREAM / f"language_{lang}" / "… |
| `/home/user/Seapower-mods/integration/raaf-f-35a-jat…` | merges | none — SEST-authored, emitted by integr… | Deliberately partial (one line, sest_aim-424) rather than rebased on any mod's ammunition_names.ini: "All four SEST packs that carry MALICE fits writ… |
| `/home/user/Seapower-mods/integration/raaf-f-35a-jat…` | adds | n/a — pack manifest | Carries the load-order mandate the pack depends on ("Place ABOVE the RAAF F-35A mod in the Mod Manager") and ApproximateVersion=0.8.2. |

**Decisions (23)** — File semantics 7, Upstream donor 5, In-game observation 4, UNSTATED 3, Engine precedent 2, Author mandate 1, Comparison 1


- **Regenerate the whole upstream aircraft file rather than ship a hand-written partial: the builder reads mods-source/3514484654/aircraft/raaf_f-35a.ini, mutates it, and writes the result.**  
  *File semantics* — build_patch.py: `UPSTREAM = ROOT / "mods-source" / "3514484654" # RAAF F-35A (Greene)`; `src = UPSTREAM / "aircraft" / "raaf_f-35a.ini"`. docs/design-notes.md: "Unit files are whole-file overrides. For aircraft/ ... the highest mod's copy loads and the rest are gone — silently."
  
  Effect: Player sees the upstream 8 loadouts (AirToAirStealth ... AntiShipHeavy) plus 4 new SEST fits in one dropdown; nothing Greene shipped disappears.
  
  If the donor changes: If 3514484654 is unsubscribed the pack's copy of raaf_f-35a.ini still loads, but the aircraft loses upstream's ammunition (usaf_aim-120c7, usaf_jsm, usn_aim-9x), meshes, animations and squa…

- **Insert the four new loadout keys before the trailing '#' comment on the AvailableLoadouts line instead of appending to the line.**  
  *File semantics* — build_patch.py: "# 1. Extend AvailableLoadouts — the upstream line carries a trailing '#'-comment, so insert before it rather than appending to the line." Upstream line 172: `AvailableLoadouts=...,AntiShipHeavy #,StrikePrecision,,,,Ferry`. Guarded: `sys.exit("AvailableLoadouts line not found — upstream layout changed")` and `sys.exit(f"l…
  
  Effect: All four SEST fits are selectable; upstream's deliberately commented-out StrikePrecision/Ferry stay disabled instead of being silently re-enabled.
  
  If the donor changes: If upstream restructures that line the build aborts loudly rather than emitting a broken loadout list.

- **Clone each new fit's station map and SubmodelsToHide from a block Greene already proved, swapping only the round: Intercept260Stealth from [WeaponSystem1AirToAirStealth], Intercept260 from …**  
  *Upstream donor* — Hide lists are byte-identical to upstream's: Intercept260Stealth and Malice424 use `pyl_l,pyl_r,wing_pyl_inner,wing_pyl_outer,wing_rail_inner,wing_rail_outer,bru-61a_left,bru-61a_right` = upstream [WeaponSystem1AirToAirStealth] line 292 / [WeaponSystem1AntiShip] line 355; Intercept260 uses upstream [WeaponSystem1AirToAir] line 278; Inter…
  
  Effect: AIM-260 fits hang and hide pylons exactly like the AMRAAM fits they replace — same six-round internal bay, same clean-signature look.
  
  If the donor changes: If Greene renames a submodel or renumbers stations the cloned hide lists go stale silently (no builder guard covers submodel names); a rebuild would pick up new geometry only for the copied…

- **Keep the wingtip rails pyl_l/pyl_r VISIBLE on Intercept260Beast, unlike the two stealth fits.**  
  *Upstream donor* — build_patch.py NEW_SECTIONS: "# pyl_l/pyl_r are the WINGTIP launch rails and [WeaponSystem2Intercept260Beast] puts AIM-9X on the wingtip stations, so they must stay visible or the missiles float unattached." Matches upstream's own split (AirToAir keeps them, AirToAirStealth hides them). Fixed in commit 673e50b: "Intercept260Beast hid pyl…
  
  Effect: The two wingtip AIM-9X on the beast fit render attached to their rails instead of floating.
  
  If the donor changes: Purely internal to this pack; unaffected by donor churn.

- **Give the external AIM-260s explicit seat corrections via new position keys injected into [WeaponSystem2] — AAM260IPositions=0,0.0025,0.0035 and AAM260OPositions=0,0.0025,0.002 — and mount t…**  
  *In-game observation* — Four tuning commits driven by looking at it: ee7d97c "correcting the low/aft hang the user screenshotted on the RAAF F-35A beast fit"; a3d140d "First guess overshot - missiles clipped into the pylons. Halved the vertical offset (~17cm up from the model origin)"; 192437f "Vertical is flush at 0.0025; pull the missiles back ~20cm"; 20642b7…
  
  Effect: On the 10-missile beast fit the four wing AIM-260s sit flush on the pylons instead of hanging low and aft or clipping through them.
  
  If the donor changes: The keys are injected into the pack's own copy of the file, so they survive donor updates only through a rebuild; if Greene moves the wing pylon geometry the offsets become wrong again with…

- **Split the offset per pylon pair rather than using one shared key — inner pylons (WS2 stations 3/4) ride z=0.0035, outer (5/6) keep z=0.002.**  
  *In-game observation* — build_patch.py: "Split per pylon pair: inner (WS2 stations 3/4) slightly forward of the outer (5/6), which keeps the proven aft position." Commit 0c05ac2: "External AIM-260s now use per-pair offsets: inner wing pylons (WS2 3/4) ride slightly forward (z=0.0035), outer (5/6) keep the proven aft position (z=0.002), on both F-35 packs." docs…
  
  Effect: Inner and outer wing AIM-260s each sit correctly on their own pylon instead of one pair being compromised for the other.
  
  If the donor changes: Same as above — pack-local, rebuild-dependent.

- **Only the outer offset is described as verified. The inner-pair value 0.0035 was introduced with a geometric rationale but no recorded screenshot or in-game check.**  
  ***UNSTATED*** — The word "proven" in build_patch.py and in commit 0c05ac2 attaches only to the outer 0.002 ("keeps the proven aft position"); nothing in the builder, README, design-notes or commit history records a look at the inner pair after the split. FLAG.
  
  Effect: The two inner-pylon AIM-260s on the beast fit may still be seated slightly wrong; nobody has said otherwise on the record.
  
  If the donor changes: n/a — a one-line constant, cheap to re-tune.

- **Transplant the F-35C's sensor systems 3-12 over the RAAF F-35A's EW half, leaving SensorSystem1 (Eyes) and SensorSystem2 (AN/APG-81) untouched, and rewrite NumberOfSensorSystems 6 -> 12.**  
  *Upstream donor* — transplant_ew_suite() docstring: "Upstream ships a 6-sensor fit whose EW half is F-22 legacy kit (AN/ALR-94 + ALQ-94). The maintained F-35C carries the real F-35 suite... SensorSystem1 (Eyes) and SensorSystem2 (AN/APG-81) are left in place because AssociatedSensors= lines point at SensorSystem2 by index; only systems 3+ are replaced, and…
  
  Effect: The RAAF F-35A gains real F-35 RWR/ESM/DECM, EOTS, EODAS, Link-16 and GPS and a usable onboard jammer, instead of the F-22's ALR-94/ALQ-94; [WeaponSystem1] AssociatedSensors=SensorSystem2 a…
  
  If the donor changes: Breaks loudly, not silently, if USNA changes: `sys.exit("could not extract the F-35C sensor block — upstream layout changed")` and `sys.exit(f"sensor block replacement matched {n} times — r…

- **Before writing, verify every transplanted SystemName is defined by some installed mod's systems/sensors.ini — scanning all of mods-source, not just the donor.**  
  *File semantics* — transplant_ew_suite(): "# Every sensor type named must be defined by a mod that will be loaded." `for f in (ROOT / "mods-source").rglob("systems/sensors.ini") ... sys.exit(f"sensor types not defined by any installed mod: {unknown}")`. This is sound because docs/design-notes.md records "systems/ and language_*/ merge key-by-key. Proof: 89…
  
  Effect: No silently dead sensor entries — an unresolvable EW type stops the build instead of shipping a fighter with a phantom jammer.
  
  If the donor changes: Because sensors.ini merges, the EW types survive unsubscribing US Naval Aviation as long as the deprecated MyGo F-35C (3508978375) is still installed; unsubscribing both would leave the sen…

- **Validate ammunition references against every ammunition/ ini in mods-source (including _vanilla), rather than against a named donor list.**  
  *File semantics* — build_patch.py: "# all of mods-source (incl. _vanilla): most stores have several providers, and a narrow donor list would hard-bind the build to one of them"; `refs = set(re.findall(r"^Station\d+=([^|\s/]+)", NEW_SECTIONS, re.M))` (the regex strips the `|AAM260I` position-key suffix) then `sys.exit(f"unresolved ammunition ids: {missing}"…
  
  Effect: None directly; it is the guard that stops a fit shipping with an id no installed mod defines (which would give an empty station in game).
  
  If the donor changes: The check runs at build time only — a later unsubscribe of the last provider of an id is caught by tools/check_dependencies.py, not by this builder.

- **Reference the AIM-260 by id (dts_aim-260 internal, dts_aim-260_w external) and do NOT ship the ammunition file, letting the Dingtools Weapon Pack's copy win.**  
  *Author mandate* — build_patch.py NEW_SECTIONS header: "# Added by the SEST RAAF F-35A JATM patch. dts_aim-260 comes from the Dingtools Weapon Pack; everything else resolves from this mod / vanilla." Two mods ship dts_aim-260.ini — 3760871384 "Dingtools Weapon Pack" and 3636386513 "F-15 EX Eagle II", same author — and their stats differ (Weapon Pack: Mass=…
  
  Effect: The JATM the RAAF F-35A fires is the Weapon Pack's datalink-guided KillProbability=0.92 round, not the F-15EX mod's weaker radio-command version.
  
  If the donor changes: If 3760871384 is unsubscribed the fits silently fall back to the F-15EX mod's weaker dts_aim-260 (or, with both gone, to empty stations). If the two mods are reordered so F-15EX outranks th…

- **Use usn_aim-9x (the id the RAAF mod itself bundles and uses) for the wingtip stations, not Dingtools' dts_aim-9x.**  
  *Upstream donor* — [WeaponSystem2Intercept260] and [WeaponSystem2Intercept260Beast] use `Station1=usn_aim-9x / Station2=usn_aim-9x`, identical to upstream [WeaponSystem2Default] lines 268-269 and [WeaponSystem2AirToAir] lines 288-289. README: "the AIM-9X is bundled with the RAAF mod itself."
  
  Effect: Wingtip AIM-9X on the SEST fits behave identically to the ones on Greene's own fits.
  
  If the donor changes: usn_aim-9x has seven providers including the RAAF mod itself, so the reference cannot go unresolved while the aircraft is installed; which copy wins depends on load order.

- **Compose Malice424 as 2x sest_aim-424 on the big bay stations 7/8 plus 2x dts_aim-260 on the bay-door rails 3/4, all pylons hidden.**  
  *Upstream donor* — build_patch.py: "# Full-stealth counter-air/SEAD fit: two AIM-424 MALICE on the big bay stations (7/8, where JSM/JDAM go) plus two AIM-260 on the bay door rails." The station map mirrors upstream [WeaponSystem1AntiShip] (Station3/4=usaf_aim-120c7, Station7/8=usaf_jsm) and [WeaponSystem1StrikeStealth] (Station7/8=usaf_gbu-31_v1) — upstrea…
  
  Effect: A clean-signature four-round fit: two 290 nm MALICE with an anti-emitter mode plus two JATM, at the cost of six-shot capacity.
  
  If the donor changes: Station 7/8 coordinates come from upstream's table; if Greene retunes the bay the fit follows on rebuild.

- **Ship the AIM-424 MALICE from one shared source module written byte-identically into every pack that carries a MALICE fit (six packs) instead of per-pack variants.**  
  *File semantics* — integration/common/aim424.py docstring: "All four SEST packs that carry MALICE fits write identical copies of ammunition/sest_aim-424.ini and a partial language_en/ammunition_names.ini - identical same-path files are a safe overlap whichever pack sits higher in the Mod Manager." Enforced downstream by tools/consolidate_packs.py: "identic…
  
  Effect: The MALICE performs the same whichever aircraft carries it and whichever pack sits highest.
  
  If the donor changes: Any hand-edit of one pack's copy fails consolidation loudly rather than shipping two different missiles under one id.

- **Align the AIM-424's flight model key-for-key with usn_aim-174b and keep a documented list of deliberate deltas (290 vs 316 nm range, 40/80 nm seeker vs 15/15, Full passive anti-emitter vs H…**  
  *Comparison* — common/aim424.py: "Same explicit-drag flight model, same 150,000 ft loft ceiling, same fragmentation warhead class, same datalink midcourse, same chart basis (36,000 ft / 260 kt), same modern ECCM keys. What stays different, on purpose: ..." Commit 9b6b2fa is the side-by-side that drove it: "Side by side in the encyclopedia the MALICE lo…
  
  Effect: The MALICE reads as a peer of the AIM-174B on the same encyclopedia assumptions: longest internal-carriage reach in the collection, best seeker, but 28 deg/s turn rate so the AIM-260 (40 de…
  
  If the donor changes: If the load order changes so a different mod's usn_aim-174b wins (3426791311, 3430135740 or 3737267013 all ship one), the card the MALICE was tuned against is no longer the card in game and…

- **Keep DragCoefficient explicit at 3.6 — never -1.**  
  *In-game observation* — common/aim424.py: "THIS KEY MUST STAY EXPLICIT: at -1 the engine back-solves 8.14 from the airframe and the missile loses roughly a third of its reach." Commit 9b6b2fa: "The root cause was DragCoefficient=-1. That is not 'default drag' - it tells the engine to back-solve the coefficient from the airframe, and on the AARGM-ER body it solv…
  
  Effect: The MALICE actually reaches its advertised 290 nm instead of quietly flying at double drag.
  
  If the donor changes: Pack-local constant; no donor dependency.

- **Keep the [Models] block byte-identical to US Naval Aviation's usn_agm-88g and add nothing to it — specifically, no ResourcesMeshScale.**  
  *In-game observation* — common/aim424.py: "REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the missile stopped rendering as an AARGM-ER afterwards - the model block falls back to AssetBundleMesh=usn_rim-7, a short fat Sea Sparrow, which is exactly what showed up under the wing... Do not add keys to it that the source mod does not use." …
  
  Effect: The MALICE renders as an AGM-88G AARGM-ER instead of a Sea Sparrow stand-in — at AGM-88G native size, which cannot be changed.
  
  If the donor changes: The mesh path `ResourcesFolder=assets/models/ammunition/agm-88/` resolves across mods (design-notes: "Asset paths resolve across mods"), so unsubscribing US Naval Aviation (3737267013) sile…

- **Keep the [col_main] Scale matched to usn_agm-88g's rather than sizing it to the missile's stated dimensions.**  
  *Engine precedent* — common/aim424.py: "This Scale is the HIT COLLIDER box, not the visual - every ammunition ini in the collection carries it under [col_main] and none has a model-size key. The visual renders at the shared usn_rim-7 mesh's native size, same as usn_agm-88g, and cannot be resized from the ini... Keep the collider matched to usn_agm-88g's, who…
  
  Effect: Hit detection matches the model the player actually sees.
  
  If the donor changes: Tied to the AGM-88G visual; if the mesh donor changes, the collider should follow.

- **Keep the display strings for the globally-shared loadout keys (Intercept260, Intercept260Beast, Malice424) identical to the F-35C pack's, and prefix all four with "SEST".**  
  *File semantics* — build_patch.py LOADOUT_NAMES: "# Intercept260/Intercept260Beast/Malice424 are also defined by the F-35C pack — keep the shared keys' strings identical across both packs." The counterpart in integration/f-35c-jatm/build_patch.py spells out why: "[LoadoutNames] keys are global across mods; the RAAF pack defines Intercept260/Intercept260Bea…
  
  Effect: The same loadout name reads correctly on both the F-35A and the F-35C regardless of which pack merges last; Intercept260Stealth is RAAF-only so it carries no cross-pack constraint.
  
  If the donor changes: Editing one pack's string without the other reintroduces a load-order-dependent label; tools/consolidate_packs.py catches conflicting values on merge ("Key-level merge of language files; co…

- **Declare ApproximateVersion=0.8.2 in _info.ini.**  
  *Engine precedent* — Commit 673e50b: "Every SEST pack declared ApproximateVersion=0.6.8 against a 0.8.x game. That check requires MAJOR and MINOR to match, so all seven packs were failing it. Now 0.8.2, matching the rebase sources."
  
  Effect: The Mod Manager stops flagging the pack as version-incompatible.
  
  If the donor changes: Must be bumped by hand when the game's minor version moves; nothing in the builder derives it from the donor.

- **Require the pack to sit ABOVE the RAAF F-35A mod (and above every workshop mod) in the Mod Manager.**  
  *File semantics* — _info.ini Description: "Place ABOVE the RAAF F-35A mod in the Mod Manager." README: "In the Mod Manager, place it above the RAAF F-35A mod. Keep Dingtools Weapon Pack installed." docs/design-notes.md Tier 0 invariant: "Every SEST pack sits above every workshop mod, as one unbroken block... tools/check_load_order.py computes the rules (ea…
  
  Effect: If violated, the entire pack — new loadouts and EW suite alike — silently does nothing.
  
  If the donor changes: Enforced by tools/check_load_order.py before every push; not enforced by the game.

- **The AIM-424's AmmoPoints=2600 sits between the AGM-88G airframe donor's 2850 and the AIM-174B's 2500, with no recorded reason for the value.**  
  ***UNSTATED*** — common/aim424.py sets `AmmoPoints=2600` with no comment, while neighbouring values carry explicit `// cf. AIM-174B ...` annotations. mods-source/3737267013/ammunition/usn_agm-88g.ini has AmmoPoints=2850 (and Mass=467, which the MALICE does copy); mods-source/3606774881/ammunition/usn_aim-174b.ini has AmmoPoints=2500. FLAG.
  
  Effect: Affects how many MALICE an airbase/magazine load consumes; no stated basis for the exact figure.
  
  If the donor changes: n/a — single constant.

- **Ship only aircraft/raaf_f-35a.ini and leave upstream's aircraft/raaf_f-35a_squadrons.ini unoverridden.**  
  ***UNSTATED*** — No comment in build_patch.py or README addresses the squadrons file; the builder simply never reads it. (Benign in practice — grep for "loadout" in mods-source/3514484654/aircraft/raaf_f-35a_squadrons.ini returns nothing, so the new keys are not referenced there — but the reasoning is not recorded anywhere.) FLAG.
  
  Effect: Squadron definitions keep coming from Greene's mod and pick up his updates directly; the new SEST fits are selectable per-aircraft but are not pre-assigned to any squadron.
  
  If the donor changes: Squadron data is lost entirely if 3514484654 is unsubscribed, since this pack does not carry a copy.

**Must stay subscribed**

- 3514484654 "RAAF F-35A Lighting II" (Greene) — MUST stay subscribed and MUST sit below the pack. It supplies the airframe mesh, animations, squadron file and the upstream ammunition the carried-over loadouts fire (usaf_aim-120c7,…
- 3760871384 "Dingtools Weapon Pack" (dingtools) — supplies dts_aim-260 (internal) and dts_aim-260_w (external). Without it all four new fits lose their primary round. It must also outrank 3636386513 "F-15 EX Eagle II", which ships…
- 3737267013 "United States Naval Aviation" (misaka) — two separate roles: (a) it is the donor for the transplanted F-35C EW block and one of two mods defining those sensor types in systems/sensors.ini (the other is the deprecated …
- 3606774881 "U.S. Navy 2027 Capabilities mod" (Prof_CH4OS) — not required to load, but it is the usn_aim-174b the MALICE was balanced against ("the version that actually wins the load order in this collection, and the card the MAL…
- SEST_Integration (the consolidated pack) must outrank every workshop mod — Tier 0 invariant, checked by tools/check_load_order.py.

**Known limits**

- The AIM-424 MALICE cannot be made to look smaller than an AGM-88G. "the Scale key in ammunition inis is the hit collider (every file carries it under [col_main]; the [Models] block has no size key), and the one candidate visual k…
- Malice424 is a 4-round fit (2 MALICE + 2 AIM-260), not 6 — the MALICE occupies the two big bay stations (7/8) that JSM/JDAM use, so bay capacity is the ceiling.
- The MALICE's 290 nm is deliberately short of the AIM-174B's 316 nm: "it has to fit inside an F-35 weapons bay" (common/aim424.py).
- MaxTurnRate 28 deg/s against the AIM-260's 40 is a deliberate trade, not a shortfall: "the MALICE out-reaches everything you can carry internally but loses the endgame knife fight" (commit f147057).
- The EW transplant is a regex cut against US Naval Aviation's usn_f-35c.ini layout; any restructuring of that file's sensor section aborts the build ("could not extract the F-35C sensor block — upstream layout changed") rather tha…
- The override hides upstream updates to raaf_f-35a.ini until the pack is rebuilt — docs/design-notes.md: "Upstream moves under you. A shadowed file can receive author updates the override hides... After any export, diff what chang…
- Wing-pylon seat offsets are hand-tuned constants in model units (~7cm per 0.001) with no automated verification; only the outer-pair value is on record as verified.

### `allied-fixes`

Repairs two allied units that were broken by cross-mod data defects (the P-8's anti-ship fit hung on a round no mod defines; HMS Ocean could not embark the Apache AH1 her own sister hulls already support) and adds two new pod-launched guided rockets rebased on proven upstream weapons, rolled out across seven allied airframes owned by four different mods — all generated by /home/user/Seapower-mods/integration/allied-fixes/build_patch.py, which guards every upstream line it touches.


**Files (13)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `aircraft/usn_p8_2027.ini` | overrides | 3606774881 — U.S. Navy 2027 Capabilitie… | Sole shipper: `find mods-source -iname usn_p8_2027.ini` returns only 3606774881. It also ships the replacement round (ammunition/usn_agm-84n.ini), so… |
| `aircraft/usn_p8.ini` | overrides | 3602046770 — Boeing P-8 Poseidon (autho… | Sole shipper of usn_p8.ini. Builder: 'usn_p8 from mod 3602046770 has the identical four-line typo and the identical ASW,AntiShip pair, so it gets the… |
| `vessels/rn_lph_ocean.ini` | overrides | 3599752717 — Euromod - Modern British N… | Sole shipper of rn_lph_ocean.ini, and the same mod ships the sister hulls that supply the precedent (rn_lph_ocean_asw_00/_13 already list uk_ah_mk_1 … |
| `aircraft/uk_ah_mk_1.ini` | overrides | 3425450153 — AH-64 Apache (author misak… | Sole shipper of uk_ah_mk_1.ini; it is also the airframe HMS Ocean was just taught to operate, which is why the new APKWS-ER fit lands here first ('Ca… |
| `aircraft/usa_ah-64a.ini, aircraft/usa_ah-64d.ini, a…` | overrides | 3425450153 — AH-64 Apache (author misak… | Sole shipper of all four Apache variants; each is re-emitted with one appended SEST_REDBACK loadout cloned from its own Strike fit (the naval AH-64NA… |
| `aircraft/usa_a-10c.ini` | overrides | 3459682829 — A-10C (author misaka) | Sole shipper of usa_a-10c.ini. Donor fit is that mod's own CAS1 block (5x usn_agr-20b on LAU-68 + TER pairs), the densest rocket fit it defines. |
| `aircraft/usaf_mq-9a.ini, aircraft/usaf_mq-9_er.ini` | overrides | 3503670861 — General Atomics MQ-9 Reape… | Sole shipper of both Reaper files. Neither declares a rocket fit, so the Strike fit is cloned with its Hellfire rails (uav_agm-114k) and GBU-49 stati… |
| `ammunition/sest_apkws_er.ini` | adds | 3425450153 — AH-64 Apache; cloned from … | Builder: 'the Apache mod's M282 APKWS with the launch envelope extended 3.5 -> 8 nm ... byte-identical but for the range line'. NOTE: 3459682829 (A-1… |
| `ammunition/sest_agr-20er.ini` | adds | 3425450153 — AH-64 Apache; cloned from … | Only the payload line changes: `Ammunition=usa_apkws_2_m282` -> `Ammunition=sest_apkws_er`, guarded to exit if that line count is not exactly 1. Pod,… |
| `ammunition/sest_agr-30.ini` | adds | 3760871384 — Dingtools Weapon Pack (aut… | Chosen over the Apache M282 after that build froze the game: 'dts_apkws-ii is a PROVEN in-pod rocket WITH loft keys from the collection's own weapon … |

*…and 3 more.*

**Decisions (22)** — File semantics 6, UNSTATED 5, Upstream donor 3, Engine precedent 3, Player directive 2, In-game observation 2, Real-world spec 1


- **Substitute usn_agm-84g -> usn_agm-84n on all four AntiShip station lines of the P-8, rather than deleting the loadout or inventing a round.**  
  *Upstream donor* — build_patch.py docstring: 'It is a typo, and the mod answers it itself: U.S. Navy 2027 writes usn_agm-84n nineteen times and usn_agm-84g four times, and all four are these station lines. usn_agm-84n is its own Harpoon Block II+ ER - 522 kg, 150 nm - already carried by its ships and its Super Hornets.' Verified: usn_agm-84g appears in exa…
  
  Effect: The P-8's only anti-ship fit now hangs 4x AGM-84N Harpoon Block II+ (150 nm) instead of loading empty. Commit da1ef63: 'It is fielded five times in NORTHERN FRONT III FINAL.'
  
  If the donor changes: The pack owns U.S. Navy 2027's whole usn_p8_2027.ini, so any future upstream edit to that file is hidden. If 3606774881 is unsubscribed, usn_agm-84n is undefined and both P-8s' AntiShip fit…

- **Apply the same substitution to the second, independently-authored P-8 (3602046770), knowingly creating a new cross-mod dependency from the Kirameki P-8 onto U.S. Navy 2027's round.**  
  *Upstream donor* — TARGETS list comment: ('3606774881', 'usn_p8_2027.ini') '# U.S. Navy 2027 - fielded in NFIII FINAL' and ('3602046770', 'usn_p8.ini') '# same typo, same fix'.
  
  Effect: Both Poseidons get a working anti-ship fit with the same round, so the two mods' P-8s behave identically.
  
  If the donor changes: Unsubscribing 3606774881 leaves the Kirameki P-8 pointing at a round its own mod does not ship — a dependency it did not have before this pack.

- **Do NOT override six other aircraft that declare a loadout with no matching WeaponSystem block (usn_e-2d, fr_e2c, fr_e2d, usn_ch-46d, usaf_ac-130a_83, jmsdf_kv_107*).**  
  *File semantics* — Docstring: 'every one of them is an unarmed aircraft whose blocks carry zero stores. The picker entry is cosmetic and an override would add a dependency for no gameplay change.'
  
  Effect: None — deliberately. Keeps the pack's override surface (and therefore its dependency list) minimal.
  
  If the donor changes: n/a — nothing shipped.

- **Do NOT override usn_p-3d despite a missing Recon block.**  
  *File semantics* — Docstring: 'usn_p-3d is missing only its Recon block; ASW, AntiShip and Empty all work, and nothing fields it.'
  
  Effect: None; the aircraft's working fits are untouched and no mission uses it.
  
  If the donor changes: n/a

- **Treat the apparent undefined DateBased_* stores on rn_merlin_hm1 and the two Lynxes as a non-defect.**  
  *Engine precedent* — Docstring: 'They do not - DateBased_ is a vanilla mechanic, used by stock submarines like usn_ssn_permit.'
  
  Effect: None — avoided a spurious override of three Royal Navy helicopters.
  
  If the donor changes: n/a

- **Reverted an earlier fix that declared Default/Empty loadouts on usaf_b-52h_419_flts, on the grounds that the engine supplies them implicitly.**  
  *Engine precedent* — Commit da1ef63: 'REVERT: the previous commit declared Empty and Default on usaf_b-52h_419_flts, claiming the author had written unreachable blocks. That was wrong. Vanilla's own usn_f-14a and usaf_b-52g do not declare them either and plainly offer them in game, and 95 of 135 allied airframes are the same - the game supplies Default/Empty…
  
  Effect: No duplicated picker entries; one fewer file overridden.
  
  If the donor changes: n/a — the file is no longer shipped by this pack.

- **Append uk_ah_mk_1 to HMS Ocean's AircraftSupported (single id appended to the existing raac_lynx_ah7 line).**  
  *Upstream donor* — Builder comment: 'her own sister hulls in the same mod (rn_lph_ocean_asw_00 and _asw_13) already list uk_ah_mk_1 ... but the base rn_lph_ocean only ever got the Lynx. One appended id fixes it.' Verified in mods-source/3599752717: line 139 of _asw_00 and _asw_13 both end in ',uk_ah_mk_1'; the base hull reads 'AircraftSupported=raac_lynx_a…
  
  Effect: HMS Ocean can embark and operate the British Army Apache AH1 — the same airframe her sister hulls already carry.
  
  If the donor changes: Whole-file override of Euromod British's rn_lph_ocean.ini; if 3599752717 is unsubscribed the hull and its model are gone entirely. The builder exits if upstream adopts the fix: 'rn_lph_ocea…

- **Justify the Apache-on-Ocean pairing with the real 2011 deployment as well as the file precedent.**  
  *Real-world spec* — Builder comment: 'uk_ah_mk_1 - the British Army Apache AH1 that really flew from Ocean off Libya in 2011'.
  
  Effect: Same as above; documents why this particular airframe id and not a generic one.
  
  If the donor changes: n/a

- **Build APKWS II-ER (sest_apkws_er) as a range-only clone: MaxLaunchRange 3.5 -> 8, everything else byte-identical to the Apache mod's M282.**  
  *Player directive* — Builder comment: 'APKWS II-ER: the medium-range strike guided rocket (user ask). The Apache mod's M282 APKWS with its launch envelope extended 3.5 -> 8 nm - in this engine range is the MaxLaunchRange key, there is no separate flight-time knob. No new art: rocket, pod, meshes and effects are the Apache mod's own, byte-identical but for th…
  
  Effect: A laser-guided 70mm rocket usable from 8 nm instead of 3.5 nm — precision strike at rocket cost, on a new id so no existing fit changes.
  
  If the donor changes: The round's art resolves through the Apache mod's material folders and vanilla weapons/usn_hydra70; without 3425450153 the carrying aircraft files are gone anyway.

- **The specific 8 nm figure for APKWS-ER.**  
  ***UNSTATED*** — No comment, commit or doc records where 8 nm comes from. The only recorded framing is 'the medium-range strike guided rocket (user ask)' and the encyclopedia text written to match it ('An uprated motor stretches the launch envelope from 3.5 to 8 nautical miles'). There is no real APKWS-ER performance figure cited.
  
  Effect: Sets the engagement range the player actually gets.
  
  If the donor changes: n/a — a literal in the builder.

- **Rebase the AGR-30 Redback onto dts_apkws-ii (Dingtools Weapon Pack) with five changed lines, abandoning the M282-derived build.**  
  *In-game observation* — Builder comment: 'rebased onto dts_apkws-ii after two freezes. The M282-based build differed from every working pod round in dozens of keys; dts_apkws-ii is a PROVEN in-pod rocket WITH loft keys from the collection's own weapon pack, so the Redback is now that file with the minimum deltas'. Commit 8630630: 'The M282-based build froze the…
  
  Effect: The Redback exists and the game does not hang when a pod carrying it is loaded.
  
  If the donor changes: Hard art dependency on 3760871384: sest_agr-30.ini keeps 'ResourcesFolder=assets/models/weapon/ammunition/apkws/' + 'ResourcesRoot=dts_apkws_ii.obj', which resolve into the Dingtools mod. U…

- **Give the Redback GuidanceType=1 (imaging IR) and leave MidCourseCorrection=0 — pure fire-and-forget — rather than the active-radar recipe first tried.**  
  *Engine precedent* — Builder comment: 'IR seeker instead of laser (GuidanceType 1, MidCourseCorrection stays 0 - pure fire and forget, five in-container precedents)'. Commit 746a5c6: 'A collection-wide survey (all 130 mods) found NO container anywhere holding a GuidanceType=3 round: active radar inside a pod is unprecedented in this engine and implicated in …
  
  Effect: 28 fire-and-forget rounds per aircraft with no datalink or designation requirement.
  
  If the donor changes: Guarded by exact-match swaps against dts_apkws-ii; any upstream change to those five lines fails the build loudly.

- **Redback performance deltas: MaxLaunchRange 6 -> 15 nm, SeekerPassiveRange 6.0 -> 8, MaxLoftAngle 5.0 -> 12.0, MaxLoftAlt 1500 -> 4000; motor, fuze, effects and terminal logic untouched.**  
  ***UNSTATED*** — The mechanism is stated ('range 6 -> 15 nm, loft raised 5/1500 -> 12/4000 for the higher profile. Motor, fuze, effects, terminal logic all stay the working weapon's') but no authority is given for 15 nm / 8 nm / 12 deg / 4000 ft. The weapon is explicitly fictional — the language file calls it a 'What-if evolution of the 70mm guided rocke…
  
  Effect: A 28-round fire-and-forget salvo out to 15 nm from a rocket pod — missile reach at rocket ammo cost.
  
  If the donor changes: Literals in build_patch.py's `swaps` list; each exits the build if it does not match upstream exactly once.

- **Roll the Redback out to six further airframes (3 Apaches, the naval AH-64NA, the A-10C, both MQ-9s) by cloning each carrier's own densest rocket or strike fit rather than authoring new stat…**  
  *Player directive* — Builder comment: 'Redback rollout (user ask): the other Apaches, the A-10C, and the MQ-9s. ... Each carrier clones its own densest rocket (or strike) fit with the pods swapped in, seats preserved.' Matches design-notes.md's 'Derive, don't invent. New loadouts clone a donor block the mod's author already proved (same stations, hide lists,…
  
  Effect: Each aircraft gains ONE extra loadout appended to AvailableLoadouts (verified, e.g. usa_a-10c.ini line 144 now ends ',SEST_REDBACK'); all original fits are untouched. Self-defence stations …
  
  If the donor changes: Ten upstream aircraft files are now whole-file overrides owned by this pack; upstream edits to any of them are silently hidden until the next re-export and diff (design-notes: 'Upstream mov…

- **For the naval AH-64NA, pick the donor fit dynamically as the block carrying the most usn_agr-20b stores instead of naming one.**  
  *File semantics* — In ROLLOUT the AH-64NA entry passes donor=None, and the builder computes 'densest fit by the first swap pattern', exiting with 'no donor fit carries the base rockets' if none does. Commit a4d3c1c: 'the naval Apache (densest-fit donor picked dynamically)'.
  
  Effect: The naval Apache's Redback fit gets 3 pods (its densest rocket block) rather than a forced 4.
  
  If the donor changes: If upstream renames or restructures its fits, the search either finds a new densest block or exits loudly.

- **On both MQ-9s, replace BOTH the Hellfire rails and the GBU-49 stations with rocket pods, hanging the LAU-68 pod on the AGM-114 position key.**  
  ***UNSTATED*** — The swap is explicit — (r'^(Station\d+=)uav_agm-114k\|AGM-114$', r'\1sest_agr-30_pod|AGM-114', 2) and (r'^(Station\d+=)uav_gbu-49$', r'\1sest_agr-30_pod', 2) — and commit a4d3c1c notes 'both MQ-9s (Strike donor, Hellfire rails and GBU stations re-podded, 4 pods each)'. What is NOT recorded is any check that a LAU-68 pod renders correctly…
  
  Effect: The Reaper gains an alternative fit of 4 pods / 28 guided rockets in place of 2 Hellfires + 2 GBU-49s; its original Strike fit remains available.
  
  If the donor changes: Two whole-file overrides of 3503670861. Guarded by exact swap counts, so an upstream station change fails the build.

- **Only the Redback travels; the laser APKWS-ER stays exclusive to the Ocean Apache.**  
  ***UNSTATED*** — Builder comment states the rule without a reason: 'Only the Redback travels - the laser APKWS-ER stays on the Ocean Apache.' Commit a4d3c1c repeats it as an assertion: 'Laser APKWS-ER stays Ocean-Apache-only.' No gameplay or realism argument is recorded.
  
  Effect: Six of the seven Redback carriers get no extended-range laser rocket option.
  
  If the donor changes: n/a — a scoping choice in the builder.

- **Name the two new rounds and two new loadouts through language_en merge files rather than by editing any mod's language file.**  
  *File semantics* — The pack ships language_en/ammunition_names.ini and loadout_names.ini with only its own keys (sest_apkws_er, sest_agr-30, SEST_APKWS_ER, SEST_REDBACK). design-notes.md: 'systems/ and language_*/ merge key-by-key ... Language merging is how packs rename other mods' units without owning the file.'
  
  Effect: Encyclopedia entries and picker names appear for the new stores; no other mod's names are lost.
  
  If the donor changes: Harmless if a donor mod is removed — orphan keys simply go unused.

- **Guard every upstream line the patch touches and fail the build rather than silently producing a no-op patch.**  
  *File semantics* — Every edit is count-checked, e.g. sys.exit(f'{name}: no {MISSING} station lines left - upstream fixed it, drop this target'), 'rn_lph_ocean.ini: AircraftSupported line changed upstream ({n} matches)', 'uk_ah_mk_1: expected 4 rocket pods in the Strike donor', and stale outputs are deleted when an upstream mod is no longer exported ('remov…
  
  Effect: None directly; it is what stops a whole-file override from shipping a stale copy of somebody else's unit.
  
  If the donor changes: This is the mechanism by which upstream drift is detected at build time instead of in game.

- **Re-search the file AFTER editing AvailableLoadouts instead of holding a match offset across edits.**  
  *In-game observation* — Builder comment: '# search AFTER the AvailableLoadouts edit - held offsets go stale (the SEAD260 lesson).'
  
  Effect: Prevents a cloned block being spliced at the wrong offset, which would corrupt the aircraft file.
  
  If the donor changes: n/a — builder correctness.

- **The pack must outrank all seven donor mods; it ships inside the single consolidated SEST_Integration folder at the top of the Mod Manager order.**  
  *File semantics* — data/load-order.tokens.txt: 'INVARIANT: every SEST_* pack sits above every workshop mod. A SEST pack is a whole-file replacement of a workshop mod's unit file; if anything outranks it the patch silently does nothing.' SEST_Integration is line 8; the donors sit at lines 16 (3760871384), 17 (3606774881), 42 (3599752717), 61 (3602046770), 6…
  
  Effect: All ten overrides actually load. If the invariant breaks, the P-8 fit is empty again and the new loadouts vanish — silently.
  
  If the donor changes: Ordering is regenerated from the tokens file by tools/set-mod-order.ps1; the checker exits non-zero on violation.

- **Donor copy for the M282 clone: the Apache mod's usa_apkws_2_m282.ini, not the A-10C mod's same-named file.**  
  ***UNSTATED*** — Two mods ship ammunition/usa_apkws_2_m282.ini (3425450153 and 3459682829) and they are NOT identical — diff shows six differences including AmmoPoints=6 present only in the Apache copy, Penetration=Moderate vs moderate, TerminalDiveDistance=1000 present only in the Apache copy, MaxLaunchAltitude=6000 present only in the A-10C copy, and H…
  
  Effect: APKWS-ER's impact effects, ammo cost and dive keys follow the Apache variant, so it behaves slightly differently from the in-game M282 it is presented as a development of.
  
  If the donor changes: If the A-10C mod is unsubscribed nothing changes for this round (the pack ships its own copy); if the Apache mod is unsubscribed the carrying aircraft files disappear anyway.

**Must stay subscribed**

- 3606774881 U.S. Navy 2027 Capabilities mod (Prof_CH4OS) — REQUIRED. Supplies the P-8 airframe/model for usn_p8_2027.ini AND the replacement round usn_agm-84n. Without it both Poseidons' AntiShip fit points at an undefined store a…
- 3602046770 Boeing P-8 Poseidon (Kirameki) — REQUIRED for the second P-8; the pack ships only the .ini, the custom model lives in the mod.
- 3599752717 Euromod - Modern British Navy (5_12) — REQUIRED for HMS Ocean's hull and model; the pack ships only the patched rn_lph_ocean.ini. Its own catalog entry records the author's requirement: 'requires Euromod to work as int…
- 3425450153 AH-64 Apache (misaka) — REQUIRED. Supplies five overridden aircraft (uk_ah_mk_1, usa_ah-64a/d/e, usn_ah-64na) with their meshes, the M282 rocket and the LAU-68 pod both new rounds are cloned from, and the rocket-pod te…
- 3459682829 A-10C (misaka) — REQUIRED for usa_a-10c.ini's model and for the stores its other fits hang (Litening, ALQ-184, GBU-12, usn_agr-20b).
- 3503670861 General Atomics MQ-9 Reaper (MyGo!!!!!) — REQUIRED for both overridden Reaper files and their models.
- 3760871384 Dingtools Weapon Pack (dingtools) — REQUIRED but NOT reported by tools/check_dependencies.py. sest_agr-30.ini keeps the donor's asset path ('ResourcesFolder=assets/models/weapon/ammunition/apkws/', 'ResourcesRoot=dts_a…
- 3629144864 Euromod pack, 3426791311 F/A-18E/F, 3414146266 A-10 — REFERENCE dependencies reported by tools/check_dependencies.py (7 / 3 / 1 files): stores and aircraft ids hung by the untouched fits inside the files this pack over…

**Known limits**

- Engine has no flight-time knob for a rocket: 'in this engine range is the MaxLaunchRange key, there is no separate flight-time knob' — so 'extended range' is expressed purely as a range number.
- No container anywhere in the 130-mod collection holds a GuidanceType=3 (active radar) round; that recipe hung the game and was abandoned. Pod rounds are effectively limited to the guidance patterns already proven in-container.
- sest_apkws_er inherits TerminalDiveDistance=1000 from the flat-flying M282 and has no loft keys — inert there, but it is the same key that froze the Redback once loft was added (commit 4ba7d54: 'the rocket inherited TerminalDiveD…
- The pack ships .ini files only — no models, textures or asset bundles (tools/check_dependencies.py: 'The packs ship 99 files and every one is a .ini ... it means NO pack is standalone'). All ten unit overrides and both new rounds…
- Ten whole-file overrides mean upstream edits to those aircraft/vessel files are hidden until a re-export and diff; design-notes.md records this as a live hazard ('Upstream moves under you ... A shadowed file can receive author up…
- The Redback and APKWS-ER are explicitly fictional ('What-if evolution of the 70mm guided rocket family'), so their numbers cannot be checked against any real specification.
- The MQ-9 Redback fit trades the Strike fit's 2x Hellfire + 2x GBU-49 for 4 rocket pods; it is an additional loadout, so the original Strike fit is still selectable.

### `ran-fleet`

Gives the collection a playable Royal Australian Navy — 7 classes, 26 named hulls — without fighting any mod for a filename: every hull is a NEW unit id cloned from the European design the real RAN ship is actually built to (or a stated stand-in), so the Spanish/British donor fleets and the RAN fleet coexist and no whole-file override is taken.


**Files (16)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3731208477 — Euromod - Modern Spanish N… | Not a contested filename — no mod in mods-source/ ships ran_ddg_hobart.ini (verified: `ls mods-source/*/vessels/ran_ddg_hobart.ini` returns nothing),… |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3731208477 — Euromod - Modern Spanish N… | Builder comment: 'keep the donor's [General] block (texture/reference wiring must match the donor mesh), then emit Australian variants with clean hul… |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3599752717 — Euromod - Modern British N… | Stated stand-in, not a parent design: 'the Type 23 MLU stands in for the MEKO 200 Anzac (no MEKO in the collection)'. Absence verified — no file matc… |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3599752717 — Euromod - Modern British N… | Same [General]-preservation rule; NumberOfVariants set to 8 for the eight HMAS hulls. |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3731208477 — Euromod - Modern Spanish N… | Parent design, not a stand-in — the Canberra class is the Juan Carlos I design. Uncontested id. |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3731208477 — Euromod - Modern Spanish N… | [General] preserved, NumberOfVariants=2 (Canberra, Adelaide). |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3731208477 — Euromod - Modern Spanish N… | Stated stand-in: 'the Galicia-class LPD stands in for the Bay-class'. No Bay-class LSD exists in mods-source (the only *bay* hits are merchant ships,… |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3731208477 — Euromod - Modern Spanish N… | [General] preserved, NumberOfVariants=1. |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3630495619 — Euromod - Cold War Spanish… | Stated stand-in: 'the Teide-class oiler stands in for the Cantabria-derived Supply-class (no Cantabria in the collection)'. Absence verified — no *ca… |
| `/home/user/Seapower-mods/integration/ran-fleet/SEST…` | adds | 3630495619 — Euromod - Cold War Spanish… | [General] preserved, NumberOfVariants=2 (Supply, Stalwart). |

*…and 6 more.*

**Decisions (22)** — File semantics 10, UNSTATED 4, Real-world spec 2, Comparison 2, Engine precedent 2, Upstream donor 1, Player directive 1


- **Build the RAN as new unit ids cloned from donors rather than overriding any donor file — the donors stay untouched and both fleets appear in the editor.**  
  *File semantics* — build_fleet.py docstring: 'Clones are NEW unit ids — nothing overrides the donors, so both fleets coexist.' Verified: none of ran_ddg_hobart / ran_ffh_anzac / ran_lhd_canberra / ran_lsd_choules / ran_aor_supply / ran_ssg_collins / ran_opv_arafura exists in any mods-source/*/vessels/ or submarines/ folder, and tools/check_dependencies.py …
  
  Effect: Australia gains 7 selectable classes / 26 named hulls; the Spanish and British fleets are unchanged and still selectable.
  
  If the donor changes: Nothing to restore on removal — deleting the pack removes only its own units. But because the pack ships .ini only and no meshes, unsubscribing a donor mod leaves the clone pointing at geom…

- **Hobart-class DDG and Canberra-class LHD are cloned from their real parent designs (F-100 Alvaro de Bazan, Juan Carlos I) rather than approximated.**  
  *Real-world spec* — Docstring: 'The RAN sails European designs, so the clones are honest: Hobart-class = the Spanish F-100 (ae_ffg_alvaro_bazan), Canberra-class LHD = Juan Carlos I'. README calls both '(the actual parent design)'.
  
  Effect: Hull form, sensors (SPY-1D(V)/Aegis), and layout are genuinely the RAN ship's, not a lookalike.
  
  If the donor changes: Loses both hulls if 3731208477 Euromod - Modern Spanish Navy is unsubscribed.

- **Five classes are declared STAND-INS, and the substitution is stated in the in-game description text rather than hidden: Anzac<-Type 23 MLU, Collins<-S-80, Choules<-Galicia, Supply<-Teide, A…**  
  *Comparison* — Each FLEET entry's 'desc' names the substitution and the reason, e.g. Anzac: 'Stand-in hull: the Type 23 MLU stands in for the MEKO 200 Anzac (no MEKO in the collection) — comparable size, towed array, point-defence SAM and a single helicopter.' Supply: '(no Cantabria in the collection)'. The absence claims check out: mods-source/ contai…
  
  Effect: Player sees an honest label in the vessel list; performance is the donor's, not the real RAN ship's.
  
  If the donor changes: Anzac needs 3599752717 (Modern British Navy); Supply needs 3630495619 (Cold War Spanish); the other three need 3731208477.

- **Replace the donors' placeholder Harpoon (usn_rgm-84d) with NSM on both Hobart and Anzac, using Red Storm Arsenal's usn_rgm_184a.**  
  *Comparison* — build_fleet.py: 'NSM - replaced Harpoon on Anzac and Hobart from 2024... Chosen over Euromod's knm_nsm_1a and the Type 23's rn_nsm by comparison: same airframe numbers as the knm round but MidCourseCorrection=3 (Datalink) vs 1 and a 10 ft skim vs 12; rn_nsm is far weaker (110 nm, Power 30, no datalink).' Every number verified in the roun…
  
  Effect: 8 deck-launched NSM per Hobart/Anzac with datalink mid-course and a lower sea-skim — a materially better anti-ship round than the placeholder Harpoon.
  
  If the donor changes: usn_rgm_184a is sole-sourced by 3413868677 Red Storm Arsenal (verified: only mods-source/3413868677/ammunition/usn_rgm_184a.ini exists). Unsubscribe RSA and both ships lose their anti-ship …

- **Keep the donors' MK141 launcher SystemName when swapping Harpoon->NSM instead of renaming or re-modelling the mounts.**  
  *File semantics* — build_fleet.py: 'The MK141 racks stay - SystemName refers to a systems/ launcher definition, and the NSM deck launchers replace Harpoon's 1:1 anyway.' Consistent with design-notes.md's rule that systems/ merges key-by-key rather than being owned by one mod.
  
  Effect: Visually unchanged deck canisters; round count unchanged (1:1).
  
  If the donor changes: None — no systems/ file is shipped by this pack.

- **Convert Hobart's Mk41 magazine module 6 from SM-2 to 8x Tomahawk (usn_rgm-109e5a), leaving 32 ESSM + 32 SM-2.**  
  *Engine precedent* — build_fleet.py: 'Module 6 converts to 8x usn_rgm-109e5a, the exact magazine pattern Modern US Navy's 2025 Burkes and Ticos use for the same round. 32 ESSM + 32 SM-2 stay - she is an air warfare destroyer first.' Precedent verified in 3390330875 Modern US Navy: usn_ddg_burke_f1_2025.ini:2516-2519 and usn_cg_ticonderoga_vls_2025.ini:1985-1…
  
  Effect: Hobart gains a land-attack cruise-missile capability (8 rounds) at the cost of 8 SM-2.
  
  If the donor changes: usn_rgm-109e5a comes from 3629144864 Euromod - Main Pack; drop it and the cells are empty. Modern US Navy is precedent only, not a dependency.

- **Convert Hobart's Mk41 module 5 from SM-2 to 8x SM-6, using the id usn_rim-174a.**  
  *Upstream donor* — build_fleet.py: 'SM-6 in module 5 - the RAN's approved Aegis refresh, and the same SM-2/SM-6/ESSM/TLAM/NSM pattern Red Storm Arsenal's own 2026 Hobart (ran_ddg_hobart_alt_late) carries. U.S. Navy 2027's usn_rim-174a wins the id. Final cells: 32 ESSM, 24 SM-2, 8 SM-6, 8 Tomahawk.' Verified: mods-source/3413868677/vessels/ran_ddg_hobart_al…
  
  Effect: 8 long-range SM-6 rounds — extended-range AAW and a secondary anti-ship shot — replacing 8 SM-2.
  
  If the donor changes: The clone names the collection-standard hyphenated id, not RSA's underscore variant, so it survives an RSA update; but it will silently take whichever usn_rim-174a wins if the load order mo…

- **Apply the armament refresh as a table of (regex, replacement, exact expected substitution count) and abort the build on any count mismatch.**  
  *File semantics* — build_fleet.py: 'Each entry: (regex, replacement, exact expected substitutions) - a count mismatch fails the build rather than shipping a half-applied refresh', implemented in refresh_armament() as `sys.exit(f"{ship_id}: armament refresh made {n} substitution(s), expected {want} - donor layout changed, re-check")`. Commit 060552a records…
  
  Effect: None directly — it prevents a silently half-armed ship after an upstream donor edit.
  
  If the donor changes: If a donor mod rearranges its magazines, the next rebuild fails loudly instead of emitting a broken hull; the already-shipped pack files are unaffected until rebuilt.

- **Every hull gets Nation=Australia, FlagTexture=flag_australia, and a transparent hull-number texture instead of the donor's national pennants.**  
  *Engine precedent* — DEFAULT_VARIANT constant in build_fleet.py. The transparent-pennant wiring is not invented — the donor's own [Default] block already reads 'ResourcesHullnumberFolder=textures/Misc/' + 'HullnumberTexture=transparent' (ae_ffg_alvaro_bazan_variants.ini:10-14); only FlagTexture and Nation are changed. flag_australia is an established id: van…
  
  Effect: Australian ensign flies; no Spanish/British pennant numbers appear on RAN hulls — but no Australian pennant numbers appear either, the sides are blank.
  
  If the donor changes: Depends on the base game shipping flag_australia, not on any mod.

- **Keep the donor variants' [General] block verbatim (only NumberOfVariants is rewritten) but drop every per-variant Emblem/Livery texture reference.**  
  *File semantics* — build_fleet.py comment: 'Variants: keep the donor's [General] block (texture/reference wiring must match the donor mesh), then emit Australian variants with clean hull numbers.' The builder hard-fails if the block is missing: `sys.exit(f"{ship_id}: [General] block not found in donor variants")`. Effect measured: rn_ff_type23_mlu_variants…
  
  Effect: All hulls of a class share the donor's base hull texture with no squadron emblem — visually uniform sisters.
  
  If the donor changes: None — self-contained in the emitted variants file.

- **Replace the donor [AirGroup] block outright but APPEND to AircraftSupported rather than replacing it, on the four aviation-capable hulls (Hobart, Anzac, Canberra, Choules).**  
  *Player directive* — README: 'Frigate/destroyer/LHD AircraftSupported lists are extended so MH-60R and S-70B-2 can cross-deck anywhere in the fleet.' Implementation is an append: `re.subn(r"^(AircraftSupported=.*)$", rf"\1,{HELOS}", ...)`. Result, e.g. ran_lhd_canberra.ini:158 = 'spa_ab212,spa_av-8b_plus,spa_md500,spa_sh-3d,spa_sh-60b,spa_sh-60b_block1,usn_m…
  
  Effect: MH-60R and S-70B-2 spawn on and can cross-deck to any of the four; the donors' Spanish/British/French types (AB-212, SH-3D, Sea Lynx, Merlin, AV-8B+) remain manually selectable on RAN decks.
  
  If the donor changes: MH-60R comes from whichever mod wins usn_mh-60r; S-70B-2 comes solely from 3403661005.

- **Canberra's air group is helicopters only (4x MH-60R + 4x S-70B-2) — no fixed wing.**  
  *Real-world spec* — FLEET desc: 'The RAN operates no fixed-wing aviation from them — the air group is MH-60R and S-70B-2 Seahawks.' README repeats it: '(no fixed-wing — RAN LHDs fly helicopters only)'. Enforced only in the [AirGroup] block (ran_lhd_canberra.ini:152-155).
  
  Effect: HMAS Canberra spawns with 8 helicopters and no Harriers.
  
  If the donor changes: Incomplete as an enforcement: the appended AircraftSupported line still carries the donor's spa_av-8b_plus, so a player can still manually load Spanish Harriers onto an RAN LHD. No note rec…

- **Class and hull names ride entirely on the merging language file; no DisplayClassName is forced into any vessel file.**  
  *File semantics* — build_fleet.py attempts the swap and degrades gracefully: `if n == 0: print(f"note: {donor} has no DisplayClassName line; relying on language names")`. Verified that this branch fires for all seven — `grep -n DisplayClassName integration/ran-fleet/SEST_RAN_Fleet/vessels/*.ini` returns nothing. design-notes.md: 'Language merging is how pa…
  
  Effect: 'Hobart-class DDG / DDG 39 HMAS Hobart' etc. appear in the vessel list; because language files merge, this coexists with the 35 other mods that ship language_en/vessel_names.ini.
  
  If the donor changes: If the language file were ever lost the hulls would fall back to raw ids — the vessel .ini files carry no display name of their own.

- **Validate every donor file, both helicopter ids, and both refresh rounds against mods-source/ before writing anything; collect all problems and exit once.**  
  *File semantics* — main() builds a `problems` list ('donor file missing', 'helo not found in any mod', 'armament refresh round missing') then `sys.exit("validation failed:\n " + ...)`. Commit 060552a: 'Round presence is validated up front, so an unsubscribed RSA or Euromod fails loudly at build time.' README: 'Validates donor files and helicopter ids again…
  
  Effect: None in game — it stops a pack being built against a collection that can no longer support it.
  
  If the donor changes: Note the helo check is deliberately loose — `MODS.glob(f"*/aircraft/{helo}.ini")` accepts ANY mod supplying usn_mh-60r, so it will not notice which of the four MH-60 sources actually wins.

- **Depend on usn_mh-60r without pinning a source mod, even though four mods in the collection ship an MH-60 family helicopter.**  
  ***UNSTATED*** — README lists 'an MH-60R source (US Naval Aviation)' — but by data/load-order.tokens.txt the id is won by 3606774881 U.S. Navy 2027 Capabilities (line 17), not 3737267013 United States Naval Aviation (line 59) or 3590477166 MH-60R Seahawk (line 96); tools/check_dependencies.py agrees, attributing the reference to 'U.S. Navy 2027 Capabilit…
  
  Effect: The Seahawk on an RAN deck is whichever mod currently outranks the others — its loadouts and sensors can change with a Mod Manager reorder, with no error.
  
  If the donor changes: Survives losing any one MH-60 source, but silently changes behaviour when their relative order changes.

- **Keep the author-deprecated S-70B-2 Seahawk mod (3403661005, Pog Frog) subscribed because this pack references it.**  
  *File semantics* — HELOS = 'usn_mh-60r,S-70B-2_Seahawk' in build_fleet.py; check_dependencies.py resolves it to 'references 1 file(s) S-70B-2 Seahawk with AGM-114 Hellfire Missiles (3403661005)'. Decision recorded in docs/conflicts-and-load-order.md:14 — 'Marked deprecated by its author | KEEP (revised 2026-08-23): SEST_RAN_Fleet and SEST_RAAF_Bases depend…
  
  Effect: Canberra/Adelaide keep their 4x S-70B-2 element; without it half the LHD air group vanishes.
  
  If the donor changes: An author-deprecated mod can be pulled from the Workshop at any time; the pack has no fallback helo and the build-time check would then fail with 'helo not found in any mod: S-70B-2_Seahawk…

- **Set the pack manifest to ApproximateVersion=0.8.2.**  
  *File semantics* — INFO_INI constant. Commit 673e50b: 'Every SEST pack declared ApproximateVersion=0.6.8 against a 0.8.x game. That check requires MAJOR and MINOR to match, so all seven packs were failing it. Now 0.8.2, matching the rebase sources.'
  
  Effect: Pack no longer flagged as version-incompatible by the Mod Manager.
  
  If the donor changes: Needs a bump when the game's minor version moves.

- **Read donor files as utf-8-sig rather than utf-8.**  
  *File semantics* — `(MODS / mod / "vessels" / f"{donor}.ini").read_text(encoding="utf-8-sig", errors="replace")`. Commit 41930a8: 'Two stray U+FEFF characters were typed into builder source literals and landed at the top of SEST_RAN_Fleet/language_en/vessel_names.ini... 74 exported upstream .ini files carry a UTF-8 BOM, and reading one with encoding="utf-8…
  
  Effect: A BOM at the head of a merged language file can break the first section header — this removes that class of failure.
  
  If the donor changes: Note the variants read at line ~230 still uses encoding="utf-8" (not utf-8-sig) — a BOM-carrying donor *_variants.ini would still splice one leading character, though the [General] regex to…

- **Give every hull of a class the same ServiceDate window, and no per-hull commissioning dates.**  
  ***UNSTATED*** — One 'service' string per FLEET entry, emitted into every [VariantN]: all 8 Anzacs read ServiceDate=1996|2045 (8 occurrences in ran_ffh_anzac_variants.ini), all 3 Hobarts read 2017|2055. No comment records why real per-hull dates were not used.
  
  Effect: In a 1998 scenario the editor will offer all eight Anzacs even though only Anzac and Arunta were in service.
  
  If the donor changes: Purely internal to the pack.

- **Leave all non-anti-ship armament as the donor's, with no note about the mismatch against real RAN fits.**  
  ***UNSTATED*** — The Anzac clone still carries eu_seawolf_GWS26 (Sea Wolf), rn_cal_114mm (4.5in Mk8) and rn_stingray_mod1_ship — the real ship has ESSM, a 5in Mk45 and Mk46/54. The Collins clone carries ger_dm2a4 torpedoes and spa_saes_mine — the real boat carries Mk48 CBASS. The ARMAMENT_REFRESH table touches only ran_ddg_hobart and ran_ffh_anzac, and o…
  
  Effect: RAN frigates fight with British-pattern guns/SAM/torpedoes and RAN submarines with German torpedoes.
  
  If the donor changes: Any future refresh must extend the same guarded ARMAMENT_REFRESH table; the guards will catch a donor that has moved underneath it.

- **Do NOT switch the Hobart clone to Red Storm Arsenal's native RAN Hobart after discovering it — borrow only its magazine pattern.**  
  ***UNSTATED*** — Commit 6310c97: 'Found while surveying Red Storm Arsenal's unique files: its own 2026 Hobart (ran_ddg_hobart_alt_late) carries SM-2 + SM-6 + ESSM Blk 2 + Tomahawk + NSM - the RAN's actual approved Aegis refresh, and exactly the direction this clone was already headed.' The commit adopts the SM-6 cell but says nothing about why the F-100 …
  
  Effect: Two RAN Hobart lineages exist side by side in the editor if RSA is enabled — the pack's ran_ddg_hobart plus RSA's ran_ddg_hobart_alt_early/_alt_late. Menu clutter, not a conflict (different…
  
  If the donor changes: Nothing breaks either way; the ids do not collide.

- **Treat the pack's load-order position as forgiving, while the repo's canonical order nonetheless hoists it into the Tier 0 SEST block.**  
  *File semantics* — README/_info.ini: 'Place it below the Euromod packs in the Mod Manager (it only adds new units, so ordering is forgiving).' setup-runbook.md agrees: 'The two Australian content packs (SEST_RAAF_Bases, SEST_RAN_Fleet) only ADD new files — they conflict with nothing, so their position is forgiving.' But data/load-order.tokens.txt has only …
  
  Effect: None — because the pack takes no override, its rank cannot make it inert the way it did for the Growler pack.
  
  If the donor changes: The Tier 0 invariant is enforced by tools/check_load_order.py for packs that DO override; this one is carried along for free.

**Must stay subscribed**

- 3731208477 Euromod - Modern Spanish Navy (jabeitor) — MANDATORY: supplies the meshes for 5 of 7 classes (Hobart/F-100, Canberra/Juan Carlos I, Choules/Galicia, Collins/S-80, Arafura/Meteoro). Without it those five hulls are .ini …
- 3599752717 Euromod - Modern British Navy (5_12) — MANDATORY for the Anzac (Type 23 MLU mesh + its British gun/SAM/torpedo definitions). NOT detected by tools/check_dependencies.py, which sees only ammunition and roster references…
- 3630495619 Euromod - Cold War Spanish Navy (zzocalu) — MANDATORY for the Supply-class AOR (Teide mesh). The sole reason the pack lists BOTH Spanish packs. Also invisible to check_dependencies.py.
- 3629144864 Euromod - Main Pack (Mitchell600) — MANDATORY: shared European weapon/sensor database, plus the Tomahawk round usn_rgm-109e5a. check_dependencies.py: 'references 15 file(s)'. Its own addons' authors state the Euromod r…
- 3413868677 Red Storm Arsenal — MANDATORY for the anti-ship battery: sole source of usn_rgm_184a (NSM). Verified sole source. Sits LAST in data/load-order.tokens.txt deliberately ('Placed last so it loses all 13 [duplicated files]…
- 3606774881 U.S. Navy 2027 Capabilities (Prof_CH4OS) — de facto supplier of usn_rim-174a (SM-6) and, by load-order rank, of usn_mh-60r. check_dependencies.py: 'references 7 file(s)'.
- 3403661005 [DEPRECATED] S-70B-2 Seahawk with AGM-114 Hellfire (Pog Frog) — MANDATORY for the Canberra/Adelaide air group. Author-deprecated; explicitly kept for this pack (docs/conflicts-and-load-order.md, tools/generate_load_ord…
- 3390330875 Modern US Navy — NOT a dependency. Precedent only: its 2025 Burke/Ticonderoga TLAM magazine block is what the Hobart's module 6 was copied from.
- 3456859157 Mogami-class Frigate — no longer referenced by this pack. It used to win the placeholder usn_rgm-84d the clones inherited; commit 060552a: 'the Mogami reference disappeared with the placeholder it was winning'. (It is …

**Known limits**

- Not modeled, no donor available: Hunter-class FFG (README: 'no Type 26 in the collection — the Modern British pack stops at Type 23/45' — verified, no *type26* file in mods-source) and MRH-90 troop lift on the LHDs. README: 'Both…
- Five of seven classes are acknowledged stand-ins — hull, gun, SAM and torpedo performance are the European donor's, not the RAN ship's. The Anzac swims as a Type 23 with Sea Wolf and a 4.5in gun; the Collins as an S-80 with DM2A4…
- No Australian pennant numbers. Hull-number textures are set to 'transparent' (inherited from the donors' own [Default] block) because no RAN pennant textures exist in the collection; per-variant emblem and livery textures are dro…
- The Australian ensign is unverified in game. README: 'The Australian ensign relies on the game's flag_australia texture... If ships show a blank flag, tell me and I'll point the variants at whatever flag texture your build ships.…
- Canberra's fixed-wing exclusion is enforced only in [AirGroup]; spa_av-8b_plus remains in the appended AircraftSupported list, so Spanish Harriers can still be loaded manually onto an RAN LHD.
- The Arafura OPV gets no MH-60R/S-70B-2 — 'airgroup': None means its AircraftSupported line is never extended and still reads the donor's 'spa_sh-60b_block1,spa_ab212'. Plausible for a hangarless OPV, but unrecorded.
- usn_mh-60r is not pinned to a mod. Four sources ship an MH-60 family helo; whichever outranks the others supplies the RAN Seahawk, and the build-time check accepts any of them.
- Mesh/asset dependencies are invisible to tooling. tools/check_dependencies.py lists only Euromod Main, U.S. Navy 2027, Modern Spanish, RSA and the S-70B-2 mod for this pack — the British and Cold War Spanish donors do not appear,…
- The clones are frozen snapshots. A donor author fixing or rebalancing ae_ffg_alvaro_bazan.ini does not reach ran_ddg_hobart.ini until build_fleet.py is re-run (design-notes.md: 'Upstream moves under you... After any export, diff …
- The installed copy captured in mods-source/_vanilla/SEST_RAN_Fleet/ is stale relative to the built pack — 7 of its files differ, including ran_ddg_hobart.ini and ran_ffh_anzac.ini, i.e. it predates the NSM/SM-6/Tomahawk refresh a…
- The variants file is still read with encoding='utf-8' (not utf-8-sig) while the main hull file was fixed to utf-8-sig — a BOM-carrying donor *_variants.ini would leak one leading character.

### `b52-arrw`

Makes the AGM-183A ARRW behave like a boost-glide weapon and be carriable across every in-service B-52 in the collection, by rebasing the two Dingtools AGM-183A ammunition files (the copies that actually win the override race) with the loft keys they were missing, and by grafting ARRW/W62/LRASM loadouts onto the Dingtools B-52H and Red Storm Arsenal's B-52O using each aircraft's own proven donor blocks.


**Files (8)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `integration/b52-arrw/SEST_B52_ARRW/ammunition/dts_a…` | overrides | 3760871384 — Dingtools Weapon Pack (aut… | FOUR mods ship this exact filename — 3741944366 B-52H, 3636386513 F-15 EX Eagle II, 3652097318 B-1B Lancer and 3760871384 Dingtools Weapon Pack. The … |
| `integration/b52-arrw/SEST_B52_ARRW/ammunition/dts_a…` | overrides | 3760871384 — Dingtools Weapon Pack | Same four-way contest, same Dingtools tiebreak. Here all four upstream copies are byte-identical (md5 ac83e099e128bd121274697d6eed4318), so the donor… |
| `integration/b52-arrw/SEST_B52_ARRW/ammunition/usn_a…` | overrides | 3502273861 — ARRW (AGM-183) | Sole owner; no competing mod ships usn_arrw.ini. Catalog note confirms non-collision: "Adds its OWN AGM-183 ammunition - it does NOT collide with the… |
| `integration/b52-arrw/SEST_B52_ARRW/aircraft/dts_b-5…` | overrides | 3741944366 — B-52H Stratofortress (auth… | Sole owner of dts_b-52h.ini across all exported mods. The pack extends the author's own file rather than authoring a B-52H, so the mesh, station tabl… |
| `integration/b52-arrw/SEST_B52_ARRW/aircraft/usaf_b-…` | overrides | 3413868677 — Red Storm Arsenal | Sole owner of usaf_b-52o.ini. The B-52O is RSA-unique content (catalog: "Largest mod in the collection - 1062 files, 638 of them content nothing else… |
| `integration/b52-arrw/SEST_B52_ARRW/language_en/load…` | merges | n/a — pack-authored, 2 keys only | language_*/ files merge key-by-key, so the pack names only the keys it introduces (Strike183Nuke, AntiShipLRASM) and leaves the F-15EX/B-1B-owned Str… |
| `integration/b52-arrw/SEST_B52_ARRW/language_en/airc…` | merges | renames a unit owned by 3502273861 — AR… | Renames usaf_b-52h_419_flts without shipping (and therefore without overriding) the ARRW mod's aircraft file — the merge semantics are what make this… |
| `integration/b52-arrw/SEST_B52_ARRW/_info.ini` | adds | n/a — pack manifest | Pack identity consumed by tools/consolidate_packs.py when building integration/dist/SEST_Integration. |

**Decisions (21)** — In-game observation 5, Engine precedent 3, Upstream donor 3, File semantics 3, Comparison 2, UNSTATED 2, Real-world spec 2, Author mandate 1


- **Add a four-key loft block (MaxLoftAngle/MaxLoftAlt/IgnoreHeightDifferenceForTargetDist/TerminalVelocity) to both dts_agm-183a files, inserted immediately after SeaSkimmingAlt**  
  *Engine precedent* — build_patch.py:8-16: "Every other hypersonic weapon here pairs a high SeaSkimmingAlt (the cruise altitude) with a MaxLoftAlt (the boost apex): usn_cps 99000/90000, plan_yj21 99000/90000, plan_yj_17 92000/95000, usa_prsm 160000/160000, wp_ss-n-26 46000/46000. dts_agm-183a and dts_agm-183a(w62) are the ONLY two files in the collection carr…
  
  Effect: ARRW now boosts to a 90,000 ft apex and glides in instead of cruising flat at 90,000 ft with no climb phase; IgnoreHeightDifferenceForTargetDist stops the altitude counting against range at…
  
  If the donor changes: Nothing breaks structurally — the loft keys are additive to a Dingtools file. If the Dingtools Weapon Pack is unsubscribed, the pack's copy still loads (unit .ini) but points at Dingtools' …

- **Anchor the loft values on usn_cps (Red Storm Arsenal's Conventional Prompt Strike) rather than on the ARRW mod's own usn_arrw, and change nothing else in the Dingtools files**  
  *Comparison* — build_patch.py:18-24: "Anchored to usn_cps - the US Navy's own boost-glide round, which this collection already fields on the Zumwalt - rather than to the ARRW mod's usn_arrw. usn_arrw models the profile well but gets the hardware wrong: 850 kg against the real ~2270 kg, Power 45 against 300, and a MaxVelocity written '10,648' with a tho…
  
  Effect: The round keeps Dingtools' 2270 kg mass, Power 300 penetrator warhead, 5291 kt / 865 nm envelope — only the flight profile changes. Confirmed by diff: exactly four added lines per file, not…
  
  If the donor changes: usn_cps is RSA content, but only its VALUES were read at authoring time — the built pack carries no runtime dependency on RSA for the ammunition files.

- **MaxLoftAngle set to 45.0 — the one loft value deliberately NOT copied from usn_cps**  
  *Comparison* — build_patch.py:46-50: "MaxLoftAngle is the one value not copied straight across: CPS is surface-launched and needs a shallow 35 deg to reach its 1889 nm; ARRW is released above 40,000 ft and boosts steeply from there, so 45 sits between CPS and the ARRW mod's 75 without inventing range the weapon does not claim." Verified: usn_cps.ini Ma…
  
  Effect: A steeper boost than the surface-launched CPS but shallower than the ARRW mod's, so the round lofts without gaining range the Dingtools MaxLaunchRange=865 does not claim.
  
  If the donor changes: Self-contained constant in LOFT; no donor coupling.

- **TerminalVelocity set to 3800**  
  ***UNSTATED*** — build_patch.py:55 — `"TerminalVelocity": "3800",` carries no comment. The docstring at :47 explicitly claims "MaxLoftAngle is the one value not copied straight across", but usn_cps.ini has TerminalVelocity=3333 and usn_arrw.ini has TerminalVelocity=4000, so 3800 is a second uncopied value with no recorded justification. The commit messag…
  
  Effect: Sets the ARRW's terminal-dive speed to 3800 kt, ~14% above the CPS anchor's 3333 and just under the ARRW mod's 4000; affects intercept difficulty and impact behaviour.
  
  If the donor changes: One dict entry; no donor coupling. But nothing records what it was calibrated against, so a future editor has no basis to keep or change it.

- **Add a Strike183Nuke loadout (4x W62) to the B-52H by regex-cloning the existing Strike183 block and substituting only the round**  
  *Upstream donor* — build_patch.py:26-30: "dts_agm-183a(w62) ships in the B-52H mod's own folder, and the F-15EX and B-1B both have loadouts for it - but the B-52H, the only aircraft that ever actually flew ARRW, has none. Adding Strike183Nuke mirrors the existing Strike183 exactly: the same four pylon stations, the same position keys, the same SubModelsToH…
  
  Effect: B-52H gains a nuclear ARRW fit: 4x AGM-183A(W62) on the pylons plus 8x AGM-86B in the rotary.
  
  If the donor changes: Guarded three ways — sys.exit if the Strike183 pair is not found ("Strike183 not found in dts_b-52h.ini - upstream changed"), if it no longer carries dts_agm-183a, or if the W62 substitutio…

- **Raise the B-52H's two ARRW position keys from y=-0.003 to y=-0.002**  
  *In-game observation* — build_patch.py, build_aircraft(): "The rounds hung visibly below the pylon adapter in game (user screenshot, confirmed as the H specifically). Upstream seats both ARRW keys at y=-0.003; raise to -0.002." Output diff: AGM183FPositions/AGM183BPositions 0,-0.003,0.01 -> 0,-0.002,0.01. Enforced by a count guard: sys.exit if n != 2 ("expected…
  
  Effect: ARRW sits flush against the pylon adapter on the B-52H instead of floating below it.
  
  If the donor changes: If the author retunes those keys upstream the regex misses and the build fails loudly rather than silently shipping the old seat.

- **Fill the previously EMPTY Strike183 bomb bay on the B-52H from the aircraft's own Strike158 donor — Station6=dts_agm-158b-2|CSRL (8x JASSM-ER)**  
  *Upstream donor* — build_patch.py: "The bay was EMPTY on both ARRW fits - the block existed with nothing in it. Fill it from the aircraft's own donors: Strike158 proves the CSRL carries dts_agm-158b-2 (8x JASSM-ER, 800 nm) with this exact SubModelsToHide list". Verified in mods-source/3741944366/aircraft/dts_b-52h.ini: [WeaponSystem1Strike158] has Station6…
  
  Effect: Strike183 goes from 4 ARRW + empty bay to 4 ARRW + 8x JASSM-ER (CSRLPositions defines 8 slots).
  
  If the donor changes: Two guards: sys.exit if "Station6=dts_agm-158b-2|CSRL" disappears from the file, and sys.exit if the Strike183 bay stops being empty upstream ("Strike183 bay is no longer empty upstream - r…

- **The nuclear fits load usaf_agm-86b in the rotary rather than the conventional round**  
  *Real-world spec* — build_patch.py: "the nuclear fit takes usaf_agm-86b, the real nuclear ALCM (Power 1000, from the B-52G AGM-86 mod's own family)". Verified: mods-source/3394781441/ammunition/usaf_agm-86b.ini Power=1000 vs usaf_agm-86c.ini Power=64. Commit 5377653: "Strike183Nuke swaps the rotary to usaf_agm-86b, the actual nuclear ALCM (Power 1000), keep…
  
  Effect: Strike183Nuke on both bombers is nuclear end-to-end: W62 ARRW outside, 8x AGM-86B ALCM inside, instead of a nuclear pylon load over a conventional bay.
  
  If the donor changes: HARD DEPENDENCY: 3394781441 (B-52G with AGM-86) is the ONLY exported mod that ships usaf_agm-86b.ini — vanilla has usaf_agm-86c but not the B. Unsubscribing it leaves both Strike183Nuke bay…

- **Give the B-52O its OWN AGM183_Pylon position key instead of reusing RSA's RGM110_Rack key**  
  *In-game observation* — build_b52o() docstring: "First cut reused RSA's RGM110_Rack position key, on the theory that its large-hypersonic fit was the ARRW fit. In game the missile hung visibly below the pylon: that key's -0.0090 y-offset is tuned for the much fatter AGM-110L. The B-52H settles it - it flies the SAME round under the SAME pylon geometry (stations…
  
  Effect: ARRW sits flush on the B-52O's pylons; the key is injected next to the author's own in the WeaponSystem2 table so RSA's AGM-110L carriage is untouched.
  
  If the donor changes: sys.exit guards on "AGM183_Pylon already defined upstream" and on RGM110_RackPositions disappearing (used as the injection anchor). The whole build_b52o() step is skipped and its output del…

- **B-52O carries two ARRW per pylon nose-to-tail at 0.082 z-separation (aft z=-0.02, forward z=+0.062) — the third calibration of the same value**  
  *In-game observation* — build_b52o() docstring: "the height checked out in game; the separation has been widened twice on screenshots - the H's 0.0457 was too tight, 0.0677 still lapped the forward round's fins - and now sits at 0.082 nose-to-tail. Two per pylon, four per loadout." Commit trail matches exactly: 8f65dc9 (z+0.01/z+0.0557 = 0.0457), d8f836b ("the …
  
  Effect: 4x ARRW visible and non-overlapping on the B-52O, matching the B-52H's warload.
  
  If the donor changes: Pack-authored key; independent of upstream retuning. Note the recorded H reference figure is questionable — see known_limits.

- **Deliberately do NOT use the B-52O's WeaponSystem1 wing pylons (Station7/8) for ARRW**  
  *Author mandate* — build_b52o() docstring: "Its WeaponSystem1 wing pylons (Station7/8) are deliberately NOT used - the matching #RGM110_RackPositions there is commented out in RSA's own file, so the author disabled that carriage and second-guessing it would put missiles at an offset nobody has ever looked at." Verified in mods-source/3413868677/aircraft/us…
  
  Effect: Caps the B-52O ARRW warload at 4 external rather than 8 — an accepted ceiling rather than a guess at untested geometry.
  
  If the donor changes: No coupling; the constraint is purely a decision not to touch a block.

- **Fill the B-52O's three new bomb bays from its own Standoff donor, with "Pylons" stripped from SubModelsToHide**  
  *Upstream donor* — build_patch.py: "Bay: the O's own Standoff donor - a CSRL of AGM-86 - minus 'Pylons' from its SubModelsToHide, because unlike Standoff our fits hang ARRW out there." Implemented as `bay = sd.group(1).replace("SubModelsToHide=Pylons,", "SubModelsToHide=")`, guarded by sys.exit if "Station6=usaf_agm-86c|CSRL" is gone from [WeaponSystem1Sta…
  
  Effect: Strike183 = 4 ARRW + 8x AGM-86C; Strike183Nuke = 4 W62 + 8x AGM-86B; AntiShipLRASM = 8 LRASM external + 8x LRASM in the rotary. Keeping "Pylons" would have hidden the very pylons the extern…
  
  If the donor changes: Guarded on the Standoff donor block; hard dependency on 3394781441 for both AGM-86 variants (usaf_agm-86c also exists in vanilla, usaf_agm-86b does not).

- **AntiShipLRASM gets its own LRASM_Pylon key — the Harpoon rack's frame with the centre column dropped and the cant removed — instead of reusing AGM84_Pylon**  
  *In-game observation* — build_b52o() body comment: "The first cut reused AGM84_Pylon - the Harpoon six-pack - and in game the fat LRASM airframes read as a Harpoon cluster. LRASM_Pylon keeps the Harpoon rack's proven x/z frame but drops its centre column: the four corner positions only, uncanted, at the centre row's hang height. Four per pylon, eight external, …
  
  Effect: Warload dropped from 12 external to 8 external LRASM so the rounds read as individual missiles, not a cluster; total 16 dts_agm-158c-3.
  
  If the donor changes: Pack-authored key; guarded by sys.exit if "LRASM_Pylon" ever appears upstream. Requires a Dingtools-family mod for dts_agm-158c-3 (Dingtools Weapon Pack wins that file too).

- **Fix usn_arrw's MaxVelocity=10,648 to 10648**  
  *Engine precedent* — build_419_flts() docstring: "It declares MaxVelocity=10,648 - the ONLY numeric value carrying a thousands separator anywhere in the ammunition of all 129 exported mods. Nothing else in the collection writes a number that way, so it is a typo, and a parser reading it as 10 knots leaves the round crawling." Verified: mods-source/3502273861…
  
  Effect: The ARRW mod's own round flies at 10,648 kt instead of whatever a comma-truncating parser yields (potentially 10 kt).
  
  If the donor changes: If 3502273861 is unsubscribed, build_419_flts() prints "usn_arrw.ini SKIPPED - ARRW mod not exported" and drop_stale() deletes the shipped copy.

- **REVERSED an earlier decision: do NOT declare Empty/Default in the 419th FLTS testbed's AvailableLoadouts, and delete the aircraft file the pack used to ship for it**  
  *Engine precedent* — build_419_flts() docstring: "NOT touched: this aircraft's AvailableLoadouts. An earlier version of this script declared Empty and Default here, on the reasoning that the blocks existed but were unreachable. That was wrong. Vanilla's own usn_f-14a and usaf_b-52g do not declare them either and plainly have them in game, and 95 of 135 allie…
  
  Effect: No change to the 419th FLTS aircraft's loadouts; avoids a possible duplicated Default/Empty entry in the loadout picker.
  
  If the donor changes: Nothing to revert — the pack no longer overrides that file at all, so the ARRW mod's own aircraft loads unmodified.

- **Rename the ARRW mod's usaf_b-52h_419_flts via a language merge rather than by shipping its aircraft file**  
  *In-game observation* — write_language() docstring: "The mission editor's type list showed two entries both reading 'B-52H': the Dingtools dts_b-52h this pack extends, and usaf_b-52h_419_flts - the ARRW mod's separate test aircraft with its own single-loadout assortment. It looked like a broken duplicate. Language files merge key-by-key, so one entry renames it…
  
  Effect: The two B-52Hs are distinguishable in the mission editor; the ARRW mod keeps full ownership of its aircraft file.
  
  If the donor changes: Harmless if the ARRW mod is unsubscribed — an orphan language key names nothing. This is the file-semantics payoff described in design-notes.md: "Language merging is how packs rename other …

- **Name only the two NEW loadout keys; leave Strike183 to its upstream name**  
  *File semantics* — Shipped comment in language_en/loadout_names.ini: "only keys this pack introduces; Strike183 keeps its upstream name because the F-15EX also declares that key and loadout names are a GLOBAL key->name table." Verified: mods-source/3636386513/language_en/loadout_names.ini:10 `Strike183=StrikeARRW` and 3652097318 the same. tools/consolidate…
  
  Effect: The B-52H/B-52O ARRW fit displays as "StrikeARRW" (the F-15EX author's string); the new fits display as "SEST Strike183 Nuclear (W62 + AGM-86B)" and "SEST AntiShip LRASM (8+8)".
  
  If the donor changes: Renaming Strike183 here would silently rename the F-15EX's and B-1B's fits too — this is the trap README.md documents ("two unprefixed keys were silently fighting over display strings in-ga…

- **Loadout keys Strike183Nuke and AntiShipLRASM shipped UNPREFIXED, against the repo's own stated rule**  
  ***UNSTATED*** — README.md, "Adding a pack" step 3: "Loadout-name keys are global across mods: prefix yours (`SEST_...`) or the consolidator will fail the build on the first clash". This pack uses bare `Strike183Nuke=` and `AntiShipLRASM=`, while sibling packs comply — integration/f-15ex-revamp uses `SEST_AntiShipLRASM6`, integration/rafale-f5 uses `SEST…
  
  Effect: None today. A future subscription declaring either key would collide over the global display string, and consolidate_packs.py only detects clashes BETWEEN SEST packs — never against a works…
  
  If the donor changes: Renaming the keys means renaming them in the aircraft AvailableLoadouts and both [WeaponSystemN...] section headers too.

- **B-52D and B-52G deliberately excluded from the ARRW rollout**  
  *Real-world spec* — Commit 13c46cf: "Five B-52s are in play: usaf_b-52d and usaf_b-52g (vanilla, the G overridden by 3394781441), dts_b-52h, usaf_b-52h_419_flts from the ARRW mod, and usaf_b-52o from Red Storm Arsenal… B-52D and B-52G are deliberately not included: they retired in 1983 and 1994 and ARRW is a 2020s weapon. Easy to add if wanted." Reflected i…
  
  Effect: The two retired airframes stay period-correct and unpatched; the vanilla B-52G's AGM-86 mod override is left alone.
  
  If the donor changes: n/a — no files touched.

- **drop_stale(): delete pack output whose upstream mod is no longer exported, rather than just skipping the build step**  
  *File semantics* — drop_stale() docstring: "Skipping the build of a file does not unship the copy from last time. A stale unit .ini left behind after its mod is unsubscribed describes a unit whose model is gone - the same trap as mods-source keeping directories for mods you removed." Commit 13c46cf records the negative test: "Tested by moving Red Storm Ars…
  
  Effect: Unsubscribing RSA or the ARRW mod cleanly removes the corresponding pack content instead of leaving an aircraft definition pointing at a missing mesh.
  
  If the donor changes: This IS the reversibility mechanism — but note it only fires when the builder is re-run, and only the RSA and ARRW paths have it. The B-52H (3741944366) and Dingtools (3760871384) paths sys…

- **Every transform is a regex against a located donor block with a hard sys.exit guard, never a hand-edit**  
  *File semantics* — Eleven distinct sys.exit guards in build_patch.py, each naming the upstream assumption it protects: "Strike183 not found in dts_b-52h.ini - upstream changed", "Strike183 no longer carries dts_agm-183a - re-check by hand", "expected 2 ARRW position keys to raise, got {n}", "Strike183 bay is no longer empty upstream - re-check", "AntiShipH…
  
  Effect: Indirect: an upstream author update that would invalidate a graft fails the build (and the repo's `build_all.py --from-scratch` + clean-git-status regression gate) instead of silently shipp…
  
  If the donor changes: The guards are what make a donor update recoverable — but they also mean any donor change blocks the whole consolidated build until a human re-checks.

**Must stay subscribed**

- 3760871384 — Dingtools Weapon Pack: the donor for both AGM-183A ammunition files and the winning owner of dts_agm-158b-2 / dts_agm-158c-3. Must stay subscribed AND stay above the other dingtools mods (author: "Put this mod ABOVE …
- 3741944366 — B-52H Stratofortress (dingtools): sole owner of dts_b-52h.ini and the B-52H mesh. The pack overrides that file whole; no skip/drop_stale branch exists for it, so unsubscribing leaves a stale aircraft definition until…
- 3413868677 — Red Storm Arsenal: sole owner of usaf_b-52o.ini and the B-52O model, plus usn_agm_110l / usn_agm_84n / usn_agm_109b that the overridden file still references. Optional at build time — build_b52o() prints "usaf_b-52o.…
- 3502273861 — ARRW (AGM-183): sole owner of usn_arrw.ini and of usaf_b-52h_419_flts (the aircraft the language file renames). Optional at build time — skipped + drop_stale.
- 3394781441 — B-52G with AGM-86 (realistic nuke): the ONLY exported mod shipping usaf_agm-86b.ini (vanilla has 86c but not 86b). Both Strike183Nuke bomb bays and the B-52O's Strike183 bay reference it. Unsubscribing it breaks thre…
- 3426791311 — F/A-18E/F and 3395022688 — Tu-95MS with AS-15 ALCM: INHERITED references, not chosen ones. Because usaf_b-52o.ini / dts_b-52h.ini are whole-file overrides, the pack also owns their references to usn_mk-82 / usn_mk-84…
- SEST_Integration must remain the single tier-0 entry above every workshop mod (data/load-order.tokens.txt INVARIANT, enforced by tools/check_load_order.py). If anything outranks it, all five overridden files silently revert.

**Known limits**

- STALE MANIFEST: _info.ini still advertises "…and the 419th FLTS testbed's unreachable loadouts declared", but that change was reversed (build_419_flts docstring: "That was wrong") and drop_stale actively deletes aircraft/usaf_b-5…
- QUESTIONABLE RECORDED FIGURE: build_b52o()'s docstring justifies the B-52O carriage by saying the B-52H "carries TWO per side nose-to-tail at 0.0457 of z-separation". The B-52H's Strike183 actually uses Station3/4 (z=0.115, y=-0.…
- Rebasing dts_agm-183a on the Dingtools copy discards the F-15EX mod's richer version of the same file (AccelerationTime=5 / Acceleration=9.4 / SustainerAccelerationTime=25 / SustainerAcceleration=5.4 plus a 36 s initial phase, vs…
- B-52O ARRW warload is capped at 4 external (two per pylon on WeaponSystem2 only). The WS1 wing pylons are off-limits by author intent (#RGM110_RackPositions commented out), so 8 external is not available without inventing unteste…
- Loadout-name keys Strike183Nuke and AntiShipLRASM are global and unprefixed; consolidate_packs.py only detects clashes between SEST packs, never against a workshop mod, so a future subscription declaring either key would collide …
- The AntiShipLRASM external warload was deliberately reduced from 12 to 8 (commit 104c452) to stop LRASM rendering as a Harpoon cluster — a visual-fidelity trade accepted against raw capability.
- The pack ships only .ini files — no meshes, textures or asset bundles (tools/check_dependencies.py header: "NO pack is standalone"). Every donor mod above must remain installed for the overridden units to render.

### `raaf-bases`

Gives the collection's RAAF/allied aircraft somewhere Australian to operate from: 15 new Australian airbase land units, each a clone of the Modern US Airbase unit re-flagged to Australia and rostered from aircraft that other mods and sibling SEST packs define, so nothing new is modelled and no existing unit file is overridden.


**Files (5)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `SEST_RAAF_Bases/land_units/airbase_raaf_{williamtow…` | adds | 3592460366 — Modern US Airbase (author … | It is the only US/Western modern airbase land unit in the collection whose flight-deck block is known good, and its model block points at vanilla sce… |
| `SEST_RAAF_Bases/land_units/airbase_raaf_*_variants.…` | adds | none — hand-written VARIANTS_INI consta… | The donor's variants file is NumberOfVariants=2 / AllVariantsAreOfSameNation=false with [Default] Nation=US and [Variant2] Nation=Germany. The pack e… |
| `SEST_RAAF_Bases/language_en/land_units_names.ini` | merges | none (generated); shares its filename w… | language_*/ merges key-by-key (docs/design-notes.md: "systems/ and language_*/ merge key-by-key... Language merging is how packs rename other mods' u… |
| `SEST_RAAF_Bases/_info.ini` | adds | none (generated from the BASES table at… | Counts in the description ("15 Australian airbases... 258 aircraft in total") are computed, not typed: per commit f8aede5, "The pack description is g… |
| `integration/dist/SEST_Integration/land_units/airbas…` | merges | consolidation output of tools/consolida… | All SEST content deploys as one Mod Manager entry at Tier 0 (generate_load_order.py TIER0 comment: "They now deploy as ONE pack... so tier 0 is a sin… |

**Decisions (21)** — File semantics 7, Upstream donor 4, UNSTATED 4, In-game observation 2, Real-world spec 2, Author mandate 1, Player directive 1


- **Build every RAAF base by cloning Modern US Airbase's airbase_us.ini and replacing only the [AirGroup] block and DisplayClassName, keeping the donor's flight-deck geometry and Reykjavik mode…**  
  *Upstream donor* — build_pack.py docstring: "Each base clones the proven Modern US Airbase unit (which itself reuses the vanilla Reykjavik airbase scenery and flight-deck geometry) and swaps in RAAF identity and air groups." Implementation: text = template[:m.start()] + airgroup + template[m.end():] with re.sub(r"^DisplayClassName=.*$", ..., count=1). Veri…
  
  Effect: Every base has a working, proven airfield: AircraftCapacity=200, 5 launch / 5 recovery points, 7 elevators, 60 deck park slots, DamagePoints=600, Role=Airfield — no new mesh, no new animati…
  
  If the donor changes: Run time: nothing breaks if Modern US Airbase is unsubscribed — the generated files are self-contained and the scenery they reference is vanilla. Build time: build_pack.py dies immediately …

- **Add new unit ids/filenames (airbase_raaf_*.ini) instead of overriding any existing airbase file, so the pack contests no whole-file override with any mod.**  
  *File semantics* — No mod in mods-source/ ships any land_units/airbase_raaf_*.ini (checked across all 132 exported mods) and none ships an Australian airbase unit. tools/generate_load_order.py:60: "TIER6_EXTRA = [] # SEST RAAF Bases moved to TIER0" — the pack left the "airbases last" tier because it has nothing to lose a conflict over; the sibling ISR pack…
  
  Effect: Modern US Airbase keeps its own airbase_us.ini and all its US air groups; the 15 RAAF bases appear alongside it in the mission editor.
  
  If the donor changes: Fully additive — removing the pack removes the 15 bases and nothing else. Any mission placing them breaks, which is why tools/preflight checks mission references.

- **Ship no aircraft/ files at all: air groups reference aircraft ids owned by other mods and sibling packs, which only need to be installed, not ordered above or below the pack.**  
  *File semantics* — The pack contains only land_units/ and language_en/. README: "Dependencies (aircraft resolve from their own mods)... A squadron whose source mod is missing simply won't spawn — the base itself still works." docs/conflicts-and-load-order.md:53: "Airbases last — ... Placed at the bottom so any overlapping files they carry lose to the aircr…
  
  Effect: Bases inherit whatever the winning aircraft file says — so SEST patches applied to the same aircraft (F-15EX Revamp, RAAF F-35A JATM, Allied Fixes, B-52 ARRW) reach the bases' aircraft auto…
  
  If the donor changes: Unsubscribing an aircraft mod silently empties that squadron slot only; the base unit still loads.

- **Validate every rostered aircraft id and squadron index at build time by counting real [SquadronN] sections, explicitly refusing to trust NumberOfSquadrons; fail the build on an out-of-range…**  
  *In-game observation* — Inline comment in build_pack.py: "Never trust NumberOfSquadrons on its own: the F-22 mod declares 7 and defines 1, which is how missions ended up referencing squadrons that silently did not exist." squadron_limit docstring: "A mod that declares more than it defines (the F-22 mod claims 7, defines 1) is the trap this exists to catch." Cor…
  
  Effect: No base can ship a squadron reference that resolves to nothing in game (the failure mode is silent — aircraft that never spawn or all share one anonymous identity).
  
  If the donor changes: If an upstream mod shrinks its squadron list, the next rebuild fails loudly instead of shipping dead references.

- **Resolve aircraft and squadron files from sibling SEST packs first, then mods-source/, then mods-source/_vanilla/original/ — a reference is valid if a SEST pack that outranks the upstream mo…**  
  *File semantics* — squadron_limit docstring: "Searches the SEST packs as well as the workshop mods and vanilla: several aircraft (F-15EX, F-22, E-7A) only get their full squadron list from a SEST pack sitting above the upstream mod, and a base that references those squadrons is valid precisely because that pack ships." Commit f8aede5: "The bases builder's …
  
  Effect: Lets the bases roster things only SEST defines — e.g. raaf_mq-4c_triton exists nowhere in mods-source, only in SEST_ADF_Persistent_ISR.
  
  If the donor changes: Breaks if the Tier 0 invariant is broken (a workshop mod placed above SEST_Integration); tools/check_load_order.py enforces it.

- **Declare the pack's build order dependency on sibling packs in data/mod-catalog.json (build_after: SEST_ADF_Persistent_ISR, SEST_F-15EX_Revamp, SEST_RAAF_Wedgetail, SEST_Raptor_Squadrons) in…**  
  *File semantics* — tools/build_all.py docstring: "Why order matters: SEST_RAAF_Bases validates its air groups against sibling packs' output (integration/raaf-bases/build_pack.py resolves squadrons through integration/*/SEST_*/aircraft/), so on a clean tree it must build after the packs it reads. That edge is declared in data/mod-catalog.json's local_packs …
  
  Effect: None directly; guarantees a --from-scratch rebuild reproduces the committed pack (verified this session: rebuild printed "15 bases, 258 aircraft total, all references validated" and left gi…
  
  If the donor changes: A renamed sibling pack fails the build ("build_after names unknown pack").

- **Give the F-15EX 66 airframes across eight distinct squadrons (two-squadron wing at Amberley plus dets at Tindal, Darwin, Scherger, Townsville, Curtin, Williamtown), each det pointing at the…**  
  *Upstream donor* — The indices only exist because SEST F-15EX Revamp ships a replacement usaf_f-15ex_SEII_squadrons.ini with NumberOfSquadrons=8 (upstream 3636386513 F-15 EX Eagle II defines 2). Mapping checks out one-for-one against that file's comments: Amberley Squadron1|Squadron2 = "#44th FS 'Vampires'" / "#67th FS 'Fighting Cocks'"; Darwin Squadron3 =…
  
  Effect: Each det shows as its own unit with its own identity/callsign rather than seven copies of the same squadron; 66 F-15EX vs 24 before.
  
  If the donor changes: Without SEST F-15EX Revamp above the F-15EX mod, six of the seven dets reference squadrons that do not exist (README first-flight check: "the F-15EX squadrons come from SEST F-15EX Revamp";…

- **Roster the E-7A at Williamtown as Squadron1 = No. 2 Squadron RAAF, drawing squadrons from SEST RAAF Wedgetail rather than the E-7A mod.**  
  *Upstream donor* — mods-source/3499239964 ([DEPRECATED] E-7A Wedgetail) ships E7A_Wedgetail_squadrons.ini with NumberOfSquadrons=1 and zero [SquadronN] sections; integration/raaf-wedgetail/SEST_RAAF_Wedgetail/.../E7A_Wedgetail_squadrons.ini defines 5, beginning "[Squadron1] No. 2 Squadron RAAF - Williamtown". README first-flight check: "The E-7A's squadron…
  
  Effect: 3 Wedgetails in RAAF 2 SQN identity at their real base instead of a nameless default.
  
  If the donor changes: Without SEST RAAF Wedgetail the reference falls back to the upstream Default-only file (the builder would emit its warning path: "squadrons file defines no [SquadronN] sections (Default onl…

- **Keep two author-deprecated mods subscribed because this pack rosters them: [DEPRECATED] E-7A Wedgetail (3499239964) and [DEPRECATED] S-70B-2 Seahawk (3403661005).**  
  *Author mandate* — The authors marked both deprecated; the repo overrode that on dependency grounds. docs/conflicts-and-load-order.md:13-14: "[DEPRECATED] E-7A Wedgetail (Pog Frog) | Marked deprecated by its author | **KEEP (revised 2026-08-23): SEST_RAAF_Bases depends on it** (Williamtown AEW&C wing)" and "...**SEST_RAN_Fleet and SEST_RAAF_Bases depend on…
  
  Effect: Williamtown's 3 Wedgetails and Townsville's 4 S-70B-2 Seahawks keep spawning.
  
  If the donor changes: Unsubscribing either mod empties exactly those squadron slots; the bases still load. If the author's replacement ships under a different unit id, the roster entries must be retargeted.

- **Use the P-8's Squadron3 for every Australian P-8A slot (Edinburgh 8, Darwin 2, Learmonth 4, Butterworth 3) to get RAAF paint.**  
  *Upstream donor* — mods-source/3602046770 (Boeing P-8 Poseidon) usn_p8_squadrons.ini [Squadron3]: "ResourcesLiveryFolder=aircraft/P8_Poseidon/Upgrade/Liveries/ / LiveryTexture=RAAF.png / Nation=Australia" — the only Australian entry among its 7 (US, India, Australia, UK, Norway, NZ, ROK). README: "8× P-8A (**No.12 SQN RAAF livery**)".
  
  Effect: Australian-marked Poseidons rather than USN grey.
  
  If the donor changes: If the P-8 mod reorders its squadron table, Squadron3 silently becomes another nation's livery — the builder's count check would still pass. The unit file itself is currently won by SEST_Al…

- **Map RAAF F-35A squadron indices to the mod's real RAAF units at the two flagship bases: Williamtown = Squadron1|Squadron2 (77 SQN + 3 SQN, 12 each), Tindal = Squadron3 (75 SQN, 12).**  
  *Real-world spec* — mods-source/3514484654 (RAAF F-35A Lighting II) raaf_f-35a_squadrons.ini comments: "[Squadron1] ## No. 77 Squadron (RAAF Base Williamtown)", "[Squadron2] ## No. 3 Squadron (RAAF Base Williamtown)", "[Squadron3] ## No. 75 Squadron (RAAF Base Tindal)", "[Squadron4] ## No. 2 Operational Conversion Unit (RAAF Base Williamtown)". Builder desc…
  
  Effect: F-35As at their real home bases carry their real squadron identities.
  
  If the donor changes: Depends on mod 3514484654 staying subscribed for both the airframe and the four squadrons; SEST_RAAF_F-35A_JATM wins the raaf_f-35a.ini override but ships no squadrons file.

- **Reuse the same four F-35A squadron indices at the other six F-35A bases (East Sale/Gingin/Butterworth = Squadron1, Pearce = Squadron2, Curtin = Squadron3, Darwin/Scherger = Squadron4).**  
  ***UNSTATED*** — No comment, commit message or doc records why a given index was picked for these bases, and two of them read against the mod's own labels: Pearce is described "Western Australia training hub: F-35A conversion unit" but uses Squadron2 = "No. 3 Squadron", while the actual conversion unit is Squadron4 = "No. 2 Operational Conversion Unit"; …
  
  Effect: Those dets fly in another squadron's markings; harmless but cosmetically wrong for anyone reading the liveries.
  
  If the donor changes: Purely a data choice in BASES; changing an index is a one-line edit plus rebuild.

- **Roster KC-135A tankers at Tindal (Squadron1), Learmonth (Squadron2) and Butterworth (Squadron3) against the vanilla aircraft, with no recorded livery check.**  
  ***UNSTATED*** — README says only "KC-135A is vanilla", and no mod in mods-source ships usaf_kc-135a*. The vanilla mods-source/_vanilla/original/aircraft/usaf_kc-135a_squadrons.ini defines 8 squadrons that are civil airline schemes: "[Squadron1] Atlantic Airlines" / ResourcesLiveryFolder=aircraft/civ_707/atlantic/, "[Squadron2] Pangaea Airlines", "[Squad…
  
  Effect: The six KC-135s at those three bases are likely to render in airliner paint rather than USAF markings — worth an in-game look; nothing in the repo records that anyone has taken one.
  
  If the donor changes: Fixable by choosing another index or another tanker id; no external dependency involved.

- **Flag every base as Nation=Australia, including RAAF Base Butterworth, which is a Malaysian base hosting an Australian presence.**  
  ***UNSTATED*** — A single VARIANTS_INI constant ("[Default] Nation=Australia / [Variant1] Nation=Australia") is written for all 15 bases; Butterworth's own description says "Forward presence, Malaysia". No comment addresses the flag, and language_en/land_units_names.ini files it under the "Australia" heading.
  
  Effect: Butterworth sorts and fights as an Australian unit in the editor and scoring.
  
  If the donor changes: One extra variants template would change it; nothing else depends on it.

- **Model the three northern bare bases (Learmonth, Curtin, Scherger) in activated crisis posture rather than as empty fields, and ship no unit for the non-flying RAAF Base Wagga.**  
  *Real-world spec* — README: "(RAAF Base Wagga is non-flying and has no unit; the bare bases are modeled in their activated crisis posture, since an empty airfield already exists as vanilla scenery.)"
  
  Effect: Learmonth (4 P-8A, 2 U-2, 2 KC-135), Curtin (8 F-35A, 6 F-15EX, 2 KC-46A drogue) and Scherger (8 F-35A, 8 F-15EX, 4 MQ-9 ER) come with air groups; a player wanting a deserted bare base uses…
  
  If the donor changes: Data-only; removing a base from BASES drops its files on the next rebuild.

- **Substitute usmc_kc-130t (US Naval Aviation) for the RAAF's Hercules fleet at Richmond (6) and Townsville (2).**  
  ***UNSTATED*** — README labels it as a substitution — "6× KC-130T Hercules (C-130 stand-in)" — but records no reason for the specific airframe. The collection has no C-130H/J transport; mod 3737267013 (United States Naval Aviation) ships both usmc_kc-130t.ini and usmc_kc-130j.ini, and nothing says why the older T was chosen over the J.
  
  Effect: Richmond's air mobility wing flies USMC-model KC-130Ts in Australian service.
  
  If the donor changes: Losing US Naval Aviation empties both slots (it is also the source of the MH-60R squadron table and the KC-130 airframes).

- **Take the MQ-4C Triton dets at Edinburgh (No.9 SQN, 3) and Tindal (2) from the sibling SEST ADF Persistent ISR pack, and drop the Zephyr S dets that came with the same branch.**  
  *Player directive* — Commit 5e47ec1: "Its RAAF bases roster additions are ported into this branch's builder rather than overwritten - the two had diverged... keeping both sets: Edinburgh gets a 3-ship No.9 SQN Triton det, Tindal a 2-ship Triton det, Learmonth a 3-ship Zephyr orbit, Woomera a Zephyr trials flight." Commit 941eba5: "Roll back the Zephyr S; the…
  
  Effect: Persistent maritime ISR from Edinburgh and Tindal; no HAPS platform anywhere.
  
  If the donor changes: raaf_mq-4c_triton exists only in SEST_ADF_Persistent_ISR — remove that pack and both dets stop spawning (and a clean-tree rebuild fails the existence check, which is why it is listed in bui…

- **Declare ApproximateVersion=0.8.2 rather than cloning the donor's 0.5.1.**  
  *In-game observation* — Commit 673e50b: "Every SEST pack declared ApproximateVersion=0.6.8 against a 0.8.x game. That check requires MAJOR and MINOR to match, so all seven packs were failing it. Now 0.8.2, matching the rebase sources." The donor mods-source/3592460366/_info.ini still reads ApproximateVersion=0.5.1.
  
  Effect: The pack passes the game's compatibility gate instead of being rejected.
  
  If the donor changes: Needs a bump when the game's minor version moves; the donor's stale value must not be copied forward by a future template change.

- **Ship the pack at Tier 0 (inside SEST_Integration, top of the Mod Manager) despite the collection's "airbases last" rule, and treat aircraft references as order-independent.**  
  *File semantics* — docs/conflicts-and-load-order.md:53 states the rule and its scope: "Airbases last — ... so any overlapping files they carry lose to the aircraft mods they draw from (which only need to be *installed* to be referenced — list position doesn't affect resolvability, only file conflicts)." Since this pack carries no overlapping file, tools/ge…
  
  Effect: None for the bases themselves; keeps every SEST patch in one unbreakable block so no reshuffle can make a patch inert (the failure that made SEST Growler NGJ + MALICE dead for days).
  
  If the donor changes: The README and _info.ini still carry the pre-consolidation instruction "Place it **below** the aircraft mods in the Mod Manager (bases last, per the repo's load-order doc)" — following that…

- **Count an airbase's rostered units as dependencies of the pack in tools/check_dependencies.py, not just weapons and overridden files.**  
  *File semantics* — tools/check_dependencies.py comment: "Units the pack rosters - an airbase that spawns E-7As needs whatever mod defines the E-7A just as much as a loadout needs its missile. Missing this reported SEST_RAAF_Bases, which rosters an entire wing, as standalone." The scan parses ^([A-Za-z0-9_.\-]+)=Squadron\d+,\d+ lines and fails when "no mod,…
  
  Effect: None in game; makes the pack's ~20 aircraft-mod dependencies visible before an unsubscribe removes a wing.
  
  If the donor changes: n/a — tooling.

- **Downgrade one class of squadron problem to a warning: if an aircraft's squadrons file defines no [SquadronN] sections at all, print a warning and continue rather than failing.**  
  *File semantics* — build_pack.py: warnings.append(f"{base_id}: {aircraft_id} squadrons file defines no [SquadronN] sections (Default only) — verify {sq} falls back to the default livery in-game"). No path currently triggers it (the current build prints no warnings), because the Default-only cases — E-7A above all — are covered by sibling packs.
  
  Effect: Permits rostering an aircraft whose mod ships only a [Default] block, at the cost of an unverified livery fallback.
  
  If the donor changes: If a sibling pack that supplies squadrons is dropped, the affected reference degrades from a hard error to this warning.

**Must stay subscribed**

- 3592460366 Modern US Airbase — BUILD-TIME ONLY. build_pack.py reads its land_units/airbase_us.ini as the template; the emitted bases are self-contained and reference vanilla Reykjavik scenery, so the shipped pack keeps working wi…
- SEST F-15EX Revamp (sibling pack) — defines usaf_f-15ex_SEII squadrons 3-8. Without it six of the seven F-15EX dets (Tindal, Darwin, Scherger, Townsville, Curtin, Williamtown) reference squadrons that do not exist; only Amberley'…
- SEST RAAF Wedgetail (sibling pack) — defines E7A_Wedgetail squadrons (upstream ships a [Default] only). Without it Williamtown's 3 Wedgetails lose their No. 2 Squadron RAAF identity.
- SEST ADF Persistent ISR (sibling pack) — sole source of raaf_mq-4c_triton. Without it the Edinburgh (3) and Tindal (2) Triton dets do not spawn and a clean-tree rebuild fails the existence check.
- 3636386513 F-15 EX Eagle II — the F-15EX airframe (66 aircraft across 7 bases).
- 3514484654 RAAF F-35A Lighting II — the F-35A airframe and its four RAAF squadrons (8 bases).
- 3499239964 [DEPRECATED] E-7A Wedgetail — kept subscribed against the author's deprecation solely for Williamtown's AEW&C wing.
- 3403661005 [DEPRECATED] S-70B-2 Seahawk — kept subscribed for Townsville's 4 Seahawks (also a SEST RAN Fleet dependency).
- 3602046770 Boeing P-8 Poseidon — P-8A airframe and the RAAF.png Squadron3 livery (Edinburgh, Darwin, Learmonth, Butterworth).
- 3737267013 United States Naval Aviation — usmc_kc-130t (Richmond, Townsville) and the winning usn_mh-60r squadron table (19 squadrons).
- 3741944366 B-52H Stratofortress + 3652097318 B-1B Lancer + 3480965706 B-2 Spirit — the Tindal/Amberley/Woomera bomber rotations (B-2 additionally needs Anchor Chain + SeaLifter per the catalog's known_missing_dependencies).
- 3744475027 KC-46A Pegasus (boom and warp/drogue ids) + 3740293822 KC-10A Extender + 3781062859 E-3G — Amberley, Pearce, Darwin, Curtin.
- 3503670861 General Atomics MQ-9 Reaper (usaf_mq-9a, usaf_mq-9_er), 3425450153 AH-64 Apache (usa_ah-64e), 3468959181 U-2 "Dragon Lady" — Tindal/Edinburgh/East Sale/Scherger/Woomera/Townsville/Learmonth.
- 3760871384 Dingtools Weapon Pack — README: "F-15EX + B-52H + B-1B (dingtools, keep Weapon Pack above them)", the author's own placement requirement.
- Vanilla only: usaf_kc-135a (no mod ships it) — Tindal, Learmonth, Butterworth.

**Known limits**

- All 15 bases are the same model. Every generated file is byte-identical to the donor from [FlightDeck] to EOF — same Reykjavik mesh, AircraftCapacity=200, DamagePoints=600, UnitScoreValue=10 — so a 4-aircraft satellite field (Gin…
- The squadron validator takes the maximum [SquadronN] count across ALL sources (defined = max(defined, real)) rather than the file that actually wins the load order. Where two workshop mods ship the same squadrons file — usn_mh-60…
- Section counting proves a squadron resolves, not that it is appropriate: vanilla usaf_kc-135a's eight squadrons are civil 707 airline liveries (aircraft/civ_707/atlantic|pangaea|transglobe), and the pack's three KC-135 dets point…
- README drift: the README table and its "253 aircraft across 15 bases" predate the Triton merge — the generated _info.ini says 258, and the README's Edinburgh and Tindal rows omit the MQ-4C dets that are in the built files. The ge…
- Builder docstring and one code comment are stale from the five-base era: "Build the SEST RAAF Bases pack: five Australian airbases" and "# Emit the five base units", against 15 entries in BASES.
- Install instructions in README and _info.ini ("Place BELOW the aircraft mods" / "Place it **below** the aircraft mods in the Mod Manager") contradict current practice — the pack now deploys inside SEST_Integration at Tier 0. Harm…
- build_after lists SEST_Raptor_Squadrons, but no base rosters an F-22 id; the F-22 appears in this pack only as the cautionary example in squadron_limit's docstring. A conservative build edge, not a live content dependency.
- Bases are air groups only — no SAM, radar or defensive land units accompany them, so a RAAF base is an undefended airfield unless a mission author places air defence separately.

### `raaf-wedgetail`

The E-7A Wedgetail mod (workshop 3499239964) ships a [Default] squadron only with its single [Squadron1] block commented out and pointing at placeholder civ_707 art, so every `SquadronReference=Squadron1` in a mission or airbase roster fails to resolve; this pack replaces the squadron file with the type's five real AEW&C operators and supplies the matching language keys, without touching the aircraft definition or its baked-in livery.


**Files (5)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `/home/user/Seapower-mods/integration/raaf-wedgetail…` | overrides | 3499239964 — "[DEPRECATED] E-7A Wedgeta… | It is the only source of the file anywhere: `find mods-source integration -iname "*E7A*" -o -iname "*wedgetail*"` returns nothing outside 3499239964 … |
| `/home/user/Seapower-mods/integration/raaf-wedgetail…` | merges | 3499239964 — "[DEPRECATED] E-7A Wedgeta… | language_*/ files merge key-by-key, so the pack adds only Squadron1..5 under [E7A_Wedgetail] and lets the donor keep ownership of the type name and d… |
| `/home/user/Seapower-mods/integration/raaf-wedgetail…` | adds | none — generated manifest (build_patch.… | Pack manifest; carries the load-order mandate "Requires the E-7A Wedgetail mod and must sit ABOVE it." and ApproximateVersion=0.8.2. |
| `/home/user/Seapower-mods/integration/dist/SEST_Inte…` | overrides | 3499239964 — "[DEPRECATED] E-7A Wedgeta… | Consolidated deployable. Verified byte-identical to the pack copy (`diff` reports no differences); tools/consolidate_packs.py hard-errors if two pack… |
| `/home/user/Seapower-mods/integration/dist/SEST_Inte…` | merges | 3499239964 — "[DEPRECATED] E-7A Wedgeta… | The pack's five Squadron keys appear at lines 42-47 of the merged file, alongside other packs' aircraft sections; consolidate_packs.py merges languag… |

**Decisions (19)** — File semantics 7, Upstream donor 3, UNSTATED 3, Engine precedent 3, Real-world spec 2, In-game observation 1


- **Ship a whole replacement aircraft/E7A_Wedgetail_squadrons.ini and require the pack to sit ABOVE the E-7A mod in the Mod Manager, rather than attempting any additive edit.**  
  *File semantics* — docs/design-notes.md: "Unit files are whole-file overrides. For aircraft/, vessels/, submarines/, land_units/, ammunition/... the highest mod's copy loads and the rest are *gone* — silently." Pack manifest: "Requires the E-7A Wedgetail mod and must sit ABOVE it." docs/setup-runbook.md item 8: "SEST RAAF Wedgetail above the E-7A Wedgetail…
  
  Effect: SquadronReference=Squadron1..5 resolves for the E-7A; if the pack is ever outranked, every Wedgetail silently reverts to the anonymous Default aircraft.
  
  If the donor changes: Order-fragile by construction: any workshop mod placed above SEST_Integration that ships the same filename makes the pack inert with no error. tools/check_load_order.py is the guard.

- **Clone upstream's [General] header verbatim (SerialnumberReferences= empty, EmblemReference=Emblem, NationFlagReference=Flag1, AllVariantsAreOfSameNation=False) and change only NumberOfSquad…**  
  *Upstream donor* — mods-source/3499239964/aircraft/E7A_Wedgetail_squadrons.ini ships exactly those four keys; upstream's own trailing comment on the fourth reads "//Speeds up nation sorting. Only needed if there is more then 1 nation variants. Default is 'true'". The pack's SQUADRONS_INI template reproduces them and formats NumberOfSquadrons={count} from l…
  
  Effect: Nation sorting keeps working now that the type genuinely spans four nations (upstream's False was previously redundant; it is now load-bearing). No serial or emblem decals, because upstream…
  
  If the donor changes: If the author later populates SerialnumberReferences or an emblem folder, the override hides it — design-notes.md: "Upstream moves under you. A shadowed file can receive author updates the …

- **Keep [Default] Nation=Australia unchanged as squadron zero.**  
  *Upstream donor* — Upstream's [Default] block is Nation=Australia; the pack's template hardcodes the same. Live missions still reference it: "E7A_Wedgetail=Default,2" (integration/missions/AUS DEF.ini:498), "Default,4" (AUS DEF.ini:604), "Default,3" (DARWIN US SUPPLY.ini:344), "Default,1" (AUS INDO-PAC ESCA.ini:249), and every spawned airframe ("Type=E7A_W…
  
  Effect: Every existing Default reference keeps working unchanged; nothing already placed in a mission moves nation or identity.
  
  If the donor changes: Nothing breaks if the donor is removed beyond the aircraft itself disappearing.

- **Make Squadron1 = No. 2 Squadron RAAF specifically, so index 1 is the Australian aircraft.**  
  *File semantics* — build_patch.py comment: "Squadron1 is No. 2 Squadron RAAF, the type's launch and primary operator, so existing missions that already ask for Squadron1 get the correct Australian aircraft." Commit caa5995: "With Squadron1 real, both missions revert to it from the Default fallback the earlier repair applied." Consumers that bank on the ind…
  
  Effect: Williamtown's three Wedgetails and the Northern Front air groups spawn as 2 SQN RAAF instead of failing to resolve.
  
  If the donor changes: Reordering the SQUADRONS list would silently re-point every existing Squadron1 reference at a different nation's aircraft; the list order is the contract.

- **Define exactly five squadrons — 2 SQN RAAF (Williamtown), 42 WG RAAF (Williamtown), 8 SQN RAF (Lossiemouth), Turkish Air Force 131 Filo (Konya), ROKAF 51st Air Control Group (Gimhae) — as t…**  
  *Real-world spec* — build_patch.py: "The real Wedgetail/AEW&C operators." and the SQUADRONS table itself. _info.ini repeats the roster. No citation, source or table for the individual basings (Williamtown / Lossiemouth / Konya / Gimhae) is recorded anywhere in the repo — they are asserted, not referenced.
  
  Effect: Five selectable identities across four nations (flag, IFF and nation sorting differ); a mission can field RAF, Turkish or Korean Wedgetails without a new mod.
  
  If the donor changes: Squadron content is pure .ini; unsubscribing the donor removes the aircraft entirely, and the squadron file then describes a unit with no mesh.

- **Include No. 42 Wing RAAF as its own squadron entry (Squadron2) alongside No. 2 Squadron RAAF (Squadron1), both Nation=Australia and both at Williamtown.**  
  ***UNSTATED*** — No comment, docstring or commit explains why the parent wing is listed as a second squadron rather than as one operator with 2 SQN. build_patch.py only says "The real Wedgetail/AEW&C operators"; commit caa5995 lists it flatly: "(No. 2 Sqn and No. 42 Wing RAAF, No. 8 Sqn RAF, Turkish 131 Filo, ROKAF 51st ACG)".
  
  Effect: Squadron1 and Squadron2 are functionally and visually identical in game (same nation, no livery difference); only the picker string differs.
  
  If the donor changes: Removing it would renumber Squadron3..5 and break any reference already pointing at those indices.

- **Do NOT override ResourcesLiveryFolder / LiveryTexture / SpecularTexture — squadrons differ by NATION, not by paint.**  
  *Upstream donor* — build_patch.py docstring: "The mod carries no alternative livery textures - its skin is baked into per-part material files - so these squadrons differ by NATION (which drives the flag, IFF and nation sorting) and identity rather than by paint. Overriding ResourcesLiveryFolder here would point the Wedgetail at another aircraft's texture, …
  
  Effect: All five squadrons wear the same RAAF-grey skin. docs/setup-runbook.md smoke-test step 6 records this as expected: "F-35As and E-7As spawn (E-7A livery is the default one — expected)."
  
  If the donor changes: Nothing to revert — the pack ships no texture references at all, so a donor art update lands unimpeded.

- **Write [E7A_Wedgetail] Squadron1..5 name keys into language_en/aircraft_names.ini.**  
  *In-game observation* — build_patch.py: "without a [E7A_Wedgetail] SquadronN name key the picker shows \"MISSING: E7A_Wedgetail name or squadron reference\" for every squadron (seen in game)." Commit 07e5f20: "The E-7A picker showed 'MISSING: E7A_Wedgetail name or squadron reference' for every squadron this pack defines: squadrons need [E7A_Wedgetail] SquadronN…
  
  Effect: The unit picker shows real squadron names instead of a MISSING error string for all five entries.
  
  If the donor changes: Language keys merge, so they are additive and harmless on their own; without the donor mod the section names a unit that does not exist.

- **Ship only the new Squadron keys in the language file and let the game's merge preserve upstream's Type/Default/DefaultDescription.**  
  *File semantics* — Generated header: "# SEST RAAF Wedgetail - squadron display names. Language files merge key-by-key, so upstream's Default/Type/Description stay untouched." docs/design-notes.md proof: "systems/ and language_*/ merge key-by-key. Proof: 89 mods ship a systems/sensors.ini from 8 to 8,141 lines and none deletes the others. Language merging i…
  
  Effect: Type=AEW&C and the donor's long DefaultDescription survive; the pack adds names without owning the file.
  
  If the donor changes: If the donor is unsubscribed the merged section still exists but names nothing; if the donor renames its keys nothing collides.

- **Keep every display name comma-free and supply a long,short pair per squadron (e.g. "E-7A Wedgetail (2 SQN RAAF),E-7A").**  
  *File semantics* — build_patch.py: "Names stay comma-free: the comma separates the long and short forms." Output: Squadron3=Wedgetail AEW.1 (8 SQN RAF),Wedgetail.
  
  Effect: Long name in the picker, short name on the tactical map; a stray comma in a name would split the field and corrupt both.
  
  If the donor changes: n/a — formatting only. Note the rule is enforced only by the author's care, not by a builder assertion.

- **Give each operator its own type designation in the short/long name: E-7A (RAAF), Wedgetail AEW.1 (RAF), E-7T (Turkey), E-7 (ROKAF).**  
  *Real-world spec* — The SQUADRONS table's third and fourth fields: ("No. 8 Squadron RAF - Lossiemouth", "UK", "Wedgetail AEW.1 (8 SQN RAF)", "Wedgetail"), ("Turkish Air Force 131 Filo - Konya", "Turkey", "E-7T Wedgetail (131 Filo)", "E-7T"). No source is cited for the designations in the builder or any doc.
  
  Effect: Map labels and picker entries read as the operator's own designation rather than a generic E-7A.
  
  If the donor changes: Cosmetic; unaffected by donor changes.

- **Validate every Nation string against the game's own list at build time and abort on an unknown one.**  
  *Engine precedent* — build_patch.py: "# Every nation must be one the game knows, or the aircraft sorts oddly." — it parses key names out of mods-source/_vanilla/original/language_en/nations.ini and `sys.exit(f"nations not recognised by the game: {unknown}")`. Commit caa5995: "the builder validates every nation against the game's own list (it caught South Kor…
  
  Effect: Flags, IFF and nation sorting resolve for all five squadrons; the near-miss "South Korea" would have sorted the ROKAF aircraft oddly.
  
  If the donor changes: Build-time only; a vanilla nations.ini that stops shipping a nation would fail the next rebuild loudly rather than silently.

- **Guard the rebase: abort the build if the donor ever defines a real [SquadronN] of its own.**  
  *File semantics* — build_patch.py: `live = re.findall(r"^\[(Squadron\d+)\]", upstream, re.M)` then `sys.exit(f"upstream now defines {live} — rebase this patch before shipping")`. Backed by docs/design-notes.md: "Upstream moves under you. A shadowed file can receive author updates the override hides — USNA's buddy-tanker fit landed in a file the Growler pac…
  
  Effect: None at runtime; prevents the pack from silently discarding author-supplied squadrons on a future export.
  
  If the donor changes: If the author uncomments his Squadron1, the pack refuses to rebuild until a human re-decides — intentional.

- **Declare exactly as many squadrons as are defined (NumberOfSquadrons=5, five [SquadronN] blocks).**  
  *Engine precedent* — Template formats the count from the table (`NumberOfSquadrons={count}` / `len(SQUADRONS)`), and integration/raaf-bases/build_pack.py's squadron_limit() docstring names the failure this avoids: "`defined` counts real [SquadronN] sections - the number that actually resolves in game - and `declared` is the highest NumberOfSquadrons anyone c…
  
  Effect: Anything that enumerates E-7A squadrons (airbase rosters, the picker) sees five that all resolve.
  
  If the donor changes: Adding a squadron requires rerunning the builder; the count cannot drift because it is computed, not typed.

- **Ship nothing but the squadron file, the language keys and the manifest — in particular do NOT override aircraft/E7A_Wedgetail.ini (sensors, flight model, AI role) or any of the donor's 25 m…**  
  ***UNSTATED*** — The pack contains exactly three files (find over integration/raaf-wedgetail/SEST_RAAF_Wedgetail). No comment, docstring or commit states why the unit file is left alone — the reasoning is inferable from the whole-file override rule and from the donor's own note ("THIS MOD IS STILL WIP, updates will come particularly to the landing gear")…
  
  Effect: The E-7A's radar, flight model and AEW role stay exactly as the donor ships them; nothing about the aircraft's capability is changed by this pack, only its identity.
  
  If the donor changes: Because the unit file is not shadowed, any donor update to it takes effect immediately — a deliberate-looking outcome with no written rationale behind it.

- **Keep the author-deprecated donor mod subscribed rather than unsubscribing it, reversing the catalog's initial advice.**  
  *File semantics* — data/mod-catalog.json: "Marked deprecated by author — unsubscribe candidate." reversed in docs/conflicts-and-load-order.md line 13: "KEEP (revised 2026-08-23): SEST_RAAF_Bases depends on it (Williamtown AEW&C wing)"; docs/setup-runbook.md line 33: "⚠️ KEEP (changed advice) — SEST_RAAF_Bases uses it — Williamtown's AEW&C wing. Deprecated …
  
  Effect: Williamtown keeps its three E-7As and the Northern Front missions keep their AEW&C racetrack.
  
  If the donor changes: Unsubscribe the donor and both this pack and SEST_RAAF_Bases are left describing an aircraft with no model; check_dependencies.py exits non-zero and names the mod.

- **Stamp the manifest ApproximateVersion=0.8.2, not the donor's 0.4.0.**  
  *Engine precedent* — Twelve of the fifteen SEST packs carry 0.8.2 (the exceptions are SEST_ADF_Persistent_ISR at 0.6.8 and SEST_Rafale_F5 at 0.8.1); the donor's own _info.ini says ApproximateVersion=0.4.0. tools/capture-context.ps1 defines what the value tracks: "game-build.txt — install build/version, so the packs' ApproximateVersion claims can be checked" …
  
  Effect: The Mod Manager does not warn the pack is stale against the installed build.
  
  If the donor changes: Cosmetic; drifts silently when the game updates unless capture-context is re-run.

- **Write the squadron label as bare trailing text on the section header line — `[Squadron1] No. 2 Squadron RAAF - Williamtown` — with no comment marker.**  
  ***UNSTATED*** — Generated file, all five blocks. The donor's line shape was `#[Squadron1] Royal Australian Air Force` — the whole line commented, so the trailing label was inside a comment. The sibling pack hedges differently: integration/raptor-squadrons/SEST_Raptor_Squadrons/aircraft/usaf_f-22_s6_squadrons.ini writes `[Squadron1] #27th FS 'Fighting Ea…
  
  Effect: None observed — the Wedgetail squadrons resolve — but the two packs disagree on the safe form of the same construct.
  
  If the donor changes: Trivially fixable in the builder template; worth aligning with the Raptor pack's `#` form unless the bare form has been verified.

- **Let the pack's files flow into the consolidated integration/dist/SEST_Integration deployable unchanged.**  
  *File semantics* — tools/consolidate_packs.py merge rules: "identical bytes -> keep one copy"; "language_*/ *.ini -> key-level merge under each [Section]. The game itself merges language files across mods, so this reproduces in one file what the game already computed"; "anything else -> ERROR. Two packs shipping different bytes at the same unit path is a r…
  
  Effect: One Mod Manager entry (SEST_Integration) delivers these squadrons along with the other fourteen packs.
  
  If the donor changes: If another pack ever ships a different E7A_Wedgetail_squadrons.ini, consolidation fails loudly instead of picking a winner.

**Must stay subscribed**

- 3499239964 "[DEPRECATED] E-7A Wedgetail" (Pog Frog) — MUST stay subscribed and MUST sit below SEST_Integration / SEST_RAAF_Wedgetail. It supplies aircraft/E7A_Wedgetail.ini, the mesh, the animations and all 25 per-part material f…
- The donor's own prerequisites — its _info.ini warns "Please ensure you take note of the requisite mods to run this, failure to do so will result in the mod not working" and links an install tutorial. The repo never enumerates the…
- mods-source/_vanilla/original/language_en/nations.ini — build-time only. The builder reads it to validate Australia / UK / Turkey / South_Korea and exits if a nation is unrecognised; the build fails if the vanilla export is missi…
- Reverse dependency: SEST_RAAF_Bases consumes this pack's Squadron1 (integration/raaf-bases/build_pack.py: ("E7A_Wedgetail", "Squadron1,3") at Williamtown; its README: "The E-7A's squadrons come from SEST RAAF Wedgetail (upstream …
- Reverse dependency: NORTHERN FRONT II.ini (lines 1386, 1444) and NORTHERN FRONT III.ini (lines 1397, 1457) reference E7A_Wedgetail=Squadron1,3 / Squadron1,8.
- tools/check_load_order.py, tools/check_dependencies.py and tools/preflight.py are the gates that catch this pack going inert, losing its donor, or having a mission reference a squadron the winning file does not define.

**Known limits**

- No per-squadron liveries are possible with this donor. Its skin is baked into per-part material files (E7A_Wedgetail_mat.ini names one wedge_paint_DefaultMaterial texture set) and E7A_Wedgetail.ini contains no livery, Modex or se…
- Squadrons differ only by nation (flag, IFF, nation sorting) and by the picker name. SerialnumberReferences is empty upstream and stays empty, so there are no tail numbers or emblems to distinguish airframes.
- Squadron1 (2 SQN RAAF) and Squadron2 (42 WG RAAF) are both Nation=Australia at the same base, so they are indistinguishable in play apart from the label.
- The donor is author-deprecated and self-described WIP ("THIS MOD IS STILL WIP, updates will come particularly to the landing gear"), so no further upstream fixes should be assumed; it is kept only because SEST_RAAF_Bases depends …
- The pack cannot change anything about the aircraft itself — sensors, flight model, AEW role and landing gear all remain the donor's, because the pack does not ship aircraft/E7A_Wedgetail.ini.
- Squadron indices are a contract. Reordering the SQUADRONS list in the builder would silently re-point every existing Squadron1 reference (RAAF Bases, both Northern Front missions) at a different nation's aircraft.
- The load order is the failure mode with no error message: below the donor the pack does nothing and, per the runbook, "it just quietly shows every jet as the same anonymous unit."
- The builder deliberately refuses to build if the donor ever ships real [SquadronN] blocks — an intentional hard stop requiring a human rebase, not an automatic merge.

### `raptor-squadrons`

The F-22 mod declares NumberOfSquadrons=7 in all three of its squadron files but defines only [Squadron1] (named "F-22A" in the language file), so every Raptor in game is the same anonymous unit and any mission's SquadronReference=Squadron2..7 fails to resolve; this pack ships replacement squadron files plus matching language entries giving all three Raptor variants the type's seven real operating squadrons with names and callsigns.


**Files (7)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `integration/raptor-squadrons/SEST_Raptor_Squadrons/…` | overrides | 3418252667 — "F-22 Raptor" by misaka (d… | No competing donor exists: a scan of all 133 mods-source/*/aircraft directories finds F-22 files in exactly one mod (3418252667 ships usaf_f-22.ini, … |
| `integration/raptor-squadrons/SEST_Raptor_Squadrons/…` | overrides | 3418252667 — "F-22 Raptor" (misaka) | Same sole provider. The three upstream squadron files are byte-identical stubs ([General] + [Default] Nation=US + [Squadron1] Nation=US, NumberOfSqua… |
| `integration/raptor-squadrons/SEST_Raptor_Squadrons/…` | overrides | 3418252667 — "F-22 Raptor" (misaka) | Same sole provider; _s6 is the variant the missions actually field (every usaf_f-22 AirGroup line in integration/missions/*.ini is usaf_f-22_s6, e.g.… |
| `integration/raptor-squadrons/SEST_Raptor_Squadrons/…` | merges | 3418252667 — "F-22 Raptor" (misaka), la… | 90 mods ship a language_en/aircraft_names.ini and the engine merges them key-by-key, so there is no override contest — but only 3418252667 defines th… |
| `integration/raptor-squadrons/SEST_Raptor_Squadrons/…` | merges | 3418252667 — "F-22 Raptor" (misaka), la… | Same sole owner of the F-22 sections. The Chinese donor is rebased separately rather than dropped, so upstream's Chinese Type=战斗机 and DefaultDescript… |
| `integration/raptor-squadrons/SEST_Raptor_Squadrons/…` | adds | none — written by the builder (INFO_INI… | Pack manifest; carries the load-order mandate in its own Description: "Requires the F-22 mod and must sit ABOVE it." |
| `integration/dist/SEST_Integration/aircraft/usaf_f-2…` | merges | this pack, consolidated by tools/consol… | Only the consolidated pack is deployed: "Fifteen Mod Manager entries meant fifteen chances for something to jump over a SEST pack and silently disabl… |

**Decisions (19)** — Upstream donor 7, File semantics 7, UNSTATED 3, Real-world spec 1, Engine precedent 1


- **Define exactly seven squadrons and keep NumberOfSquadrons=7 rather than reducing the count to one to match what upstream actually defines.**  
  *Upstream donor* — builder comment: "# Upstream promises seven squadrons, so seven is what we define - existing missions asking for any index in range now resolve." Upstream mods-source/3418252667/aircraft/usaf_f-22_squadrons.ini is literally: NumberOfSquadrons=7 / [Default] Nation=US / [Squadron1] Nation=US — nothing else.
  
  Effect: Mission AirGroup lines that name Squadron2..7 now resolve instead of spawning aircraft with no resolved squadron: "NORTHERN FRONT II.ini:1381 usaf_f-22_s6=Squadron4,6|Squadron5,6|Squadron6,…
  
  If the donor changes: If the F-22 mod is unsubscribed the three squadron .ini files reference a model (assets/models/aircraft/f22/F22.obj) that no longer exists — the pack ships no meshes or textures at all. If …

- **Ship all three Raptor squadron files (usaf_f-22, usaf_f-22_s5, usaf_f-22_s6), not just the one the missions use.**  
  *File semantics* — AIRCRAFT_IDS comment: "# The three Raptor ids the mod ships, all with the same squadron problem." Verified: the three upstream *_squadrons.ini files are identical stubs. aircraft/ is a whole-file override directory (docs/design-notes.md: "Unit files are whole-file overrides... the highest mod's copy loads and the rest are *gone* - silent…
  
  Effect: All three Raptor variants get the same seven squadrons; the display name keeps each variant's own tag, e.g. "Squadron3=F-22A(S-6) 90th FS 'Pair O Dice',F-22A".
  
  If the donor changes: Three shadowed files instead of one: any upstream edit to those files is hidden until the pack is rebuilt (docs/design-notes.md: "Upstream moves under you. A shadowed file can receive autho…

- **Ship NO new liveries — leave ResourcesLiveryFolder/LiveryTexture unset; squadrons differ by identity, nation flag and callsign only.**  
  *Upstream donor* — docstring: "NO NEW PAINT. The mod's model has no Modex/serial/emblem submodels (the \"#---------- Modex ----------\" block in usaf_f-22_s6.ini is empty) and ships a single f-22_mat.ini texture set, so squadrons differ by identity, nation flag and callsign rather than by livery. Pointing ResourcesLiveryFolder at another aircraft's texture…
  
  Effect: Seven visually identical Raptors that read as different units in the UI and on the tacmap. Anyone expecting squadron skins gets none — the README heads the section "No new paint — read this…
  
  If the donor changes: Nothing to break: the decision is to touch nothing. If misaka later ships per-squadron textures, the pack's squadron files would shadow them until rebased.

- **Copy upstream's [General] block verbatim into every generated squadron file — SerialnumberReferences=AF_Serial, EmblemReference=Emblem, NationFlagReference=Flag1 — even though AF_Serial res…**  
  *Upstream donor* — SQUADRONS_HEADER literal in build_patch.py reproduces upstream's [General] key-for-key; README states the consequence plainly: "its model has no decal submodels at all... so `SerialnumberReferences=AF_Serial` points at nothing."
  
  Effect: None beyond upstream behaviour — the nation flag still resolves, serial/emblem stay inert exactly as before the patch.
  
  If the donor changes: Inert keys; harmless if upstream changes them, but the pack's copy would freeze the old values until rebuilt.

- **Give every squadron Nation=US and no other keys.**  
  *Upstream donor* — Upstream's own [Default] and [Squadron1] contain exactly "Nation=US"; the builder emits f"[Squadron{i}] #{name} - {basing}\nNation=US\n\n" and keeps [Default] Nation=US. The SQUADRONS table is all-USAF/ANG units.
  
  Effect: All seven fly under the US flag; no per-squadron nation surprises.
  
  If the donor changes: None — matches the donor exactly.

- **Populate the seven slots with the F-22's real operating squadrons and their real wings/bases: 27th FS 'Fighting Eagles' and 94th FS 'Hat in the Ring' (1st FW, JB Langley-Eustis), 90th FS 'P…**  
  *Real-world spec* — docstring: "The squadron names and basings are the real ones." The SQUADRONS list carries the basing string for each entry and it is echoed into the generated file as a comment, e.g. "[Squadron5] #199th FS 'Mytai Fighters' - 154th Wing HI ANG, JB Pearl Harbor-Hickam". README repeats the roster as a table. NOTE: no source, reference or ci…
  
  Effect: Raptor units read as named USAF squadrons in the unit list and on the tacmap instead of seven copies of "F-22A".
  
  If the donor changes: Text only; unaffected by upstream changes except that the builder refuses to rebuild if upstream starts defining its own squadrons.

- **Coin the per-squadron callsign words: Talon, Ringer, Dice, Bulldog, Mytai, Gamecock, Stinger.**  
  ***UNSTATED*** — There is no external authority — the builder says so itself: "The callsigns are flavour derived from each unit's nickname, not documented radio callsigns." README repeats it verbatim. Flagged here because the roster next to it IS claimed as real; the callsigns explicitly are not.
  
  Effect: Radio/unit callsigns read as e.g. "Raptor Dice" per squadron rather than everything being "Raptor".
  
  If the donor changes: Cosmetic; safe to change at any time by editing the SQUADRONS table and rebuilding.

- **Write the Callsigns line in the three-field form SquadronN,<type callsign>,<squadron flavour>, keeping the upstream type word first.**  
  *Engine precedent* — The only rationale recorded in the pack is the comment "# Generic type callsign kept first so the existing \"Raptor\" flavour survives." with TYPE_CALLSIGN = {"en": "Raptor", "cn": "猛禽"}; upstream's line is the two-field "Callsigns=Squadron1,Raptor". The three-field form is established elsewhere in the collection and is checkable — e.g. …
  
  Effect: Output: "Callsigns=Squadron1,Raptor,Talon|Squadron2,Raptor,Ringer|...|Squadron7,Raptor,Stinger" (cn: "Squadron1,猛禽,Talon|...").
  
  If the donor changes: If the engine's parsing of the third field ever changed, every squadron would fall back to the type word; nothing else in the pack depends on it.

- **Overwrite upstream's Squadron1 name ("F-22A") with a real squadron identity, rather than pinning it byte-identical the way the sibling F-15EX pack pins its first two.**  
  *Upstream donor* — docstring: "only ever defines [Squadron1] - and names it \"F-22A\" in the language file, so every Raptor in the game is an anonymous \"F-22A\" no matter which squadron a mission asks for." Upstream line is "Squadron1=F-22A,F-22A" — a type name in a squadron slot, i.e. a placeholder, unlike integration/f-15ex-revamp/build_patch.py where u…
  
  Effect: Missions already sitting on Squadron1 (e.g. "NEWEST NORTHERN AUS CH DEFENCE.ini:475 usaf_f-22_s6=Squadron1,10", "NORTHERN FRONT II.ini:1438 usaf_f-22_s6=Squadron1,6") change display from "F…
  
  If the donor changes: Drop the pack and every Raptor reverts to the anonymous "F-22A"; no mission file is modified by this pack, so nothing is stranded.

- **Build each squadron display name as "<upstream Default long name> <squadron>" and keep upstream's short name untouched, read out of the donor rather than hard-coded.**  
  *Upstream donor* — Code reads the donor's own Default line — re.search(r"^Default=([^,\n]+),([^,\n]*)$") with a hard exit ("[{aircraft_id}] has no parsable Default= line") — then emits f"Squadron{i}={long_name} {name},{short_name}". Result for the s5 variant: "Squadron4=F-22A(S-5) 525th FS 'Bulldogs',F-22A", preserving upstream's own "F-22A(S-5)"/"F-22A(S-…
  
  Effect: The variant tag stays visible next to the squadron identity, so an s5 and an s6 flight are still distinguishable in the UI.
  
  If the donor changes: If upstream renames the variants, a rebuild picks the new names up automatically; a stale pack would show the old ones.

- **Rebase both language files and preserve the Chinese localisation: upstream's Chinese Type/DefaultDescription and its 猛禽 type callsign are kept, only squadron identities are added.**  
  *Upstream donor* — TYPE_CALLSIGN = {"en": "Raptor", "cn": "猛禽"} mirrors upstream's cn line "Callsigns=Squadron1,猛禽"; rename_squadrons() docstring: "Rewrite the Squadron*/Callsigns lines of every F-22 section in a language file, keeping every other line (descriptions included) intact", with the kept-lines filter dropping only ^(Squadron\d+|Callsigns)= and a…
  
  Effect: Chinese-language players keep Chinese descriptions and the 猛禽 callsign while gaining the seven squadrons.
  
  If the donor changes: Language files merge key-by-key, so upstream keys the pack does not write still reach the game; but the pack's Squadron*/Callsigns keys win while it outranks the mod.

- **Leave the squadron identity strings in English inside language_cn (e.g. "Squadron5=F-22A 199th FS 'Mytai Fighters',F-22A").**  
  ***UNSTATED*** — The builder shares one SQUADRONS table across both languages and only the type callsign is localised (TYPE_CALLSIGN). README states the outcome — "the Chinese file keeps its own \"猛禽\" type callsign and Chinese descriptions, with only the squadron identities added" — but no reason is recorded for not translating the identities. Flagged.
  
  Effect: Chinese UI shows Chinese type/description with English squadron names and English flavour callsigns.
  
  If the donor changes: Cosmetic; a translated table could be added to the builder at any time.

- **Refuse to build (hard exit) if upstream ever defines squadrons other than [Squadron1] alone, or if a language section the rewrite needs is missing, or if descriptions are lost; only warn (n…**  
  *File semantics* — check_upstream(): "Refuse to ship if upstream has started defining its own squadrons." -> sys.exit(f"{path.name} now defines squadrons {live} — rebase this patch"); plus exits for "has no NumberOfSquadrons — upstream layout changed", "language_{lang}/aircraft_names.ini has no section for {missing}", and "descriptions lost during rewrite"…
  
  Effect: None directly — it prevents a future rebuild from silently burying an upstream fix.
  
  If the donor changes: The count check is only a printed note, so an upstream change from 7 to some other declared number would still build; the section/squadron guards are fatal and force a manual rebase.

- **Pack must be loaded ABOVE the F-22 mod; deployed as part of the consolidated SEST_Integration entry pinned to the top of the canonical order.**  
  *File semantics* — _info.ini Description: "Requires the F-22 mod and must sit ABOVE it." README install step 2: "it carries full replacement copies of the three `*_squadrons.ini` files and the higher-listed mod wins the file." docs/setup-runbook.md item 8: "**SEST Raptor Squadrons above the F-22 mod**... Below their target they do nothing, and the aircraft…
  
  Effect: Correctly ordered, the seven squadrons appear; mis-ordered, the patch is inert with no error message.
  
  If the donor changes: Any reorder that lifts 3418252667 above SEST_Integration silently disables the whole pack — the exact failure mode that once made SEST_Growler_NGJ_MALICE inert for days (docs/design-notes.m…

- **Ship .ini files only — no model, texture or asset bundle — accepting a hard dependency on the F-22 mod rather than vendoring anything.**  
  *File semantics* — tools/check_dependencies.py docstring: "The packs ship 99 files and every one is a .ini - not a single model, texture or asset bundle among them. That is deliberate (the repo stays small and the patches stay readable) but it means NO pack is standalone." Its run output for this pack: "SEST_Raptor_Squadrons / overrides 3 file(s) F-22 (341…
  
  Effect: Nothing while the F-22 mod is installed; without it, the squadron definitions point at a mesh that is not there.
  
  If the donor changes: Unsubscribing 3418252667 breaks the pack entirely (and removes the aircraft anyway).

- **Do not touch the F-22 unit files themselves (aircraft/usaf_f-22*.ini) — the pack's scope stops at *_squadrons.ini and the two language files.**  
  *File semantics* — The builder's AIRCRAFT_IDS loop reads and writes only f"{aircraft_id}_squadrons.ini"; the aircraft definitions, loadouts and materials are never opened. Consistent with docs/design-notes.md: "Upstream moves under you. A shadowed file can receive author updates the override hides." (No comment in this builder states the scope choice expli…
  
  Effect: Raptor performance, sensors and loadouts remain 100% upstream — this pack changes identity only.
  
  If the donor changes: Upstream loadout/sensor updates to usaf_f-22*.ini flow through untouched, because those files are not shadowed.

- **Mission-side counterpart: unresolved Squadron2..7 references were folded onto Squadron1 by integration/missions/fix_squadron_refs.py before this pack existed, and can be re-split afterwards…**  
  *File semantics* — fix_squadron_refs.py docstring: "Missions built in the editor can name squadrons the providing mod does not define (e.g. usaf_f-22_s6 offers only Default and Squadron1, but a mission asks for Squadron4-7), which leaves those aircraft without a livery at spawn." and "--spread is the inverse, for after a SEST pack adds squadrons a mod neve…
  
  Effect: With the pack loaded, a base's Raptor wing can read as four separate named squadrons on the tacmap instead of one anonymous 16+ ship block (--spread only fires on a single squadron of >= SP…
  
  If the donor changes: Remove the pack and those references stop resolving again; the checker would have to re-collapse them.

- **Stamp _info.ini with [Compatibility] ApproximateVersion=0.8.2 although the donor mod declares 0.7.0.**  
  ***UNSTATED*** — INFO_INI literal in build_patch.py line 74: "ApproximateVersion=0.8.2". Upstream mods-source/3418252667/_info.ini says "ApproximateVersion=0.7.0". No rationale is recorded in this builder; it matches an unwritten repo-wide convention — 13 of the 15 SEST builders use 0.8.2 (adf-persistent-isr uses 0.6.8, rafale-f5 uses 0.8.1), and tools/c…
  
  Effect: Governs the Mod Manager's game-version compatibility warning for the pack, not gameplay.
  
  If the donor changes: A game version bump past 0.8.x would need every builder's literal updated; nothing detects staleness automatically.

- **Pack .ini output is treated as the exact bytes installed, pinned to LF and read from donors as utf-8-sig.**  
  *File semantics* — Commit 41930a8: "Pack .ini files are both version-controlled source and the exact bytes install-sest-packs.ps1 copies into StreamingAssets... They are now pinned to LF." and "74 exported upstream .ini files carry a UTF-8 BOM, and reading one with encoding=\"utf-8\" keeps it as a leading character that is then spliced into the pack. All 1…
  
  Effect: None visible; prevents a stray U+FEFF at the head of a merged language file and CRLF churn between the repo and StreamingAssets.
  
  If the donor changes: Verified stable: re-running build_patch.py during this review reproduced all six output files byte-identically (clean git status).

**Must stay subscribed**

- Workshop 3418252667 "F-22 Raptor" (misaka) — MANDATORY. The pack is six .ini files and no assets; without the mod there is no F22.obj mesh, no f-22_mat.ini texture set and no usaf_f-22* unit definitions, so the squadron files def…
- Load-order position: SEST_Integration (which carries this pack) must outrank 3418252667. Below it, the three *_squadrons.ini overrides lose and the patch is silently inert — every Raptor reverts to the anonymous "F-22A" with Squa…
- mods-source/3418252667/ must stay exported in the repo for rebuilds — build_patch.py hard-exits with "upstream squadrons file missing" / "upstream language file missing" if the donor tree is absent.
- Downstream: integration/missions/fix_squadron_refs.py --spread depends on this pack being the winning provider of aircraft/usaf_f-22*_squadrons.ini to know that Squadron2..7 now exist.

**Known limits**

- No per-squadron liveries are possible with this donor: the model carries no decal submodels (the "#---------- Modex ----------" block in usaf_f-22_s6.ini is empty) and the mod ships a single texture set (assets/models/aircraft/f2…
- SerialnumberReferences=AF_Serial and EmblemReference=Emblem are carried over from upstream but resolve to nothing — kept for donor fidelity, not because they do anything.
- The callsign words (Talon, Ringer, Dice, Bulldog, Mytai, Gamecock, Stinger) are invented flavour derived from unit nicknames, explicitly "not documented radio callsigns".
- The squadron roster and basings are asserted as real but carry no citation anywhere in the repo.
- language_cn keeps Chinese descriptions and the 猛禽 type callsign, but the squadron identity strings and flavour callsigns are English.
- Three upstream files are now shadowed: any misaka update to usaf_f-22*_squadrons.ini is hidden until the pack is rebuilt. The builder's guard converts that into a loud failure ("now defines squadrons [...] — rebase this patch") o…
- Seven is a ceiling set by upstream's declaration, not by the type: real F-22 units beyond these seven (and the historical churn at Eglin) are not representable without changing NumberOfSquadrons and re-checking every mission refe…
- ApproximateVersion=0.8.2 is hard-coded per builder; nothing detects it going stale against the game version.

### `zumwalt-cps`

Restores the DDG-1000 CPS variant's hypersonic launcher, which Modern US Navy's shipped hull loses because `vessels/usn_ddg-1000_cps.ini` declares `[WeaponSystem1]` twice (LMVLS APM and MK57 1, with no `[WeaponSystem2]`) and wires the LMVLS's only fire-control sensor to a `SensorSystem12` that does not exist on an 11-sensor hull — shipped as a rebased whole-file override of that mod's file with 23 in-place line edits.


**Files (3)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `vessels/usn_ddg-1000_cps.ini (built to /home/user/S…` | overrides | 3390330875 — Modern US Navy (author Mit… | No competing donor exists: `find mods-source -iname 'usn_ddg-1000*'` returns copies only under 3390330875 (vessels/usn_ddg-1000_cps.ini plus the auth… |
| `_info.ini` | adds | none — authored by build_patch.py's INF… | Pack manifest: `Name=SEST Zumwalt CPS Fix`, `ApproximateVersion=0.8.2`, and a Description that states the defect and the dependency ("Requires Modern… |
| `integration/dist/SEST_Integration/vessels/usn_ddg-1…` | merges | 3390330875 — Modern US Navy (via this p… | tools/consolidate_packs.py folds all 15 per-pack outputs into the single deployable SEST_Integration; no other pack ships this path, so it carries th… |

**Decisions (19)** — File semantics 10, Engine precedent 5, Upstream donor 3, In-game observation 1


- **Renumber the SECOND `[WeaponSystem1]` (the block labelled `# MK57 1`) to `[WeaponSystem2]`, rather than deleting a block, renumbering the LMVLS, or renumbering the other 20 MK57s.**  
  *Upstream donor* — The mod author's own working copies restore exactly this numbering. `mods-source/3390330875/ships/usn_ddg-1000/alt/usn_ddg-1000_cps - Kopie (2).ini` line 343 `[WeaponSystem1] # LMVLS`, line 390 `[WeaponSystem2] # MK57 1`, line 435 `[WeaponSystem3] # MK57 2`; `... - Kopie - Kopie.ini` lines 332/379/424 agree. build_patch.py docstring: "Ev…
  
  Effect: All 23 weapon systems load instead of 22. The LMVLS Advanced Payload Module survives alongside all 20 MK57 cell blocks, so the ship keeps both its 12 IRCPS rounds and its full MK57 battery.
  
  If the donor changes: Unsubscribe Modern US Navy and the override has nothing to override — the DDG-1000 CPS unit ceases to exist (this pack ships no mesh). If Mitchell600 fixes the duplicate upstream, `check_up…

- **Treat the DUPLICATE section number as the bug and the missing `[WeaponSystem2]` gap as harmless — i.e. fix by renumbering, not by padding the gap.**  
  *Engine precedent* — build_patch.py docstring: "a sweep of all 734 units in mods-source that declare weapon systems found this file to be THE ONLY ONE with a duplicate section number. Gaps, by contrast, appear in 83 shipped units that work, so the missing [WeaponSystem2] is harmless on its own - it is the duplicate that costs a launcher." Same figures in the…
  
  Effect: Scopes the patch to one renumbered section header instead of restructuring the file.
  
  If the donor changes: The sweep is not re-run at build time and its script is not checked in, so the claim cannot drift-check itself — see known_limits: it no longer reproduces against the 2026-08-26 export.

- **Assume a duplicate section is silently collapsed by the loader (one block discarded, no error), rather than assumed to be a load failure or a parse error.**  
  *Engine precedent* — README evidence #2: "`mods-source/_vanilla/original/vessels/fr_ss_agosta.ini` declares `[SensorSystem6]` twice with two genuinely different sonars (`DSUV-22`, `DUUX-2`), `NumberOfSensorSystems=8`, and no `[SensorSystem7]`. That sub loads and plays — because losing a redundant passive sonar is invisible. Losing a ship's only hypersonic la…
  
  Effect: Explains the reported symptom (no crash, no error, the missile is simply absent from the weapons panel) and justifies a data-only fix.
  
  If the donor changes: Precedent is from vanilla, not a mod — cannot be lost by unsubscribing anything.

- **Infer the parser is last-wins (LMVLS overwritten by the later MK57 block), but do NOT let the fix depend on that inference.**  
  *In-game observation* — README: "The reported symptom is 'IRCPS doesn't work', which only happens under last-wins — the LMVLS losing to the later block. That is also the ordinary behaviour of assigning into a dict by key. The fix removes the ambiguity either way, so it does not depend on the inference being right." test_patch.py docstring states the epistemic l…
  
  Effect: Under either rule the patched file loads 23/23 systems (test_patch.py checks 3 and 4); upstream loads 22/23 either way — first-wins loses MK57 1, last-wins loses the LMVLS and with it the I…
  
  If the donor changes: n/a — a diagnostic inference, not a shipped value.

- **Point the LMVLS's fire control at `SensorSystem3,SensorSystem11` (SPY-3 + SM Datalink), replacing the sole dangling `SensorSystem12`.**  
  *Upstream donor* — README: "The correct value is read off the control hull, not invented: all 20 VLS blocks in `usn_ddg-1000.ini` use `SensorSystem3,SensorSystem13` (SPY-3 + SM Datalink), and CPS `SensorSystem11` is the byte-identical SM Datalink block (`SystemName=eu_JUWL`)." Verified: `grep -c 'SensorSystem3,SensorSystem13' mods-source/3390330875/vessels…
  
  Effect: The LMVLS gains working fire control — SPY-3 for the picture and the JUWL datalink for midcourse guidance, identical to how the same author wires the base Zumwalt's 20 VLS blocks. Without i…
  
  If the donor changes: The value is a hull-local index, so it survives any Mod Manager reorder; but if upstream renumbers the CPS sensor list again, `SensorSystem11` silently means something else — `validate()` o…

- **Adopt the weaker invariant "every launcher keeps at least ONE resolvable sensor" rather than "no dangling sensor references anywhere".**  
  *Engine precedent* — build_patch.py `validate()` comment: "A dangling entry alongside a valid one is tolerated - 30 units in this collection ship that way - but a launcher whose ONLY entry dangles has no fire control, which is half of what was wrong here." README: "A dangling sensor reference is on its own tolerated — 30 units in the collection have one, inc…
  
  Effect: Keeps the patch minimal — it repairs the one launcher that was actually blind and does not chase cosmetic dangling refs across the collection.
  
  If the donor changes: Survey-derived threshold; nothing to unsubscribe.

- **Also strip the stale trailing `SensorSystem12` from the 20 MK57 blocks (`SensorSystem3,SensorSystem11,SensorSystem12` → `SensorSystem3,SensorSystem11`) — declared cosmetic, not a fix.**  
  *Engine precedent* — build_patch.py docstring: "The MK57s carry the same stale SensorSystem12 as a third entry, which the game ignores because SensorSystem3 and SensorSystem11 are both valid. That is tidied here too, but it was never the bug." README change table: "Stale trailing `SensorSystem12` dropped from the MK57 blocks (already inert; consistency only)…
  
  Effect: None expected — the entry was already ignored. This is the only edit in the pack with no defended gameplay consequence, so it is also the only one whose no-op status rests purely on the sur…
  
  If the donor changes: Carried inside the whole-file override; lost with the pack.

- **Relabel `[WeaponSystem23]` from `#Mk46 GWS 1` to `#Mk46 GWS 2` — comment text only.**  
  *File semantics* — build_patch.py: "Both Mk46 gun mounts are labelled 'GWS 1'; they are different mounts (eu_mk46_turret_1 vs _2). Comment only, but this file is confusing enough." Verified upstream lines 1512 and 1534 both read `#Mk46 GWS 1`; patched line 1534 reads `#Mk46 GWS 2`.
  
  Effect: None — the engine does not read the trailing comment.
  
  If the donor changes: n/a

- **Leave `NumberOfWeaponSystems=23` untouched.**  
  *File semantics* — README: "Deliberately **not** changed: `NumberOfWeaponSystems=23` (already correct once renumbered, 1..23 contiguous)". `validate()` enforces it: `if sorted(nums) != list(range(1, declared + 1)): problems.append(...)`. Verified: line 351 `NumberOfWeaponSystems=23`, line 253 `NumberOfSensorSystems=11`, both contiguous in the output.
  
  Effect: The declared count and the actual sections agree for the first time — 23 systems declared, 23 present (LMVLS + 20 MK57 + 2 Mk46).
  
  If the donor changes: n/a

- **Do not edit Euromod's `ammunition/usn_ircps.ini` or `systems/weapons.ini` — the fix is confined to the one hull file.**  
  *File semantics* — README: "Deliberately **not** changed: … anything in Euromod's `usn_ircps.ini` (cross-mod edits affect every consumer, and none of them can make a launcher exist)." Follows the project's override rule (docs/design-notes.md: "Unit files are whole-file overrides … the highest mod's copy loads and the rest are *gone* — silently"): shipping …
  
  Effect: No other ship or mod that references `usn_ircps` is affected; only the CPS Zumwalt changes.
  
  If the donor changes: Nothing to reverse — the pack never claims a second file. Also means the LMVLS-only launcher binding stays upstream's decision.

- **Leave the launcher/magazine geometry alone after verifying it already balances: 4 containers × 3 attachments = 12 = magazine load.**  
  *Upstream donor* — build_patch.py docstring: "eu_lmvls_apm and eu_lmvls are defined in Euromod's systems/weapons.ini, the magazine holds 12x usn_ircps, and 4 containers x 3 attachments matches that count exactly." Verified: `[WeaponMagazine_LMVLS]` at line 1722 → `Ammunition1=usn_ircps`, `Ammunition1_Count=12`; `[WeaponSystem1] # LMVLS` → `NumberOfContaine…
  
  Effect: 12 IRCPS rounds, 4 tubes, 3 per tube — the loadout the author intended, with `ModuleType=VLS` and `FireRate=30`.
  
  If the donor changes: Depends on Euromod's `eu_lmvls_apm` keeping `NumberOfAttachments=3`; the test would catch a change, the builder would not.

- **Ship the fix as a whole-file replacement placed ABOVE Modern US Navy, not as a partial/keyed patch.**  
  *File semantics* — build_patch.py: "# Whole-file override: the game replaces unit files, it never merges keys." README install step 2: "It must sit **ABOVE Modern US Navy** in the Mod Manager — it carries a full replacement copy of `vessels/usn_ddg-1000_cps.ini` and the higher-listed mod wins the file. `data/load-order.tokens.txt` already places it there."…
  
  Effect: The player's game loads this repaired copy of the hull instead of Mitchell600's.
  
  If the donor changes: If anything is reordered above the SEST block the patch goes inert with no error — the exact failure that killed SEST_Growler_NGJ_MALICE for days (docs/design-notes.md). check_load_order.py…

- **Enforce that the patch is 23 in-place line edits by failing the build on any line-count change.**  
  *File semantics* — build_patch.py: `if len(text.splitlines()) != original_lines: sys.exit("line count changed — the patch should be edits in place, not insertions")`. README: "23 lines, all edits in place — the file's line count is unchanged, and the build fails if it isn't." Verified: upstream and output are both 3807 lines; `diff` yields 46 changed lines…
  
  Effect: Guarantees the shipped override is upstream's file with 23 values changed, so every other property of the ship (meshes, 3800 lines of submodels, damage model) is the author's.
  
  If the donor changes: n/a — a build-time guard.

- **Refuse to build on any of four upstream changes rather than silently producing a stale override.**  
  *File semantics* — `check_upstream()` exits if duplicates are no longer exactly `[1]`, if the two `[WeaponSystem1]` labels are not LMVLS then `MK57 1` ("the two [WeaponSystem1] blocks are not LMVLS then MK57 1: {labels} — rebase"), or if a `[WeaponSystem2]` has appeared; `main()` exits if `"Launcher1=eu_lmvls_apm" not in ircps` ("usn_ircps no longer binds …
  
  Effect: Protects against re-shipping a fix for a bug the author has fixed, which would freeze the player's Zumwalt at an old revision.
  
  If the donor changes: n/a — build-time guards.

- **Validate the output against five reference namespaces, keeping weapon-system and sensor-system `SystemName`s in separate pools and resolving `ContainerBase`/`Collider` inside the ship file …**  
  *File semantics* — `validate()` docstring: "Note the two distinct namespaces, which are easy to conflate: SystemName= in a weapon block -> systems/weapons.ini; SystemName= in a sensor block -> systems/sensors.ini; ContainerBase=/Collider=/Mount= -> a submodel section in THIS file (eu_mk46_barrel_1, for instance, is defined inside the ship ini, not in weapo…
  
  Effect: Catches a broken reference before the player sees a missing turret or an unlaunchable round.
  
  If the donor changes: The ammunition pool is only three sources wide, so an id supplied by some fourth mod would be falsely reported.

- **Keep the `Container1_Hatch=` idiom untouched even though it looked irregular.**  
  *Engine precedent* — README: "Deliberately **not** changed: … the `Container1_Hatch=` idiom (576 uses across the collection)". Verified exactly: `grep -rhE '^Container[0-9]+_Hatch=' mods-source | wc -l` = 576. The LMVLS block uses it four times (`Container1_Hatch=eu_lmvls_hatch_1` … `_4`, with matching `LMVLS_Tube_N_Open/Close` animations).
  
  Effect: Hatch animations on the four LMVLS tubes keep working as the author built them.
  
  If the donor changes: n/a

- **Accept the Navy 2027 / Euromod reorder as harmless to this pack rather than pinning Euromod's rank.**  
  *File semantics* — docs/conflicts-and-load-order.md: "**Navy 2027 now sits above Euromod.** … the LMVLS and IRCPS the Zumwalt fix needs are Euromod-only ids that no ordering can take away." The ids `eu_lmvls_apm`/`eu_lmvls` live in Euromod's merging `systems/weapons.ini` and `usn_ircps` is an ammunition file no other exported mod ships.
  
  Effect: The fleet-wide SM-2/RAM/ESSM consistency change was made without regressing the Zumwalt.
  
  If the donor changes: Only unsubscribing Euromod (3629144864) breaks it — reordering cannot.

- **Prove the fix without the game: 12 static checks including a two-rule loader simulation and a check that the SEST copy actually wins the file.**  
  *File semantics* — test_patch.py: `load_weapon_systems(text, rule)` — "A keyed loader stores sections in a dict by name, so a repeated name either keeps the first occurrence and ignores later ones, or is overwritten by the last." Results table in README: upstream first-wins = 22/23 (MK57 1 lost), upstream last-wins = 22/23 (LMVLS lost, IRCPS unfireable), p…
  
  Effect: None directly; it is the confidence basis for shipping a fix nobody has yet confirmed in game.
  
  If the donor changes: Check 5 (author-backup agreement) breaks if Mitchell600 removes the `ships/usn_ddg-1000/alt/` backups from a future export — those files are the only external corroboration of the intended …

- **Deploy only through the consolidated pack (integration/dist/SEST_Integration), not as its own Mod Manager entry.**  
  *File semantics* — tools/consolidate_packs.py docstring: "Fifteen Mod Manager entries meant fifteen chances for something to jump over a SEST pack and silently disable it — the exact way SEST_Growler_NGJ_MALICE once went inert. One consolidated pack collapses that entire failure class." data/load-order.tokens.txt lists only `SEST_Integration` at the top. V…
  
  Effect: One entry to keep at the top of the order instead of a fragile block of fifteen.
  
  If the donor changes: The per-pack folder stays the build unit; forgetting to re-run consolidate_packs.py after a rebuild means the deployed file is stale while the repo looks correct.

**Must stay subscribed**

- 3390330875 — Modern US Navy (Mitchell600). MUST stay subscribed AND below the SEST block. It supplies the DDG-1000 CPS hull, its mesh and all 3807 lines this pack rebases on; the pack ships no models (tools/check_dependencies.py:…
- 3629144864 — Euromod - Main Pack (Mitchell600). MUST stay enabled. `eu_lmvls_apm` and `eu_lmvls` are defined in its systems/weapons.ini (line 157: NumberOfAttachments=3) and the round itself is mods-source/3629144864/ammunition/u…
- Build-time only: both mods must be present under mods-source/ or build_patch.py exits before writing anything.
- Deployment: tools/consolidate_packs.py must be re-run after any rebuild — tools/install-sest-packs.ps1 deploys integration/dist/SEST_Integration only.

**Known limits**

- Parser behaviour is unobservable. Nobody outside Triassic can see which block Sea Power's ini loader keeps on a duplicate section, so the fix is proved under BOTH first-wins and last-wins rather than measured (test_patch.py docst…
- No recorded in-game confirmation. All 12 checks are static file analysis. The README gives a manual recipe ("Put a Zumwalt CPS in a mission and open its weapons panel… Assign an IRCPS to a land or surface target") but no screensh…
- README arithmetic nit in that same recipe: it says the player should see "**22 launchers**: the LMVLS with 12× IRCPS, plus 20 MK57 blocks and 2 Mk46 gun mounts" — that is 23, and the file declares NumberOfWeaponSystems=23. The ve…
- The uniqueness claim has gone stale against the current export. build_patch.py and _info.ini both assert this is "THE ONLY ONE" of 734 units with a duplicate weapon-system number, but a re-sweep of mods-source (re-exported 2026-0…
- Cross-mod defects are out of scope by design: Euromod's usn_ircps.ini binding the round to a single launcher type is left as the author wrote it.
- The LMVLS fire-control value is a hull-local index (SensorSystem11). validate() proves it resolves, not that it is still the SM Datalink — a future upstream sensor renumber would pass the build while silently re-aiming the launch…
- Whole-file override risk stated in docs/design-notes.md: "A shadowed file can receive author updates the override hides." Any future Mitchell600 change to usn_ddg-1000_cps.ini beyond these 23 lines is invisible to the player unti…

### `f-16cm-jatm`

Adds two derived loadouts (AIM-260 JATM intercept, AIM-424 MALICE) to the USAF F-16CM Block 52 by re-shipping Zero Two's whole aircraft file with 29 added lines, so a next-gen AAM defined in one mod (Dingtools) and a mesh defined in a third (US Naval Aviation) can be hung on an airframe from a fourth without any of them being modified.


**Files (5)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `integration/f-16cm-jatm/SEST_F16CM_JATM/aircraft/us…` | overrides | 3758320372 — F-16C Fighting Falcon (mod… | No competition exists: `find mods-source -name "usaf_f-16*"` returns this filename only under 3758320372. The only other F-16 in the collection, 3416… |
| `integration/f-16cm-jatm/SEST_F16CM_JATM/ammunition/…` | adds | Mesh/material: 3737267013 — United Stat… | New id, so no file is displaced. For the 174B baseline the module states the tie-break explicitly: "Aligned to usn_aim-174b as shipped by U.S. Navy 2… |
| `integration/f-16cm-jatm/SEST_F16CM_JATM/language_en…` | adds | none — SEST-authored, two keys only | language_*/ files merge key-by-key (docs/design-notes.md: "`systems/` and `language_*/` merge key-by-key... Language merging is how packs rename othe… |
| `integration/f-16cm-jatm/SEST_F16CM_JATM/language_en…` | adds | none — SEST-authored, generated by inte… | One key (sest_aim-424) with the encyclopedia card. Same merge semantics; identical bytes to the copy five sibling packs ship, so overlap is order-ind… |
| `integration/dist/SEST_Integration/{aircraft/usaf_f-…` | merges | consolidated by tools/consolidate_packs… | The aircraft file is unique to this pack (diff -q against the pack copy: identical). sest_aim-424.ini collides with five other packs and resolves und… |

**Decisions (18)** — File semantics 6, Upstream donor 3, UNSTATED 2, Comparison 2, Engine precedent 2, Player directive 1, Real-world spec 1, In-game observation 1


- **Build the pack at all, and confine it to the USAF CM airframe: "Only the USAF CM airframe is touched; the HAF/POL/TUAF/IAF F-16s keep their stock loadouts." AIRFRAME = "usaf_f-16cm-bl52d".**  
  *Player directive* — Commit e11cec5 (2026-08-26, the pack's only commit): "Requested alongside a question about borrowing the F-16C mod's targeting pod for the F-15EX." The scope limit is stated in build_patch.py's docstring, lines 16-17; the mod ships five other F-16 files (haf_f-16c-bl50, haf_f-16c-bl52plus, iaf_f-16c-barakII, pol_f-16c-bl52plus, tuaf_f-16…
  
  Effect: Only USAF Block 52D Vipers gain the two new fits; Greek, Polish, Turkish and Israeli F-16s are untouched and keep receiving Zero Two's updates directly.
  
  If the donor changes: Zero cost — those five files are never shadowed, so nothing to unwind.

- **Derive SEST_F16_Intercept260 from the mod's own AirToAirVLongRange block rather than authoring a station table: DERIVATIONS[0] = ("SEST_F16_Intercept260", "AirToAirVLongRange", [swaps]).**  
  *Upstream donor* — build_patch.py docstring: "Two derived loadouts, both on the mod's own proven fits"; docs/design-notes.md working practices: "**Derive, don't invent.** New loadouts clone a donor block the mod's author already proved (same stations, hide lists, keys) and swap rounds." The generated block keeps the donor's SubModelsToHide string verbatim …
  
  Effect: A 4× AIM-260 + 2× AIM-9X + three-tank very-long-range CAP fit that renders exactly like the stock VLongRange fit it clones.
  
  If the donor changes: If Zero Two renames or removes AirToAirVLongRange the builder exits: "donor loadout {donor} not found - upstream changed".

- **Each AIM-120D→AIM-260 swap keeps the donor's per-store seat key: usaf_aim-120d|aim-120d-34 → dts_aim-260|aim-120d-34 and |aim-120d-56 → |aim-120d-56, rather than hanging the round bare.**  
  *Real-world spec* — build_patch.py docstring: "The JATM is built to the AMRAAM footprint, so each round keeps the donor's aim-120d seat key." The keys are real offsets in the donor file: aim-120d-34Positions=0,0,-0.001824 and aim-120d-56Positions=0,0,-0.001595 (mods-source/3758320372/aircraft/usaf_f-16cm-bl52d.ini lines 248 and 254). Consistent with docs/de…
  
  Effect: The AIM-260s sit on the AMRAAM rails at exactly the depth the AMRAAMs did — no floating or sunken rounds.
  
  If the donor changes: If upstream drops those position keys the missiles shift to raw station coordinates; nothing errors, it just looks wrong.

- **Derive SEST_F16_MALICE from the SEAD block and put the AIM-424 on the HARM stations (Station9/Station10), hung BARE with no seat key, exactly as the donor hung usn_agm-88.**  
  *Upstream donor* — build_patch.py docstring: "the two AGM-88 HARMs become AIM-424 MALICE - the 424 rides the AGM-88G AARGM-ER airframe, so these are literally its stations"; swap tuple is ("usn_agm-88", AIM424_ID) with no pipe key on either side. This is the one airframe where design-notes' rule ("The AIM-424 renders with the AGM-88G mesh whose origin ride…
  
  Effect: 2× AIM-424 MALICE where the HARMs were, plus 2× AIM-260, 2× AIM-9X, Sniper + HTS pods and all three tanks.
  
  If the donor changes: Guarded: "no stations carry {old} - upstream changed" if the SEAD block stops carrying usn_agm-88.

- **Swaps match the WHOLE store spec including the pipe seat key, not just the ammunition id.**  
  *File semantics* — build_patch.py lines 37-38: "Store specs are matched whole, pipe seat keys included, so a swap keeps or changes the seat deliberately, never by accident." Implemented as re.sub(rf"^(Station\d+=){re.escape(old)}(\s*)$", ...) — anchored both ends.
  
  Effect: None directly; it prevents a class of silent mis-seating when one airframe uses the same store on two different seats (the F-16 file has aim-120d-34, -56 and -78 variants).
  
  If the donor changes: n/a — build-time discipline.

- **Take the AIM-260 from Dingtools Weapon Pack (dts_aim-260) rather than from either subscribed mod that defines usn_aim-260a.**  
  ***UNSTATED*** — build_patch.py records only the constant, with no comparison: WEAPON_PACK = ROOT / "mods-source" / "3760871384" # Dingtools (dts_aim-260). Competing definitions exist and are subscribed: mods-source/3418252667/ammunition/usn_aim-260a.ini (F-22 Raptor, misaka) and mods-source/3607989779/ammunition/usn_aim-260a.ini (F-35C Alt. Loadouts). T…
  
  Effect: Players get dingtools' JATM numbers (125 nm, 3507 kt, MaxTurnRate 40, SeekerActiveRange 32) rather than whatever usn_aim-260a carries.
  
  If the donor changes: Unsubscribing Dingtools leaves six Station lines pointing at an undefined store; tools/check_dependencies.py exits non-zero ("references 1 file(s) Dingtools Weapon Pack (3760871384)").

- **Hang dts_aim-260 (the internal-carriage variant) on the F-16's external wing/fuselage AMRAAM stations, where the project's own convention uses dts_aim-260_w.**  
  ***UNSTATED*** — FLAG — no comment anywhere in build_patch.py. The convention is documented in the sibling packs: integration/f-35c-jatm/README.md and integration/raaf-f-35a-jatm/README.md both say "`dts_aim-260` internal, `dts_aim-260_w` external, matching dingtools' own internal/external carriage convention on the F-15EX", and integration/f-15ex-revamp…
  
  Effect: Every rail-launched AIM-260 off the F-16 falls unpropelled for 0.8 s (a bay-ejection delay) instead of 0.01 s. Whether that is visible or costs launch envelope at low altitude has not been …
  
  If the donor changes: One-line fix in DERIVATIONS if it ever matters; no upstream dependency changes.

- **Give the AIM-424 MALICE the AIM-174B's flight model key-for-key, with an enumerated set of deliberate deltas rather than free-hand numbers.**  
  *Comparison* — integration/common/aim424.py: "It is deliberately built as a peer of the AIM-174B rather than a lesser cousin: the flight model is aligned key-for-key with U.S. Navy 2027's usn_aim-174b so the two encyclopedia cards compare directly", followed by a "What stays different, on purpose" table. I checked every cited figure against mods-source…
  
  Effect: MALICE reads as a bay-sized 174B: 290 nm instead of 316, Power 48 vs 52, CEP 10 m vs 6, but a 40 nm active / 80 nm passive seeker and full anti-emitter homing against the 174B's HomeOnJam.
  
  If the donor changes: If U.S. Navy 2027 is unsubscribed the MALICE is unaffected (it is a standalone file), but the comparison it was tuned against disappears from the game and whichever lower mod then owns usn_…

- **Keep DragCoefficient explicit at 3.6 instead of the engine default -1.**  
  *Engine precedent* — integration/common/aim424.py: "THIS KEY MUST STAY EXPLICIT: at -1 the engine back-solves 8.14 from the airframe and the missile loses roughly a third of its reach", repeated inline in the shipped ini: "DragCoefficient=3.6 // explicit - a -1 here back-solves to 8.14 and kills the reach". The donor file's own comment documents the mechanis…
  
  Effect: MALICE actually reaches its advertised 290 nm; at -1 it would fall to roughly two-thirds of that.
  
  If the donor changes: n/a — self-contained in the SEST file.

- **Ship the AIM-424's [Models] block byte-identical to USNA's usn_agm-88g and never add keys to it — specifically, no ResourcesMeshScale.**  
  *In-game observation* — integration/common/aim424.py: "REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the missile stopped rendering as an AARGM-ER afterwards - the model block falls back to AssetBundleMesh=usn_rim-7, a short fat Sea Sparrow, which is exactly what showed up under the wing... Do not add keys to it that the source mod doe…
  
  Effect: The MALICE renders as an AARGM-ER under the F-16's HARM pylons instead of a stubby Sea Sparrow.
  
  If the donor changes: If US Naval Aviation (3737267013) is unsubscribed, ResourcesFolder=assets/models/ammunition/agm-88/ resolves to nothing and the game falls back to the usn_rim-7 asset bundle — "same as the …

- **Leave the AIM-424's apparent size alone: [col_main] Scale=0.005,0.005,0.04291637 is kept matched to usn_agm-88g and treated as the hit collider, not a visual dimension.**  
  *Engine precedent* — integration/common/aim424.py collider comment: "This Scale is the HIT COLLIDER box, not the visual - every ammunition ini in the collection carries it under [col_main] and none has a model-size key... and cannot be resized from the ini (ResourcesMeshScale, the one candidate key, breaks the model)." Commit 705057b: "Collider comment in co…
  
  Effect: MALICE looks AGM-88G-sized under the wing, permanently. Accepted, not fixable from data files.
  
  If the donor changes: n/a

- **Add sest_aim-424.ini as a new ammunition id rather than editing or overriding any existing missile, and accept that six SEST packs now ship byte-identical copies.**  
  *File semantics* — integration/common/aim424.py: "All four SEST packs that carry MALICE fits write identical copies of ammunition/sest_aim-424.ini and a partial language_en/ammunition_names.ini - identical same-path files are a safe overlap whichever pack sits higher in the Mod Manager." tools/consolidate_packs.py rule 1: "identical bytes -> keep one copy"…
  
  Effect: No existing weapon changes stats because of this pack; ammunition/ override order is irrelevant for the 424.
  
  If the donor changes: Deleting this pack does not remove the MALICE — five other packs still define it.

- **Ship only the aircraft file — no override of any ammunition file the F-16 mod owns (usaf_aim-120d, usn_agm-88, the tanks, f16_anaaq-33, usaf_anasq-213 are all referenced, none is re-shipped…**  
  *File semantics* — Pack contents are exactly: _info.ini, aircraft/usaf_f-16cm-bl52d.ini, ammunition/sest_aim-424.ini, language_en/{ammunition_names,loadout_names}.ini. docs/design-notes.md: "Unit files are whole-file overrides... the highest mod's copy loads and the rest are *gone* — silently." Every additional file shipped would be another silently-won co…
  
  Effect: The stores keep whatever values the winning mod gives them — e.g. usn_aim-9x currently resolves to U.S. Navy 2027 (line 17 of the token list, above all six other owners) and usn_agm-88 to M…
  
  If the donor changes: Side effect worth knowing: because the pack now owns the whole F-16 file, the stock SEAD/SEADECM/DEAD/DEADECM fits inside it still hang usn_agm-88, so this pack inherits a REFERENCE depende…

- **Retain the Sniper (f16_anaaq-33|ANAAQ-33) and HTS (usaf_anasq-213|HTS) pods and all three tanks on the MALICE fit, even though the anti-radiation missiles the HTS exists to cue are gone.**  
  *Upstream donor* — build_patch.py docstring: "Sniper pod, HTS pod and all three tanks stay." It is the minimum-delta consequence of cloning SEAD — only the two swap pairs change, everything else is copied. No rationale is recorded for keeping the HTS specifically.
  
  Effect: The MALICE Viper carries a HARM Targeting System pod with no HARM. The AIM-424 is TargetType=AAW with SecondaryTargetType=ASuW, so this fit is an anti-AEW/anti-jammer/anti-ship loadout wear…
  
  If the donor changes: Dropping the pods would be a one-line addition to the swap list; keeping them costs nothing but the pylon.

- **Guard the build against upstream drift with five hard exits rather than best-effort patching.**  
  *File semantics* — build_patch.py: missing-input check ("missing {mod.name}/{need} - re-export mods-source"), "AvailableLoadouts not found", "SEST keys already declared upstream" (so an upstream that later ships these keys is not silently double-defined), "donor loadout {donor} not found - upstream changed", "no stations carry {old} - upstream changed", "W…
  
  Effect: None at runtime; it is what stops a silently-empty loadout reaching the game after a Zero Two update.
  
  If the donor changes: A Zero Two update to the F-16 file is hidden by this override until someone re-exports mods-source and re-runs the builder — the exact failure mode design-notes describes ("A shadowed file …

- **Deploy through the consolidated SEST_Integration pack and change nothing in the load order.**  
  *File semantics* — Registered in data/mod-catalog.json local_packs as {"folder": "SEST_F16CM_JATM", "source": "integration/f-16cm-jatm", "builder": "build_patch.py"}. Commit e11cec5: "Registered in local_packs, which is all it takes now: build_all consolidates it into SEST_Integration, the installer deploys it, and the load order is untouched - the consoli…
  
  Effect: The pack cannot be silently disabled by a Mod Manager reorder — the failure that left the Growler pack inert for days.
  
  If the donor changes: n/a — structural.

- **Keep every displayed string comma-free and ship only the two new keys in language_en.**  
  *File semantics* — build_patch.py LOADOUT_NAMES comment: "Comma-free: commas are field separators in language files"; integration/common/aim424.py: "language_en/ammunition_names.ini format: stem=DisplayName,Nickname,Category,Description (the description must not contain commas — they are field separators)." Shipped values: SEST_F16_Intercept260=SEST Interc…
  
  Effect: The two fits show readable names in the loadout picker instead of raw keys, without the pack owning any other mod's loadout names.
  
  If the donor changes: n/a

- **Decline the F-15EX targeting-pod swap that prompted this pack, rather than adding a cross-mod pod substitution.**  
  *Comparison* — Commit e11cec5: "Investigated and declined the pod swap as pointless: Zero Two's f16_anaaq-33 is the same recipe as Dingtools' dts_anaaq-33 the F-15EX already hangs - same mesh (the material inside the F-16 mod is literally still named dts_anaaq-33_mat.ini), same 208 kg, same AN/AAQ-33(L)/(V) sensors, which are properly defined in four m…
  
  Effect: No change to the F-15EX; one fewer cross-mod dependency created.
  
  If the donor changes: n/a — nothing was shipped.

**Must stay subscribed**

- 3758320372 — F-16C Fighting Falcon (modern), Zero Two. MUST stay subscribed and stay below the SEST block. The pack ships a whole-file override of its aircraft/usaf_f-16cm-bl52d.ini; without the mod the airframe has no mesh, no u…
- 3760871384 — Dingtools Weapon Pack, dingtools. MUST stay subscribed: defines dts_aim-260, hung on six stations across the two new fits. Author mandate recorded in the catalog: "Put this mod ABOVE any of my mod". Without it both f…
- 3737267013 — United States Naval Aviation, misaka. MUST stay subscribed for the MALICE to look right: sest_aim-424's [Models] points at assets/models/ammunition/agm-88/agm-88g.obj and usn_agm-88g_mat.ini, which only this mod ship…
- 3606774881 — U.S. Navy 2027 Capabilities, Prof_CH4OS. Currently the winning owner of usn_aim-9x (the wingtip rounds on both new fits) and of usn_aim-174b, the missile the AIM-424 was calibrated key-for-key against. Listed by chec…
- 3430135740 — F/A-18 Murder Hornet with AIM-174B, Cropgun. Inherited, not chosen: because this pack now ships the whole F-16 file, the stock SEAD/SEADECM/DEAD/DEADECM fits inside it still reference usn_agm-88, and Murder Hornet (t…

**Known limits**

- The AIM-424 cannot be made to look smaller. "ResourcesMeshScale, the one candidate key, breaks the model" (integration/common/aim424.py), and the [col_main] Scale is the hit collider, not the visual. The MALICE will always render…
- The MALICE fit inherits an exact station co-location from upstream: tools/check_station_clash.py at the tight 0.001 threshold reports "usaf_f-16cm-bl52d.ini WS1 SEST_F16_MALICE S11=f16_anaaq-33 <-> S17=usaf_anasq-213 d=0.00000" —…
- No language_cn. The pack writes only language_en, so SEST_F16_Intercept260 and SEST_F16_MALICE appear as raw keys in a Chinese-language client. Four sibling packs (f-15ex-revamp, f-35c-jatm, growler-ngj-malice, raptor-squadrons) …
- No in-game verification is recorded for either fit. The commit reports "16 packs build from scratch byte-identically; preflight, check_load_order and check_dependencies green" — check_station_clash is not among them, and docs/set…
- No README. Every other JATM/loadout pack of comparable size documents itself (integration/f-35c-jatm/README.md, raaf-f-35a-jatm/README.md, f-15ex-revamp/README.md); this pack's entire rationale lives in the builder docstring, the…
- Doc drift in the shared MALICE module this pack depends on: integration/common/aim424.py still says "All four SEST packs that carry MALICE fits" (six do now) and its "# Users:" line lists usn_f-35c, raaf_f-35a, usaf_f-15ex_SEII a…
- The pack shadows Zero Two's F-16 file. Any future author update to usaf_f-16cm-bl52d.ini is invisible in game until mods-source is re-exported and build_patch.py re-run — the standing hazard design-notes names ("Upstream moves un…

### `rafale-f5`

Gives the three late-standard Dassault Rafales (fr_rafale_b_l / c_l / m_l) six JATM-era loadouts — AIM-260, AIM-424 MALICE and LRASM fits — by re-shipping misaka's aircraft files with extra [WeaponSystem1*] blocks cloned from the mod author's own proven loadouts, so French airframes can carry weapons that live in three other mods without any of those mods being edited.


**Files (8)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `/home/user/Seapower-mods/integration/rafale-f5/SEST…` | overrides | 3504168760 — Dassault Rafale (misaka) | Uncontested. A scan of mods-source shows only 3504168760 ships any fr_rafale_*.ini (18 files); no competing mod defines the airframe, so the whole-fi… |
| `/home/user/Seapower-mods/integration/rafale-f5/SEST…` | overrides | 3504168760 — Dassault Rafale (misaka) | Same: sole provider of the file. 918 lines. |
| `/home/user/Seapower-mods/integration/rafale-f5/SEST…` | overrides | 3504168760 — Dassault Rafale (misaka) | Sole provider, and the airframe the pack exists for — build_patch.py docstring: 'the M_L is fielded in every NORTHERN FRONT mission'. Verified: fr_ra… |
| `/home/user/Seapower-mods/integration/rafale-f5/SEST…` | adds | New unit id (no upstream file). Flight … | Two different donors for two different halves, both named in integration/common/aim424.py: the mesh donor is US Naval Aviation because 'The 3D model … |
| `/home/user/Seapower-mods/integration/rafale-f5/SEST…` | merges | SEST-authored; upstream 3504168760 ship… | language_*/ files merge key-by-key across mods, so the pack can name its six new loadouts without owning any file the Rafale mod ships. Six keys only. |
| `/home/user/Seapower-mods/integration/rafale-f5/SEST…` | merges | SEST-authored (integration/common/aim42… | One key, sest_aim-424, for the encyclopedia card. Same merge semantics; identical bytes to the other MALICE-carrying packs. |
| `/home/user/Seapower-mods/integration/rafale-f5/SEST…` | adds | n/a | Pack manifest. Consolidation regenerates it for integration/dist/SEST_Integration. |
| `REFERENCED, NOT SHIPPED: dts_aim-260 and dts_agm-15…` | adds | 3760871384 — Dingtools Weapon Pack (din… | Four mods ship dts_agm-158c-3 (3760871384, 3636386513 F-15 EX, 3652097318 B-1B, 3741944366 B-52H) and two ship dts_aim-260 (3760871384, 3636386513). … |

**Decisions (18)** — In-game observation 6, File semantics 5, UNSTATED 3, Upstream donor 2, Comparison 1, Player directive 1


- **Every one of the six loadouts is derived from an existing upstream [WeaponSystem1*] block by regex substitution of store ids only — station numbers, SubModelsToHide lists and seat keys are …**  
  *Upstream donor* — build_patch.py docstring: 'Each is derived from one of the mod's own fits by swapping rounds on the stations the donor already proves, so the geometry is the author's.' Confirmed by diffing output against mods-source/3504168760/aircraft/fr_rafale_m_l.ini: e.g. SEST_MALICE is StrikeLongRange with S3/4 fr_mica-em and S9/10 fr_meteor change…
  
  Effect: Six new selectable fits per airframe; no stock Rafale loadout changes.
  
  If the donor changes: If misaka renames or removes AirToAirLongRange / StrikeLongRange / AntiShip / AirToAirIntercept the build exits with '<airframe>: donor loadout <donor> not found' rather than emitting a wro…

- **The AIM-424 mounts BARE on stations 5/6 (written as 'sest_aim-424', no |SCALP suffix) even though it replaces a store that used the SCALP seat.**  
  *In-game observation* — build_patch.py inline comment: '# The 424 mounts BARE, like the AIM-260 does - the SCALP seat's / # -0.006 z offset floated it visibly clear of the pylon (screenshot).' The seat exists and matches: fr_rafale_m_l.ini:219 'SCALPPositions=0,-0.001794,-0.006172'. Recorded again in docs/design-notes.md: 'the Rafale's 424 (the SCALP seat float…
  
  Effect: MALICE rounds sit flush on the heavy wet stations instead of hanging in space below them.
  
  If the donor changes: Nothing breaks if upstream changes SCALPPositions — the fit no longer uses that key. It only matters again if misaka moves the bare station-5/6 origins.

- **LRASM is seated on the SCALP key ('dts_agm-158c-3|SCALP'), not on the AM39 key it inherits from the AntiShip donor.**  
  *Comparison* — build_patch.py: '("fr_am-39_Block2|AM39", "dts_agm-158c-3|SCALP"), # LRASM keeps the heavy seat', and the docstring: 'seated on the SCALP key rather than the Exocet one (1,023 kg rides the 1,300 kg round's mount, not the 655 kg one's)'. In-file masses back the direction of the argument though not the exact figures: dts_agm-158c-3 Mass=10…
  
  Effect: A 1,023 kg LRASM hangs at the heavy-store height instead of the Exocet's shallower one.
  
  If the donor changes: derive() fails loudly if the AntiShip donor stops carrying fr_am-39_Block2|AM39 ('no stations carry ... - upstream changed'). If misaka removes the SCALP position key the round falls back t…

- **Every fr_meteor in every derived fit becomes dts_aim-260 — the SEST Rafale fits are Meteor-free — and the swap spec gained a '?' optional prefix so airframes whose donor never carried Meteo…**  
  *In-game observation* — Commit 78bd451 ('Feedback batch from in-game testing'): 'Rafale: SEST fits are Meteor-free on all three airframes - the swap table gains a "?"-optional form so airframes whose donors never carried Meteor still build.' Implemented as ('?fr_meteor', 'dts_aim-260') on all six derivations. NOTE — the builder's own documentation now contradic…
  
  Effect: Fuselage/outer stations that were Meteor now fire AIM-260 (125 nm dts_aim-260 vs the Meteor); the 'Heavy' fit really is 6x AIM-260 as its label claims.
  
  If the donor changes: Optional swap: if upstream drops Meteor from a donor the build still succeeds silently. The AIM-260 comes from Dingtools Weapon Pack — unsubscribe it and all six fits hang an undefined stor…

- **SEST_Intercept260Heavy deletes the donor's wing tanks (Station7/Station8) outright; the centreline tank (Station11) stays.**  
  *In-game observation* — build_patch.py: 'the donor's WING tanks (7/8) go - the AIM-260s the swap puts on the adjacent rails are Meteor-class fat and clip them (reported in-game); the centreline tank stays, nothing sits beside it.' Commit 1d59795: 'Swapping those rails to AIM-260s (Meteor-class diameter) left the missiles visibly overlapping the wing tanks in-ga…
  
  Effect: Heavy intercept fit trades two 1,200 L wing tanks for a clean look: 6x AIM-260 + 2x MICA-IR + centre tank.
  
  If the donor changes: derive()'s drop guard exits with 'expected donor AirToAirIntercept to fit Station7 - upstream changed, re-check the drop list' if misaka reworks that fit.

- **SEST_Intercept260F5 (the long-range fit) KEEPS its wing tanks despite carrying the same fattened rail rounds.**  
  *Player directive* — Commit 1d59795: 'SEST_Intercept260F5 (the long-range fit) keeps its wing tanks deliberately — they are that loadout's purpose. If the same clip shows there, the fix is a seat offset for its rail AIM-260s, not a tank removal.' i.e. the in-game report scoped the complaint to the Heavy fit only.
  
  Effect: Long-range intercept keeps three tanks and may show the same visual clip until someone reports it.
  
  If the donor changes: n/a — no upstream coupling.

- **The two _ER fits strip 'Center_Pylon' out of the SubModelsToHide list they copied from their donors, and derive() gained a general 'unhide' parameter to do it.**  
  *In-game observation* — Commit 9f51015 header: 'Center_Pylon (reported in-game: "no centre fuel pylon rendering" on SEST Intercept MALICE Long Range) ... those donors never fit a centre store, so their SubModelsToHide includes Center_Pylon, and the copied hide list left the added tank hanging under an invisible pylon.' Corroborated by an engine-precedent check …
  
  Effect: The centreline tank on the two LongRange fits now hangs from a visible pylon instead of floating.
  
  If the donor changes: Guarded: 'expected Center_Pylon in donor <donor>'s SubModelsToHide - upstream changed, re-check the unhide list' aborts the build if misaka stops hiding it.

- **The pack's own loadout key SEST_Intercept260 was renamed SEST_Intercept260F5 to stop it colliding with the Growler pack's key of the same name.**  
  *File semantics* — Commit 9f51015: 'Key namespacing (consolidation prep — [LoadoutNames] keys are global across mods, so two packs defining one key differently fight over the display string) ... rafale-f5's SEST_Intercept260 collided with the Growler pack's key of the same name ("SEST Intercept (AIM-260)" vs "... (8x AIM-260)"). Renamed to SEST_Intercept26…
  
  Effect: The Rafale fit reliably shows 'SEST Intercept (AIM-260)' rather than whichever pack happened to outrank the other.
  
  If the donor changes: Purely internal; safe against any workshop mod that later defines SEST_Intercept260.

- **Only the three late-standard combat airframes are overridden. The other 15 fr_rafale_*.ini files upstream ships (squadron rosters, nuclear variants, the tanker, and the early B/C/M) are lef…**  
  *In-game observation* — AIRFRAMES = ['fr_rafale_b_l', 'fr_rafale_c_l', 'fr_rafale_m_l'] with the docstring's justification for the M: 'the M_L is fielded in every NORTHERN FRONT mission' (confirmed against integration/missions/). The inclusion of the B_L and C_L rests on nothing recorded beyond being the same late standard, and the exclusion of fr_rafale_*_squa…
  
  Effect: Squadron rosters and nuclear/tanker Rafales continue to receive upstream updates untouched; only the three combat airframes get SEST fits.
  
  If the donor changes: Low exposure: three files to re-diff after a misaka update instead of eighteen.

- **The six new keys are appended to the existing AvailableLoadouts line rather than replacing it, and the build aborts if upstream ever declares one of them.**  
  *File semantics* — build_patch.py main(): "if any(k in la.group(2) for k in NEW_KEYS): sys.exit(f'{airframe}: SEST keys already declared upstream')", then text = text[:la.end(2)] + ',' + ','.join(NEW_KEYS) + ... Output line reads 'AvailableLoadouts=AirToAir,AirToAirLongRange,...,AntiShip,SEST_Intercept260F5,SEST_MALICE,SEST_AntiShipLRASM,SEST_Intercept260H…
  
  Effect: All nine stock Rafale loadouts remain selectable alongside the six SEST ones.
  
  If the donor changes: If misaka ever ships a key by one of these names the rebuild stops rather than producing a duplicate declaration.

- **Blocks are spliced immediately before the '[---------- WeaponMagazines ----------]' marker, and the builder pre-checks three upstream files before touching anything.**  
  *File semantics* — main() exits with 'missing dependency: <path>' unless mods-source/3760871384/ammunition/dts_aim-260.ini, .../dts_agm-158c-3.ini and mods-source/3504168760/aircraft/fr_rafale_b_l.ini all exist; and with '<airframe>: WeaponMagazines marker missing' if the splice point is gone. Matches docs/design-notes.md 'Everything is generated. Packs re…
  
  Effect: None directly — it is what stops a silently wrong pack from shipping.
  
  If the donor changes: Every upstream change that would invalidate the pack becomes a build failure, not a broken save.

- **The AIM-424 MALICE is a shared, byte-identical file written by integration/common/aim424.py, not a Rafale-local weapon.**  
  *File semantics* — integration/common/aim424.py module docstring: 'All four SEST packs that carry MALICE fits write identical copies of ammunition/sest_aim-424.ini and a partial language_en/ammunition_names.ini - identical same-path files are a safe overlap whichever pack sits higher in the Mod Manager.' (Now seven copies including dist; all md5 86788be118…
  
  Effect: The Rafale's MALICE is the same missile the F-35C, RAAF F-35A, F-15EX, F-16CM and Growler packs carry — one encyclopedia card, one balance point.
  
  If the donor changes: A hand-edit to any single pack's copy would fail consolidation with a named-pack error rather than silently diverging.

- **The AIM-424's flight model is aligned key-for-key to U.S. Navy 2027's usn_aim-174b, with a short list of deliberate deltas; DragCoefficient is pinned explicitly at 3.6.**  
  *Upstream donor* — integration/common/aim424.py: 'Aligned to usn_aim-174b as shipped by U.S. Navy 2027 Capabilities (3606774881) - the version that actually wins the load order in this collection ... Same explicit-drag flight model, same 150,000 ft loft ceiling ... What stays different, on purpose: MaxLaunchRange 290 vs 316 nm - it has to fit inside an F-3…
  
  Effect: 290 nm reach, 40 nm active / 80 nm passive seeker, dual-pulse motor — a peer of the AIM-174B rather than a lesser cousin, and readable against it on the same card assumptions.
  
  If the donor changes: If 3606774881 is unsubscribed the missile still works; only the comparison baseline it was tuned against disappears.

- **The AIM-424's [Models] block is byte-identical to US Naval Aviation's usn_agm-88g and ResourcesMeshScale was removed.**  
  *In-game observation* — integration/common/aim424.py: 'REMOVED: ResourcesMeshScale. Shrinking the mesh by 0.9 was cosmetic, and the missile stopped rendering as an AARGM-ER afterwards - the model block falls back to AssetBundleMesh=usn_rim-7, a short fat Sea Sparrow, which is exactly what showed up under the wing. The [Models] block below is now byte-identical …
  
  Effect: MALICE rounds on the Rafale's stations 5/6 render as AARGM-ERs instead of stubby Sea Sparrows.
  
  If the donor changes: Unsubscribe 3737267013 and the missile silently reverts to the usn_rim-7 asset-bundle stand-in — visual only, no crash.

- **The pack is Tier 0: it must sit above 3504168760 (and above nothing else on this pack's account — it ships no file any other mod ships).**  
  *File semantics* — data/load-order.tokens.txt header: 'INVARIANT: every SEST_* pack sits above every workshop mod. A SEST pack is a whole-file replacement of a workshop mod's unit file; if anything outranks it the patch silently does nothing.' tools/check_load_order.py computes the rule rather than listing it: 'For each SEST pack, every mod that also ships…
  
  Effect: If violated the six fits vanish from the loadout dropdown with no error message.
  
  If the donor changes: SEST_Integration is first in data/load-order.tokens.txt; 3504168760 is at line 73.

- **Loadout display names are shipped for English only.**  
  ***UNSTATED*** — LOADOUT_NAMES = {'en': {...}} with no other locale. Commit 78bd451 records the scope as a fact without a reason — 'F-15EX en+cn, Growler en+cn, Rafale en' — even though upstream 3504168760 ships language_cn/ and language_fr/ folders and other SEST packs do carry cn labels. No comment in build_patch.py addresses it.
  
  Effect: Under a French or Chinese locale the six SEST fits display as raw keys (SEST_MALICE_ER, etc.). Upstream ships no loadout_names.ini in any locale, so this is a gap rather than a regression.
  
  If the donor changes: n/a

- **The pack manifest declares ApproximateVersion=0.8.1.**  
  ***UNSTATED*** — INFO_INI in build_patch.py, hardcoded. Every other current pack declares 0.8.2 (13 packs) except SEST_ADF_Persistent_ISR at 0.6.8. No comment explains why this one is a revision behind — it looks like an un-bumped constant, not a decision.
  
  Effect: Cosmetic compatibility banner in the Mod Manager only.
  
  If the donor changes: n/a

- **Loadout labels carry no store counts.**  
  ***UNSTATED*** — The recorded reason is now false: 'No store counts in the labels: the late airframes keep Meteor on the fuselage stations their donors gave them, so composition varies.' The Meteor purge removed that variance, and one label already breaks the rule — 'SEST Intercept Heavy (6x AIM-260)'.
  
  Effect: Labels understate what four of the six fits actually carry.
  
  If the donor changes: n/a

**Must stay subscribed**

- 3504168760 — Dassault Rafale (misaka). HARD. Supplies the meshes, animations, assets/ and the fr_mica-ir / fr_meteor(now unused) / fr_tank_1200 / fr_scalp-eg ammunition, plus the SCALPPositions seat key the LRASM rides. The pack …
- 3760871384 — Dingtools Weapon Pack (dingtools). HARD, and specifically this copy: all six fits hang dts_aim-260 and the two anti-ship fits hang dts_agm-158c-3, neither of which the pack ships. Unsubscribed, every SEST Rafale fit …
- 3737267013 — United States Naval Aviation (misaka). SOFT but visible: supplies assets/models/ammunition/agm-88/agm-88g.obj, the real mesh behind sest_aim-424. Without it the MALICE renders as the AssetBundleMesh=usn_rim-7 Sea Spa…
- 3606774881 — U.S. Navy 2027 Capabilities mod (Prof_CH4OS). REFERENCE ONLY: the AIM-424's flight model was aligned to its usn_aim-174b so the two encyclopedia cards read on the same assumptions. Nothing breaks if it goes; the bala…
- integration/common/aim424.py — internal. build_patch.py imports AIM424_ID and write_aim424 from it; the missile is not defined in this pack.
- tools/consolidate_packs.py — the per-pack folder is a build unit, not the deployed artifact. Only integration/dist/SEST_Integration is installed (tools/install-sest-packs.ps1).

**Known limits**

- Whole-file override exposure: the three fr_rafale_*_l.ini files are full snapshots of misaka's 909/918/930-line originals. Any upstream fix to those airframes is hidden until build_patch.py is re-run — docs/design-notes.md, 'Upst…
- Builder documentation has drifted from builder behaviour on Meteor. The module docstring still says 'Wingtip MICA-IR, the donors' Meteors and the tanks stay' and 'the two SCALP-EG ... become AIM-424 on the same SCALP seat' — both…
- The AIM-424 cannot be visually resized from the ini: 'The visual renders at the shared usn_rim-7 mesh's native size ... and cannot be resized from the ini (ResourcesMeshScale, the one candidate key, breaks the model).' Only the […
- SEST_Intercept260F5 may show the same wing-tank/AIM-260 clip that forced the Heavy fit to shed its tanks; the recorded position is that if it appears, the fix is a seat offset for the rail rounds, not a tank removal (commit 1d597…
- Cosmetic build artifact: derive() captures a donor block up to the next '[', so SEST_Intercept260Heavy — cloned from the last block before a section comment — carries a stray '#---------- Anti-Surface ----------' line at the end …
- English-only loadout names; ApproximateVersion left at 0.8.1 while the rest of the collection is at 0.8.2.

### `jmsdf-mogami`

Reconciles the standalone Mogami-class frigate mod with the Euromod JMSDF pack by replacing the frigate's USN SH-2F air group with the JMSDF SH-60K and admitting both Euromod Seahawks, so a JMSDF ship stops flying an American helicopter when the two mods are subscribed together.


**Files (4)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `integration/jmsdf-mogami/SEST_JMSDF_Mogami/vessels/…` | overrides | 3456859157 — "Mogami-class Frigate" (ca… | It is the only source of the file anywhere in the collection: `ls mods-source/*/vessels/js_ffg_mogami.ini` returns exactly one hit (3456859157), and … |
| `integration/jmsdf-mogami/SEST_JMSDF_Mogami/_info.ini` | adds | none — written verbatim from the builde… | Pack manifest, not donor content. Carries the load-order instruction ("Place ABOVE the Mogami mod in the Mod Manager") and ApproximateVersion=0.8.2. |
| `integration/dist/SEST_Integration/vessels/js_ffg_mo…` | merges | consolidated by tools/consolidate_packs… | The deployable is the single consolidated pack: dist/_info.ini reads "All SEST content as one pack, so a single Mod Manager entry at the top of the l… |
| `aircraft/jp_sh-60k.ini and aircraft/jp_sh-60j.ini (…` | adds | 3695809489 — "Euromod - Modern Japanese… | Sole shipper of JMSDF Seahawks in the 133-mod export: `ls mods-source/*/aircraft/jp_sh-60*` returns only 3695809489 (jp_sh-60j, jp_sh-60k and their _… |

**Decisions (15)** — File semantics 7, Upstream donor 3, UNSTATED 3, Real-world spec 1, Engine precedent 1


- **Rebase the patch on the standalone Mogami mod's own vessel file rather than authoring a ship, changing only 2 of 4,231 lines.**  
  *File semantics* — build_patch.py: `src = MOGAMI / "vessels" / "js_ffg_mogami.ini"` with guard `sys.exit("Mogami donor vessel not found — re-export mods-source")`. docs/design-notes.md: "Unit files are whole-file overrides. For aircraft/, vessels/, submarines/, land_units/, ammunition/, biologic/, ui/, the highest mod's copy loads and the rest are *gone* —…
  
  Effect: Nothing about the hull, sensors, Mk41 VLS, RAM, 127 mm gun or damage model changes; the ship the player gets is the donor's ship with a different helicopter.
  
  If the donor changes: Unsubscribing 3456859157 leaves the pack's .ini pointing at a hull mesh that no longer exists. docs/collection-cleanup.md line 24: "Mogami-class frigate (3456859157) — SEST JMSDF Mogami is …

- **Swap the embarked helicopter from usn_sh-2f to jp_sh-60k.**  
  *Real-world spec* — build_patch.py docstring: "The standalone Mogami mod embarks a USN SH-2F Seasprite; the real FFMs fly the SH-60 family, and the Euromod JMSDF pack ships jp_sh-60k/jp_sh-60j. This patch overrides the vessel to embark an SH-60K". Donor line replaced: `usn_sh-2f=Default,1` -> `jp_sh-60k=Default,1`.
  
  Effect: The Mogami's single hangar slot (donor `AircraftCapacity=1`) now launches a JMSDF SH-60K instead of a 1970s USN Seasprite: 146 kt vs 138 kt MaxSpeedAtSeaLevel, and the K's station table add…
  
  If the donor changes: If Euromod JMSDF is unsubscribed the [AirGroup] names a unit nothing defines; the hangar has no valid default aircraft, and only the retained usn_sh-2f entry in AircraftSupported is still r…

- **Replace the entire [AirGroup] block, not just the aircraft line, keeping the donor's own `=Default,1` slot syntax.**  
  *Upstream donor* — build_patch.py: `re.subn(r"\[AirGroup\].*?(?=\n\[)", "[AirGroup]\njp_sh-60k=Default,1\n", text, count=1, flags=re.S)`. The `Default,1` form and the count of one are cloned from the donor's `usn_sh-2f=Default,1`, and match the donor's `[FlightDeck] AircraftCapacity=1`.
  
  Effect: Exactly one embarked helo, as upstream — no capacity inflation.
  
  If the donor changes: Fragile against upstream growth: the rewrite discards whatever the block contained. If the mod author later adds a second entry (a second helo, a UAV), the pack silently drops it — the guar…

- **Set AircraftSupported=jp_sh-60k,jp_sh-60j,usn_sh-2f — add both JMSDF Seahawks and keep the SH-2F.**  
  *Upstream donor* — build_patch.py: `re.subn(r"^AircraftSupported=.*$", "AircraftSupported=jp_sh-60k,jp_sh-60j,usn_sh-2f", ...)` replacing the donor's `AircraftSupported=usn_sh-2f`. The only stated reason for retaining the Seasprite is the parenthetical "(the SH-2F stays supported for compatibility)" in the docstring, README and _info.ini — the compatibilit…
  
  Effect: The player can re-equip the Mogami with the SH-60K, the SH-60J or the vanilla SH-2F; missions or saves written against the old usn_sh-2f id still validate.
  
  If the donor changes: The usn_sh-2f entry is vanilla-backed and survives any mod being removed; the two jp_ entries go dangling with Euromod JMSDF.

- **Make the SH-60K the embarked default and leave the SH-60J as a selectable alternative only.**  
  ***UNSTATED*** — No recorded justification. The builder treats the two symmetrically as a precondition (`for helo in ("jp_sh-60k", "jp_sh-60j")`) and the docstring asserts the outcome without comparing them: "This patch overrides the vessel to embark an SH-60K". docs/design-notes.md contains no Mogami, SH-60 or JMSDF entry at all (grep for mogami|sh-60|j…
  
  Effect: Determines which helo spawns without player intervention in every mission that places a Mogami.
  
  If the donor changes: Trivially editable, but a reviewer cannot check the choice against any recorded criterion.

- **Take the helos from Euromod JMSDF (3695809489) rather than from any other Seahawk-shipping mod, and reference them rather than shipping copies.**  
  *Upstream donor* — Docstring: "the Euromod JMSDF pack ships jp_sh-60k/jp_sh-60j". README: "With Euromod JMSDF's Asahi/Atago/Maya, the Mogami completes the modern JMSDF surface line." Verified sole provider of the jp_ ids; competing Seahawks in the export (usn_sh-60b, usn_sh-60f, spa_sh-60b from 3731208477 "Euromod - Modern Spanish Navy") are other navies. …
  
  Effect: The embarked helo is Euromod's JMSDF model with its own sensors and stores, kept up to date by its author.
  
  If the donor changes: Because the pack ships zero aircraft files, an Euromod JMSDF update improves the helo for free — but removing that mod breaks the air group with no fallback beyond the vanilla SH-2F.

- **Install above the Mogami mod, as part of the unbroken SEST_Integration Tier 0 block at the top of the Mod Manager.**  
  *File semantics* — _info.ini: "Place ABOVE the Mogami mod in the Mod Manager." README: "Order: above the Mogami-class Frigate mod." data/load-order.tokens.txt header: "INVARIANT: every SEST_* pack sits above every workshop mod... if anything outranks it the patch silently does nothing." tools/check_load_order.py docstring: "Move anything above it and the p…
  
  Effect: Ordering is the difference between the SH-60K air group applying and the game silently loading the donor's SH-2F version instead.
  
  If the donor changes: Any reorder that lifts 3456859157 above SEST_Integration reverts the ship to the SH-2F with no error message; check_load_order.py is the only thing that catches it, and only pre-push.

- **Ship through the consolidated SEST_Integration pack rather than as a separate Mod Manager entry.**  
  *File semantics* — tools/consolidate_packs.py; integration/dist/SEST_Integration/_info.ini: "All SEST content as one pack, so a single Mod Manager entry at the top of the list carries every patch. Consolidated from: ... SEST JMSDF Mogami ...". Verified the dist copy of vessels/js_ffg_mogami.ini is byte-identical to the pack's. The installed game copy also …
  
  Effect: One top-of-list entry carries the Mogami fix along with 15 other packs; no per-pack ordering for the player to get wrong.
  
  If the donor changes: Rebuilding dist without this pack drops the override; the standalone SEST_JMSDF_Mogami directory remains installable on its own.

- **Declare ApproximateVersion=0.8.2 in the pack manifest.**  
  *Engine precedent* — Commit 673e50b: "Every SEST pack declared ApproximateVersion=0.6.8 against a 0.8.x game. That check requires MAJOR and MINOR to match, so all seven packs were failing it. Now 0.8.2, matching the rebase sources." The rule is documented in the donors' own manifests — both 3456859157 and 3695809489 carry the stock comment ";ApproximateVersi…
  
  Effect: The pack is accepted by the Mod Manager's compatibility check instead of being rejected/warned on a 0.8.x build.
  
  If the donor changes: A game update to 0.9.x invalidates this string for every pack at once; it is a manifest literal in the builder, not derived from the donors.

- **Read the donor as utf-8-sig and write the pack as LF-pinned utf-8.**  
  *File semantics* — build_patch.py: `src.read_text(encoding="utf-8-sig", errors="replace")`. Commit 41930a8: "74 exported upstream .ini files carry a UTF-8 BOM, and reading one with encoding=\"utf-8\" keeps it as a leading character that is then spliced into the pack. All 15 builders now read donors as utf-8-sig." .gitattributes pins `*.ini text eol=lf` bec…
  
  Effect: None directly; prevents a stray U+FEFF at the top of the vessel file, which would corrupt the first key the game parses.
  
  If the donor changes: Defensive only — this pack's output bytes were not changed by the fix; a future re-export of a BOM-carrying Mogami update would be handled correctly.

- **Fail loudly on upstream drift instead of producing a silently wrong pack.**  
  *File semantics* — Three guards in build_patch.py: `sys.exit("Mogami donor vessel not found — re-export mods-source")`, `sys.exit(f"JMSDF helo not found: {helo}")`, `sys.exit("no [AirGroup] block found — upstream layout changed")` and `sys.exit("no AircraftSupported line found — upstream layout changed")`. Matches docs/design-notes.md: "Everything is gener…
  
  Effect: A donor rename or restructure stops the build rather than shipping a Mogami with a broken or unpatched air group.
  
  If the donor changes: The guards cover presence, not content: an upstream change that keeps both keys but rewrites the hangar (see the [AirGroup] block-rewrite risk) passes all four.

- **Depend on Euromod JMSDF entirely through prose (README + _info.ini) — the automated dependency gate cannot see it.**  
  *File semantics* — tools/check_dependencies.py reports only: "SEST_JMSDF_Mogami / overrides 1 file(s) Mogami-class frigate (3456859157) / references 2 file(s) Gerald R. Ford-class CVN (3461044389)" — no Euromod JMSDF row. The checker extracts stores via `^Station\d+=([A-Za-z]\S*)` and `^Ammunition\d*=(\S+)` and rosters via `^([A-Za-z0-9_.\-]+)=Squadron\d+,…
  
  Effect: A collection pruned of Euromod JMSDF passes every automated gate and still ships a Mogami whose default air group cannot spawn.
  
  If the donor changes: Only the build-time guard `sys.exit(f"JMSDF helo not found: {helo}")` catches it, and only for whoever rebuilds the pack — never for the player.

- **Accept the donor's inherited store references (ESSM/RAM) unexamined as part of the whole-file copy.**  
  *File semantics* — The pack's copy carries `Ammunition1=usn_rim-162` (Count=32), `Ammunition1=usn_rim-116` (Count=42), `usn_rur-5`, `usn_cal_127mm`, `usn_mk46_ship`. check_dependencies resolves two of those winning files to 3461044389 "Gerald R. Ford-class CVN", reported as "references 2 file(s)". Nothing in the builder or README mentions this; it follows …
  
  Effect: The Mogami's ESSM and RAM magazines behave according to whichever mod currently wins ammunition/usn_rim-162.ini and usn_rim-116.ini, not according to anything this pack chose.
  
  If the donor changes: Removing the Ford mod moves those ammunition definitions to the next-highest provider (or vanilla); the pack does not pin them.

- **Document "+ Euromod Main" as a requirement in the README.**  
  ***UNSTATED*** — README: "Requires: Mogami-class Frigate mod · Euromod JMSDF (+ Euromod Main)." But data/mod-catalog.json records for 3695809489: requires = ["euromod-main (inferred from Euromod addon naming; not stated in the truncated description)"] — the repo itself flags this as an inference, not an author mandate. Sibling Euromod entries (Nordic 364…
  
  Effect: Tells the player to subscribe a mod whose necessity to this specific chain has not been confirmed.
  
  If the donor changes: If the inference is wrong, the instruction is merely surplus; if it is right and ignored, the Euromod JMSDF helos may fail to load with no message from any checker.

- **Leave unexamined that the embarked SH-60K's materials resolve out of a third mod's asset tree.**  
  ***UNSTATED*** — mods-source/3695809489/aircraft/jp_sh-60k.ini uses `ResourcesFolder=assets/models/aircraft/sh60/` with `ResourcesMesh=h60_hull_a` plus 25 `ResourcesMaterialFolder=assets/models/aircraft/sh60/` lines, yet Euromod JMSDF's own asset tree contains only assets/models/aircraft/jp_mh-60r/. The sole assets/models/aircraft/sh60/ directory in the …
  
  Effect: If the sh60 material folder's provider is absent, the helo this pack embarks may render untextured or fail to load, while the Mogami itself looks fine.
  
  If the donor changes: Unsubscribing US Naval Aviation (3737267013, load-order line 59) is currently a silent risk to this pack's air group that no gate and no doc flags.

**Must stay subscribed**

- 3456859157 "Mogami-class Frigate" — MANDATORY. Supplies the hull, mesh and the 4,231-line file the pack rewrites. Without it the pack's vessel .ini defines a ship with no model. docs/collection-cleanup.md: "SEST JMSDF Mogami is b…
- 3695809489 "Euromod - Modern Japanese Maritime Self Defence Force" — MANDATORY at runtime, and the entire point of the pack. Supplies jp_sh-60k (the embarked default) and jp_sh-60j. Without it the Mogami's [AirGroup] names an und…
- 3629144864 "Euromod - Main Pack" — claimed by the README ("+ Euromod Main"), but data/mod-catalog.json marks this requirement for 3695809489 as "inferred from Euromod addon naming; not stated in the truncated description". Treat …
- 3737267013 "US Naval Aviation" — UNDECLARED and undocumented. Owner of the only assets/models/aircraft/sh60/ folder in the export, which jp_sh-60k.ini's ResourcesFolder and 25 ResourcesMaterialFolder lines point into. Removing it…
- 3461044389 "Gerald R. Ford-class CVN" — INHERITED, not chosen. check_dependencies reports "references 2 file(s)" for this pack: the donor's usn_rim-162 (ESSM, 32 rounds) and usn_rim-116 (RAM, 42 rounds) magazine definitions curre…
- vanilla usn_sh-2f — NOT a dependency. mods-source/_vanilla/original/aircraft/usn_sh-2f.ini ships with the base game, so keeping it in AircraftSupported costs nothing and always resolves.

**Known limits**

- One helo, always: the donor's [FlightDeck] AircraftCapacity=1 caps the air group, so the patch swaps the type but cannot add a second airframe.
- The [AirGroup] rewrite is a whole-block replacement with count=1 and no entry-count guard. If the mod author later lists additional aircraft in that block, the rebuild silently discards them — the guards only fire when the block …
- The pack ships no language_en file, so the ship's displayed name and description stay owned by the Mogami mod's (merging) language files. This is deliberate per design-notes ("Language merging is how packs rename other mods' unit…
- The pack's hardest dependency — Euromod JMSDF — is invisible to tools/check_dependencies.py, which parses only Station/Ammunition stores and `uid=SquadronN,n` rosters. Air-group and AircraftSupported entries match none of its pat…
- The pack declares ApproximateVersion=0.8.2 while both donors declare 0.8.0. Compatible today (the check matches MAJOR.MINOR and accepts a higher PATCH), but the pack's version is a hand-set literal in the builder, not derived fro…
- mods-source is a text-only export (0 .obj files), so which mod owns the SH-60 mesh binary cannot be proven from the repo; the sh60 material-folder evidence points at US Naval Aviation but stops short of proof.
- The choice of SH-60K over SH-60J as the default embark, and the specific compatibility scenario that the retained usn_sh-2f entry protects, are both unrecorded — the two airframes are identical in Role and MaxSpeedAtSeaLevel, so …

### `tacmap-colors`

Vanilla's translucent dark-blue waypoint lines (ARGB 100,0,0,220) collapse into an unreadable tangle once a mission carries many routes, so this pack regenerates the whole vanilla tactical-map UI file with opaque, thickened waypoint lines (black by day / white by night), a distinct selected route, and faded formation tethers — a readability fix that has to be shipped as a complete file because ui/ is a whole-file override domain.


**Files (3)**

| File | Action | Donor | Why this donor |
|---|---|---|---|
| `integration/tacmap-colors/SEST_TacMap_Colors/ui/Def…` | overrides | None — base game. Donor is the vanilla … | No competing donor exists. A repo-wide search (find mods-source -ipath "*Settings_UI_Tactical.ini") returns only mods-source/_vanilla/original/ui/Def… |
| `integration/tacmap-colors/SEST_TacMap_Colors/_info.…` | adds | None — generated from the INFO template… | Mod Manager metadata for the pack itself; ApproximateVersion=0.8.2 matches the exported game build and the stamp used by 12 of the 14 sibling builder… |
| `integration/dist/SEST_Integration/ui/Default/Settin…` | adds | The pack's own output, copied by tools/… | SEST TacMap Colors is the only SEST pack shipping any ui/ file, so consolidation has no colliding path to resolve (consolidate_packs.py: "anything el… |

**Decisions (12)** — UNSTATED 5, File semantics 4, Engine precedent 2, In-game observation 1


- **Rebase on the vanilla game export rather than on any workshop mod — the pack has no upstream mod donor at all.**  
  *Engine precedent* — build_pack.py:30 `VANILLA = ROOT / "mods-source" / "_vanilla" / "original"`, plus the collection survey: `find mods-source -ipath "*Settings_UI_Tactical.ini"` matches only the vanilla export across all exported mods; the 12 mods that ship a ui/ folder ship Settings_UI_General.ini / layout.ini / minimap.ini instead. docs/packaging-and-rec…
  
  Effect: The colour scheme applies in every mission regardless of which content mods are subscribed; nothing else in the collection contests the file.
  
  If the donor changes: Nothing to lose from unsubscribing a mod — there is no donor mod. The exposure is a game patch: a 0.8.3 rewrite of the file would be masked by this override until the pack is rebuilt from a…

- **Ship the complete 167-line file, not a fragment, and hard-fail the build if the output is short or a different length than the donor.**  
  *File semantics* — build_pack.py:102-107 — "# Sanity: we shipped the whole file, not a fragment (unit inis are whole-file overrides and the UI file behaves the same way)." followed by `if out_lines != src_lines or out_lines < 150: sys.exit(f"output looks truncated: ...")`. Backed by docs/design-notes.md: "Unit files are whole-file overrides. For `aircraft/…
  
  Effect: Because the whole file loads, the pack also pins vanilla's [TacticalMap_Geometry] (MapSize=400,400, MapPosition=12,42, MapInitialZoom=8, all other line thicknesses), [FormationManager_Geome…
  
  If the donor changes: If the game patches any unrelated key in that file (a new cursor, a changed map default), the shipped copy silently keeps the old value. docs/design-notes.md: "Upstream moves under you. A s…

- **Refuse per-domain (air vs surface vs ground) waypoint colouring — declare it impossible through data.**  
  *Engine precedent* — build_pack.py:9-13 — "IMPORTANT - THERE IS NO AIR/GROUND SPLIT. The game exposes exactly one waypoint line colour (WaypointsLineColor) plus a night variant and a selected-waypoint colour. Nothing in ui/ distinguishes an aircraft's route from a ship's or a ground unit's, so a per-domain colour is not possible through data alone - it would…
  
  Effect: Every route on the tactical map — strike package, surface group, ground column — draws in the same colour. The only axis of separation delivered is day vs night and selected vs unselected.
  
  If the donor changes: Not reversible by data; would require a code mod (Anchor Chain family) rather than an ini override.

- **Force waypoint lines fully opaque: WaypointsLineColor 100,0,0,220 -> 255,0,0,0 and NightWaypointsLineColor 100,107,207,255 -> 255,255,255,255.**  
  *In-game observation* — build_pack.py:4-7 — "Vanilla draws waypoint lines as ARGB 100,0,0,220 - a dark blue at 39% alpha - which turns into an unreadable dark tangle once a mission has a lot of routes on screen." Commit 76575f1 repeats it. Arithmetic checks out (100/255 = 39.2%) and the donor value is confirmed by diff. CAVEAT: the tangle is asserted as observe…
  
  Effect: Routes read at full opacity on a busy map instead of fading into each other and into the map background.
  
  If the donor changes: Self-contained; unaffected by any mod. Reverts only if some future mod is placed above SEST_Integration and ships the same file (none currently does).

- **Use the game's automatic day/night pair as the default (`--waypoints auto`) instead of one fixed colour, with `--waypoints black|white` as an escape hatch that forces both.**  
  *File semantics* — build_pack.py:14-17 — "What CAN be separated is day vs night: the game swaps to the Night* set automatically, so black is used by day and white at night by default, which keeps the lines readable against both map backgrounds." The donor file structurally confirms the mechanism: a complete parallel Night* block at lines 55-99 mirroring ev…
  
  Effect: Lines flip black -> white when the map switches to its night palette, with no player action.
  
  If the donor changes: Rebuild with `--waypoints black` or `--waypoints white` to pin one colour. Note tools/build_all.py invokes the builder with no arguments, so the committed output is always the `auto` / thic…

- **Choose black for day and white for night specifically (rather than, say, yellow/magenta or the vanilla blue at full alpha).**  
  ***UNSTATED*** — The only recorded justification is the inline comment at build_pack.py:75 — `else: # auto: whichever reads better on each background` — an assertion with no measurement, screenshot, or reference behind it. Nothing in docs/design-notes.md, docs/setup-runbook.md or commit 76575f1 records a comparison of candidate colours. (Unremarked by th…
  
  Effect: Routes are solid black on the day map and solid white on the night map.
  
  If the donor changes: Cosmetic and rebuildable; nothing depends on it.

- **Keep the selected route visually separate: WaypointSelectedColor=255,255,0,0 (identical to vanilla — an idempotent rewrite) and NightWaypointSelectedColor 255,245,131,130 -> 255,255,80,80.**  
  ***UNSTATED*** — build_pack.py:81-83 — "# Keep the selected route obviously distinct from the rest." states intent only. The day write is a no-op (diff shows line 21 unchanged against vanilla), so only the night value is a real change, and the specific value 255,255,80,80 has no recorded derivation.
  
  Effect: The selected unit's route stays red (day) / light red (night) while all other routes go black or white, so the route you are editing pops out of the mass.
  
  If the donor changes: Cosmetic. Note the day red 255,255,0,0 is the same value the donor uses for HostileColor and WeaponMaxRangeColor, so a selected route shares the map's hostile red.

- **Fade formation membership tethers rather than recolour them: alpha 64 -> 48 on both FormationMembershipLineColor (0,0,255) and NightFormationMembershipLineColor (107,207,255), hues untouche…**  
  ***UNSTATED*** — build_pack.py:84-86 — "# Formation tethers share the tangle; make them faint so routes dominate." Intent recorded; the choice of 48 (a 25% alpha reduction) has no stated derivation, and FormationMembershipLineThickness=1 in [TacticalMap_Geometry] is deliberately left alone without comment.
  
  Effect: Formation tethers recede behind the now-opaque routes instead of competing with them.
  
  If the donor changes: Cosmetic; rebuild to change.

- **Thicken waypoint lines from vanilla 1 to 1.5, exposed as a `--thickness` parameter.**  
  ***UNSTATED*** — build_pack.py:62-63 — `ap.add_argument("--thickness", type=float, default=1.5, help="waypoint line thickness (vanilla 1)")`, written into [TacticalMap_Geometry] WaypointLineThickness at line 87. The vanilla baseline of 1 is verified by diff (donor line 112: WaypointLineThickness=1). Why 1.5 rather than 2 is recorded nowhere; the docstrin…
  
  Effect: Routes are 50% wider on the tactical map — more legible when zoomed out, marginally more clutter when zoomed in.
  
  If the donor changes: Rebuild with `--thickness N`; overwritten back to 1.5 by any later tools/build_all.py run.

- **Fail the build loudly if any targeted key is missing from the donor, and stamp Mod Manager compatibility at ApproximateVersion=0.8.2.**  
  *File semantics* — build_pack.py:48-55 — `set_key` docstring "Replace key=... , keeping any trailing comment. Fails loudly if absent." with `sys.exit(f"{key} not found in {REL} — upstream layout changed")`; plus the missing-donor guard at 67-68 ("vanilla file missing (re-export mods-source?)"). The 0.8.2 stamp (INFO template, line 44) matches the exported …
  
  Effect: None directly; it converts a silent vanilla-layout drift into a build failure before a broken file can be installed.
  
  If the donor changes: If the game renames or drops a key (e.g. in 0.8.3), the build stops rather than shipping a stale file — but only if someone re-exports the vanilla files and reruns the builder.

- **Treat load-order position as forgiving: the pack needs no specific rank beyond the project-wide Tier 0 rule.**  
  *File semantics* — _info.ini (generated, build_pack.py:99): "Place ABOVE nothing in particular; it only overrides the vanilla UI file." docs/setup-runbook.md:163: "`SEST_TacMap_Colors` only overrides a vanilla UI file, so it is equally forgiving", and its row in the target order table at line 189: "SEST TacMap Colors ← overrides the vanilla tactical-map UI…
  
  Effect: Reordering any workshop mod cannot disable the colour scheme — unlike the unit-file packs, which go inert if outranked.
  
  If the donor changes: Would only matter if a future workshop mod started shipping ui/Default/Settings_UI_Tactical.ini; SEST_Integration's top placement already wins that contest.

- **Ship alongside Better TacMap (3768036424) with no recorded compatibility check.**  
  ***UNSTATED*** — Better TacMap is #5 in data/load-order.tokens.txt (3768036424) and catalogued in data/mod-catalog.json as "VERIFIED: pure code mod (settings.cfg only in export) — Anchor Chain family UI overhaul", described by its author as "Adds additional information to the tactical map" and stamped ApproximateVersion=0.8.1. Its settings.cfg carries a …
  
  Effect: Presumed none: a code mod drawing extra contact readouts over a tactical map whose colours this pack sets. Unverified whether Better TacMap re-reads or overrides TacticalMap_Colors at runti…
  
  If the donor changes: If Better TacMap does override these colours in code, this pack's changes would be invisible with it enabled and would reappear on unsubscribing it — untested either way.

**Must stay subscribed**

- None at runtime beyond the base game — docs/packaging-and-recovery.md: "SEST_TacMap_Colors needs nothing but the base game". Unsubscribing any workshop mod cannot break it, and tools/check_dependencies.py lists nothing for it.
- Build-time only: mods-source/_vanilla/original/ui/Default/Settings_UI_Tactical.ini must be present, or the builder exits with "vanilla file missing (re-export mods-source?)". Regenerate via tools/export-mod-configs.ps1 from the g…
- Deployment: the pack reaches the game only through integration/dist/SEST_Integration (tools/consolidate_packs.py -> tools/install-sest-packs.ps1). That single Mod Manager entry must stay at the top of data/load-order.tokens.txt p…

**Known limits**

- ONE waypoint colour, engine-imposed. Air, surface and ground routes cannot be separated through data: the engine exposes only WaypointsLineColor / NightWaypointsLineColor / WaypointSelectedColor (+ night). Per-domain colouring "w…
- Whole-file override freezes the rest of the tactical UI. Shipping all 167 lines to change 7 also pins vanilla's [Cursors] pointer table, [TacticalMap_Geometry] map size/position/zoom and remaining line thicknesses, [FormationMana…
- The selected-route red (255,255,0,0) is the same red the donor file already uses for HostileColor and WeaponMaxRangeColor; the night value 255,255,80,80 sits close to NightHostileColor 255,245,131,130. A selected route and hostil…
- tools/check_load_order.py would not catch a future contest over this file: it collects override files with `if p.parent.name in OVERRIDE_DIRS` (line 50/66), and this file's parent directory is `Default`, not `ui`, so the pack con…
- No screenshot or in-game verification is recorded for any colour choice, despite docs/design-notes.md making screenshots the tiebreaker ("When a rule and a screenshot disagree, the screenshot wins"). The readability claims rest o…
- The pack has no README.md — build_pack.py's docstring and the generated _info.ini description are the only documentation.
- Only the ui/Default profile is shipped. The vanilla export also contains ui/Test/Settings_UI_Tactical.ini, but that file is empty (0 lines), so nothing is lost by not overriding it.
- Interaction with Better TacMap (3768036424), a code-level tactical-map overhaul in the same load order, is untested; its exported settings.cfg contains no colour keys, which is suggestive but not proof.
