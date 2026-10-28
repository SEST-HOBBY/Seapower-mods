# SEST World Sandbox 2028 - Regional Expansion (preview)

An **optional new-game world** for Dynamic Campaign Mod 0.25.0 (3813157776, the version installed in the 24 Oct capture).

On 25 Oct 2026 the purchase list grew from 1,559 to 1,561 entries (Euromod RAN's F-35A Block 4 and late F-35B), and US Naval Aviation's HH-60H rename (`usn_hh-60` to `usn_hh-60h`) went into both worlds, with an alias that keeps older saves' helicopters. The same day the mod updated to 0.25.0.1: a rebuilt DLL, with its own campaigns' data unchanged (`docs/workshop-refresh-20261025-review.md`). This world's start was seen on 0.25.0 and has not yet been seen on 0.25.0.1. On 28 Oct 2026 both worlds' twelve US Navy P-8As became U.S. Navy 2027's `usn_p8_2027` (PR #47, rebuilt), and Red Storm Arsenal's P-3-bodied `usn_p_8a` left the buy list: 1,560 entries (`docs/playtests/world-p8-20261026.md`).

- **Separate campaigns.** The original `sest.world_sandbox_2028` campaign and its saves are unchanged. The variant has its own id, `sest.world_sandbox_2028.regional`, and folder, `dynamic_campaigns/sest-world-regions-2028/`, and both are listed in the Campaign menu.
- **How it is built.** It is generated from the original by `integration/world-sandbox/build_regions.py` and the spec `integration/world-sandbox/regions-2028.json`. `build_dynamic_campaign.py` runs it after the original, so `tools/build_all.py` builds both.
- **Same inputs, same bytes.** A test rebuilds the variant from the spec and compares the bytes with the shipped file.

| | Original | Regional |
|---|---:|---:|
| Bases | 141 | 156 |
| Forces (BLUE / RED) | 267 (170 / 97) | 293 (170 / 123) |
| Patrols | 49 | 54 |
| Purchase entries | 1,560 | 1,560 |
| Replenishment ship types | 7 | 9 |

## What it adds

All 26 additional forces are RED. The BLUE forces, the member nations, the purchase catalogue and the original bases are unchanged.

- **Europe.**
  - Kronstadt: three corvettes patrolling the central Baltic.
  - Chernyakhovsk: eight Su-30SM2 and four Su-24M2.
  - Krymsk: eight Su-30SM.
  - Pskov: two Il-76MD and four Mi-8.
- **Libya and the Sahel.**
  - Tobruk: a corvette on a coastal patrol, and a Pashin replenishment ship.
  - Al-Khadim: MiG-29s and Mi-24s.
  - Al-Jufra: Su-25SM3s and Il-76s.
  - Bamako, Niamey and Bangui: helicopter detachments.
  - These are **fictional 2028 Russian detachments or access arrangements**, not claims of sovereignty or current orders of battle.
- **Eastern Mediterranean.**
  - Tartous: a Project 11356 frigate on patrol, and a Pashin replenishment ship.
  - Hmeimim: four Su-30SM and two Il-76.
  - Syrian access is a **scenario assumption**: this Dynamic Campaign Mod release has no host-basing model, so the host is abstracted as RED-controlled.
- **Iran.**
  - Chabahar: an Alvand frigate and three Peykaap boats patrolling off the Makran coast, and a Delvar supply ship.
  - Konarak: six F-4E.
  - Shiraz: four F-14A and six F-4E.
- **Gulf of Aden.** A Type 054A and a Type 903A from the existing PLA base at Djibouti, on an escort patrol.

## Replenishment (24 Oct, Claude)

The mod moves fuel and ammunition at sea from a ship type listed in the campaign's `replenishment` table. A force starts loaded only when it is marked `cargo: full`. The committed variant had neither for its Russian supply ships. Now:

| Ship | Fuel (t) | Ammunition (t) | Basis |
|---|---:|---:|---|
| `rfn_aor_pashin` (Tobruk, Tartous) | 6,500 | 250 | About 40% of its 16,250 t game displacement, in line with the original's supply ships |
| `ir_aor_delvar` (Chabahar, new group in harbour) | 350 | 50 | Sized to its 904 t game hull. GPT's draft of 2,100 t fuel and 100 t ammunition exceeded the ship's own displacement |

These are game-balance estimates, not certified ship stores. `build_regions.py` adds them to the table without changing any of the original's figures. It stops if a `cargo` force carries no listed supply ship. The original's seven supply ship types and their loads are unchanged.

## Fixes made in this pass

- **A patrol waypoint on land.** The validator's water check, which needs `global_land_mask`, was skipped where the variant was first generated. It finds the Tobruk coastal escort's third waypoint, 32.8 N 22.3 E, on land near Derna. The point moves to 33.1 N 22.3 E, and every regional patrol leg is checked at sea along its length.
- **Reproducible output.** The committed JSON had been serialised differently from the builder. It is now always regenerated, and a test compares the shipped bytes with a fresh build.
- **The Chilean frigate.** New campaigns use `ch_ffg_jacob_van_heemskerck` only. The save alias `ch_ffg_jvh` (from PR #43, consolidated here) stays loadable for old saves but is never sold. Its alias line named `ch_ffg_jacob_van_heemskerck.ini` without its folder, and `check_alias_bases.py` reported it as a unit file the game cannot load. It now reads `#!alias vessels/ch_ffg_jacob_van_heemskerck.ini`, as every other alias in the collection does, and the test that required the old form checks the new one.

## Install and playtest

1. Install the playtest bundle for this branch (or sync the branch) and restart the game fully. Dynamic Campaign Mod 0.25.0 and the current collection must be enabled.
2. **Campaign menu.** Both *SEST World Sandbox 2028* and *SEST World Sandbox 2028 - Regional Expansion (preview)* are listed. Start the **Regional** one as a new campaign. Do not Continue an original World Sandbox save into it.
3. **START CAMPAIGN** reaches the strategic map with no "this game has no ..." error. Try both sides. As RED, the regional bases and forces appear and can be bought for and ordered.
4. **Patrols.** Let a few days pass:
   - the Baltic, Tobruk, Tartous, Makran and Gulf of Aden patrols move along their routes;
   - aircraft at the new air bases fly;
   - nothing spawns endlessly.
5. **Replenishment.** Send a regional surface group within 5 NM of its Pashin or Delvar.
   - Fuel and ammunition rise, and the supply ship's cargo falls.
   - Watch for any unlimited or duplicated stock.
6. **Battles.** Let a contact become a battle. The right forces should appear, and survivors, losses and ammunition expended return to the map.
7. **Persistence.** Save, quit to the menu, reload: positions, damage, purchases, fuel, stocks and losses survive. Run several combat and supply cycles.
8. **The original World Sandbox** still starts and loads on its own.

Send `Player.log`, `BepInEx/LogOutput.log` and screenshots of any error.

## Remaining runtime uncertainties

Only the start has been seen. On 24 Oct 2026 the owner started it as a new campaign on the uploaded build (`8e72f353`). Patrols, replenishment, battles and saves have not been reported. Static validation (`check_dynamic_campaign.py`: engine rules, audit references, SEST collection and water checks) is not an in-game test.

- **Replenishment accounting** between the mod's strategic transfer and SEST Replenishment's in-battle rules is untested; `DYNAMIC_CAMPAIGN_ADAPTER.md` already flags it.
- **Long supply lines.** Supply from the Novorossiysk depot to Bamako, Niamey and Bangui (2,600 to 3,000 NM) may rarely arrive.
- **AI use of the new forces.** Whether the RED AI uses the new air detachments and patrols actively, or leaves them idle, is unknown.
- **Battle density.** Starting patrols near BLUE assets (Djibouti, the Eastern Mediterranean) may produce early battles. The density has not been tuned.
- **Runway headings.** They are taken from the real airfields. Seventy bases in the original carry the same validator note.

## Change log

- New optional campaign, *SEST World Sandbox 2028 - Regional Expansion (preview)*: 15 bases and 26 RED forces across the Baltic, Black Sea, Libya, the Sahel, Syria and Iran, plus a PLA escort group in the Gulf of Aden. Russian and Iranian supply ships replenish their regional groups.
- World Sandbox: starts again after Euromod Chile's frigate rename. Old saves keep their frigate.
- The original World Sandbox is otherwise unchanged.

Sources for the regional background (scenario framing only; force allocations are fiction):
- Russian presence in Libya: https://www.tearline.mil/public_page/libya-russia-develops-air-base-infrastructure-likely-to-secure-military-foothold-in-sahel-region
- Africa security relationships: https://www.everycrsreport.com/reports/IF12389.html
- Eastern Mediterranean access: https://www.al-monitor.com/originals/2026/09/russian-convoy-resupplies-syria-coastal-facilities-first-time-moscow-damascus
