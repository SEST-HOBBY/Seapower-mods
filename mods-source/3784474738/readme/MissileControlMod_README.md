# MissileControlMod 0.1.5

An opt-in AnchorChain module for short launch control, additional native maneuver authority, and directional control effects. The included PAC-3 MSE and base-game SA-N-9 overrides are **gameplay tuning examples**, not measured missile performance data.

## Configuration examples

The PAC-3 MSE and SA-N-9 package files are fixed regression examples from earlier releases. Live AC Pack tuning may differ. The 0.1.5 updater installs only the DLL, this README and the three reviewed Aster overrides; it preserves the current PAC-3 MSE and SA-N-9 files.

- `ammunition_overwrite/usn_pac3_mse_OVWR.ini`: PoweredTurnover follows the configured clearance distance and TurnoverRate toward the native flight path. Launch ControlEffects=All reuses the Maneuver_Nose definitions, including the four added diagonal mounts; they are eligible once visual Stage 2 begins. Only the nose jets visualize launch control. The existing motor thrust and plume timing remain active, with no StageExhaust deflection controller. Terminal control adds 10 G while its configured ActiveDuration allows it; -1 removes the time limit. The existing fins and stage settings are retained.
- `ammunition_overwrite/wp_sa-n-9_OVWR.ini`: retains the user's custom model, fins and tuning. Ejects at the configured EjectionSpeed, travels the configured clearance distance along the launch axis, tips toward the native flight path, brakes the turn with opposite jets within the configured angle window, then ignites and blends into normal flight. Keeps native TerminalLoft. Adds 5 G during the first 2 seconds of TerminalApproach while the motor burns.
- `effects/weapons/emitters/thrusters/control_thruster.ini`: the user's composite jet with flame, glow and smoke, emitting along its own positive Z axis. The available `control_thruster_pac3.ini` variant arranges multiple jets in a row; each nose definition's Effect key selects its resource.

Version 0.1.5 adds optional `InvertControl=False` to individual Thruster definitions. `True` reverses the automatic side selection without rotating or relocating the effect. The Aster 15, Aster 30 and Aster 30 Block 1 overrides enable it for their four Stage-2 maneuver jets. Their mounts (Z=0.001249) are behind the regular mesh midpoint (Z=0.006603), so the automatic torque calculation selected the opposite side compared with the MSE nose layout. This is a visual selection override, not a physical centre-of-mass estimate or an extra guidance force. Existing missiles that omit the key keep their previous behavior.

Version 0.1.4 added MinTurnRate=3 to the TVC section in both examples. Small terminal corrections no longer trigger the control effects; the launch controller and native maneuver authority remain independent of this visual threshold.

Version 0.1.3 fixed stage-filtered jets staying off after separation: MultiStageMissiles assigns its current-stage field only after SwitchMesh returns, so the adapter uses the requested stageIndex argument. Initial binding also synchronizes any stage events that occurred before the control runtime existed, and a pooled launch resets the stage to 1. Debug logs include visual-stage transitions.

## Launch configuration

Place these keys in `[MissileLaunchControl]`. Unconfigured ammunition keeps native behavior.

