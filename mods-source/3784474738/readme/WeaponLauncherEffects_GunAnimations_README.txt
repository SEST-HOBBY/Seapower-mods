GUN AND CIWS ANIMATIONS
WeaponLauncherEffects 1.0.31

Works with or without ExtendedGuidance. Enable Weapon Launcher Effects in AC Pack.
Restart the game after changing DLLs or model configuration.

Add these existing keys to the unit's [WeaponSystemN] section (Type=Gun or Type=CIWS):

[WeaponSystem5]
Type=Gun
SystemName=YourGun
OpenSystemAnimation=Gun_Open
CloseSystemAnimation=Gun_Close
LoadAmmunitionAnimation=Gun_Reload

Names refer to animations already defined for that unit. The mod does not create
model parts or animation sequences. An existing OVWR may supply the same keys.
There is no SystemOpenAnimation alias; the native spelling is OpenSystemAnimation.

Opening completes before shots are allowed. A new task during closing queues a
reopen after the close finishes. The gun stays open during reload and engagement.

Close starts only after the game's moveToRestPosition succeeds / native rest state
is reached, MoveToRestPositionTime has elapsed, and no task, reload, firing or shared
mount use remains. It does not replace native rotation speeds, angles or rest motion.
There is no additional fixed 10-second CIWS close timer. Missing CloseSystemAnimation
leaves the open mechanism in its authored open pose.

LoadAmmunitionAnimation follows the existing native ReloadTime and reload clock.
It runs once per actual magazine reload, not per shot or burst. Manual and shared
reloads use the same path. No reserve ammunition means no fabricated replenishment.
Animations never change ammunition counts or extend the native reload timer.

Use finite model transform sequences. Looping animations, missing model objects,
nonfinite keyframes, launcher position offsets and SpawnedObject/spawn-callback
sequences are rejected for these gun animations. UnloadAmmunitionAnimation is not
played automatically when an already empty ready magazine is replenished.
Reload clips should finish in the normal usable pose. Avoid competing sequences
controlling the same axes as normal turret aiming or barrel recoil.

Pause and time acceleration follow mission time. Saves record WLEGunPose,
WLEGunPoseElapsed and WLEGunIdleAge; these are save-state fields, not authoring keys.
Old saves remain loadable. Invalid custom clips are skipped with a warning, and
runtime animation failure releases the custom firing gate.

Weapons without valid animation keys retain their existing native behavior.
