ExtendedGuidance 0.10.19 - measured guidance and fire control
Physical radar and EO/IR measurements now also cover units in the same taskforce.
Self-detection stays excluded; automatic target selection and ROE remain native.
Accepted manual orders use the same sensor and firing-solution requirements.
Ship observations and weapon aimpoints are separate: guns retain native hull
height, while CIWS retains native compartment selection and small-boat targeting.
Measurement error is preserved. Surface impacts use native compartment damage;
aircraft and missile impacts use their native armor/health values.
CIWS uses one firing permission, including arcs, alignment, reaction delay and
ammunition range. Valid low-confidence solutions can start an assessment burst;
existing bursts are not restarted because of small confidence changes.
Gun/CIWS diagnostics add firePermit, fireReason, hardBlocked, fireStarts,
fireHolds, predictedErrorM and aimOffsetM. No additional INI keys are needed.

Gun and CIWS sensor selection
AssociatedSensors is an ordered allow-list for measured gun/CIWS fire control.
The first usable listed sensor supplies the solution. Missing measurements, damage,
channel conflicts or disabled sensors allow the next listed sensor to be used.
An explicit list never falls back to an unlisted radar, bridge optic or shared source.
INI order is preserved even when the native game sorts its working list by height.
AssociatedSearchSensors remains the native search/cue assignment; it does not add
fire-control candidates to AssociatedSensors.
Without a fire-control assignment, EG prefers a usable FCR, then a usable search
radar, then EO/visual control; measured quality chooses within each category.
Explicit Manual/Local modes retain local visual control and cannot borrow radar.
Radar and EO/IR observations retain native visibility, epochs and plotting policy.
The missile-test log includes mount/source section, policy, priority and acquisition
status, including periods when CIWS holds fire. No new INI keys are required.

ExtendedGuidance 0.10.4 -- AC Pack

Gun and CIWS fire control
-------------------------
Moving air/surface targets use measured contacts. Assigned sensors are exclusive;
without an assignment, eligible own-platform sensors provide the fallback. Native
sensor auto-enable settings, channels and antenna movement remain in force.
A sensor already supporting another target is not commandeered. Releasing a gun
removes only its own reservations and preserves concurrent missile support.

FireControlMode is the existing weapon-system key in systems/weapons.ini or its
OVWR. Missing mode uses the native Director default. Explicit Manual, Local and
LocalControl exclude automatic FCR fallback and use local visual observations.
Mount/module type does not select this behavior. No new keys are required.

Fast prediction blends with a longer trend for repeated observed maneuvers;
short-flight shots favor current motion. Fire never waits for a full history.
CIWS fire authorization uses measured uncertainty, ammunition range/budget and
remaining threat reaction time. Native reaction delay and mechanical limits remain.
A temporary lost track does not reactivate native percentage calibration.

Existing sensor keys (native sensor sections or sensors OVWR files):
FCSolutionGainRate: response to new measured motion; higher values converge faster.
FCMinSolution: initial solution confidence (0..1), used for gun/CIWS fire permission.
Fresh observations build confidence; coasting reduces it. Urgent valid intercepts
may fire despite low confidence. Target speed, aimpoint and dispersion are unchanged.
FCTracksRounds: correction from observable sampled projectile/group trajectories,
limited to 20 samples per second per weapon. Unobserved rounds provide no bonus;
random ammunition dispersion is not corrected away. Round tracking prefers a
suitable radar when candidate measurement quality is otherwise comparable.

The measured solution and ammunition dispersion each enter once. No separate
calibrated CIWS aim error, random evasion penalty or time-only spotting bonus is
added. Native ammunition/reload handling, armor, health and kill accounting remain.
Fired CIWS groups follow finite ballistic trajectories and survive a firing pause
or target switch; they are consumed once on arrival. F10 Kills/Fails remain usable.
Fixed map-point fire, land aimpoints and laser-guided ammo retain native aiming.
Surface aim height uses the native hull reference without applying elevation twice.

Map Pk previews retain the native calculation. Missile-test recording includes
GUN_SOLUTION with measurement source, observed corrections and in-flight groups.

ExtendedWarhead
---------------
Optional ammo section immediately after [WarheadData]. It may also be supplied
through an ordinary ammo OVWR. Native warhead/fuze keys remain valid without EG.
Example for a programmable 76 mm round:

[ExtendedWarhead]
EffectType=PFF
Caliber=76
AirMode=GatedProximity
SurfaceMode=Impact
AdaptiveFuze=true

