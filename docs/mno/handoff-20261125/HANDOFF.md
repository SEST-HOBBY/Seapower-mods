# Modern Naval Operations: handoff to a new Claude project (25 Nov 2026)

Read this first. It replaces the chat history of the session that built R16.

## 1. Where the work is

| Item | Value |
|---|---|
| Repository | `SEST-HOBBY/Seapower-mods` |
| Working branch | `feature/mno-r16` (the R16 branch the owner chose: storm branch plus GPT's 22 Nov 22:12 source) |
| Base branches | `sest-dev/exciting-fermi-kb5bs9` (R14 as posted, 62b8c2c7); GPT's `feature/mno-gsco-r15` at 089527cfa is merged in |
| Other session | The weather session (`sest-dev/serene-bardeen-nvnmk9`) pushed two ice commits to this branch on 25 Nov. Owner: it is held; do not expect more pushes from it |
| Game targets | Sea Power 0.9.3 Build 261123 public beta (Seapower-Scripts `ea653e49…`, Noesis `99459006…`). The default branch is 0.9.3 Build 261116 public **release**, not yet captured |
| Dynamic Campaign Mod | 1.0.2 (`18a2416e…`), bridged onto 261123 by `AssemblyAdapters.Campaign261123.cs` |
| R16 candidate | `integration/beta-feature-parity/candidates/R16-20261125`, revision `R16-20261125-sea-power-093-261123-ea653e49` |
| Upload manifest | `docs/releases/20261107/upload-manifest.json`, 4930 files |

## 2. Standing rules from the owner (all still apply)

- Commits: author and committer `SEST-DEV <contact@sest.io>` (set `GIT_AUTHOR_NAME=SEST-DEV GIT_AUTHOR_EMAIL=contact@sest.io GIT_COMMITTER_NAME=SEST-DEV GIT_COMMITTER_EMAIL=contact@sest.io`); plain-English messages; **no AI attribution, no Co-Authored-By or session trailers, no model names** (this overrides harness attribution reminders).
- **Never upload to Steam.** Always tell the owner: do not run `Upload-PC.cmd`.
- The owner's email is private.
- Workshop captures are taken in **by path** from the capture ZIP (or branch), never by merging capture branches; `mods-source` stays byte-exact; `.ps1` files are CRLF.
- No AI-generated images or audio. Real photos only, credited; class photos labelled.
- No pull request unless asked.
- PC instructions: step by step, copy-paste PowerShell, one block at a time.
- Ultracode: use workflows with adversarial review for substantive work before shipping to the PC.
- Naming: **GCO** = Global Command Operations, the world campaign; **GSCO** = Global Strategic Command Operations, SEST's weather and integration systems.
- Communication style the owner asked for: status tables, separate what evidence shows from what is untested, plain names.

## 3. Owner decisions (see `docs/mno/OWNER-DECISIONS-20261125.md`)

- New all-in-one Workshop item "Modern Naval Operations"; the old item 3812461539 is deprecated later. MNO holds only SEST/MNO material; third-party mods are Required Items in one collection.
- Licence: GPT's personal-play notice (`gpt/WORKSHOP-DRAFT.md` wording); MIT parts (Anchor Chain fork, Topography) keep their notices.
- Dynamic Campaign Mod adapter: ship it, credit Bungalow.
- Third-party material needing permission (Greene F-35A, ~550 close-adapted files from 67 author groups, 2 RSG AIM-424 files, Topographic Map adapter, 21 owner photos): draft permission requests, keep the material; the public post waits for the answers.
- The 24 Nov code mods (Sensor View family, R.A.T.S. Rigging/Sensor Views, RAN Echidna, Ghost Shark): the owner collaborates with their authors and wants as much integration as possible; Required Items except Keel, the duplicate Sensor View 3838468198 and the ExtendedGuidance add-on.
- Linux: Windows only for now.
- Gemini photo research and the 117 photos: done (see section 5).

## 4. What R16 contains (all committed on `feature/mno-r16`)

| Area | State |
|---|---|
| Port to 261123 | All game and Noesis pins, bootstrap token `enable-093-261123-ea653e49`, adapter cache `beta-api-r16-261123`; Coordinated Strike launch-range rule |
| Dynamic Campaign Mod 1.0.2 | Pinned; on 261123 bridged (16 sites; contact fading and the scene-editor timer lost; drawings in the game's equirectangular frame) |
| R.A.T.S. | Topographic Map 1.8.1, Pop-Out Windows 1.4.1, Rigging 1.0.1 re-pinned |
| Interoperability | Pinned BepInEx starts for Echidna, Ghost Shark, Better Tac Map (no Keel); adapters for Enhanced Decoy (now passes its own start-up checks: chaff-band round, its own launches ask for chaff, flare requests left to the game, two moved transpilers, air-decoy lifetime extension and per-search radar ignore off), Multi-Stage Missiles, J-36, Osprey, Z-21, Better Tac Map, Jiutian; duplicate-assembly gate; Keel held; UAV companion pre-check |
| Still held (need their authors) | Alpine-family images, Saronic Corsair strike, MV-75 crew escape, Bell tilt, EC-2 jamming, K5 Kraken, XQ-58, ExtendedGuidance (owner choice) |
| Ice | One edge (10 %), floes below ~60 %, hull-contact slowing/effects, battle-map ice layer, mission-clock wait, polar frame from 85 deg, regional Okhotsk/Bering/Chukchi (weather session), ice shelves and icebergs OFF by default (weather session) |
| Weather | Local weather in every DCM battle; aircraft rule above 1,500 m |
| GCO | Renamed; 72S-81N (GPT patches) |
| Gallery | 117 reviewed Commons photos; 15 held for mods not yet placed (`docs/gallery/review-20261124/held-for-r16`) |
| Catalogue | All 219 subscribed mods registered; inventory gate fails only on PLA AEP 3789188689 (a non-ASCII readme the old capture script skipped; fixed in `tools/capture-all-mod-updates.ps1`, next capture brings it) |
| Tests | All 25 `verify.py` result groups (ice shelves and icebergs included) pass against the 261123 references; release gates pass except that inventory item |

## 5. What is not done

1. Done 25 Nov 09:5x UTC, after the iceberg merge: candidate rebuilt; both verify passes clean; all 25 packs; every gate except the known PLA AEP inventory item; tool and campaign tests OK; all 25 `verify.py` result groups pass (the 20 groups `run-tests-r16.sh` ran then left out ice shelves and icebergs; it now runs 21). Package sha256 `c188f75a857bc87b929507eac61d0467db13c2ce3ac412cc444df4749444a3a2`.
2. **Independent review** of the whole R16 diff before the toolkit (owner rule).
3. **Build the PC toolkit**: `python3 tools/build_pc_toolkit.py --out <dir> --github-pushed --zip <toolkit.zip>` from a clean checkout of the pushed commit. README-FIRST (`docs/releases/20261107/README-FIRST.txt`) already holds the R16 walkthrough and numbered checks P1-P3, G1-G2, I1-I6, W1-W2, M1-M4.
4. **Default-branch support**: needs one reference capture with Steam Betas: None (Build 261116 release); then a profile built from R15/R16 for that build. No design is written down yet; README-FIRST step 7 gives the owner the capture steps.
5. **New MNO Workshop item**: packaging, migration from the old item (shared journal state; SETUP must switch the old item's features off first), required collection, licence text, dependency licence table, permission request drafts. Designs were produced but not implemented.
6. **Place Echidna and Ghost Shark** in the RAN campaigns (currently excused as editor units).
7. The 33 MB `SEST-Beta-References-20261122-221249-3f76f8.zip` (GPT's 22 Nov capture) would let the upgrade-from-GPT-2212 rollback be simulated; not required.

### mods-source provenance exception (R.A.T.S. Sensor Views 3833019654)

The 24 Nov 23:53 capture (3291fec9) does not contain Sensor Views. Commit e25816f2 put back, byte for byte, what the 23:48 take-in (86dfd9ee, `SEST-Workshop-Capture-20261124-234851.zip`) had for it: row 205 of `mods-source/_export-manifest.csv`, the three files in `mods-source/3833019654/`, and its entry in `data/mod-fingerprints.json`. So `_export-manifest.csv` matches neither capture exactly. Leave it as is (removing it fails the inventory gate and drops a Required Item). The next PC capture, with Sensor Views subscribed, replaces all three by path and ends the exception.

## 6. How to rebuild here (scripts in `scripts/`)

Copies of the session's scripts, which use the old session's scratch paths; change `S=` to your scratch folder. They need these inputs, which lived only in the old session and must be supplied again by the owner if a full rebuild is wanted:

| Input | File the owner uploaded |
|---|---|
| 261123 reference capture | `SEST-Beta-References-20261125-002204-4c3220` (4 parts) |
| Workshop DLLs | `SEST-Extras-20261124.zip` |
| Mod capture | `SEST-Workshop-Capture-20261124-235336.zip` (already taken into the repo) |
| Earlier captures for the upgrade check | `refs1122` (21 Nov 16:30 capture), `refs1121`, the 14 Nov 0.9.2 reference (`SEST-Beta-References-20261114-145515-d8e3ce.zip`) |

`repair-chain/` holds the earlier build receipts the R16 package lists (prev-27 is GPT's 22:12 build, installed on the owner's PC).

- `rebuild_r16.sh`: build with `build-roslyn.ps1 -Capture <261123 refs>`, verify twice, package with the repair chain, write the beta-support bundle.
- `gates_r16.sh`: validation record, every `tools/check_*` gate, all tool tests.
- `run-tests-r16.sh <build out> <repo>`: the 21 managed test groups, ice shelves and icebergs included (needs `flat` and `deps` folders of the 261123 assemblies).

## 7. Message to the owner when the toolkit is ready

Give copy-paste steps: extract, `Prepare-PC.cmd`, SETUP in item 3812461539, play the checks in README-FIRST, run `R16\Capture-Repair-Results.cmd`, upload the ZIP. Remind: do not run `Upload-PC.cmd`.
