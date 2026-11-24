# Hand-off: battle sea ice for origin/feature/mno-r16

This folder updates the battle sea-ice port on `origin/feature/mno-r16` to match
this branch's `integration/environment/mno_env/seaice.py`. That file now has a
regional calibration for the Sea of Okhotsk and the Bering Sea. See
`docs/environment/SEA-ICE-MARGINAL-SEAS.md`.

Nothing here has been applied to feature/mno-r16. The agent that owns that
branch should apply it.

## Why the plain regenerate is not enough

On feature/mno-r16, `SeaIceModel.cs` is gated by the SHA-256 of `seaice.py`
(stamped in `SeaIceData.g.cs` by `tools/make_sea_ice_data.py`). The new
`seaice.py` has a new hash, so the port must be regenerated.

But the old generator builds edges as `{north, south, sh_summer}` only. The new
`seaice.ice_at` needs `edges["marginal"]` for points in the two seas, and it
raises `ValueError` without it. The C# model also has no marginal-sea code. So
four files needed small hand edits. They are in `patches/hand-edits.diff`
(made against feature/mno-r16 at commit
`d8ac81ba8370a06b7201f461bfacd4aedbc3b743`):

- `tools/make_sea_ice_data.py`: solves and stores the two regional edges per
  date. Writes them to new arrays `SeaIceData.CommonMarginal` / `LeapMarginal`
  (stride 2: Okhotsk, Bering). The old `Common` / `Leap` arrays keep stride 3,
  so existing checks such as `SeaIceTests.cs` "731 rows" still hold. Also writes
  the sea masks and constants. Adds golden longitudes 138, 141, 143.6, 152 E and
  168 W, so the golden file covers the seas.
- `integration/beta-feature-parity/runtime/SeaIceModel.cs`: `Edges` gains
  `Okhotsk` and `Bering`; `IceAt` calls the new `MarginalSea`, `IceOrder` and
  `MarginalConcentration` (a hand port of `seaice.ice_order` and
  `seaice.marginal_concentration`).
- `tools/sea_ice_model.py`: the same change in the Python mirror.
- `tools/tests/test_sea_ice_model.py`: the mirror check uses the full edges,
  covers the new longitudes, and gains `test_marginal_seas`.

## What is in this folder

Paths match the feature/mno-r16 tree:

- `tools/make_sea_ice_data.py`, `tools/sea_ice_model.py`,
  `tools/tests/test_sea_ice_model.py`: patched files.
- `tools/sea_ice_edges.json`: GENERATED.
- `integration/beta-feature-parity/runtime/SeaIceData.g.cs`: GENERATED.
- `integration/beta-feature-parity/tests/SeaIceGolden.g.cs`: GENERATED.
- `integration/beta-feature-parity/runtime/SeaIceModel.cs`: patched file.
- `patches/hand-edits.diff`: the hand edits as a unified diff.

## How it was made

1. The four r16 files and the three generated files were taken with
   `git show origin/feature/mno-r16:<path>` into a scratch copy of the tree.
2. The patches above were applied there.
3. `python3 tools/make_sea_ice_data.py --env <this checkout>/integration/environment --full`
   was run. It took about 6 minutes on 4 cores. The stamped hash of
   `mno_env/seaice.py` is
   `fe4aa2dd70dd6e7108b1ecfdb09211311ec56126095334683c82268bcfe81409`.
4. Checks run:
   - `--check` (solves everything again and compares with the written files).
   - `SEST_ENV_DIR=<this checkout>/integration/environment python3 -m unittest discover -s tools/tests`:
     6 tests OK, including `test_mirror_matches_seaice_py`.
   - The C# model, `SeaIceData.g.cs` and `SeaIceGolden.g.cs` compiled with Mono
     `mcs` (namespace turned into block form for that old compiler) and a small
     check program: 10,693 golden points, 595 of them in the two seas. Worst
     difference from `seaice.ice_at`: 3.3e-13 percentage points.
   - The full `SeaIceTests.cs` harness was NOT run. It needs the game's
     assemblies and Mono.Cecil.

## How to apply (on a checkout of feature/mno-r16)

1. Copy this folder's `tools/` and `integration/` trees over the branch root.
   (`patches/` and this README are not needed there.)
2. Run `python3 tools/make_sea_ice_data.py --env <weather checkout>/integration/environment --check`.
   It must print "sea-ice generated files match the weather branch sources".
   If `seaice.py` changed after hash `fe4aa2dd...`, run it without `--check` first.
3. Run `python3 -m unittest discover -s tools/tests`, with `SEST_ENV_DIR` set to
   the weather checkout so the mirror test runs.
4. Build and run the managed `SeaIceTests.cs` as usual. Its golden check now
   covers the two seas.

## Behaviour change in battle

- Sea of Okhotsk: ice from late November to early July. Peak in Feb-Mar. Open
  water July to October. Before, the north of the sea stayed iced all summer.
- Bering Sea: winter extent now matches NSIDC (about 0.62 million km2 in March,
  2016-2025). Before, it was about 0.27.
- Everywhere else: identical, bit for bit.
- Maximum concentration in the two seas is 95 %, not 98 %.
