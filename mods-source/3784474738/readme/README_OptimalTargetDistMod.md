# Optimal Target Distance

AnchorChain/Harmony DLL mod for Sea Power. It adds distance-based preference to the
existing automatic ammunition selection, independently configurable lower/upper
automatic target-altitude gates, and SystemGroup-based shared launch intervals.

## INI keys

Add the optional keys under the ammunition file's existing `[Guidance]` section:

```ini
OptimalTargetDist=60,180

MinAttackAltitude=15
MaxAttackAltitude=80000
AutoAttackBelowMinAltitude=True
AutoAttackAboveMaxAltitude=False
```

`OptimalTargetDist` accepts one nautical-mile value or a comma-separated minimum and
maximum. Reversed ranges are normalized; malformed values are ignored.

The split altitude values default independently to the existing
`AutoAttackOutsideAltitudes` value. If neither split key exists, the original game
path is left unchanged.

Distance preference is applied only after Sea Power's original automatic launcher,
range, guidance, FCR, arc, availability, and target checks have accepted a candidate.
When ammunition with and without the new distance key is mixed, the legacy result is
retained unless it also has the key and at least two valid configured candidates can
be meaningfully compared.

## Shared launch groups (1.1.0)

Add these keys to the ship's launcher `[WeaponSystemN]` sections:

```ini
[WeaponSystem4]
SystemName=eu_mk41_quad
SystemGroup=MK41_fwd
SharedLaunchInterval=1

[WeaponSystem5]
SystemName=eu_mk41
SystemGroup=MK41_fwd
SharedLaunchInterval=1

[WeaponSystem8]
SystemName=eu_mk41
SystemGroup=MK41_aft
SharedLaunchInterval=1
```

Within one ship, matching groups share the start timer even when SystemName differs.
Different groups are independent even when SystemName matches. The entire group
name is compared case-sensitively after trimming whitespace; underscores have no
special meaning. Ships never share timers with each other.

Without SystemGroup (or with an empty value), launchers retain name-based sharing
with other ungrouped launchers. Grouped and ungrouped launchers are independent.
At least one member must define SharedLaunchInterval, in seconds. Use the same value
on all members; if values differ, the largest non-negative finite value is used.

Only the native shared-timer key changes. FireRate, reloads, target acquisition,
CombatSystem/reaction delays, radar/guidance channels, sensor alignment and other
launch checks remain active. Existing salvo handling and SalvoFireTime are retained:
the native game skips the FireRate/shared-delay checks during a running salvo.

The supplied Mk41 definitions use FireRate=30 (two seconds per WeaponSystem),
PerContainerReload=True and ReloadTime=2 (seconds per cell). SharedLaunchInterval=1
adds a one-second minimum between ordinary launches across each configured bank;
other launch conditions can increase the actual interval.

Enable AC Pack and restart the game completely. This DLL respects the parent mod's
saved Mod Manager checkbox. Group timing requires AC Pack; without it, the game
uses its original name-based sharing. The runtime DLL belongs only in AC Pack.

Release/beta API and grouping behavior were checked offline against the installed
public assembly and available historical release/stable-beta fixtures. Gameplay
and save/load acceptance in the game are still pending.

## Ammunition copies and launcher diagnostics (1.1.2)

On builds that clone cached ammunition parameters, the clone retains the exact
master's optional distance and altitude policy. Constructor-based older builds
continue to use the original loading hook. No INI changes are required.

For an SM-6/SM-3 launch-abort investigation, create an empty file at
`%USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\Mods\OptimalTargetDist\launcher-diagnostics.enabled`
and fully restart the game. `[LauncherAbort]` lines record the native abort message,
launcher state, magazine/loaded counts and associated search-sensor status.
Messages are limited to one per launcher per real second. Remove the file and
restart to disable tracing. The trace changes no firing conditions or inventory.

## Target-aware loft optimization (1.2.0)

The existing ammunition switch also enables the incoming-missile correction:

```ini
[Guidance]
OptimizeLoftAlt=True
```

The current game defaults this switch to True. No additional key or DLL is needed.
False disables the correction. It applies to kinematic KappaLoft paths against
approaching missiles; aircraft and surface-target profiles retain native behavior.

When little time remains, the optimized loft peak is reduced using the target's
three-dimensional position and velocity, including its descent. Very urgent shots
use the game's linear path to the moving intercept point. TerminalApproachDist,
TerminalLoft, native target leading, speed limits and turn limits are retained.

This is a constant-velocity estimate, calculated when waypoints are created or
rebuilt. It is not continuously recomputed and cannot guarantee interception.
Range/launch checks and displayed trajectory estimates still use the existing
native or worker prediction model; this change adjusts the live missile path.

Numerical workers keep their existing snapshots and shared result caches. The
correction updates only this missile's waypoint settings on the main thread.
Older asynchronous game builds apply it after the native result is published.
There is no added per-frame simulation, polling, thread pool or worker dependency.

Fully exit and restart Sea Power after replacing the DLL. The same 1.2.0 binary was
checked offline against the installed public build and available historical
release/beta assemblies, including four-thread tests with the installed workers,
MultiStage API checks and MissileControl waypoint composition. In-game flight
acceptance remains pending.