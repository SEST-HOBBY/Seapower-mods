Custom Audio Loader 2.9.1

AC Pack Settings -> Audio and interface -> Custom Audio Loader
The main switch controls all custom audio below. Fully restart Sea Power after
changing a switch. All three child options default to enabled.

Alarms: ship, SAM-site and airbase alarms, including crew announcements.
Sonar: custom sonar pings. Torpedo and noisemaker motors remain independent.
Missile sounds: missile motors, missile sonic booms and missile explosions,
including impacts, self-destruction and high-speed destruction effects.
Turning an option off leaves the corresponding original game audio available.

Gun, CIWS and launcher sounds stay enabled whenever the main switch is enabled.
Jet audio and aircraft sonic booms are independent of the Missile sounds option.
Mapping Enabled flags and mod-order priority continue to apply to every domain.

CustomAudioLoader.dll contains all these features and external WAV loading.
CombatAudio.dll is retired; do not keep an older copy alongside this loader.
The former combat-audio preference is no longer used. Existing preferences for
other modules are preserved.

Files in systems:
AlarmAudioClip_Mapping.ini - national, historical and model alarm profiles.
DistantAudio_Mapping.ini - missile/aircraft flight, boom and explosion settings.
WeaponAudioClip_Mapping.ini - weapon, CIWS and launcher replacements.
SonarAudioClip_Mapping.ini - sonar pings.
TorpedoAudioClip_Mapping.ini - torpedo motors.
NoisemakerAudioClip_Mapping.ini - noisemaker motors.
CustomAudioLoader_Priority.ini - audio-priority overrides.
Distances in alarm/distant mappings are metres. See NavalAlarm_Readme.txt and
FlightAudio_Readme.txt for detailed configuration.

Optional manual settings, in the game's persistent Mods/ACPack/submods.ini:
[Submods]
io.github.euromod.sonar-audio-loader=true
io.github.euromod.sonar-audio-loader.alarms=true
io.github.euromod.sonar-audio-loader.sonar=true
io.github.euromod.sonar-audio-loader.missiles=true

Pilothouse remains optional and processes supported added sounds downstream.
Its manual General Quarters command is independent of this mod's Alarms switch.
Crew announcements remain spatial ship sounds; player voice lines are unchanged.
