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

- **Gates before every push:** `check_load_order`, `check_dependencies`,
  `preflight` (every reference the missions make), `check_station_clash`,
  `check_weapon_employment` (every weapon can actually be fired by the mount
  carrying it), full pack rebuilds. All exit non-zero; all have been
  negative-tested — the employment gate against both bugs it was built from,
  the stripped NSM datalink association and the GBU-53's 200 ft release band.
