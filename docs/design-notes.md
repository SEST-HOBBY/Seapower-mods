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
  corpus — the five size bonuses and the clamp — so none of the 541
  anti-air-capable rounds could opt out of losing them. The other two,
  `InterceptOutOfAltitudePenalty` and `InterceptSpeedPenaltyMultiplier`, are
  declared per round in 161 and 176 ammunition files; the rest inherited
  nothing. Counts from `tools/survey_attack_altitudes.py`; re-run it after any
  export or reorder rather than trusting these. That mod wanted to change two impact-size values. `SEST_Intercept_Model`
  restores the table; `integration/intercept-model/build_patch.py` records what
  arming the clamp changes and which rounds needed fixing first.
  Measured, not observed in game: it was found by diffing the winning copy
  against vanilla, not by anything looking wrong on screen. Check global tables
  the same way you check units.
- **An absent band is not the same as a zero — an absent *bound* is still
  open.** Three stock AAW missiles (`fr_super-530f`, `pla_pl-2`, `pla_pl-2b`)
  declare no attack-altitude band at all and have always shipped against a
  `damage.ini` where the 5% clamp is live, so a missing band cannot default to
  zero or they would be permanently clamped. That settles the both-absent case
  only. It does not settle the 68 modded rounds that declare *one* side and no
  vanilla file does: an engine may skip the check when neither bound is present
  yet still run it against a defaulted other side. Untested; fire an AMRAAM
  (floor only) and a RAM (ceiling only) and read the percentage.
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
  track is left over from an unsubscribe. `capture-context.ps1` now reports both
  directions, with `NeedsDownload` and `NeedsUpdate`.
- **The Steam UI's subscribed count is server-side and can legitimately be higher
  than both.** Subscribed Collections have no content to download, and an item the
  author delists stays in your subscription count forever. Neither can load, so
  neither belongs in the load order.

Earned twice in one session: the repo reported 138, the Mod Manager agreed at 138,
and Steam said 140. Nothing was wrong. Before chasing a count, say which of the three
you are quoting.

## What an editor round-trip keeps, and the one thing it silently rewrites

Saving a mission in Sea Power's own editor rewrites every section from the editor's
in-memory model. The save is not a diff, so the question is never "did it change the
file" - it is "which of our intent survived the model". Measured on `SEST Banda Front
Lean v2` (`b1c6ee1e` -> `a30a8b04`, three units added, ~90 nudged): 606 insertions
against 734 deletions, a net loss of 128 lines while gaining three units.

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
  free. Nothing warned: the unit count was right and preflight resolved all 879
  references, because every reference was still valid. Only the intent was gone.

`integration/missions/restore_roe.py` restores it from the last committed copy, and
should be run after every editor save. Run it before the commit, not after.

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

- **The export must mirror deletions, or the repo lies.** For a day the repo
  showed Modern US Navy's `usn_ddg_burke_f3.ini` and U.S. Navy 2027's
  `usn_rim-162e.ini` as present while the game logged both as not found: the
  exporter copied files in and pruned unsubscribed mods, but never deleted a
  file an author had removed inside a mod, so every checker resolved against
  ghosts and passed. It mirrors within each mod now. The tell was git: the
  ghost files' last commit predated the export that touched their neighbours.
- **A mod made only of `#!alias` patches breaks whenever its base mod renames
  a hull.** U.S. Navy 2027 aliases every ship onto a Modern US Navy hull, and
  Modern US Navy pushed ten renaming updates in three days (v558-567, 16-18
  Sep 2026). The Flight III base was retired twelve hours after 2027's last
  fix, and the game died at startup with KeyNotFoundException 'AirGroup' -
  the patch's own [FlightDeck] asking for the air group the missing base
  carried. `tools/check_alias_bases.py` names this before launch, and the
  missions field the Modern US Navy hulls directly now
  (`retarget_usn2027_hulls.py`). Re-pointing a patch at a re-laid-out base is
  not a fix - slot 2 had become the Phalanx - so SEST_USN2027_Fixes flattens
  old base plus patch into one standalone hull until the author catches up.
  The author caught up on 2026-09-20: the 2027 patch now aliases
  `usn_ddg_burke_f3_125.ini`, the hull Modern US Navy really ships, so the
  pack's own guard said RETIRE THIS PACK and it is gone - the guard that
  knows when its fix is obsolete is the whole point of writing one.