| Key | Default | Meaning |
| --- | --- | --- |
| `Enabled` | `False` | Enable launch control for this ammunition. |
| `Profile` | `SoftLaunchTurnover` | `SoftLaunchTurnover`: unpowered ejection, body tip-over, ignition, handoff. `PoweredTurnover`: native motor works during clearance/tip-over. |
| `ReplaceInitialFlightPhase` | `True` | Replace the native straight-flight delay for this missile instance. Native launch initialization and the configured launch-mesh switch still run. Set False to retain the native delay as well. |
| `ClearanceDistance` | `8` | Metres traveled along the original launch axis before turning. |
| `EjectionSpeed` | `35` | Metres/second relative to the launcher; used only for soft launch. Inherited platform velocity and gravity are included. |
| `TurnoverAim` | `NativeFlightPath` | Native steering goal after waypoint/loft/FOV corrections; or `FixedPitch`; or `RelativePitch`. Horizontal direction always follows the native steering goal. |
| `TurnoverPitch` | `0` | Degrees. Positive means nose up; negative means nose down. FixedPitch is horizon-relative, -90..90. RelativePitch adds to the launch elevation, then clamps to -90..90. Ignored by NativeFlightPath. |
| `TurnoverRate` | `180` | Maximum body rotation in degrees/second during launch. Independent of later MaxTurnGBonus. |
| `TurnoverTolerance` | `3` | Remaining alignment error in degrees at which tip-over finishes. |
| `TurnoverBraking` | `False` | Optional SoftLaunchTurnover slowdown with opposite control jets shortly before alignment. PoweredTurnover is unaffected. |
| `TurnoverBrakeAngle` | `20` | Maximum remaining angular error at which braking may start, in degrees. Must be greater than TurnoverTolerance. |
| `TurnoverBrakeDuration` | `0.12` | Maximum braking interval in simulation seconds. The braking window may shrink to meet this limit without overshooting. Range: 0.01..2. |
| `HandoffTime` | `0.2` | Seconds blending inertial ejection motion into native forward motion. Zero hands over immediately. |
| `MaxControlTime` | `3` | Maximum clearance + tip-over time, in simulation seconds. Timeout ignites if necessary and releases control. Handoff can add its own short duration. |
| `VisualPivot` | `Auto` | Geometric midpoint of the regular flight mesh, or explicit `x,y,z` **in metres**. This is a cosmetic pivot, not a mass-centre estimate. Root position, collision geometry and target coordinates are not relocated. |
| `DelayStage1EffectsUntilTurnoverComplete` | `False` | Additional Stage-1 visual gate for PoweredTurnover. SoftLaunchTurnover already delays ignition and scheduled stage effects. Applies to all Stage-1 exhaust slots; an ended stage is never replayed. |
| `ControlEffects` | `Auto` | Auto selects definition sections beginning with `Launch_`; All selects every control-effect definition. Prefix matching is case-insensitive. |
| `Debug` | `False` | Log launch transitions, native stage, save/load state, bound jets and each jet's first emission. |

ClearanceDistance is the distance to the START of tip-over along the original launch axis, measured from the missile's launch position. It is not the final ignition altitude or a height above sea level. A soft-launched missile keeps its upward momentum while rotating and braking, so ignition can happen several metres higher. EjectionSpeed, TurnoverRate, the required turn angle and braking settings affect that additional rise.

For a vertical launch, `TurnoverAim=RelativePitch` and `TurnoverPitch=-80` requests 10 degrees above the horizon. `FixedPitch=-15` requests 15 degrees below the horizon. These are launch attitudes; they do not create a top-attack flight profile. Subsequent waypoints and attack behavior remain native.

The custom launch phase is an overlay, not a new value inserted into the game's flight-stage enum. F10 continues to show native stages such as ToBearing; Debug logs show Clearance, Turnover and Handoff. Underwater and aircraft/drop launches retain their specialized native launch behavior.

### Counter-thrust and effect duration

With TurnoverBraking enabled, the launch rotation slows using constant angular deceleration in the final braking window. Launch thrusters visualize the opposite torque during that slowdown, using their existing Position and Rotation. No extra effect sections are needed. The driving-side emission stops when the opposing side takes over; already spawned particles keep their authored lifetime.

Braking begins no earlier than TurnoverBrakeAngle. The usable stopping angle excludes TurnoverTolerance and is limited to half of `TurnoverRate * TurnoverBrakeDuration`. With the installed SA-N-9 settings (200 deg/s, 20-degree brake angle, 3-degree tolerance, 0.12-second maximum), an unchanged steering goal gives a braking interval of up to **0.12 seconds**, beginning at approximately 15 degrees of remaining error. Starting closer to the target shortens it. The current native goal is sampled on every steering step; the controller does not freeze an old target bearing. Braking is derived from the current orientation and needs no pulse timer that would restart on save/load.

Launch thrusters stop emitting at completion of the braked tip-over; ignition and the Stage-1 effect then begin, followed by handoff. MaxControlTime remains the fallback if the target cannot be reached. Without TurnoverBraking, launch jets retain their previous rotation-driven behavior through the eligible launch/handoff phase and fade with ResponseTime. Maneuver jets remain constrained by their flight-phase filters and ActiveDuration. Stage motor effects keep their separate StageBurnTime and stage-separation lifetime (16 seconds for the SA-N-9 example).

Thruster demand is updated on each native physics step, including the final tip-over step. A newly activated continuous emitter receives one immediate particle so a short pulse does not wait for its emission-rate interval. Very short pulses can still finish within one rendered frame at high time compression; a visible multi-frame flash cannot be guaranteed in that case.

