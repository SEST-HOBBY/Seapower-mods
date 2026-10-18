# SEST Sea Power — Image Acquisition Pack (14 October 2026)

## What this pack is

A prepared, **non-invasive acquisition package**, based on the connected GitHub repository `SEST-HOBBY/Seapower-mods` and the SEST gallery's existing missing/weak-image priority list. It is **not** a finished archive of image binaries: network access to Commons image bytes was not available in the artifact-building environment. The included launcher downloads eligible media directly from Wikimedia Commons **on your Windows PC**, verifies file-level licensing through Wikimedia's API, and creates a local image contact sheet plus attribution list. No AI-generated images are included.

**Coverage:** 89 original `NO PHOTO`/`WEAK PHOTO` priority rows + 27 October addition/family rows = **116 unit-image mapping actions**, deduplicated into **110 distinct image groups** (these figures describe the *audit*, not 116 new image files). Sources are divided into:

- **13 pinned Wikimedia Commons File pages:** individually inspected online. The script **rechecks each current file licence** before downloading into `downloaded/verified_file_pages/`.
- **39 category-based source pools:** download the best licensed, photo-like result into `downloaded/REVIEW_REQUIRED/` only. **Do not treat category membership as confirmation of exact configuration.**
- **46 Commons search queues:** find possible licensed images but treat them as **unapproved candidates**, again inside `REVIEW_REQUIRED/`.
- **6 duplicate/reuse actions:** share the approved parent-class image.
- **7 unsourced/fictional/concept holds:** no misleading 'real' photograph.
- **5 Anduril copyright/permission holds:** no automatic scraping of proprietary official or Workshop images.

The 89 legacy rows were directly reconciled with `integration/gallery/source/data/photo_priorities_fielded_units_191.csv` on the repo's `feature/northern-front-iii-export` branch. The original gallery README described **517 photographs, 88 flags, 12 loading-screen backgrounds, and 190 Workshop mods**. October's canonical load-order work had reached **195 Workshop mods** before the new Anduril item was exported; Anduril `3819522350` is a *pending next-export* addition, not proof the repo already contains its files.

## Get the actual photographs on Windows

Extract the ZIP and run **`RUN_WINDOWS.cmd`** (double-click) or open PowerShell in this directory and run:

```powershell
py -3 .\fetch_images.py --mode all
```

This is standard-library Python; there are **no pip packages to install**. Python 3.9+ is recommended. It downloads a suitable image only if Commons reports a compatible licence and supported raster format. Each image receives its source URL, author, licence, image checksum, original dimensions and review state in `ACQUIRED_IMAGES.csv`. No game files or GitHub branches are touched.

Run *only* the 13 pinned File-page sources first, if preferred:

```powershell
py -3 .\fetch_images.py --mode verified
```

Or additionally acquire images from the 39 targeted subject categories, but not the looser searches:

```powershell
py -3 .\fetch_images.py --mode categories
```

The downloader may take several minutes and may reject candidates when Commons metadata is incomplete, a category has only drawings/models, or a download fails. That is intentional. An unavailable or poor source remains in `PENDING_IMAGES.csv` rather than being silently replaced with unrelated imagery. The script uses no third-party image search and doesn't fabricate new image content.

After downloading, open **`CONTACT_SHEET.html`** to review the actual pictures. In particular, look for photographs that depict the right *variant*, *operator*, *era* and *installation* rather than simply a similar-looking system. Preserve `ATTRIBUTION_CANDIDATES.md`, especially for CC BY / BY-SA images. Commons' licence can vary by file; files in a category are not necessarily uniformly licensed.

## Files in this pack

