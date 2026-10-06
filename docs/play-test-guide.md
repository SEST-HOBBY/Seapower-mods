# Play-test guide — all four campaigns

A plain checklist for testing the SEST campaigns in the game. It covers what
matters most, in the order to test it. Each campaign also has a detailed test
card (`docs/campaigns/<campaign>/test-card.md`) with every check numbered; this
guide uses the same numbers in brackets where they apply, so a report can point
at either.

Nothing in Sulu Line has been run in the game yet. The other three have been
loaded and partly played; their open questions are listed below.

---

## 0. Before you start (5 minutes)

1. Game closed. In the repo folder on the PC:
   `.\tools\sync-sest.ps1` — it must end with **IN LINE** and the current
   commit number.
2. Start Sea Power → **Mod Manager**: *SEST Integration Pack* is at the top
   and ticked. If it offers to move or fix dependencies, say **no**.
3. **Options:** note the two weapons settings under Left Shift+O —
   "Ships on Weapons Tight engage hostile aircraft" and "Ships use anti-ship
   missiles on Weapons Free". Leave them at their defaults and say what they
   were in your report.
4. Keep a note open. For every mission you play, write down:
   - the mission name and result (won / lost / ran out of time);
   - the objective list as it shows at the end, and the points awarded;
   - anything ashore, missing, unnamed or showing MISSING TEXT;
   - for a problem: what you did, what happened, and a screenshot.

**Save often.** Several checks need a save, a quit to desktop and a reload.

---

## 1. Quick check: everything loads (15 minutes)

Do this first. If something here fails, stop and report it; the deeper checks
depend on it.

| Do | Expect | If not |
|---|---|---|
| Open **Campaigns** | Eight entries: Southern Watch, Southern Reach - Tasman Shield, Red Line - The Other Watch, Sulu Line - The Island Road, and an *Open Allocation* version of each | Name the ones missing |
| Look at each campaign's background | A dark chart with numbered mission marks, the campaign name bottom-left | Blank or a stock picture: say which campaign |
| Mission browser (single missions) | Folders: Southern Watch, Southern Watch - Dispatches, Southern Reach, Tasman Shield, Red Line, Sulu Line | A missing folder |
| Load one mission from each folder from the browser: **Southern Watch 01 - White Water**, **Southern Reach 04 - Macquarie Passage**, **Red Line 01 - Trailing Contact**, **Sulu Line 01 - The Island Road** | Every ship and aircraft appears, flags shown, no ship on land | A missing or grounded unit: its name and the mission |
| Open a briefing in each | Photo banner at the top, a chart in the right-hand pane, photos of your forces and the opposition at the end | Blank pane or no photos |

---

## 2. Sulu Line — The Island Road (new, nothing tested yet)

Philippine Navy, seven missions, October–November 2028. **The whole campaign
rests on one rule: there is no free rearm.** Check that first.

### 2A. Starting the campaign

| Do | Expect | If not |
|---|---|---|
| Start Sulu Line on **Standard** | Commander screen: nation **Philippines**, the Philippine flag as navy emblem, rank **Commodore**, a Spanish-style default name (editable). Rank pictures are blank on purpose | The screen refuses the nation, shows a broken image, or won't continue **(4.1)** |
| Read Campaign Rules → Your Goal | "Rearm: never free…", and a paragraph naming the three supply-ship sales | Still says "for free" **(1.3)** |
| Open the Task Force builder before mission 1 | 1,000 points. On sale: Jose Rizal class, Miguel Malvar class, Del Pilar class, Conrado Yap, BRP Tarlac / Davao del Sur, HTMS Chula, the H-76 helicopter. **Not** on sale yet: Thai frigate, RAN Anzac, FA-50, the C8 charter **(1.1)** | Anything else on sale, or a supply ship missing |
| Check prices | Philippine units 20% cheaper than their list price; Thai, Australian and MSC units at full price. Note especially whether the **Jose Rizal** and **Miguel Malvar** get the discount (their files spell the nation in lower case) **(4.2)** | Note the prices you see |

**Buy:** at least one frigate, one Tarlac, and the H-76.

### 2B. The no-rearm rule (most important)

| Do | Expect | If not |
|---|---|---|
| In mission 1, fire some 76 mm rounds and at least one missile. Win | — | — |
| Open the Task Force screen before mission 2 | The frigate shows **fewer** rounds than she started with. **No** green "Rearmed" icon. The stores editor is locked with "Ammunition expended and no rearm before this mission" **(1.2)** | She is full again → the rule does not work in game. **Report this first**; the campaign needs rethinking |

### 2C. Supply ships at sea