EffectType: HE, PFF, KETF, Native. Missing: HE for native HighExplosive, otherwise
Native. AP, HEAT, illumination, cluster and other types are never inferred from Power.
Native disables the extended effect/fuze path for that ammunition.
Caliber: millimetres, up to 500. Missing/0: infer mm, cal_127 or inch names; otherwise
use native impact-size class. Legacy cal_762 and cal_05in mean 7.62 and 12.7 mm.
AirMode / SurfaceMode: Inherit, Impact, Proximity, GatedProximity, Timed.
Missing modes inherit native behavior. KETF surface use is limited to Impact;
Inherit also selects Impact for KETF against surface targets.
AdaptiveFuze: true/false, default false. HE/PFF proximity sensing seeks closest
approach within its sensor radius instead of firing at first threshold crossing.
AirImpactPriority / SurfaceImpactPriority: true/false, default false. A direct
collision in the current integration step takes priority over a proximity event.
These flags do not predict an unobserved future collision.

Native FuzeProximityDistance remains the sensing radius. Gated/Timed modes retain
an existing positive FuzeGateSeconds when the native mode matches. Newly assigned
gated proximity defaults to 1 s; newly assigned timed mode uses 0.002 s timing spread.
Timed events use the launch solution; they cannot follow later target maneuvers.
KETF adds an automatic caliber-dependent forward stand-off to its programmed burst.

HE/PFF effects have bounded radial falloff; PFF has greater effective reach and
fragment-cloud penetration. KETF uses a finite expanding forward cloud, without
spawning fragment/submunition objects. Native Power supplies the damage magnitude;
caliber also influences the effect scale. These are game abstractions, not measured
lethal-radius specifications. Armor, accumulated damage and native critical damage
remain effective; a hit need not destroy the missile. Surface HE/PFF airbursts and
direct impacts use native hull/compartment damage. KETF does not add a separate
fragment-versus-ship armor simulation. Existing AP/HEAT damage paths are unchanged.

Included OVWRs: three Euromod Mk15 FCR versions; Leonardo 76/127 mm ammo; Euromod
127 mm aliases/variants; 30 mm SeaSnake ABM and 35 mm Millennium AHEAD. SAPOM,
SAPOMER and guided Vulcano retain their native effect. OVWRs preserve native keys.
Restart Sea Power after installing. Existing submod settings are retained.

Radar and datalink corrections (0.9.8)
-------------------------------------
No new keys are required. Restart the game after installing.
SeekerReceiverSensitivity applies to active and semi-active radar reception.
ARH family defaults use 2E-11 watts; SARH defaults remain 1E-13 watts.
SeekerReferenceRange still sets an explicit reference calibration; native seeker
range remains the operating limit. Angular resolution now also limits ARH/SARH
measurement precision. It does not change beam width or gimbal coverage.
Hybrid HOJ/passive reception uses the RF_Passive profile's receiver sensitivity;
a dedicated RF_Passive missile retains its effective per-missile sensitivity.

SARH reception includes compatible assigned offensive jammers and the target's
native automatic self-screen noise, evaluated at the receiving missile.
Native range-query options are preserved, including ECM exceptions used by HOJ.
These hypothetical queries do not publish contacts or refresh datalink tracks.
Missing profile files/sections use the built-in shipped values. Legacy profile
aliases inherit canonical overrides unless their own section overrides a key.
Platform acquisition, tracking gates, scan timing and mechanical movement remain
native; obsolete seeker timing/association rows were removed from radar profiles.

Native radar gates and target memory (0.9.4)
-------------------------------------------
Use existing ammunition [Guidance] keys. No new configuration keys are needed.
Example:
[Guidance]
RangeGate=2
SizeGate=1.1
TargetMemory=True

For active radar homing, RangeGate is the initial search-region radius in nautical
miles around the predicted launch/contact cue, enlarged by its uncertainty.
It does not replace ExtendedGuidance SeekerRangeGate, the tracking gate in metres.
SizeGate is an RCS ratio tolerance, applied as a soft plausibility weight. The
initial native maximum-RCS prior has a wider tolerance than local measured echo
history. Aspect/noise tolerance remains; a mismatched echo is not forbidden.
Unresolved mixtures cannot be separated by this size check. Zero, negative or
missing native gates disable the respective additional filter. Existing profile
resolution and tracking gates still apply. These RCS keys do not filter IR/HOJ.

All owned seekers retain short profile-defined track coasting. After that,
TargetMemory=False releases the old association and resumes normal search.
True permits bounded prediction-based reacquisition: an additional three coast
intervals, clamped to 2-8 seconds, after the normal coast interval. A retained
association is not an acquired track. Expiration preserves the INS solution.
Fresh authorized datalink observations can still cue acquisition; stale updates
cannot extend local memory. TargetMemory does not reveal the live target position
or guarantee rejection of countermeasures. Native map Pk estimates are unchanged.