## Maneuver configuration

Place these keys in `[MissileThrustVectorControl]`.

| Key | Default | Meaning |
| --- | --- | --- |
| `Enabled` | `False` | Enable additional maneuver authority. |
| `FlightPhases` | `TerminalApproach` | Comma-separated native phase names, or All. |
| `MaxTurnGBonus` | `0` | Additional permitted lateral acceleration in G. Both the native G limit and the corresponding speed-dependent angular-rate limit are increased. Shared ammunition parameters are not modified. |
| `MinTurnRate` | `3` | Minimum combined pitch/yaw turn rate in degrees/second that activates TVC control effects. Active effects stop below 80% of this rate (2.4 deg/s with the default). 0 disables this filter. Pure roll does not trigger it. Range: 0..1440. |
| `ActiveDuration` | `-1` | Seconds since first eligible phase entry. -1 is unlimited; 0 disables the window. The clock continues outside the phase and during motor-off intervals; re-entry/relight does not refill it. |
| `RequireMotorBurning` | `True` | Require the native motor to be burning. Use False for independent attitude-control jets. |
| `ControlEffects` | `Auto` | Auto selects `Maneuver_` definition sections; All selects all control-effect definitions. |
| `Debug` | `False` | Enable diagnostic logging. |

The launch controller has priority during its own short phase. The maneuver budget becomes eligible after handoff. Effects are cosmetic and do not each add another copy of the G bonus. A jet can visualize a turn with MaxTurnGBonus=0; the bonus does not require a particle resource.

MinTurnRate filters TVC visuals only, using the actual rotation sampled each physics step. It leaves MaxTurnGBonus available for guidance and does not change the ActiveDuration clock. Launch-selected effects bypass this threshold, including shared Maneuver_ jets selected by launch ControlEffects=All. For Thruster effects, crossing below the lower threshold stops new emission; existing particles finish their authored lifetime. For StageExhaust, deflection returns smoothly to neutral while the existing motor plume keeps its own burn schedule. The 80% stop threshold prevents rapid on/off switching near the start threshold; raising MinTurnRate requires stronger corrections, while lowering it shows smaller corrections.

Supported phase names: `Launch`, `ToBearing`, `MaintainHeight`, `MoveToLoftAlt`, `MaintainLoftAlt`, `MoveToSeaSkimming`, `MaintainSeaSkimming`, `MoveToFinalFlightAlt`, `MaintainFinalFlightAlt`, `AlignSensorToTarget`, `TerminalApproach`, `EnterSearchMode`, `PerformSnakeSearch`. Unknown names reject the ammunition's control configuration instead of silently enabling the wrong phase.

## Named effect definitions

Use sections such as `[Launch_MainMotor]` or `[Maneuver_NoseLeft]`. The **section name**, not the Effect resource path, determines Auto selection. All still respects phase/stage filters. A definition selected by both controllers owns only one visual instance.

Common keys:

| Key | Default | Meaning |
| --- | --- | --- |
| `Type` | `Thruster` | Thruster or StageExhaust. |
| `FlightPhases` | `All` | Optional native flight-phase filter. |
| `Stages` | `All` | Optional comma-separated MultiStage visual stage numbers. Flight phases and visual stages are separate concepts. |
| `FullDeflectionRate` | `30` | Body turn rate in degrees/second that requests full emission/deflection. |
| `ResponseTime` | `0.08` | Seconds of exponential visual smoothing. Zero responds immediately. |

For `Type=Thruster`:

- `Effect`: required single-effect resource path, which may contain supported sub-emitters. The provided resources emit along local +Z.
- `Position=0,0,0`: missile-local **game/mesh units**, consistent with base-game EffectPosition/SubModel Position keys. 1 metre = 0.0148809375 units.
- `Rotation=0,0,0`: local Euler degrees applied to the neutral +Z jet.
- `InvertControl=False`: optional per-jet side-selection override. True negates the automatically calculated torque direction; Position and Rotation keep their visual meaning. Applies to Thruster effects in either launch or maneuver control, including opposite-side soft-launch braking. It does not affect StageExhaust, MinTurnRate, emission lifetime, native guidance or the G bonus. Set the same value on opposing jets when reversing a complete group.
- Place the jet at its actual visual mount. The active side is calculated from `(mount - mesh midpoint) x (-jet direction)` and the signed body turn rate (opposite torque during enabled soft-launch braking). Moving the same jet from the nose to the tail therefore reverses its turning contribution. A jet with no useful lever arm stays off.
- Use particles with a continuous emission rate for proportional control. Invisible, zero-rate carriers using Birth/InheritNothing links to continuous children or further such carriers are adapted on the private effect instance: their links and carrier bursts are removed, and the visible children are driven directly. This supports the existing flame/glow/smoke effect and the MSE five-port row without changing their source assets, placement, material or particle lifetime. Other burst-only or complex sub-emitter chains are not guaranteed proportional actuators.

