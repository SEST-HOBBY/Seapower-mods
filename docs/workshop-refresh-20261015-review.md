# Workshop refresh, 15 October 2026

Captured on the PC on 15 Oct (`chore/workshop-refresh-20261015`: e4787d2e the
first capture, ac15c0b3 the export, da383f67 the capture after the first
launch on the local install). Built on `feature/workshop-update-20261015`.

## 1. The install

- SEST loads from the local `StreamingAssets\SEST_Integration` at position 1;
  the Workshop copy (3812461539) is unsubscribed and gone from disk. The live
  order matches `data/load-order.tokens.txt` and every SEST override outranks
  its target (`check_load_order.py`). 196 Workshop mods, nothing new or
  removed.
- **The game is 0.8.6, Build 261014** (Unity 6000.0.84f1): crash fixes,
  among them one when mods push the unit catalogue past 4,032 classes. Every
  pack now says `ApproximateVersion=0.8.6` (24 builders).
- The stock-game mirror (`mods-source/_vanilla`) was not re-exported, so it
  is still 0.8.5's. 0.8.6's notes list crash fixes and the Unity update only,
  and `StreamingAssets\original` still holds 7,643 files, so no stock data is
  expected to have changed. Confirm with `export-mod-configs.ps1
  -IncludeVanilla`; `check_vanilla_drift.py` then says.

## 2. The mods that changed

| Mod | What changed | Effect on SEST |
| --- | --- | --- |
| Euromod - Main Pack (5_12's notes) | Shafrir 2, a 30 mm HEDP round, seven sensor and weapon sections | All prefixed `eu_` (`eu_M230`, `eu_AN/APG-78`, `eu_Agave` ...): no collision with AH-64 Apache's M230 and APG-78, which SEST's five Apaches hang, or Etendard Family Jets' Agave |
| Euromod - Modern US Navy | The battle flag moved into each Burke's Default loadout; the BattleFlag loadout dropped | SEST Replenishment's Burke forks re-forked |
| Spanish Navy Mod (Cold War) v3.54 | Moroccan Lazaga fast attack craft, reliability values, scenarios moved to a folder | Replenishment forks the new hulls; the world sandbox's arsenal gains Morocco (two units) |
| Spanish Navy Mod (Modern) v1.46 | Reliability values, one-line `AssociatedSensors` lists | The RAN fleet's clones (Hobart, Canberra, Choules, Collins, Arafura, the supply ship) follow; stock uses the one-line form in 127 ship files |
| Anduril Maritime Drones | A propeller shaft and material on the Dive-LD and XL | none |
| Identify Expanded | One DLL, 3.420; a MissingMethodException fix; formation logic for aircraft | none. Its log says it cannot find its language file (it looks under `StreamingAssets\IdentifyExpanded`): a note for the author |

The PLAN Pack, Ka-31, Tu-214R and E-3G show as "updated" in the update check
because of the line-ending fault the inventory check names, not because their
authors changed them.

## 3. The pictures log

Menu plugin 1.1.0 wrote 1,356 `[SEST Pictures]` lines in twelve passes:

- **Start-up screen**: stock `original\ui\backgrounds\loading_screen_74.png`
  with the MicroProse and Triassic logos, shown before any mod is read. A
  mod cannot replace it by file.
- **Main menu**: the background is drawn from the `ui/backgrounds` pool and
  changes while the menu is open: SEST's `loading_screen_80` first, then
  PLAN Pack's `plan_loading_screen_15`.
- **Mod Manager**: The Royal Navy's (3491248180) `loading_screen_17`,
  although SEST ships a `loading_screen_17` and sits 196 places above it.
  In this log, for pictures, the mod lower in the order won the shared
  name. The Royal Navy ships `loading_screen_1` to `30`, so SEST's first
  30 slots may never show. One observation; a second session would confirm.

A decision for the player: whether to move SEST's set onto names no other
mod uses (the pool then holds SEST's 80 beside The Royal Navy's 30 and
PLAN's), or leave it.

## 4. Gates

Every gate passes but `check_inventory` (the four CR-stripped mods still owed
a `git add --renormalize`). 191 campaign tests and 98 tool tests pass. The
zone rule holds on the rebuilt files: no box inside a circle still waiting
for a unit, 22 escorts with no box as before.

## 5. Commons photos from the acquisition kit

The image acquisition kit of 14 Oct (`tools/image-acquisition`) ran on the PC
and downloaded 79 licence-checked Wikimedia Commons photos; 31 groups stayed
pending (five Anduril families held for permission, seven concepts held, 19
with no usable photo). The photos went to `chore/image-intake-20261015`, which
is never merged. Every one was looked at against its unit
(`integration/gallery/commons-review-20261015.csv` gives each verdict and
reason):

- **38 approved**, taken in by `integration/gallery/commons_photos.py` with
  their Commons credit, licence and SHA-256 (`commons-photos.csv`): 23 the
  same type as the unit, 13 class photos, two gallery-only context photos
  (Liaoning small behind the Dalian yard; a training launch tube for the
  Minuteman silo). 17 public domain, 2 CC0, 19 CC BY or BY-SA.
- **32 units get a new encyclopedia picture**, among them the Buk-M3 and its
  radar, Topol-M, KF-21, KUH-1 Surion, Yasen, Admiral Grigorovich, Incheon,
  Peykaap III, Todaro, HH-3E, the Arafura and RAAF Edinburgh, Scherger and
  Tindal. The J-15D's render-infographic picture, judged unusable, is
  replaced by a J-15 class photo. A reviewed exact picture is never
  replaced.
- **41 rejected**: five would have replaced the SEST author's own photos
  (B-52G, DF-21, DF-26, F-16A, J-35) and are refused by the importer; nine
  duplicate or fall short of photos the gallery already has; the rest show
  the wrong subject (a childcare centre for Whenuapai, a house for
  Barksdale, a meeting for the ROK MH-60), a render or drawing (Bonifaz,
  Chungnam, Suffren), or the subject too small to see.
