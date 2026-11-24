# Gemini encyclopaedia research: audit and finished source list (24 Nov 2026)

Gemini's research of 23–24 Nov was checked line by line against the repository. Seven independent audits were run, and an adversarial reviewer re-checked each one. Commons and Steam cannot be reached from the build machine, so **no Commons file, author or licence in it is confirmed yet**. That check runs on the PC, through the existing licence-gated kit.

## What came out of it

| Output | Where | Contents |
|---|---|---|
| Source list for the PC kit | `tools/image-acquisition/SEST_IMAGE_MASTER_20261124.csv` | 176 Commons files in 177 groups, covering 774 unit rows. Of those rows, 172 are marked exact, 565 class photo and 37 context only. |
| Rows not fetched | `docs/gallery/GEMINI-20261124-NOT-FETCHED.csv` | 44 rows: 21 already in the gallery, 13 rejected, 10 render-only. Each has a reason. |
| Full audit record | `docs/gallery/gemini-audit-20261124.json` | Every row and claim with its evidence, after adversarial review |
| Kit changes | `tools/image-acquisition/fetch_images.py` | `--master`; UK OGL and Japan PDL accepted; pinned files whose titles say rendering, mock-up, model, drawing or painting are refused; a new list's output goes to `runs/<list>/` |

Nothing reaches the gallery until the photos have been downloaded, looked at and approved with `integration/gallery/commons_photos.py intake`.

## Where Gemini was wrong

| Claim | Status | Evidence |
|---|---|---|
| "217-mod catalogue", "202-mod list", "190 mods" | **Wrong** | `data/mod-catalog.json` has 212 mods. The PC had 210 subscriptions on 21 Nov. 190 is the stale 9 Oct `Gallery/data/mod_coverage.csv`. |
| 1,924 of 3,927 definitions lack photos | **Stale** | Reproduces only from the 9 Oct file. `unit_image_mapping.csv` (15 Oct) has 3,987 rows: 2,058 mapped and 1,929 gaps. 22 catalogue mods are missing from the coverage data. |
| 279 non-photo, 67 shared ordnance, 1,418 ready, 40 fictional | **Not in repo data** | Only the 120 alias rows exist. There are 37 labelled-fictional gap rows, not 40. 279, 67 and 1,418 are Gemini's own estimates. |
| "Query defects" (Indonesian F-16, Russian Sejjil, US Navy Forpost …) | **Wrong framing** | There is no search-query column. Where curated queries exist they are already correct, e.g. "Sejjil missile Iranian mobile launcher". The raw-id labels are a label-builder gap, not a query bug. |
| Tools `process_gallery_batch.py` and `fetch_catalog_covers_and_gaps.py` | **Do not exist** | The real pipeline is `tools/image-acquisition/fetch_images.py` (PC), then review, then `integration/gallery/commons_photos.py`. |
| Tridon Mk 2 "ID pending, collection 3829404451" | **Wrong** | It is 3829171147 (Swedish Army Air Defence, Tridon Mk2), already in mods-source, and it needs Euromod. |
| Euromod 3812454152 renamed to a Korean title by MackerelPurpura | **Not supported** | Its current `_info.ini` name is "Euromod-HD Hyundai Export Ships Mod". Neither the Korean title nor that author appears anywhere. |
| R.A.T.S. Keel "replaces Anchor Chain", "add to SETUP" | **Wrong** | Keel takes over Anchor Chain and bundles Anchor Chain 1.1 under MIT. SEST's bounded loader admits neither, and the PC runs Anchor Chain 1.2.0. Keep 3380210757 and do not add Keel. The author is Lukas Struckl ("Ratte"), not "Kanalratte". |
| Keel, Rigging and the other R.A.T.S. items as material MNO could absorb | **Not allowed** | The R.A.T.S. Source License 1.0 forbids reuploads, modpacks and reuse without written permission. List them as required items only. |
| Echidna "explicitly fictional" | **Overstated** | Only a comment in its sensor file says its values are fictional. It still gets a render, because no real counterpart exists. It needs Keel and ships a DLL. |
| Chinese UAV pack by "Mt.KL" | **Wrong** | No such author or unit exists. The pack is titled "— Fictional", needs Anchor Chain, and names 4 dependencies. Photos may show the real types, labelled by type only. |
| Be-12 "1965–1995" | **Wrong** | The mod gives Be-12 from 1965, Be-12N from 1972 and a Vietnamese squadron from 1981, with no end date. |
| Marine Fauna blue whale photo | **Wrong** | The mod has 13 animals and no blue whale. Proposals are missing for 9 of the 13. |
| Zyetseth "retired" | **Wrong** | The mod is active and in the load order. The ship is fictional, so it gets a render. |
| S-300PMU2 and Su-30SM2 "merged into REDFOR" | **Wrong** | They overlap with REDFOR. Both are active, and S-300PMU2 still takes precedence. |
| Fujian 3663564190 pulled; S-70B-2 deprecated; 3602046770 is the P-8 | **Correct** | S-70B-2 is deprecated but must be kept, because it is the only source of its unit. |
| Trump-class, Yak-44, Project 11780 and 21956 "fictional" | **Wrong category** | These are real unbuilt designs or programmes. They still get renders. |
| J-50 and J-36 "classified/unbuilt" | **Wrong** | They are flying prototypes. A real photo may be used only with a verified free licence. J-36A is a fictional variant. |
| CPS and AIM-260 "unbuilt" | **Wrong** | Both are real, tested weapons. US government test photos may exist. |
| Official USN artist renderings for Constellation and Columbia | **Rejected** | A rendering is not a photograph. Use in-game renders, or real construction photos labelled as such. |
| Unit ids throughout | **Many wrong** | Wrong case (`usn_cg_ticonderogaVLS`), `_` for `-`, an invented `type_21_acsl_lynx` (really `type_21+ACSL_lynx`), ranges that hide ids, truncated file titles. All were resolved against `unit_image_mapping.csv` in the list. |