For `Type=StageExhaust`:

- `Stage=1`: existing MultiStage stage to bind.
- `EffectIndex=1`: existing stage effect slot; **1 is the default**. Slot 1 corresponds to Stage1FlightEffect (or Stage1FlightEffect1).
- `MaxDeflectionAngle=15`: maximum additional visual deflection in degrees.
- The adapter preserves the authored placement, neutral rotation, scale and lifetime. The standard stage plume points backward along local -Z before its authored rotation. It never respawns a burned-out exhaust. Define each stage/slot only once.

For PoweredTurnover, delaying Stage-1 effects consumes the existing stage burn window: it does not extend burn time, separation time, or motor thrust. Soft-launch effects start with the actual delayed ignition. Stage transitions themselves remain owned by MultiStageMissiles; absolute numeric separation times are still measured from launch, not from ignition. Use appropriate separation times for your launch profile.

## Compatibility and validation

The module reads the native `setCourseTowardsPosition` goal during launch. It does not call CalculateInterceptAimPoint again: that method mutates guidance and waypoints. The native ToBearing/TerminalLoft planner, target choice, collision check and lifetime remain active. After handoff, only effective native turn limits are modified; no second steering rotation is appended.

The current game assembly and MultiStageMissiles 1.2.26 adapter are fingerprint-checked. An unreviewed game update disables this module and retains native behavior. An unrecognized Stage mod disables its adapter; a staged soft launch or explicit Stage-1 gate then keeps native launch rather than starting with a broken effect gate. Competing transpilers on the modified native methods and a detected Oniks launch hook cause initialization to roll back. Other mods that directly write missile rotation outside these hooks can still conflict and require an in-game check.

Own launch phase, inertial velocity, elapsed control time, motor clock and maneuver budget are saved with versioned keys. Old saves without these keys do not replay the launch or receive a new finite maneuver budget. Pausing uses simulation time; pooled/destroyed missiles release their private jets and restore cosmetic offsets. Visual pivot compensation is skipped for a render hierarchy that contains a collider.

The build script compiles against the installed Unity/game assemblies and runs offline checks of braking trajectories across physics step sizes, parsing, phase budgets, angle/G conversion, hook IL, dependency contracts, package references and preservation of the reviewed Aster overrides. PAC-3 MSE and SA-N-9 regression examples remain fixed while the user's live versions are checked for configuration compatibility. It also parses the package INIs with the game's actual INI reader, with two Unity path getters adapted in memory for the offline test. A separate regression process executes the production thruster torque calculation with Aster/MSE layouts, the stage callback and the MSE launch/terminal effect gates against the old-field/new-argument transition ordering, pooled reset and restored state. Its managed object shells bypass Unity-dependent static initializers in memory. No installed game assembly is modified. These checks do not render a Unity scene. In-game launch, save/load, time-compression and visual tuning remain to be verified.

Suggested in-game checks: SA-N-9 against low and high targets with TerminalLoft enabled; inspect tip-over, opposite jets and subsequent ignition; compare FixedPitch and RelativePitch; PAC-3 MSE nose jets during powered launch and terminal corrections; finite and unlimited ActiveDuration; pause/time acceleration; save/load during ejection and terminal control; effect stop at stage separation/burnout. Use newly launched missiles when checking launch changes. With Debug=True, inspect Player.log for visual stage=2, firing messages and optional-resource errors, then set Debug=False after tuning. The initial Bind log alone does not prove that a jet was drawn on screen.

Source and build script are in `CustomSonarAudio/MissileControlMod`. Build output uses `.dll_` to avoid AnchorChain loading a second copy; only the installed AC Pack copy is active.