Launch navigation (0.9.2)
------------------------
A new launch takes one fresh ranged contact from the launcher's permitted native
plotting table. Position, motion and observation age initialize INS navigation;
the original game calculates interception lead from that current-position cue.
This does not create a seeker lock or enable a post-launch datalink. Without a
valid ranged contact, the assigned point remains the fallback and pooled motion
is discarded. Submunitions retain the assigned-point fallback.

New permitted datalink observations can update navigation. Re-reading the same
observation does not replace its accepted motion or refresh its timestamp.
LocalTerminalOnly, native missile profiles, loft and seeker activation remain.
With missile diagnostics enabled, launchObservation records the launch source.
Test newly launched missiles after restarting. Previously saved in-flight missiles
retain their stored navigation data; the original launch contact is not recreated.
No new INI keys are required.
Statcards (0.9.1)
----------------
Open a missile or radar's normal information card. Effective seeker labels also
appear in armament lists. Missile descriptions start with Extended guidance:
seeker type, support, target memory, HOJ where available, seeker range limit,
gimbal half-angle, tracking rate, angular resolution and track coast time.
Track coast is a measurement retention interval, not total INS flight endurance.
SARH terminal handover requires a compatible launcher and datalink carrier.

Radar cards and unit sensor tables show the resolved antenna model, fire-control
processing family, range limit and applicable weapon support. Native channel,
altitude and frequency entries remain. Radar descriptions start with Extended
radar details, including beamwidth, resolution, clutter rejection and the native
mechanical search scan period when configured. FCRs do not show mount coverage.
No new tooltips or countermeasure success percentages are introduced. Displayed
range limits and model parameters are not guaranteed detection performance.
ICWI is not claimed or enabled. TV guidance remains native; IIR labels apply to
IR missiles whose effective EG profile is an imaging profile.

Values use the existing missile/sensor keys and mapping precedence. No new keys
are required. EG must be enabled in AC Pack settings before starting the game.
This update changes presentation; legacy map Pk estimates remain unchanged.
Sea environment (0.9.0)
----------------------
Radar and RF missile observations sample the native Ceto CPU wave surface when
available. Wave heights determine intermittent masking and local reflection
height; nearby samples provide surface slopes for a bounded clutter correction.
Samples are captured on the main thread and passed to workers as immutable data.
No new keys are required. Native missile altitude control remains unchanged.
The mod checks ocean/spectrum availability and readable displacement buffers.
Missing data or unsupported ocean APIs use the statistical sea model. A genuine
adapter error produces one warning; diagnostic measurements include nativeWavePoints
and waveSampler. A positive point count means native geometry reached that evaluation.
Range previews remain statistical and stable. IR has no new RF wave penalties.
Queries follow the CPU ocean surface, not every shader detail. Cosmetic overlays
are excluded. Fine-scale scattering remains statistical; reflection height is
sampled locally, not a full ray trace of moving reflective facets. Native wave
sampling cost and visual agreement still require in-game acceptance.
MultipathStrength=0 disables multipath, not sea clutter or wave masking.

Activation
Restart Sea Power after installation or configuration changes. Both AC Pack's
Mod Manager checkbox and the ExtendedGuidance submod switch must be enabled.
The submod defaults to off; existing preferences are preserved. Normal startup:
[ExtendedGuidance] loaded successfully.

Scope
EG evaluates platform-radar returns (RCS, geometry, clutter, Doppler and ECM).
Radar observations include bounded, time-correlated signal fluctuations. Native
radar contacts receive measurement-dependent range/bearing errors; expected range
previews stay stable. Each receiver has separate observations.
Native search sweeps, confirmation, echo clustering, contacts, FCR movement and
gun mechanisms remain native. Guns and missiles read existing native contact estimates.
EG provides ARH, SARH, IR, passive-RF and radio-command missile tracking,
including ASMs, groups and IR/RF hybrids. Each missile has its own seeker geometry.
Native contact cues are advanced from their observation time. Surface seeker
measurements retain a separate hull aim offset; lost tracks coast on the last
estimate. Unresolved seeker echoes produce a weighted measurement with ambiguity.
Track changes require persistent evidence; AntiCountermeasuresBonus affects this
association for radar and IR seekers, not a permanent bonus for captured chaff.
No additional keys are required. Diagnostics show echo contributors, ambiguity,
mean SNR and fluctuations; two rolling 32 MiB logs retain longer test flights.
Transport-only DL1 proxies use a real radar for required own-missile tracking.
Command-updated IR seekers use the configured handover while supported. Without
fresh support they may search autonomously after launch/drop, including while
lofting; failed seekers remain unavailable. IR observations obey SeekerPassiveRange.
Fresh, matching external range/velocity estimates continue to support IR tracking.
Measured ship echoes constrain the aim height to the native hull convention;
this does not grant an IR range measurement. High-altitude thermal scaling cannot
subtract the target's baseline emission. Native channel limits still apply.
IR target switches, IR decoys and passive RF capture have distinct event messages.
IR uses a bounded terrain/water background trace in the current flat game geometry.
A clear-air path approximation attenuates long low-altitude paths more strongly
than high-to-high paths. Launch feasibility and seeker observations share the model.
No temperature, Earth-curvature or two-band simulation is included. Existing
IRBackgroundRejection still controls profile rejection of the sampled background.
Missile diagnostics include IR intensity, background kind/distance, atmospheric
transmission, surface constraint and range cue. No additional keys are required.

