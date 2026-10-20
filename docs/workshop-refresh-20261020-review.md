# Workshop refresh, 20 October 2026

Two captures on the PC, both on game 0.8.6 Build 261014 (no game update,
nothing under `_vanilla` moved):

- `40deeb7f` on `chore/workshop-refresh-20261020`, 12:40 Brisbane, from the
  deploy branch at `e7b32f11`: seven author updates and two new
  subscriptions.
- `6d67dcfa` on `chore/workshop-refresh-20261020b`, 17:52, on top of the
  first: Euromod-India-Navy's afternoon update, with the PC running GPT's
  `f0d9d915` build.

Both are merged into `sest-dev/jolly-ride-rptj4t` together with GPT's line
(`gpt/fleet-terrain-debrief-20261020`, ten commits on `e7b32f11`). The
facts are in `data/install-snapshot/workshop-refresh-summary.txt`; this is
the judgement. Each mod's review was done by its own reader and checked
against the from-scratch rebuild of the capture; the adversarial second
pass did not run (spend limit), so every claim below was re-read here
before it was acted on.

## 1. The updates

| Mod | Change | SEST |
|---|---|---|
| Euromod - Modern US Navy (3390330875), v618 | The OHP long-hull LAMPS-3 alias is gone, replaced by a standalone `usn_ffg_ohp_longhull_sh60b` (a flattened vanilla long hull: SH-60B x2, SQR-19, Mk 46 Mod 5, one Nixie, one loadout). The Wasp's deck stock: capacity 45000 -> 85000, Harpoon 48 -> 88, AirTorpedo 80 -> 30, AdvancedARM 64 -> 94. The OHP MLU's variants enter service in 2020 instead of 2099. | SEST Replenishment now forks the new hull (its two SRBOC launchers reloadable). Its Mk 13 names `WeaponMagazineMK13Late`, which the flattened file no longer defines, so the launcher never loaded: repaired in `ras.py` HULL_REPAIRS. The Wasp fork re-based cleanly. The world campaign's buy list follows the rename on the rebuild. Nothing else in SEST named the old id. |
| Euromod - Main Pack (3629144864) | Adds `eu_Spherion_B`, a hull sonar equal to the Anzac mods' Spherion B, and its English name. | No key clash; no unit uses it yet. |
| Mogami-class frigate (3456859157) | The ESSM VLS now lists the OPY-2 fire-control radar. | SEST JMSDF Mogami re-forked with its own edits intact. |
| Gerald R. Ford-class CVN (3461044389) | SPY-3 added to both Mk 29 ESSM launchers on all three hulls. Air group, deck and variants unchanged. | SEST Replenishment's forks re-based; GPT's F-35C wing applies on top (the rebuild, not a hand merge). |
| US Naval Aviation (3737267013), v99 | Re-ships `usn_aim-9l`, `usn_aim-9m` and `usn_gbu-24`; the F-35C gains `AirToAirLongRange` (six AIM-120D3 internal); AIM-120C/C7/D/D3 gain TerminalLoft and a reliability trio; the Stinger gains MaxTurnG=25. | USNA's AIM-9M (vanilla flight model) now wins - the player's call is to keep it. SEST's AIM-9L fix is rebased onto USNA's file (below). SEST F-35C JATM carries the new fit. The GBU-24 stays shadowed by SEST's vanilla copy. |
| PLAAF Aircraft Pack (3812111085) | Retunes 16 rounds; only the PL-15S reaches the game (through the PLA AEP's `#!extend` stub): seeker 8 -> 13 NM, flight time 245 -> 180 s. YJ-98 SearchVelocity 1650 -> 550 kt. | The J-35's PL-15S changes in Red Line (player side), Southern Watch 11 and Southern Reach / Tasman Shield. GPT's J-20 change is on the airframe; the J-20A's `_LQS` rounds are untouched, so nothing doubles up. The 17 Oct review said the PL-15S retune did not reach the game; it did, through the stub. |
| Anduril Maritime Drones (3819522350) | Needs Anchor Chain now; a contact-strike DLL (K5KrakenContactStrike 1.0.0, 8 hooks, OWA variant only); licence widened to code. | SEST borrows no Anduril file. The DLL loads beside SEST's two plugins with no hook conflict (both captures). Paper Trail's recon K5 is unaffected. |
| MV-75 Cheyenne II (3810611344) | Steam's date moved; no exported file or DLL changed: a model or texture update. | Look at Valor 73 in D8 at the next play test. |
| Euromod-India-Navy (3807164392), afternoon | Mount positions on the F-33 and F-47 hulls. | Not placed by any SEST mission. |

## 2. New mods

Combat Cost Tracker (3807187341) and Group Manager (3818251045) join the
collection (the player, 20 Oct): 200 Workshop mods, 201 Mod Manager
entries. GPT's line had already placed both in the canonical order and the
catalog, and adds SEST's cost compatibility list
(`COST-COMPATIBILITY.txt`). Both load through Anchor Chain with no error.
The collection (3812390790) and the item's Required Items need both added
on Steam before the next upload.

## 3. Fixes made in this pass

- **OHP long hull Mk 13** (`integration/common/ras.py`): the launcher names
  its magazine again.
- **AIM-9L** (`integration/collection-fixes/build_patch.py`): rebased onto
  USNA's file. The F-16 pack's copy turned at 90 deg/s, faster than the
  R-73 (60) and SEST's AIM-9X (70), and almost four times the AIM-9M now in
  the game; USNA's is vanilla's scale (24 deg/s, 40 g). The same two
  defects are corrected. A guard now stops the build if the winning AIM-9M
  ever carries them.
- **Briefing photos** (`build_pack.gallery_catalogue`): a unit SEST forks
  is won by the pack's own record, which the gallery index holds without
  the photo; 54 placed units showed none, the P-8A (35 missions), Type 054A
  (25) and Type 056A (14) among them. Another record's photo of the same id
  now stands in. The briefing's eight recognition slots are now split, four
  a side with any unused half going to the other: with the player's side
  better pictured it had crowded the opposition out (Red Line 03 lost the
  RAAF F-35A), and within a side military classes come before civilian
  `civ_*` traffic. The RAN's own Seahawk (`ran_mh-60r`, 31 missions
  since GPT's change) and the RQ-7 field team (12) take the gallery's MH-60R
  and RQ-7 photos through `profiles.tsv`, as the Danish MH-60R does.
- **REQUIRED-MODS** (`build_pack.resolve`): rounds are credited down an
  `#!extend` chain to the full copy, and a deck's embarked aircraft (the
  mission's air group, else the variant's, else the hull's) are credited
  with every round their fits hang. Red Line and Southern Reach had listed
  the PLAAF Aircraft Pack as unused.
- **D1 Western Passage**: the new crediting found HMS Richmond's deck
  carrying the Royal Navy mod's Sea King (her hull's default group is a
  Wildcat and a Sea King) beside the Wildcat the mission places as
  Richmond Flight. The Sea King left service in 2018; the hull now carries
  an empty group of its own, so Richmond Flight is her one helicopter, and
  the Royal Navy mod is again reached by nothing.
- **D8 The Long Perimeter**: GPT's last commit changed the deployment-zone
  builder without rebuilding D8; the rebuild splits its detachment box in
  two (it does the same on GPT's commit alone).
- The GBU-24 consumer comment in Collection Fixes names its live consumers.

## 4. Left for later

- No checker resolves a placed carrier's effective air group; a Ford
  variant's unresolved `usn_mh-60r_26` went unseen until GPT replaced the
  variant wings.
- `tools/check_mod_conflicts.py` under-counts SEST collisions for USNA
  (sorts SEST packs by the wrong rank).
- CREDITS does not show USNA's share of SEST's F-35C file (below the 90%
  whole-file threshold).
- The PL-15S keeps MaxLaunchRange 125 NM with a 180 s flight limit; SEST's
  reach gate reads 125, which is conservative.
- Upstream, worth telling the authors: the OHP Mk 13 magazine name and the
  Chinese name key `usn_ffg_ohp_longhull_sh-60b` (Modern US Navy).
