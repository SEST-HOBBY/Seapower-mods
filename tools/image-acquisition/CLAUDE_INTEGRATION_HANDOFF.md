# Claude handoff — SEST gallery image additions (read-only first)

Repository: `SEST-HOBBY/Seapower-mods` (default/deploy branch observed as `feature/northern-front-iii-export`; do not assume `main` is the deployment target).

## Objective

Finish the photo gap and quality overhaul using *real, appropriately licensed photography*. A compiled acquisition/research queue is in `SEST_IMAGE_MASTER_20261014.csv`. Do not use AI-generated images. Do not duplicate class photos by variant; use credited aliases and transparent `exact_photo`/`exact_class_photo`/`family_reference`/`context_reference`/`authorized_mod_render` designations.

## Review and validation sequence

1. **Read-only compare first.** Review the latest `data/load-order.tokens.txt`, `docs/mod-catalog.md`, `mods-source/`, `integration/gallery/source/data/mod_coverage.csv`, `unmapped_entries.csv`, `unit_image_mapping.csv`, `photo_priorities_fielded_units_191.csv`, `integration/gallery/source/catalogue.js`, `PHOTO_CREDITS.txt`, and image build scripts. Confirm which additions are *actually* in the latest git tree. Do not conflate installed Workshop count and canonical entries including SEST.
2. **Anduril** Workshop `3819522350`: ask for/inspect the current PC export if absent. Resolve *all ten* real unit IDs for Dive-LD, Dive-XL, Copperhead-100/500 and K5 KRAKEN. Alias variants to 4-5 recognizable family images, rather than inventing filename/INI identities. Explicitly account for the Dive-XL SU variant if present. Do not ship the supplied Workshop screenshot or Anduril website art as a public asset without rights evidence.
3. **Rebuild inventory.** Re-run gallery alignment using the latest winning unit definitions. Audit removed/modded units, including any changed Korea, V-22, Flight Deck Ops, strategic missile and Russian SAM files. Don't treat ammunition, animations or sensor config sections as independent photo-required vehicles.
4. **Select licensed photographs.** Import files only from `downloaded/verified_file_pages` or manually approved `downloaded/REVIEW_REQUIRED`; source each file's Wikimedia Commons description page and licence metadata. A search result title or a Commons category *alone* does not prove rights or exactness.
5. **Credits and manifests.** Update source catalogue assets with creator/licence/source page/sha256/dimensions, credit block, image exactness, replacement history and actual image_file mapping for each physical unit. Resolve class-level aliases without cloning identical image bytes; identify and remove stale images/mappings. Existing `apply_added_photos.py` has a constrained `NEW_CATEGORY` map and may need a controlled extension for new IDs.
6. **No direct deployment yet.** Write changes on a new `feature/*` branch; leave `main` untouched. Do not include AI attributions in Git commit/PR bodies. Rebuild `integration/gallery` and `integration/dist` only after source approvals. Run existing gallery build/check scripts, `tools/build_all.py --from-scratch`, preflight and tests; compare outputs and inspect at least one random asset for each category before proposing a PR. Distinguish script-checked from playtested behavior.

## Current snapshots

- The gallery's legacy prioritized actions: 89 rows, many are family/context references rather than 89 unique photos.
- Master dataset: 116 mapped actions (89 legacy + 27 additions); 110 unique suggested asset groups before reconciling against the *full* existing 517-photo catalogue.
- 13 pinned Commons file pages (12 licences verified online), 39 Commons categories, 46 search queues, 7 holds, 5 permission holds and 6 reuses.
- The current gallery README says 190 Workshop mods / 517 photos / 601 encyclopedia pictures; new canonical count from 13 Oct was 195 Workshop mods, and the new Anduril mod has not yet been confirmed exported/committed.
- Store snapshot/build commit and newly verified mod IDs in manifests rather than in generated filenames (rename the stale `photo_priorities_fielded_units_191.csv` by introducing a stable alias and updating HTML links).

## Expected result

A reviewable PR containing an updated 2026-10-14+ gallery catalogue and unit-photo mappings, an actual approved assets folder and full attribution records, reproducible tests, and an explicit list of still-missing systems. Not a blind bulk import of every visually similar image.
