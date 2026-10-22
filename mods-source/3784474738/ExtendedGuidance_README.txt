ExtendedGuidance 0.4.0 -- AC Pack

Restart Sea Power after installing or changing configuration. This DLL follows
AC Pack's Mod Manager checkbox AND its ExtendedGuidance submod switch.
ExtendedGuidance defaults to off in the AC Pack submod menu. Enable it there,
then restart Sea Power. Existing saved choices are preserved. Normal startup:
[ExtendedGuidance] bereit.

Scope
AAW active-radar, semi-active-radar and pure infrared missiles against airborne
targets, including SAMs defending against incoming missiles. ASMs, surface
engagements, group-capable/grouped missiles and combined passive-RF/IR seekers
(such as the Euromod RAM family) retain native guidance. Propulsion, steering,
fuzes, damage and native reliability remain in use. No multipath.

Configuration priority, independently for each key
1. Effective ammunition INI: [ExtendedGuidance], immediately after [Guidance].
2. systems/ExtendedGuidance_OVWR.ini: [ammunition_filename_without_ini].
3. Fixed profile in systems/ExtendedGuidance_Profiles.ini.

Enabled=True/False controls one missile type. SeekerProfile=Auto can override
an explicit mapped profile while retaining numeric per-key overrides.
Aliases and extend files use the game's effective INI resolution.

Example missile section:
[ExtendedGuidance]
SeekerProfile=IIR_Imaging
SeekerCoastTime=0.8
SeekerUpdateInterval=0.05

The same keys work in an OVWR section, for example:
[example_ir_missile]
SeekerProfile=IR_AllAspect_IRCCM
SeekerAngularResolution=0.08

IR profiles: IR_RearAspect, IR_AllAspect, IR_AllAspect_IRCCM, IIR_Imaging.
Rear-aspect restrictions take precedence in automatic classification.
Explicit AntiCountermeasuresBonus selects a fixed conventional IR/IRCCM profile;
otherwise TargetMemory with IOCDate (FOCDate fallback) can select IRCCM.
Dates and native penalties do not scale physical model parameters. Auto never
infers imaging. Explicit AIM-9X, PL-10 and IRIS-T mappings select IIR_Imaging.
KillProbability and SpoofChance are not inputs to the new seeker decisions.

IR keys
SeekerAngularResolution: angular resolution, degrees, >0..10.
SeekerAngularGate: angular association width, degrees, >0..90.
IRReferenceSignature: reference effective IR intensity in native signature
  units, >0; default 100. SeekerPassiveRange supplies its reference range.
  A positive SeekerReferenceRange overrides that reference, in nautical miles.
IRBackgroundRejection: background rejection fraction, 0..1.
IRBrightnessRejection: rejection of sudden bright-source changes, 0..1.
IRShapeRejection: resolved angular-size consistency weight, 0..1.
SeekerTrackRate, SeekerAcquireTime, SeekerReacquireTime, SeekerCoastTime and
SeekerUpdateInterval also apply to IR. Default IR sample interval is 0.05 s.
Native SeekerFOV, SeekerGimbalFOV, IsRearAspectOnly and TargetRearCone apply.

Radar profiles: ARH_Generic, ARH_PD_Early, ARH_PD_Standard, ARH_PD_Advanced,
ARH_AESA, SARH_Generic, SARH_Generic_Early, SARH_Generic_Advanced, SARH_Pulse,
SARH_CW_Early, SARH_CW_Advanced, SARH_PD_Early, SARH_PD_Advanced.
Legacy AMRAAM_Active, AMRAAM_Advanced and Sparrow_M names remain accepted aliases.
Missile-specific calibration belongs in missile or mapping overrides.
Radar Auto uses authored altitude/speed/size penalties and IOC/FOC to choose
one fixed profile. It never infers AESA or a particular SARH waveform.

Numerical keys and units
SeekerBeamWidth: full antenna beam width, degrees, 0.2..90.
SeekerSidelobeSuppression: dB, 0..80.
SeekerRangeResolution: echo resolution width, metres, 0..10000; zero disables
  range separation of clutter. It does not set the tracking association gate.
SeekerRangeGate: tracking association width, metres, 0..20000; zero disables it.
SeekerDopplerGate: tracking association width, m/s, 0..2000; zero disables it.
SeekerManeuverAllowance: process acceleration uncertainty, m/s^2, 0..300.
SeekerDopplerResolution: equivalent radial speed width, m/s, 0..500;
  zero disables Doppler discrimination.
SeekerClutterRejection: residual rejection outside the clutter notch, dB, 0..80.
SeekerTrackRate: angular tracking rate, degrees/second, >0..2000.
SeekerCoastTime: seconds without measurement before track loss, 0..30.
SeekerAcquireTime, SeekerReacquireTime: continuous detection dwell, seconds, 0..10.
SeekerUpdateInterval: simulation seconds between measurements, 0.02..2;
  default 0.1. Steering continues each native update using the track prediction.
SeekerReferenceRange: nautical miles for SeekerReferenceRCS, 0..300;
  zero uses native ARH gain/power/wavelength, with the reference-target detection
  range bounded by native SeekerActiveRange. Positive values set an explicit
  reference sensitivity. Neither mode changes the native maximum seeker range.