- **Gates before every push:** `check_load_order`, `check_dependencies`,
  `preflight` (every reference the missions make), `check_station_clash`,
  `check_weapon_employment` (every weapon can actually be fired by the mount
  carrying it), full pack rebuilds. All exit non-zero; all have been
  negative-tested — the employment gate against both bugs it was built from,
  the stripped NSM datalink association and the GBU-53's 200 ft release band.
- **Air wings on land units.** A mission gives an airbase its aircraft with `CustomAirGroup=True`
  followed by `<aircraft id>=SquadronN,count|SquadronM,count` lines inside the land-unit block;
  the squadron numbers index the aircraft's `_squadrons.ini`, and vanilla single-livery types use
  `Default`. Only units whose file carries `[AirGroup]`/`[FlightDeck]` (LandUnitSubType=Airbase,
  the helo rig) can take one; the showcase generator refuses an air group on anything else.
- **Shipping lanes are routed, not drawn.** Hand-placed waypoints crossed land in 20 of 27 lanes
  on the first try (Kangean, the Leti islands, Dolak, Jolo, Timor's south coast). `sea_routes.py`
  takes via points that name the corridor and finds the water path between them on the land mask
  (A*, 0.025° grid, no corner-cutting past land, a 60% cost penalty on cells touching land so
  lanes stand a mile or two off the beach). Simplification is per leg so via points survive: a
  whole-chain simplification turned the Lombok–Makassar VLCC lane into one straight line hugging
  the Sulawesi coast, legal on the mask and wrong as a lane.
- **A deletion mirror needs an absolute destination and a sanity bound.** The exporter's new
  "remove files the mod no longer ships" loop compared `FullName` (absolute) against a
  `$DestDir` still holding a literal `..\`, so no exported file ever matched the keep-set and
  the first run deleted 7,876 of them - every mod but the twelve whose ids sort last. It now
  normalises `$DestDir` with `GetFullPath`, skips a mod that copied nothing, and refuses to
  delete more than half of a mod's exported files (above 20) on the grounds that an update
  retires a handful, never most: a mirror that can empty the repo is worse than a ghost file.
- **A mod can delete a round and leave the hulls that load it.** U.S. Navy 2027 removed
  usn_rim-162e on 15 Sep 2026; seventeen of its own Burkes still name it in a Mk 41 magazine,
  which the game logs as "could not find" and the cell never fires. Missions avoid this by
  fielding the Modern US Navy hulls instead; the one hull SEST ships flattened re-points the
  magazine at Euromod's identical RIM-162H, guarded both ways (the original must still be
  gone, the substitute must resolve).
- **Hand-placed ships need the land mask too.** The land units go through the mask, so nobody
  checked the vessels: the Darwin surface group had been parked on the Tiwi Islands and a US
  destroyer on Palawan since the showcase was written. Both generators now refuse to write a
  mission with a vessel ashore. A warship must also clear a 6 nm halo, since a position can be
  a water cell and still be a beach the group cannot manoeuvre in; a merchant only has to be on
  water, because a ferry legitimately starts alongside.
- **Anchor Chain has two layering directives, not one.** `#!alias` replaces a whole unit;
  `#!extend` merges a few keys onto the file of the SAME name one rung lower in the load order.
  Seventy-eight ammunition files across three mods use `#!extend` and nothing checked them, even
  though they break exactly the way the alias that crashed the game did. Resolving an extend
  needs the load-order *stack*, not the winner: `winning_file` on a same-name target returns the
  patch itself and loops. `refine_civ_traffic.file_stack` returns every copy in order, and the
  checker takes the entry below the patch.
- **An extend only applies if it outranks what it extends.** A mod the catalog does not list is
  appended at the bottom of the order, which is fatal for an expansion pack whose whole content
  is extends: the PLA AEP pack sat below every mod it patches and did nothing at all.
- **Severity follows the file kind.** A unit file with no base is the startup crash, because the
  loader cannot build the unit. A round with no base only means that weapon never fires, which
  the game survives, so the checker reports it and still exits zero.
- **A guard that says "rebase this" should retire the fix itself when it can.** Five packs were
  wedged because their guards treated "upstream fixed it" as a build failure. A guard can tell
  the two apart: if the defect the fix targets is gone from the donor, stop overriding that file
  and say so, and only fail when every target of a fix is clean (then the fix itself is
  obsolete). The P-8 Harpoon typo, the F/A-18E tanker port, the AIM-9M and the MH-60R Penguin
  seat all retired themselves this way, and the Ocean's Apache line stopped failing every time
  the author added an airframe by appending to the list rather than matching it exactly.
- **An unsubscribe can leave a unit that only your own patch defines.** usn_ea-18g_2020s came
  from a mod deprecated into Modern US Navy; after the unsubscribe the id survived only as this
  collection's shadow copy, pointing at an asset folder no longer installed - a Growler with no
  model, fielded by ten saved missions. Check the whole file stack, not just the winner: if the
  only provider is a SEST pack, the unit is being kept alive by the patch and needs either a
  live donor or a retirement plus mission retargeting.
- **A seat key belongs to a mesh, not to a station.** `Station<n>=<store>|<Key>` applies
  `<Key>Positions` as an offset from the hardpoint, so two stores with different mesh origins on
  one key cannot both sit flush. The F-15EX seats the AIM-120 and the AIM-260 on the same "120"
  key although they render from different meshes (dts_aim-120.obj, dts_aim-260.obj), which is
  why the AIM-260s hang low and aft of the inner rails - visible mainly there because the 610
  gal tank alongside gives the eye a reference. Upstream does the same, so the defect is
  inherited rather than introduced. The fix is a key per mesh, derived from the AIM-120 seat
  plus one named delta so the wing rails and the eight belly rack slots cannot drift apart.
- **When the only evidence is another airframe, ship the settled value, not the opening guess.**
  The F-35 JATM packs measured this same mesh-origin difference over four in-game passes; their
  first attempt (up 0.005) clipped the pylons and was halved, so 0.0025 is what carries across.
  It remains a first cut anywhere else, because that pass compared a different AIM-120 mesh.
  The offset therefore lives in one place, `integration/common/aim260.py`, and every pack that
  mounts an AIM-260 derives its seats from it - one edit moves the F-15EX's nine seats and the
  F-16's two together, instead of a tuning round per airframe.
- **Derive the corrected seats, and check nothing puts the store back on the shared one.** The
  F-15EX pass runs after every loadout is assembled, so it covers the author's carried fits as
  well as this pack's, and a later step that writes a station line by hand would undo it - the
  symmetry repair did exactly that with a hardcoded `|120`. A guard after the last mutation
  fails the build if an AIM-260 is back on a key in the map.
- **A mod renaming its units is the routine failure, not the exception.** Euromod JMSDF renamed
  jp_sh-60j/k to jmsdf_sh-60j/k on 19 Sep 2026, a week after Modern US Navy retired the Burke
  that crashed the game. The Mogami builder failed loudly (good) and twenty-nine missions carried
  a dangling air group that only preflight caught. Both are cheap to fix and impossible to
  notice by eye, which is the argument for running build_all and preflight after every export
  rather than only when something looks wrong.
- **An unsubscribed mod must leave the hand-written tiers too.** generate_load_order filtered
  unsubscribed mods out of the alphabetical tiers but not out of TIER0-3 and TIER7, which name
  ids directly, so set-mod-order kept warning that it had nothing to place for three mods Steam
  had never downloaded. emit() now drops any entry the catalog no longer carries.
