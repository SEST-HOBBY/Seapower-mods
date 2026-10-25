Test Range 0.1.3

Use
1. Enable AC Pack and Test Range in the AC Pack settings menu, then restart Sea Power.
2. Select the defending unit. Open F10 > Spawn > Test Range | Missile Test.
3. Click Nation to open the nation list. Click Missile to open the filtered missile list.
   Both lists have a search field. All nations includes every loaded missile entry.
4. Select range, salvo size, launch interval, altitude and missile taskforce.
5. Open Defense weapons to select individual ammunition types, or All / Only CIWS /
   Only SAMs / None. Click Done, then Start missile test.

Controls
- Spawn distance: 4, 10, 20, 40, 80, 160 or 300 nautical miles from the selected target.
- Salvo size: 1-128. Quick buttons: 1, 4, 8, 16 and 32.
- Launch mode: simultaneous or staggered. Intervals: 0.5, 1, 2, 3 or 5 mission seconds.
- Spawn altitude: 30, 100, 1000 or 10000 feet.
- Missile side: Enemy, Player or Neutral. Choose a side hostile to the defending unit.
- Cancel salvo cancels pending launches only.
- Reset filters removes all current test-defense restrictions, including flying salvos.
- Respawn selected unit reloads the selected ship, submarine, aircraft, helicopter or
  land unit with its current loadout. Pending launches against it are cancelled;
  choose defense weapons again for the replacement. Existing missiles stay in flight.
- Missile Trails toggles the native global weapon-trail display (also used by the
  original F10 Weapon Trails control). It does not enable Weapon Test Mode.
- Back to Spawn returns to the original spawn controls.

Defense filter
Choices are copied when starting a salvo. They apply only to the selected defending
unit engaging that salvo's directly spawned missiles. Other units and other targets retain normal weapon behavior. Chaff and ECM use the separate Countermeasures controls. Ammunition selection applies to every
mount using that ammunition. CIWS means the game's CIWS weapon systems; SAMs means
missile ammunition configured for air targets. The game still decides when permitted
weapons can fire. Keep the native Spawn tab's Unit Defence setting ON for defense tests.
Selections do not rewrite ship data, ammunition inventories or saved weapon settings.

Countermeasures
Open Countermeasures beside Defense weapons. Chaff / Decoys blocks new launches
from the selected unit's chaff systems, including EnhancedDecoy air decoys (Nulka).
ECM / Jamming blocks that unit's native defensive jamming and noise-jamming effects.
These are live unit-wide restrictions against ALL threats, unlike the salvo-only
weapon filter. Selecting another unit or finishing/cancelling a salvo does not
release them. Allow all restores this unit; Reset filters restores all units.
Respawn and mission exit also release restrictions. No inventory, sensor settings
or saved unit data are changed. Existing decoys, their independent jammers and
previous missile deflections are not undone. Disable before launching a fresh test.

Timing and limitations
Pausing holds pending launches. Time compression uses mission time. Staggered mode
launches at most one missile per rendered update; very high time compression can
therefore extend the requested spacing instead of releasing a catch-up burst.
The target and geographical launch point are captured at salvo start. Closing F10
or selecting another unit does not redirect the salvo. Target destruction, scene
unload or mission-clock rollback cancels pending launches. Tests/filters are not saved.

These are native debug missile spawns already in flight, with ship-like timing.
They do not create a physical launch ship or its launcher/guidance context. Launcher-
dependent effects and submunition release may therefore be unavailable. Separate
child weapons are outside this filter. Missile fuel, range, seeker and target-type
limits still apply; a 300 nm spawn does not grant a short-range weapon 300 nm range.
Nation groups follow ammunition filename prefixes used by the game; unknown mod
prefixes appear as Other (prefix). Only currently loaded ammunition definitions appear.

Submod switch
File: Unity persistentDataPath/Mods/ACPack/submods.ini
[Submods]
euromod.test-range=false
Values: true / false. Default: true. Changes require a full game restart.
The parent AC Pack selection in Mod Manager must also be enabled.