The map Pk percentage formula remains native. EG-controlled missiles bypass the
native random interception, decoy/ECM rolls and forced-miss terminal deviation.
Fuze encounters, damage and equipment failures still determine actual outcomes.
Propulsion, loft, sea-skimming, waypoints, pop-up and native group flight remain
native. ESM, visual/sonar contact discovery, TV/laser guidance, fixed-point gun aiming and unguided
weapons retain their own models. Existing information/point-value estimates are
not combat outcome simulations. RF sea multipath is described below.

Missile configuration: per-key priority
1. Effective ammunition INI: [ExtendedGuidance], immediately after [Guidance].
2. systems/ExtendedGuidance_OVWR.ini: [ammunition_filename_without_ini].
3. Selected fixed profile in systems/ExtendedGuidance_Profiles.ini.

[ExtendedGuidance]
SeekerProfile=Auto
SeekerCoastTime=0.8
SeekerUpdateInterval=0.1

Equivalent mapping example:
[example_missile]
SeekerProfile=ARH_Surface
SeekerRangeResolution=75

Enabled=False restores native guidance for that missile type. It does not disable
EG platform radars. SeekerProfile=Auto overrides a mapped profile choice while
retaining numeric per-key overrides. Effective aliases and extensions apply.

Profile families
Air radar: ARH_Generic, ARH_PD_Early, ARH_PD_Standard, ARH_PD_Advanced, ARH_AESA;
SARH_Generic_Early, SARH_Generic, SARH_Generic_Advanced, SARH_Pulse,
SARH_CW_Early, SARH_CW_Advanced, SARH_PD_Early, SARH_PD_Advanced.
Surface radar: ARH_Surface_Early, ARH_Surface, ARH_Surface_Advanced,
SARH_Surface_Early, SARH_Surface.
IR: IR_RearAspect, IR_AllAspect, IR_AllAspect_IRCCM, IIR_Imaging.
Other: RF_Passive, Command_Radar.
Legacy AMRAAM_Active, AMRAAM_Advanced and Sparrow_M remain accepted aliases.

Auto uses guidance type, primary target domain, IOCDate (FOCDate fallback) and
available native penalty/CM metadata to select fixed profiles. Dates and penalties
do not scale profile values. Surface defaults use pre-1980 / 1980-1999 / 2000+
ARH families; SARH uses pre-1980 / later. Missing dates use the middle surface
family. These defaults do not impose an airborne-target Doppler notch on ships.
Auto never infers a particular SARH waveform, imaging IR or an AESA missile seeker.
Explicit rear-aspect restrictions take priority for IR classification.

Common keys and units
SeekerAntenna: Mechanical or AESA for radar missile seekers.
SeekerBeamWidth: full one-way half-power beam width, degrees, 0.2..90.
SeekerSidelobeSuppression: dB, 0..80.
SeekerRangeResolution: metres, 0..10000; zero disables range discrimination.
SeekerRangeGate: association width, metres, 0..20000; zero disables the gate.
SeekerDopplerResolution: equivalent radial-speed width, m/s, 0..500;
  zero disables Doppler discrimination.
SeekerDopplerGate: association width, m/s, 0..2000; zero disables the gate.
SeekerManeuverAllowance: process acceleration uncertainty, m/s^2, 0..300.
SeekerClutterRejection: rejection outside the clutter notch, dB, 0..80.
SeekerTrackRate: degrees/second, >0..2000.
SeekerCoastTime: seconds without measurement before local lock is lost, 0..30.
SeekerMemoryTime: total association memory after the last measurement, seconds, 0..300.
With TargetMemory=True, memory lasts at least SeekerCoastTime. Otherwise it ends
with coast. Expired memory clears association, not the stored INS navigation state.
SeekerAcquireTime, SeekerReacquireTime: detection dwell, seconds, 0..10.
Reacquire applies only to the same retained track. New/forgotten echoes require
initial acquisition again, including IR and passive RF. Physical gates still apply.
SeekerUpdateInterval: missile measurement interval in simulation seconds,
  0.02..2; default 0.1, IR default 0.05. Native steering continues between samples.
