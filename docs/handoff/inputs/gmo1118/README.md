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

Environment overlap: polar zones POL-01..05 are where `integration/environment` sea-ice,
ice-shelf (Natural Earth 1:10m) and iceberg rules apply first; see `docs/environment/`.