| Do | Expect | If not |
|---|---|---|
| In mission 2, fire the gun. Then bring the frigate **within half a mile** of your Tarlac, **both ships at 8 knots or less**, and wait | The frigate's 76 mm count climbs; the Tarlac's stock falls **(2.1)** | Nothing crosses: note the round, the ships, both speeds and the distance |
| Same, after firing a **MICA** and a **Harpoon** | Both come back | Note which does not |
| If you bought the Thai frigate (from mission 2): fire a Harpoon, then go alongside | It comes back **(2.2)** | The launcher stays empty while the gun refills |
| After a mission where the Tarlac gave stores, check her before the next mission | Her stock is still lower **(2.3)** | It refilled to full: report it. The campaign still works but is easier than intended |
| Let a supply ship be sunk | She is gone from your task force. Mission 5's window does **not** sell another; missions 4 and 6 do **(2.4)** | — |

### 2D. Mission by mission

| Mission | What to check |
|---|---|
| **1 The Island Road** | Convoy of two reaches the box 30 NM south-west; two Meridian fast attack craft come from the south-east. Win = both convoy ships in the box |
| **2 Fire Mission Jolo** | Ship starts 25 NM north of Jolo. Steam in; the 76 mm reaches the ridge from about 8 NM. **Three of five** positions destroyed = victory **(3.1)**. Check the launch rails can attack your ship |
| **3 Ayungin** | Everything Chinese stays at Hold and never fires **(5.1)**. Firing on any of them ends the mission. The boat entering the shoal's lagoon wins |
| **4 Service at Sea** | Keep your lead ship within 3 miles of *Sulu Provider* for 30 minutes: a "Thirty minutes" message appears, then she steers north to the box. Use her to rearm: go alongside at 8 kn or less. Sink her in a second run and check she is **missing** from mission 6 **(2.5)** |
| **5 Celebes Gate** | Four coasters, one is the gun-runner (armed, with an escort boat and a drone nearby). Sinking a wrong one ends the mission. Sinking the right one before the Basilan Strait wins |
| **6 The Aborlan Battery** | Two Silkworm launchers ashore fire at ships inside about 25 NM, including the convoy at anchor **(3.2)**. Both launchers destroyed wins |
| **7 Balabac Strait** | Chinese surface group of five from the west, two JH-7A strike aircraft, maybe a submarine. **Three of five** ships sunk wins. Note how much ammunition you had left |

### 2E. Bring back

Mission results; the answer to **2B** (most important); whether rounds crossed
in **2C** and at what speeds; whether supply-ship stocks persisted; the
discount prices; how many shots it took to win missions 2 and 6.

---

## 3. Southern Watch — The Northern Lifeline

Royal Australian Navy, October–November 2028. 12 core missions, 4 optional
operations, 2 contingencies, plus 8 single missions under *Southern Watch -
Dispatches*. Full card: `docs/campaigns/southern-watch/test-card.md`.

| Check | Do | Expect |
|---|---|---|
| Builder **(2.2–2.3)** | Before mission 1 | Only Anzac, Arafura and MH-60R on sale; Anzac at 192 (240 less 20%) |
| Your ship appears **(2.4)** | Deploy into mission 1 | The ship you bought is there, on station, not drifting, with no extra authored ship beside it |
| Roster grows **(2.5)** | Before mission 2 | Hobart and P-8 added |
| Air tasking **(3.1–3.5)** | Open Air Tasking before missions 1, 2 and 6 | Ship's Flight; then Maritime Patrol; then Combat Air Patrol. **Never** a row with 0 slots |
| Fuel **(4.2)** | Mission 7, follow a Super Hornet to the end | It gets home to Darwin. Running dry is the most likely failure here |
| Losing cleanly **(5.2)** | Mission 1, lose three merchants on purpose | Defeat, and the other objectives show **cancelled** |
| Memory **(6.1–6.4)** | Lose HMAS Supply in mission 2, then reach mission 9; also save, quit and reload in between | MV Coral Provider is **missing** from mission 9. Keep Supply alive and she is there |
| Rearm earned **(6.9)** | Hold mission 9's service window, then look before mission 10 | A rearm is offered. Miss the window and it is not |
| Rearm at sea **(6E)** | Mission 9, fire a missile, then go within half a mile of HMAS Stalwart at 12 kn or less | The missile comes back |
| Optional ops **(6.7)** | Bring both Korean warships in at O3, then start mission 6 | ROKS Sejong the Great is in your screen |

---

## 4. Southern Reach — Tasman Shield

Royal Australian Navy, December 2028–March 2029. 26 missions in two
chapters. Every position was checked against a real coastline, so grounding
is the thing to watch. Full card: `docs/campaigns/southern-reach/test-card.md`.

