# Follow-up to the 19 October playtest

Base: `e7b32f11a906418b6e1343beff31b867d8dd7557`, the user's last Steam
upload and PC install (4,084 deployed files). Changes are on
`fix/playtest-20261019`; the existing deployment branch is preserved.

| Report | Change | What still needs the game |
|---|---|---|
| Cannot select a ship during initial aircraft preparation | Removed the automatic `Action_PrepareFlightDeck` pause. Authors can request it with `initial_deck_prep=True`. Native Task Force **Prepare Airbase** remains enabled under the existing rules. | A selectable ship-deck planner in the Task Force screen is **unfinished**. No exposed campaign key implements it. It needs a game UI change or a separately developed and tested plugin. |
| Seahawk pods float without their supporting arm | US and RAN MH-60R fits keep `H60_Pylon114` visible and use the lower missile seats. Both S-70B-2 fits use their single modelled Penguin arm, with one 19-round pod. Torpedo-specific offsets no longer position the S-70's pods. | Check clearance in the loadout preview and after takeoff. The config identifies the supporting meshes; it does not provide a rendered model preview here. |
| AGR-30 needs more loft, a six-second motor and slow cruise | Retains the donor APKWS model, pod compatibility, warhead and air/sea/land target classes. New profile below. | Timing, actual flight path, in-flight retargeting and moving-target hit rate need measurement in Sea Power. |
| Weather Alternate vessels beach | Both coasters and the raiders now use the passage east of Kai Kecil, with formation spacing reduced from 1.5 to 0.3 NM to fit the channel. The coasters have explicit routes ending at a real anchorage approach, with stop orders. Town moved onto firm ground. | Watch a complete convoy transit and ensure the game's coastline agrees with the source map. |
| The Open Door carrier is inland | Moved from `-4.3133,135.8867` to `-2.8,135.8`, in Cenderawasih Bay, over eight NM off the source coastline. The mission now uses coastline validation. | Confirm the carrier spawns at sea and the Growler can recover. |
| Langgur supplies F-4s and EA-6s | Every named Langgur strip explicitly has an empty custom resident air group. The modern aircraft already supplied airborne by each mission retain their recovery field. The scenery no longer imports the vanilla air wing. | Recover and relaunch the mission aircraft. No extra reserve aircraft were added. |
| Some placement boxes do not move support units | Existing deliberate restriction retained: generated missions allow deployment of the purchased task force and assigned Air Tasking flights. Supplied convoys, support units and bases retain their authored positions. | This is expected; it does not mean the mission has failed to recognise an allocated unit. |

## AGR-30 candidate profile

This remains a fictional game weapon. The previous `VelocityBleed=0.4`
configuration did not establish a 600-knot cruise: velocity bleed is a
lifetime-dependent kinematics factor, not a cruise-speed command.

| Purpose | Configuration |
|---|---|
| Launch envelope | 30 NM; original 0.16 NM minimum retained |
| Climb | `MaxLoftAngle=35`, `MaxLoftAlt=6562` feet (approximately 2 km) |
| Phase speeds | `MaxLoftVelocity=450`, `MaxVelocity=150`, `ApplyKinematics=False` |
| Visible motor | Six-second timed sustainer effect, starting at launch; original continuous in-flight effect removed. Initial booster slot is effectively zero, following the stock AIM-54A effect arrangement. |
| Guidance | Active radar terminal seeker; radio midcourse correction; retargeting and target memory enabled |
| Seeker envelope | 35 NM active and passive range, 60-degree field of view, 120-degree gimbal |
| Terminal phase | Handoff and dive at 1 NM; retains `TerminalAlt=Maintain` |
| Reliability | Seeker reliability 0.99, hit probability 0.95; original small warhead retained |
| Endurance allowance | 1,500 seconds; a 30 NM flight at 150 knots takes 720 seconds before climb, manoeuvres and diversions |

These are supported INI fields found in the exported stock missiles. The
speed caps come from the stock SS-N-22's phase settings, the timed motor
effect arrangement from AIM-54A, and command retargeting from Walleye II.
They form a test candidate, not measured performance. A two-kilometre loft
is not a terrain-clearance guarantee, and 150-knot cruise cannot chase a
fast jet. Test ground installations, a crossing merchant ship and a slow
drone, then change targets after launch. Check motor extinction at six
seconds at 1x speed. Record actual cruise speed and altitude rather than
judging them from the nominal range or the encyclopedia.

## Geography regression

`CoastPlacer.route()` now checks every sailed leg, including the launch
position to the first waypoint. Quarter-NM sampling and a half-NM shore
margin reject tracks whose endpoints are both wet but whose passage cuts
an island. This exposed one additional Kai crossing: Ballistic Shield's
Tual ferry. Its route now follows the same passage and exits south of Kai.
Home Waters' expedition ship also clipped the Fiordland shore; it now
stands west of Puysegur before turning north toward Milford.

The committed Natural Earth extracts and the land mask establish positions
against real coastlines. They do not establish depth or exact agreement
with the game's terrain. Standalone and campaign copies, including Open
Allocation, are regenerated from the same source.

The official [Task Force Mode campaign guide](https://steamcommunity.com/sharedfiles/filedetails/?id=3756769210)
documents land-based Airbase Prep, generated/replaced deployment and Air
Tasking. It does not expose a ship-deck preparation picker. This patch does
not claim to add one.

## Acceptance before a Workshop update

Use the prebuilt consolidated pack from the fix branch. Start fresh copies
of **Weather Alternate** and **The Open Door**; already-generated campaign
missions or saved battles can retain the old geometry and air groups.

1. Weather Alternate: both merchants sail through the passage into the
   anchorage without intervention. Raiders and fishing boat stay at sea.
2. The Open Door: carrier is afloat; Langgur has no inherited F-4/EA-6 wing;
   the F-35s can recover there.
3. Seahawk loadout previews: arm remains visible, pods attach cleanly,
   and the S-70B-2 has one pod on its modelled missile arm.
4. AGR-30: check 6-second flame, loft, cruise speed, long-range moving
   targets and retargeting. Check for freezes with both pod sizes.
5. Native airbase preparation still opens from Task Force planning; no
   automatic preparation modal interrupts mission launch.

Validation results are included in the downloadable package. The fix branch
is saved locally and supplied as a Git bundle; it has not been published to
GitHub. None of the game checks above has been performed in this environment.
Publishing to the existing Steam item remains the owner's Mod Manager step.
