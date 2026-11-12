# SEST MAKRAN LINE
## The Fuel Road — campaign lore and build brief

**Fictional campaign:** 24 October – 14 November 2028 (four missions) · **Written:** 11 November 2026 · **Package:** `integration/campaign/makran_line/` · **Slug:** `sest-makran-line`

**Premise:** With America's ready combat power drawn north, insurers stop covering the tanker road from the Gulf to Karachi, and the fictional Meridian Maritime Group offers the tankers its own armed "escorts". A Pakistan Navy task group, Task Force 88, keeps the road open.

**Confidence convention** (as Southern Watch's bible): *documented* is a cited public fact; *campaign assumption* is our fiction; *mod approximation* is an implementation compromise.

## 1. Canon and fiction

Makran Line sits inside Southern Watch's six weeks (Southern Watch bible, "Fictional campaign: 18 October–28 November 2028") and on the same premise: the confrontation elsewhere in the Indo-Pacific that "draws much of the immediately available US combat power north", and the Meridian Maritime Group's model of "escorted groups … inspections … preferred terminals", here carried to the Gulf–Karachi tanker route.

What is fiction (*campaign assumption*):

- The **Meridian Maritime Group**, its ships (MV Meridian Sentinel, MV Sea Venture, MV Sea Falcon, the "Meridian Escort" trawlers) and its operations.
- Every named merchant, tanker and dhow, and the 2028 war-risk listing of the North Arabian Sea.
- The **commander**. The default name, *Kamran Aziz Durrani*, is built from the game's own `[Names_Pakistan]` pool (first Kamran, middle Aziz, last Durrani). It was checked twice on 11 Nov 2026 before it shipped, and no naval officer of that name was found:
  - web searches for the full name, and for "Kamran Durrani" with Commodore, Admiral or Captain and "Pakistan Navy";
  - the English Wikipedia's "List of serving admirals of the Pakistan Navy", as last edited on 5 Nov 2026. It has no Durrani and no Aziz; its one Kamran is Rear Admiral Kamran Ahmed.

  The nearest namesake the searches found is not a naval officer: Kamran Shah Durrani, the nineteenth-century ruler of Herat. The Navy's own site could not be searched from the build environment, so an officer below flag rank with this name cannot be ruled out. The player can change the name on the commander screen, and the prose never uses it: the commander is "the task group commander" throughout.
- Task Force 88's 2028 operations, and the Regional Maritime Security Patrol resuming in the epilogue.

What is not in the story, on the owner's decisions of 11 Nov 2026:

- **No Indian or Iranian state unit** is placed, and no Iran-registered hull (the Peykaap III that Southern Watch and Sulu Line fly as Meridian craft) is used. Meridian fields **armed merchants and trawlers** only: the armed Okean and side trawlers, the Poltava freighter with SS-N-2 launchers, the armed ACT-1 and the armed ro-ro, all from Moloti's Armed Merchantmen, every one with an explicit `Nation=Meridian`.
- **No Baloch insurgency** and no fighting ashore.
- No Chinese or Russian unit: the Z-9CE registers Pakistan in the Pakistani Pack, and every placed unit's nation is checked by the campaign tests (`MakranLineTaskGroup`).

Documented. The news pages below could not be opened from the build environment: on 11 Nov 2026 each was found by a web search, and the facts are those the search gave for it. Read each page before quoting it anywhere else.

- **Task Force 88** was assembled by the Pakistan Navy for the seaward security of Gwadar port and its sea lanes (Dawn, 12 Dec 2016, "Special force set up to guard Gwadar port's sea lanes", <https://www.dawn.com/news/1301970>). It was inaugurated at Gwadar on 13 Dec 2016 (Voice of America through GlobalSecurity.org, <https://www.globalsecurity.org/wmd/library/news/pakistan/2016/pakistan-161213-voa01.htm>; Dawn's report of the ceremony, <https://www.dawn.com/news/1302102>). At the ceremony the command telescope went to its first commander, a Commodore (The Express Tribune, <https://tribune.com.pk/story/1262606>; Business Recorder, <https://www.brecorder.com/news/331446>). That is the campaign's reason for starting the commander as a Commodore (section 4).
- The **Regional Maritime Security Patrol** (RMSP) is the Pakistan Navy's own patrol programme, begun in 2018 to make its patrols region-centred and less dependent on navies from outside the region; it still takes its turns commanding the Combined Maritime Forces' task forces 150 and 151 (Business Recorder, July 2018, "PN plans regional maritime patrols in Indian Ocean", <https://brecorder.com/news/4616246>; Daily Pakistan, 12 Jul 2018, on the first RMSP deployment, <https://en.dailypakistan.com.pk/12-Jul-2018/pakistan-deploys-its-first-ever-navy-ship-in-gulf-of-aden-southern-red-sea-region>; for task force 150, Combined Maritime Forces, 28 Jan 2026, <https://combinedmaritimeforces.com/2026/01/28/pakistan-navy-assumes-command-of-combined-maritime-forces-combined-task-force-150/>).
- **PNS Moawin** (A39), the Navy's fleet tanker, was commissioned on 16 October 2018 (English Wikipedia, "PNS Moawin (A39)", read on 11 Nov 2026). The campaign has no supply ship because the collection has none (section 3).

## 2. The four missions

| Code | Date | Mission | What it is | Generation |
|---|---|---|---|---|
| MK01 | 24 Oct 2028 0630 | **The Fuel Road** | Two tankers from the outer roads to the Karachi pilot station; two Meridian armed trawlers come in from the west, a third shadows | Generated (anchor `escort`) |
| MK02 | 31 Oct 2028 0550 | **Gwadar Roads** | Three armed trawlers attack the Gwadar anchorage; an armed freighter with SS-N-2 launchers is anchored among the merchants and fires at minutes 14 and 32 | Generated (anchor `screen`) |
| MK03 | 6 Nov 2028 0130 | **Hangor** | Detached submarine operation: PNS Hangor classifies the mothership and takes station on her rendezvous, unseen, firing nothing | None (authored) |
| MK04 | 14 Nov 2028 0500 | **Port Qasim** (final) | Three tankers into Port Qasim; three trawlers and an armed ro-ro attack; the mothership runs for the open sea and must be sunk or made to heave to | Generated (anchor `escort`) |

Release terms, as each brief states them:

- **MK01:** both tankers within six miles of the Karachi pilot station.
- **MK02:** all three trawlers and the armed freighter sunk (a `destroy` victory with an `also` destroyed term; *Launcher* is "Also required" and flagged Main).
- **MK03:** Meridian Sentinel classified, then Hangor within three miles of the trail datum afterwards (an `after` classify stage that sets `MK03MotherNamed`). Any Meridian ship classifying Hangor ends it (`F("Unseen", kind="unseen")`), and so does a weapon on any ship.
- **MK04:** two of the three tankers within four miles of the Port Qasim anchorage, Meridian Sentinel sunk or hove to, and no incoming weapon tracked. The victory has two `any_of` paths, *Sunk* and *HoveTo*; a `turn_back` makes her heave to when the screen's lead ship is within three miles of her on her track (the ship's flight does not count), transfers her to Neutral, sends her to the Karachi roads at telegraph 2, and makes her later loss end the mission (a protected neutral, on the *Traffic* objective). *Mothership* is "Also required" and flagged Main. Progress reports (*Halfway*, *FirstIn*, *Running*) are intel lines only.

The one campaign variable: MK03 writes `MK03MotherNamed` when Hangor classifies the mothership; MK04 reads it to put her position on the plot as a datum for fifteen minutes (`reveal_if`, the shape of Red Line's Datum → Routes They Can See).

Geography: the proven-point pool has 24 sea points off Karachi and none off Gwadar, so every mission is proved against `integration/campaign/geo/arabian_theatre_coast.json` (Natural Earth 1:10m, design step P1). PAF Base Masroor, Gwadar airport, the HQ-16AE site and the C-602 battery stand ashore; every station at sea has 2 NM or more of water.

## 3. The 2028 force, and what the collection cannot field

A realistic Pakistan Navy surge group for this in 2028 would be two Tughril-class frigates, a Babur-class corvette, a Yarmook-class offshore patrol vessel, PNS Moawin or Nasr, maritime patrol aircraft and Air Force JF-17s on call.

What the collection fields (Pakistani Pack, Workshop 3812140001, every unit `Nation=Pakistan`):

| Roster | Picks | Price | Notes |
|---|---|---|---|
| Type 054A/P (Tughril class) `pns_type_054a_p` | Variant1–4 | 280 | F-261 to F-264; the Z-9CE lands through SEST Cross-Deck |
| PNS Alamgir (F-260), Perry long hull | Variant1 | 160 | **Kept in service for 2028 as a stated scenario assumption.** She was commissioned in 2011; her retirement date is not public |
| Z-9CE `plan_z-9ce` | Squadron1 | 20 | on the 054A/P and the Alamgir (Cross-Deck campaign fit) |
| SH-3H `pns_sh-3h` | Squadron1 | 25 | on the Alamgir's own deck list |
| JF-17 Block II / III | Squadron1, 2 | 40 / 50 | released from MK02 |
| ZDK-03 | Squadron1 | 70 | released from MK02 |

Not sold, on purpose:

- **Submarines.** The builder sells none. PNS Hangor (the Pakistani Pack's S-26P) is placed, named, in MK03 only.
- **SEST Replenishment's `plan_ffg_type_054a(_late)_rsa` Variants 37–40**, which also register Pakistan: a second copy of the Tughril class.
- **The J-10CE**, off the roster by the owner's decision: the Air Force flies it from the north.

**Missing from the collection** (stated, not stood in by another navy's hull): the Babur (MILGEM) corvette, the Zulfiquar (F-22P) frigate, the Yarmook OPV, PNS Moawin or Nasr (so there is **no supply ship**), the Agosta 90B submarine, and the P-3C, ATR 72 and Sea Sultan patrol aircraft.

**Free rearm** (*mod approximation*): with no Pakistani supply ship there is nothing to rearm the ships at sea, so every force allocation rearms them — the turn round is at Karachi between missions. The package refuses a window that sells without rearming (`makran_line/__init__.py`), and the rules page says so (`REARM_RULES`).

## 4. The commander and the awards

- `CommanderNations=Pakistan` only; the default nation is Pakistan; the game's own `[Names_Pakistan]` pool; starting rank level 7, **Commodore** (OF-6), the rank Task Force 88's first commander held (section 1).
- The ladder is the Pakistan Navy's ten commissioned ranks in their English Commonwealth form — Midshipman, Sub-Lieutenant, Lieutenant, Lieutenant Commander, Commander, Captain, Commodore, Rear Admiral, Vice Admiral, Admiral — as the English Wikipedia's "Pakistan Navy ranks and insignia" lists them (citing the Navy's own 2013 ranks page). **The abbreviations are not verified**: the Navy's official site could not be read when they were written, and they follow the Royal Navy's pattern. RIBBONS.txt says so too.
- The navy emblem is the national flag of Pakistan from the SEST gallery's flag set (public domain), written as `sest_pakn_emblem.png`. The Navy's own ensign is not in the gallery set.
- Awards are **fictional SEST ribbons only**: the Makran Line Service Ribbon (completing MK04), the Arabian Sea Security Ribbon (MK02) and the Trailing Operations Ribbon (MK03). No real Pakistani award is represented until its ribbon and criteria are sourced.

## 5. Stock trigger shapes

Every trigger is a stock piece (the builder's own checks: `check_victory_keys`, `check_required_objectives`, `check_turn_back`, `check_progress`, and the pack-wide expression checks). The combinations MK04 shares with Red Line's The Order to Withdraw have **no exact stock line**, as Red Line's test card says: two area tests in one trigger (each heave-to challenge), and AND NOT on a loss (the HoveTo path, which waits for her afloat). They are on the test card's PC checks.
