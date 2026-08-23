# SEST RAAF Bases

The complete RAAF base network — every operational flying base, the three northern bare bases
in activated posture, the Woomera range, and the forward presence at Butterworth — populated
with the collection's aircraft: the RAAF's real order of battle plus the allied heavy-iron
rotations the north of Australia actually hosts. Each base clones the Modern US Airbase unit
(which reuses vanilla Reykjavik airbase scenery and its proven flight-deck geometry), so no
new models are needed.

## The bases

| Base | Air group |
|---|---|
| **RAAF Base Williamtown** | 24× F-35A (3 SQN / 77 SQN liveries) · 3× E-7A Wedgetail |
| **RAAF Base Tindal** | 12× F-35A (75 SQN) · 4× B-52H · 2× B-2 Spirit · 2× KC-135 · 4× MQ-9 |
| **RAAF Base Amberley** | 12× F-15EX Eagle II · 2× B-1B · 3× KC-46A (boom) · 2× KC-10A · 2× E-3G |
| **RAAF Base Edinburgh** | 8× P-8A (**No.12 SQN RAAF livery**) · 4× MQ-9 |
| **RAAF Base Darwin** | 8× F-35A · 6× F-15EX · 2× KC-46A (drogue) · 2× P-8A · 4× MH-60R |
| **RAAF Base East Sale** | 4× F-35A (lead-in det) · 4× MQ-9 (training) |
| **RAAF Base Pearce** | 8× F-35A (conversion unit) · 2× KC-46A |
| **RAAF Base Gingin** | 4× F-35A · 2× MH-60R (SAR) |
| **RAAF Base Richmond** | 6× KC-130T Hercules (C-130 stand-in) · 2× MH-60R |
| **RAAF Base Townsville** | 8× AH-64E Apache · 4× MH-60R · 4× S-70B-2 Seahawk · 2× KC-130T |
| **RAAF Base Learmonth** *(bare base)* | 4× P-8A · 2× U-2 · 2× KC-135 |
| **RAAF Base Curtin** *(bare base)* | 8× F-35A · 2× KC-46A (drogue) |
| **RAAF Base Scherger** *(bare base)* | 8× F-35A · 4× MQ-9 ER |
| **RAAF Woomera Airfield** | 2× U-2 · 4× MQ-9 ER · 2× B-2 (test det) |
| **RAAF Base Butterworth** *(Malaysia)* | 6× F-35A · 3× P-8A · 2× KC-135 |

205 aircraft across 15 bases. All units are `Nation=Australia`, `LandUnitSubType=Airbase`.
(RAAF Base Wagga is non-flying and has no unit; the bare bases are modeled in their activated
crisis posture, since an empty airfield already exists as vanilla scenery.)

## Dependencies (aircraft resolve from their own mods)

RAAF F-35A (Greene) · E-7A Wedgetail (Pog Frog — deprecated but functional) · Boeing P-8
Poseidon (Kirameki) · F-15EX + B-52H + B-1B (dingtools, keep Weapon Pack above them) ·
B-2 Spirit (needs Anchor Chain + SeaLifter) · E-3G · KC-46A · KC-10A Extender · MQ-9 Reaper ·
U-2 Dragon Lady · AH-64E (misaka AH-64 pack) · KC-130T + an MH-60R source (US Naval Aviation) ·
S-70B-2 Seahawk (Pog Frog) · KC-135A is vanilla.

A squadron whose source mod is missing simply won't spawn — the base itself still works.

## Install

1. Copy `SEST_RAAF_Bases/` into `Sea Power_Data\StreamingAssets\`.
2. Place it **below** the aircraft mods in the Mod Manager (bases last, per the repo's load-order doc).
3. The five bases appear in the mission editor as Australian airbase land units.

## First-flight checks

- The E-7A's squadrons file defines only a Default livery (its `[Squadron1]` block is commented
  out upstream) — confirm the Wedgetails spawn at Williamtown with the default livery.
- The SEST patches (F-15EX Revamp, RAAF F-35A JATM) apply to these bases' aircraft automatically,
  since they extend the same unit definitions.

## Rebuilding

```bash
python3 integration/raaf-bases/build_pack.py
```

Regenerates all five bases from the template and re-validates every aircraft id and squadron
index against `mods-source/` (it fails loudly on a missing aircraft or out-of-range squadron).