SeekerReferenceRange: nm for SeekerReferenceRCS, 0..300; zero derives sensitivity
  from native ARH power/gain/wavelength, bounded by native SeekerActiveRange.
SeekerReferenceRCS: reference cross section, m2, >0.
SeekerReceiverSensitivity: ARH/SARH/passive receiver threshold, watts, >0.
SeekerAngularResolution: angular error/resolution, degrees, >0..10.
SeekerAngularGate: angular association width, degrees, >0..90.
GroundClutterSigma0: land backscatter coefficient, dB, -80..0.
SeaClutterSigma0: sea backscatter coefficient at sea state 3, dB, -100..0.

IR keys
IRReferenceSignature: reference native IR intensity, >0; default 1.
IRBackgroundRejection, IRBrightnessRejection, IRShapeRejection: fractions, 0..1.
Native SeekerPassiveRange sets reference sensitivity; a positive
SeekerReferenceRange overrides it in nm. Signal uses inverse-square falloff.
Native engine/aspect scaling, SeekerFOV, SeekerGimbalFOV, IsRearAspectOnly and
TargetRearCone apply. IR launch acquisition uses the same sensitivity/background
model. Target memory alone does not bypass launch acquisition.

Radar configuration
Profiles: Radar_Search, Radar_Tracking, Radar_PhasedArray, Radar_PESA, Radar_AESA.
FCR families: Radar_FCR_Pulse, Radar_FCR_MTI, Radar_FCR_PD,
Radar_FCR_PD_Advanced, Radar_CW_Illuminator. No OVWR is required for these defaults.
Per-key priority: Seeker* keys in the named sensors.ini section >
[Radar:SystemName] mapping > native sensor values > family fallback.

[Radar:example_radar]
GuidanceRole=Radar
SeekerProfile=Radar_AESA
SeekerAngularResolution=0.05

Type=DirectedSearch selects Radar_PhasedArray. For Type=Targeting, existing
SubClutterVisibility selects Pulse at 0, MTI above 0 and below 40, PD at 40..46,
and PD_Advanced at 47 or above. Missing metadata retains Radar_Tracking.
These are fixed simulation families, not continuous date-based bonuses.
Other types select Radar_Search. DirectedSearch alone does not prove AESA.
Exact hardware mappings or SeekerAntenna=AESA/PESA/Electronic select those families.
Native BeamWidth, RangeResolution and SubClutterVisibility override fallbacks.
Explicit Seeker* values override them; explicit zero remains zero.
Platform overrides accept beam, sidelobe, range/Doppler resolution and gates,
maneuver, clutter rejection, track rate, coast/acquire/reacquire, angular resolution
and ground/sea sigma. Missile reference sensitivity and IR-only keys do not apply.
Platform returns are evaluated within the native scan schedule. SPG-62, CEROS
and other FCRs use the same adapter and automatic profile selection; no special
platform tracker or required OVWR is added. Radar_CW_Illuminator is retained as a
legacy profile name with common PD defaults, without a separate transmitter path.
Platform contact age, uncertainty and acquisition timing now follow the native
contact system. Legacy platform tracking-time/association keys remain readable
but do not replace that system. Physical clutter, beam and Doppler values apply.
FCSolutionGainRate, FCMinSolution and FCTracksRounds feed the measured gun solution (see 0.9.9).

EG replaces old radar echo/LookDownMultiplier detection gates. Land and sea clutter
are evaluated even with LowAltitudeClutter=Off. Native instrument ranges, radar
altitude coverage, roles, arc/alignment, LOS, horizon, mast availability, readiness
and channel constraints remain. Native ammunition launch/target envelope keys,
including minimum target altitude where enforced by the game, are not removed.

Datalinks
[Radar:example_datalink]
GuidanceRole=Datalink
TrackSource=Auto

GuidanceRole: Auto, Datalink or Radar. Explicit mappings override the raw Gain >200
fallback. Native DatalinkGuidance alone does not make a real radar transport-only.
TrackSource: Auto prefers the native selected measured source. An exact on-platform
sensor SystemName selects that source from the eligible measured observations; a different
native source is not silently accepted. The key also restricts DL launch-range
evaluation. Fake DL gain cannot create detections. Native contact sharing remains;
submerged launchers use their local table. Bearing-only reports cannot supply a
new missile range measurement.
DL MaxRange bounds sender-to-missile communication, with LOS/horizon and native
weapon-channel constraints. Mode 1 also checks the assigned missile's radar return;
mode 3 does not. SARH still needs a compatible real illuminator.

