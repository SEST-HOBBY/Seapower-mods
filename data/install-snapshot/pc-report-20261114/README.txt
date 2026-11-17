The PC's report of 14 Nov 2026, as the owner sent it.

These are the eleven files of SEST-090-UPDATE-REPORT.zip (SHA-256 db094655c8a3bda7e64e3e0414db1ec91324c0ad20468e1bdce6bf383dceba00), written
on the gaming PC at 2026-11-14 07:57 +10:00 by a read-only capture of its own,
not by tools/capture-context.ps1. Their line ends are LF here; nothing else is
changed. The PC's tool had redacted personal paths before it wrote them.

What it compared: the text files of the 200 installed Workshop folders with
data/mod-fingerprints.json at commit 01cfa43b (baseline-used.json is that
file). It marks 77 mods UPDATED. 59 of them differ only in the
ApproximateVersion line SEST's own SETUP writes into an installed _info.ini
(the "SEST marked this mod compatible" line), which is not an author's
change; mods-source keeps the author's file. 18 are authors' updates, and
their text came with the report in SEST-UPDATED-MOD-TEXT-part01.zip and
-part02.zip (SHA-256 bd8cc284de13b72c223f3a6b3eab9ab4c66b8f1f6166a3071c50b78a27777aa1
and 194d678ce6bca779cc0abe26baf69f65d0813a41eafbed4251f62359b5136ca1): they
are in mods-source, taken in the same commit as this folder.

What it shows of the game: Player-log-excerpt.txt is a launch of
0.9.2-261113b and Player-prev-log-excerpt.txt of 0.9.1-261112b, so the game
has moved twice since the 0.9.0 Build 261111 export in mods-source/_vanilla.
pc-state.txt gives the SHA-256 of that 0.9.2 game's Seapower-Scripts.dll.
The tool did not find the game's changelog. BepInEx-log-excerpt.txt is still
the log of the 12 Nov launch (0.9.0), so BepInEx wrote no log in the two
later sessions. vanilla-paths-not-on-disk.txt lists ten files of the 0.9.0
export that the installed game no longer has.

The other files of data/install-snapshot/ are the 12 Nov capture and are
not replaced by this report.
