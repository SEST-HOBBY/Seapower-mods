Provided by CustomAudioLoader.dll. The Missile sounds option controls missile motors, booms and explosions; aircraft audio follows the main Custom Audio Loader switch. Restart after changing options.

CUSTOM AUDIO LOADER 2.7.8 - FLIGHT AUDIO

DistantAudio_Mapping.ini is the shared configuration for jet aircraft, missiles,
sonic booms and the existing additional missile explosion layer. Restart the game.

HOW IT WORKS
FlightAudio.Enabled=True selects the new shared controller. Jets and Missiles
switch the respective MOTOR domains. SonicBoom and its per-source Enabled switches
control shock impulses independently, including unpowered supersonic glide.
Native speed/local sound speed determine propagation, without authored sub/supersonic
motor variants. No loop restarts just because Mach or camera distance changes.

Only an active engine emits motor sound. Stored sound can arrive after burnout or
destruction. The heard position, engine phase, pitch and strength come from emission
history, not the missile's present position. A supersonic source cannot send new
engine sound ahead of its wavefront; earlier subsonic/start emissions may still arrive.
Newly observed sources need their initial sound-travel time to become audible at
distance: the controller does not invent pre-mission emissions.
Both causal roots of a straight supersonic path can contribute. At the shock caustic,
Doppler is bounded (0.65..1.75) and amplitude never diverges. A separate short impulse
represents the shock crossing; it does not run continuously or trigger merely at Mach 1.

One boom per missile launch; jets may rearm after 10 seconds, at least 60 degrees of
heading change and a new approach. A destroyed source retains pending emitted waves.
Paused-camera moves, selection/mode jumps and teleports cannot manufacture connecting
supersonic paths. Continuous camera movement is included in Doppler/arrival geometry.

NATIVE SOUNDS AND MOD ORDER
Jet aircraft use their loaded native engine/far/afterburner clips. Turboprop aircraft
are outside this motor replacement. Missiles prefer the current stage/native motor
clip; NearAudioClip supplies a missing-clip fallback. OverrideNativeNearClip=True
forces that fallback as an explicit replacement. Native looping motor sources are
muted only while the controller owns a valid replacement; original mute states are
restored on release, failure or host cleanup. Wind, sonar, weapon effects and alarms
are not leased. Native launch/booster one-shots remain native; these are not delayed
or looped by this controller. No native prefab/clip asset is modified.

UseNativeASMClips=True keeps the native motor clip also at distance for primary
TargetType=ASuW (including IRCPS). Other rocket missiles use the new reference rumble
at distance. A/B selection and source phase reduce synchronisation. Only the two base
WAVs are needed; distance coloration is a dynamic low-pass, not distance WAV swaps.
Native stage clips remain near; set UseNativeASMClips=False to opt an ASM into the
reference rocket far layer. Credits are in Missile_Distant_Rumble_Readme.txt.

Priority domains: Missiles, Aircraft, SonicBooms, Explosions. A higher enabled mod's
compatible DistantAudio mapping is consumed in game order. Higher-priority explicit
claims in CustomAudioLoader_Priority.ini (Aircraft=True or AllAudio=True, etc.) and
recognised audio assets cause this controller to yield the affected domain.
Higher audio plugins on recognised native hooks also cause yielding. Arbitrary foreign
plugin side effects cannot be reliably disabled. Native resources themselves resolve
through the game's resource loader and retain its mod precedence.

CONFIGURATION
[Motor.Rocket], [Motor.Jet], [Motor.AircraftJet] define source profiles.
[Motor.Unit.exact_ini_stem] overrides the loaded model; [Motor.Unit.exact_ini_stem.StageN]
overrides a MultiStage stage. More-specific sections inherit unspecified keys.
[MotorTypeOverrides] remains supported. MotorType=Auto/Rocket/Jet/Ramjet/Off may also
be set on a unit profile. Ramjet uses the Jet profile. ApplyKinematics=True is only
an automatic rocket classification heuristic, not a speed or burn-state test.
MotorType=Off/Enabled=False yields to native motor sound; it does not disable shocks.