## Photos changed or refused

| Row | Verdict | Reason |
|---|---|---|
| Oniks, Exocet AM39, LANTIRN, ARRW, ESSM, SM-6, HQ-9, nuclear and coal plants, Liberty, HEMTT, Type 12, Iskander, Yasen, humpback, Virginia, Wedgetail, F-15EX, Fury, Type 071, Liaoning/Fujian | **Already in the gallery** | Gemini offered files the gallery already ships or has credited. Only the mapping to the gap ids is missing (see the not-fetched list). |
| EDA-S landing craft (6) | Rejected | The 2012 photo is nine years older than the EDA-S, so it must show a CTM or EDA-R. |
| ASRAAM | Rejected | The file title says it is a mock-up. |
| MdCN | Rejected | Storm Shadow is a different missile. |
| Kormoran (AS.34) | Rejected | The photo shows a Tornado, not the missile. |
| KAB-500Kr | Rejected | The KAB-500S-E has a different guidance head. |
| CAMM / Sea Ceptor | Rejected | It shows a ship leaving port. |
| Iran Bell 212 | Rejected | It shows the 2024 crash aircraft, and the licence is unknown. |
| Borei | Held | Mil.ru with no CC tag. It qualifies only if the PC finds CC BY 4.0. |
| PVO airbase | Rejected | The photo is a B-52 aircraft, not a base. |
| Tridon | Rejected | Naval gun PNG with two authors. Use a render. |
| Chinese munitions (12 ids, 75 rows) | Open | No files proposed. They need a targeted search, for example by Chinese designation. |
| Fictional or unbuilt hulls (Kirov improved, Ulyanovsk, Burke HELIOS, Okean "surprise", Saronic and others) | Render only | A photo of something else must not stand in for them. |
| Many Gemini "exact" photos | Downgraded to class photo | The variant, operator or date is not shown: Mi-6, Be-12, WZ-10, Kilo 877V, Oberon, Galerna, MV-22/JGSDF and others. |

## Repository problems the audit found (not Gemini's)

1. **Gallery data is a month old.** `mod_coverage.csv` and `unmapped_entries.csv` predate 22 catalogue mods and the 9 new mods in mods-source. Regenerate them in the next build.
2. **17 fictional units show real photos**: Hollywood-class, Udaloy III, Centaur CATOBAR, F123 2030 MLU and others. **Owner decision:** either a render, or keep the real photo labelled "class photo of the base class". This applies only to fictional refits of real hulls.
3. **Sui and Tang are swapped** in the gallery labels for Type 095, 096 and 09X. The mod has 095 = Sui and 096 = Tang.
4. **Van Galen trap.** The Dutch mod has both the new ASW frigate (F-806, unbuilt) and the historical F-834. Block photos of the old ships for the new unit.
5. **The Liaoning row is keyed to an id that doesn't exist** (`plan_cv16_liaoning`) in `commons-photos.csv`.
6. **Meshy-AI meshes in two mrresident mods** (the RBS 15KA launchers and the Giraffe 4A radar module). A render used as their encyclopaedia picture would show AI-made geometry. **Owner decision.**

## PC step

Run from the kit folder in the repo checkout, or from a copy of `tools/image-acquisition`:

```powershell
py -3 .\fetch_images.py --mode verified --master SEST_IMAGE_MASTER_20261124.csv
```

Then open `runs\SEST_IMAGE_MASTER_20261124\CONTACT_SHEET.html`. Check each picture against its unit: right subject, variant, operator and era, and a real photograph. Upload `ACQUIRED_IMAGES.csv`, `PENDING_IMAGES.csv` and the `downloaded` folder. The kit skips a file whose live licence is not PD, CC0, CC BY, CC BY-SA, UK OGL or Japan PDL, or whose title says it is not a photograph.
