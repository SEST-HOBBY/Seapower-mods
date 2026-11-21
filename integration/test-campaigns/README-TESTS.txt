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
- Sea ice: the campaign mod itself has none (no ice on its map, in its
  routes or in its speeds). In the game itself, ice is a fixed map that only
  adds to sonar ocean noise. SEST's runtime (SeaIce=1 under [Runtime], on
  when the line is missing) adds seasonal ice INSIDE battles: visible pack
  ice, ships slowed or stopped, submarines held under heavy ice, and ice
  noise on sonar, all from the same climatology for the battle's place and
  date. Section 4 tests it with the polar campaigns. CampaignIce=1 (on when
  the line is missing) adds the same ice to the CAMPAIGN MAP: drawn on the
  globe with an ice-edge line, in the map readout, and slowing surface
  groups in it (submarines pass under). Routes are NOT changed yet: a route
  still runs through the pack and the group crawls there. Section 5.

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
   A Norwegian frigate in the marginal ice (N1, 73.5N 36E), the submarine
   Kobben under the pack 66 nm north (N4, 74.6N 36E), frigates off Bear
   Island (N2, 74N 19.5E) and in the ice-free Norwegian Sea (N3, 67N 6E);
   Russian frigates close on N1/N4 and N2 from open water. Group N5, a
   frigate off the eastern Murman coast (69.5N 40E, 4 % ice), and Red N3, a
   picket deep in the eastern Barents pack (72.5N 49E, 88 %), are section
   5's transit test; they start 235+ nm from every Russian or Norwegian
   group and 239+ nm from where Red N1 and Red N2 make contact, so they
   neither make a contact of their own nor join those battles.
   Check: the map draws to 81N, ships move and route, a contact battle loads,
   the coast and terrain look right. In the battle note Ocean Noise from the
   weather panel. Look for any ice, speed limit or other ice effect (N1-N6).

3. POLAR SOUTH, ANTARCTIC PENINSULA (about 30 min)
   "SEST Test: Polar South (Antarctic Peninsula)". 12 January 2029, southern
   summer. A Chilean frigate in the Bransfield Strait (62.9S 58.6W), a
   British frigate in the western Weddell pack (S2, 67.2S 49W), HMS Astute
   under it 48 nm south (S4, 68S 49W), a Drake Passage control (57.3S 64W).
   Russian frigates from a test port at Bellingshausen Station close on S1
   and on S2/S4. Group S5, a frigate south-east of Elephant Island (62.5S
   52W, 2 %), and Red S3, a picket in the south-western Weddell pack (67.75S
   58W, 79 %), are section 5's transit test; they start 204+ nm from every
   other group and 230+ nm from where Red S1 and Red S2 make contact.
   Check: the map draws to 72S, ships route around the Peninsula, a battle
   at 63S or 68S loads with the Antarctic coast, Ocean Noise, and any ice
   effect (S1-S6).