Volume is capped at 1. HalfLevelMetres controls pressure-like distance falloff;
MaxDistanceMetres is a soft-ended range. Near levels are capped instead of diverging.
BlendStartMetres/BlendEndMetres crossfade native near and far clips without restarts.
NearLowpassHz/FarLowpassHz/FilterDistanceMetres control distance coloration.
ForwardGain controls emission directivity; it does not replace propagation geometry.
SmoothingSeconds smooths gain/filter/pitch changes. Doppler uses actual motion rather
than random pitch modulation. Recorded environmental reverb is already in the rumble;
there is no additional long fixed reverb tail masquerading as a burning motor.

Strength multiplies source pressure. MassFlowKgPerSecond explicitly overrides missile
strength; ReferenceMassFlowKgPerSecond sets its reference. Recognized native boosters
use 50% of total missile mass for the booster and 50% for the remaining missile.
Recognition uses the loaded booster effect name containing "booster".
MultiStage missiles with at least two positive stage burn times use 50% each for
the first two burning stages and 20% each for subsequent burning stages. Non-burning
stages do not consume a share. These independent acoustic estimates are divided by
the corresponding burn duration; they are not real fuel masses or a mass balance.
Unknown durations retain a mass-based fallback. Explicit MassFlowKgPerSecond wins.
Other native missiles retain the fuel/acceleration estimate. No physics, burn-state
or sound-arrival gate is changed by this acoustic weight approximation.
Jet aircraft strength follows native throttle/afterburner state. Max range is authored;
mass/fuel change the level inside that cap, not a physically measured audible radius.

LIMITS AND COST
Defaults: 10 geometry updates/real second, 256 tracked sources, 1024 segments/source,
12 motor voices, 4 shock voices and 8 additional impact voices at the default
32 real game voices. Caps are further bounded to 3/8, 1/8 and 2/8 of the
reported Unity real-voice count, leaving a quarter for native audio. Smooth straight sections merge up to 5 mission
seconds. Histories expire after their travel range; the capacity can truncate complex
long paths. Voices are assigned by final layer level, retaining existing selected
loops before assigning new ones. Overload can drop quiet sources/events, with no global
hit/boom cooldown. Pools, cached getters and reused lists limit allocation; no per-frame
global scene scan, terrain ray tracing or worker-thread Unity access is added.

This is a sampled geometric approximation, not a complete acoustic simulation.
No terrain/weather ray tracing, frequency-dependent atmospheric model or calibrated
sound pressure. Pitch is bounded and does not reverse the recording on reversed-time
supersonic branches. Only two strongest branch representatives are retained for a
complex manoeuvring source. Fast time compression/turns reduce accuracy; the source
history clock follows mission time, while looping audio playback uses the audio clock.
Original launch one-shots and explosion events have separate timing.

MIGRATION AND VALIDATION
Separate MissileMotorSupersonic/RocketMotorSupersonic and old ASM profile sections
were removed from this mapping. Older WAVs were left in place. Legacy parsing remains
for another higher-priority mod's older mapping without FlightAudio.Enabled=True.
Alarm and weapon clip assignments are unchanged. Missile motor and explosion levels
are tuned in DistantAudio_Mapping.ini. Exact-DLL offline tests are recorded externally with the build. No new beta
or live Unity listening validation is claimed. Fully restart Sea Power after installation.

2.7.4 AUDIO AND ALARM REPAIR
E-2D and other turboprops retain their native engine sound. Wind/airflow clips are
not replacement motors. NearGain in a Motor profile multiplies the close motor
level, fading to 1 from BlendStartMetres to BlendEndMetres; default 1, valid 0.1-3.
Rocket NearGain=1.5 raises the close level without extending its distant range.
Missile Jet uses Volume=0.45, HalfLevelMetres=400 and MaxDistanceMetres=3500.
AircraftJet has its own unchanged profile. Levels are relative mixer gains, not dB.

