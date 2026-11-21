SEST TEST CAMPAIGNS: WEATHER HAND-OFF, PLACED STORM AND POLAR PROBES (20 Nov 2026)

Three small Dynamic Campaign Mod 1.0.1 campaigns for PC testing. They are
tests, not campaigns to play: fog of war is off and the forces are small.
They install into the game's user folder, not the Workshop item, and remove
cleanly. They need the R15 toolkit installed (Dynamic Campaign Mod 1.0.1 on).

WHAT THEY CAN AND CANNOT SHOW (from the game and campaign mod code)
- The campaign mod itself cannot be told to put a storm somewhere: its
  campaign file has no storm or fixed-weather setting, and every new
  campaign draws new weather. SEST's runtime adds one: a campaign folder
  that holds sest-weather.json beside campaign.json gets that file's storms
  inside the campaign mod's own weather model (WorldStorms=1 under [Runtime]
  in the SEST runtime pack's plugins\sest_runtime.ini; on when the line is
  missing). The Hormuz campaign carries one, Cyclone DARYA. Everything else
  in the weather is still the campaign mod's own draw. There are no
  fixed-weather zones yet.
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

1. HORMUZ WEATHER SPLIT AND CYCLONE DARYA (about 60 min)
   Campaign menu: "SEST Test: Hormuz Weather Split". 15 January 2028 04:00Z.
   Group A destroyer in the northern Gulf (27.9N 50.3E), Group B just east of
   the Strait of Hormuz (26.0N 56.7E), Group C in the Arabian Sea (22.4N
   61.8E). An Iranian flotilla starts about 120 nm from each.
   Before starting the game, for the log lines: add WorldStormsDiagnostics=1
   under [Runtime] in the SEST runtime pack's plugins\sest_runtime.ini
   (optional; the storm works without it).
   The placed storm, Cyclone DARYA (all times UTC, campaign time):
   - 15 Jan 04:00 (start): about 20.1N 64.5E, south-east of Group C, about
     70 kn ("Cyclone (category 1)" on its card, "Cyclone DARYA" on the map
     and the contact screen). Group C is about 200 nm off: background
     weather, rising.
   - 15 Jan 18:00 (about 14 h in): passes about 35 nm east of Group C at
     about 88 kn (category 2). Group C should read sea state 9, about
     55-95 kn (strongest on the storm's east side), storm label
     "Cyclone DARYA".
   - 16 Jan 16:00 (about 36 h in): passes about 20 nm east of Group B,
     coming up the channel between Musandam and the Iranian coast, at about
     65 kn. Group B should read sea state 9.
   - then turns west through the Strait of Hormuz, south of Qeshm, and
     weakens over the Gulf ("Tropical storm DARYA" under 64 kn, "Tropical
     depression DARYA" under 34 kn); it ends on 17 Jan 18:00 at 26.25N
     53.2E, about 185 nm short of Group A, which keeps the campaign mod's
     own background weather throughout.
   The whole track is over water: the eye never crosses Oman or Iran (the
   builder checks every point and segment against the land mask).
   DARYA's eye is calm in the campaign mod's model (wind falls towards zero
   inside about 20-24 nm of the centre); the strongest ring is 20-50 nm out, and
   gale-force wind reaches about 100-150 nm.
   a. Turn on the weather layer. Hover over each group and note wind, sea
      state, cloud and rain (H2-H4). Note any storm or low drawn (H5).
      DARYA must be drawn south-east of Group C with its past track,
      forecast points and cone, and listed in the storm list (D2, D3).
      Screenshot the map with the weather layer.
   b. Time-compress. If the flotillas do not close on their own, order a
      blue group toward its flotilla. Keep the blue groups apart.
   c. At each contact: note the group and time, hover the map at that spot,
      then choose Play battle. In the battle note cloud, rain/fog/thunder and
      sea state. End the battle and return (H6-H10).
      Try to fight one contact at Group C while DARYA is within about 120 nm
      (15 Jan 12:00 to 16 Jan 00:00): the contact screen should show the
      storm, and the battle high sea state with rain and thunder (D5).
   d. Note the campaign time before and after one battle (H11).
   e. Hover Group C about 14 h in, Group B about 36 h in, Group A as DARYA
      dies (D4, D6, D7).
   f. Save, quit to the menu, load the save: DARYA must be at the same place
      (D8). Then start "SEST Test: Polar North" in the same game session: no
      DARYA there (D9).
   g. THE WEATHER LAYER IN A BATTLE (D10-D13). Take a contact into a battle
      while DARYA is within a few hundred nm (best: Group C between 15 Jan
      12:00 and 16 Jan 00:00, or Group B between 16 Jan 10:00 and 22:00).
      In the battle open the tactical map, open its Layers menu (the same
      menu where Topographic Map adds "Topography (heights and depths)") and
      find "Weather (storms, gale rings, forecast track)" (D10). It starts
      on; tick it on if it is off. You should see:
      - a white square at DARYA's centre with "Cyclone DARYA <wind> kn" and
        "gale <n> nm, core <n> nm" beside it;
      - the gale-force ring (yellow under 48 kn, orange 48-63 kn, red 64-95
        kn, magenta 96 kn and up) and a thin dashed white core ring (the
        radius of maximum wind, about 20 nm);
      - a dashed white track ahead with small squares labelled +1 h, +3 h,
        +6 h and +12 h (fewer near the storm's end, 17 Jan 18:00).
      Zoom out if DARYA is off screen. Screenshot it (D11). Time-compress
      for 30+ minutes of battle time: the centre, rings and labels move
      along the track (D12). Hover the map inside the gale ring: a readout
      with the label, the distance from the centre, inside or outside the
      gale ring and the motion ("moving NW 14 kn"); untick the layer and
      everything goes (D13). The campaign mod's own tropical storms and
      gales near the battle are drawn the same way.
   If A, B and C read almost the same away from DARYA, start a new campaign
   (new weather draw); try up to three times and say how many.
   With diagnostics on, Player.log (and the collected storms-log.txt) shows:
     [SEST Runtime] world storms installed: ...; diagnostics on
     [SEST Runtime] world storms: sidecar ...\sest-test-hormuz-weather\sest-weather.json:
       sest-darya Cyclone DARYA 2028-01-15 00:00Z to 2028-01-17 18:00Z, peak 90 kn
     [SEST Runtime] world storms: 1 storm(s) from ... tied to the weather model; ...
     [SEST Runtime] world storms: 2028-01-15 04:00Z sest-darya "Cyclone DARYA" at ...
       (one line per campaign hour while DARYA lives)
     [SEST Runtime] world storms: contact <id> at <lat lon> <time> battle
       [Environment]: SeaState=... Clouds=... WindDirection=... Weather=...
     [SEST Runtime] world storms map layer installed: a "Weather" entry ...
     [SEST Runtime] world storms map: layer "Weather (storms, gale rings,
       forecast track)" added to the tactical map's Layers menu (#610), on
       (at the first battle)
     [SEST Runtime] world storms map: drawing on the tactical map (host ...)
     [SEST Runtime] world storms map: weather model from the running campaign
     [SEST Runtime] world storms map: <n> redraw(s) in 10 s (...); battle
       2028-01-16 16:20Z at <lat lon>; 1 storm(s): sest-darya <lat lon>
       65 kn 21 nm off, gale <n> nm   (every 10 s while the layer is on)
   Without diagnostics only the "installed", "sidecar", "tied", "map layer
   installed" and "map: layer ... added" lines appear (the "tied" line
   again after a load or a battle return). A line "world storms
   unavailable; Dynamic Campaign Mod's own weather retained" means the
   storm is off for that session; "world storms map layer unavailable" or
   "... stopped" means only the battle-map layer is off: send either. If
   the layer is in the menu but nothing is drawn, send the lines starting
   "world storms map:" (with diagnostics on), especially "a rendered map
   with view model ... is not the tactical map". WorldStormsMapLayer=0
   under [Runtime] turns the layer off.

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
It makes Downloads\SEST-TestCampaigns-results-<time>.zip (logs, the
"world storms" log lines in storms-log.txt and every battle file written
since install) and a RESULTS.txt next to it with lines H1-H11, D1-D9,
N1-N6, S1-S6. Fill that in or reply with the lines. Then:
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Uninstall

If a campaign is missing from the menu, search Sea Power\BepInEx\
LogOutput.log for "Skipping campaign" and send that line.

Source: integration/test-campaigns/make_test_campaigns.py (rebuilds the
three campaign.json files from the world campaign, writes the Hormuz
sest-weather.json with tools/make_sest_weather.py, and checks them).
