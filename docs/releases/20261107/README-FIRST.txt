MODERN NAVAL OPERATIONS - OWNER'S PC WALKTHROUGH
R16 - 25 November 2026 - Workshop data from the 24 Nov 23:53 capture
Game target: Sea Power 0.9.3 Build 261123 public beta. Dynamic Campaign Mod 1.0.2.
Do not run Upload-PC.cmd. This is a PC test build, not a posting.

WHAT IS NEW IN R16
- Built for game Build 261123 (R15 switched its code off on this build).
- Dynamic Campaign Mod 1.0.2 runs on 261123 through a SEST bridge: the campaign
  map, side colours and drawings work; old or uncertain contacts are no longer
  drawn faded; east-west ring and ruler figures shrink with latitude, as on the
  game's own campaign map.
- GCO is the world campaign (Global Command Operations), open from 72S to 81N.
- Ice: one edge (10 %) for drawing and slowing; separate floes below about 60 %;
  ships slow and make ice effects only where the hull meets drawn ice; a Sea ice
  layer on the battle map; polar frame from 85 degrees; Okhotsk, Bering and
  Chukchi seasons.
- Local weather follows the camera in every campaign battle, GCO included.
- SEST's loader starts RAN Echidna and Ghost Shark code without R.A.T.S. Keel,
  loads one Sensor View copy only, and adapts Enhanced Decoy, Multi-Stage
  Missiles, J-36 systems, Osprey, Z-21, Better Tac Map and the Jiutian UAV.
- 117 new reviewed photographs in the encyclopedia and gallery.

1. PREPARE YOUR PC
a. Close Sea Power. Let Steam finish all downloads.
b. Extract the R16 toolkit ZIP into a fresh folder in Downloads.
c. Double-click Prepare-PC.cmd in that folder. Look for "VERIFIED: all 4935 canonical upload files match the release manifest."
   If it asks for a menu probe: start Sea Power, wait ten seconds at the main menu, quit, run Prepare-PC.cmd again.
   If it stops on an author update or a DLL change, keep the message and send it; do not work around it.
d. With the game closed, run "SETUP - double-click me.cmd" in the subscribed item:
   C:\Program Files (x86)\Steam\steamapps\workshop\content\1286220\3812461539
   Look for "All done". Save the wording of any [!!] line.
e. Keep every Required Item subscribed, including R.A.T.S. Keel (3835527459), both
   Sensor View items (3822119548, 3838468198) and Sensor View - ExtendedGuidance support
   (3838469336). SETUP checks LOAD-ORDER.txt and stops if one of them is missing.

2. START CHECK
Start Sea Power to the main menu, then quit. The BepInEx log should show
"Sea Power 0.9.3-261123 verified (ea653e49)" and "ADAPTED DynamicCampaignMod ... side-colour=8, terrain-background=1".
Step 6 collects the logs.

3. CAMPAIGN AND BATTLE FLOW (any campaign battle)
P1 The clock does not run while the preparation checklist is open.
P2 After Start preparation it stays paused until you start it.
P3 Your own units show on the map from the first paused moment.
G1 Start a fresh "Global Command Operations (GCO)" world. The map draws, side colours are right,
   F11 opens. Draw a ring and a ruler, save, reload: they come back.
G2 An old world from R15 (use a copy) loads with its forces and date.
R  Red Line ribbons: checks R5 and R6 cover the debrief awards; R1 to R4 need R16 and are run from
   docs/campaigns/red-line/test-card.md in the release checkout.

4. ICE (Polar North, Polar South, or GPT's MNO Ice scenarios if still installed)
I1 In patchy ice (about 20-50 %) you see separate floes, not large sheets.
I2 Sail between floes: full speed, no grinding. Sail into a floe: it slows and grinds.
I3 A ship's channel pushes small floes aside; the rest of the area does not redraw.
I4 Battle map Layers: "Sea ice" shows fill, ice edge and heavy-pack lines under the units.
I5 Heavy pack (over 60 %): as before (matt, closed, submarine held).
I6 MNO Ice 04 (87N): the ice appears once the mission has loaded; the date is 10 April, not 1 January.

5. WEATHER AND MODS
W1 In a GCO battle near bad weather, attach the camera to a ship for a few minutes of game time:
   the sea state and rain follow the campaign weather and change as the weather moves.
W2 An aircraft view above 1,500 m does not change the sea state below it.
M1 In the editor, place RAN Echidna and Ghost Shark: both show English names; Echidna's mast
   power and Ghost Shark's tube launch work in a scenario.
M2 Sensor View opens with its key and works once (no doubled overlay).
M3 Better Tac Map, Enhanced Decoy chaff, a multi-stage missile, an Osprey and the Jiutian UAV
   each work in a quick scenario.
   Enhanced Decoy: the BepInEx log shows "Enabled v0.5.4" and no "Initialization rolled back".
   Try a ship with chaff and flares twice, Realistic Countermeasures off and then on.
   Off: a chaff order fires the mod's chaff salvo and the order log says chaff is out; chaff
   also goes out on its own against an incoming radar missile, and the missile is drawn off.
   On: a chaff order still follows the mod (salvo and range limits) and fires chaff only, no
   flares; a flare order fires flares as without the mod; release on its own is the game's,
   without the mod's limits, and a ship with air decoys may not release flares on its own
   against an infrared missile. In both: note any air decoy that vanishes while still
   falling, or a late swarm decoy that stays up after it should have reached the sea.
M4 The encyclopedia shows the new photos (for example K9 Thunder, 2S43 Malva, NSM).

6. COLLECT
Quit Sea Power. Run R16\Capture-Repair-Results.cmd from this toolkit. Send the ZIP it names in
Downloads, with your notes against P1-P3, G1-G2, I1-I6, W1-W2 and M1-M4 (pass, fail or not tried).

7. DEFAULT-BRANCH CAPTURE (once, when convenient)
The default branch is Sea Power 0.9.3 Build 261116 public release, a different file from the betas.
R16 stays off on it. To let MNO support it: in Steam, Sea Power > Properties > Betas > None; let it
update; run the reference capture (tools\capture-beta-references.ps1 in your clone); set the beta back.

This toolkit's branch, feature/mno-r16, is in the included Git bundle. The source receipt identifies the exact revision. If Git specifically reports a missing prerequisite and your previous PC checkout is available, open PowerShell and run:
  git -C "$env:USERPROFILE\Seapower-mods" fetch origin feature/mno-r16
Then run Prepare-PC.cmd again.
