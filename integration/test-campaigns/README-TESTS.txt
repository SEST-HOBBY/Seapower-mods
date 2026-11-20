SEST TEST CAMPAIGNS: WEATHER HAND-OFF AND POLAR PROBES (20 Nov 2026)

Three small Dynamic Campaign Mod 1.0.0 campaigns for PC testing. They are
tests, not campaigns to play: fog of war is off and the forces are small.
They install into the game's user folder, not the Workshop item, and remove
cleanly. They need the R15 toolkit installed (Dynamic Campaign Mod 1.0.0 on).

WHAT THEY CAN AND CANNOT SHOW (from the game and campaign mod code)
- The campaign mod cannot be told to put a storm somewhere: its campaign
  file has no storm or fixed-weather setting, and every new campaign draws
  new weather. Weather differences between places come from its weather
  model; a storm or low appears only when the model makes one.
- Each battle gets ONE weather for the whole battle, sampled where and when
  the contact happens. Different weather for different ships means separate
  contacts, so the groups are 350-700 nm apart (the mod merges groups within
  about 200 nm into one battle).
- Sea ice: the campaign mod has none. In the game, ice is a fixed map that
  only adds to sonar ocean noise; there is no visible ice and no effect on
  movement. The polar campaigns test the map, routing and battles at high
  latitude, which the Antarctic and Arctic regions will need.

INSTALL (game closed)
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1
If the game is not in the default Steam folder add:
  -GameDir "D:\SteamLibrary\steamapps\common\Sea Power"

1. HORMUZ WEATHER SPLIT (about 45 min)
   Campaign menu: "SEST Test: Hormuz Weather Split". 15 January 2028.
   Group A destroyer in the northern Gulf (27.9N 50.3E), Group B just east of
   the Strait of Hormuz (26.0N 56.7E), Group C in the Arabian Sea (22.4N
   61.8E). An Iranian flotilla starts about 120 nm from each.
   a. Turn on the weather layer. Hover over each group and note wind, sea
      state, cloud and rain (H2-H4). Note any storm or low drawn (H5).
      Screenshot the map with the weather layer.
   b. Time-compress. If the flotillas do not close on their own, order a
      blue group toward its flotilla. Keep the blue groups apart.
   c. At each contact: note the group and time, hover the map at that spot,
      then choose Play battle. In the battle note cloud, rain/fog/thunder and
      sea state. End the battle and return (H6-H10).
   d. Note the campaign time before and after one battle (H11).
   If A, B and C read almost the same, start a new campaign (new weather
   draw); try up to three times and say how many.

2. POLAR NORTH, BARENTS SEA (about 30 min)
   "SEST Test: Polar North (Barents)". 10 March 2028, winter ice maximum.
   Norwegian frigates at the ice edge (76.8N 36E), off Bear Island (74N
   19.5E) and in the ice-free Norwegian Sea (67N 6E); Russian frigates close
   on the first two.
   Check: the map draws to 81N, ships move and route, a contact battle loads,
   the coast and terrain look right. In the battle note Ocean Noise from the
   weather panel. Look for any ice, speed limit or other ice effect (N1-N6).

3. POLAR SOUTH, ANTARCTIC PENINSULA (about 30 min)
   "SEST Test: Polar South (Antarctic Peninsula)". 12 January 2029, southern
   summer. A Chilean frigate in the Bransfield Strait (62.9S 58.6W), a
   British frigate at the Weddell Sea ice edge (68S 42W), a Drake Passage
   control (57.3S 64W). Russian frigates from a test port at Bellingshausen
   Station close on the first two.
   Check: the map draws to 72S, ships route around the Peninsula, a battle
   at 63S or 68S loads with the Antarctic coast, Ocean Noise, and any ice
   effect (S1-S6).

COLLECT AND REMOVE (game closed)
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Collect
It makes Downloads\SEST-TestCampaigns-results-<time>.zip (logs and every
battle file written since install) and a RESULTS.txt next to it with lines
H1-H11, N1-N6, S1-S6. Fill that in or reply with the lines. Then:
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Uninstall

If a campaign is missing from the menu, search Sea Power\BepInEx\
LogOutput.log for "Skipping campaign" and send that line.

Source: integration/test-campaigns/make_test_campaigns.py (rebuilds the
three campaign.json files from the world campaign and checks them).
