# Dynamic Campaign Mod - static review bundle

Supplied by the user on 10 October 2026. A read-only review of Bungalow's Dynamic Campaign Mod
0.24.0 (DLL SHA-256 `0047b9e6...cd4a3`): metadata and CIL inspection, nothing executed or installed.

Read `REVERSE_ENGINEERING_REVIEW.md` first. `CLAUDE_REVIEW_HANDOFF.md` is the brief that came with
it; `BUNDLE_README.md` is the bundle's own readme. `dll-evidence.json` holds the method names, calls
and strings (including every `CampaignDefinition.Validate` message the SEST validator re-applies),
`selected-evidence.il.txt` short instruction excerpts, `campaign-audit.json` the scoped checks of
the sample campaign.

Every file here matches the SHA-256 in `bundle-manifest.json`. Not copied: the bundle's
`reference-inputs/` (Bungalow's `campaign.json` and `_info.ini`, the author's own files) and the
DLL itself. The SEST adapter took only the schema and the price scale from the sample; see
`../DYNAMIC_CAMPAIGN_ADAPTER.md`.