| File | Use |
|---|---|
| `SEST_IMAGE_MASTER_20261014.csv` | Master of all 116 original gap/addition actions with units, group, source, exactness, priority, notes |
| `IMAGE_SOURCING_INDEX.html` | Offline searchable index with hyperlinks and remote preview thumbnails for individually sourced File pages |
| `PINNED_VERIFIED_FILE_PAGES.csv` | 13 pinned Commons File pages, 12 with web-checked licences |
| `ANDURIL_VARIANT_RECONCILIATION.csv` | Five family assets pending the new mod's **10 actual INI variants** |
| `fetch_images.py` | Download and metadata/rights gate; produces photos, contact sheet and full file-level credits |
| `build_master.py` and `build_preview.py` | Recreate the static CSV and HTML from the research rows |
| `legacy_gaps.tsv`, `additions.tsv`, `curated_sources.tsv` | Source datasets for maintenance |
| `CLAUDE_INTEGRATION_HANDOFF.md` | Practical, read-only-first guidance for use with existing SEST repo |
| `private_reference/Anduril_Workshop_Page.png` | Screenshot supplied in conversation, **NOT a cleared game/gallery asset** |

## Anduril Maritime: Unmanned Fleet

Workshop item: `https://steamcommunity.com/sharedfiles/filedetails/?id=3819522350`.

Five visual families need asset records: **Dive-LD**, **Dive-XL**, **Copperhead-100**, **Copperhead-500**, **K5 KRAKEN**. Actual internal unit/variant identifiers must be extracted from the latest Steam-exported mod — the author lists ten vehicle variants, but guessing their filenames is inappropriate. Some variants may share one family image.

Original equipment photography from Anduril's website, or Alpine's in-game screenshots/renders, is **not automatically redistributable**. Contact the owner/author or verify a licence before putting exact photos/models in public releases. The screenshots in this pack are reference-only. A generic AUV may be a *context* photograph, but should never be labelled Dive-XL or K5 KRAKEN.

## Integrating into SEST safely

This acquisition ZIP does not write to `integration/gallery/source/` or `integration/dist`. The existing `integration/gallery/apply_added_photos.py` currently requires known `asset_id` values, and accepts only a hard-coded category for newly created assets. As a result, do not bulk-copy new files and claim a valid in-game mapping. Instead, provide Claude Code with `CLAUDE_INTEGRATION_HANDOFF.md`, the master CSV, and the reviewed image folder, then have it update the mapping/catalogue and tests on a dedicated `feature/*` branch. Keep `main` untouched. The final audit must check source licences, photo exactness labels, and resolve mod load-order winners.

## Rights and accuracy

- **No AI imagery.** Official Anduril product pictures are held until permission/licence is established.
- **CC BY-SA / CC BY**: credits, licence links, and modification statements must accompany every redistributed work. ShareAlike rules can apply to adaptations, so review distribution format before publication.
- **U.S. Government public domain**: Commons often labels U.S. federal work PD, but jurisdiction and any separate rights still require review, especially for distribution outside the US.
- **Public domain / CC0 does not imply endorsement.** No armed force, author, company, Wikimedia, or source endorses SEST.
- **No automatic 'exact' promotion.** Category/search results remain unapproved until reviewed against the actual Sea Power configuration and imagery.

## In the SEST repo (added 15 October 2026)

The kit lives in `tools/image-acquisition/`. Wikimedia Commons is not
reachable from the build machine, so it runs on the gaming PC:

1. `py -3 .\tools\image-acquisition\fetch_images.py --mode all` from the repo
   folder. Its output (`downloaded/`, `ACQUIRED_IMAGES.csv`,
   `PENDING_IMAGES.csv`, `CONTACT_SHEET.html`) is git-ignored.
2. Push that output to a branch of its own, `chore/image-intake-<date>`, with
   `git add -f`. It is never merged: rejected candidates stay out of the
   deploy history.
3. The reviewer looks at every photo, writes a review CSV (approve or reject,
   and a verdict: same_type, same_family or context), and runs
   `integration/gallery/commons_photos.py intake <kit folder> <review.csv>`
   then `commons_photos.py apply`. Only approved photos are copied into
   `integration/gallery/commons/`, with their Commons credit in
   `integration/gallery/commons-photos.csv`.

`private_reference/` and the workbook from the original ZIP are not in the
repo: the Anduril Workshop screenshot is not cleared for redistribution.
