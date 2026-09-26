# Red Line — first play test

Nothing in this campaign has been run in the game. This card is the order to
falsify the build's claims in, riskiest first, and what "wrong" looks like for
each. It assumes the Southern Watch and Southern Reach cards have been run
once, so a mod-supplied campaign loading, its art, and Task Force Mode buying
and rearming are not repeated except where this campaign does something new:
the player is China, the rules of engagement are the mission, and two
missions are lost when the *enemy* classifies you.

Report back with the step number and what you saw. A step that fails stops
that column, not the whole card.

## First things to fly after this round

1. **Hold and Tight** — 4.1 and 4.3 below: the whole campaign stands on them.
   Test the installed copies: a mission re-saved in the game's editor comes
   back with every Hold and Tight turned Free.
2. **The unseen trigger** — 5.1 and 5.2 below.
3. **RL04's replenishment ship** — the Type 901 beside Liaoning is SEST
   Replenishment's hull; the win needs both in the box (6.2).

The rest of this round's checks (RAS, the ARRW profile, the Redback, MALICE
mass, SM-3 terminal, Intercept Model A/B, the A-10C+, Mogami's Seahawk, the
editor-crash sweep, the new scenarios) are listed at the top of the Southern
Watch card.

## Install

Same procedure and pack as the other two (`../southern-reach/install-alignment.md`).
The campaign is `campaigns/sest-red-line/`, and again as `missions/Red Line/`
for the mission browser.

## 1 — does it load

