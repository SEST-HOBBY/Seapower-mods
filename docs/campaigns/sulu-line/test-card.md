# Sulu Line — first play test

Nothing in this campaign has been run in the game. The builder has checked
every unit, variant, position, objective, trigger and price (the full dry run,
`check_campaign_coverage.py` and the campaign tests pass), but the campaign's
central rule rests on game behaviour nobody has watched yet. This card lists
those claims, riskiest first, and what "wrong" looks like for each.

Report back with the step number and what you saw. A step that fails stops
that column, not the whole card.

## 1. No free rearm (the whole campaign stands on this)

1.1 **The opening window.** Start *Sulu Line*. The builder offers Philippine
hulls, the H-76, BRP Tarlac / Davao del Sur and HTMS Chula. Buy at least one
frigate and one supply ship. *Wrong:* no supply ship on offer, or the Thai
frigate is on offer here (it should appear from Fire Mission Jolo).

1.2 **Ammunition carries over.** In The Island Road fire some 76 mm and at
least one missile, then win. In the Task Force screen before Fire Mission
Jolo the frigate shows **fewer** rounds than she started with and there is
**no** green "Rearmed" icon; the stores editor is locked ("Ammunition
expended and no rearm before this mission"). *Wrong:* the frigate is full
again — `TaskForceModeRearm=False` is not honoured and the campaign's rule
does not exist in game.

1.3 **The rules page.** Campaign rules → Your Goal says "Rearm: never free…"
and the rearming paragraph names the three supply-ship sales.

## 2. Supply ships

2.1 **Transfer at sea.** In Fire Mission Jolo, fire the gun, then bring the
frigate within half a mile of your Tarlac (or Chula) at **8 knots or less**,
both ships. The frigate's 76 mm count climbs; the supply ship's pool falls.
Repeat for a MICA (Rizal/Malvar) and a Harpoon canister. *Wrong:* nothing
crosses — note which round, which ships, the speeds and the distance.

2.2 **Philippine and Thai launchers reload.** The Rizal's Harpoon canisters
and the Naresuan's Harpoon launchers take rounds back (SEST
Replenishment now carries those three mods' hulls). *Wrong:* the launcher
stays empty while the gun refills.

2.3 **The supply ship's pool persists.** After a mission in which the Tarlac
gave stores, check before the next one whether her pool is still reduced.
Nothing in the stock files says either way. *If it refills to full*, the
campaign still works (she is a ship you must keep alive) but the briefings'
"their stocks are finite" overstates it; report it.

2.4 **A lost supply ship stays lost.** Let a supply ship be sunk. She is gone
from the task force, and Celebes Gate's window does not sell another; Service
at Sea's and The Aborlan Battery's windows do.

2.5 **Service at Sea.** Sulu Provider (the MSC C8) is a working supplier. Hold
the lead ship within three miles of her for thirty minutes: the "Thirty
minutes" message appears and the charter steers north. In a second run let
her be sunk after the message, then take the lead ship into the withdrawal
box: the mission is **won** with Charter failed, and The Aborlan Battery
opens **without** her at the anchorage. (Until 20 Oct 2026 her loss ended
the mission, so that branch could only follow a defeat.) *Wrong:* the
mission ends when she sinks = an old build.

2.6 **Retired (21 Oct 2026).** The Open Allocation versions left the pack,
so there is no *Sulu Line - Open Allocation* to start; the row is kept as
the record of what was asked. *The Open Allocation version's supply ships:*
start *Sulu Line - Open Allocation*. Before The Island Road it offers
Tarlac / Davao del Sur and Chula but **not** the C8; before Fire Mission
Jolo **no** supply ship, with the window's note saying the story keeps some
units to its own windows; before Service at Sea and The Aborlan Battery all
three. Its description in the campaign list names **no** allied fleet.
*Wrong:* a supply ship on sale before Fire Mission Jolo, or the C8 before
The Island Road = an old build.

## 3. Fire missions

3.1 **Jolo.** The five positions are on the Patikul ridge, ashore. A frigate
inside about eight miles can reach them with the 76 mm; three destroyed ends
the mission as a victory.

3.2 **Aborlan.** The two Silkworm launchers fire at ships inside about
twenty-five miles, including the convoy at the Narra anchorage. Both
destroyed ends the mission. Since 13 October the battery (both launchers,
the radar and the guns) is not on the map for the first five minutes and
comes up at about minute 5; nothing fires at the convoy before then.
*Wrong:* rounds at the convoy before minute 5, or the battery never
appears. `Disabled=True` on a land unit has no stock precedent (only a
Workshop campaign uses it); if the battery never comes up, report it
first, because the mission cannot be won, and the fallback is weapons
Tight on the battery. Southern Watch's S-400 battery (its card, 6C.9) has
the same dependency.

## 4. The commander and the coalition roster

4.1 **Commander screen.** Nation Philippines, the Philippine flag as the navy
emblem, the rank ladder with Commodore selected, a name from the Spanish name
pool. *Wrong:* the screen refuses the nation or shows no emblem.

4.2 **The discount.** Philippine hulls are 20% cheaper; Thai, Australian and
MSC units are at their listed price. The two Euromod frigates declare
`Nation=philippines` (lower case) in their variants file; check that they
still get the discount.

## 5. Ayungin

5.1 Nothing fires at the boat. The first public build placed two Type 056A
corvettes (YJ-83) and a Type 054A at weapons Hold, and a player saw YJ-83s on
the boat within fifteen seconds: **Hold does not stop an AI ship firing.**
Since 6 Oct the cutters carry machine guns only and shadow north of the
boat's track, the watcher is an unarmed intelligence ship and the aircraft a
KJ-500. Check the cutters never close the boat; firing on any Chinese unit
still ends the mission.

## 6. The spotter drones (13 October)

Both drones are held back so the boats have no track in the first five
minutes (`Disabled=True`, switched on by a timed trigger, stock's own
pattern); the briefs say so.

6.1 **Service at Sea.** The Meridian spotter drone appears at about minute
5, not before, 27 NM from Sulu Provider, and the three boats (43 NM out)
do not fire on her before then. *Wrong:* missiles at the charter before
minute 5, or the drone never appears.

6.2 **Celebes Gate.** The spotter drone appears at about minute 5, 28 NM
from the frigate; Meridian Escort 18 (36 NM out) does not fire before
then. *Wrong:* rounds at the frigate before minute 5, or the drone never
appears.

## 7. A reveal at Classify and the Identify objective (21 October)

7.1 **Night Market, then The Okean.** Win Night Market (take the
semi-submersible), then fly The Okean. The PDEA intel line comes up and
the armed trawler Hai Xing 7 is on the plot classified from the start
(`SLNarcoTaken`). Say exactly what the **Identify** objective ("Classify
the armed trawler") does with a ship that starts classified: completes at
once, completes only after you classify her again, or never. The mission
is won by stopping her either way. This is one of the two in-pack proofs
(with Southern Reach card 3.10) that decide whether Red Line's RL03 reveal
after The Ships from the North comes back (Red Line card 7.4, held since
21 Oct 2026).

## 8. The fields and the coalition's helicopters (27 October)

Two corrections made by hand on the owner's PC on 27 Oct 2026, now made by
the builders (`sulu_line/`, and `CAMPAIGN_DECK_TYPES` in
`integration/cross-deck/build_pack.py`). Nothing in this section has been
seen in the game from a built pack. Test each step from a fresh load: a new
campaign, a campaign save taken at a Task Force window, or a mission loaded
from the browser. A mid-mission save keeps the aircraft it stored and shows
the old state.

The fields. Every Philippine field (Puerto Princesa, Zamboanga, Sanga-Sanga)
was written without a `CustomAirGroup`, and a field without one gets its
unit file's air group: the stock `airfield_small_1`'s F-4D/Es, RA-5Cs,
EA-6Bs, an E-3A, P-3Cs, SH-3Hs and CH-46s, free. Each now carries
`CustomAirGroup=True` and nothing else.

The decks. The coalition's helicopters could not use the decks they are
sold with: the Jose Rizal and Miguel Malvar files list only a Korean Super
Lynx, the Naresuan's no Seahawk and no H-76, Tarlac's no Seahawk, and the
Anzac's no H-76. SEST Cross-Deck now adds these as campaign fits, through
the same Anchor Chain `#!extend` stubs as Southern Watch card 6J, which
nobody has yet shown the game reads. Steps 8.2 and 8.3 are that proof for
this campaign, and their result answers 6J too.

8.1 **Empty fields.** Fly The Island Road and look at Puerto Princesa
(Antonio Bautista Air Base): it holds the aircraft you bought for it and the
mission's own flights, and nothing else. Do the same at Zamboanga in Fire
Mission Jolo and at Sanga-Sanga in Night Market. *Wrong:* any F-4, RA-5C,
EA-6B, E-3A, P-3C, SH-3H or CH-46 on a Philippine field - the field's
`CustomAirGroup=True` was not honoured; note the field and the mission.

8.2 **The H-76 on the frigates.** Start a new *Sulu Line*. In the window
before The Island Road buy a Jose Rizal or a Miguel Malvar and the H-76, and
assign the H-76 to the frigate in the Task Force Manager. (Or, in the
mission editor, load *Sulu Line 01 - The Island Road* from the browser and
give the Jose Rizal-class frigate already there an H-76.) *Expect:* the
assignment is accepted, and the helicopter launches from and recovers to
the frigate. *Wrong:* refused - the game ignores an `AircraftSupported` set
through `#!extend`; bring back Player.log and the `pn_ffg-150` and
`pn_ffg-06` lines of the pack's `CROSS-DECK.txt`.

8.3 **The coalition's decks.** At the window before Service at Sea, which
sells the Thai detachment, the Anzac and their helicopters, check four
pairings in the Task Force Manager: a Thai Seahawk and an MH-60R on HTMS
Naresuan; a Thai Seahawk and an MH-60R on BRP Tarlac; an H-76 on the Anzac.
(In the mission editor: *Sulu Line 04 - Service at Sea* from the browser,
with the ships placed by hand.) *Expect:* each is accepted, launches and
recovers. *Wrong:* note which pairing is refused, and bring the
`CROSS-DECK.txt` line for that ship.

8.4 **The placed H-76 and its home.** In the seven core missions the H-76
flight that starts in the air (Ship's Flight) has had no `HomeBase` in its
mission file since 27 Oct: the frigate's deck now takes it, and in a
Generated mission the builder never names a player ship as home (Southern
Watch's Rig Seventeen died loading when it did). It is still charged fuel.
In The Island Road fly it until it is low. *Expect:* it recovers and
refuels on the frigate or at Puerto Princesa, and its search-and-rescue
tasking does not report "no home base". *Wrong:* it will not land anywhere,
or SAR reports no home base - report it; the fallback is a builder option
that homes it on the field. (Night Market and The Okean are launched as
authored and still home it on Sanga-Sanga.)

8.5 **The AW109E.** The H-76 is offered first as the mod's Squadron2,
*AW109E LAH* (its AW109 livery on the H-76 model), then as the AUH-76
(Squadron1), and every mission that places an H-76 places the AW109E.
*Expect:* the AW109E livery. *Wrong:* a white or missing texture - the
Luzon Line's `aircraft/helo/phl_sh-2f_tx.png` is not reaching the game (the
repo's copy of the mod has no textures to check it against).

8.6 **The RAN MH-60R on sale.** It is sold with the Anzac and nowhere else:
before Service at Sea and before The Aborlan Battery, not before The Island
Road or Fire Mission Jolo, at 35 points with either RAN squadron (816 or
808). The Ship's Flight row in Air Tasking now also offers its
`ASWLongRange`, `ASWHunter` and `SEST_REDBACK` fits. *Wrong:* the MH-60R on
sale before Service at Sea, or a row with no loadout it can fly.
