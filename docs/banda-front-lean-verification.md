# Banda Front Lean verification — 19 September 2026

The handover starts at `5ac8e449` on `sest-dev/beautiful-cerf-i7fqei`. The
follow-up branch `fix/banda-front-lean-finalize` (one commit, `f6e2966e`) has
been merged into `sest-dev/beautiful-cerf-i7fqei`, and the further fixes below
sit on top of it there. Everything installs from that branch.

## Result

`SEST Banda Front edited.ini` (the editor save) is untouched. The transform is
re-run from it and the Lean copy is byte-identical on every run.

| Side | Land units in the edited save | Land units in Lean |
|---|---:|---:|
| Taskforce1 | 241 | 101 |
| Taskforce2 | 413 | 184 |
| Neutral | 140 | 129 |
| Total | 794 | 414 |

All 110 formations remain, including 106 land formations. All eight land units
outside formations remain. All 63 existing ships and aircraft are unchanged,
as are surviving land-unit positions, headings, types, and blue/red air groups.
Fifteen neutral airfields and helicopter rigs have explicitly empty air groups.
The 25 already-placed neutral aircraft remain.

## Follow-up fixes

From `fix/banda-front-lean-finalize`:

- A guidance radar or launcher outside a formation no longer causes a
  `None` formation-index crash. A battery with an unformed radar is considered
  under its first formed launcher; retained launchers keep their associated
  radar, including when either member is outside a formation.
- BMD keep decisions are recorded against each unit's own formation. A wholly
  unformed battery remains intact.
- Removing land units from one side preserves newly added units belonging to
  the other side instead of failing with a mapping `KeyError`.

From the four-reviewer pass on `5ac8e449` (structure, air groups, code and
judgement; nineteen findings, each checked against the code or the file):

- A formation with no military unit in it (a refinery, an LNG plant, a port, a
  power station) is not a base and is left exactly as it is; `--trim-civil`
  applies the one-of-each-kind rule there too. This is where 396 became 414.
- Anti-ship launchers follow the same rule as ballistic-missile TELs, drones and
  technicals: one of each type before a second of any, so Sorong keeps a YJ-12
  and a DF-10A rather than two YJ-12s, and the Bastion battery a K-300P and a Bal.
- Any hand-named unit in a hand-placed formation is kept with its label, not
  only the first member.
- One search radar per site across the builder's layers: an Air Defence layer
  and a Coastal Battery layer at the same site no longer keep one each.
- The HQ-7B acquisition radar (filed as `LandUnitSubType=SAM`, no weapons) is
  classed as a radar, not a gun, so it survives on its own merit.
- `set_custom_air_group` keeps a blank line that separated a block from the
  next, so a save written with blank lines is not refused as "body changed".
- The report names neutral units as the save numbers them (grounding runs before
  renumbering), and its notes come out in file order.

## Verification

| Check | Result |
|---|---|
| Regression suite | 9 tests pass: removal, references, air groups, unformed batteries, and full mission regeneration (`python3 -m unittest discover -s tools/tests -p 'test_trim_land_sites.py' -v`) |
| Seven synthetic missions from the reviewers (a BMD section split across two formations, a stray battery radar, a stray BMD radar, a stray launcher, two layers each with a search radar, a hand-named unit that is not first, a save with blank lines between blocks) | Each now trims as intended and verifies clean |
| Repeated regeneration in a temporary directory | Identical bytes on both runs and identical to the committed Lean file; edited input unchanged |
| Mission structure | Counts, dense unit numbering, formation references, and language references pass |
| `preflight.py "SEST Banda Front Lean"` | 754 references resolve |
| `build_all.py --from-scratch` | All 17 builders and consolidation complete; no generated content diff after Git's newline normalization |
| `check_load_order.py` | 46 overlaps checked across 133 order entries; all SEST overrides outrank their donors |
| `check_dependencies.py` | Required upstream mods are exported and ordered |
| `check_weapon_employment.py` | Eight distinct findings, identical across original, edited, and Lean missions; this gate remains red |
| `check_alias_bases.py` | Unit-base check exits successfully but reports existing ammunition/base warnings |

The rebuild produces CRLF instead of the committed LF in both copies of
`usn_ddg_arleigh_flt3_2027_variants.ini`. Their contents match after newline
normalization. Those unrelated generated files are not changed by this follow-up.

The eight weapon findings are two land-launcher guidance-channel findings
(NASAMS and SLAMRAAM), three MLRS magazine references, the Su-57 KH-58 position
group, the F-4E CAS station count, and the SEST Growler gun-magazine reference.
They are recorded rather than waived or folded into a mission-trimming change.

The source save also places 31 of the 40 retained externally guided launchers
outside their configured radar search radius. The trimmer retains radar
associations without moving the user's units. Retaining a radar does not prove
that a distant launcher can use it in game. Geometry and weapon-employment
repairs remain separate work; no in-game performance or firing test was possible
in this environment.

Reproduce the focused checks from the repository root:

```bash
python3 -m unittest discover -s tools/tests -p 'test_trim_land_sites.py' -v
python3 tools/preflight.py "SEST Banda Front Lean"
python3 integration/missions/trim_land_sites.py --dry-run
```

## Install on the PC

With Sea Power closed, from the repo root in PowerShell. The installer copies
every mission under `integration\missions` into the game's `user_missions`
folder (new files added, changed files overwritten, nothing deleted), so the
Lean copy appears beside the edited save, which the game already has:

```powershell
cd C:\Users\rolyl\Seapower-mods
git checkout sest-dev/beautiful-cerf-i7fqei
git pull origin sest-dev/beautiful-cerf-i7fqei
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1
```

`tools\sync-sest.ps1` refuses to run from any branch but the deploy branch
named in `data\deploy-branch.txt`; `install-sest-packs.ps1` has no such guard,
which is why it is called directly here. To copy the one mission and nothing
else:

```powershell
Copy-Item -LiteralPath 'C:\Users\rolyl\Seapower-mods\integration\missions\SEST Banda Front Lean.ini' `
  -Destination 'C:\Program Files (x86)\Steam\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\user\missions\user_missions\'
```

Verified source SHA-256:
`1b9d4cd7f3a2d59680634ae4cdec6b22d8942f3346ba535ff447ccf21dbecf94`.

Verified Lean SHA-256:
`8f22919799da44cf16805414349920341474482782f23facc4bf989bc3a6fa90`.