4. ICE IN BATTLE (about 75 min; sections 2 and 3's campaigns)
   Before starting the game add under [Runtime] in the SEST runtime pack's
   plugins\sest_runtime.ini:  SeaIceDiagnostics=1  (SeaIce=1 is the default).
   Expected ice (the runtime's own model; make_test_campaigns.py prints it):
     North, 10 Mar (12 Mar):  N1 frigate 50 % (51 %)   restricted, 0.4 x speed
                              N4 Kobben  75 % (75 %)   heavy: held under the ice
                              N2 Bear Island 13 %      caution, 0.7 x speed
                              N3 control  0 %          open water
                              Red N1 starts at 9 % and patrols into 46 %
     South, 12 Jan (14 Jan):  S2 frigate 58 % (49 %)   restricted, 0.4 x speed
                              S4 Astute  75 % (67 %)   heavy: held under the ice
                              S1 Bransfield 3 %, S3 Drake 0 %: open water
     The ice retreats fast in January: fight the southern contact early.
   a. North: time-compress until Red N1 makes contact with N1/N4 (one battle:
      the groups are 66 nm apart). Play battle.
   b. I1 VISIBLE ICE. Look at N1 from above (external camera, about 200 m
      up, then 2-5 km up): white-grey pack ice with dark leads and holes, to
      the horizon, thickening toward the north; it must not move when you
      pan or when the camera jumps between units. Screenshot both heights.
      Then look south toward Red N1's open water: the ice edge, then sea.
      Jump the camera to a unit 30+ km away and back: the ice around the
      camera must be back within about a second (nearest first), with no
      open-water holes meanwhile. Time-compress across midnight with the
      camera over the pack: the sheet must not blink out (old chunks stay
      drawn until the new date's chunks are ready).
   c. I2 UNDER THE ICE. Select the Kobben, go to its periscope/underwater
      view (or an external camera under water): the ice underside overhead,
      with light through the leads. Screenshot. If the battle has a high sea
      state (5+), check again: the underside must still be under water
      (the lift is capped at 1 m, the underside stays 1 m below the sea).
   d. I3 SHIP SPEED. Order N1 to flank ahead (north, into heavier ice): the
      message "In ice (50 %, restricted): speed limited to N kn" (0.4 x its
      top speed) or, past 60 %, "Held by pack ice (NN %): heavier ice ahead,
      steerage way only (N kn); back out or turn toward open water": it
      slows to 0.1 x its top speed but never stops, so it can still turn.
      Order astern: it backs at 0.4 x ("working out of the ice") whatever the
      ice astern. Turn it south (toward lighter ice): 0.4 x ahead again.
      Note the speeds. N1 must never be dead in the water.
   e. I4 SUBMARINE HOLD. Kobben: order Surface, then periscope depth, then
      snorkel, then raise the periscope/ESM mast. Each is refused ("Order
      refused: ice overhead (75 %)... the order is kept for open water",
      "Mast stays down..."); the depth readout stays at or below 98 ft.
      Lowering any mast still works. Then hold the manual pitch-up and
      blow-ballast keys for 30 s: one message "Manual depth control
      overridden: ice overhead..." (not a stream) and the boat does not rise
      above 98 ft.
   f. I5 LEADS. Move the Kobben slowly (5 kn) under the pack until the
      message stops (a lead: the log says "released (NN %, in a lead)") or
      drive it south into ice under 60 % (N1's area): Surface must then work.
      A boat ordered to periscope depth under the ice goes to periscope depth
      by itself once released ("ordered depth NN ft given back" in the log).
      An AI diesel boat that starts snorkelling under the pack waits
      ("snorkelling state waits under the ice") and snorkels once in open
      water; it must not stay at 98 ft with the snorkel down.
   g. I6 OCEAN NOISE. Select N1, then the Kobben, then (South) S3: note
      Ocean Noise in the weather/sensor panel: higher in heavier ice, the
      native value in open water.
   h. I7 OPEN WATER. In a battle at N3 (or S3) there is no ice, no speed
      message and Surface works.
   i. South: the same at S2/S4 (I8-I10), early on 12 January.
   j. I11 FRAME RATE. Note the FPS with the camera over the pack and over
      open water (or compare with SeaIceSheet=0). Send the "sea ice
      visuals" lines.
   k. I12 SHELVES/COAST. Note whether the battle map shows the Antarctic
      coast or shelves as land near S2/S4 and send the "terrain ... ft" in
      the "sea ice @" line for a unit there.
   l. I13 MATT ICE, NO MIRROR. Look at the pack around N1 from 200 m, from
      2-5 km and fully zoomed out, at day and (time-compress) at dusk/night:
      it must read like snow-covered land or a ship's deck, white-grey and
      matt, darker at night, a little blue on the shaded side, fading into
      the fog/haze toward the horizon; no mirror-like sky reflection, no
      sparkle, no glow against the sky when zoomed out. Screenshots at each
      height, one at night. Send the "sea ice material: ..." line (shader,
      smoothness, metallic, keywords, "matt True", scene fog/ambient). If it
      is too bright or dark set SeaIceAlbedo=0.7 (0.5-0.95) and note the value
      you like; SeaIceSmoothness=0.05 makes it even flatter.
   m. I14 SOLID SLABS. From a low external camera (10-30 m up) look along the
      ice edge and into leads, near and 5-20 km away: each floe a solid slab
      with white-grey sides, no sea surface visible between the ice top and
      its underside, no see-through gaps where chunks meet. Repeat at a high
      sea state if the battle has one. Then set SeaIceOceanClip=0, restart,
      and look again at the same place: if waves now poke through the ice top
      near the camera that were hidden before, the clip works (say so). Under
      water (the Kobben's view) the underside must still be there.
      Screenshots. Send the "slabs closed ...; ocean clip overlays <n> (...
      HasClipOverlay True, Ocean.clipOverlaySize ...)" part of the "sea ice
      visuals" line.
   n. I15 CHANNEL. Order N1 north at full ahead into the pack for 5 minutes
      (it slows; that is the speed rule), then look behind it from above:
      an open-water channel about 1.5 x its beam wide with ragged edges,
      following its track. Screenshot. Order a second ship (or N1 after a
      U-turn, once 2 minutes have passed) to follow in the channel: it must
      be faster than in the pack beside it (the "sea ice speed" line shows
      "(channel: 50 % x (1 - 0.8 x openness 1.00))"). Time-compress 45 min:
      the channel narrows in steps and closes. Pan away 30+ km and back, and
      let the game recentre (long camera moves): the channel stays where it
      was. Then at 100x and 1000x compression for a few minutes: the channel
      still refreezes in 45 min of GAME time (at 1000x about 3 s), and a ship
      keeps carving a continuous channel (no gaps) at those rates. A ship
      stuck in heavy pack inside a half-refrozen channel, ordered toward
      lighter ice, must still make about 0.4 x flank ("escaping"), not
      steerage way. Send the "sea ice channels: ..." lines.
   o. I16 BREAKING PIECES. Watch N1's bow from close (100-300 m) while it
      breaks ice: small white floe pieces pushed out from the bow, sliding
      aft along the hull, tumbling slightly, drifting and sinking into the
      channel edges within half a minute. Stop the ship: no new pieces. In
      open water (N3): none. With several ships breaking ice, the ship the
      camera is on keeps its pieces (they settle, not pop); ships 3 km or
      more from the camera throw none. Screenshot. Send the "sea ice effects:
      bow pieces <n> alive of cap 120 ..." line.
   p. I17 SOUND. With the camera near N1 while it breaks ice: a low grinding
      rush at the bow (the game's hull-wash sound pitched down) rising with
      speed; NO crack or explosion sound (there is no crack clip by default);
      silence when it stops or leaves the ice; nothing from a distant ship.
      Time-compress above 2x: the grinding fades out; back at 1x-2x it
      returns. Note whether it sounds like ice. Send the "sea ice breaking
      sounds: loop clip ... loaded, crack clip none ..." line and the
      "sounds ..." part of the "sea ice effects" line. SeaIceSoundClip=<audio
      resource> tries another loop; SeaIceCrackClip=<resource> adds cracks
      (real-time rate limit, only at 1x or slower) if you have a clip that
      does not sound like a hit.
   q. I18 SONAR NOISE. From the Kobben's passive sonar (or another ship's),
      note N1's contact while it breaks ice and when it stops: it must be
      heard farther / stronger while breaking (up to 8 dB louder) in every
      ASW realism setting. The "sea ice channels" line counts "breaking noise
      added to passive target levels <n> times" (must be above 0 while a
      sonar listens to N1) and "to interferer levels <n> times" (above 0 only
      with the most detailed ASW simulation).
   r. I19 UNDER THE PACK. With the Kobben held under solid pack, look from
      the external camera under water: the underwater look (fog, colour,
      the underside of the ice) must stay on while the camera is under solid
      ice, not switch to the above-water look until a lead. Frame rate in a
      polar battle with several ships must not drop compared with
      SeaIceOceanClip=0.
   Player.log lines (with SeaIceDiagnostics=1):
     [SEST Runtime] sea ice installed (ocean noise, ship speed, submarines): ...
     [SEST Runtime] sea ice sheet driver installed (...); Ceto: ...
     [SEST Runtime] sea ice visuals: sheet; shader Legacy Shaders/Diffuse; Ceto:
       ...; ocean clip: bound (...)   (or the shader that loaded; "floes (no
       shader)" means the fallback ran)
     [SEST Runtime] sea ice material: shader <name> (render queue <n>), colour
       0.84/0.86/0.88 (albedo 0.80 ...), smoothness <n or n/a (Lambert, no
       specular)>, metallic <n>, keywords [...], emission off, reflection
       probes off ...; matt True; scene fog ..., ambient ..., sun ...
     [SEST Runtime] sea ice effects: bow pieces on, cap 120; breaking sounds
       bound (...); loop clip 'audio/ships/Ship-Flow', crack clip '(none)';
       channels on
     [SEST Runtime] sea ice: battle frame at 74.0, 36.0; date 2028-03-10 ...
     [SEST Runtime] sea ice noise scale: native environment map maximum blue
       <n> -> <dB> at 98 %
     [SEST Runtime] sea ice noise: first getFloeIce at ...: native <a>, model
       <c> % -> <b>
     [SEST Runtime] sea ice @ 2028-03-10 09:12: <unit> at <lat, lon>: ice 50 %,
       ocean noise <n>, floe ice term <n>, access(none) Restricted, terrain
       <n> ft[, submarine submerged <n> ft, HELD under ice]; last 10 s: speed
       caps <n>, depth clamps <n>, orders clamped <n>, blows refused <n>,
       masts refused <n>, keeping targets clamped <n>, rises stopped <n>,
       manual control overridden <n>, orders given back <n>, snorkel states
       held <n>, ...   (every 10 s)
     [SEST Runtime] sea ice speed: <ship> at ... ice 50 % (model 50 %) lightest
       ahead 55 % class none state Restricted capped 28.0 -> 11.2 kn (flank
       28.0)   (", escaping" or ", steerage way" when blocked)
     [SEST Runtime] sea ice submarine: <boat> held at ... ice 75 %; depth <n>
       ft, ordered <n> ft -> 98 ft
     [SEST Runtime] sea ice visuals (sheet): camera at ... ice 50 %; chunks
       <n> drawn (<n> visible), <n> stale kept until covered, <n> retired,
       <n> empty, <n> building, <n> queued, <n> triangles; <n> built in <ms>
       ms each (thread pool), <n> uploads <ms> ms avg, worst <ms> ms (main
       thread); lift <m> m (cap 1.0), surface units <n>, Ceto wave at camera
       <m> m; floes 0; slabs closed (near 2.0 m, far 3.5 m thick, far lift
       <m> m); ocean clip overlays <n> (bound ...; <n> created, <n> killed,
       Ceto OverlayManager.HasClipOverlay True, Ocean.clipOverlaySize <SIZE>);
       channel chunks <n> at 64 cells, <n> rebuilt in the last 10 s, ...
     [SEST Runtime] sea ice material in use: shader <name> ...   (each report)
     [SEST Runtime] sea ice channels: <n> segments in <n> carve cells (250 m)
       over <n> chunks, <n> tracks; last 10 s <n> points added; <n> refrozen
       and <n> dropped (cap 4096) this battle; <n> snapshots published (last:
       <n> chunks rebuilt, <n> shared); <n> chunks waiting to rebuild;
       refreeze 45 min of game time (clock GameTime.missionElapsedTime,
       compression <n>x); speed eased by a channel <n> times; ships breaking
       ice <n>; breaking noise added to passive target levels <n> times, to
       interferer levels <n> times
     [SEST Runtime] sea ice effects: bow pieces <n> alive of cap 120 (<n>
       spawned, <n> recycled while full, <n> not spawned for a nearer ship's,
       this battle); sounds bound (...); <n> loops playing (<n> started, <n>
       on the ship's mixer group), cracks 0 played, 0 held back by the rate
       limit, <n> frames muted by time compression above 2x, this battle;
       loop clip 'audio/ships/Ship-Flow', crack clip none
     [SEST Runtime] sea ice breaking sounds: loop clip 'audio/ships/Ship-Flow'
       loaded, crack clip none (SeaIceCrackClip empty, the default)
       ("NOT FOUND" names the option to set)
   Send I1-I19 with the screenshots and those lines. If waves show through
   the ice, note the sea state: the lift is capped at 1 m above the sea so
   the underside stays under water (SeaIceSheetLiftM=0..1 changes it inside
   that cap). Near a ship the ice top must not stand above its waterline;
   note any ship that looks buried in the ice.

5. CAMPAIGN MAP ICE (about 40 min; sections 2 and 3's campaigns)
   On by default (CampaignIce=1 under [Runtime]). For the log lines add
   CampaignIceDiagnostics=1 under [Runtime] in plugins\sest_runtime.ini
   (optional). CampaignIceMap=0 or CampaignIceMovement=0 turn one part off.
   What you should see (the runtime's own model; make_test_campaigns.py
   prints it as the "ICE edge in view" and "ICE transit" lines):
   - The ice is drawn ON THE GLOBE, the campaign mod's own map: pale
     white-blue fill whose opacity follows the concentration (faint at the
     edge, nearly opaque in the close pack), a crisp CYAN line on the ice
     edge (15 %) and a NAVY line where the heavy pack starts (60 %, where
     ships of ice class "none" are beset). Only over water.
   - With the weather layer OFF the ice is drawn alone. With it ON, the ice
     and both lines are drawn over every weather layer (wind, sea state,
     rain, clouds, fog, storms), and the forecast slider shows the ice of the
     shown day.
   - North, 10 March 2028: the edge crosses 36E at about 71.7N, 30E at
     72.5N, 25E at 73.2N (in view at the start); the navy line is at about
     73.9N on 36E; the Norwegian Sea (67N 6E) is open. The White Sea and the
     Gulf of Bothnia also show ice. Time compression: the edge on 36E is at
     about 72.3N on 10 April, 73.7N on 10 May, 75.7N on 10 June, 78.8N on
     10 July (the overlay is rebuilt the day the date changes; one step a
     day at most, many days unchanged in March).
   - South, 12 January 2029: the edge at about 64.4S on 55W and 65.0S on
     49W, the navy line at about 66.6S on 55W; the Bransfield Strait and the
     Drake Passage open. It retreats: 64.8S on the 14th, 65.3S on the 26th,
     66.2S on 10 February (on 55W).
   - Hover (weather layer ON; the campaign mod shows its readout only then):
     over water in the ice the readout ends with e.g.
       Ice 62 % (heavy pack)
       Surface groups 10 % speed (beset); submarines pass under
     at 74N 36E on 10 March; "pack ice" from 15 %, "drift ice" under 15 %
     (no speed line under 10 %); nothing on land or in open water.
   - Movement: a surface group cannot go faster than a factor of its FULL
     speed (what its slowest ship makes at the telegraph setting, with
     damage and fuel), set by the ice at its position for the slowest
     surface ship's ice class (every ship is class "none" today): 1.0 under
     10 %, 0.7 from 10 %, 0.4 from 30 %, 0.1 (beset, never 0) from 60 %. A
     group ordered slower than that ceiling keeps its ordered speed; one
     ordered faster is held at the ceiling, and its speed text reads
     "NN kn (ice)" instead of "(heavy seas)" (in the fleet list an
     out-of-fuel group reads "(out of fuel, ice)"). A group of only
     submarines keeps its speed; one surface ship with them sets the pace.
     The cap is on DCM's own WeatherKnots (not saved), so the ETA, the AI's
     closing times (which assume full speed up to the cap) and the movement
     all follow it. In DCM's Cheats panel, "weather" off hides the ice too.
   a. C1. Start "SEST Test: Polar North (Barents)". In the log: "campaign
      ice installed: map (...); movement (...)".
   b. C2. Weather layer off: screenshot the globe at the start view (73N
      25E) and zoomed in on 36E: fill, cyan edge, navy heavy line. Log:
      "campaign ice map: overlay for 20280310: ... built in N ms off the
      main thread" and "campaign ice map: sea ice draped on the globe with
      the weather layer off (...)". If you use the campaign mod's Cheats
      panel: its "weather" entry off hides the ice too (log: "... weather
      overlay is hidden (Cheats: weather); the sea ice is hidden with it"),
      and on again brings it back.
   c. C3. Weather layer on: step through every layer; screenshot two. The
      ice must be on each, the same as with the layer off (at the weather
      image's coarser 0.25-degree cells). Log: "campaign ice map: weather
      frame 2028-03-10 08Z composited with sea ice (N ice pixels; frame 1)".
   d. C4. Hover over 74N 36E, then 72N 36E (about 19 %: "pack ice",
      "Surface groups 70 % speed"), then 67N 6E (no ice line). Paste them.
   e. C6. Select Group N5 and order it to Red N3 (72.5N 49E, 252 nm
      away). Note its speed text and ETA as it goes: full speed for
      about 49 nm (to about 70.1N 41.7E, 10 %), then 0.7 of its speed
      "(ice)" (the 15 % edge at about 70.3N 42.5E), then 0.4 from about
      114 nm (70.8N 44E, 30 %). About 152 nm out (71.3N 45.4E, 49 %) N5 is
      100 nm from Red N3 and Dynamic Campaign Mod opens the contact: that
      ends the transit after about 38 nm at 0.4 (the beset 0.1 stage, past
      60 % at about 71.6N 46E, is C7's N1). The "ICE transit" line of
      make_test_campaigns.py lists the ice every 19 nm: 4, 6, 8, 12, 17, 24,
      32, 42, 52, 62, 71, 78, 84, 88 %, and "ICE transit reach" where 0.4
      starts and the contact comes. With CampaignIceDiagnostics=1 the log has
      "campaign ice @ <time>: Group N5 ... at <lat, lon>: ice NN % (...),
      factor 0.7, full speed NN kn, ordered NN kn, weather cap ... -> NN kn
      (ice)" once per hour (an order to full speed shows the cap).
      The route itself does not bend around the ice (not in this version).
   f. C7. Order the Kobben (N4) across the pack (e.g. to 76N 40E): its own
      speed, no "(ice)". Order N1 (73.5N 36E, 50 %) north: 0.4, then beset
      (0.1) past 60 %; it still moves.
   g. C5. Time-compress to 10 May (or drag the forecast slider): the edge on
      36E moves north to about 73.7N. Screenshots before and after, and the
      day it first moved (the overlay line in the log names the date).
   h. C8. "SEST Test: Polar South": the edge at about 64.4S on 55W is in
      view at the start (62S 55W); S5 to Red S3 (67.75S 58W, 350 nm) as C6:
      full speed for about 103 nm (to 64.0S 53.8W), 0.7 from there (the
      15 % edge at about 64.5S 54.3W), 0.4 from about 192 nm (65.4S 55.3W,
      30 %), and the contact about 251 nm out (66.3S 56.3W, 51 %), after
      about 60 nm at 0.4. Ice every 19 nm: 2, 3, 4, 5, 7, 9, 12, 16, 21, 26,
      32, 38, 45, 52, 58, 64, 70, 75, 79 %. Time-compress a week: the edge
      retreats south.
   i. C9. Hormuz campaign: no ice, nothing changed on the map or in speeds.
   j. C10. Note any stutter when the date changes. Send the "campaign ice"
      lines (INSTALL-TEST-CAMPAIGNS.ps1 -Collect puts them in
      storms-log.txt) and any "campaign ice ... unavailable" or "stopped"
      line: it names the part that switched itself off.
   Not in this version: routes that avoid the pack, an "Ice" entry in the
   campaign mod's layer list or legend, and the readout with the weather
   layer off.

COLLECT AND REMOVE (game closed)
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Collect
It makes Downloads\SEST-TestCampaigns-results-<time>.zip (logs, the
"world storms" and "campaign ice" log lines in storms-log.txt, local
weather lines included,
and every battle file written since install) and a RESULTS.txt next to it
with lines H1-H11, D1-D13, L1-L9, N1-N6, S1-S6, C1-C10 (add I1-I19 from
section 4).
Fill that in or reply with the lines. Then:
  powershell -ExecutionPolicy Bypass -File .\INSTALL-TEST-CAMPAIGNS.ps1 -Uninstall

If a campaign is missing from the menu, search Sea Power\BepInEx\
LogOutput.log for "Skipping campaign" and send that line.

Source: integration/test-campaigns/make_test_campaigns.py (rebuilds the
three campaign.json files from the world campaign, writes the Hormuz
sest-weather.json with tools/make_sest_weather.py, and checks them).