SeekerReferenceRCS: reference cross section, square metres, >0.
SeekerReceiverSensitivity: SARH receiver threshold, watts, >0.
GroundClutterSigma0: land backscatter coefficient, dB, -80..0.
SeaClutterSigma0: sea backscatter coefficient at sea state 3, dB, -100..0.

Behavior and limits
Owned shots bypass native Pk, probabilistic decoy/ECM decisions and forced-miss
terminal deviations. Actual fuze encounters and native damage still decide hits.
Native prelaunch hit-chance estimates/UI percentages are not replaced.

Radar ground/sea clutter works with LowAltitudeClutter=Off. FCR channel,
operating-state and native arc/alignment constraints remain. Numerical FCR
tracking handles LOS, signal, clutter and combined decoys; the old Chaff
collider-blocking decision is bypassed for owned shots.

IR uses existing target signature, native engine/aspect scaling and relative
bearing measurements. It does not observe true target range or velocity.
Range starts with launch/support information and is propagated. Imaging uses
an angular-size/temporal approximation, not rendered thermal imagery. Background
contrast uses bounded sky/land/water categories, not detailed clouds or terrain
temperatures. Combined decoys share native positions and lifetimes. Their IR
intensity has a simple rise/decay envelope; individual flare trajectories are
not simulated. Profile values are empirical game parameters, not measured
hardware specifications. RF jamming does not affect pure IR measurements.

Event log
TRACK LOST, REACQUIRED, SPOOF and final MISS/ENGAGEMENT ENDED use native event
numbering, time, weapon/launcher/target IDs. Loss is debounced; normal updates
produce no log spam. Reacquisition clears old loss causes. Decoy capture requires
an actual tracked-source change. Native hit/damage logs are retained. A failed
shot with an uncertain cause is labelled accordingly, not automatically evaded.
Available native outcome hooks distinguish hits, interceptions and operator
self-destruct. Older builds without an exposed warhead-failure flag cannot
provide that specific diagnostic. No global game/foreign-mod log filtering.

One numerical worker evaluates immutable snapshots; Unity reads and event-log
writes stay on the main thread. Track histories reset on reload/time reset and
are not serialized. Offline model/API tests are not in-game acceptance evidence.

Datalink and radar mapping
Add radar sections to systems/ExtendedGuidance_OVWR.ini:
[Radar:example_datalink]
GuidanceRole=Datalink
TrackSource=Auto

GuidanceRole accepts Auto, Datalink or Radar. An explicit mapping takes priority
over native DatalinkGuidance and the raw INI Gain > 200 dB fallback. TrackSource
accepts Auto or an exact sensor SystemName on the launching platform. Explicit
sources are restrictive: an unavailable named source is not silently replaced.
Auto prefers associated sensors with usable tracks and retains similar-quality
sources to avoid switching repeatedly. No off-platform cooperative engagement
or satellite relay is inferred. Known real radars above 100 dB are explicitly
mapped as Radar; their nonphysical gain is bounded by authored MaxRange at 2 m2.

One native radar paint can feed several missiles, but only for the same radar
instance and target. Each missile retains its own received update, radio path,
local seeker geometry, clutter, chaff candidates and acquisition history.
Search-radar paints keep their native cadence; prediction never refreshes the
measurement timestamp. Native detection is a prerequisite for platform reports;
ExtendedGuidance adds its own signal/clutter/decoy checks to those reports.

DL systems retain native weapon channels and compatibility. Their MaxRange is
used as the sender-to-missile radio limit, with terrain/horizon checks. No extra
unverified radio latency or packet-loss model is imposed. Existing timestamps
and simulation scheduling remain effective. MidCourseCorrection=1 additionally
checks physical radar coverage/signal for its own assigned missile (the generic
CanDetectAirToAirMissiles search exclusion does not apply); mode 3 does not require
that missile radar return. SARH separately needs a real compatible illuminator.

Seeker activation starts local acquisition without removing DL support. A
confirmed local track takes precedence, including a locally captured decoy.
After local loss, a permitted external track can cue reacquisition. External
updates never create local lock or automatically identify chaff. LocalTerminalOnly
cuts further external updates on entry into TerminalApproach, while allowing
prediction from information already received. Otherwise support may continue.

Radar seeker antenna behaviour (0.5.0)
Uses existing keys only. SeekerAntenna chooses Mechanical or AESA.
Mechanical steering consumes time at SeekerTrackRate degrees/second. AESA steering settles within one model update; SeekerTrackRate still bounds the existing tracked line-of-sight acceptance.
SeekerAcquireTime/SeekerReacquireTime require detectable measurement time after steering. SeekerCoastTime retains the existing track-memory behaviour.
SeekerBeamWidth is full one-way half-power width. The simplified fixed-panel AESA model applies projected-aperture gain loss and beam broadening off axis, bounded by native SeekerGimbalFOV. Native SeekerFOV limits acquisition/search.
Search follows the supplied cue/estimated uncertainty, using one shared beam for all candidate echoes. No antenna type bypasses clutter, jamming, line of sight or measurement requirements.
This antenna model applies to radar missile seekers only. Platform radars retain their separate native-observation-based model. No detailed waveforms, adaptive nulling or mechanically repositioned AESA panels are modelled.
