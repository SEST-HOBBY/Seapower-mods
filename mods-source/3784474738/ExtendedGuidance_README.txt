ExtendedGuidance 0.8.7 -- AC Pack

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
gun solutions remain native. Missiles read existing native contact estimates.
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
native. ESM, visual/sonar contact discovery, TV/laser guidance, guns and unguided
weapons retain their own models. Existing information/point-value estimates are
not combat outcome simulations. Multipath is not implemented.

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
SeekerCoastTime: seconds without measurement before loss, 0..30.
SeekerAcquireTime, SeekerReacquireTime: detection dwell, seconds, 0..10.
SeekerUpdateInterval: missile measurement interval in simulation seconds,
  0.02..2; default 0.1, IR default 0.05. Native steering continues between samples.
SeekerReferenceRange: nm for SeekerReferenceRCS, 0..300; zero derives sensitivity
  from native ARH power/gain/wavelength, bounded by native SeekerActiveRange.
SeekerReferenceRCS: reference cross section, m2, >0.
SeekerReceiverSensitivity: SARH/passive receiver threshold, watts, >0.
SeekerAngularResolution: angular error/resolution, degrees, >0..10.
SeekerAngularGate: angular association width, degrees, >0..90.
GroundClutterSigma0: land backscatter coefficient, dB, -80..0.
SeaClutterSigma0: sea backscatter coefficient at sea state 3, dB, -100..0.

IR keys
IRReferenceSignature: reference native IR intensity, >0; default 100.
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
FCSolutionGainRate, FCMinSolution and FCTracksRounds keep their native behavior.

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
TrackSource: Auto uses the native contact estimate. An exact on-platform sensor
SystemName restricts acceptance to an estimate reported by that sensor; a different
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
Two rotating files, each at most 8 MiB; missiles at most 2 Hz, launchers at most 1 Hz
of simulation time. Bounded background file writer, 300 lines/wall-second cap;
dropped records are reported. Logged truth positions are comparison data only.

Limits
Profile values are empirical simulation settings, not measured weapon performance.
Surface defaults, IR contrast/shape discrimination and RF association need gameplay
calibration. No multipath, detailed waveforms, thermal imagery, adaptive nulling,
individual flare trajectories or detailed range-deception jamming are modelled.
Existing combined chaff/IR decoys retain native positions and lifetimes.
One bounded numerical worker handles immutable snapshots; Unity reads, ECS writes
and event publication stay on the main thread, with equivalent synchronous fallback.
Saved EG contacts recover serialized measured positions conservatively. Detailed
missile acquisition history resets on reload and uses the saved native flight cue.
Final-binary offline model/API tests cover installed public build 26103404 and the
available beta assembly. Actual gameplay acceptance in both remains pending.

SARH recovery (0.8.1)
- EG SARH missiles against air targets retain a bounded recovery period after
  loss of terminal guidance. A valid local echo does not require a datalink.
- Recovery uses existing seeker coast/acquisition settings and SelfDestructDelay;
  datalink missiles may continue toward their estimated intercept, capped at
  30 seconds without reacquisition. No new configuration keys are required.
- Existing FCR reservations survive temporary loss of visibility; actual RF
  measurements still require coverage and native antenna alignment. Native
  channel limits, manual disable, geometric misses and lifetime limits remain.
- These recovery limits are simulation assumptions, not published SM-2 timers.

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