SARH with MidCourseCorrection=3 prefers an available native or mapped DL carrier.
A separate illuminator is reserved near the lesser of TerminalApproachDist and
SeekerPassiveRange, with existing acquisition/update settings and native antenna
slew rates providing prepointing time. Native movement performs the alignment.
Without a compatible DL carrier, native continuous FCR guidance remains available.
WeaponChannels and TargetChannels remain separate: 2 weapons / 1 target permits
two missiles at the same target, not two distinct targets. Original 1 / 1 entries
stay 1 / 1. This does not model time-shared ICWI against separate targets.
A fresh local seeker solution takes priority, including a captured decoy. Permitted
external information can cue reacquisition but cannot create a local lock.
LocalTerminalOnly cuts new external updates in TerminalApproach; previous
information can still be predicted. Group flight uses measured leader handovers.

Passive RF / Home-on-Jam: existing [Guidance] keys
SecondaryPassiveRadarGuidanceType=None / HomeOnJam / Full
PassiveRadarGuidanceFrequencies=All or the native frequency list
SeekerPassiveRange, AntiCountermeasuresBonus

Pure anti-radiation missiles use RF_Passive automatically. HOJ accepts jammer
emissions; Full also accepts radar emissions. Frequency, source operation,
coverage, LOS/horizon and authored passive range apply. Passive RF and IR supply
bearing information; they cannot measure true range or radial velocity. Associated
fresh radar/DL information may refine range only through an allowed link.
AntiCountermeasuresBonus has a bounded association effect, not a range or Pk bonus.
Native automatic self-screen noise can remain active without an offensive Jams
command. Turning that command off does not necessarily stop automatic emission.

Displays and diagnostics
F10 Radar shows the EG profile and instantaneous return margin/rejection with
native contact management. The local range estimate uses current geometry and
ECM; it is not a fixed specification or proof of an acquired track.
Missile diagnostics retain local/support/navigation estimates and identify native
platform tracking in the supportSensor entry.
The sensor-information Radar graph uses the EG kernel for air and surface
previews, with flat sea, an inbound target and no ECM. It is not a terrain-aware
combat prediction. Other sensor graphs remain native.

F10 > Missile Test > Missile diagnostics: OFF/ON records ordinary scenarios.
The recording button is below Start Missile Test. During a native test, the
compact Recording button is in the right column. F10 may be closed while recording.
Do not start the native Missile Test for a normal battle: it creates extra units.
Native test start also enables recording for that test. The Log/Missile Test tabs
belong to the game. EG adds diagnostic controls and numbered tracking/outcome events.
TRACK LOST, REACQUIRED, SPOOF, HOJ and MISS retain native event numbering and IDs.
Native hit/damage reports remain; an unknown miss cause is not labelled a notch.

Log: %USERPROFILE%/AppData/LocalLow/Triassic Games/Sea Power/Mods/ExtendedGuidance/Diagnostics/missile-test.log
Two rotating files, each at most 32 MiB; missiles at most 2 Hz, launchers at most 1 Hz
of simulation time. Bounded background file writer, 300 lines/wall-second cap;
dropped records are reported. Logged truth positions are comparison data only.

Limits
Profile values are empirical simulation settings, not measured weapon performance.
Surface defaults, IR contrast/shape discrimination and RF association need gameplay
calibration. No detailed waveforms, thermal imagery, adaptive nulling,
individual flare trajectories or detailed range-deception jamming are modelled.
Existing combined chaff/IR decoys retain native positions and lifetimes.
One bounded numerical worker handles immutable snapshots; Unity reads, ECS writes
and event publication stay on the main thread, with equivalent synchronous fallback.
Saved EG contacts recover serialized measured positions conservatively. Detailed
missile acquisition history resets on reload and uses the saved native flight cue.
Final-binary offline model/API tests cover installed public build 26103404 and the
available beta assembly. Actual gameplay acceptance in both remains pending.

Guidance recovery (0.10.12)
- Radar and IR missiles use the same terminal-loss policy. A fresh local bearing
  remains valid guidance; permitted ARH/IR datalink also remains usable. SARH
  terminal DL never substitutes for illumination.
- InertialGuidance=True (native default) permits continuation from a stored ranged
  estimate while a conservative intercept remains possible within native lifetime.
  This uses estimated target motion, own velocity, turning limits and available
  energy; it does not query the true target position or run a trajectory optimizer.
- Without INS, a usable estimate or feasible geometry, the seeker gets its coast/
  acquisition allowance plus native SelfDestructDelay. Bearing-only continuation
  may retain SeekerMemoryTime when TargetMemory=True; it cannot invent range.
  Repeated stale reads or changing failure reasons do not renew this search period.
