# SEST ADF Persistent ISR

Projecting the stratospheric surveillance layer into Sea Power: two Australian
high-altitude ISR drones as **new unit ids**, both flying the MQ-9 Reaper mod's
long-wing ER mesh as accepted stand-ins (the donor is untouched; both fleets
coexist).

## The aircraft

|---|---|---|
| What it is | Airbus solar-electric stratospheric pseudo-satellite, flight-proven from Wyndham WA (76,100 ft world record) | The RAAF's maritime Global Hawk — No. 9 SQN, Edinburgh, forward det at Tindal |
| Signature | **RCS `VeryTiny` (0.001 m², stealth class)** — 75 kg of radar-transparent carbon and solar film. **IR `VeryTiny`** — no combustion at all | RCS `Small`, IR `Small` — composite HALE jet, quieter on radar than a fighter but no stealth aircraft |
| Sensors | **Fully passive — it emits nothing**: OPAZ EO/IR survey payload (`SEST_OPAZ`, Recon-capable) + airframe optics + ELINT receiver | AN/ZPY-3 **MFAS 360° AESA** surface-search radar (periscope-capable, datalinked) + MTS-B optics + ELINT + RWR |
| Flight | Cruise 40 kt at 63,000 ft, ceiling 76,000 ft, ~a month on station | Cruise 310 kt at 53,000 ft, ceiling 56,500 ft, 8,200 nmi / 24+ h |
| Weapons | None (5 kg payload margin) | None — it finds, others finish |
| AI role | `Recon,ESM` | `MaritimePatrol,Recon,ESM` |

radar nor IRST will realistically ever see, parked above weather and above most
SAM engagement floors, feeding passive contacts to the force by datalink. The
Triton is the opposite trade — an emitting, findable, but far-seeing 2M-mi²/day
broad-area radar picture.

## Dependencies

**General Atomics MQ-9 Reaper** (Workshop 3503670861) must stay installed and
enabled — meshes, materials, textures, the gear animation file and the Triton's
MTS-B sensor definition (`AN/AAS-52_Visual`) all resolve from it cross-mod.
Everything else (AdvancedOptics, AircraftELINT, AircraftRWR, audio) is vanilla;
the pack ships its own `AN/ZPY-3` and `SEST_OPAZ` sensor definitions.

## Install

1. Copy `SEST_ADF_Persistent_ISR/` into `Sea Power_Data\StreamingAssets\`
   (or rerun `tools\install-sest-packs.ps1`).
2. Place it **below** the MQ-9 Reaper mod in the Mod Manager (additive — it
   only adds new units, so ordering is forgiving).
3. Both aircraft appear under Australia in the mission editor as UAVs, and the
   SEST RAAF Bases rebuild stations them at Edinburgh, Tindal, Woomera and
   Learmonth.

## First-flight checks

  18–70 kt. Confirm the AI holds a stable orbit and the landing pattern works
  at Woomera; if the flight model refuses the low speed band, raise
  `StallSpeed`/`SpeedAndRange_*` toward 40–90 kt and shorten
  `SpeedAndRange_Cruise` accordingly — the signature/passive-sensor character
  is the point, the exact knots are negotiable.
  mesh — close) and keeps its spinning pusher prop; the Triton hides the prop
  and flies as a clean jet but is visually undersized (20 m mesh vs 39.9 m).
  Both use the donor's 42nd ATKS gray livery with the Australian flag.
  emitters at all — if `SEST_OPAZ` or the ELINT fit ever shows as an emitter,
  that's a bug in this pack, not the game.

## Rebuilding

```bash
python3 integration/adf-persistent-isr/build_pack.py
```

Validates the MQ-9 ER donor layout, every hidden submodel, the vanilla and
MQ-9 sensor definitions and the animation file against `mods-source/` before
emitting; fails loudly if the donor mod updates incompatibly.
