# NF3 Scenarios

Small standalone missions carved out of **NORTHERN FRONT III FINAL NEWEST** by
`../make_scenarios.py`. Every unit keeps the type, loadout, position and waypoints it
has in the parent mission — these are the same forces, fought in isolation.

**Generated, including this file. Do not edit by hand.** Change the scenario list in
`make_scenarios.py` and re-run; the parent mission is never modified, so re-importing a
newer save and regenerating gives you scenarios that match it.

| Scenario | Units | The fight |
|---|---|---|
| **Sanctioned Convoy Intercept** | 84 | Three sanctioned tanker lifts are running out of Bayu-Undan, Ichthys and Montara under escort. A RAN inshore screen and a single strike pair have to sort neutral traffic from sanctioned traffic and stop the latter. Includes the full civilian layer. **+ran_aor_supply** injected into RAN Inshore Screen (not in the parent mission). |
| **Bomber Stream** | 27 | Nine H-6K Zhanshen inbound in three packages. Two F-22 flights and their tankers are all that stands between them and the coast. Pure air intercept - no surface units, no land clutter. |
| **Carrier Duel** | 15 | A Ford-class group and a PLAN carrier group in the same water, each with its own escort and air wing, and nothing else to hide behind. **+plan_aor_type901** injected into PLAN Carrier Group (not in the parent mission). |
| **SEAD over the Shelf** | 28 | An S-400 site and a supporting air-defence battery cover the shelf. A strike package with dedicated escort has to open the corridor. The SEST MALICE and AGM-88 fits are what this one is for. |
| **Boomer Hunt** | 78 | A PLAN SSBN group is transiting with escort. A NATO surface group and a single ASW pair have to find it before it reaches open water. Includes the full civilian layer. **+usn_take_lewis_clark** injected into NATO Fleet A (not in the parent mission). |
| **Ballistic Shield** | 25 | Four DF-26B launchers and a mixed Iskander/Scud/Shahed battery range on the northern bases. Darwin and Scherger have THAAD and PAC-3 and no depth to trade - every leaker lands on an airfield. |
| **Northern Fleet Sortie** | 11 | Varyag, an improved Kirov and three modern escorts against a Euro-NATO group of a Lafayette OPV, a K130, an Iver Huitfeldt and an F127. Five against five, except NATO is also shepherding the Algol - a 288 m sealift hull with no weapons that the whole group exists to keep alive. **The smallest of the set.** **+wp_vt_boris_chilikin** injected into Russian Carrier Group (not in the parent mission). |
| **Fujian Strike** | 22 | Type 003 Fujian with a Type 055, a Type 09X boat, Red October and eight J-15D against a Ford group. Where Carrier Duel is two gunlines in the same water, this one is decided in the air. |
| **Coastal Ambush** | 13 | An HY-4 coastal battery with a ZSU-23-4, a Shahed launcher and fuel bunkers sits on the headland. Two A-10Cs and the RAN inshore screen have to dig it out. The smallest scenario in the set - thirteen units, one hill, no room to be clever. |
| **Fifth Generation Sweep** | 25 | Three J-50 under six Su-35S and six J-16A, against eight Raptors and their tankers. Stealth on both sides, nothing on the surface, and the tankers are the only thing making the Raptors' fuel arithmetic work. |
| **Deep Strike Corridor** | 18 | A layered eastern IADS - HQ-16A, HQ-22A, HQ-19, a DF-21C and three Sejjil launchers around a modern airbase. A strike package, its F-15 escort and two A-10Cs have to open a corridor through it. A harder, deeper problem than SEAD over the Shelf, against a different air-defence mix. |

Entries marked **+<type> injected** carry a unit the parent mission does not have. Carving can
only subtract, and four of the source's twelve surface formations already sail with a supplier
(Carrier Group A has both the Kilauea and the Sacramento, NATO Fleet B the Algol, CN Carrier
group the Boris Chilikin) — so injection is aimed only at the groups that had none, to exercise
SEST Replenishment At Sea where it actually changes the fight. Each injected ship is placed at
the centroid of the formation it joins, nudged clear of the nearest hull, on the formation's
own heading, and appended to that formation so the AI keeps it in station.

11 scenarios. `tools/install-sest-packs.ps1` copies them with `-Recurse` into
`user\missions\user_missions\`, where the game lists them flat alongside the full
missions — the subfolder is a repo-side grouping only.

## Regenerating

```bash
python3 integration/missions/make_scenarios.py            # build all + this README
python3 integration/missions/make_scenarios.py --list     # show the source's formations
python3 tools/check_scenarios.py                          # validate every scenario
```
