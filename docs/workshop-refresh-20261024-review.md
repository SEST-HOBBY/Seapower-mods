# Workshop refresh, 24 October 2026

One capture on the PC, `970a3578` ("chore: capture workshop refresh
2026-10-24") on `chore/workshop-refresh-20261024`, fast-forwarded on top of
`88bde742` (the F11 split). The game session it logged ran the build installed
before that, Codex's private playtest (`a4fc5b16...` runtime DLL in
`plugin-dlls.txt`). No game update: Sea Power is still 0.8.7 Build 261021
(Steam build 26103404), and `check_vanilla_drift.py --since 1bda58a6` finds no
drift. **Nine author updates**, no mod added or removed (199 Workshop mods; 190
unchanged). The facts are in `data/install-snapshot/workshop-refresh-summary.txt`
(regenerated here); this is the judgement.

The capture breaks no SEST build or gate. One SEST record needed a hand fix:
Euromod Chile renamed a hull that SEST's cost mappings named. Everything else
rebuilt: SEST forks of eleven changed files take the authors' changes, and the
world sandbox follows the rename.

## 1. SEST's plugins in the logged sessions

`player.log` and `player-prev.log` show every runtime module installing on
0.8.7, with the Combat Cost Tracker 0.7.1 beside them. These are the first PC
lines for Codex's F11 build, and no module reported a failure:

- MST terrain correction installed
- task-force debrief correction installed
- campaign combat costs installed
- combat inventory capture installed
- Cumulative Combat Costs and Last games embedded in original F11

The earlier session played two Task Force campaign missions and logged both
debriefs. They reproduce the stores carry-over bug the owner reported:

| Debrief | Mission total | Campaign total |
|---|---|---|
| Mission 2 | Player $77.2K, Enemy $1.96M | 1 mission: Player $77.2K, Enemy $1.96M |
| Mission 3 | Player $10.8K, Enemy $0 | 2 missions: Player $88.0K, Enemy **$500K + ?** |

Mission 2's enemy losses fell from $1.96M to $500K plus unknown once mission 3
had launched. The native rows stayed, but SEST's lost-stores and expenditure
keys were gone. That is the cause fixed in `88bde742`:

- `SaveDebriefSnapshot` copies the debrief into the campaign `.sav` before SEST's keys are written.
- `LinearCampaign.Initialise` rebuilds the temporary state from that `.sav` when the next mission launches.

On this campaign, mission 2's stores come back from the local history record if exactly one completed record matches. The PC check is `docs/playtests/campaign-costs-panel-20261024.md`, step 9.

`player-prev.problems.txt` has the usual hits: SEST's "missing from section 3"
false positive, CombatWorker's SecondThrust fallback and IDX's missing
localisation file.

## 2. The updates

| Mod | Change | SEST |
|---|---|---|
| Euromod - Modern US Navy (3390330875), v622 | `usn_lhd_wasp` and `_early`: commented circuit lines removed and one duplicate `ExitPosition` dropped (the same as its `Position`). `usn_mh-60r_p2`: `WeaponSystem1Default` moved below `Empty`, unchanged. | SEST Replenishment's two Wasp forks rebuild with the change. |
| Modern US Airbase (3592460366) | `airbase_us` gains frontal, side and bottom areas, KC-46A/KC-10A/KC-135 tanker squadrons, and a malformed `S-70B-2_Seahawk=Squadron1=5=5` line. | The 17 RAAF/RNZAF base forks take the three area lines only, because their air groups are SEST's own. The malformed line is not carried. |
| U.S. Navy 2027 Capabilities (3606774881) | EA-18G, F/A-18E/F, F/A-18F Block III: EO camera views, ±70° pitch limits. MH-60R: AN/ALR-94 ESM and AN/ALQ-144 jammer, EO attack views, weapon stations 3/4 lowered by 0.0005, Mk 54 Mod 2 (`usn_mk54_2_air`) in place of `usn_mk54_air`. Ticonderoga VLS 2027: its alias file now spells out the base's general values. | Growler NGJ/MALICE's four Hornet forks, the Allied Fixes MH-60R (AGR-30 Redback pods retained) and Replenishment's Ticonderoga fork rebuild with the changes. |
| F-35C Lightning II Alt. Loadouts (3607989779) | EO views, ±70° pitch limits. | SEST F-35C JATM's fork rebuilds with them. |
| Euromod - Main Pack (3629144864), v487 | New sensors: Scimitar RWR, Sphinx ESM, RAMSES ECM and related system groups. | None directly; Chile now uses them. |
| Euromod - Scandinavian Navy (3642656500) | NASAMS reworked: `scn_nasams_essm_ii` removed, own `[scn_NASAMS_MML]` launcher (900 s reload), AIM-120C-7/AIM-9X and Sentinel radar edits. Iver Huitfeldt's CEROS director renamed `dk_iver_CEROS-200_CWI`. | Replenishment's Iver Huitfeldt fork rebuilds with the new director name. No SEST mission fields the NASAMS. ESSM-II's price leaves the cost list with the file. |
| Euromod - JMSDF (3695809489), v42 | SH-60J/K: tail modex submodel, squadrons 2 → 5 (Squadron1 and Default keep their names), Asahi/Atago/Maya variant edits. | Mogami, Replenishment and the campaign rosters name Default or Squadron1, so all still resolve. Visual only. |
| THE REDFOR MOD (3732654992) | New: X-59MK (`red_x-59mk`), Buk-M3 TELAR/slave/radar (`wp_buk-m3`, `wp_bukslave`, `wp_m3-radar`), AS-18 materials. Su-30SM2 carries the X-59MK on station 20 and drops `AntiShipPrecision`. | `wp_buk-m3` and `wp_bukslave` collide with BUK-M3 (3564792549), which loads first (148 against 188) and still wins: Collection Fixes' Buk-M3 launcher repair checks the winner and passed. SEST flies the Su-30SM2 only as combat air patrol. The X-59MK takes a labelled model price (USD 2.0M) in the cost list. |
| Euromod - Modern Armada de Chile (3776730617), v9 | `ch_ffg_jvh` renamed `ch_ffg_jacob_van_heemskerck`. Karel Doorman and both Type 23s point to the Main Pack's new sensors, and its own duplicate sensor sections go. | Hand fix: `mappings.json`'s reviewed mapping moves to the new id. The world sandbox regenerates with it; the frigate is still not placed. |

## 3. Validation

All 25 packs rebuilt from scratch (4,294 files), with the 13 gates and the tool and campaign suites run on the result; `data/campaign-costs-panel-review-20261024.json` holds the counts. No mission file changed.
