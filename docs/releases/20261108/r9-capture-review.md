# R9 follow-up: 8 November 2026 at 22:23 Brisbane

The supplied capture `SEST-Beta-References-20261108-222324-bde4bd.zip`
contains 331 hash-verified references and no missing entries. Its game hash
is `499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9`,
unchanged from R8's target. Player.log now identifies 0.8.7-261107. The four
recorded installed SEST/Bootstrap hashes match the reviewed R8 payload;
the private loader is also identified as running in the log.

The capture reproduces startup failures in Missile Control 0.1.18, Test
Range 0.2.4 and Optimal Target Distance 1.2.2. The R7/R8 test dispatcher
assumed these updated images could load directly and skipped the older
adapter fixtures. R9 adds current-image adapters and executes the real
current validators/transpilers rather than making that assumption.

The new adapters preserve the author's effective G-limit calculation,
extend only the sensor-hook reflection signature, and permit the fourth
shared-launch timer write. Optional AAW interception stays uninstalled;
its Ready flag remains false. Unknown author hashes are not rewritten.

Seven exact author image hashes which self-rejected their native hook
contracts are held before CLR load. This includes both repeated copies of
Exterior Cameras and Alpine scoped runtime fixes. Native helpers without a
CLR PE directory are excluded before Cecil metadata discovery. No author
Workshop DLL is overwritten.

Repeated Identify stop/surrender broadcasts fail in FindSender after an
unassigned ObjectBase reaches the native IsPlayerUnit getter. Three sites,
including the diagnostic message, now use a taskforce-safe positive predicate.
The actual compiled predicate IL is exercised with null, unassigned, player
and non-player candidates. An unassigned candidate's fake native getter
throws if reached, so the test verifies the guard rather than hiding errors.

The cost screenshot verifies current mission data is visible: AGR-30 is
USD 70,000 and enemy losses include hull and remaining stores. It verifies
neither all campaign-history/debrief behavior nor stable UI rendering.
R9 has not been launched in Unity. The data bundle stays the reviewed
8 November 20:05 configuration snapshot; this capture contains DLL/log
references, not a complete new author configuration export.
