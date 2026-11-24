Gun firing sound with Launcher Effects

Install WeaponLauncherEffects 1.0.34 and CustomAudioLoader 2.9.6 together, then fully restart Sea Power.

Existing sound settings stay in systems/WeaponAudioClip_Mapping.ini:
[MK45]
WeaponAudioClip=audio/weapons/Gun-MK45.wav
WeaponAudioPosition=0,0,0
WeaponAudioRollOff=Logarithmic
WeaponAudioDistance=1,10
WeaponAudioVolume=1.2
WeaponAudioAudibility=Above

Launcher Effects keeps the muzzle flash, smoke, shell case and animations.
A valid mapped sound replaces the original once per shot. Without an available override, the original firing sound remains available. Explicit empty/None/Off sound values retain intentional silence. Existing audio-mod priority and audibility settings still apply.

Do not delete WeaponEffect_Mapping sections to restore sound. No new mapping keys are required.

