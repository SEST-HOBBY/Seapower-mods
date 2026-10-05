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
minutes" message appears and the charter steers north. Sink her in a second
run: The Aborlan Battery then opens **without** her at the anchorage.

## 3. Fire missions

3.1 **Jolo.** The five positions are on the Patikul ridge, ashore. A frigate
inside about eight miles can reach them with the 76 mm; three destroyed ends
the mission as a victory.

3.2 **Aborlan.** The two Silkworm launchers fire at ships inside about
twenty-five miles, including the convoy at the Narra anchorage. Both
destroyed ends the mission.

## 4. The commander and the coalition roster

4.1 **Commander screen.** Nation Philippines, the Philippine flag as the navy
emblem, the rank ladder with Commodore selected, a name from the Spanish name
pool. *Wrong:* the screen refuses the nation or shows no emblem.

4.2 **The discount.** Philippine hulls are 20% cheaper; Thai, Australian and
MSC units are at their listed price. The two Euromod frigates declare
`Nation=philippines` (lower case) in their variants file; check that they
still get the discount.

## 5. Ayungin

5.1 Nothing fires: the coast guard cutters, the militia trawlers, the PLAN
frigate and the Y-8 stay at Hold all mission. Firing on any of them ends it.
