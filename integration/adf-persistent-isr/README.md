# SEST ADF Persistent ISR

Projecting Australia's high-altitude maritime surveillance layer into Sea Power: the
MQ-4C Triton as a **new unit id**, flying the MQ-9 Reaper mod's long-wing ER mesh as an
accepted stand-in (the donor is untouched; both fleets coexist).

## The aircraft

| | `raaf_mq-4c_triton` |
|---|---|
| What it is | The RAAF's maritime Global Hawk — No. 9 SQN, Edinburgh, forward det at Tindal |
| Signature | RCS `Small`, IR `Small` — composite HALE jet, quieter on radar than a fighter but no stealth aircraft |
| Sensors | AN/ZPY-3 **MFAS 360° AESA** surface-search radar (periscope-capable, datalinked) + MTS-B optics + ELINT + RWR |
| Flight | Cruise 310 kt at 53,000 ft, ceiling 56,500 ft, 8,200 nmi / 24+ h |
| Weapons | None — it finds, others finish |
| AI role | `MaritimePatrol,Recon,ESM` |

An emitting, findable, but far-seeing platform: one orbit sweeps a 2M-mi²/day broad-area
radar picture and feeds it to the force by datalink.

## Dependencies

**General Atomics MQ-9 Reaper** (Workshop 3503670861) must stay installed and
enabled — meshes, materials, textures, the gear animation file and the Triton's
MTS-B sensor definition (`AN/AAS-52_Visual`) all resolve from it cross-mod.
Everything else (AdvancedOptics, AircraftELINT, AircraftRWR, audio) is vanilla;
the pack ships its own `AN/ZPY-3` sensor definition.

## Install

1. Copy `SEST_ADF_Persistent_ISR/` into `Sea Power_Data\StreamingAssets\`
   (or rerun `tools\install-sest-packs.ps1`).
2. Place it **below** the MQ-9 Reaper mod in the Mod Manager (additive — it
   only adds a new unit, so ordering is forgiving).
3. It appears under Australia in the mission editor as a UAV, and the SEST RAAF
   Bases rebuild stations it at Edinburgh, Tindal, Woomera and Learmonth.

## First-flight checks

- The Triton hides the donor's pusher prop and flies as a clean jet, but is visually
  undersized (20 m mesh vs 39.9 m real span). It uses the donor's 42nd ATKS gray livery
  with the Australian flag.
- Confirm the AI holds a stable orbit and that the landing pattern works at Woomera.
- The radar is the only emitter: the optics, ELINT and RWR are all passive. If the MTS-B
  or the ELINT fit ever shows as an emitter, that's a bug in this pack, not the game.

## Rebuilding

```bash
python3 integration/adf-persistent-isr/build_pack.py
```

Validates the MQ-9 ER donor layout, every hidden submodel, the vanilla and
MQ-9 sensor definitions and the animation file against `mods-source/` before
emitting; fails loudly if the donor mod updates incompatibly.
