# SEST Dynamic Campaign static review bundle

Read `REVERSE_ENGINEERING_REVIEW.md` first. `CLAUDE_REVIEW_HANDOFF.md` is the implementation-review brief for the browser session. `campaign-audit.json` records scoped structural checks, and `dll-evidence.json` records assembly identity, selected methods/calls/strings and persisted-type fields. `selected-evidence.il.txt` contains short instruction excerpts.

`reference-inputs/` contains the user-supplied campaign JSON and INI, unchanged. The third-party DLL and a complete decompiled project are not included. No repository changes or game tests were performed.

To use this in another assistant session, attach the files/archive there. Pasting a `sandbox:/...` URL alone does not transfer the files between sessions.

This is an inspection report, not a mod to install. Static evidence is not a promise of compatibility or a source-code licence.
