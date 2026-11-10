# R10 Topographic Map port

The 23:53 Brisbane capture (`SEST-Beta-References-20261108-235339-dedf89.zip`)
contains 331 verified reference files, no missing entries and the same game
hash `499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9`.
Its log confirms R9 and successful Missile Control/Test Range/Optimal Target
Distance startup. No Identify broadcast send is recorded, so the sender fix
has not been marked gameplay-verified by this capture.

The captured `SeaPowerTopo.dll` is the 1.5.0 globe build, SHA256
`cba22efb544775821c5f5d461a90059225bd5526228d7d6f76e708eeef299619`.
Exactly four native operands fail to resolve: two reads each of the removed
Globals._heightMultiplier and Globals._underWaterDepthFactor. R10 replaces
these four instructions with native fixed factors 1 and 2 in the private
cache. The original Workshop image is retained. The old flat-map variant
stays held before CLR load on this globe game.

The author source independently fixes the removed options at commit
635a7df109a97f8899f235f462bb7f8d44d99803:
https://github.com/struckl/SeaPowerTopo/commit/635a7df109a97f8899f235f462bb7f8d44d99803
The original mod is by Lukas Struckl and the MIT notice is included.

The native ScaleDEMHeight double routine uses a shallow-water boundary in
world-height units equivalent to 50 DEM metres. The old map raster used
48 metres. R10 changes that one metre-domain boundary to 50, retaining all
other raster logic, interpolation, palettes, worker behavior and UI. Passing
raw metre values straight to the native world-unit routine would be wrong;
the adapter does not do that. Tests compare the actual raster arithmetic
with native arithmetic and native unit conversion across all 65,536 signed
DEM samples and additional shoreline/altitude samples. Maximum round-trip
float difference is 0.00390625 m.

All native operands resolve after adaptation. CLR type discovery, the native
map-layer constructor, palette getter and three hook targets pass. The
388 other method bodies retain their behavior. Delayed Noesis map-hook
installation is preserved. No renderer, game entrypoint or Unity mission was
executed locally. PC visual/response checks remain required.

Only the bounded loader payload changes from R9. The existing Runtime/UI,
Identify path shim, Bootstrap, data snapshot, canonical stable upload and
all other feature holds remain. No Steam submission or GitHub push is claimed.
