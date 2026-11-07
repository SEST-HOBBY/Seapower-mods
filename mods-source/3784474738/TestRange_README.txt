Test Range 0.2.3

Use
1. Enable AC Pack and Test Range in the AC Pack settings menu, then restart Sea Power.
2. Select the defending unit. Open F10 > Missile Test. Test Range is the default view.
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
- The Test Range and native views are isolated, including native-view diagnostic controls.
  Native missile test switches to the original Missile Test view. Stop any running
  native test before starting Test Range; the native test changes global debug overrides.

ExtendedGuidance diagnostics
Each Test Range salvo automatically enables EG scenario recording before any
missile is spawned. ExtendedGuidance must be enabled and its diagnostic hooks
initialized; an unavailable recorder or known file error prevents the test start.
An already running recording is kept without clearing or restarting its session.
Recording continues after the salvo; the native-view recording button can stop it.
Every new Test Range salvo enables it again; pending launches also re-enable it.
This does not start the native Missile Test or change its combat overrides.
EG writes Mods/ExtendedGuidance/Diagnostics/missile-test.log under the game's
persistent data folder. TEST_RANGE_START includes the salvo and Test Range log
path; the Test Range log records EG_DIAGNOSTICS. Both logs remain in English.
EG keeps its existing asynchronous writer, rotation and sampling/rate limits.

Results and automatic logging
Results / Log opens a separate movable window. It opens automatically on test start.
Results are grouped and sorted by missile ID: Launched, Hit, Miss, Flying, Incomplete.
A hit means the native blast handler accepted a hit on the selected target. It does
not guarantee damage or a kill. Multiple hit callbacks count once. Hitting another
object is not a selected-target hit. Mission exit, clock reset or target respawn
ends unfinished observations as Incomplete, not as Miss. Directly spawned test
missiles are counted; separate submunitions/daughter weapons are not included.

Miss details show known native destruction evidence (interception, water collision,
maximum travel distance, target-loss self-destruct) or explicitly unknown cause.
Each missile retains its last THREE DISTINCT OBSERVED SEEKER STATES with mission
second timestamps: active mode, seeker mode, locked target/countermeasure, target
loss and jamming deviation. Sampling occurs after native
missile fixed updates and before destruction. Transitions within a single native
update may not be observable. These observations are not proof of miss causation.

Defending launchers report actual end-of-update stages, native abort messages and
native sensor engagement issues for tracked test missiles. Examples include
TargetIsNotDetectableByFCR and TargetIsNotDetectableBySearchSensor. Warming up,
alignment and reload delays are waiting states, not proven permanent failures.
Diagnostics observe native decisions without rerunning target/radar checks. A
weapon that never enters engagement may provide no specific abort reason.
Repeated equal observations are counted and reported at most every 5 mission
seconds; observation counts are NOT numbers of attempted missile launches.

An English .log is opened automatically before the first salvo, including UTC
and mission-time timestamps. File: Unity persistentDataPath/Mods/TestRange/Logs/
TestRange-<UTC timestamp>-<id>.log. The full path is shown in the Results window
and announced in Player.log. Detailed results live in this separate TestRange log.
No manual logging switch is required. A write failure is shown and prevents further
spawns. Events are flushed immediately. Results remain visible after the mission.
New result log is available once no test missiles remain under observation.
A log holds up to 4096 shots; a new salvo exceeding that limit is refused.

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