- These are simulation abort criteria, not documented missile-specific timers.
  Native geometric misses, collision, stall and maximum lifetime still apply.
  FCR reservations survive temporary visibility loss. Final release clears only
  completed users, preserving other weapons and prelaunch reservations.
- Idle guns/FCRs use native return-to-rest angles, rates and weapon delay. EG does
  not replace search radar rotation or override authored rest/cold positions.

The selected missile bottom status row shows current EG guidance, including
SARH/ARH/IR, HOJ/passive RF, datalink, memory and recovery time. It refreshes
at most four times per simulated second. Target numbers remain native map
track numbers. Illumination loss is not labelled as proven FCR track loss.

Chaff
Passive RF chaff now has an age envelope and spatial extent, using its existing
DefensiveEffectTime and RCS. SpoofChance is a bounded strength hint (0.5 + value),
not a success roll. IsAirDecoy=True excludes powered decoys from cloud aging.
RF measurements account for resolution-cell coverage and centroid uncertainty.
Missile test logs include selectedDecoy, rfDecoy extent/RCS and clean-track age.
When ASM service dates are absent, explicit AntiCountermeasuresBonus selects an
early (<0.15), standard (<0.6), or advanced surface profile. Explicit EG profile
and mapping choices still take precedence. No new INI keys are required.

Sea multipath (0.8.8)
--------------------
Applies to radar measurements over water: platform radars, ARH and SARH.
No land multipath or IR/passive-RF multipath is modeled. Existing clutter remains separate.
The flat-water model uses antenna/target geometry, wavelength, sea state and antenna patterns.
SARH evaluates illumination and receive paths separately. No FCR rotation or missile flight
controller is replaced. A missed measurement may coast; it does not directly self-destruct.

Optional keys in [ExtendedGuidance] missile sections, missile mapping sections,
[Radar:SystemName] mappings or the existing radar sensor section; also accepted in profiles:
MultipathStrength=0.65         // 0..1; 0 disables, effective reflected field strength
MultipathRejection=0.35        // 0..1; residual elevation-error rejection, not fading immunity
MultipathDiversityMHz=20       // 0..2000 MHz RMS effective frequency diversity
MultipathPolarization=Average // Average, Horizontal, Vertical
Direct keys override mapping keys, which override profile defaults. Existing files need no changes.
Advanced PD processing families and ARH_AESA default to rejection 0.55 and diversity 40 MHz.
AESA does not receive an additional blanket multipath bonus. All these defaults are simulation
assumptions, not measured device specifications. Sea state describes statistical roughness;
individual waves and precise RF pulses are not simulated. Both enhancement and fading occur.
The field model uses a fixed 40 ms averaging window and unresolved phase uncertainty;
angle errors are bounded and uncertainty is carried into seeker filtering.

F10 radar: MP reports signal change in dB and elevation bias in degrees.
Missile diagnosis: multipath power, elevation bias/sigma and receive/transmit path differences;
supportObservation explains missing DL measurements. A valid DL transport stays connected
when the target observation is temporarily missing or stale. Own-platform contacts are tried
when the taskforce's selected contact cannot provide a usable ranged estimate.



0.9.3: IR/IIR map sectors follow the simulated seeker look direction; body-heading fallback before a look estimate. Search/guidance behavior is unchanged.

0.9.3: Radar and IR/IIR seekers expand a bounded search raster around their last cue. The instantaneous cone remains narrow; every fourth look revisits the cue. Slew and acquisition dwell apply. No new INI keys.
Map layers: Missile Datalinks (after Weapon Seekers). Light-blue dashed lines show active, fresh command/datalink support for own-side missiles, from their assigned emitter. Hidden on INS-only/coasting, lost connections, or destruction. The toggle is saved in Mods/ExtendedGuidance/map-datalinks.txt. Lines use native geographic map projection and do not affect guidance.

Inertial navigation
[Guidance]
InsDrift=0.05

Uses the existing key in degrees per minute; explicit 0 disables EG drift.
Resolution: explicit [Guidance] InsDrift, then [ExtendedGuidance] InsDrift,
then the missile mapping InsDrift, then the selected profile InsDrift.
Missing profile values inherit the built-in profile. Values must be finite and
nonnegative. Profile defaults use 0.15 for early/simple families and 0.05 otherwise;
individual mappings can select 0.02 for better navigation. AESA alone grants no
INS bonus. These are effective model settings, not published weapon specifications.
An accepted new target measurement corrects the effective guidance error.
During gaps, horizontal heading drift integrates over own movement. It is
not a fresh random position offset per frame and is not target covariance.
IR bearing-only coast holds an independent heading with the same drift.
Changing target or reloading starts a new effective drift state. Vertical
inertial/accelerometer errors and a complete inertial navigation unit are
not simulated. The fallback is a generic approximation, not a measured
specification of every missile. Existing missile files require no extra keys.

