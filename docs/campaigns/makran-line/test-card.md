# Makran Line — first play test

Nothing in this campaign has been run in the game. The builder has checked
every unit, variant, position, objective, trigger and price (the dry run,
`check_campaign_coverage.py`, preflight, `check_scenarios.py` and the
campaign tests pass), but the campaign rests on game behaviour nobody has
watched yet. This card lists those claims, riskiest first, and what "wrong"
looks like for each.

Report back with the step number and what you saw. A step that fails stops
that column, not the whole card.

## 1. The campaign, the commander and the roster

1.1 **The campaign is listed.** The Campaigns menu has a fifth entry, *Makran
Line - The Fuel Road (Pakistan Navy)*, and the mission browser a *Makran
Line* folder with four missions. *Wrong:* either is missing.

1.2 **The commander screen.** Start *Makran Line* on **Standard**. The Service
Record offers **Pakistan** only. The screen shows the Pakistan Navy, the
flag of Pakistan as its emblem, rank **Commodore** and the default name
*Kamran Aziz Durrani* (editable). Rank pictures are blank on purpose. Note
how the abbreviations read (CDRE and the others are unverified). *Wrong:* the
screen refuses the nation, shows a broken image, or will not continue.

1.3 **The opening window.** The builder offers the Tughril class (four
hulls), PNS Alamgir, the Z-9CE and the Sea King, and nothing else: no
JF-17, no ZDK-03, no submarine, no second Tughril class from SEST
Replenishment. Each class shows the same-nation discount. *Wrong:* a JF-17
on sale here, or a class at full price.

1.4 **The Z-9CE lands.** In The Fuel Road the Z-9CE flight takes off from and
lands on a Tughril, and on the Alamgir if you bought her (SEST Cross-Deck's
campaign fit); the Sea King lands on the Alamgir. Load *Makran Line 01 - The
Fuel Road* from the mission browser as well: the Tughril's own air group is
empty (the mission clears it), so her one deck slot is free for the Z-9CE.
*Wrong:* a helicopter that cannot land, one sent to PAF Base Masroor with a
frigate in reach, or a PLAN Z-9F (China flag) in the Tughril's hangar.

1.5 **Free rearm.** Fire some rounds in The Fuel Road and win. Before Gwadar
Roads the frigates show the green "Rearmed" icon and full magazines. The
rules page says "Rearm: free at every force allocation". *Wrong:* rounds
missing at Gwadar Roads.

1.6 **Masroor and Gwadar are empty fields.** PAF Base Masroor (MK01, MK04)
and the old Gwadar airfield (MK02, *Gwadar airfield (old airport)*) hold only
the aircraft you assigned: no stock F-4s, E-3A or P-3Cs. *Wrong:* any
aircraft you did not buy.

1.7 **The briefing banners.** Only The Gwadar Roads banner is a Pakistani
photo (a JF-17). The other three are another navy's ship or helicopter of the
same class or family, and each caption says "family reference". *Wrong:* a
caption that presents a PLAN or US Navy photo as a Pakistani unit.

## 2. The Fuel Road and Gwadar Roads

2.1 **Flags.** Every Meridian boat and ship is on the Meridian side and shows
"Meridian Maritime Group" and the Meridian flag on its unit panel and its
contact (map) marker, never the USSR's, Russia's, Iran's, the UK's or
France's. Two of the armed Okean's liveries register the UK and France, and
the mission's `Nation=Meridian` overrides them. *Wrong:* any other flag icon,
a missing flag icon, or a nation name other than Meridian on the panel or
contact of a Meridian unit. The flag on the 3D model's mast, and its funnel
markings, belong to the hull file and are not part of this check: a Red
Ensign and UK funnel on one Okean, a French flag on the other, a Soviet
merchant flag on the Poltava and the ro-ro, an Australian merchant flag on
the ACT-1, a Norwegian flag on the side trawler. SEST ships no Meridian mast
flag.

2.2 **MK01's release term.** The mission is won when both tankers are inside
the six-mile circle off the Karachi pilot station; the *Progress: FirstIn*
line comes when the first is. *Wrong:* a win with one tanker in, or none
when both are.

