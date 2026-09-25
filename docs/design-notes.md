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
- **A renamed base breaks every patch aliased onto it.** U.S. Navy 2027 is 28
  `#!alias` patches over Modern US Navy hulls. Modern US Navy renamed its Flight III
  from `usn_ddg_burke_f3` to `usn_ddg_burke_f3_125` (v567, 18 Sep 2026) before 2027
  caught up, and the game died at startup with *KeyNotFoundException 'AirGroup'*:
  the patch's own `[FlightDeck]` asked for the air group the missing base would have
  supplied, and Player.log named the symptom, not the file.
  `tools/check_alias_bases.py` walks every chain through the load order the way the
  game does. Run it after every mirrored export; before the mirror, a deleted base
  kept resolving against its ghost. On the 24 Sep 2026 export all 28 bases resolve
  (2027 now aliases `usn_ddg_burke_f3_125`), so the missions keep the 2027 hulls and
  their `≥119_*` / `≥125_*` loadouts instead of being moved onto plain Modern US
  Navy hulls, which would drop those fits.
- **Anchor Chain has two layering directives, not one.** `#!alias` replaces a whole
  unit; `#!extend` merges a few keys onto the file of the SAME name one rung lower in
  the load order. Ammunition packs lean on it (all 18 of the PLA AEP pack's rounds
  on the 24 Sep 2026 export), and an extend breaks exactly the way the alias that
  crashed the game did. Resolving an extend needs the load-order *stack*, not the
  winner: `winning_file` on a same-name target returns the patch itself and loops.
  `refine_civ_traffic.file_stack` returns every copy in order, and the checker
  takes the entry below the patch. Severity
  follows the file kind: a unit file with no base is the startup crash, because the
  loader cannot build the unit, so it fails the check; a round with no base only
  means that weapon never fires, which the game survives, so it is reported and the
  check still exits zero.
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

- **Gates before every push:** `check_load_order`, `check_dependencies`,
  `preflight` (every reference the missions make), `check_station_clash`,
  `check_weapon_employment` (every weapon can actually be fired by the mount
  carrying it), full pack rebuilds. All exit non-zero; all have been
  negative-tested — the employment gate against both bugs it was built from,
  the stripped NSM datalink association and the GBU-53's 200 ft release band.
