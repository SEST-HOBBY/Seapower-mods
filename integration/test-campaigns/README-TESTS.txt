SEST TEST CAMPAIGNS: WEATHER HAND-OFF, PLACED STORM, LOCAL BATTLE WEATHER AND POLAR PROBES (21 Nov 2026)

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
- The game holds ONE weather state per battle, sampled where and when the
  contact happens. SEST's local battle weather (LocalWeatherView=1 under
  [Runtime], on when the line is missing) changes that state while you play,
  in battles of a campaign with placed storms only: sea state, wind, rain,
  thunder, snow and fog follow the ship the camera is attached to (or the
  free camera), a few seconds after you move it. It is still one state:
  every ship, sensor and the campaign mod's battle AI use the weather of
  where you look. Clouds stay the battle's own. Groups A, B and C are
  350-700 nm apart so each is its own contact (the mod merges surface groups
  within 200 nm in open sea, 150 nm near a coast, into one battle); Groups D
  and E are placed to be pulled into ONE battle (1h below).
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
   h. LOCAL BATTLE WEATHER: ONE BATTLE, TWO WEATHERS (L1-L9; about 30 min).
      Groups D and E sit south-east of Group C in the open Arabian Sea:
      Group D, DDG-105 Dewey, at 20.55N 64.77E; Group E, DDG-106 Stockdale,
      at 21.3N 67.2E, 144 nm east-north-east of D. Red D (two Alvand
      frigates) starts at 23.6N 66.6E and comes south. At 15 Jan 08:00Z
      (4 h after the start) DARYA is at 20.67N 64.07E, 78 kn: Group D is
      40 nm from its centre, inside the gale ring (about 120 nm); Group E is
      180 nm off, outside it. Expected from the campaign mod's own model
      (approximate: it draws new background weather for each new campaign):
        Group D: sea state 8-9, rain and thunder, wind about 60 kn
                 (sea state 7+ in 57 of 60 campaign draws);
        Group E: sea state 2-5, no rain (5 or less in 45 of 60 draws).
      This holds from about 07:00Z to 10:00Z (D stays 33-57 nm from the
      centre, E 175 nm or more).
      Before starting the game, add WorldStormsDiagnostics=1 under [Runtime]
      for the view lines (optional; the feature works without it).
      1. Start a NEW "SEST Test: Hormuz Weather Split" campaign (this test
         wants the start at 04:00Z). Keep Group C clear of Groups D and E;
         if Red C makes contact with Group C first, fight or resolve it as
         usual (its battle is more than 200 nm from D and E).
      2. Time-compress. Red D should reach about 100 nm from Group E (the
         contact range) a few hours in. If no contact by about 07:30Z,
         order Group E north towards Red D. Note the contact time (L1).
      3. On the contact screen both DDG-105 Dewey (Group D) and DDG-106
         Stockdale (Group E) must be in the battle (L2). If only one is, the
         battle point was too far from the other: note the time and the
         ships listed.
      4. Play battle. Unpause when ready (world battles start paused).
         Player.log shows "world storms local weather: battle <id> at ...:
         view weather on; baseline SS..., clouds held at ..." (L3). The
         battle's own weather is the campaign mod's at the contact point
         (near E): expect about sea state 3, broken cloud, no rain.
      5. Select DDG-105 Dewey (Group D) and attach the camera to it (the
         usual unit view). Wait about 10 s. The sea should rise to sea state
         8-9 (big waves), rain falls and lightning flashes; the weather panel
         reads the new sea state. Player.log: "world storms local weather:
         applied sea state 3 -> 9 (setSeaState), wind ... , rain on, thunder
         on at view unit ... DDG-105 ..." (L4). Screenshot.
      6. Jump to DDG-106 Stockdale (Group E). Within about 10-30 s the sea
         drops to about sea state 3 and the rain and lightning stop (the sea
         state changes at most once per 25 s, rain/thunder/fog at most once
         per 20 s, and only after the camera has stayed 5 s). Player.log:
         "applied sea state 9 -> 3 ..., rain off, thunder off at view unit
         ... DDG-106 ..." (L5). Screenshot.
      7. Jump back and forth a few times, waiting 30 s each time: each ship
         shows its own weather every time (L6). Jumping faster than every
         5 s changes nothing (by design).
      8. Free camera: detach and fly from E towards D (or use the map to
         move the camera). Half-way the weather starts to build; over D it
         is the storm (L7). Clouds do not change anywhere (they stay the
         battle's own: by design in this version).
      9. With the camera on D (storm showing), save the game (any save).
         Player.log: "world storms local weather: save: the battle's own
         weather written (SS3 ...), not the view's (SS9 ...)"; the storm
         stays on screen (L8). Optional (not tested off the PC): quit and
         load that save; say whether it loads with the battle's own weather
         (about sea state 3) and whether the view follows the camera again.
      10. End the battle and return to the map. Player.log: "world storms
         local weather: battle <id> (the battle ended): baseline restored
         ..." (or "its scene is gone, nothing to restore") (L9).
      With diagnostics on, every 10 s: "world storms local weather: view
      <unit ...|camera> <lat lon> (<east> nm E, <north> nm N of the battle
      centre), battle <UTC> (sampled <hh:mm>Z, 10-minute steps from the
      contact time): DCM SeaState=... WindFrom=...
      Weather=... Clouds=... storm Cyclone DARYA; target ...; applied ...;
      baseline ...; held ..." (send a few of these with any failure).
      In a battle of a campaign WITHOUT placed storms (Polar North, or any
      other campaign) the log says "world storms local weather: battle <id>:
      the campaign has no placed storms (sest-weather.json); the battle
      keeps its own weather" and nothing changes. A Dynamic Campaign Mod
      Battle AI test (the mod's test menu) run in this campaign keeps the
      test's own fixed weather (scattered cloud, sea state 2): the log says
      "world storms local weather: battle <id>: a Dynamic Campaign Mod Battle
      AI test battle (BattlePlan.TestBattle) ...; the battle keeps its own
      weather" (optional; say if you ran one). Any other battle whose written
      weather is not the campaign model's own logs "... its written weather
      is not the campaign model's own at the Engagement point and time
      (...)" and keeps it: send that line. LocalWeatherView=0 under
      [Runtime] turns the feature off; "world storms local weather
      unavailable" or "... stopped" means it is off for the session: send
      that line.
      If D and E read alike in the battle (both calm or both stormy), the
      campaign mod drew unusual background weather: start a new campaign and
      try again (up to three times; say how many).
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
"world storms" log lines in storms-log.txt, local weather lines included,
and every battle file written since install) and a RESULTS.txt next to it
with lines H1-H11, D1-D13, L1-L9, N1-N6, S1-S6. Fill that in or reply with the lines. Then:
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Uninstall

If a campaign is missing from the menu, search Sea Power\BepInEx\
LogOutput.log for "Skipping campaign" and send that line.

Source: integration/test-campaigns/make_test_campaigns.py (rebuilds the
three campaign.json files from the world campaign, writes the Hormuz
sest-weather.json with tools/make_sest_weather.py, and checks them).