| Check | Do | Expect |
|---|---|---|
| Coastline **(1A.1–1A.2)** | Load **Tasman Shield 02 - Cook Strait**, pause at the start, then run 10 minutes at 8x | Every ship afloat; the ferries cross Wellington–Picton without grounding |
| Anchorage **(1A.3)** | Load **Southern Reach 04 - Macquarie Passage** | Supply and Coral Pioneer in Buckles Bay, afloat |
| Builder **(2.1)** | Before mission 1 | Anzac 192, Hobart 384, Seahawk 16 |
| Rearm earned **(2.3–2.4)** | Before SR06: once after **missing** SR04's 30-minute window, once after **holding** it | No rearm / rearm offered |
| Rearm at sea **(4.10)** | SR04, fire an NSM or ESSM, then go within half a mile of Supply at 12 kn or less | It comes back |
| Detachment **(2.5)** | Before TS02 | You choose which ships sail |
| Optional pair **(2.8)** | After TS09 | Both TS10A and TS10B offered; play one; after TS11 both are gone |
| Consequences **(3.6, 3.11)** | Sink VICTOR in SR07 → check SR10; sink ROMEO in TS05 → check TS09 | The sunk boat is missing later |
| Weapons Tight **(4.8)** | SR10, everything red starts Tight | Nothing fires until you do |
| Defector **(6)** | TS11A The Twelve-Mile Line | See section 6 of the card |

---

## 5. Red Line — The Other Watch

People's Liberation Army Navy, November 2028–February 2029, six missions. Won
by restraint: almost every mission is lost by firing on the wrong thing.
Full card: `docs/campaigns/red-line/test-card.md`.

| Check | Do | Expect |
|---|---|---|
| Commander **(1.2)** | Start the campaign | Nation China, rank Rear Admiral, PLAN emblem; rank pictures blank on purpose |
| Weapons Hold **(4.1)** — biggest risk | RL01, leave everything at Hold for 10 minutes with the submarine astern and the Poseidon overhead | Nothing fires |
| Weapons Tight **(4.3)** | RL02, frigate at Tight with the Poseidon passing overhead | It does not shoot the Poseidon |
| Direct order **(4.4)** | RL04, frigate at Hold, order it to fire on *Meridian Harmony* | The order is obeyed. Note what weapons state it switches to |
| No rearm **(3.4)** | Before RL04 | Repair only, no rearm offered |
| Unseen **(5.1–5.2)** | RL05: wait deep and slow for a minute, then come to periscope depth under the Poseidon | Nothing at first; once the Poseidon classifies the boat, the mission is lost |
| Racetracks **(8.1)** | RL05 at 8x, watch the Poseidon for the whole mission | It keeps flying back and forth; it does not circle one end |
| Timing **(6.1)** | RL04, ignore the coaster | She clears the screen and the mission is lost around T+40 to T+60. Note the minute |
| Supply ships (Open Allocation) | Start *Red Line - Open Allocation* | Type 901 and 903A supply ships on sale |

---

## 6. Pack features to check while playing

| Feature | Where | Expect |
|---|---|---|
| Encyclopedia photos | Encyclopedia → any campaign ship (e.g. Anzac, Collins, Supply, Spruance, Tarlac) | A real photograph with its credit |
| New flags | Any unit of Peru, Ireland, Bahrain, Lebanon, Greenland, Hong Kong, Uzbekistan… | A flag, not a missing-flag icon |
| Readable names | Russian ships | Names in English letters, not Cyrillic |
| Spruance | Encyclopedia → Spruance class (VLS, LAMPS III) | Named, no "Missing Class"; places on the map without an error |
| Apache AH Mk 1 | Default loadout on the ground and in flight | Rocket pods no longer drawn over the Brimstones |
| RAAF F-35A | Strike Long Range Stealth (internal JSM) | No empty wing pylons |
| Merchant supply ships | Any mission with a C8, Seabee, Ro-Ro A/B or Mercur on your side | Ships take stores alongside at 8 kn or less |
| Map lines | Tactical map with several routes | Black lines by day, white at night, selected route red |
| Gallery | Mod Manager → SEST Integration Pack → Open Folder → Gallery → gallery.html | Opens in a browser with photos and credits |

---

## 7. What to send back

For each campaign you played, paste the notes from step 0, and put these
first:

1. **Sulu Line 2B:** were ships rearmed for free before mission 2? (yes / no)
2. **Sulu Line 2C:** did rounds cross from the supply ship? Which rounds, at
   what speeds?
3. **Red Line 4.1:** did anything at Hold fire?
4. **Southern Watch 2.4:** did your bought ship appear where it should?
5. **Southern Reach 1A.2:** did any ship run aground?
6. Any crash, freeze or red error text, with the mission name.
