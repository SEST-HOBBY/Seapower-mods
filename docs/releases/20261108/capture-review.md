# 8 November capture review

Base: private release commit `be631deafd8a357372c126d30707d8f72737aef5`.
Capture: `SEST-Workshop-Capture-20261108-200546-FULL.zip`, containing the
configuration review and `SEST-Beta-References-20261108-200849-2c2101.zip`.
The supplied initial text ZIP and the corresponding FULL section are byte-identical.

Inventory: 204 Workshop folders (203 dependencies plus SEST), no missing
canonical IDs, 94 changed/new files, 14 deletions, no capture-stage failures.
The 110 DLL hash records match the 7 November snapshot. The actual managed
game DLL does not: `9b35a7aa...` becomes `499675cd...`; the Steam build record
changes from 26479221 to 26502734. The captured Player.log label is still
0.8.7-261106, so R8 identifies its target by the exact assembly hash rather
than inventing another version label. Noesis remains `7b1fd6a6...`; Combat
Cost Tracker 0.8.0 remains `8f7195ff...`.

The seven author updates are Modern US Navy (3390330875), Mogami
(3456859157), PLAN (3775128499), South Korea (3789208859), India
(3807164392), Hyundai Export Ships (3812454152), and Modern RAN (3820759806).
Raw author bytes and explicit deletions are imported before rebuilding.
The RAN's root `ran_ffg_mogami_improved` outranks the standalone Mogami copy
under the existing order; the winning-source builders select it. Nested
Testing/WIP files remain non-root definitions. No subscription or order was
changed.

R8 adds one native API bridge beyond R7: the captured Dynamic Campaign Mod
night-sensor query appends the new optional `nation=null`. Native method
metadata, the exact written call, all admitted direct native references and
runtime/UI bindings are checked. The five candidate DLLs remain separate
from canonical stable code. Native rendering and gameplay are not tested.
