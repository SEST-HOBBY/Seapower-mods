# F-15EX Eagle II — Revamped Loadouts

Cross-mod loadout expansion for dingtools' **F-15 EX Eagle II**, built from weapons already in
the collection. Ships as a patch mod that sits **above** the F-15EX in the Mod Manager
(and below Dingtools Weapon Pack, per its author's instruction).

## The eight loadouts

| # | Loadout | Stores | Weapon source | Status |
|---|---|---|---|---|
| 1 | **Air Superiority+** | 12× AIM-120D-3 · 2× AIM-9X | Dingtools Weapon Pack | Ready once IDs resolved |
| 2 | **JATM Sniper** | 6× AIM-260A · 4× AIM-120D-3 · 2× AIM-9X | Dingtools Weapon Pack | Ready once IDs resolved |
| 3 | **Maritime Strike** | 4× AGM-158C LRASM · 4× AIM-120D-3 · 2× AIM-9X | TBD — see open questions | Blocked on LRASM source |
| 4 | **Standoff Land Attack** | 5× AGM-158B JASSM-ER · 4× AIM-120D-3 | TBD — same | Blocked on JASSM source |
| 5 | **Quicksink** | 4× GBU-31 (Quicksink anti-ship JDAM) · 6× AIM-120D-3 · 2× AIM-9X | Dingtools Weapon Pack (GBU-31) | Ready once IDs resolved |
| 6 | **SDB Truck** | 16+× GBU-39/53-class SDB · 4× AIM-120D-3 · 2× AIM-9X | Dingtools Weapon Pack (AG list truncated in description — confirm) | Confirm SDB presence |
| 7 | **Harpoon Classic** | 4× AGM-84D · 6× AIM-120D-3 · 2× AIM-9X | Murder Hornet (defines AGM-84D) | Ready once IDs resolved |
| 8 | **What-if: Big Stick** | 4× AIM-174B · 6× AIM-120D-3 | Murder Hornet (defines AIM-174B) | Ready once IDs resolved; clearly labeled what-if |

Rationale: the real F-15EX's selling points are magazine depth (12+ AAM carriage via AMBER-style
racks), outsized station 2/5/8 capacity for large standoff stores, and day-one JATM compatibility —
loadouts 1–4 map those directly. 5 and 6 give it the strike roles Sea Power missions actually use.
7 and 8 are cross-mod fits: 7 is era-plausible, 8 is a flagged what-if (air-launched SM-6 is a
Super Hornet program in reality).

## How it gets built

1. `loadouts.spec.json` in this folder is the source of truth: every loadout, station assignment,
   and weapon reference with a `weapon_id: TBD` placeholder per store.
2. When `mods-source/` lands (run `tools/export-mod-configs.ps1` and push), resolve each TBD
   against the actual INI files: the F-15EX unit definition gives the station schema and existing
   loadout syntax; Dingtools Weapon Pack and Murder Hornet give the weapon IDs.
3. Emit the final patch INI(s) mirroring the F-15EX mod's own loadout format exactly (schema
   copied from its files, not guessed), as a standalone folder installable alongside the mods.

## Open questions the export resolves

- **LRASM / JASSM-ER**: does any subscribed mod define them? Candidates: the truncated AG list of
  Dingtools Weapon Pack, and U.S. Navy 2027 Capabilities (edits USN weapons to 2027 standard).
  If neither has them, we clone a suitable existing ASM/ALCM definition (e.g. Murder Hornet's
  AGM-84D or a vanilla AGM-86 variant) into new AGM-158B/C entries with corrected range/speed/
  seeker parameters — that's config-only and fully within reach.
- **SDB presence** in the weapon pack's AG list.
- **Station/hardpoint schema** of the F-15EX mod (station count, AMBER-style multi-rack support,
  CFT modeling, whether tanks are modeled as stores).
- **Whether the F-15EX mod already ships loadouts** overlapping these (avoid duplicate names;
  revamp rather than duplicate).

## Load order for users of this patch

Dingtools Weapon Pack → **this patch** → F-15 EX Eagle II (and Murder Hornet anywhere below the
weapon pack; only its weapon definitions are referenced).
