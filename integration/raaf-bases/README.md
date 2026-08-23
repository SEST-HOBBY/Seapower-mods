# SEST RAAF Bases

Five Australian airbases populated with the collection's aircraft — the RAAF's real order of
battle plus the allied heavy-iron rotations the north of Australia actually hosts. Each base
clones the Modern US Airbase unit (which reuses vanilla Reykjavik airbase scenery and its proven
flight-deck geometry), so no new models are needed.

## The bases

| Base | Air group |
|---|---|
| **RAAF Base Williamtown** | 24× F-35A (3 SQN / 77 SQN liveries) · 3× E-7A Wedgetail |
| **RAAF Base Tindal** | 12× F-35A (75 SQN) · 4× B-52H · 2× B-2 Spirit · 2× KC-135 · 4× MQ-9 |
| **RAAF Base Amberley** | 12× F-15EX Eagle II · 2× B-1B · 3× KC-46A (boom) · 2× KC-10A · 2× E-3G |
| **RAAF Base Edinburgh** | 8× P-8A (**No.12 SQN RAAF livery**) · 4× MQ-9 |
| **RAAF Base Darwin** | 8× F-35A · 6× F-15EX · 2× KC-46A (drogue) · 2× P-8A · 4× MH-60R |

106 aircraft total. All units are `Nation=Australia`, `LandUnitSubType=Airbase`.

## Dependencies (aircraft resolve from their own mods)

RAAF F-35A (Greene) · E-7A Wedgetail (Pog Frog — deprecated but functional) · Boeing P-8
Poseidon (Kirameki) · F-15EX + B-52H + B-1B (dingtools, keep Weapon Pack above them) ·
B-2 Spirit (needs Anchor Chain + SeaLifter) · E-3G · KC-46A · KC-10A Extender · MQ-9 Reaper ·
an MH-60R source (US Naval Aviation / Modern US Navy / standalone) · KC-135A is vanilla.

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
