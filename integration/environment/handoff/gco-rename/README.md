# GCO rename: what is left on feature/mno-r16

Checked against `feature/mno-r16` at `d8ac81ba8` (24 Nov 2026). Nothing here has been pushed to that branch.

## Already GCO in the source

- `integration/beta-feature-parity/runtime/WorldOpeningBriefing.cs:22`: `CampaignTitle = "Global Command Operations (GCO)"`
- `integration/world-sandbox/modern_world.py`, `build_dynamic_campaign.py` and `SEST_World_Campaign/_info.ini`
- `dynamic_campaigns/sest-world-regions-2028/campaign.json` (in both the world-sandbox and dist copies)
- the `_info.ini` description in `integration/dist/SEST_Integration`

## Still the old name

| Where | Shows | Fix |
|---|---|---|
| `candidates/R15-20261117/SEST.RuntimeFixes.dll` (59b54124), the newest compiled runtime | "Global Maritime Operations 2028" (3 strings) | Rebuild on the PC (below) |
| `WORLD-CAMPAIGN-READ-ME.txt`: the template in world-sandbox, plus the SEST_World_Campaign and dist copies | "Global Strategic Command Operations (GSCO)" | `0001-gco-rename-text.patch` |
| `tools/tests/test_regional_expansion.py:35` | still expects GSCO, so it **fails** against the GCO campaign.json | `0001-gco-rename-text.patch` |
| The `beta-support/manifest.json` revision `R15-20261122-MNO-GSCO-2212-aae79728` | an R15 revision label | Leave it. The next candidate build writes a new revision |
| `docs/releases/20261107/*` and `docs/campaigns/southern-watch/workshop-listing.md` | The R15 Steam copy | Public copy. Change it at the next Workshop update; nothing is posted from here |

The `dist/.../plugins/SEST.RuntimeFixes.dll` (7ba6d6d9) is the original 1.5.0 runtime. It has no campaign title, so it shows no name at all.

## Apply the text patch

Run this on a checkout of `feature/mno-r16`:

```
git am integration/environment/handoff/gco-rename/0001-gco-rename-text.patch
```

Test run in this container, with the patch applied: `test_regional_expansion` passes (it failed before the patch). Two cases in `test_world_operations_realism` error both before and after the patch. Both need the `global_land_mask` package, which this container lacks.

## Rebuild the runtime (PC only)

The DLL cannot be compiled in the cloud container. `build.py` and `build-roslyn.ps1` refuse to run without the captured
game and author references (Seapower-Scripts.dll, Harmony, BepInEx, Unity modules), and those are not in the
repository. Since `d8ac81ba8` the pins target Build 261123 (`ea653e49`).

1. On the PC, check out `feature/mno-r16` with the patch applied.
2. Capture references for Build 261123. Use the capture the other session used for the 261123 port.
3. Run `integration/beta-feature-parity/build-roslyn.ps1 -Capture <capture> -Output <new empty folder> -Revision R16-<date>-ea653e49`.
4. Check: `strings -el SEST.RuntimeFixes.dll` (or open it in a hex viewer) must contain "Global Command Operations (GCO)"
   and not "Global Maritime Operations".
5. Run `verify.py`. The companion DLLs (ContactsFix, IdentifyDataPaths) are rebuilt in the same run, because they pin the
   runtime's SHA-256.

The rebuilt DLL is not IN-GAME TESTED until the campaign menu and the opening brief are seen showing GCO on the PC.
