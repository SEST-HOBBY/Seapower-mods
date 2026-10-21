# SEST campaign upgrade plan: Open Allocation, side play and campaign depth

Planning document, 20 Oct 2026. I edited, built and committed nothing. The repository is at `4defe5c8` on `sest-dev/jolly-ride-rptj4t` with a clean tree. For this final pass I re-checked at that commit every fact that Section 8 depends on, using reads of the source and the built output plus read-only imports (`python3 -B`). The facts that come only from the planners' and reviewers' work are attributed to them.

**The owner's decisions of 21 Oct 2026, after this plan was written.** All three are in the pending 20 Oct update.
- **The Open Allocation twins retire now** (Q5, option b): "make open allocation redundant. will be used for other world wide campaign or dynamic sest world campaign." That drops the one released update of proof and the notice one release ahead that this plan set (§1, §3.2 item 4, A4, B12). Each campaign is listed once; `-open` saves, `NEW TEST 1.sav` among them, cannot be continued. The builder keeps the twin machinery dormant and tested as an opt-in (spec `OPEN_ALLOCATION`) for a world-wide Task Force Mode campaign; the SEST World Campaign, a Dynamic Campaign Mod campaign that `build_pack` does not build, could draw on AF's priced list. A4's retirement is done; B12 keeps A3's PLAN reserve and the optional names. SWBN, "Open Allocation retired from the pack (21 October 2026)".
- **RL03's Classify-level reveal on `RLO2EscortsNamed` is held** until the Red Line test card's 7.4 is answered: "If you don't want to play it through first, I recommend removing it now and adding it back once it's proven." RLO2 writes nothing and RL03 reads nothing; the proof is Southern Reach card 3.10 and Sulu Line card 7.1. Red Line build notes, "RL03's reveal held (21 October)".

- **Open Allocation is built into the standard campaigns** ("Build open allocation into standard campaign"). Asked from which window, the owner chose the reserve's own (recommended): "Everything goes on sale from the window where allied escorts already open: Weapons Free in Southern Watch, Tasman Crossing in Southern Reach, and Red Line's first force allocation. Earlier windows keep the story's own list, so the opening stays small and nothing the versions sold is lost. Bought aircraft still need a usable base or deck." The reserve now names the whole fleet (spec `RESERVE_FLEET`): in Southern Watch and Southern Reach the allied fleet - 52 ship classes, carriers, amphibious and replenishment ships among them, HMAS Adelaide, and 19 and 10 allied aircraft types where a row launches and recovers them - and in Red Line the PLAN's own Type 901 and 903A, which is A3's 901 and 903A done without its 052D and 055. That reverses §1's "No carriers, amphibious ships, tankers or allied aircraft". No twin comes back; HMAS Choules and the Supply-class AOR stay off sale (missions place every hull of both). SWBN, "21 October: the allied fleet in the standard campaigns".

Where this plan says the twins stay, that the reserve sells escorts only, or that RL03 reads RLO2, read it with these three decisions.

**Path shorthand:**
- Code: BP = `integration/campaign/build_pack.py`, CD = `integration/campaign/campaign_data.py`, MD = `integration/campaign/mission_depth.py`, AF = `integration/campaign/allied_fleet.py`, CCC = `tools/check_campaign_coverage.py`, TBP = `integration/campaign/test_build_pack.py`.
- Campaign packages: SR/ = `integration/campaign/southern_reach/`, RL/ = `integration/campaign/red_line/`, SL/ = `integration/campaign/sulu_line/`.
- Output: OUT = `integration/campaign/SEST_Campaign/campaigns`.
- Docs: SWB, SWBN, SWTC = the Southern Watch bible, build notes and test card under `docs/campaigns/southern-watch/`. RLB = `docs/campaigns/red-line/campaign-bible.md`. SRB = `docs/campaigns/southern-reach/campaign-bible.md`. WL = `docs/campaigns/southern-watch/workshop-listing.md`.

---

## 1. Summary

### What I propose, in order

1. **Next Steam update: Batch 1, about 2 sessions, safe for existing saves (Section 8).** No new missions, no new campaign entries, no renames. It has four parts.
   - **Open Allocation folded in.** The Open Allocation idea moves into the standard campaigns as a small, realistic **allied reserve** of escort ships:
     - Southern Watch: frigates from *Weapons Free*, destroyers from *Southern Lifeline*.
     - Southern Reach: three frigate classes from *Tasman Crossing*.
     - No carriers, amphibious ships, tankers or allied aircraft. *Superseded 21 Oct 2026: the whole allied fleet from the same windows, aircraft where a row can fly them.*
     - No ship that a mission names elsewhere is for sale.
   - **The four Open Allocation twins stay** as they are. The one exception is Sulu Line's twin, whose two defects are fixed. *Superseded 21 Oct 2026: the owner retired all four in this update (Q5, option b).*
   - **Shipped defects fixed.** These are defects the planners and reviewers found and I re-confirmed:
     - The lost O5 → SW04 reveal.
     - Red Line's briefing and order of battle show which navy its two submarines belong to, before the player has classified them.
     - Russian flags on Red Line's civilian ships.
     - Red Line's reports name officers, which its bible forbids.
     - Sulu Line's unreachable Service at Sea branch.
     - Sulu's twin selling supply ships in windows where the story does not.
     - Sulu's twin description calling its own partners "the allied fleet".
   - **New gates** that would have caught these defects.
2. **Then depth, in the order that costs players the fewest restarts:**
   1. Sulu Line first. It has never been run in game (`docs/play-test-guide.md:9`), so renumbering its missions is free now.
   2. Red Line second. It is small and only partly played.
   3. Southern Reach's dispatches. They sit outside the mission chain, so they are save-safe.
   4. Southern Reach's nine new side missions, in **one** update with one restart notice. That campaign is published and played.
3. **Side play grows through Red Line, which is the Eastern (PLAN) side of Southern Watch and Southern Reach.**
   - After Batch 1 fixes its leaks, a "mirror" helper and one Chinese-side pilot dispatch follow.
   - Russia stays in dispatches.
   - No Sulu Line red side by default.
   - ~~The twins retire only after the reserve has been proven in one released update.~~ The owner retired them on 21 Oct 2026, in Batch 1's update, without that release or the notice (Q5).

**Effort:** about 47 sessions in all, plus play time on the PC (Section 5).

### Decisions that block Batch 1

Questions Q1–Q8 in Section 6. In short:
- the batch's scope;
- which allied classes go in the reserve, and from when;
- when Southern Reach's reserve opens;
- no reserve for Red Line or Sulu Line yet;
- keep the twins (decided otherwise on 21 Oct 2026: retire them now);
- no renames yet;
- re-pick the RAN Anzacs to their MH-60R variants;
- how Sulu's Service at Sea should work.

### Where I followed the reviewers rather than the planners

Every place where the planners and reviewers disagreed, I followed the reviewers, except for the four departures listed in Part A §3.10. The main corrections:
- The design wanted reserves in Red Line and Sulu Line. Both contradict those campaigns' own written rules (`RL/tables.py:64-68`; `SL/__init__.py:96`).
- Southern Watch's last window must keep the allied escorts it sells today (OUT `sest-southern-watch/campaign.ini` [Mission40]).
- Opening the reserve at window 05 does not contain balance: that window comes just before a one-ship mission.
- The duplicate-named-hull filter is only per-campaign today. Southern Reach sells `js_ffg_mogami` Variant1 (JS Mogami) and `ko_ffg-818` Variant1, which other missions place.
- A save in progress may not see `campaign.ini` changes (`docs/packaging-and-recovery.md:776-778`).

---

## 2. Where the campaigns stand today (build-time numbers at `4defe5c8`)

| Rubric | Southern Watch | Southern Reach | Red Line | Sulu Line |
|---|---|---|---|---|
| Core / optional / contingency / dispatch | 12 / 10 / 2 / 11 | 23 / 3 / 0 / 0 | 6 / 0 / 0 / 0 | 7 / 3 / 0 / 0 |
| Spine entries (`NumberOfMissions`) | 41 | 46 | 10 | 15 |
| Dates | 18 Oct–28 Nov 2028 | 6 Dec 2028–2 Mar 2029 | 5 Nov–19 Jan; story frame 3 Nov–25 Feb | 12 Oct–23 Nov 2028 |
| Chapters | 6 | 2 | 1 (two implicit arcs) | none |
| Side ops flown by another force | 8 in the spine, plus 11 dispatches | 3 core detached ops, all Australian or RNZAF | 1 (RL05) | 3 (all three optionals) |
| Side ops flown by the player's own force (losses carry over) | 6 | 4 detachments | 0 | 0 |
| Variables declared / read | 15 / 15 | 20 / 20 | 1 / 1 | 5 / 4 (`SL04ServiceHeld` is never read) |
| Carried support losses | 5 | 2 (Derwent Spirit; Rankin via MD) | 0 | 1, reachable only in a lost run |
| Partners earned by an outcome (`IsTrue`) | 2 (Sejong, KC-46) | 0 | 0 | 0 |
| Story pages | 17 | 20 | 4 (all signals) | 5 |
| Neutral units / missions that have them | 49 / 19 of 24 | 110 / 26 of 26 | 21 / 6 of 6 | 29 / 10 of 10 |
| Role gaps | few | interdiction, covert, night start, air defence | SAR, defence against an air raid | ASW, SAR, air defence, covert |
| Max completion points / start / cap | 2,210 / 1,000 / 1,500 | 2,980 / 1,000 / 1,500 | 560 / 1,000 / 1,500 | 890 / 1,000 / 1,600 |
| Buy windows / rearm | 7 / free at 7, plus 1 conditional | 14 / 13 free, plus 2 conditional | 4 / free at 4 of 5 | 4 / SL01 only |
| Roster lines: standard / twin | 13 / 84 | 13 / 75 | 9 / 11 | 12 / 12 (identical) |
| Own docs | bible, build notes, test card | the same, plus AUTHORING | bible, build notes, test card | test card only |
| Played in game | partly | partly; published | loaded, partly played | never |