Native sea roughness and diagnostic retention (0.10.12)
- When CPU ocean displacement data are available, EG measures 64 dispersed open-
  water heights once per simulation second globally. Significant wave height is
  estimated as four times RMS about mean level; wakes/overlays are excluded.
  This single roughness estimate feeds clutter, Doppler spread, wave masking and
  multipath. Game SeaState 10 and 12 are no longer forced to SS9 roughness.
- Unavailable ocean data retain the previous bounded statistical fallback (SS9
  ceiling); wave periods remain approximate. No forced GPU readback is performed.
- Missile diagnostics show nativeHs_m, effectiveHs_m and waveHeightSource. Test
  start markers include globalSeaState. Unchanged idle launcher snapshots are
  limited to one per minute; engagement and inventory changes remain visible.
- Optional FUZE records capture the native intended-target proximity test: swept
  CPA, configured fuze radius, target body radius and native trigger/veto result.
  This observer does not alter damage or fuzing. Generic collider/Spherecast and
  SmartFuse outcomes are not reported as measured swept-proximity CPA.

F10 mean-return diagnostics and radar curves use the same observed roughness as
measurements, without adding instantaneous wave masking to the preview.

EG reaction control (0.10.15)
- While EG is enabled, Observe, Orient, Act and SoftKill reaction timing is
  enabled for both sides with a neutral scale of 1. Native OODA menu choices
  display "EG controlled - active"; their saved values are preserved and
  apply again when EG is disabled after restarting the game.
- The native contact-processing queue and evaluation progress remain in use.
  CombatSystem ReactionTime, CICSlots and EvaluationSlots determine central
  processing. An explicit CICSlots value is not enlarged by DL director channels.
  Physical sensor scans, mechanical aiming and reload delays remain separate.
- WorksStandalone controls independent local reaction. Automatic alone does
  not bypass central evaluation. Explicit manual gun control is not promoted
  to autonomous radar control. Manual engagement orders bypass automatic target
  evaluation but still require normal acquisition and physical firing readiness.
- EG CIWS acquisition starts with a usable assigned sensor observation. Brief
  coast intervals preserve progress; expired measurements and new targets reset
  acquisition. Ships without new keys retain the native parameter fallbacks.
- Native aircraft without a CombatSystem and non-air contact processing retain
  their native evaluation exceptions. This is not a full human decision model.
- Soft-kill delay uses the host reaction band and crew once, independent of the
  fastest gun fitted. Measured contact estimates determine threat priority.
- Missile diagnostics add bounded [EG OODA] queue-state messages and an effective
  policy line. No extra routine startup details are emitted with diagnostics off.
- This update does not change seeker noise/chaff discrimination or missile PK.
Weapon-scoped missile observations (0.10.16)
- Start data and external missile updates now use the actual launch weapon's
  authored sensor assignments. AssociatedSearchSensors are considered in listed
  order, followed by AssociatedSensors as additional search sources, without
  duplicates. Native changes to list order do not change the authored priority.
- An explicit list restricts selection to those sensors. Missing, off, damaged,
  expired or unresolved entries never permit an unrelated sensor fallback.
  With no assignments, the existing automatic measured-contact selection remains.
- TrackSource further restricts the source set; it cannot expand an explicit list.
  Local/shared plotting permissions and recipient self-source exclusion remain.
- High-gain DL sensors remain transport/channel providers, not physical target
  measurements. DL1 own-missile tracking also respects the eligible sensor set.
- Unresolved launch weapon ownership blocks new external observations. Ordinary
  save restoration supplies the native saved weapon ownership. No eligible fresh
  measurement means no new measurement update; an existing assigned-point cue,
  permitted INS/coast and the missile's own seeker remain independent.
- No new INI keys. Optical accuracy, clutter calibration and terminal guidance
  eligibility have not been retuned by this change.
Mission reload
EG clears per-mission tracks, gun solutions and pending worker ownership at native
mission initialization/unload. Native fire orders and completed contacts stay native.
EGOrientStateV1 in saved object sections preserves elapsed OODA processing work,
including queued progress. It is save data, not an INI configuration key. Older
saves use the native ContactsInProcessing conversion; unavailable queued progress
cannot be recovered. Gun solutions/acquisition rebuild from valid measurements.
KETF/ABM bursts orient their visual spark cone along the actual projectile path.