[MissileExplosion] uses Volume=0.90, HalfLevelMetres=6000, MaxDistanceMetres=24000 and MixHeadroom=0.80.
The close attack starts at full configured level; no fade-in suppresses the crack.
Visible missile destruction and blastzone events share one per-launch deduplicator.
Duds and discarded weapons remain excluded. A missile water splash alone is not
an explosion. Floating-origin shifts preserve queued and playing event locations.

MaxVoices=8 bounds playing impacts. At capacity, an older tail fades for 25 ms;
its first 120 ms are protected. Due events can wait up to 350 ms after sound arrival,
excluding pause time. Extreme saturation can still omit events. This is a capacity
limit, not a global hit cooldown. Travel delay remains about 2.9 s per kilometre.
Impact priority is 90, motor 100, shock 110 (lower values have higher priority).
MixHeadroom bounds the additional impact mix using cached peak envelopes; it cannot
limit native/foreign sources. No Unity voice-cap setting or WAV file is changed.

Alarm roles are resolved by enum name from the running game. The exact US PAC-3
site override continues to select Incoming_US.wav, independent of mission year.

[FlightAudio] DiagnosticLogging=True writes bounded investigation summaries.
A supersonic-follow camera outside the wavefront can correctly receive no motor
sound, even close to the missile. No motor emission is invented ahead of the cone.
Set diagnostics False after listening acceptance. Fully restart after installation.

2.7.4 LIFECYCLE AND SOURCE DIAGNOSTICS
Destroyed tracked objects stop their owned native motor loops before ownership is
released. Normal release on disable/reset/eviction restores native audio. A reused
missile launch is not stopped by an older track. Previously muted sources, wind,
one-shots and replaced clips are not stopped by terminal cleanup.
With DiagnosticLogging=True, bounded reports list actual playing custom motor clips,
nearby ships' native engine/flow/prop sources, and camera/listener positions. Each
custom boom logs model, object ID, launch, mission time and emission distance, up to
32 entries. The listener lookup runs only during bounded ten-second diagnostics.
Motor profile volumes/ranges remain unchanged; explosion falloff extends to 24 km;
0-1 source volume is not a calibrated loudness or a guarantee for the complete mix.

Impact diagnostics also record detected events, queue/rejection reasons and playback,
limited to 192 entries per game process. The eight-impact voice cap is unchanged.

2.7.8 EXPLOSION ARRIVAL AND POWER-SELECTED CLIPS
PropagationDelay=True follows an expanding sound front against the current camera
path. Moving closer or farther changes arrival; a camera teleport behind an already
passed front does not replay the explosion. Pauses use mission time. Queued fronts
survive missile destruction and expire beyond MaxDistanceMetres. Pending events can
be retained while the camera is initially outside range. Each impulse plays once.

[MissileExplosion] UsePowerBasedClips=True selects clips from the loaded
[WarheadData] Power value, captured once per explosion. Power is a game damage value,
not a stated TNT mass. MediumMinPower=20, LargeMinPower=50 and VeryLargeMinPower=80
are inclusive lower thresholds; smaller positive values select Small. Thresholds
must be finite, positive and strictly increasing; an invalid set reverts to20/50/80.

[Explosion.Small], [Explosion.Medium], [Explosion.Large] and [Explosion.VeryLarge]
contain AudioClips, a comma-separated list of native resource paths or custom WAVs.
The defaults are verified base-game explosion resources. Selection within a list is
stable per event and does not consume the game's random stream. Original effect clip,
volume, pitch, missile mass and warhead type do not select the class. Output uses the
common Volume and distance controls with normal pitch and distance low-pass filtering.
No synthetic reverberation, reflections or separate custom distant explosion is added.

Power0 intentionally emits no explosive bang. Negative/nonfinite/missing Power,
missing chosen clips or queue rejection preserve native playback. One successful
replacement suppresses only the matching missile explosion's original sound layers.
Multiple native callbacks and pooled missile objects cannot create another replacement.
Gunfire, flak shells, fire loops and splashes retain their existing sound paths.
Disabling UsePowerBasedClips leaves the native effects intact; legacy AudioClip-based
additional layers are still supported only when explicitly configured in that mode.