**Sources for the table:**
- Group counts and variables: my import of `campaign_specs()`, which runs `mission_depth.apply()` (BP:501-502).
- Spine entries: `OUT/*/campaign.ini:68`.
- Roster lines: counted from `OUT/*/player_task_force_roster.ini` and the `-open` copies.
- Southern Watch and Southern Reach rosters are 13 rather than 10 because `expand_roster` adds three allied escorts (MD:206-234).
- Play status: `docs/play-test-guide.md:9-10`.
- All other rows: the four inventories, with the reviewers' corrections. The entry counts are 41/46/10/15, not 42/47/11/16, and Southern Watch has 15 variables at build time, not 11.

---

## 3. Part A: Open Allocation folded into the standard campaigns, and red-side / blue-side play

### 3.1 What the request means here

- **Open Allocation.** The owner's stated want was "the allied fleet - US, UK, NATO and Pacific allies - costed and in the Unit Catalog, not only the campaign's own roster sooner" (SWBN:1404-1406). Folding it in means that the fleet goes on sale inside the standard campaign entry.
- **Red side / blue side.** The player is always Taskforce1 (BP:4279-4281). A red side puts the PLAN in Taskforce1 and the coalition in Taskforce2, as Red Line already does (`RL/rl01_trailing_contact.py:34`).
- **"Modernised Warsaw vs NATO".** Realistically this is a US-led coalition against a China-led side, with Russia alongside but not under China's command. ASSUMPTION: no Eastern treaty bloc exists in 2028. Red Line's canon already keeps Russia "under its own arrangement" (RLB:34).
- **"All campaigns".** I read this as the four shipped campaigns, not new theatres. That is Q14.

### 3.2 Recommended design (Design 3, corrected by the reviewer)

1. **One curated allied reserve, inside a standard campaign only where it is realistic.** This means Southern Watch now and Southern Reach in limited form. The campaign's own navy stays released by the story.
2. **Escort ships only, no aircraft, in the first version.** This is realistic: allied air assets stay under their own national command, and SRB:101 says allied aircraft "never join the owned roster". It also avoids the builder-ordering problem with `usable_allied()` and `widen_flights` that the reviewer found (BP:7541-7552, BP:7648-7650).
3. **No duplicate named hulls anywhere in the pack.** A reserve variant that any campaign mission places, on any side, is not for sale. Dispatches are excluded from this check.
4. **The twins stay unchanged for now**, except for the Sulu fixes. They remain the "everything from the first window" option. They retire only after the reserve has been proven in game. *Superseded 21 Oct 2026: retired with Batch 1, before the reserve is proven (Q5, option b).*
5. **Sides are separate campaign entries.** The game allows one roster, one commander, one rules page and one Situation order of battle per entry (engine research §1, hard constraint 3), and the builder writes no forks (BP:6653-6700).
   - Red Line is the Eastern side of Southern Watch (RL01–RL04) and Southern Reach (RL05–RL06).
   - The player stays Taskforce1 in every mission.
   - No `persistentEquals` forks.
6. **No new engine keys.** Every key used is already written by the builder.

**Rejected:**
- **Design 1, a choice of side inside each campaign.** It would roughly double the entries (to about 84 for Southern Watch) using untested patterns, and leave about 40 dead entries on the map.
- **Design 2, the whole bloc at every window.** It loses the story's staging and would sell a Ford at SW01.

### 3.3 Campaign list structure

| Stage | Entries | Names |
|---|---|---|
| Next update (Batch 1) | 8: four standard, four `-open` twins. Every folder path is unchanged, so no save is stranded. *Superseded 21 Oct 2026: 4 standard entries, the twins retired; `-open` saves are stranded* | Unchanged (`OUT/*/campaign.ini:64`, e.g. "Southern Watch (Royal Australian Navy)"). The bracketed navy already says which side the player is on. A bloc tag waits for Q6 |
| After the reserve is proven (B12) | ~~4 standard entries; twins retired~~ Done with Batch 1 (21 Oct 2026) | Optional side tag before the bracket, e.g. "Red Line - The Other Watch - Eastern side (People's Liberation Army Navy)", if Q6 says so |

### 3.4 Mechanism

| Piece | Today | Batch 1 |
|---|---|---|
| Which allied ships are sold in the standard campaign | Hard-coded set `{rn_ff_type23, js_ffg_mogami, ko_ffg-818}` in Southern Watch and Southern Reach. It opens at every buy window except Southern Watch's 01–03 (MD:206-234) | A spec key `RESERVE`: a list of `dict(unit=, opens=<mission code>)`. Its windows are keyed by mission code, because Southern Reach repeats window numbers across its two chapters (reviewer A16) |
| Variants on sale | MD drops variants placed by blue units in the same campaign only (MD:216-218) | Drops every variant placed by any campaign mission of the pack, on any side. This removes Mogami Variant1 and Daegu Variant1 from Southern Reach's sale. Both are checked today (my scan of the specs: JS Mogami SW10 blue / RL03 red; Daegu SW O3 blue) |
| Window text | MD appends a fixed sentence (MD:233) | A generated sentence naming the classes on sale at that window |
| Rules page | No mention of allied ships (0 matches in `OUT/sest-southern-watch/campaign_rules_en.xml`) | One line: which classes, from which window, at their own navy's price. Allied aircraft and carriers are not sold. The game's own "Unrestricted mode" sells everything (`mods-source/_vanilla/original/language_en/ui.ini:3498-3499`) |
| Allowlists | Explicit in every window | Still explicit. The stock roster file says the builder "check[s] this file first ... then filter[s] further down if the mission has an allowlist" (`mods-source/_vanilla/original/campaigns/pacific-strike-task-force/player_task_force_roster.ini:2`) |
| Commander and discount | One nation (CD:471-484) | Unchanged. Allied ships pay list price. `FOR_NATION` stays keyed by the commander's nation (AF:260) |
| Twin roster | `ROSTER + allied` (BP:7651) | Unchanged in structure. Twin picks shrink slightly with the pack-wide filter, which is probably harmless: a save keeps what it bought (SWBN:2638-2640) |
| Twin "allied fleet" sentence | Counts every non-commander unit on the twin roster (BP:370-382, called with `twin_roster` at BP:7658). That is why Sulu's twin claims "5 classes from Thailand, Australia and USA" (`OUT/sest-sulu-line-open/campaign.ini:65`) | Built from the allied entries only. CCC derives it from the twin's rows that are not in the base roster (CCC:438-441). No reserve sentence goes into the base Description, which avoids the double count the reviewer found |
| Twin gating | Every open window sells the whole roster (BP:385-429). Sulu's twin therefore sells the C8 at SL01 and every supply ship at SL02 (checked: `OUT/sest-sulu-line-open/campaign.ini` [Mission2], [Mission5]) | New spec key `OPEN_HOLD`: units the twin sells only where the story's own allowlist sells them. Sulu sets it to its supply ships (`SL/tables.py:124`). This fixes the C8 at SL01 too |

### 3.5 Red and blue availability per campaign

| Campaign | Blue (coalition player) | Red (PLAN player) | Notes |
|---|---|---|---|
| Southern Watch | Standard entry plus twin | Red Line RL01–RL04 (and its later northern additions). D4 *Return Passage* is the Russian view (CD:2949) | Canon: the coalition campaigns are canon, and red wins by restraint (`RL/__init__.py:16-26`) |
| Southern Reach | Standard entry plus twin | Red Line RL05–RL06, plus the planned southern chapter | |
| Red Line | — | Standard entry plus twin | Never sells Russian or Pakistani hulls to a PLAN commander (realism, RLB:34) |
| Sulu Line | Standard entry plus twin | None by default. At most the SLD6 dispatch (PLAN view, labelled non-canon) | No purpose-built China Coast Guard hull; Sulu uses the stock Qiongsha as a stand-in (`SL/sl03_ayungin.py:4,106-108`). It is also a live real dispute (Q11) |

### 3.6 Force rosters per bloc, and gaps

**Western: the recommended Southern Watch reserve (11 classes, prices from AF).**

