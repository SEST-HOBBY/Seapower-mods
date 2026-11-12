ExtendedGuidance 0.10.31 - CIWS timing

Existing keys remain in the weapon definition in systems/weapons.ini.
No new weapon key is required.

ReactionTime: seconds of preparation per observed air target. Other targets can
prepare while the weapon engages its current target. Fresh permitted observations
are required; brief coast gaps retain progress. Central processing is not charged
a second time to non-standalone weapons. Actual mount alignment, director takeover,
arcs and a usable fire-control solution remain necessary.

TargetChannels: sensor capacity for simultaneous CIWS target preparation. Uses
existing sensor values, including per-mount AdditionalTargetChannels. The current
target is prioritized, then observed threat urgency. Shared physical sensors share
one capacity; the same target consumes one slot even with several CIWS users.
Native target assignments count toward that same capacity. Unprepared contacts
remain detectable. Losing a slot stops preparation credit, not assessment of
rounds already fired. The usual native default is one when the key is absent.
WeaponChannels is not reused as the background processing limit. Physical firing
and director assignment keep their existing restrictions.

VolleyMaxRounds: maximum delivered rounds before assessment. If absent/zero, the
authored burst duration and rate of fire provide a burst-sized budget. A sufficient
estimated exposure can end a volley at a normal burst boundary; actual target
health is not read for this decision.

VolleyCooldown: maximum per-target assessment wait, capped at 2 seconds in EG.
Explicit 0 disables this wait; smaller positive values are retained. Native missing
value is 15 seconds, so the EG cap gives an effective 2-second fallback.
The wait ends early only after the expected final projectile encounter and a new
usable observation, or when imminent impact requires urgent fire. Other prepared
targets remain eligible during assessment. This is not a thermal cooling model.
APDS uses expected passage, not a fictional detonation.

WorksStandalone and AutoEnableSensor keep their existing roles. Explicit sensor
lists remain restrictive and ordered. Automatic search activation only applies to
explicit operational search radars, autonomous self-defense and native EMCON
permission; unlisted sensors are not enabled by preparation.

F10 CIWS Kills/Fails retain their native override. Non-air targets and local/manual
fire-control paths retain their existing behavior. EG disabled restores native
weapon timing; the additive Mk15 sensor INIs remain normal game data.

Basegame Mk15 package: 26 original vessel files, 47 physical mounts, 48 loadout
bindings. Each mount has one combined radar under AssociatedSensors only. Full Block 0/1/1B
definitions live in AC Pack/systems/sensors.ini; Euromod tuning remains in
sensors_GunFCS_OVWR.ini. Vessel extends live in vessels/Original.
Three differently named Burke Upload aliases are not covered by native extend.
Millennium/Goalkeeper and other CIWS keep their authored sensor assignments.

Validated offline against the saved public and stable-beta assemblies. Actual
firing, sensor scanning and target-switch cadence require in-game acceptance.

Closed-loop spotting (FCTracksRounds=True)

The currently used radar must support round tracking. Guns and CIWS select every
N-th emitted round, with N=max(1,ceil(configured RPM/600)). The counter survives
short pauses and target changes. No additional key is required.
Selected physical rounds provide noisy current-position observations at0.1s
intervals. At least4 samples over0.29s are required. The observer fits its own
motion estimate; it never reads simulation velocity, gravity or a future hit.
Prediction is limited to0.35s and no more than75% of the observed time baseline.
Erased/expired/burst rounds cannot continue producing projectile measurements.
Long-flight observations are limited to the final1.1s before estimated encounter.

Repeated observations of one round refine its estimate without increasing the
number of independent rounds. A short multi-round window estimates a common aim
bias; target uncertainty is retained as a common floor. Significant revised target
maneuvers are rejected as calibration evidence. Existing ammunition dispersion,
physical fuzes, damage and F10 overrides are unchanged.
Calibration uses relative horizontal/vertical laying axes per mount, radar and
ammunition. Target changes do not restore another target's weapon bias. Confidence
and correction fade during observation gaps; sensor/ammunition changes and mission
resets clear calibration. No guaranteed accuracy improvement simply from elapsed
time. Diagnostics include independentRounds, roundStride and groupCorrectionRad.

These observation intervals and prediction limits are simulation approximations,
not published Phalanx hardware settings. Offline regression and controlled model
checks passed; actual gameplay effectiveness still needs an in-game test.

Command guidance measurement correction (0.10.33)
Pure command-guided missiles now include the measured own-missile radar position
error in their control point. The common radar measurement model supplies noise,
geometry and multipath. Target observations retain their original timestamps and
uncertainty. No additional PK roll or seeker penalty is applied to ARH/SARH/IR.
Diagnostics commandTracking shows ownError_m, ownSigma_m and observation age.
