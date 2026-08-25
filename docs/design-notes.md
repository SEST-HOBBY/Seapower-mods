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

## Working practices

- **Derive, don't invent.** New loadouts clone a donor block the mod's author
  already proved (same stations, hide lists, keys) and swap rounds. Choices
  between candidate rounds are settled by comparison tables (AIM-424 vs 174B,
  the three NSMs, RSA's AIM-120D), not preference.
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