- **Frigate tier, from *Weapons Free* (window 05):**
  - UK: Type 23 (260), River Batch 2 (80; the UK's real permanent Indo-Pacific presence).
  - Japan: Mogami (300), Asahi (360).
  - South Korea: Daegu (280), Chungnam (300).
  - France: La Fayette modernised (200), Aquitaine (360).
  - Every one costs less than Hobart's 480, so the one-ship mission (`max_units=1`, CD:5303-5311) is not won with a bought destroyer.
- **Destroyer tier, from *Southern Lifeline* (window 09):** Type 45 (460), Burke Flight IIA (480), Burke Flight III (520).
- **Window 12** keeps everything. It sells allied escorts today.
- **Left out, and why:**
  - Carriers, LHDs, LPDs and replenishment ships: Southern Watch's own rule makes them scripted theatre assets (CD:5238-5242, a comment that also needs correcting), and a bought deck has no air group (AF:3-4).
  - Zumwalt, Maya and Atago (Japan's ballistic-missile-defence ships stay home), and Sejong and Jeongjo (Sejong is the earned O3 partner).
  - All allied aircraft.
  - European navies other than the UK and France (Q2).
- **Realism basis:** "limited US/Japanese/French support ... a small number of escorts" (SWB:18, :24).

**Western gaps (engine research §4):** no Queen Elizabeth carrier, no Type 26 or Type 31, no UK-registered F-35B, no Izumo, Kongo or P-1, no Korean fighter or replenishment ship, no RNZN warship, no Taiwanese ships. The allied fleet has no Australian escort (AF:231-239), so the design's "Australian escorts for Sulu" default does not exist (reviewer A6).

**Eastern:**
- **PLAN: deep.** Type 055, 052D, 052C, 054A/B, 056A, two carriers, Type 071, Y-9/KQ-100, KJ-500/600, J-15/16/35, Z-9/18/20. Source: the engine inventory at `/tmp/claude-0/-home-user-Seapower-mods/cb2a533c-0bb4-50d5-9069-2002ad35f1f1/scratchpad/inv.json`.
- **Priced for a reserve:** only `PLAN_SUPPORT`, the Type 901 and 903A (AF:251-258). The escort tier has no prices anywhere (reviewer A5).
- **Gaps:** no Type 075, no purpose-built China Coast Guard hull, and no Chinese research ship (Nan Hai 27 is the Soviet-registered `wp_agi_okean`).
- **Russia:** broad surface and air, but logistics is one Pashin and ASW helicopters are only the Ka-27 family. The Tu-160 cannot be sold (no nation in its file). Every modern file registers `Soviet`, so a bought hull would fly the USSR flag (ASSUMPTION).
- **Iran and North Korea:** no modern navy.
- **Pakistan:** the best modern partner in the collection, but unrealistic in either theatre.

### 3.7 Builder changes

- **Batch 1:** see Section 8.2.
- **Later (A2, A3, A4 in §3.8):**
  - the remaining red-side presentation work: `threat_profile` scoped to spared or weapons-Hold red units (BP:6089-6099), and the pack-wide neutral flag rule in `integration/common/flags.py:27`;
  - a `mirror()` helper for flipping a mission's sides;
  - a priced PLAN escort tier, with a bible change to `RL/tables.py:64-68`;
  - side tags in names if chosen;
  - ~~retiring the twins (CCC:541-542 and :612, the TBP `OpenAllocation` tests, `docs/play-test-guide.md:42`, `integration/campaign/setup/sest-setup.ps1:309`).~~ Done 21 Oct 2026, with Batch 1: no spec opts in to a twin (`OPEN_ALLOCATION`), the gate checks one only for a spec that does, and the TBP tests build one in a temporary folder.

### 3.8 Phasing

| Step | Content | Sessions |
|---|---|---|
| A1 (in Batch 1) | Reserve, filter, rules line, twin hold, twin sentence fix, Red Line `recognise`/`orbat` and label keys | about 1.1 |
| A2 (B5) | `threat_profile` scoped to spare/Hold; neutral flags pack-wide; `mirror()` plus a pilot: *Bomber Stream* (O8) flown from the Chinese side as "Red Line - Dispatches" (key exists, `RL/__init__.py:116`; `DISPATCH_DESC` is empty at :126) | about 3 |
| A3 | Red Line reserve: 901 and 903A everywhere they make sense, 052D and 055 after pricing, with RLT and RLB changes (Q5) | about 1 |
| A4 (B12) | ~~Retire the twins, with a notice one release ahead~~ (done 21 Oct 2026, with Batch 1 and no notice: the owner's Q5); side tags in names if Q6 says so | 0.5–1 |
| A5 (conditional) | Sulu red-side dispatch | 1 |

### 3.9 Risks

1. **Saves.** A `campaign.ini` change may not reach a campaign already under way (`docs/packaging-and-recovery.md:776-778`). The reserve will probably show only in a new campaign, so the change log must say so.
2. **The game reading long allowlists.** The 13 Oct report suggests it does (SWBN:2627-2634), but test-card rows G.7 and G.8 are unrecorded (SWTC:339-340).
3. **The Unit Catalog lists the whole roster file** (G.7). From SW01 it will show reserve classes the player cannot yet buy. The rules line explains this.
4. **The default changes for every subscriber.** The allied escorts were opt-in through the twins, and MD's three escorts have not yet been uploaded (merged in `71bd3004` on 20 Oct, after the last upload `c948bc9a`, `docs/workshop-refresh-20261015-review.md:95`).
5. **Required mods grow** for the standard Southern Watch and Southern Reach. Every reserve mod is already in the collection, because the twins use them.
6. **Avoided entirely:** the player as Taskforce2, and `persistentEquals` forks.

### 3.10 Where I departed from the reviewer, and why

1. **Southern Reach timing.** The reviewer said leave MD's three escorts at every window and ask whether to drop them. I recommend opening them from *Tasman Crossing* (TS04), the first window after the Tasman chapter's first authorised kill (TS03, SRB:282). This follows the owner's realism rule that allies arrive once there is a war, and SRB:101's ownership rule.
2. **A destroyer tier from window 09.** This answers the reviewer's own balance objection about window 05.
3. **Ships only.** This removes the reviewer's ordering and `widen_flights` costs.
4. **No reserve sentence in the base Description.** This removes the reviewer's double-count problem.

---

## 4. Part B: bringing Southern Reach, Red Line and Sulu Line to Southern Watch's depth

### 4.0 Corrections that apply to all three plans (from the depth review)

| # | Correction |
|---|---|
| X1 | Southern Watch's baseline is **15 variables, all read**, not 11 (my audit). The four extra are SW08's strike outcomes |
| X2 | Collins Variant3 (HMAS Waller) is the only Collins hull nobody places (`mods-source/3820759806/language_en/vessel_names.ini:112-117`). Red Line's ALPHA moves to it. Variant6 is now Rankin (MD:112-113). If Southern Reach's SR11A survives, Waller is shared safely, because ALPHA's last appearance (22 Nov) comes before SR11A. RLB:28 is rewritten to "no hull a coalition mission can own or lose before her last Red Line appearance" |
| X3 | Red Line's rule is that it flies no day **Southern Watch or Southern Reach** flies (RLB:72). Move SR05A to 20 Dec and SR11A to 11 Jan. Overlaps with Sulu Line are allowed: Southern Watch and Sulu already share six days |
| X4 | "Nan Hai 31" is used for two different hulls. Rename one |
| X5 | The hard-coded total in `integration/campaign/test_playtest_revision.py:245` (77) should be derived from the specs. Merge order matters, because all three plans edit MD and BP |
| X6 | REALISM: Euromod RAN's Anzac Variants 1–3, 5, 6 and 8 are S-70B-2 fits that ended in 2016 (`mods-source/3820759806/vessels/ran_ffh_anzac_variants.ini:15-105`). The MH-60R hulls are Variants 4, 7 and 9–14 (`…/language_en/vessel_names.ini:63-76`). Southern Watch and Sulu Line sell 3 and 8 (CD:438; `SL/tables.py:108`); Southern Reach sells 2, 3, 5, 6, 7 and 8 (`SR/tables.py:97-102`). Q7 |

### 4.1 Southern Reach / Tasman Shield

**Targets (corrected).**

| Group | Now | Target | Why |
|---|---|---|---|
| Core | 23 | 23 | Already nearly twice Southern Watch's 12 |
| Optional | 3 | **10 (+7)** | Two side windows in each of the five two-week blocks that have none. SR11A is dropped: the reviewer found it thin, and it names ships it never shows (Q15) |
| Contingency | 0 | 2 | |
| Dispatch | 0 | 8 | Plumbing exists (`SR/__init__.py:144,154`) |
| Variables | 20 | 30 | |
| Story pages | 20 | 28 | |
| Spine entries | 46 | 63 | 9 missions and 8 pages added |
| Points | 2,980 | 3,410 | Cap unchanged at 1,500; needs a balance pass |

**Spine side missions (9).**

| Code | Date | Title | Flown by | Premise | Writes → read by | Fix from the review |
|---|---|---|---|---|---|---|
| SR02A | 10 Dec 21:40 | Compliance Corridor | Player detachment, Bluefin 31 | Get alongside an AMS bunker tanker before the "fisheries" 054A reaches her. Southern Reach's first `denied` race and first dusk start | SR02ACorridorClosed → SR06: 054A and Z-9 absent | Reader effect is weak (11 days later); accept, or find a nearer reader |
| SR03A | 13 Dec | Astrolabe | France: FS Courbet, Panther, L'Astrolabe stand-in, Atlantique 2 | France escorts its own Antarctic ship; Canberra gets only the picture | SR03AFrenchPicture → SR05: 15-minute datum. SR03AFrigateLost → TS10A: Courbet absent | **Blocking:** Courbet is a neutral in TS10A, and every neutral feeds the fatal "Neutral harmed" trigger (BP:4382-4383, 5180-5196). The builder must leave `spawn_if` units out of the neutral set (with a test) and score her as a non-fatal `spare`. The Atlantique range check passes (`mods-source/3567256221/aircraft/fr_atl2.ini:76`) |
| SR05A | **20 Dec** (moved) | Bear Watch | RAAF F-35A pair, Wedgetail 04 | Intercept and escort two Bears and a Midas under the rules of engagement | SR05ABearsEscorted → SR07: Bear-F and Midas absent | Drop the KC-30A; stay inside unrefuelled radius from East Sale; reword `SR/lore.py:218-230` and `SR/sr12_turning_north.py:5,22,36` ("first fighter cover for the task group"). Alternative: a Wedgetail and P-8 shadow with no fighters |
| SR06C | 22 Dec | Raft Line (contingency) | Player detachment | Race the Russian tender to two crew from Derwent Spirit | SR06CCrewRecovered → SR07: 10-minute datum on VICTOR | Raft moved to about −51.4, 165.6, 20–40 NM east of SR06's track (`SR/sr06_broken_supply_line.py:24-25,35`); recheck with `coast.check()`. Win by ship only: slot aircraft cannot be named in triggers (BP:5208-5235) |
| SR09A | 4 Jan | Stalwart's Rendezvous | Player detachment, HMAS Stalwart | Hold a 25-minute service window | SR09AStalwartHeld → SR10: rearm | Rendezvous moved to about −55, 128 on the SR09→SR10 track. The planned 52S 145E needs 20.6 kn sustained at sea state 6 |
| TS02C | 26 Jan | Southerly (contingency) | Player detachment, Kiwi 05 | A disabled ferry in a southerly, with TANGO about | TS02CFerryHeld → TS03: Kiwi 06 joins (`IsTrue`) | Repeats TS02's water; low risk. `IsTrue` is unproven |
| TS04A | 2 Feb | Norfolk Watch | UK: HMS Spey, Kiwi 06 | Evidence on an AMS supply ship off Norfolk Island | TS04AReeferNamed → TS05: 054A and Z-9 absent | Kingston anchorage is 1.06 NM off: `coastal=True` |
| TS06A | 9 Feb 23:30 | Rotation West | USA: Virginia (Submarine Rotational Force-West) | Trail SIERRA-TWO unseen | TS06AYasenTrailed → TS08: Yasen classified | Southern Reach's first night start |
| TS08A | 17 Feb | Shirase | Japan: JS Maya, Shirase stand-in | Escort the icebreaker home | TS08AShiraseThrough → TS11: JS Maya joins (`IsTrue`) | Q15 (Maya or Mogami) |

**Changed core missions:** SR05, SR06, SR07, SR10, SR12 (only if SR11A is kept), TS03, TS05, TS08, TS10A and TS11, as readers. The SR plan §2.2 has the details.

**Dispatches (8).** Browser only; outside the spine; save-safe.

| Code | Date | Player side | Premise | Fix from the review |
|---|---|---|---|---|
| SRD1 | 3 Dec 2028 | Japan | Shirase's outbound leg from Fremantle | Kumano (Mogami Variant2) stays on sale, because the filter excludes dispatches |
| SRD2 | 30 Dec 2028 | USA | A Deep Freeze escort, with a `lift` on the 054A's fire-control lock | — |
| SRD3 | 7 Dec 2028 | Russia | VICTOR's covert transit; SR02 seen from the other side | — |
| SRD4 | Nov 1984 | New Zealand | Cold War exercise | `ran_ffg_adelaide`'s only variant is **HMAS Darwin** (`mods-source/3455404959/language_en/vessel_names.ini:149`) |
| SRD5 | 18 Feb 2029 | Chile | Ex-RAN Adelaides on passage to Sydney | Rewrite the `euromod-chile` excuse (CD:274-277) |
| SRD6 | 2034, labelled fictional | Australia | Sea-control Canberra | Fujian is `plan_cv_type_003` (`RL/rl01_trailing_contact.py:131`), not `plan_cv_fujian` |
| SRD7 | Jun 2029 | Australia | Sinking exercise against the hulk "ex-HMAS Anzac" | Mogami Variant14 is *Mackay*; the first Australian hull is Variant11 *Wollongong* (`mods-source/3456859157/language_en/vessel_names.ini:27-30`). Q20 |
| SRD8 | after 22 Jan (moved) | New Zealand | No. 5 Squadron's ASW barrier | On 18 Jan its opposition cannot reach RL06's Fiordland start the next morning (`RL/rl06_the_quiet_side.py:41,125-132`); move the date or change the opposition. P-8s fly from Ohakea |

**Narrative.**
- Eight pages: `00d` before SR03, `01d` before SR03A, `05c` before TS02, `06b` before TS05, `06c` before TS06, `06d` before TS07, `06e` before TS08, `07a` before TS08A.
- Pages hung before optionals become main-chain entries that every player sees (BP:6893-6900), so `01d` and `07a` report only the request.
- New cast: the French attaché, Spey's CO, the Submarine Rotational Force-West liaison, the JMSDF liaison, the RCC duty officers, Stalwart's master. No Chinese person is named.

**Builder and data.**
- `SR/tables.py`: 17 MODULES entries and 17 CALENDAR rows.
- `SR/__init__.py` audits: writer dated before reader; every declared variable read; `expires_after` names a later core mission; an `IsTrue` unit is never in a victory, fatal or `denied` term; dispatches carry no variables.
- 17 MD REPORTS entries.
- BP: SERVICE labels for France, Japan, the UK, the USA, Chile, New Zealand and Russia; **conditional neutrals left out of the neutral-loss trigger**.
- AUTHORING updates (`IsTrue`, timed datum, `enter=`, `denied`, the Seahawk cockpit at `SR/AUTHORING.md:234-235,334`).

**Phasing.**

| Step | Content | Sessions | Save impact |
|---|---|---|---|
| SR-0 | Groundwork and documentation drift | 1 | none |
| SR-D1 | SRD2, SRD3, SRD7, SRD8 | 1.5 | none |
| SR-AB | All 9 spine missions and 8 pages in **one** update | 8 | one restart notice |
| SR-D2 | SRD1, SRD4, SRD5, SRD6 | 2 | none |
| Proof | In-game proof run | 1 | — |

About 13.5 sessions in all.

**Risks:**
- `IsTrue` and `rearm_if` are unproven in game: run Southern Watch test 6.7 (Sejong) first.
- `unseen` and the timed datum are new to Southern Reach.
- The campaign is published and has been played, so SR-AB forces a restart (`docs/campaigns/southern-reach/build-notes.md:455-458`). WL:57 "Twenty-six missions" must change in the same update.
- New coastlines are proved only against Natural Earth.
- Gallery photos are missing for `ran_lhd-cv_canberra_late`, `ran_f-35b`, `wp_ssn_victor3` and `wp_tu-95rt`.

### 4.2 Red Line

**Targets.** 12 core / 10 optional / 2 contingency / 5 dispatches. That is 24 campaign missions plus 17 pages, giving 41 entries (Southern Watch's shape). 13 variables with 15 links. 7 buy windows. About 2,130 points.

**Existing missions.**

| Code | Batch 1 (Section 8) | Later |
|---|---|---|
| RL01 | ALPHA Variant6 → Variant3 (`RL/rl01_trailing_contact.py:137`); `recognise=False, orbat=False`; explicit nations on the ferry and trawler (built as Russia at `OUT/sest-red-line/missions/Red Line 01 - Trailing Contact.ini:87,114`); report rewritten (MD:74) | Coast geography after moving the 2.40N waypoint |
| RL02 | GOLF `recognise=False, orbat=False`. Today the briefing shows "Virginia-class (2027)", and `OUT/sest-red-line/enemy_theater_roster.ini:21-24` files her under USN. Report rewritten (MD:75 says "ceasefire" on 12 Nov) | Reads RLO1 (900-second datum); one ship |
| RL03 | Spared units labelled "do not engage" (BP:5746); report (MD:76 names LI) | Reads RLO2 (built with RL-1; held 21 Oct 2026 until Red Line test card 7.4 is answered); support loss on Dragon Eye 05; one ship |
| RL04 | Report (MD:77 names CHEN) | GOLF can also be sunk in RL08 |
| RL05 | Nation on the cruise ship (built :67); report (MD:78 "snorkel" on a nuclear 093B) | Reads RLO6 as a **datum on HOTEL**. The Triton stays a fatal spare: the plan's removal broke RLB:27 (reviewer C4). Points 80 → 100 |
| RL06 | Nation on the cruise ship (built :84); report (MD:79) | Reads RLO8 and RLC2; one ship; points 0 → 160 |

**New missions (18).** All dates fall on days Southern Watch and Southern Reach do not fly, after the X3 moves.

| Code | Date | Title | Group / flown by | Premise | Writes → read by | Fix from the review |
|---|---|---|---|---|---|---|
| RLO3 | 7 Nov | Bahodopi Roads | optional, detachment | Meridian "inspects" a Chinese ore carrier off Morowali | RLO3MeridianStruck → RL07, RLO5 | Hold Fire and Restraint as separate objectives (`lift`) |
| RL07 | 8 Nov | Weda Bay | core, one ship | The evacuation half of the mandate | — | The jetty stage must use `at_unit` or a box at least 1 NM off (BP:993-1000) |
| RLO1 | 11 Nov | Datum | optional, Y-9 | Put a class on GOLF and fire nothing | RLO1GolfDatum → RL02 | Checked clean against the canon timeline |
| RLO2 | 18 Nov | The Ships from the North | optional, Y-9 and J-15 | Name the Japanese escorts | RLO2EscortsNamed → RL03 (held, owner, 21 Oct 2026) | ASSUMPTION: a reveal satisfies classify. Unproven, so RL03's reveal is held until test card 7.4 is answered |
| RLO4 | 18 Nov | Not Under Your Command | optional, detachment | A fire aboard the northern element's transport | RLO4ElementEscorted → RL08 (`IsTrue`) | — |
| RL08 | 22 Nov | Nineteen Days | core, whole force | Replenishment with two submarines in the picture | RL02GolfSunk (second writer) | Hulunhu's route must end inside the stage box (BP:4674-4680) |
| RLC1 | 24 Nov | Pilot in the Water | contingency, detachment | Race an RAN OPV to a downed J-15 pilot | — | `hold_minutes` needs a `held` message (BP:4775-4778) |
| RLO5 | 30 Nov | The Tow | optional | A false-flag attempt on a damaged 054A | — | Writes nothing (padding) |
| RL09 | 19 Dec | Normal Mode | core | Lombok passage | — | Its Anzac must be a hull no roster sells (see the note under this table); needs a Java coast extract |
| RLO6 | 23 Dec | Intercept | optional, J-15 and Ka-31 | Identify the P-8 professionally | RLO6InterceptClean → RL05 HOTEL datum | Reward changed (above) |
| RLO7 | 29 Dec | Taihu | optional, detachment | Replenish at sea state 5 | RLO7TaihuMet → RL10 rearm | — |
| RL10 | 8 Jan | Fire in the Ice | core | Rescue at the ice edge | RL10AllFound → RL11 | Role `patrol`: the only coalition unit is an unarmed Triton (reach gate BP:2608-2617). Record the 052D at the ice edge in both bibles (SRB:106) |
| RLC2 | 12 Jan | Port Ross | contingency | A storm-damaged 056A shelters | RLC2CorvetteSheltered → RL06 | The second decoy gets its own station |
| RLO8 | **18 Jan** (moved from 13) | Collector | optional, Nan Hai 27 | Record Kiwi 05's pattern | RLO8PatternsRecorded → RL06 | On 13 Jan she could not reach SR12 (31.5 kn needed) |
| RLO9 | 3 Feb | Survey | optional | Hull 419's last appearance | — | Writes nothing |
| RLO10 | 10 Feb | Last Fuel | optional, detachment | The last full replenishment | RLO10ServiceHeld → RL11 rearm | — |
| RL11 | 20 Feb | Fewer Ships | core | Recover survivors after Portland | RL11SurvivorsAboard → RL12 | Set the variable on the victory: with a hold, a stage's `sets` fires on arrival (BP:4716-4718) |
| RL12 | 24 Feb | The Closure | core, final | Hold the line; let a test merchant pass | — | Remove Nan Hai 27: she is in the Hauraki Gulf on 22 Feb (`SR/ts10a_northern_priority.py:16,130`) |

**Note on the Anzac for RL09, RL11 and RL12.** After the X6 re-pick, the only unsold MH-60R Anzacs are Stuart (crippled in Southern Watch's C2) and the decommissioned Anzac herself. Withhold one hull, for example Variant13 Ballarat, from Southern Reach's roster when RL09 is built.

**Dispatches.** RLD1–RLD5 as planned. Drop RLD6, a recent real event (Q20). RLD1 and RLD2 would be the first real ship names in Red Line. RLD3's `plan_dd_luda1` has no gallery photo.

**Narrative.**
- 13 new pages in signal, log and INTSUM form, using the existing labels (`make_art.py:353-357,400-417,826-829`).
- No press pages: that would mean impersonating real Chinese state outlets.
- The cast are roles, never names (RLB:35).

**Economy.** No free rearm except at home port (RL09) or from replenishment (`rearm_if` RL10 and RL11), as the tasking says (`RL/lore.py:35-36`). RL02, RL03, RL06 and RL07 become one-ship missions.

**Phasing.**

| Step | Content | Sessions |
|---|---|---|
| RL-1 | RLO1, RLO2, RLC1, the RL02/RL03 readers (RL03's held on 21 Oct 2026) and 4 pages (the fixes move to Batch 1). *Built with Batch 1, owner's Q1, 20 Oct 2026* | 2 |
| RL-2 | RL07, RL08, RLO3, RLO4, RLO5, economy restage | 4.5 |
| RL-3 | Java extract, RL09, RLO6, RLO7 | 3 |
| RL-4 | RL10, RLC2, RLO8 | 3 |
| RL-5 | RL11, RL12, RLO9, RLO10 | 3.5 |
| RL-6 | Dispatches | 2.5 |

About 18.5 sessions in all.

**Risks:**
- `unseen` is untested; RL05, RL06 and RL09 depend on it.
- How the AI behaves at weapons Hold and Tight.
- In-mission supply from Hulunhu and Taihu.
- Red Line has been partly played (`docs/play-test-guide.md:9-10`), so each spine batch needs a restart notice.
- Hull 334 and Hull 419 must not appear after 28 Jan and 4 Feb.

### 4.3 Sulu Line

**Targets.** 12 core / 10 optional / 2 contingency / 8 dispatches. 41 entries. 14 variables with 17 links. 7 buy windows, with 3 supply sales as now (`SL/tables.py:121-124`). About 2,010 points.

**Renumbering.** Renumber to chronological codes now, while nothing has been played. The plan's order holds: SL05A→SL08A before SL03A→SL05A.

**New and changed missions.**

| New code (old) | Date | Title | Group / flown by | Writes → read by | Fix from the review |
|---|---|---|---|---|---|
| SL02 (new) | 16 Oct | Cagayancillo | core, whole force | SLTenderSunk → SL06 | Relabel the stations in Service at Sea "out of Cagayancillo"; they are 120–130 NM from the island (`SL/sl04_service_at_sea.py:104-110`) |
| SL02A | 17 Oct | Gateway | optional, RAAF P-8 | SLGatewayContact → SL11 (`IsTrue`) | Field: Puerto Princesa (Butterworth is outside the coast box) |
| SL03A | 21 Oct | The Lamitan Coaster | optional, **player detachment** | SLCoasterStopped → SL07 | — |
| SL04 (new) | 23 Oct night | The Zamboanga Crossing | core | SLCrossingLeaderNamed → SLC2 | Crossing start `coastal=True`; move the landing box off the 0.5 NM waypoint margin (BP:952-959) |
| SL04A | 24 Oct | Dustoff | optional, PN H-76s | SLDustoffFlown → SL07 | The landing-zone hold uses `at_unit` on a land marker (the point is on land) |
| SLC1 | 28 Oct | Recto Bank | contingency, player detachment | SLRectoCrewSaved → SL11 | — |
| SL06 (SL04) | 2 Nov | Service at Sea | core | SLProviderLost → **SL10 Aborlan** (the existing reader, `SL/sl06_the_aborlan_battery.py:102-106`) | The charter is no longer fatal (Batch 1). Sulu Provider **stays at Aborlan** and does **not** reappear at Honda Bay. Aborlan is a supply sale anyway (`SL/sl06…:137`); the plan contradicted itself (reviewer D1) |
| SL06A | 4 Nov | Malampaya | optional, one player ship | — | Platform position is an ASSUMPTION |
| SL07 (new) | 6 Nov | Siasi | core | — | Pier box at least 1 NM off; the UAV recovery point moves onto land |
| SL07A | 8 Nov night | The Floating Armoury | optional | SLArmouryNamed → SL08 | `unseen` without a time window (BP:4914-4923) |
| SLC2 | 11 Nov | Tug and Barge | contingency | reads SLCrossingLeaderNamed | — |
| SL09 (new) | 14 Nov dusk | Honda Bay | core: air defence | SLLanderSunk → SL10 | No Sulu Provider here |
| SL10A | 17 Nov | Tabak Down | optional, Thai S-70B | — | Drop the `CSARPointModifier` claim: authored rafts do not trigger it |
| SL11 (new) | **21 Nov** (moved from 20) | The Listening Strait | core: ASW under restraint | SLSubTracked → SL12 | SL12's "two days ago" line (`SL/sl07_balabac_strait.py:47-48`) becomes "tracked through the strait two days ago" |
| SL11A | **22 Nov** (moved from 21) | The Dangerous Ground | optional, USN P-8 | SLGroupPictured → SL12 | — |

**Other changes:**
- Meridian Tender 9 should not combine `spawn_if` with `enter=22`; that pairing is unproven. Place her at the start, at a distance.
- The plan's rule that "a `spawn_if` unit may not appear in any trigger" is too broad. It applies only to mission-ending triggers (`SL/sl06…:100-101`).

**Dispatches.**
- SLD1–SLD8 as planned.
- SLD2 needs a Spratly extract (`tools/make_coast_extract.py:20-21`).
- SLD3: fictionalise the opposing group (Q20).
- SLD6 is the PLAN view, labelled non-canon (Q11).
- SLD8 needs `coastal=True`.

**Narrative.**
- 12 pages and an invented cast.
- SANTOS becomes MANALO in Batch 1 (MD:80,86,89), because Southern Watch already has Master Leila Santos (SWB:128).

**Rearm.** Batch 1 removes the dead `SL04ServiceHeld` (Q8). Later batches add no `rearm_if`. The rearm is the physical transfer alongside the charter or a bought supply ship (`SL/__init__.py:15-19`).

**Phasing.**

| Step | Content | Sessions |
|---|---|---|
| SL-0 | In Batch 1 | — |
| SL-1 | Renumbering, 5 cores, rows and windows, 6 pages, bible v1 | 3.5 (the reviewer found 3 optimistic) |
| SL-2 | SL02A, SL03A, SL04A, SLC1, SL06A | 2 |
| SL-3 | SL07A, SLC2, SL10A, SL11A | 1.5 |
| SL-4 | Dispatches | 2 |

About 9 sessions in all.

**Risks:**
- Nothing in Sulu has been run in game.
- Whether supply-ship pools persist between missions (`docs/campaigns/sulu-line/test-card.md:43-47`).
- The AI ignoring weapons Hold.
- Coast geography for Basilan, Siasi and Jolo.

---

## 5. Combined roadmap

| Batch | Contents | Sessions | Depends on | Ships to the PC | Save impact |
|---|---|---|---|---|---|
| **B1: next update** | Section 8 | 2 | — | The reserve, the fixes, the gates | None. The reserve may show only in a new campaign |
| B2 | Sulu SL-1 | 3.5 | B1 (variable gate, charter fix) | Sulu at 12 core, 6 pages, bible | Sulu restart; nobody has played it |
| B3 | Red Line RL-1 | 2 | B1 (`recognise`/`orbat` keys) | 3 side missions, 4 pages. *Built with B1, owner's Q1, 20 Oct 2026* | Red Line restart notice |
| B4 | In-game proof run | 1 plus play | B1–B3 on the PC | Results: `IsTrue` (SWTC 6.7), `rearm_if`, `unseen`, timed datums, reserve purchase | — |
| B5 | Side play A2 | 3 | B1, B4 | `mirror()`, the Chinese-side *Bomber Stream* pilot, scoped threat display, pack-wide neutral flags | None (dispatch) |
| B6 | SR-0 and SR-D1 | 2.5 | B1 filter (dispatches excluded) | 4 Southern Reach dispatches | None |
| B7 | Sulu SL-2 and SL-3 | 3.5 | B4 (`IsTrue` for Gateway) | 9 side missions | Sulu restart |
| B8 | Red Line RL-2 and RL-3 | 7.5 | B4 (`unseen`), Java extract | RL07–RL09 and 5 side missions | Red Line restart |
| B9 | SR-AB | 8 | B4, builder neutral fix | 9 spine side missions, 8 pages | **One** Southern Reach restart |
| B10 | Red Line RL-4 and RL-5 | 6.5 | B8 | RL10–RL12 and the rest | Red Line restart |
| B11 | Remaining dispatches (SR-D2, RL-6, SL-4) | 6.5 | coast extracts | 17 dispatches | None |
| B12 | A3 and A4 | 1.5–2 | Reserve proven in one release | PLAN reserve (the 901 and 903A done with Batch 1, 21 Oct 2026; 052D and 055 open), ~~twins retired~~ (done with Batch 1, 21 Oct 2026), optional names | Twin saves stranded on 21 Oct, with no notice ahead |

Total about 47 sessions.

**How Batch 1's Open Allocation and side work changes every later mission's authoring:**
1. **The named-hull filter.** Any variant of an allied class that a new campaign mission places, on any side, comes off sale in every reserve in the pack. Examples: JS Maya V1 in TS11 and TS08A, HMS Spey (River B2 V5) in TS04A, Courbet (La Fayette V2). Authors pick variants knowingly, and the gate test lists what was removed.
2. **Red units the player must spare** get the "do not engage" recognition label automatically. A unit whose identity is the puzzle needs `recognise=False` and `orbat=False`. Every red-side mission after B1 uses these.
3. **The pack-wide variable gate** applies to every new mission: every read needs a writer, and every writer needs a reader.
4. **The Anzac convention (if Q7 is yes):** 2028–29 missions place only MH-60R variants. Red Line needs a hull that no roster sells.
5. **After B5,** every Chinese-side or Russian-side dispatch is authored through `mirror()`.
6. **New units that a campaign gates** to certain windows go in that campaign's `OPEN_HOLD`, so the twin follows the story.

---

## 6. Decisions for the owner (recommended answer first)

**These block Batch 1:**

1. **Scope of the next update.** (a) Section 8 only: fixes, the allied reserve and gates, with no new missions (recommended, save-safe). (b) Also Red Line's three side missions (forces a Red Line restart). (c) Also four Southern Reach dispatches (about +1.5 sessions).
2. **Southern Watch reserve.** (a) The 11 classes in §3.6, frigates from *Weapons Free* and destroyers from *Southern Lifeline*, window 12 keeping all, with no carriers, amphibious ships, tankers or aircraft (recommended). (b) MD's three escorts only. (c) Everything from window 05. (d) Also add the German, Italian, Spanish, Dutch, Norwegian and Danish classes.
3. **Southern Reach reserve.** (a) The three classes (Type 23, Mogami, Daegu) from *Tasman Crossing* (recommended, realism). (b) At every window, as the current unreleased build does. (c) None (SRB:101).
4. **Red Line and Sulu Line reserve.** (a) None this update (recommended: `RL/tables.py:64-68`; `SL/__init__.py:96`). (b) Red Line's 901 and 903A now, with a bible change.
5. **The twins.** (a) Keep all four; fix Sulu's two defects (recommended). (b) Retire now. This strands `-open` saves, including `NEW TEST 1.sav` (`docs/packaging-and-recovery.md:752-757`). **Decided 21 Oct 2026: (b)**, in the pending 20 Oct update, with Sulu's fixes kept in the dormant code; the builder keeps the twins as an opt-in for a world-wide campaign.
6. **Campaign names.** (a) Unchanged this update; the bracketed navy already says the side (recommended). (b) Later, a side tag before the bracket: "Western side" / "Eastern side". (c) "NATO" / "Warsaw", which is less realistic for the Banda Sea.
7. **RAN Anzacs.** (a) Re-pick every 2028–29 Anzac, sold or placed, to its MH-60R variant, with a PC check (recommended, realism). (b) Leave as is until the PC shows which helicopter a bought Anzac embarks.
8. **Sulu Service at Sea.** (a) Charter no longer fatal; remove the dead `SL04ServiceHeld`; the rearm stays the physical transfer (recommended). (b) Charter no longer fatal and `SL04ServiceHeld` wired to Celebes Gate's `rearm_if`, which makes the in-mission transfer redundant.

**These block later batches:**

9. **Red-side canon.** Keep the coalition campaigns canon, with red winning by restraint (recommended), or play alternate history.
10. **Russia.** Dispatches only (recommended); Russian hulls on sale; or a Russian-led campaign.
11. **Sulu red side.** Skip it, apart from the SLD6 dispatch labelled non-canon (recommended); build it with China Coast Guard stand-ins; or drop SLD6 too.
12. **Indonesia.** A non-aligned partner, as in Southern Watch (recommended), or red as in the world-sandbox document.
13. **Order of depth work.** Sulu, then Red Line, then Southern Reach dispatches, then Southern Reach's spine in one restart (recommended).
14. **New theatres** (Baltic, North Atlantic). Not now (recommended).
15. **Southern Reach slate.** Drop SR11A for exactly 10 optionals (recommended), or keep 11. TS11's reward: JS Mogami (recommended, so the fleet action is not made easy) or JS Maya.
16. **`IsTrue` partner rewards.** Only after Southern Watch test 6.7 passes in game (recommended).
17. **Red Line codes.** Stable codes, with display numbers re-derived once per batch (recommended), or a one-time renumber.
18. **Red Line rearm.** Only at home port or from replenishment (recommended), or as now.
19. **Sulu.** 12 cores, renumbered now (recommended). One pick each for the RAN and Thai frigates: only after confirming in game that one purchase per variant is the cap.
20. **Dispatch realism.** Drop RLD6 (recent real event); fictionalise SLD3's opposing group; label SRD6 and RLD5 (2034) as fictional; allow the SRD7 hulk target "ex-HMAS Anzac" (recommended for all four).
21. **Points.** Accept the new totals (Southern Reach 3,410, Red Line about 2,130, Sulu about 2,010) and run one balance pass after B4 (recommended).

---

## 7. Evidence notes

### Re-checked at `4defe5c8` for this document

- **Branch and deploy.** `data/deploy-branch.txt` names `sest-dev/loving-bell-3cnvvw`. That branch does not resolve in this clone, and `c8f1b0f5` is an ancestor of HEAD, two commits back (`87b43e03`, `4defe5c8`). The PC last synced to `c8f1b0f5` (`docs/workshop-refresh-20261020-review.md:155`). `44cde6d0` is in the clone, 14 commits behind HEAD.
- **Last upload:** `c948bc9a` on 15 Oct (`docs/workshop-refresh-20261015-review.md:95`); 82 commits since.
- **SW04 overwrite:** CD:5868 appends the `O5ReceiverNamed` reveal, then CD:5908 assigns `_m["reveal_if"] = [...]`, replacing it.
- **Allied escorts in the build:** MD:206-234 hard-codes three classes. They are in Southern Watch's [Mission17] and [Mission40] allowlists and in Southern Reach's roster with Mogami Variant1 (`OUT/sest-southern-reach/player_task_force_roster.ini:18`).
- **Pack-wide placement scan:** among allied entries, Southern Reach sells Mogami Variant1 (placed by SW10 blue and RL03 red) and Daegu Variant1 (placed by SW O3).
- **Sulu twin:** [Mission2] sells the C8; [Mission5] sells all three supply ships; the description claims an allied fleet (`OUT/sest-sulu-line-open/campaign.ini:65`). The standard campaign sells none of them at SL02.
- **Red Line leaks:**
  - The RL02 briefing labels a Virginia photo "Expected opposition".
  - `enemy_theater_roster.ini:11-12` lists `ran_ssg_collins=Variant6` and :21-24 a USN submarine section.
  - Neutrals are built with `Nation=Russia` in RL01 (:87 ferry, :114 trawler), RL05 (:67) and RL06 (:84), all cruise ship or civilian hulls.
  - An explicit `nation=` always wins over the remap (`integration/common/flags.py:19-23`).
- **Mission reports:** MD:74-79 name LI and CHEN, put "ceasefire" on 12 Nov, and say "snorkel" for a nuclear boat. MD:80, 86 and 89 sign Sulu reports SANTOS.
- **Variables:** Southern Watch 15/15, Southern Reach 20/20, Red Line 1/1, Sulu 5/4 (unread: `SL04ServiceHeld`, set at `SL/sl04_service_at_sea.py:75`). The Sulu charter is fatal (:81) and is also the support-loss unit (:82-88).
- **Anzac variants:** `mods-source/3820759806/vessels/ran_ffh_anzac_variants.ini:15-169`; names at `…/language_en/vessel_names.ini:63-76`.
- **Spec assembly:** `campaign_specs()` builds each spec and runs `mission_depth.apply(specs)` across all of them (BP:432-503), so a pack-wide filter fits there.
- **Twin writer and gate:** BP:355-429 and BP:7644-7670. The twin gate is CCC:377-480.
- **Saves:** a mission-file change "needs nothing"; a new entry means restart; a `campaign.ini` value "may not reach" a running campaign (`docs/packaging-and-recovery.md:774-778`).
- **Change-log home:** WL:110 already holds the pending "20 Oct 2026" block. WL:64-71 has the Sulu and "not yours to keep" text.
- **Gates and tests:** "All twelve gates green; tools 133 tests (7 skipped), campaign 222 tests" (`docs/workshop-refresh-20261020-review.md:122`). Gate commands are at README.md:62-89 and `docs/packaging-and-recovery.md:819-826`.
- **Open play-test items:** `docs/playtest-20261020.md:236-249`. Item 8 asks for a standard-roster allied escort purchase. The no-runtime note is at :251-252.

### Open ASSUMPTIONs

1. The PC is at `c8f1b0f5`, and `loving-bell` is there too. Neither could be resolved in this clone.
2. Which twelve tools the docs mean by "twelve gates". My reading: the 15 `tools/check_*.py` scripts minus the report-only `check_system_names` and `check_reloadable` and the per-mod `check_mod_conflicts`. Plus `build_all --from-scratch` with a clean `git status`, and `preflight --all`.
3. A running campaign does not see new `campaign.ini` allowlists. It will load, but may not offer the reserve.
4. Removing roster picks does not break a save that holds one (SWBN:2638-2640 is the only evidence).
5. The game reads a long allowlist (SWTC G.7 and G.8 unrecorded).
6. A bought Anzac embarks its variant's air group (S-70B-2 on Variants 1–3, 5, 6 and 8), and ServiceDate does not bar it without "Limit unit dates".
7. `spawn_if` IsTrue spawns; `TaskForceModeRearmByVariableAND` works; `unseen` works. All three are unproven in game.
8. Whether variables written during a lost attempt persist.
9. Whether an unspawned conditional unit counts as destroyed in a neutral-loss or fatal trigger. The plan's fix is to keep such units out.
10. Inserting spine entries breaks saves past that point. Evidenced for Southern Reach (`docs/campaigns/southern-reach/build-notes.md:455-458`) and assumed elsewhere.
11. An authored C8 carries its full 300,000-point pool in every mission.
12. One purchase per variant (Sulu's "one frigate" bounds).
13. A bought Soviet-registered hull flies the USSR flag.
14. Long campaign names are not truncated in the list (relevant only if Q6 is answered b or c).
15. No Eastern treaty bloc exists in 2028; Indonesia is non-aligned.
16. Malampaya's position, and the Kingston anchorage at 1.06 NM.
17. Effort estimates: about 0.3–0.5 session per mission plus 0.5 per batch.

---

## 8. Next update batch (B1): what to build now

### 8.1 Scope, effort and save safety

- **Effort: about 2 sessions,** or 1.8 without the Anzac re-pick.
- **Save safety:**
  - No campaign gains or loses a spine entry, so every `Parents` and expiry index is unchanged. *The exception is Red Line, whose RL-1 the owner added (Q1): its restart is accepted (8.3).*
  - Mission-file changes need nothing (`docs/packaging-and-recovery.md:774-776`).
  - Allowlist and roster changes may reach only new campaigns, which is said in the change log.
  - Twin folders and paths are unchanged.

### 8.2 Files and changes

| # | File (where) | Change | Why |
|---|---|---|---|
| 1 | MD:206-234 | Replace `expand_roster` with `apply_reserve(specs)`, called once from `apply()` before the per-mission loop. It reads each spec's `RESERVE` (`unit`, `opens` mission code). It drops every variant that any non-dispatch mission of any campaign places on any side. It adds the reserve to the roster, removes those units from `ALLIED_FLEET` (as now), extends allowlists at buy windows dated on or after `opens`, and writes a generated class-list sentence | Data-driven reserve; pack-wide named-hull filter |
| 2 | CD, beside ROSTER (CD:434-445); correct CD:5238-5242 | `RESERVE` with the 11 classes and two tiers (§3.6, per Q2) | — |
| 3 | BP:443-455 (the `watch` dict) | Pass `RESERVE=sw.RESERVE` | Spec plumbing |
| 4 | `SR/tables.py` and `SR/__init__.py` CAMPAIGN | `RESERVE`: Type 23, Mogami and Daegu, opening at TS04 (Q3) | Realism timing |
| 5 | BP `campaign_rules()` (BP:194-339) | One line in story mode when `RESERVE` exists | The player is told |
| 6 | BP:7658 | `allied_line(allied, …)` instead of `twin_roster` | Fixes Sulu's false sentence |
| 7 | BP `open_allocation_ini()` (BP:385-429) and `SL/__init__.py` CAMPAIGN | New `OPEN_HOLD` (Sulu's three supply ships). A held unit appears in a twin window only where the base allowlist has it | Fixes the twin's SL01 and SL02 leak |
| 8 | CCC `open_twin()` (CCC:377-480) | The allied sentence comes from twin rows not in base (CCC:438-441); held units are expected only where the base sells them | Keeps the coverage gate true |
| 9 | CD:5908 | `_m["reveal_if"] = _m.get("reveal_if", []) + [dict(` | Restores O5 → SW04 |
| 10 | BP `recognition()` (BP:5465), `enemy_roster_ini()` (BP:5898), `recognition_xml()` (BP:5746) | Honour `recognise=False` and `orbat=False`. Label red units named in a `spare` resolver "Protected – do not engage" | Red-side presentation; correct for every campaign |
| 11 | `RL/rl01_trailing_contact.py:137`; `RL/rl02_routes_they_can_see.py:132` | ALPHA → Variant3; `recognise=False, orbat=False` on ALPHA and GOLF | Canon (RLB:28, `RL/rl02…:14-17`) |
| 12 | `RL/rl01…:152,157`; `RL/rl05…:153`; `RL/rl06…:143` | Explicit `nation=`: Indonesia for RL01's ferry and trawler; Panama, a flag of convenience Sulu already uses, for the cruise ships | Right flags |
| 13 | MD:74-79; MD:80,86,89 | Rewrite the six Red Line reports with roles, not names. SANTOS → MANALO | RLB:35; cast collision with SWB:128 |
| 14 | `SL/sl04_service_at_sea.py:70-88,147`; `SL/__init__.py:69-72` | Victory on `screen#1` at the box after the 30-minute stage. "Charter" becomes a scored protect objective. Remove `F("Charter")`, the `SL04ServiceHeld` set and its declaration. Guard message without "(rearm_if)" (per Q8) | Makes the existing Aborlan branch reachable in a win |
| 15 | `SL/sl03a_the_okean.py:95-98` | Correct the lose text (Patrol is not fatal) | Text matches data |
| 16 | TBP | New tests: reserve opens only from its mission; window 12 keeps escorts; destroyer tier absent at SW05; Southern Reach sells no Mogami V1 or Daegu V1; Sulu twin sells supply ships only where the story does; Sulu twin has no allied sentence; rules line present; SW04 built with both reveals; **pack-wide: every variable read is declared and every declared variable is read**; `recognise`/`orbat`/label behaviour. Update the AlliedFleet, `allied_line` (TBP:2145-2155) and RulesPage tests | Gates that would have caught these defects |
| 17 | `integration/campaign/test_playtest_revision.py:245` | Derive the mission count from the specs (still 77) | X5 |
| 18 (Q7) | CD:438 and placed Variant3/8; `SR/tables.py:97-102` and placed Variants 2/6; `SL/tables.py:108` | Anzac picks and placements 2→10, 3→11, 5→12, 6→13, 8→14 (7 stays). Test: no 2028–29 placement or sale of a variant whose ServiceDate ends before 2028 | Realism, X6 |
| 19 | Docs | RLB:28; Red Line build notes :208-214; Red Line test card 8A.5; SWTC section 6 (O5→SW04 row), G.6 (:338) and 2.3 (:139, if Q7); Sulu test card 2.5; `docs/campaigns/side-operations.md:66`; `docs/play-test-guide.md` (the checks in 8.4); FEATURES.md; WL description (:64-71) and change log | Docs match the build |

**Not touched:** campaign names, commander settings, points, prices, spine order, and every twin path.

### 8.3 Missions

- **New missions:** none in the batch as planned. The owner's Q1 (20 Oct 2026) added Red Line's step RL-1 (§4.2): RLO1 *Datum*, RLO2 *The Ships from the North*, RLC1 *Pilot in the Water*, the RL02 and RL03 readers and four pages, built with it (RL03's reader held on 21 Oct 2026 until it is proven). Red Line's spine goes from 10 entries to 17, so a Red Line campaign under way restarts; no other spine changed. None of the three dates had to move under X3. GOLF moved to `usn_ssn_virginia_2027` Variant10 under the corrected RLB:28, because Variant1 is the hull *Fujian's Shadow* can lose on the 23rd. Campaign missions 66 → 69, the pack 77 → 80.
- **Changed:**
  - Southern Watch 04 *The Quiet Passenger* (reveal).
  - Red Line 01–06 (recognition, order of battle, flags, reports).
  - Sulu Line 04 *Service at Sea* (charter), 03A *The Okean* (text), and SL01, SL05 and SL07 (report signature).
  - Every Southern Watch, Southern Reach and Sulu Line mission that places an Anzac, if Q7 is yes.
  - Briefings with spared red units get the new label (for example Southern Reach SR07's Fersman, Red Line RL03).

### 8.4 How Open Allocation and side choice appear in this update

- **Open Allocation:**
  - Southern Watch's standard campaign sells all eleven allied escort classes, frigates and destroyers together, from *Weapons Free* (owner's decision Q2, option c, 20 Oct 2026).
  - Southern Reach sells three escort classes from *Tasman Crossing*.
  - Each is said in the window text and on the rules page.
  - *Extended 21 Oct 2026:* the whole allied fleet from the same windows, and Red Line's Type 901 and 903A from its first force allocation (the owner's third decision above).
  - ~~The four twins remain the "everything from the start" option. Sulu's twin now follows the story's supply-ship windows.~~ Superseded 21 Oct 2026: the twins are retired in this update, and each campaign is listed once.
- **Side choice:** no new entry and no rename. Red Line, the Eastern side, stops giving away its puzzles in the briefing and the Situation window, and labels coalition units it must not fire on. That is the groundwork for the mirror dispatches in B5.

### 8.5 Acceptance checks

**Build and gates.**
- `python3 tools/build_all.py --from-scratch`, then commit; `git status` clean afterwards.
- `python3 tools/preflight.py --all`.
- The twelve gates (ASSUMPTION 2): `check_inventory` (red only on its four known CR-stripped mods), `check_alias_bases`, `check_vanilla_drift`, `check_game_version`, `check_load_order`, `check_dependencies`, `check_scenarios`, `check_stale_phrases` (retire "CAPTAIN LI", "POLITICAL OFFICER CHEN", "neither campaign places"), `check_station_clash 0.001`, `check_weapon_employment`, `check_pack_fidelity`, `check_campaign_coverage`.

**Unit tests.**
- `python3 -m unittest integration/campaign/test_build_pack.py integration/campaign/test_playtest_revision.py`: 222 tests plus the new ones (241 ran at `5076cd99`, the inherited opening-range classes counted twice; 270 with Batch 1's, 278 with RL-1's, 284 with the 21 Oct 2026 changes: the twins retired, RL03's reveal held; 289 with the allied fleet in the standard campaigns, later that day).
- `python3 -m unittest discover -s tools/tests -p 'test_*.py'`: 133 tests.

**Offline output checks.**

| Where | Expect |
|---|---|
| Southern Watch [Mission17] (SW05) allowlist | All eleven reserve classes, frigates and destroyers alike (Q2, option c); since 21 Oct 2026 the whole allied fleet the build keeps (72 units) |
| Southern Watch [Mission30], [Mission36] and [Mission40] (SW09, SW11, SW12) allowlists | All eleven reserve classes; since 21 Oct 2026 the same 72 |
| SW01–SW03 allowlists ([Mission2], [Mission8], [Mission13]) | No allied hull, and no allied aircraft |
| Southern Watch and Southern Reach `campaign_rules_en.xml` | One line on the reserve: *Weapons Free* and *Tasman Crossing*; ~~"Allied escorts are on sale from the force allocation before …"~~ since 21 Oct 2026 "Every force allocation from the one before … also sells the allied fleet - …"; Red Line's names its Type 901 and 903A, never as allied; none in Sulu Line ~~or any twin~~ (no twin ships since 21 Oct 2026) |
| Southern Reach roster | No `js_ffg_mogami` Variant1 and no `ko_ffg-818` Variant1 |
| Southern Reach windows before TS04 | No allied escort |
| ~~Sulu twin [Mission2]~~ | ~~No C8~~ Superseded 21 Oct 2026: the twin is retired; TBP `SuluOpenAllocation` builds it in a temporary folder and checks this |
| ~~Sulu twin [Mission5]~~ | ~~No supply ship~~ Superseded 21 Oct 2026, as above |
| ~~Sulu twin Description~~ | ~~No allied sentence~~ Superseded 21 Oct 2026, as above |
| Red Line RL02 briefing XML | No "Virginia" |
| Tasman Shield 11A briefing XML | The 054A and Z-9C read "Opposition - do not fire first", not "Protected - do not engage": its Restraint lifts on hostile intent (`lift`) |
| Red Line `enemy_theater_roster.ini` | No `SubmarinesPersistent_USN`, no Collins |
| Red Line mission files | No `Nation=Russia` on neutrals |
| Southern Watch 04 mission file | Both "Reveal from" triggers |

**In-game checks before upload.** Upload is gated on the changes being played (`docs/campaigns/southern-watch/publishing.md:244-247`).

| # | Do | Expect |
|---|---|---|
| R1 | New standard Southern Watch, windows 01–03 | No allied hull offered |
| R2 | *Weapons Free* window: buy a Mogami or Type 23 | Offered at list price; it sails; still only one ship sails (`MaxUnits=1`); the Type 45 and both Burkes offered too (Q2, option c) |
| R3 | *Southern Lifeline* window | All eleven still offered; a Type 45 or Burke bought here sails |
| R4 | *The First Ship Through* window | Escorts still offered |
| R5 | New Southern Reach | Mogami Variant1 never offered; allied escorts first appear at *Tasman Crossing* |
| R6 | Sulu Line, standard (the twin retired 21 Oct 2026), *Fire Mission Jolo* window | No supply ship |
| R7 | A pre-update standard Southern Watch save, mid-campaign | It loads. Record whether the reserve appears (expected: maybe not) |
| R8 | `NEW TEST 1.sav` | Since 21 Oct 2026: cannot be continued, the twin being retired; note what the game shows, and that the campaign menu lists four campaigns |
| R9 | Red Line 01 and 02 briefings and the Situation window | No Collins or Virginia photo or entry; protected units labelled |
| R10 | Sulu *Service at Sea*: let Sulu Provider be sunk and complete the rendezvous | Mission won; *The Aborlan Battery* starts without her |
| R11 | Fly O5 and O2, then *The Quiet Passenger* | Both datums appear |
| R12 (Q7) | Buy an Anzac | It embarks an MH-60R. *Not in this batch: Q7 was answered no (20 Oct 2026), and the Anzac re-pick (8.2 #18) was not built* |

Also play the eight open items in `docs/playtest-20261020.md:236-249`. They cover changes already in this update.

### 8.6 Deploy and publish

1. Commit on `sest-dev/jolly-ride-rptj4t`.
2. Carry the commit to the deploy branch named in `data/deploy-branch.txt` (`sest-dev/loving-bell-3cnvvw`). Fast-forward if it is an ancestor (ASSUMPTION 1).
3. On the PC: `.\tools\sync-sest.ps1` must report IN LINE.
4. Play R1–R12.
5. Before Submit, apply the pending Required Items changes (WL:112-116: add 3807187341 and 3818251045; remove 3440622312).
6. Paste the change log. Update the description lines in the same sitting (`docs/campaigns/southern-watch/publishing.md:348-353`).

### 8.7 Change-log lines

*Superseded (20 Oct 2026). The lines as pasted are the pending "20 Oct 2026" block in `docs/campaigns/southern-watch/workshop-listing.md`, which follows the owner's decisions: every Southern Watch escort class from Weapons Free (Q2, option c), no Anzac line (Q7), and a* Red Line *block for RL-1's side operations with its restart notice (Q1). The block below is the plan as first written, kept for the record.*

Append these inside the pending "20 Oct 2026" block at WL:110, which has not been uploaded:

```
[b]Allied escorts[/b]
[list]
[*]Southern Watch: allied escorts can now be requisitioned in the standard campaign, at their own navies' prices. From Weapons Free: Type 23 and River-class (UK), Mogami and Asahi (Japan), Daegu and Chungnam (South Korea), La Fayette and Aquitaine (France). From Southern Lifeline: Type 45 and Arleigh Burke Flight IIA and III. No carriers, amphibious ships, tankers or allied aircraft, and no ship a mission names elsewhere.
[*]Southern Reach: Type 23, Mogami and Daegu escorts from Tasman Crossing.
[*]A campaign already under way may not show them: start a new campaign to see them. The Open Allocation versions are unchanged and still offer everything from the first window.
[/list]

[b]Fixes[/b]
[list]
[*]Southern Watch, The Quiet Passenger: Paper Trail's lead on the passenger appears again, beside Southern Cross's datum on the submarine.
[*]Red Line: briefings and the Situation window no longer show the trailing submarines' class or navy before you classify them, and ships you must not fire on are labelled as such. Civilian ships fly their own flags, and the command-net reports no longer name officers.
[*]Sulu Line, Service at Sea: losing Sulu Provider no longer ends the mission. Complete the rendezvous without her and she is missing at The Aborlan Battery.
[*]Sulu Line - Open Allocation: supply ships are on sale only where the story sells them, and the description no longer lists Sulu's own Thai and Australian units as an allied fleet.
[*]RAN Anzacs carry the MH-60R, as they have since 2017.
[/list]
```

The last fix line applies only if Q7 is yes.

**Description edit (WL:69-71).** Replace "partners arrive on their own terms and are not yours to keep" with: "Partners arrive on their own terms; in Southern Watch and Southern Reach allied escorts can also be requisitioned at their own prices, and in Sulu Line the Thai detachment and one RAN frigate are bought into the task group."

### 8.8 Not in this batch, and when it comes

1. **B2:** Sulu's renumbering and five new cores.
2. ~~**B3:** Red Line's three side missions.~~ Built with B1: the owner's Q1 (20 Oct 2026) added RL-1 to this batch (8.3).
3. **B4:** an in-game proof run.
4. **B5:** `mirror()` and the Chinese-side pilot dispatch; scoped threat display; pack-wide neutral flags.
5. **B6:** Southern Reach's groundwork and four dispatches.
6. **B7–B11:** the rest of the depth work.
7. **B12:** PLAN reserve and names (the twins retired with B1, 21 Oct 2026).

Section 5 has the order and dependencies.
