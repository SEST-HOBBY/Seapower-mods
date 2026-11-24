VLS launch effects | Mk41 and Mk57
For Mk41 and Mk57, including Quad, LauncherIgnitionLeadSeconds in
systems/WeaponEffect_Mapping.ini sets the time from vent ignition to release.
The supplied value is 0.30 mission seconds. Set it to 0 for release-time
ignition. Pause holds the countdown. Other launchers use their existing timing.

LauncherEffect starts the vent fire and its full rising plume. Visible vent
flame remains Local. Pale smoke is emitted in World space at sampled flame
births. Normal launchers also emit the short warm head there. Quad versions
use a lower flame and pale plume and omit the warm head. Each Mk57 fire root
samples both existing vent mesh strips. Counts cover both strips together.

LauncherContainerEffect is a filled, spreading deck cloud at the firing cell.
Its .18-second delay starts at successful missile release. Its inner
layer fills the center. The native SmokeEffect fallback uses the same path.
With the supplied timings, deck smoke begins about .48 seconds after ignition.
The rocket ignition sound starts at the cell through CustomAudioLoader and
continues with the released missile. Distance propagation uses the same source
history. If the launch aborts during the lead or subsequently fails, the first
moment of ignition may already have been seen or heard.

One shadowless point light at the vent follows the short-lived exhaust_core
lip through the installed MultiStageMissiles MotorLight extension. Authored
ranges are .21 game units for Normal and .15 for Quad. Smoke keeps its
existing lit materials. It receives nearby light and emits none of its own.

Launcher gameplay caches existing effect and mapping references. Restart
Sea Power before a fresh mission test after installing mapping changes.