2.3 **MK02's armed freighter fires.** MV Sea Venture, anchored among the
merchants, sails in her StyxCarrier fit (eight SS-N-2 containers; the
Default fit carries only machine guns) and launches an SS-N-2 at the first
tanker at minute 14 and at the second at minute 32 (her `Attack=` orders). Report whether each launch
happens, whether the tanker survives a hit, and whether the 054A/P's HQ-16
engages the missile. *Wrong:* no launch at all (a scripted order is not a
shot until it is seen).

2.4 **MK02's shore units.** The HQ-16AE site and the C-602 battery at Gwadar
start at Hold, on land, and can be released and fired. *Wrong:* a unit in
the sea or one that cannot be set to Free.

2.5 **MK02's release term.** The mission ends when the three trawlers and the
armed freighter are sunk, not before. *Launcher* is listed as "Also
required" and flagged Main in the objectives list.

2.6 **The Okeans' guns.** The Meridian Okeans in MK01, MK02 and MK04 carry
the 40 mm Bofors (their Bofors fit), as the MK01 brief says, not the ZU-23.
*Wrong:* a twin 23 mm mount and no Bofors on an Okean.

## 3. Hangor

3.1 **The boat.** PNS Hangor (S-131) starts dived below the layer at weapons
Hold; there is no force allocation. *Wrong:* the task group's ships appear.

3.2 **The classification stage.** Classify MV Meridian Sentinel on passive
sonar. The "SONAR / HANGOR: Contact classified" line comes, and only after
it does taking the boat into the three-mile circle on the trail datum win.
Enter the circle first and wait: the win must come when she is classified.

3.3 **Unseen.** Surface or close a trawler until it classifies the boat: the
mission ends as a failure. Note whether the armed trawlers' and the
merchant's sensors classify a dived S-26P at all.

3.4 **Restraint.** Sinking any ship ends the operation as a failure. A
torpedo that misses, or only damages, ends nothing: no stock trigger reacts
to a launch. *Wrong:* a launch alone ending the mission, or a sinking that
does not.

## 4. Port Qasim

4.1 **The heave-to.** With the screen's lead ship at **Hold**, close Meridian
Sentinel on her track south of the delta. Within about three miles she must
change to a neutral symbol, take the new waypoint to the Karachi roads and
slow to telegraph 2, and a BRIDGE intel line says so. The ship's flight
alone must not do it. Note the range. Sinking her afterwards must end the
mission with "had hove to and was under escort when she was sunk". The
*Progress: Running* report must not appear after she has turned.

4.2 **Sunk instead.** In a second run, sink her from beyond three miles, then
sail the lead ship through the water she passed: no heave-to line may come,
and the mission must still be won once two tankers are in the anchorage
circle with nothing inbound.

4.3 **She clears to sea.** In a third run, leave her alone: when she enters
the four-mile circle south of the delta the "cleared the delta" message
comes and *Mothership* fails.

4.4 **Her speed.** At telegraph 3 in sea state 3, measure her knots and the
minute she reaches that circle. The challenge chain runs along her route to
it, so her speed decides whether the lead ship can catch her on it.

4.5 **The datum from Hangor.** Win Hangor, then fly Port Qasim: Meridian
Sentinel's position is on the plot for fifteen minutes, with the FLEET
OPERATIONS line. Without Hangor won, no datum. *Wrong:* a datum either way,
or never.

4.6 **Main flags.** *Mothership* (MK04) and *Launcher* (MK02) are second Main
objectives; they must change only the objectives list and the debrief, not
the win or the loss.

4.7 **Ships after a loss.** In one run let a trawler sink one tanker and
bring the other two in: the mission is won, and the debrief shows *Lose none
of the three tankers* **Failed** (-30), not Complete. *Wrong:* Ships
Complete after a tanker was lost.

4.8 **The ribbons.** Complete Gwadar Roads, Hangor and Port Qasim: the Arabian
Sea Security Ribbon, the Trailing Operations Ribbon and the Makran Line
Service Ribbon appear in the Service Record, each with its mission's date.
No real Pakistani award is granted.

## 5. Trigger shapes with no exact stock line

Port Qasim writes the same pieces as Red Line's The Order to Withdraw, and
the same two combinations have no exact stock line: two area tests in one
trigger (each *Challenge HeaveTo N*) and AND NOT on a loss (the HoveTo path
waits for her afloat). 4.1 and 4.2 cover both; Red Line's test card, checks
P3, P4 and P7, are the same checks on its coaster.
