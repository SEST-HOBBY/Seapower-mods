# R12 world-battle preparation and exit presentation

The owner reports the rest of R12 looks good and requested clearer battle
setup plus an explicit way to end an unsuccessful/unfinished world battle.
The 9 November 19:10 capture contains the expected R12 Runtime/UI hashes,
world integration startup, normal battle return and normal game shutdown.
All 331 captured reference sizes and SHA256 hashes were checked successfully.

UI Follow-up 1.4.10 adds a native message-box checklist at the beginning of
a fully loaded, paused world battle. Start preparation dismisses it while
leaving the simulation paused. The player arranges aircraft/loadouts,
formation, courses, sensors and weapon status, then explicitly unpauses.
The checklist includes the exit route. A new GameMain/replay receives its
own opening; a mid-battle save or an already unpaused game is not interrupted.

The native pause-menu Exit caption becomes End battle... for a live DCM
battle only. Its original command object, enabled state and visibility are
preserved. The original command opens the normal debrief, and DCM's existing
return-to-campaign confirmation retains its full warning. A short prefix
explains that victory is not required and leaving does not undo combat or
grant a win. Quit-game confirmations and ordinary mission menus are retained.
No result, combat, auto-resolution, service-award or campaign-state logic is
replaced. The optional integration requires the inspected DCM hash.

Only SEST.ContactsFix.dll changes from the previous R12 payload. The Runtime,
loader, bootstrap and Identify shim are byte-identical. The updated feature
archive is included in the canonical Workshop tree and uses the existing
stage/repair/restore workflow. Existing R12 repair provenance is retained.

Managed tests exercise opening/replay/load gating, real captured bindings,
original exit-command identity, native availability and retention of the
full author warning. Installer fixtures exercise the R12 upgrade and rollback.
New native rendering and user interaction still need the focused PC checks
below; the previous R12 playtest is not presented as testing this change.

1. Close Sea Power and run Repair-PC.cmd from the updated full toolkit.
2. Start a world battle while paused. Check the checklist, Start preparation,
   flight-deck/formation setup and explicit unpause. Recheck a replay.
3. Use Esc > End battle... before victory. Check the debrief and full campaign
   warning, cancel once, then confirm return. Check the report and save/load.
4. Confirm a mid-battle load is not interrupted. Quit and run
   R12\Capture-Repair-Results.cmd for the follow-up capture.
