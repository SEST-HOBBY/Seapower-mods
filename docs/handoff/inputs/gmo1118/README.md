# gmo1118 package: registry draft and check, 18 November 2026

The owner re-sent `SEST_GMO_Engineering_Handoff_Package_2026-11-18.zip` (20 files; the PDF
dossier, Markdown handoffs, figures and this registry). It is the same `gmo1118` design package
reviewed in `docs/handoff/WORK-PACKAGES-20261118.md` section 6, which records where it is
superseded (new "Modern Naval Operations" item; campaign id no longer frozen) or contradicted.
Only the registry draft is kept here, as a read-only input for BA-13 (Regional Watch); no builder
reads it.

`SEST_GMO_RON_Registry_Draft_2026-11-18.json`: status `DESIGN_ONLY_NOT_RUNTIME_READY`; 26 zones
(POL 6, SAM 6, AFR 6, IND 8), 12 gates, 6 corridor families; reference points only, **no
geometry**.

Checked against the built campaign
`integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns/sest-world-regions-2028/campaign.json`
at `0683f0bb`:

- every one of the 38 `native_base_ids_existing` entries is a base in `campaign.json` (196 bases);
- the three zones whose reference point lies south of the -62 bound (POL-03 Ross Sea, POL-04
  East Antarctica, POL-05 Dronning Maud Land) are all `POLAR_ENGINE_GATE`, consistent with PC-05;
- seven zones (POL-06, AFR-01..04, IND-04, IND-08) have no existing base: zone-only until the
  owner's side decisions (WORK-PACKAGES section 7, answers 5 and 6) and GM-01..04 research;
- the package's own README says the owner's regional research is still to be supplied.

## Regional research PDF (18 November)

`Strategic_Maritime_Areas_of_Significance_2026-11-18.pdf` (11 pages, ChatGPT Deep Research,
SHA-256 `16759af5...`): a ranked, sourced overview of 34 locations in four regions. No
coordinates, unit ids, sides or base data, so it is a priority and source list, not builder
input (the same status the work packages gave the earlier GPT report). Its claims dated 2026
are not checked here; GP-10 is the independent check.

`region-research-crosswalk.csv` maps every ranked location to registry zones, their activation
stage and the existing campaign bases:

- 33 of 34 locations fall in an existing registry zone; 25 of the 26 zones are named by the
  research (IND-02 Arabian Sea / Western India is not ranked separately).
- **Gaps** the research ranks that the registry lacks: the **Amundsen and Bellingshausen Seas**
  (Antarctic rank 8) and the **Weddell Sea proper** (rank 6; POL-02 covers only its approaches).
  Both lie south of -62, so they wait on PC-05 anyway.
- 15 of 34 have no existing base: all of Africa south of Djibouti, the River Plate, Cocos,
  the Mascarenes and the three Antarctic gateways. These need the owner's side decisions
  (WORK-PACKAGES section 7, answers 5 and 6); the research itself says Antarctic presence is
  logistics and science under the Treaty, which supports answer 6's "labels and waypoints".
- Its five Antarctic gateways (Ushuaia, Punta Arenas, Cape Town, Hobart, Christchurch): only
  Punta Arenas exists as a base.

Environment overlap: polar zones POL-01..05 are where `integration/environment` sea-ice,
ice-shelf (Natural Earth 1:10m) and iceberg rules apply first; see `docs/environment/`.
