# SEST YF-23 MALICE

An AIM-424 MALICE loadout for the **F-23A Block 40**, the 2025 configuration of Alpine's
YF-23 Black Widow II mod (Workshop `3796349767`).

## The new loadout

| Loadout | In-game name | Stores |
|---|---|---|
| `Malice424` | SEST Intercept MALICE (2x AIM-424 int) | 2× **AIM-424 MALICE** on the bottom pair of the main bay + 4× AIM-260A above them + 2× AIM-9X Block II in the side bays — full stealth, every round internal |

The mod's own three loadouts (`Empty`, `Ferry`, `AirToAir`) are kept untouched. `AirToAir` is
the six-JATM fit; `Malice424` trades the bottom two JATM for two MALICE.

## Why only the Block 40

The mod ships six airframes — the original YF-23 and F-23A Blocks 10 through 40 plus a Block 40
strike variant — and only `yf23_f23a_block40_2025.ini` carries the AIM-260A. That is the one
file this pack overrides. The mod is the sole provider of every `yf23_*` stem in the collection,
so the override has exactly one mod to outrank.

## Why the MALICE is a bare `sest_aim-424`

The mod carries its rounds as its own internal-bay variants (`yf23_aim260a_internal`,
`yf23_aim9x2_internal`). Each is a complete missile definition pointing at the author's own
model; nothing in them is bay-specific — `_internal` is the author's convention for "my model,
sized for my bay". A `yf23_aim424_internal` would be a name with no model behind it, so the
MALICE rides the bay stations as the same `sest_aim-424` every other SEST pack uses.

## The AIM-424 MALICE

`ammunition/sest_aim-424.ini` is the Raytheon AIM-424 LRAAM, revealed by the US Navy on
22 August 2026 and already in flight test. Two-stage solid-propellant, 4.11 m on the same
34.3 cm body as the SM-6, blast-fragmentation warhead, and a Navy-stated range **in excess
of 250 nm** — modelled here at **290 nm**, just under the AIM-174B's 316. Active-radar
terminal homing with datalink midcourse plus a passive anti-emitter mode.

The 3D model is a stand-in — no AIM-424 mesh exists, so it renders on US Naval Aviation's
AGM-88G assets. Mass and seeker figures are this repo's estimates; the Navy disclosed
neither. See `integration/common/aim424.py` for the reasoning behind each.

## Dependencies and load order

- **YF-23 Black Widow II** (`3796349767`) — the base airframe and its AIM-260A / AIM-9X rounds.
- **US Naval Aviation** (`3737267013`) — the AGM-88G model the MALICE borrows as a stand-in.

Deploys inside the consolidated SEST Integration Pack at tier 0, which sits above every
workshop mod by invariant; `tools/check_load_order.py` computes and enforces the rule.

## Build

```
python3 integration/yf23-malice/build_patch.py
```
