# Setup Runbook — cleaning the 109 and installing the SEST packs

Follow top to bottom on the gaming PC. Everything here reflects the file-level findings from
`mods-source/` and the five SEST packs on this branch.

## Phase 0 — before touching anything

- Screenshot your current in-game Mod Manager order (rollback reference).
- Unsubscribing is reversible; nothing below deletes local files you can't get back.
- On the PC: `git pull` in your `Seapower-mods` clone so you have the latest `integration/` folders.

## Phase 1 — verify the loaders (do this FIRST)

The collection's code-level mods stand on two loaders; confirm them before any cleanup so you
don't misdiagnose breakage later.

1. **Anchor Chain** — subscribed ✔ but "will not function on its own": its documented manual
   preloader install must be done. Quick test: if the **B-2 Spirit** shows up and flies in-game,
   both loaders are fine.
2. **SeaLifter** — not in your subscription list, but required by A-10A/A-10C, Su-25, Mi-8 T/TV,
   B-2, and the Type 003/004 carriers. If any of those is missing from the unit list, install
   SeaLifter (subscribe + its preloader) before proceeding.

## Phase 2 — unsubscribe list (revised — read the KEEPs)

| Mod | Action | Why |
|---|---|---|
| Shahed-136 Drone (Obiwonkanblomi) | **Unsubscribe** | Duplicate; Zero Two's Geran-2 version is the more complete and stays |
| [DEPRECATED] F-35C (MyGo) | **Unsubscribe** | Superseded: US Naval Aviation carries the maintained F-35C, and SEST_F-35C_JATM builds on that |
| F-35C Lightning II Alt. Loadouts (Prof_CH4OS) | **Unsubscribe** | It patches the MyGo standalone you're removing; SEST_F-35C_JATM replaces the role on the maintained airframe |
| [DEPRECATED] F/A-18E/F (MyGo) | **Unsubscribe, then smoke-test** | Modern US Navy / USNA cover the Super Hornet. After removing, spawn a Murder Hornet loadout — if the jet's model is missing, resubscribe and report it (Murder Hornet's target mod is unconfirmed; I'll rebase it like the F-35C) |
| ADO – Nimitz (2000s) | **Keep for now, decide after test** | Flight Deck Ops is the renamed continuation; ADO-Nimitz may *depend* on it rather than compete. Test a Nimitz with both enabled, then with ADO disabled — keep whichever deck behaves |
| [DEPRECATED] E-7A Wedgetail (Pog Frog) | ⚠️ **KEEP** (changed advice) | **SEST_RAAF_Bases uses it** — Williamtown's AEW&C wing. Deprecated but functional |
| [DEPRECATED] S-70B-2 Seahawk (Pog Frog) | ⚠️ **KEEP** (changed advice) | **SEST_RAN_Fleet and Townsville use it** — LHD air groups and RAN dets |

Everything else stays. The three Fujians / four MH-60 sources / duplicate missile definitions
are a mod-order question, not an unsubscribe question — the file-level scan (roadmap item 1)
settles those properly later.

## Phase 3 — install the five SEST packs

Copy these folders from the repo's `integration\` directories into
`Sea Power_Data\StreamingAssets\` (next to `original` and `user`):

1. `SEST_F-15EX_Revamp` — 4 new F-15EX loadouts (LRASM×6, Harpoon, Quicksink, AIM-174B)
2. `SEST_F-35C_JATM` — AIM-260 fits for the Ford's F-35Cs (+ fixes USNA's duplicated AntiShip section)
3. `SEST_RAAF_F-35A_JATM` — 3 AIM-260 fits for the RAAF F-35A
4. `SEST_RAAF_Bases` — 15 Australian airbases, 211 aircraft
5. `SEST_RAN_Fleet` — 7 RAN classes, 26 named hulls

Then enable all five in the Mod Manager.

## Phase 4 — mod order (top = highest priority; the higher-listed mod wins file conflicts)

```
── Tier 1: loaders ──────────────────────────────────────────
Anchor Chain                     (SeaLifter loads via its preloader)
── Tier 2: weapon/system databases ──────────────────────────
SAM Pack                         (author: "top of TOE")
PLA Land Unit Pack               (author: above any PLA-related mod)
Dingtools Weapon Pack            (author: above any dingtools mod)
Euromod - Main Pack
Modern PLAN Systems
── Tier 3: patches (each above what it modifies) ────────────
U.S. Navy 2027 Capabilities
SEST F-15EX Revamp               ← above the F-15EX mod
SEST F-35C JATM                  ← above US Naval Aviation & Modern US Navy
SEST RAAF F-35A JATM             ← above the RAAF F-35A mod
F/A-18 Murder Hornet
B-52G with AGM-86
Tu-95 With AS-15                 (its global munition edits make it a patch)
Flight Deck Ops
ADO - Nimitz (2000s)             (if kept after the Phase 2 test)
Ground Upgrade: SPAA
── Tier 4: core faction packs ───────────────────────────────
Modern US Navy · United States Naval Aviation · all Euromod
addons (both Spanish, British, German, Dutch, Nordic, Italian,
JMSDF) · SEST RAN Fleet · Chinese Navy · Russian Navy 21 ·
submarine packs · carriers & amphibs
── Tier 5: individual units ─────────────────────────────────
All standalone aircraft/helis/UAVs/land systems (E-7A, S-70B-2,
P-8, U-2, tankers, MQ-9, AH-64, fighters, bombers...) · Civil
Aircraft Mod
── Tier 6: airbases last ────────────────────────────────────
SEST RAAF Bases · Modern US Airbase · Modern Russian Airbase ·
Modern Chinese Airbase
```

## Phase 5 — ten-minute smoke test

1. **F-15EX** → loadout picker shows 18 entries including AntiShipLRASM6, AntiShipHarpoon, StrikeQuicksink, Intercept174.
2. **Ford (JSF variant)** → F-35C flights offer *Intercept (AIM-260, stealth)* and *Intercept Beast*.
3. **RAAF F-35A** → three Intercept fits present.
4. **Place RAAF Base Williamtown** → F-35As and E-7As spawn (E-7A livery is the default one — expected).
5. **Place RAAF Base Tindal** → B-52H/B-2 present (B-2 also re-proves the loaders).
6. **Spawn HMAS Hobart** → Australian ensign shows (if the flag is blank, report it — one-line fix), MH-60R on deck.
7. **Spawn HMAS Canberra** → helicopter-only air group operates.
8. **Murder Hornet check** from Phase 2 if you dropped the MyGo F/A-18E/F.

Anything that fails: note which step and paste what you see — every SEST pack regenerates from
a script, so fixes are fast and versioned.
