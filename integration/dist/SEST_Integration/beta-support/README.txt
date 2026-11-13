SEST WORKSHOP FEATURE UPDATE

The F11 World Operations, service progress, Coordinated Strike refinements
and debrief mission ribbons (for campaigns that define them) are included in
this Workshop item for game build
0.8.7-261107 only, the public beta before Sea Power 0.9.0. On every
other game build, 0.9.0 included, SETUP installs none of it and changes no code.

With Sea Power closed, run SETUP - double-click me.cmd at the pack root.
On that beta build a fresh installation stages the features: launch to the
main menu, wait about ten seconds, quit, then run SETUP again. An enabled
installation is updated in one SETUP run; run SETUP again after Steam
updates this item. On any other game build SETUP puts the normal SEST
plugins back if the beta files are installed.

What SETUP changes on that beta build: it adds SEST.BetaSafeBootstrap.dll to
BepInEx\plugins and SEST's modified Anchor Chain to
BepInEx\config\SEST-BetaAnchorChain, replaces SEST's own plugins in this
item's plugins/ folder, rewrites the Mod Manager order without the local
IdentifyExpanded row (Identify Expanded and this pack stay on) and moves a
local StreamingAssets\IdentifyExpanded folder to
%LOCALAPPDATA%\SEST\IdentifyExpanded. Everything is backed up first under
%LOCALAPPDATA%\SEST\BetaCompatibility. It does not change your Steam
branch, native game DLLs or saves, and it does not force unknown game or
author DLL versions: SETUP then says which file needs a SEST update.

To opt out, run one of these at the pack root (game closed); SETUP then
leaves the features off, also after Steam updates:
  SEST beta features - turn off.cmd   loader off, files kept
  SEST beta features - remove.cmd     normal SEST plugins back, beta files removed
  SEST beta features - turn on.cmd    on again (runs SETUP)
On that beta build Workshop code mods load only through SEST's beta loader,
so with the features off they stay off too; data mods and campaigns work.

Native rendering and gameplay still require PC acceptance testing.