| # | Do | Expect | If not |
|---|---|---|---|
| 1.1 | Campaign list | A third entry, **Red Line - The Other Watch (People's Liberation Army Navy)**: 10 entries (6 missions, 4 pages), a dark chart from the equator to 50 South behind it | Missing = the third `campaigns/` folder is not read; the browser copies (1.3) are the way in |
| 1.2 | Start it | The commander screen: nation China, name *Cao Mingyuan* (editable), rank Rear Admiral | The rank insignia and navy emblem are **deliberately blank** (the game ships none for China). A broken-image icon, an error, or a screen that will not continue is the report |
| 1.3 | Mission browser | A **Red Line** folder with six missions | |
| 1.4 | Load RL01 and RL06 from the browser | The player's side flies the Chinese flag; Kiwi 05 (RL06) the New Zealand one; Meridian Harmony (RL04) and Austral Compliance (RL06) Panama's | A unit that fails to appear names its mod |

## 2 — the pages and the art

| # | Do | Expect | If not |
|---|---|---|---|
| 2.1 | The prologue | A signal on grey-green teleprinter stock from Fleet headquarters, 3 November; the box at the foot headed **COMMANDER'S NOTE** | ANALYST NOTE anywhere in this campaign is a bug |
| 2.2 | The page before RL04 | OUTGOING in red at the top; the group's signal of the 22nd, the reply, the ceasefire order of the 26th | |
| 2.3 | The page before RL05, and the epilogue | New orders, 22 December; the last signal, 25 February, OUTGOING, headed **FILE NOTE** at the foot | |
| 2.4 | The campaign map | Every page stands on the dark message tile; there is no newspaper tile in this campaign | A blank tile = `bkg_tile_message.png` not read |
| 2.5 | Any mission card | RED LINE and the date on the card, the title clear of the chart, own forces in blue, one objective ring. RL06's ring is the frigate's decoy station, not the rendezvous | |

## 3 — Task Force Mode

| # | Before | Expect | If not |
|---|---|---|---|
| 3.1 | RL01 | Builder open: Type 054A (280), Luda (160), Sovremenny (320), Z-9C (20); one Ship's Flight row | Anything else on sale = the allowlist is not read |
| 3.2 | RL02 | The same, plus the Y-9 (50) and a Maritime Patrol row | |
| 3.3 | RL03 | Plus the J-15 (40), J-15D (45) and KJ-500 (70); a Maritime Patrol row and a two-seat CAP row. A Y-9 bought in RL02 is offered for the Maritime Patrol row | A Y-9 or KJ-500 with no row to fly = the Recon row is not read |
| 3.4 | RL04 | Repair only: no purchase, no rearm ("what the twenty-third spent stays spent") | Rearm offered = `TaskForceModeRearm=False` ignored |
| 3.5 | RL05 | No builder and no deployment: Hull 419 alone, as authored | Any of the screen on the plot = blank generation not honoured |
| 3.6 | RL06 | On sale: Type 054A, Type 056A (120), Z-9C; the Sovremenny and Luda are not. One already owned still sails with the screen (`TaskForceModeRequireEntireTaskForce`) | A northern hull left behind = the whole force is not required after all; say which |

## 4 — the rules of engagement (the biggest single risk)

Every mission is lost by firing on the wrong thing. Whether that is a rule the
player keeps or one the AI breaks for them is the question.

| # | Mission | Do | Expect | If not |
|---|---|---|---|---|
| 4.1 | RL01 | Leave everything at weapons **Hold** for ten minutes with ALPHA astern and the Poseidon overhead | Nothing fires | A Hold unit that fires = Hold is not honoured on spawn; the mission is unplayable as written |
| 4.2 | RL01 | Set the Z-9C to **Free** over ALPHA | Note whether it torpedoes her unbidden. If it does, the mission ends at once with Restraint failed | The fatal does not fire on the boat's loss = the `spare` + fatal pair is broken |
| 4.3 | RL01, RL02 | Set the frigate to **Tight** with the Poseidon inside its missile envelope; in RL02 it starts Tight and the racetrack passes over it | It does not engage: the game's tooltip says Tight allows self-defence only | If Tight engages a Hold aircraft, RL02 is lost by its default setting and every brief that says "set them free and..." understates it |
| 4.4 | RL04 | At **Hold**, order the frigate to fire on Meridian Harmony directly | The order is obeyed | If a Hold ship cannot be ordered to fire, the brief's "engage the coaster by direct order" is wrong: note what state it takes (Tight?) and whether that then touches the Poseidon |
| 4.5 | RL03 | Fly the KJ-500's racetrack and let the F-35s (weapons **Tight**) close | They shadow and do not fire first | F-35s firing unprovoked = Tight is not honoured on red; the mission becomes a fighter fight |
| 4.6 | RL02 | Let GOLF (weapons **Free**) come | She attacks Hai Yang 7 | A passive GOLF makes the escort trivial: say so |

## 5 — the unseen trigger (new)

`UnitClassified` with `Condition_Taskforce=Taskforce2` on the player's own
boat: it fails when the coalition *classifies* her, not when it detects her.

| # | Mission | Do | Expect | If not |
|---|---|---|---|---|
| 5.1 | RL05 | Start and wait one minute, deep and slow | Nothing: the Unseen objective stays open | Failing at T+0 = the condition reads the player's own knowledge, not the enemy's |
| 5.2 | RL05 | Take Hull 419 to periscope depth under the Poseidon, or go active | Once the Poseidon classifies her: Unseen failed, the defeat message, the mission over | The boat obviously held and nothing happens = the trigger never fires; the mission is then a timed passage |
| 5.3 | RL05 | A clean run: below the layer at 5-6 knots, among the whale and the longliner, under a Poseidon that keeps flying its racetrack (8.1) | Victory in the forward box, 9.7 NM on, at about T+97 to T+116 of the 120 minutes, with Unseen still open | If the Poseidon classifies a boat at 5 kn below the layer every time, the barrier is too good; bring back the time it took and the speed |
| 5.4 | RL06 | Let Kiwi 05 classify the tender (a surfaced merchant) | Nothing fails: only Hull 334 is watched | |
| 5.5 | RL06 | Bring Hull 334 shallow under the racetrack | Unseen failed, mission over | |

## 6 — timing

| # | Mission | Do | Expect | If not |
|---|---|---|---|---|
| 6.1 | RL04 | Do nothing about Meridian Harmony; note the clock when the red box at the edge of the screen fires | "MERIDIAN HARMONY has cleared the screen...", the mission lost, well inside the 80 minutes: 15.3 NM at telegraph 4 is about T+46 (0356) at 20 knots, T+40 at her 23-knot maximum, T+61 at 15 | She reaches it after 0430 = the mission ends on the clock instead; bring back the minute and her speed so the box can be moved |
| 6.2 | RL04 | Sink her early, then take the group north-west | Victory only when Liaoning and the replenishment ship are both in the box | Victory at the kill = the `also` term was not read; victory with her afloat = the same |
| 6.3 | RL04 | Get the group into the box first, then sink her | Victory at the kill | |
| 6.4 | RL06 | Keep the frigate on the decoy station to T+30 | "DECOY REPORT..." at T+30; then the win when the tender and the boat are both at the holding position | The report early (the frigate merely inside at any time) or never |
| 6.5 | RL06 | Take the frigate off the station before T+30 | No report and no win, however the tender does | |

## 7 — the one consequence

| # | Write | Then read | Expect |
|---|---|---|---|
| 7.1 | RL02: sink GOLF | RL04 | No submarine astern (`RL02GolfSunk`), and nothing fails at the first second: *Boat* stays open to the end. If *Boat* shows failed at T+0, the engine counts a unit that never spawned as destroyed - report it, because Southern Reach's *Last Ship South* tanker has the same shape. That is why GOLF is in no fatal |
| 7.2 | RL02: leave her | RL04 | GOLF astern at weapons Hold; the SUBMARINE THREAT line on the briefing map either way |

## 8 — what the playability review could not settle

Found by reading every mission file against its brief with distances and
speeds worked out (`build-notes.md`, *Playability review*). Each is a
behaviour of the engine that no file states.

| # | Mission | Do | Expect | If not |
|---|---|---|---|---|
| 8.1 | RL05 at 8x | Watch the Poseidon for the whole 120 minutes; then Kiwi 05 in RL06 | It flies its racetrack to the end, back and forth (`Waypoints=...\|Loop`, stock's Senkaku Run form) | It circles one end after about half an hour = `\|Loop` is not honoured; RL05's barrier and RL06's watch over the rendezvous then close after 23-29 minutes, and every looped route needs its ends written out to the clock instead |
| 8.2 | RL02, RL04, RL06 | Read the speed of Hai Yang 7 at telegraph 3, Meridian Harmony at telegraph 4 and Austral Compliance at telegraph 3 | About 15, 20 and 15 knots: the build notes' times assume 5/10/15/20 knots at telegraph 1-4 for a hull without its own ladder | Bring back the three speeds; every surface time in the build notes scales with them |
| 8.3 | RL01, RL04, RL06 | Let Fujian, the withdrawing group and the tender reach the ends of their routes, each of which ends inside its box | They stop there, or hold station | A hull that sails on out of its box: a win that comes later than her arrival (RL01 after the classification, RL04 after the kill, RL06 after the half hour) needs the player to stop her first. Note it for the brief |
| 8.4 | RL05, RL06 | Watch the Poseidon (weapons **Hold**, ASW fit) over a boat that is below the layer | Note whether it lays sonobuoys or only flies | A Poseidon that never lays a buoy classifies only a mast or a periscope: the unseen objectives are then decided at periscope depth alone. Say what classified the boat when one did |
| 8.5 | RL05 | Take Hull 419 to periscope depth with her radars off (they start off), then switch the radar on | Off: nothing, unless the periscope is seen. On: the Poseidon's ESM classifies her and the mission ends | Classified with the radar off by ESM = something else is radiating; say what |
| 8.6 | RL02 | Let the tanker run at GOLF with the frigate on her bow, doing nothing | GOLF attacks Hai Yang 7 somewhere in the first half hour; the frigate, 3.5 NM on the threat bow, is where the escort should be | GOLF firing from beyond 20 NM, before any escort could act = the boat is too good at weapons Free; bring back the range she fired from |
| 8.7 | RL04 | Sink Meridian Harmony with a mobility kill first (engines, not hull) | The win waits for her to be destroyed | If the player can only stop her, never sink her, the win never comes: say which weapons finished her |

## 9 — the numbers to bring back

For each mission played: the result (win / lose / timeout), the objective
ledger as shown, the points awarded, the minute RL04's coaster reached her box
(6.1), whether 4.4's direct order worked and at what weapons state, the time
the Poseidon took to classify each boat (5.2, 5.3, 5.5), the three telegraph
speeds (8.2), whether a looped racetrack held (8.1), the range GOLF fired
from (8.6), and any unit that was ashore, missing or misnamed.