Explosion route coverage
Power selection covers missile HitAir, HitShip, HitGround and HitDefault routes,
including native target-dependent fallback and operator/automatic self-destruction.
High-speed visual replacements retain the same power-selected sound. The original
effect slot is captured before MultiStage substitutes its visual, preventing the
old effect sound from being added again. No visual effect is replaced by this mod.
Non-explosive water splashes and duds remain excluded; gun/flak audio is unchanged.

Range diagnostics include horizontal separation, vertical separation, full spatial
distance and Unity virtual-voice state. Impact playback is checked again after0.2s,
avoiding reliance only on the state immediately after AudioSource.Play.

Pilothouse compatibility
When Sea Power Pilothouse is loaded, CustomAudioLoader applies its own distance
and source level first, then Pilothouse's current bridge settings. Pilothouse's
EngineVolumeMultiplier covers custom aircraft and missile motor voices;
AircraftVolumeInside also recognizes detached aircraft motor and boom voices.
Missile booms and explosions remain exterior sounds and receive the bridge's
normal exterior filtering. Own-ship alarms use their ship identity for
OwnAnnouncementVolume; nearby other ships are not treated as the own ship.

No additional INI switch is required. Change bridge sound settings in Pilothouse.
Entering/leaving the bridge, toggling muffling and reusing pooled voices retain
separate base and bridge gains. Custom sound positions remain at their acoustic
emission locations. Pilothouse is optional; unsupported adapter layouts are logged.
Restart the game after installing either DLL. No Pilothouse Workshop files are changed.



Rocket near launch and loop (2.9.5)
Motor.Rocket uses Missile_Rocket_Launch.wav (first0.42s of the supplied base-game
Surface to Air Missile Launch1) and a mono,level-matched copy of the requested
Missile-Large_MotorLoop.wav. The original source loop is unchanged.
IgnitionCrossfadeSeconds=0.42 starts the equal-power transition immediately.
IgnitionNearOnly=True limits the launch transient to the near layer; distant
motors continue normally. No initial intro-only hold interval. Cold-launch and
once-per-launch gates remain; aircraft and turbojet profiles are not assigned it.
Empty IgnitionAudioClip or IgnitionGain=0 still bypasses the optional start sound.

The existing stage acoustic mass/burntime estimate scales both layers together.
It is an authored proxy for source strength,not a measured thrust/SPL model.
One burning MSM stage uses its full acoustic mass and actual stage burntime.
With multiple burning stages,the first two use50%acoustic mass,additional stages20%;native boosters
follow the existing split. No extra multiplier or size-based pitch stretching.
Small/long-burning motors can be quieter; shorter/higher-flow burns stronger,
within the existing gain cap. Preserve native aircraft/turbojet pitch. Fixed
near overrides use pitch1; original ASM far sound retains its original pitch.

New missile voices without the transient use StartSmoothingSeconds=0.01 for
initial settling (about95%in30ms at a constant target); later movement uses the
existing SmoothingSeconds=0.15. Launch transient sources start at target gain
and their WAV contains a3msedge fade. Frame sampling and causal propagation still
apply. There is no claim of zero physical travel time or live hearing acceptance.
Native SA-N-6/9 cold-ejection exceptions still require actualSustainer ignition.

Sonic boom output (2.9.4)
Both hosts share a bounded one-shot pool. Per-frame 30ms gain/filter smoothing follows the camera; trajectory/delivery timing is unchanged. MixHeadroom=0.80 bounds the conservative sum of upcoming dry sample peaks of this pool, with fast reduction and 200ms recovery. This is not a limiter on the whole game mix. SmoothingSeconds is configurable from0.01 to0.15. Pilothouse is applied after these base levels. WAVs use two finite N-wave edges with no added echoes; sharp attacks remain intentional.

