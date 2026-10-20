# Units without a picture - research list (20 Oct 2026)

The units SEST's campaigns place or sell that have no usable photo in the briefings and the gallery, worked out from the built missions and rosters at `e7b32f11` with the same test the briefing uses (`build_pack.recognition`). The same rows, with spare columns for what you find, are in `tools/image-acquisition/UNIT_IMAGE_GAPS_20261020.csv`.

**What a photo needs:** public domain (US federal: navy.mil, af.mil, army.mil, DVIDS), CC0, CC BY or CC BY-SA. Not NonCommercial, not NoDerivatives, not Crown copyright (the Australian Defence image library and UK MOD are Crown copyright unless the file on Commons says CC BY), not manufacturer marketing pictures, not Workshop screenshots without the author's permission, no AI images. Check the licence on each file's own page. Send me the file page link and I will do the intake (`commons_photos.py`).

**How sure the leads are:** an agent read each unit's own file to say exactly what it is, and searched for leads. "(seen)" marks a lead it actually looked at. The second, checking pass did not run (spend limit), so treat the rest as places to start, not answers. The 25 base-game units at the end of P2/P3 were identified from the game's own name files only.

**97 units:** 27 P1, 32 P2, 38 P3. Separately, 54 units already have a gallery photo that the briefings fail to show; that is a fix on my side, listed at the end, nothing to research.


## P1 - your forces, or 5+ missions

### `civ_fv_fishingboat_a` - A generic small outrigger shrimp trawler of the Gulf of Mexi - *any representative photo*

- **Where:** 21 mission(s), neutral
- **Find:** A steel or wooden outrigger shrimp trawler (or prawn trawler) of about 20-25 m with the wheelhouse forward and twin outrigger booms, under way or alongside. A Gulf of Mexico shrimper or an Australian Northern Prawn Fishery trawler both fit. These would make the photo wrong: a Filipino banca (outrigger canoe), an Asian longliner or purse seiner, or a stern trawler with a gantry. The photo must match the in-game hull, not the mission's 'banca' or 'tuna boat' labels.
- **If not found:** Reuse the existing 'trawler' asset (White Horse, CC BY 2.0, credit Barry Lewis), labelled 'Small outrigger trawler (representative fishing vessel)'.
- **Leads:** Wikimedia Commons: Category:Shrimp boats (or search 'shrimp trawler outriggers') [mixed; NOAA PD and CC BY-SA user photos]; NOAA Photo Library / NOAA Fisheries: shrimp trawler Gulf of Mexico [Public domain (US federal)]; Wikimedia Commons search: prawn trawler (Australian examples: Karumba, Cairns, Darwin) for regional flavour [CC BY-SA user photos; check each]
- **Already tried:** Nothing for this unit id in the 14 Oct master, curated_sources.tsv, the 15 Oct review or the catalogue.js gaps. A related asset exists: 'trawler' (File:Fishing trawler "White Horse" beached in Seaford, July 1989 (1).jpg, Barry Lewis, CC BY 2.0). profiles.tsv already judges it same_family for the armed copy of this hull (ir_fv_fishingboat_armed, 'beam trawler with outrigger booms broadly resembles an outrigger shrimp trawler'). It is P1 despite being neutral generic traffic because it appears in 21 missions, the most of this batch, and it should be an easy win. The research budget for web searches ran out, so nothing could be confirmed.
- **Licence:** Do not use state-agency photos (Texas Parks & Wildlife, Louisiana, Florida FWC); they are NOT public domain. Australian government images (AFMA, state fisheries) are Crown copyright unless the Commons page shows CC BY. Avoid stock sites.

### `airbase_raaf_darwin` - RAAF Base Darwin

- **Where:** 11 mission(s), player
- **Find:** The military side of RAAF Base Darwin: flightline, apron, hangars or an aerial view, ideally with combat aircraft (RAAF F-35A, or USAF fighters, bombers or tankers on Pitch Black / EAC rotations), 2010s-2020s. Wrong photos: interiors or cargo holds (the 15 Oct intake rejected 'inside a C-5's hold'), shots of only the civil Darwin airport terminal, RAAF Base Tindal pictures from the same exercise, and 1940s war-damage photos unless labelled historical.
- **If not found:** A US-military photo of aircraft on the Darwin flightline, captioned for example 'RAAF Base Darwin flightline, Exercise Pitch Black 2026 (U.S. Air Force photo by Tech. Sgt. Peter Reft)'.
- **Leads:** dvidshub.net: 'U.S. Air Force participates in Exercise Pitch Black 2026', images 9832307-9832313 (7 images, RAAF Base Darwin, 21-22 Jul 2026; C-130J on the Darwin flightline, RAAF and USAF C-130Js parked together), U.S. Air Force photo by Tech. Sgt. Peter Reft [Public domain (US federal work)] (seen); dvidshub.net: 'MRF-D Marines participate Mindil Beach flying display', images 9829300 / 9829314 (MV-22B taxiing on the Darwin flightline, Jul 2026). USMC photographer, Sgt. Kyle Chan named on one listing; check each credit [Public domain if a USMC photographer] (seen); Wikimedia Commons (already in SEST commons-photos.csv): File:Talisman Sabre 2025 Logistics Download Operations at Royal Australian Air Force base Darwin, Australia (9145907).jpg (U.S. Army, Sgt. Devin Davis). SEST already uses it for the HEMTT. Check whether the base or flightline is visible enough to reuse [Public domain] (seen); af.mil / pacaf.af.mil / DVIDS: 'B-52 Stratofortress bombers arrive at RAAF Base Darwin' Enhanced Air Cooperation (US Air Force bomber rotations) [Public domain if a US photographer]
- **Already tried:** 14 Oct master row 8 / curated_sources: Category:RAAF Base Darwin (exact_base_reference, P1, 7 legacy missions). 15 Oct intake raaf_darwin REJECTED, 'inside a C-5's hold'. catalogue.js photo_subject_gaps 'RAAF Base Darwin', query intitle:"RAAF Base Darwin". RAAF Base Tindal was solved the same way, with a USAF Pitch Black 2024 Commons photo (raaf_tindal.jpg).
- **Licence:** DVIDS also hosts ADF-photographer images marked 'public domain' that are really Crown copyright. Example: DVIDS 2772213 (Pitch Black 2016 F-16s at Darwin, credited to LSIS Jayson Tufrey, ADF). Do not use those, or anything from images.defence.gov.au or airforce.gov.au. NT Library items carry mixed licences, and CC BY-NC is not allowed.

### `civ_fv_fishingboat_b` - A generic small European side trawler of about 30 m, the Nor - *any representative photo*

- **Where:** 11 mission(s), neutral
- **Find:** A small (25-35 m) side trawler with the wheelhouse aft or amidships, gallows on the side, a foremast and a sheer bow. Icelandic, Faroese, Norwegian, Danish or Finnish boats are best, and a 1950s-80s photo is fine. These would make the photo wrong: a stern trawler with a stern ramp or gantry, a beam trawler with outrigger derricks, a large 60-70 m distant-water side trawler (acceptable only as family), a purse seiner, or a Southeast Asian banca. The photo must match the in-game hull, not the mission labels.
- **If not found:** Reuse the existing 'trawler' asset (White Horse, CC BY 2.0, credit Barry Lewis), labelled 'Small European trawler (representative; beam-trawl rig, not side-trawl)'.
- **Leads:** Wikimedia Commons search: side trawler; sidetrawler Iceland / Faroe / Norway; Category:Side trawlers (if it exists) [CC BY-SA / PD (old photos); check each]; Wikimedia Commons search: Ross Tiger trawler Grimsby. It is a preserved 1957 side trawler of about 33 m, a close size match, though British. [CC BY-SA user photos]; Finna.fi (Finnish Heritage Agency / Museovirasto): troolari (trawler) / kalastusalus. Filter to CC BY 4.0. [CC BY 4.0 for many Museovirasto images; reject CC BY-NC-ND items]
- **Already tried:** Nothing for this unit id in the 14 Oct master, curated_sources.tsv, the 15 Oct review or the catalogue.js gaps. A related asset exists: 'trawler' (File:Fishing trawler "White Horse" beached in Seaford, July 1989 (1).jpg, Barry Lewis, CC BY 2.0). profiles.tsv judges it same_family for the armed copy of this exact hull (civ_fv_fishingboat_b_armed, same mesh ships/civ_fv_fishingboat_b): 'broadly similar to the generic 30 m small side trawler, though the rig differs'. It is P1 because it appears in 11 missions. The research budget for web searches ran out, so nothing could be confirmed.
- **Licence:** Nordic museum portals (DigitaltMuseum, Sjöhistoriska, Finna) mix licences: CC BY and CC BY-SA are fine, but CC BY-NC, CC BY-ND and 'all rights reserved' are not. Check each item.

### `phl_h-76` - AUH-76

- **Where:** 9 mission(s), player; sold in sest-sulu-line; sest-sulu-line-open
- **Find:** A Philippine Air Force S-76 / AUH-76. Ideally it is in the armed configuration with stub pylons and gun or rocket pods, in olive or camouflage paint (1980s-2000s). Next best: a PAF S-76A in its later SAR fit. Wrong photos: an SH-2 Seasprite (even though the in-game mesh is one), civil offshore S-76s (CHC and others), the S-76D, and the Sikorsky H-76 Eagle company demonstrator (manufacturer imagery).
- **If not found:** A PAF S-76A in SAR configuration, labelled 'Philippine Air Force S-76A: the airframe of the AUH-76, shown unarmed'. If nothing PAF clears licensing, use any S-76A labelled 'Sikorsky S-76 type reference'.
- **Leads:** Wikimedia Commons: File:745 Sikorsky S-76 Philippine Air Force (7838651568).jpg (PAF S-76 at Mactan-Cebu, 20 Mar 2012, by Aeroprints.com via Flickr) [Aeroprints.com Flickr imports are usually CC BY-SA 3.0; check page] (seen); Wikimedia Commons: File:Philippine Air Force Sikorsky S-76.jpg (617x442, sourced from the PAF aircraft gallery) [PD-PhilippinesGov tag: risky (see warning)] (seen); Wikimedia Commons: Category:Aircraft of the Philippine Air Force (look for an S-76 subcategory and a higher-resolution 'Philippine Air Force S-76A.jpg', which a search result mentioned but I did not open) [mixed; check each] (seen); Wikimedia Commons: Category:Sikorsky S-76 [mixed; check each] (seen)
- **Already tried:** Nothing found. No row in the 14 Oct master or curated_sources.tsv, no 15 Oct intake decision, no photo_subject_gaps entry, and no S-76 asset in the gallery.
- **Licence:** Philippine government works (PD-PhilippinesGov) have no copyright, but RA 8293 s.176 requires prior approval for commercial exploitation, so they are unsafe for redistribution on Steam. Prefer US DoD or Aeroprints CC BY-SA files. Sikorsky or Lockheed Martin H-76 Eagle brochure images are manufacturer marketing and not allowed.

### `plan_ssn_type_093b` - Type 093B Shang III-class SSN

- **Where:** 7 mission(s), opponent/player; sold in sest-southern-reach; sest-southern-reach-open; sest-southern-watch; sest-southern-watch-open
- **Find:** A Type 093B (Shang III) SSN: the stretched Shang hull with the vertical-launch section behind the sail, ideally surfaced, PLAN, 2020 or later. These would make a photo WRONG: a Type 093 or 093A (no VLS section; family only), the Type 091 Han (e.g. the Changzheng 1 museum boat at Qingdao), the Type 094 Jin SSBN (long missile-deck hump), or a Type 039/039A Yuan SSK. Watch out for Commons 'File:Chinese Type 093 submarine.jpg'. It now redirects to 'Chinese Type 039A submarine.jpg', is a 2008 'self-made' upload, and its identity is disputed. Do not use it as a 093.
- **If not found:** A Type 093 or 093A Shang photo, for example the Japanese MoD January 2018 surfaced boat, captioned 'Type 093-family (Shang) SSN, earlier 093/093A boat shown; the 093B adds a VLS section aft of the sail'.
- **Leads:** Wikimedia Commons: Category:Type 09III submarines (the Commons category for the Type 093 / Shang class; alternative names Type 093, Shang class). Check each file for 093B features; most will be 093/093A at best. [mixed, check each file] (seen); Japan Ministry of Defense, Joint Staff Office press releases (mod.go.jp/js), 11-12 Jan 2018: Photos of the Shang-class (Type 093) SSN that surfaced flying the PRC flag in the East China Sea after transiting the Senkaku contiguous zone. News outlets (The Diplomat, Baird Maritime) credit the photos to Japan's MoD. This boat is a 093/093A, so it is family only. [Government of Japan Standard Terms of Use 2.0 (compatible with CC BY 4.0). Confirm on the MoD page or a Commons copy]; Wikimedia Commons: File:Shang class SSN.svg: a silhouette drawing, not a photo. Use only as a last-resort diagram. [check file page] (seen); DVIDS / navy.mil: "Shang-class" OR "Chinese submarine" OR "PLA Navy submarine" (US surveillance releases are rare) [public domain (US federal)]
- **Already tried:** 14 Oct master row 10: P1 - fielded frequently, asset shang_family, search 'Chinese Type 093 attack submarine', family_reference, 'Exact 093B public image uncertain', status 'search candidate; photo and licence need review'. curated_sources.tsv line 9 has the same entry. catalogue.js photo_subject_gaps has 'Type 093 Shang submarine' (asset shang, query intitle:"Type 093"): no reusable photo passed. The 15 Oct intake has nothing. The siblings plan_ssn_type_093 and plan_ssn_type_093a are also photo_gap, so one good Shang photo covers three units.
- **Licence:** Nearly every 093B image online comes from Chinese state media (CCTV, Xinhua, chinamil.com.cn, Weibo/forum leaks, all rights reserved) or commercial satellite imagery (Maxar, Planet, Airbus: copyrighted). None is usable. The Japanese MoD terms exclude third-party content, so check the specific page.

### `pn_ffg-150` - Jose Rizal Class

- **Where:** 7 mission(s), player; sold in sest-sulu-line; sest-sulu-line-open
- **Find:** BRP Jose Rizal (FF-150) or BRP Antonio Luna (FF-151) in service, 2020 or later. Commons notes the pennant numbers changed in 2026 to FFG-14 and FFG-15, so a photo showing 14 or 15 is the same ship. Best is a clear broadside or 3/4 view at sea. A photo is wrong if it shows: BRP Rizal (PS-74), the old ex-USN Auk-class patrol vessel (the gallery's 'rizal_old' asset, File:2020-01-29 BRP Rizal-BRP Mahusay.jpg, is that ship and must not be aliased here); the larger Miguel Malvar-class HDC-3200 corvettes (FFG-06/07, delivered 2025, similar look); the launch-day photo at HHI Ulsan (incomplete ship); or a ship badge, seal or infographic.
- **If not found:** No fallback should be needed, since exact public-domain photos exist. One photo can serve both pn_ffg-150 and pn_ffg-150_2, labelled 'as delivered, without VLS' for the VLS unit.
- **Leads:** Wikimedia Commons: File:BRP Jose Rizal at RIMPAC 2020 001.jpg (via DVIDS, MCSN Lily Gebauer, US Navy) [Public domain (US Navy work)] (seen); Wikimedia Commons: File:BRP Antonio Luna FFG15 (260424-N-DC740-1104 1440p).jpg (US Navy VIRIN, Balikatan 2026) [Public domain (US Navy) - confirm on the file page] (seen); Wikimedia Commons: Category:Jose Rizal class frigate [varies per file] (seen); Wikimedia Commons: Category:BRP Jose Rizal (FF-150) (about 69 files: RIMPAC 2020, 2022-2026; also listed as Category:BRP Jose Rizal (FFG-14)) [mix of US Navy PD, Philippine Navy PD-PhilippinesGov and one CC BY-SA file; check each] (seen)
- **Already tried:** Nothing found in the 14 Oct master, curated_sources, the 15 Oct intake or photo_subject_gaps. Catalogue entries pn_ffg-150 and pn_ffg-150_2 are both photo_gap. Beware: the gallery's 'rizal_old' asset is the old patrol vessel BRP Rizal (PS-74), a different ship.
- **Licence:** Avoid File:BRP Jose Rizal from JMSDF Ship at RIMPAC 2020.jpg: it is a JMSDF 'courtesy photo', so its PD-USGov tag is doubtful. Do not use HHI marketing images or Philippine news-outlet photos. Philippine Navy uploads carry PD-PhilippinesGov, which needs prior approval for commercial use (check the tag); prefer the US Navy files.

### `rok_f-50_ph` - FA-50PH

- **Where:** 6 mission(s), player; sold in sest-sulu-line; sest-sulu-line-open
- **Find:** A Philippine Air Force FA-50PH in light grey with PAF roundel and serial (the delivered batch is 15-0xx), 2015 or later. Ground or air both work; an exercise shot alongside USAF aircraft is fine if the FA-50PH is the clear subject. Wrong subjects: ROKAF FA-50, T-50 or TA-50; Indonesian T-50i; Iraqi T-50IQ; Thai T-50TH; Polish FA-50GF/PL; Malaysian FA-50M.
- **If not found:** Reuse the existing fa50 asset (images/aircraft/fa50_commons.jpg: ROKAF FA-50s, Republic of Korea Armed Forces, CC BY-SA 2.0), captioned 'FA-50 family (ROKAF aircraft shown), not a PAF FA-50PH'.
- **Leads:** dvidshub.net/image/7938370: 'Cope Thunder 23-2': Philippine Air Force FA-50 on the taxiway at Clark Air Base, July 2023, SrA Vaughn Weber [Public domain (USAF)] (seen); dvidshub.net/image/7997440: 'Cope Thunder 23-2': PAF FA-50 taxiing at General Santos, July 2023 [Public domain (USAF)] (seen); pacaf.af.mil News/Photos igphoto 2003180783, 2003180739, 2003180721, 2003180757: 'Fifth gen fighters debut in the Philippines', March 2023: F-22A with a PAF FA-50PH in flight and on the Clark flightline, SrA Jessi Roth [Public domain (USAF)] (seen); pacaf.af.mil igphoto 2003449548 (also 5af.pacaf.af.mil): Cope Thunder 24-1, April 2024: USAF F-16 flying with a PAF FA-50 near Basa AB [Public domain (USAF)] (seen)
- **Already tried:** No row for rok_f-50_ph in the 14 Oct master or curated_sources. The related rok_fa50 (ROKAF) row used Category:FA-50 Fighting Eagle and noted 'Philippine family photo possible'. The 15 Oct intake approved fa50 (ROKAF formation, same_family) for rok_fa50 only. Not in photo_subject_gaps; the catalogue shows photo_gap.
- **Licence:** Exercise Pitch Black 2024 (Darwin) photos from the Australian Defence image library (images.defence.gov.au) are Crown copyright and NOT usable. Neither are PAF Facebook, PNA or Rappler photos credited to the PAF, unless they carry a free licence. PD-PhilippinesGov files need prior government approval for profit-making use, so prefer the US public-domain frames. No KAI marketing images.

### `shahed_tel_black` - Shahed-136-black

- **Where:** 5 mission(s), opponent
- **Find:** A Shahed-136 (or Geran-2) on a ground launcher, ideally a truck-mounted launch rack with the drone in place. An Iranian IRGC truck or pickup launcher is fine as the family reference. Wrong photos: wreckage and debris (no launcher), the US LUCAS clone, the Shahed-238 jet version, the Shahed-131, CAD drawings, renders and artist's impressions.
- **If not found:** A Shahed-136 on any Iranian launcher, labelled 'Shahed-136 on an Iranian launcher (family reference; not the in-game truck or livery)'. Failing that, a static Shahed-136 airframe photo labelled 'Shahed-136 airframe reference', or an in-game screenshot.
- **Leads:** Wikimedia Commons: File:Military equipment displayed for the 44th Iranian revolution anniversary rally - Shahed 136.jpg (Shahed-136 on a launcher in a pickup truck, Tehran, 11 Feb 2023, source Tasnim) [CC BY 4.0 (Tasnim); confirm on the file page] (seen); Wikimedia Commons: File:2023 IRGC Aerospace Force achievements Exhibition in Qom (33).jpg (Shahed-136 on display; whether a launcher is visible is unconfirmed) [probably CC BY 4.0 (Iranian agency); check] (seen); Wikimedia Commons: Category:Shahed 136 [varies by file] (seen); Wikimedia Commons: Category:Geran-2 (for the black Russian livery; contents not checked, likely mostly wreckage) [varies (Ukrainian government files are often CC BY 4.0)] (seen)
- **Already tried:** The 14 Oct master CSV (P1, asset_group shahed_tel) and curated_sources.tsv queued only a Commons MediaSearch for "Shahed-136 mobile launcher Iran" (family_reference, note "Use same Shahed family asset for black/white variant"). It was never imported, and the 15 Oct intake has no row. catalogue.js has a separate gap, asset 'shahed136_weapon' ("Shahed-136 — airframe reference", query intitle:"Shahed-136"). The gallery's existing 'shahed136' asset is a 392x220 image supplied by the SEST author with licence 'Not recorded'; it shows the drone, not a launcher. The mod author's profile picture exists (existing-profiles.tsv, 1357x644).
- **Licence:** Tasnim, Mehr and Fars files on Commons are CC BY 4.0. IRNA, AP, Reuters and AFP are not usable. Renders, SVG drawings, the artist's impression and the existing 'shahed136' asset (licence not recorded) must not be used. The LUCAS photo is public domain but shows a different (US) drone.

### `usn_ForpostR705` - Forpost-R UAV

- **Where:** 5 mission(s), opponent; sold in sest-southern-watch; sest-southern-watch-open; sest-sulu-line; sest-sulu-line-open
- **Find:** Forpost-R (Russian-built Searcher II derivative), Russian Army or Navy service, about 2019 onward, in flight or on static display. It should show a twin-boom pusher UAV with a high wing and twin fins. Best: a photo captioned 'Forpost-R' (e.g. Army-2019/2020/2022 static displays). Wrong photos: Israeli-operated Searcher I/II or Indian/Sri Lankan Searchers captioned as such (same airframe but wrong operator; acceptable only as a labelled family reference), Orlan-10 or other Russian drones, wreckage shots from Ukraine where the airframe is not recognisable, and 3D renders. Note the original 2011-2013 'Forpost' (MAKS-2011, Innovation Day 2013) is the pre-localisation version with Israeli components. It looks nearly identical but is not strictly the Forpost-R.
- **If not found:** The existing forpost.jpg (Forpost at MAKS-2011), labelled 'Forpost (licence-built IAI Searcher II), family reference: the Forpost-R is the Russian-localised version and looks almost the same'. Mapping it closes the gap without new research. Use an Army-2022 Forpost-R file only if its licence checks out.
- **Leads:** SEST gallery (already on disk): images/aircraft/forpost.jpg = File:Forpost UAV at MAKS-2011 01.jpg (asset_id forpost, mapped to no unit in unit_image_mapping.csv) [CC BY-SA 4.0 (Vitaly Kuzmin, valid because the file predates 30 Aug 2017)] (seen); Wikimedia Commons: Category:Forpost (UAV) (lists 'Forpost R' / 'Forpost-R UCAV' as aliases; holds about 27 files including Army-2022 photos dated 2022-08-20) [mixed: CC BY-SA 4.0 Vitaly Kuzmin (only if online before 30 Aug 2017), CC BY 4.0 mil.ru; check each file] (seen); Wikimedia Commons: File:Forpost UAV InnovationDay2013part2-02.jpg [probably CC BY-SA 4.0 (Vitaly Kuzmin, 2013); check page] (seen); Wikimedia Commons: Category:IAI Searcher (parent airframe, family reference only) [mixed; check each] (seen)
- **Already tried:** 14 Oct master (SEST_IMAGE_MASTER_20261014.csv row 17) and curated_sources.tsv line 25: asset group 'forpost', P1, Category:Forpost (UAV), family_reference, note 'Forpost family - Forpost-R must be visually verified'. 15 Oct intake (commons-review-20261015.csv): 'forpost' rejected with 'the gallery's photo stays'. So the gallery already holds forpost.jpg (MAKS-2011 Forpost, CC BY-SA 4.0), but that asset is mapped to no unit, which is why this unit still shows NO PHOTO. There is no photo_subject_gaps entry in catalogue.js.
- **Licence:** Vitaly Kuzmin photos on Commons are CC BY-SA 4.0 only if the image was on vitalykuzmin.net before 30 Aug 2017. Army-2022 shots by him are NOT free. Use mil.ru-sourced or Commons-own-work Army-20xx files instead.

### `pla_airbase_modern` - Modern Chinese airforce base - *any representative photo*

- **Where:** 4 mission(s), opponent/player
- **Find:** A modern PLAAF military airfield (apron or flightline with PLAAF aircraft, or an aerial / satellite view), 2010s+. A free ground photo of Wugong itself is very unlikely. The honest options are a satellite view captioned as Wugong, or a ground photo of another PLAAF airfield captioned as a representative PLAAF base. Wrong photos: civil Chinese airports, Taiwanese ROCAF bases, Russian bases, carrier decks, and any photo captioned as Wugong when it is not.
- **If not found:** A PLAAF aircraft on a PLAAF airfield apron, captioned 'PLAAF airfield (Changchun, 2025 open day), representative'. Or a Sentinel-2 / Landsat image captioned 'Wugong Air Base, Shaanxi (satellite)'.
- **Leads:** Wikimedia Commons, uploader 颐园居 (Special:ListFiles): Own-work photos from the PLAAF Aviation Open Day / Changchun Air Show, 19-23 Sept 2025, at a PLAAF airfield. The gallery's existing hq22.jpg (File:HQ-22 20250921.jpg, CC BY-SA 4.0) comes from this event. Look for apron or flightline views with PLAAF aircraft [CC BY-SA 4.0 (as on hq22.jpg); check each file]; Copernicus Sentinel-2 (Copernicus Browser) or USGS EarthExplorer (Landsat); Commons satellite uploads: Satellite view of Wugong Airbase, Shaanxi (about 20 km north of Xi'an, Wugong county / Yangling district) [Sentinel: free with 'Contains modified Copernicus Sentinel data [year]' (CC BY-SA 3.0 IGO on Commons). Landsat: public domain]; Wikimedia Commons: Airshow China (Zhuhai Jinwan) PLAAF static display / apron photos. Context only: Zhuhai is the show airport, not a named PLAAF base [CC BY / BY-SA per file]
- **Already tried:** 14 Oct master row 15 / curated_sources: search 'People Liberation Army Air Force air base flightline' (context_reference, P1, 4 legacy missions; note 'Generic PLA airbase, never mark exact installation'). Nothing for pla_airbase reached the 15 Oct intake, and there is no catalogue.js photo_subject_gaps entry.
- **Licence:** Xinhua, CCTV, China Military Online (chinamil.com.cn), Global Times, airliners.net, JetPhotos and AirHistory.net are all rights reserved. Maxar and Planet commercial satellite images are not free unless a specific image is CC-licensed on Commons. FAS / GlobalSecurity pages mix declassified US imagery (PD) with commercial imagery (not free), so check each picture.

### `usaf_f-15ex_SEII` - F-15EX

- **Where:** 3 mission(s), player; sold in sest-southern-watch-open
- **Find:** A USAF F-15EX Eagle II in the grey/blue two-tone scheme: test aircraft (ET, Eglin, 40th FLTS or 85th TES), Oregon ANG 142nd Wing/123rd FS, or Kadena (ZZ). Wrong subjects: F-15E (dark grey; it also has CFTs, so check the designation in the caption), F-15QA, F-15SA, F-15IA and F-15C.
- **If not found:** Not needed: the exact photo (asset f15ex) is already in the library.
- **Leads:** Already in the SEST gallery: integration/gallery/source/images/aircraft/f15ex.jpg (asset f15ex): Commons File:F-15EX Eagle II.jpg, Ethan Wagner, Edwards AFB / DVIDS 6650896. It shows ET-coded 40 FLTS F-15EX 20-001 in flight, an exact match for SEST's 40th FLTS squadron. No research needed: map usaf_f-15ex_SEII to asset f15ex. [Public domain (USAF)] (seen); dvidshub.net/image/6552157 to 6552163 ('F-15EX arrival') and 6557890 ('AF's first F-15EX arrives at Eglin'): First F-15EX arriving at Eglin, March 2021, Tech. Sgt. John Raven / Samuel King Jr. (alternatives only) [Public domain (USAF)] (seen)
- **Already tried:** 14 Oct master and curated_sources: File:F-15EX Eagle II.jpg (Public domain, source_verified_web, 'await API check and download', P1). 15 Oct intake: f15ex rejected with 'the gallery already has this same Commons file'. The file sits in images/aircraft/f15ex.jpg and PHOTO_CREDITS.txt, but in catalogue.js this unit has asset_id empty and mapping_status photo_gap, and profiles.tsv has no row for it. This is a mapping gap.
- **Licence:** The existing file is public domain (a USAF work). Avoid Boeing marketing photos. Oregon ANG frames on DVIDS are fine when credited as US Air National Guard or USAF photos, but check that the credit is not a state or contractor credit.

### `civ_ms_c8` - Base-game 'Barge Carrier', a LASH (lighter-aboard-ship) merc

- **Where:** 2 mission(s), player; sold in sest-sulu-line; sest-sulu-line-open
- **Find:** A LASH barge carrier: long hull with the superstructure well forward, a large travelling gantry crane on rails over the hatches, and the forked stern overhang where lighters are lifted. Best is one of the listed ships, ideally Waterman's Stonewall Jackson or Robert E. Lee, or Central Gulf's Green Valley or Green Harbour in MSC prepositioning service. These would be WRONG: a SEABEE barge carrier (Lykes 'Doctor Lykes' type, stern elevator, no gantry), a BACAT, the Soviet LASH types in the same Commons category (Tibor Samueli, Yulius Fuchik: different design), or an ordinary container ship.
- **If not found:** Any C8-type LASH with the stern gantry, preferably a listed ship (Acadia Forest or Rhine Forest), captioned with the ship's real name and 'LASH barge carrier'.
- **Leads:** Wikimedia Commons: Category:Lash vessels. Its subcategories include Acadia Forest (ship, 1969) (12 files) and Rhine Forest (ship, 1972), both listed civ_ms_c8 variants (Variant18 and Variant20). [mixed, check each file] (seen); Wikimedia Commons: File:Lash vessel.JPG (filed under Category:Rhine Forest (ship, 1972); open it to confirm the ship and that the gantry is visible) [public domain (self-dedication by Jdw at Dutch Wikipedia)] (seen); DVIDS / navy.mil / MSC archives / NARA (Commons DN-SC series): "LASH" OR "lighter aboard ship" with "Green Valley", "Green Harbour", "Austral Lightning", "Diego Garcia" (Afloat Prepositioning Force, 1980s-2000s) [public domain (US Navy / MSC)]
- **Already tried:** Nothing found: no row in the 14 Oct master, curated_sources.tsv, the 15 Oct intake or photo_subject_gaps. The unit is not in the gallery catalogue at all (status NOT IN GALLERY).
- **Licence:** Many LASH photos come from shipspotting sites or company brochures (all rights reserved). Use only Commons files with a free tag or US federal photos.

### `mv22b_osprey` - MV-22B Osprey

- **Where:** 2 mission(s), player
- **Find:** A USMC MV-22B in standard fleet grey, best a VMM-263 or VMM-162 aircraft (the caption or tail code names the squadron), at sea or on an amphibious ship's deck, 2007 or later. Wrong subjects: the HMX-1 green/white VIP Osprey, the AFSOC CV-22B (radar bulge in the nose), the US Navy CMV-22B (enlarged sponsons), the JGSDF V-22B, and frames where the Osprey is hidden or out of shot (the 15 Oct intake rejected one with 'people disembarking; no Osprey in view').
- **If not found:** Until a grey VMM-263/162 photo is found, map the unit to the existing mv22 asset, captioned 'USMC MV-22B Osprey (HMX-1 VIP livery shown)'.
- **Leads:** dvidshub.net/image/963402: MV-22B of VMM-263 landing aboard USS Wasp (LHD 1), 2013, US Navy photo by MIDN 3/C Alexandria Segovia (sibling 963403) [Public domain (US Navy)] (seen); dvidshub.net/image/3543403 and /image/3543411: 'VMM-263 trains aboard USNS Lewis B. Puller', 2017 [Public domain (USMC)] (seen); allhands.navy.mil Media/Gallery igphoto 2002373274, 2002373275, 2002373276: VMM-263 MV-22B Ospreys landing on USS New York (LPD 21), 6th Fleet, 2018, Cpl Juan A. Soto-Delgado [Public domain (USMC/US Navy)] (seen); dvidshub.net search: "VMM-162" MV-22B flight deck [Public domain (USMC/US Navy)]
- **Already tried:** 14 Oct master and curated_sources: mv22b row, Category:MV-22B Osprey (category candidate, exact_photo, P1). 15 Oct intake: mv22b candidate rejected ('people disembarking; no Osprey in view'). The gallery already has images/aircraft/mv22.jpg (HMX-1 green/white MV-22B), but profiles.tsv maps it only to usmc_mv-22b and jgsdf_mv-22b. This unit id has an empty asset_id (photo_gap). Not in photo_subject_gaps.
- **Licence:** Do not use Bell or Boeing press or marketing images, or JMSDF/JGSDF images of Japanese V-22s (wrong unit). DVIDS, marines.mil and navy.mil photos by service members are public domain. Skip DVIDS items credited to contractors or civilians who are not government employees.

### `phl_pb_jose_andrada` - Jose Andrada-class

- **Where:** 2 mission(s), player
- **Find:** A Philippine Navy Jose Andrada-class patrol boat (hull numbers PC-370 to PC-395 range, e.g. BRP Jose Andrada PC-370, BRP Hilario Ruiz PC-378, BRP Juan Magluyan PC-392): a small grey 24 m boat with a single 25 mm Mk 38 mount on the foredeck, visible in close-up. A photo is wrong if it shows: an Acero-class (Shaldag Mk V) boat with a Typhoon remote weapon station and Spike launcher; a Tomas Batilo-class (ex-ROK Chamsuri) boat, which the same mod defines separately; a Kagitingan or Conrado Yap class boat; white-hulled Philippine Coast Guard craft; or a distant formation shot where the boat is a speck.
- **If not found:** Any Jose Andrada-class hull, even one with a later gun fit, labelled with the boat's name. Otherwise leave the gap; do not substitute another PN patrol class.
- **Leads:** Wikimedia Commons: Category:Jose Andrada-class patrol craft (7 subcategories, incl. Category:BRP Jose Andrada (PC-370), BRP Hilario Ruiz (PC-378), BRP Juan Magluyan (PC-392)) [Mostly Philippine Navy (PD-PhilippinesGov); check each file] (seen); Wikimedia Commons: Category:BRP Jose Andrada (PC-370) [check each file] (seen); DVIDS: Image 9362239, 'U.S. Navy, Philippine Navy, Japanese Maritime Self-Defense Force, and Royal Canadian Navy sail in formation [Image 4 of 4]'. The caption names BRP Jose Andrada (PC 370); check the boat is large enough in the frame. [Public domain (US Navy)] (seen); navy.mil / DVIDS: 'Maritime Cooperative Activity' Philippine Navy patrol boat 'PC 3' (the MCA sails often include Andrada-class boats) [Public domain if a US service member took the photo]
- **Already tried:** Nothing found: no row in the 14 Oct master, curated_sources or the 15 Oct intake, and no photo_subject_gaps entry. The catalogue entry is photo_gap. The only thing in existing-profiles.tsv is the mod's own 512x230 profile art.
- **Licence:** Philippine government photos on Commons are usually tagged PD-PhilippinesGov. IP Code s.176 requires prior approval for commercial exploitation, so check the tag on each file and prefer US DVIDS or navy.mil shots. Do not use photos from PNA, Inquirer, GMA or other news outlets, or Facebook posts.

### `wp_airbase_modern` - Modern Russian airforce base - *any representative photo*

- **Where:** 2 mission(s), opponent/player
- **Find:** A representative Russian Aerospace Forces (VKS) air base: runway, apron or shelters with Russian combat or bomber aircraft visible. Engels (Tu-95/Tu-160) or Olenya are ideal because the variant name and layout come from them. Label it as a representative base, not as Biak or Frans Kaisiepo. Wrong photos: US or NATO bases (the 15 Oct reject was 'US troops at night'), Ukrainian bases, close-ups of a single aircraft with no base visible, and commercial satellite imagery.
- **If not found:** Any clearly Russian military airfield photo with VKS aircraft on the apron, labelled 'Representative Russian air base (context)'. A Copernicus/Landsat image of Engels or Olenya would also be honest if credited.
- **Leads:** Wikimedia Commons: Category:Engels Air Base [varies by file] (seen); Wikimedia Commons: File:Lineup of Tu-95 at Engels Air Base.jpg [unknown (possibly mil.ru CC BY 4.0); check the file page] (seen); Wikimedia Commons: Category:Olenya Air Base (7 files; check none is Maxar/Planet imagery) [varies by file] (seen); Wikimedia Commons: Category:Air Force of Russia bases (browse for mil.ru flight-line shots) [mil.ru files CC BY 4.0; others vary] (seen)
- **Already tried:** The 14 Oct master (P1, asset_group russian_airbase) and curated_sources.tsv queued a MediaSearch for "Russian air force base flightline aircraft" (context_reference, "Generic Russian airbase"). The 15 Oct intake REJECTED the russian_airbase candidate ("US troops at night; not a Russian base"). The catalogue has no gap query for it. The gallery entry is photo_gap.
- **Licence:** Maxar, Planet and Airbus satellite images are copyrighted, so do not use them. Spotter photos on Commons are often CC BY-SA but some are Flickr NC: check. mil.ru files are CC BY 4.0.

### `Liberty` - Statue Of Liberty

- **Where:** 1 mission(s), player
- **Find:** The Statue of Liberty on Liberty Island, New York, with the statue clearly visible, front-lit and filling a good part of the frame. Wrong photos: replicas (Paris, Las Vegas, Odaiba and others), skyline shots where the statue is a speck or missing (the 15 Oct rejection reason), and close-ups of the plaque, crown or stairs.
- **If not found:** Map the existing liberty.jpg as is. A front-lit NPS public-domain photo would be a straightforward upgrade.
- **Leads:** SEST gallery (already on disk): images/bases/liberty.jpg = File:New York City (New York, USA), Statue of Liberty -- 2012 -- 6660.jpg (asset_id liberty, mapped to no unit; graded B because it is backlit and small in the frame) [CC BY-SA 4.0 (Dietmar Rabich)] (seen); Wikimedia Commons: File:Statueofliberty nps.jpg [public domain (National Park Service, US federal)] (seen); Wikimedia Commons: File:Statue of Liberty National Monument STLI 02-05.jpg (and STLI 02-02) [probably NPS public domain; check page] (seen); NPS (nps.gov/stli photo gallery / NPS Digital Image Archives): Statue of Liberty [public domain (NPS); must not imply NPS endorsement]
- **Already tried:** 14 Oct master row 115 and curated_sources.tsv line 34: asset group 'liberty', P4, a search for 'Statue of Liberty New York real photo', exact_photo, 'Context landmark, low priority'. 15 Oct intake: 'liberty' rejected because 'the statue is not in the picture'. The gallery already holds liberty.jpg (CC BY-SA 4.0), but it is mapped to no unit. No photo_subject_gaps entry.
- **Licence:** NPS photos are public domain (US federal). The statue itself (1886) is public domain, so there is no sculpture-copyright issue. Avoid stock-agency and NYC tourism-board images.

### `airbase_raaf_curtin` - RAAF Base Curtin (Bare Base)

- **Where:** 1 mission(s), player
- **Find:** RAAF Base Curtin itself: runway, apron or aerial view with deployed military aircraft. The best fit is fighters or tankers during an exercise (Talisman Sabre 2023/2025, Pitch Black), 2010s-2020s. Wrong photos: sunset silhouettes or close-ups where the airfield cannot be seen (the 15 Oct intake rejected one), RAAF Learmonth or RAAF Scherger (the other two bare bases), Derby town airport, and anything only named 'Curtin' (Curtin University, John Curtin). Also wrong: Pitch Black 2024 images whose caption says Tindal even if DVIDS tags them Curtin.
- **If not found:** An aircraft on the Curtin flightline, captioned 'RAAF Base Curtin, Talisman Sabre 2023 (US Air Force photo)'. It must still be Curtin. Do not substitute Tindal or Darwin for this unit.
- **Leads:** pacaf.af.mil (US Air Force, Pacific Air Forces): igphoto 2003275445: F-22 of the 199th Air Expeditionary Squadron taxiing at RAAF Base Curtin, 2 Aug 2023, Talisman Sabre 23, U.S. Air Force photo by Senior Airman Jai Kurihara-Alfonso [Public domain (US federal work); credit the photographer] (seen); dvidshub.net: News 450574 'Agile operations during Talisman Sabre 23' and its image set (F-22s taxiing at Curtin, an RAAF F-35A taking off from Curtin). Also the DVIDS search 'RAAF Base Curtin' [Public domain if the photographer is US military. Check each credit] (seen); dvidshub.net: Image 7934955 'RAAF Base Curtin operations Talisman Sabre 23' (Capt. Margaret Kealy-Machella). This is a trauma drill, not the airfield, so it is a weak subject. Confirm she is US Air Force and not ADF [Public domain only if US service member] (seen); Wikimedia Commons: Category:RAAF Base Curtin (from the 14 Oct master; one file was rejected at the 15 Oct intake) [varies per file]
- **Already tried:** 14 Oct master row 63 / curated_sources: Category:RAAF Base Curtin (exact_base_reference, P2). 15 Oct intake raaf_curtin REJECTED, 'silhouettes at sunset'. catalogue.js photo_subject_gaps 'RAAF Base Curtin', query intitle:"RAAF Base Curtin". No US-government source has been tried yet.
- **Licence:** Images from the Australian Defence image library (images.defence.gov.au), airforce.gov.au and defence.gov.au are Crown copyright, and so is any ADF-photographer image even when DVIDS mirrors it as 'public domain'. Use only photos credited to US service members, or a Commons file that carries CC BY / CC BY-SA. Contact Air Land and Sea's Talisman Sabre 2025 C-17 photo is press, not free.

### `airbase_rnzaf_auckland` - RNZAF Base Auckland (Whenuapai)

- **Where:** 1 mission(s), player
- **Find:** The RNZAF Base Auckland airfield at Whenuapai: apron, hangars or runway, ideally an RNZAF C-130J (or C-130H / Boeing 757) of 40 Squadron on the flightline, 2010s-2020s. Wrong photos: anything that is only the Whenuapai suburb or locality (the 15 Oct intake rejected 'a childcare centre'), Hobsonville, RNZAF Base Ohakea (where the RNZAF P-8As fly from), and RNZAF aircraft photographed at Red Flag-Alaska or other overseas bases.
- **If not found:** An RNZAF C-130J on the apron, captioned 'RNZAF Base Auckland (Whenuapai), Feb 2025 (U.S. Air Force photo)'.
- **Leads:** dvidshub.net: Image 8890549 '374 AW Leadership visits RNZAF Base Auckland during C-130J standup' (set of 9, Feb 2025, RNZAF C-130J at the base), U.S. Air Force photo by Senior Airman Jacob Wood [Public domain (US federal work)] (seen); dvidshub.net: Image 7198301 'U.S. Ambassador to New Zealand visits 353 SOW, RNZAF 40 SQ for TN22' (taken at the base, 3 May 2022, Exercise Teak Net 22). Check the photographer is US military [Public domain if a US photographer] (seen); Wikimedia Commons: Search 'RNZAF Base Auckland' / 'RNZAF Whenuapai' rather than Category:Whenuapai (the suburb category produced the childcare centre) [varies per file]; MOTAT collection (collection.motat.nz): 'RNZAF, Whenuapai', 1940s aerial views (accession 16-2139 to 16-2550). Historical only [Rights field blank in the listing, so check each record. Do not assume it is free] (seen)
- **Already tried:** 14 Oct master row 64 / curated_sources: Category:Whenuapai (context_reference, note 'Ensure photo is of RNZAF base, not unrelated locality'). 15 Oct intake whenuapai REJECTED, 'a childcare centre'. catalogue.js photo_subject_gaps 'RNZAF Base Auckland', query intitle:"Whenuapai" airbase.
- **Licence:** NZDF and nzdf.mil.nz images are New Zealand Crown copyright. Do not use them unless a Commons copy carries CC BY. Avoid DVIDS 2030108 (Flash Lantern Net 2015), which is credited to the New Zealand Defence Force. Getty 'RNZAF Base Auckland' images are all rights reserved.

### `airbase_us` - U.S. Air Force Base - *any representative photo*

- **Where:** 1 mission(s), player
- **Find:** A representative modern US Air Force base flightline with jets on the ramp, 2000s+. The best fit is Eglin AFB, Florida, because the mission uses Variant1 'Eglin Air Force Base'. Wrong photos: foreign or historical airfields (the 15 Oct intake rejected 'a 1950s French airfield in Indochina'), museum ramps, and Port Moresby / Jacksons International Airport. The mission calls it 'Jackson Field', but the unit itself is a US base, so a Moresby photo would mislabel it everywhere else.
- **If not found:** Any af.mil flightline photo of a USAF base, captioned 'U.S. Air Force base flightline (Eglin AFB, Florida), representative'.
- **Leads:** eglin.af.mil News/Photos: 'Business as usual' igphoto 2000234143 (F-15 on the flightline, F-16 overhead, C-130 taxiing); 'Flightline activity' igphoto 2002758825 / 2002758838 (June 2021) [Public domain (US Air Force); credit the photographer] (seen); 33fw.af.mil News/Photos: 'Lightning flightline' igphoto 2001660663 (F-35As on the Eglin flightline) [Public domain (US Air Force)] (seen); Wikimedia Commons: Category:Eglin Air Force Base (look for aerial or flightline files sourced from af.mil) [Public domain for af.mil files]
- **Already tried:** 14 Oct master row 116 / curated_sources: search 'United States Air Force base flightline hangars' (context_reference, P4, 'Generic base'). 15 Oct intake usaf_base REJECTED, 'a 1950s French airfield in Indochina'. There is no catalogue.js photo_subject_gaps entry. The gallery's approved a10_base photo (Patrick AFB flightline, PD) is a same-family precedent for a generic USAF base.
- **Licence:** Use only af.mil, dvidshub.net or defense.gov photos by service members. Do not use Lockheed Martin or Boeing marketing photos, Florida state or local news images, or stock sites.

### `fr_as_332M` - AS332M Super Puma

- **Where:** 1 mission(s), player
- **Find:** A French military AS332 Super Puma, long fuselage (AS332M/M1, or the French Air Force AS332L/L1), in ALAT or Armee de l'Air service, 1990s-2020s. Next best: another military AS332M1 (Spanish 402 Esc HT.21, Swiss T-3xx). Wrong photos: the SA330 Puma (older, smaller nose, wheels not in sponsons), the H225/EC725 Caracal (5-blade rotor, new nose), short-fuselage AS332B/F (the pack has separate fr_as_332B and fr_as_332F units), and civil offshore Super Pumas. Those are acceptable only as a labelled family reference.
- **If not found:** The existing superpuma.jpg, labelled 'Super Puma family (Finnish Border Guard AS332L1), not the French military aircraft', or the Spanish 402 Esc AS332M1 file labelled 'AS332M1 Super Puma, Spanish Air Force 402 Esc (one of this unit's liveries)'.
- **Leads:** Wikimedia Commons: Category:Airbus Helicopters H215 Super Puma by operator (lists subcategories 'Airbus Helicopters AS 332 Super Puma in the French Army' (2 files) and '... in the French Air Force'; click through from here) [mixed; check each] (seen); Wikimedia Commons: Category:F-RAFY (aircraft) (a French Air Force AS332, several photos) [mixed; check each] (seen); Wikimedia Commons: File:Aerospatiale AS-332M1 Super Puma (HT.21A-4 - 402-23) del 402 Escuadrón, Ala 48 del Ejército del Aire (14918506943).jpg (exactly the mod's Squadron3 airframe, 402-23) [Flickr import, probably CC BY-SA 2.0; check page] (seen); Wikimedia Commons: File:AS332M1 Super Puma - RIAT 2014 (center).jpg (operator not confirmed, probably the Swiss AF display) [check page] (seen)
- **Already tried:** 14 Oct master row 41 and curated_sources.tsv line 43: asset group 'superpuma', P2, Category:Eurocopter AS 332 Super Puma, exact_class_photo, 'Subtype/operator requires verification'. 15 Oct intake: 'superpuma' rejected with 'the gallery's photo stays'. The gallery holds superpuma.jpg (File:AS332 Super Puma OH-HVF Turku Airshow 2015 03.JPG, Finnish Border Guard AS332L1, public domain by MKFI) and cougar.jpg (German MoD AS532, CC BY 2.0), but neither is mapped to fr_as_332M. No photo_subject_gaps entry.
- **Licence:** French MoD (defense.gouv.fr / ECPAD) images are not freely licensed. AN- and JP-numbered Commons imports are often GFDL-only. Airbus Helicopters press photos are not allowed.

### `jmsdf_ddh_hyuga` - Hyūga Class

- **Where:** 1 mission(s), player
- **Find:** JS Hyūga (DDH-181), or her sister JS Ise (DDH-182), from 2009 onward: full-length flight deck with a starboard island. These would be WRONG: the Izumo-class (DDH-183/184: larger, no Mk 41, now F-35B capable), the WWII battleship/hybrid carriers Ise and Hyūga (1917-18), or the Shirane/Haruna-class DDH.
- **If not found:** Use the gallery's existing JS Ise image, captioned 'JS Ise (DDH-182), Hyūga-class sister ship'. A Hyūga-specific photo is only a nice-to-have.
- **Leads:** Wikimedia Commons: Category:JS Hyūga (DDH-181) and Category:Hyuga class destroyers [mixed: US Navy PD, CC BY-SA, JMSDF] (seen); Wikimedia Commons: File:US Navy 091117-N-6233H-098 The Japan Maritime Self-Defense Force helicopter destroyer JS Hyuga (DDH 181) leads a formation of U.S. Navy and Japan Maritime Self-Defense Force sips during Annual Exercise (ANNUALEX 21G).jpg (MC1 John M. Hageman, Nov 2009) [public domain (US Navy)] (seen); Wikimedia Commons: File:JS Hyuga (DDH-181) - Starboard beam view.jpg (Matthew Fern, 9 Oct 2009, 4729x3153, via Flickr) [CC BY-SA 3.0 US (credit Matthew Fern)] (seen); Wikimedia Commons: File:USS Sterett (DDG 104), JS Hyuga (DDH 181), USS Kidd (DDG 100) and USS Robert Smalls (CG 62) sail in formation during Multi-Large Deck Event (MLDE) (8114905).jpg (Nov 2023, current fit; the ship appears small in a formation) [probably public domain (DVIDS / US Navy); confirm the tag] (seen)
- **Already tried:** No Hyūga row in the 14 Oct master, curated_sources.tsv, the 15 Oct intake or photo_subject_gaps; the catalogue has it as photo_gap. However, the sister unit jmsdf_ddh_ise from the same mod already maps to asset 'ise': images/update_190/ise_1ffff13924.jpg, from Commons 'File:JS Ise, Haruyuki and Abukuma in the East China Sea after Keen Sword 2013, -16 Nov. 2012 c.jpg' (US Navy 121116-N-EY938-612, public domain). The 5 Oct check passed it as same_type (profiles.tsv line 219: 'JS Ise (DDH-182) underway, full broadside'); its catalogue integration_review is still 'pending'. This unit includes Ise as Variant2, so that photo is already an exact-class image and can be aliased now with no new research.
- **Licence:** JMSDF website photos are released under the Government of Japan terms (CC BY 4.0-compatible), but some JMSDF pages exclude third-party photos, so confirm per image. Do not use the mod's Workshop render (existing-profiles.tsv 1024x360) without the author's permission.

### `ko_ffg-818` - Daegu Class

- **Where:** 1 mission(s), player; sold in sest-southern-reach-open; sest-southern-watch-open
- **Find:** A clearly identifiable Daegu-class frigate (FFX Batch II) of the ROK Navy, hull numbers 818-827, ideally a broadside or 3/4 view at sea where the pennant number can be read. A photo is wrong if it shows: an Incheon-class ship (FFG-811 to 817, FFX Batch I; the gallery already has 'incheon'); a Chungnam-class ship (FFG-828 and up, Batch III, flat-faced integrated mast with fixed radar panels); the Pohang-class corvette ROKS Cheonan (PCC-772) that sank in 2010, or any Pohang-class corvette (these clash with the frigate names Cheonan and Pohang); a builder's scale model (the Commons class category holds an HDF-3500 model photo); or a distant formation shot where the class cannot be told apart (the reason the 15 Oct intake rejected the last candidate).
- **If not found:** The existing 'incheon' asset (File:Incheon 0228.JPG, public domain), labelled 'Incheon class (FFX Batch I), the predecessor of the Daegu class; family reference, not the Daegu class'.
- **Leads:** Wikimedia Commons: Category:ROKS Seoul (FFG-821): 7 files, including the ship underway in the Yellow Sea at the 73rd Battle of Incheon commemoration (14 Sep 2023) and a 2023 exercise with USS John Finn [US Navy files are public domain; check each ROK-sourced file (KOGL Type 1 or CC BY-SA)] (seen); Wikimedia Commons: Category:Daegu class frigates (parent category; ship subcategories for Cheonan, Daegu, Daejeon, Gyeongnam and Seoul; Gyeongnam (FFG-819) and Cheonan (FFG-826) were empty when searched) [varies per file] (seen); DVIDS: News 566280, 'U.S., Republic of Korea conduct Maritime Counter Special Operations Forces Exercise for 2026' (11-14 May 2026), which lists ROKS Daegu (FFG 818). Look at the photos attached to it. [Public domain (US Navy) if a service member took the photo] (seen); DVIDS: Image 9402351, 'Dewey participates in MCSOFEX [Image 5 of 8]', and the rest of that set. These may be the same Nov 2025 Daejeon shots already rejected as too distant, so check before using. [Public domain (US Navy)] (seen)
- **Already tried:** 14 Oct master + curated_sources: queued Category:ROKS Daejeon (FFG-823) as exact_class_photo (P2), noted 'needs visually recognizable photo'. 15 Oct intake: asset 'daegu' REJECTED, 'the ships are too far to identify'. catalogue.js photo_subject_gaps: 'Daegu class frigate', research_query intitle:"ROKS Daegu". The only thing in existing-profiles.tsv is the mod's own 1024x324 profile art, not a photo.
- **Licence:** Do not use builder images from Hanwha Ocean/DSME or HD HHI, or Yonhap and other news-agency photos. ROK government images must say KOGL Type 1 (attribution) on Commons, not KOGL Types 2-4 (non-commercial or no-derivatives). Avoid DVIDS images marked 'courtesy photo' from the ROK Navy unless the Commons file carries a free licence.

### `nato_large_pvo_airbase1` - Barksdale Air Force Base

- **Where:** 1 mission(s), player
- **Find:** Barksdale AFB, Louisiana: B-52Hs on the flightline or ramp, or an aerial of the airfield, 2000s-2020s. Wrong photos: base buildings or housing without the airfield (the 15 Oct intake rejected 'a house; no airbase in view'), and B-52s photographed at Minot, Andersen, Fairford or Edwards. The ini's 419th FLTS is an Edwards unit, so do not chase Edwards images.
- **If not found:** B-52Hs on the Barksdale flightline, captioned 'Barksdale AFB, Louisiana (U.S. Air Force photo)'. Note that the mission renames the unit 'Range field'.
- **Leads:** barksdale.af.mil News/Photos: B-52H Stratofortress bombers on the flightline at Barksdale AFB (e.g. the 11 July 2013 image of B-52Hs taxiing to parking); also 10af.afrc.af.mil igphoto 2002491298 (a 307th BW B-52 on the flightline before Hurricane Laura, 2020) [Public domain (US Air Force); credit the photographer] (seen); af.mil / dvidshub.net: 'Barksdale Air Force Base flightline' / 'Barksdale aerial' [Public domain]; Wikimedia Commons: Category:Barksdale Air Force Base (one file was already rejected; pick a flightline or aerial file sourced from af.mil) [Public domain for af.mil files]
- **Already tried:** 14 Oct master row 44 / curated_sources: Category:Barksdale Air Force Base (exact_base_reference). 15 Oct intake barksdale REJECTED, 'a house; no airbase in view'. catalogue.js photo_subject_gaps 'Barksdale Air Force Base', query intitle:"Barksdale" aerial.
- **Licence:** Use only US federal photos. Avoid Shreveport / Louisiana local-news and state images, the 1930s 'World's Largest Airport' postcard on airplanes-online.com (unknown rights), and stock sites.

### `usaf_f-15e_SE` - F-15E

- **Where:** 1 mission(s), player; sold in sest-southern-reach-open; sest-southern-watch-open
- **Find:** A USAF F-15E in gunship grey with conformal fuel tanks and two crew, ideally tail code SJ, MO or LN. Wrong subjects: F-15EX (two-tone camouflage), F-15K/SG/SA/QA/IA, F-15C/D and F-15J.
- **If not found:** Not needed: the exact photo (asset f15e) is already in the library.
- **Leads:** Already in the SEST gallery: integration/gallery/source/images/aircraft/f15e.jpg (asset f15e): Commons File:Green Flag West 11-08.jpg, SrA Brett Clashman, USAF 110622-F-KX404-022. It shows an SJ-coded (4th FW) F-15E in flight, an exact match for the mod's 334/335/336 FS. No research needed: map usaf_f-15e_SE to asset f15e. [Public domain (USAF)] (seen); dvidshub.net / seymourjohnson.af.mil (only if a different frame is wanted): "F-15E Strike Eagle" "4th Fighter Wing" OR "494th Fighter Squadron" [Public domain (USAF)]
- **Already tried:** 14 Oct master and curated_sources: search 'USAF F-15E Strike Eagle in flight' (exact_photo, P2). 15 Oct intake: an f15e candidate was rejected with 'the gallery's photo stays', because the f15e asset already exists. But in catalogue.js this unit still has asset_id empty and mapping_status photo_gap, and profiles.tsv has no row for it. This is a mapping gap, not a research gap.
- **Licence:** The existing file is public domain (a USAF work). If replacing it, avoid Boeing marketing images and spotter photos on JetPhotos or airliners.net.

### `usn_asv_saronic_corsair_scout` - Saronic Corsair Scout ASV

- **Where:** 1 mission(s), player
- **Find:** The real Saronic Corsair (24 ft, about 7.3 m, open-deck autonomous boat) under way, ideally in US Navy or US government trials. The scout fit is the modder's sensor setup on the same hull, so any Corsair photo matches it. A photo is wrong if it shows another Saronic model (the small Spyglass, the mid-size Cutlass, the large Marauder), another maker's USV (MARTAC Devil Ray/Mantas, L3Harris, Saildrone), or a mod render.
- **If not found:** One Corsair photo can cover all 7 Corsair variants, labelled 'Saronic Corsair; the scout fit is a mod configuration'. If no free photo exists, use an in-game screenshot of the mod model, with the mod author's permission (Workshop 3766210676). Do not use a different USV as a stand-in.
- **Leads:** DVIDS: 'Saronic' / 'Corsair autonomous surface vessel' (check the credit is a US service member, not a 'courtesy photo' from Saronic) [Public domain if taken by US military personnel]; Wikimedia Commons: search 'Saronic Corsair' / 'Saronic Technologies' [check the source of each file]; navy.mil photo gallery: 'Saronic' OR 'Corsair ASV' (unmanned surface vessel exercises) [Public domain (US Navy)]
- **Already tried:** Nothing found: no row in the 14 Oct master, curated_sources, the 15 Oct intake or photo_subject_gaps. All 7 Corsair variants are photo_gap in the catalogue. Web search budget ran out before DVIDS/Commons could be checked for this unit.
- **Licence:** Saronic press kit and website images are manufacturer marketing and need permission. Workshop screenshots and renders need the mod author's OK. DVIDS 'courtesy photo' credits from the company are not federal works.

### `usn_usv_k5_kraken` - K5 KRAKEN fast optionally crewed surface vessel from Kraken 

- **Where:** 1 mission(s), player
- **Find:** The Kraken Technology Group K5 KRAKEN boat itself (about 11 m fast planing USV), ideally in US or allied military trials. The US-built Anduril version for the US Navy is not known to have been photographed yet. A photo is wrong if it shows the smaller K3 SCOUT (a different Kraken model, seen in Royal Navy and NATO trials), an Anduril undersea vehicle (Dive-LD, Dive-XL, Copperhead), or a render.
- **If not found:** One family image for all four K5 variants. Realistically this is an in-game screenshot of the mod's K5 model, used only with the mod author's written OK (Workshop 3819522350), labelled 'in-game model'. Do not use a K3 SCOUT photo as a stand-in unless it is labelled 'smaller sister design K3 SCOUT, context only'.
- **Leads:** DVIDS: 'KRAKEN' 'K5' unmanned surface vessel (check the credit is a US service member) [Public domain if taken by US military personnel]; Wikimedia Commons: search 'Kraken Technology Group' / 'K5 Kraken' [check the source of each file]
- **Already tried:** 14 Oct master 'anduril:k5_kraken' (P0): HOLD, permission / authorized_mod_render, 'Requires permission for product or mod render; reference user screenshot only; No license for Workshop author's screenshot'. additions.tsv says the same. ANDURIL_VARIANT_RECONCILIATION.csv: 'Await Steam export; alias its actual variants to family image'. No catalogue entry or gap entry (NOT IN GALLERY). Web search budget ran out before DVIDS/Commons could be checked for this unit.
- **Licence:** Kraken Technology Group and Anduril website and press images are manufacturer marketing and need permission. Royal Navy and UK MOD photos of Kraken boats are Crown copyright (OGL), and they show the K3 anyway. The Workshop author's screenshots are reference only (README).

### `wp_rkr_kirov_improved` - Kirov-class (Improved)

- **Where:** 1 mission(s), player
- **Find:** Pyotr Velikiy (Northern Fleet flagship, commissioned 1998), the one ship actually in this fit: AK-130 twin gun aft, Kortik/Kashtan mounts, Kinzhal VLS. The Frunze and Kalinin refits to this standard are a what-if under the Soviet flag, so label the photo as Pyotr Velikiy. Clear 3/4 or broadside at sea. A photo is wrong if it shows: Admiral Nakhimov after its 2020s refit (UKSK VLS, Pantsir-M, no Granit; that is the separate unit wp_rkr_admiral_nakhimov_refit); the original Kirov/Admiral Ushakov (twin 100 mm guns, SS-N-14); the 19th-century ironclad Pyotr Velikiy; or a model.
- **If not found:** For the Frunze and Kalinin variants, a Pyotr Velikiy photo labelled 'Pyotr Velikiy, the real ship in this configuration; Frunze/Kalinin refits are hypothetical'. A 1980s-90s photo of Kalinin (pre-refit Admiral Nakhimov) labelled as a sister ship would also be honest.
- **Leads:** Wikimedia Commons: Category:Pyotr Velikiy (ship, 1996) (about 46 files; Category:Russian battlecruiser Pyotr Velikiy redirects here) [varies per file] (seen); Wikimedia Commons: File:Russian battlecruiser Pyotr Velikiy-7.jpg (and -9) by Szilas, Baltic Sea, 3 Aug 2017 [Public domain (released by author)] (seen); Wikimedia Commons: File:Russian Battle Cruiser Pyotr Velikiy.jpg [CC BY 3.0 (credit required)] (seen); Wikimedia Commons: File:103. ТАРК «Пётр Великий» проекта 1144, шифр «Орлан».jpg [unknown; check (may be mil.ru CC BY 4.0)] (seen)
- **Already tried:** 14 Oct master + curated_sources: queued only a Commons search 'Pyotr Velikiy Kirov class battlecruiser' as a family_reference (P2), noted 'Parent hull only, improved version fictional'. That note is too strict: Variant3 is Pyotr Velikiy itself, which is exact for this fit. Not in the 15 Oct intake. catalogue.js photo_subject_gaps: 'Kirov class cruiser', research_query intitle:"Pyotr Velikiy" cruiser. The Varyag and Nakhimov-refit units are also photo_gap.
- **Licence:** File:HMS Dragon with Kirov Class 'Pyotr Velikiy' MOD 45157553.jpg (and 45157551) is a Royal Navy / UK MOD image under the UK Open Government Licence (Crown copyright). Under the SEST rules, do not use it unless SEST decides OGL is acceptable; the gallery's licence list already has some OGL files, so ask. Do not use TASS or RIA Novosti photos.


## P2 - opponents and roster units in 1-4 missions

### `airfield_small_1` - Generic small airfield (base game) - *any representative photo*

- **Where:** 26 mission(s), neutral/player
- **Find:** any small military airstrip from the air; a context picture is fine
- **Leads:** Commons, DVIDS aerial photos of small airfields [per file]

### `civ_ms_roro_b` - Base-game 'RORO B', a Soviet medium cargo ro-ro with a bow r

- **Where:** 10 mission(s), neutral
- **Find:** A Soviet-built medium ro-ro of the Ivan Skuridin type (about 140 m, bow ramp/visor, two vehicle decks), ideally one of the named ships under a Soviet or later Russian or other flag. These would be WRONG: the cruise ferry Lev Tolstoy (already rejected), the large Kapitan Smirnov or Akademik Tupolev class ro-ros, Ivan Rogov-class landing ships, or modern Ro-Pax ferries.
- **If not found:** A photo of any Soviet or Russian medium bow-door ro-ro of the same era, captioned 'Soviet medium ro-ro (representative of the type)'. Priority is P2, not P1: it appears in 10 missions but only as neutral traffic.
- **Leads:** Wikimedia Commons: Search by sister-ship name: "Znamya Oktyabrya", "Timur Frunze", "Vera Khoruzhaya", "Viktor Talalikhin", "Nikolay Przhevalskiy", "Gavril Kirdishev" (Commons search for 'Ivan Skuridin' itself returned no ship file) [check each file (CC BY-SA if user-taken)]; Wikimedia Commons / NARA DN-SC series: US Navy Cold War photos of Soviet ro-ro merchants carrying military cargo (search "Soviet roll-on/roll-off" "DN-SC") [public domain (US Navy / DoD)]
- **Already tried:** 5 Oct profiles.tsv line 82: the gallery's 'roro' photo (cruise ferry Lev Tolstoy) was rejected as wrong_subject for civ_ms_roro_b_armed, 'not the Ivan Skuridin-type bow-ramp cargo RORO'. Nothing else in the 14 Oct master, curated_sources.tsv, the 15 Oct intake or photo_subject_gaps, and it is not in the gallery. The web search budget ran out before the class or yard could be confirmed (one source says Soviet ro-ros built at Zhdanov yard, Leningrad, had a large lifting bow door).
- **Licence:** fleetphoto.ru, shipspotting.com and the Russian maritime-registry photos are all rights reserved.

### `civ_fv_sterntrawler_b` - Stern trawler B (base game) - *any representative photo*

- **Where:** 8 mission(s), neutral/player
- **Find:** modern stern trawler (one photo can serve A-D)
- **Leads:** Commons "Category:Stern trawlers" [per file]

### `civ_ms_act_1` - ACT 1-class container ship (base game) - *any representative photo*

- **Where:** 3 mission(s), neutral/player
- **Find:** early container ship (ACT 1 class, 1969)
- **Leads:** Commons "Category:ACT 1 (ship, 1969)" or container ships [per file]

### `civ_ms_car_carrier_a` - Car carrier (base game) - *any representative photo*

- **Where:** 3 mission(s), neutral/player
- **Find:** pure car/truck carrier
- **Leads:** Commons "Category:Car carriers" [per file]

### `plan_type_052d_p3` - Type 052D Phase 3

- **Where:** 3 mission(s), opponent; sold in sest-southern-reach; sest-southern-reach-open; sest-sulu-line; sest-sulu-line-open
- **Find:** One of the 12 Phase-3 hulls named in the mod, with a readable pennant number (156, 122, 132, 162, 123, 124, 133, 163, 164, 165, 134 or 157). These are the 052DL boats with the longer flight deck/hangar section and the big 11-barrel Type 1130 CIWS. The photo should be close enough to see the hull, not a dot on the horizon. A photo is wrong if it shows: an earlier 052D such as Kunming 172, Changsha 173, Hefei 174, Yinchuan 175 or Xiamen 154 (Phase 1/2, shorter deck, Type 730 CIWS on the early ships); a Type 052C; a Type 055; or any of the distant shots the 15 Oct intake already rejected.
- **If not found:** A clear photo of an earlier 052D (e.g. Kunming 172 or Xiamen 154), labelled 'Type 052D (earlier batch, shorter flight deck); family reference, not the 052DL / Phase 3 hull'.
- **Leads:** Wikimedia Commons: Category:PLANS Zibo (DDG-156): about 10 dated files (e.g. 'PLANS Zibo (DDG-156) 20210825.jpg', 1433x430). The naming matches Japan Joint Staff press-release photos; they are low resolution. [Japan Government Standard Terms of Use (CC BY 4.0 compatible) if sourced from the Joint Staff; confirm per file] (seen); Wikimedia Commons: File:PLANS Guilin (DDG-164) sail with PLANS Shandong (CV-17) 20240719.jpg (Japan Joint Staff Office; Category:PLANS Guilin (DDG-164, 2019)). Check that the destroyer is large enough in the frame. [Japan Government Standard Terms of Use (CC BY 4.0 compatible)] (seen); Wikimedia Commons: Category:PLANS Suzhou (DDG-132) (2 photos from 2022) [unknown; check each file] (seen); Wikimedia Commons: Category:Type 052D destroyer: browse the subcategories for Huainan (DDG-123), Tangshan (DDG-122), Kaifeng (DDG-124), Nanning (DDG-162), Lishui (DDG-157) [varies; prefer Japan Joint Staff Office or mil.ru files] (seen)
- **Already tried:** 14 Oct master + curated_sources: queued Category:PLANS Xiamen (DDG-154) as a family_reference only (P1, 'Type 052D baseline, later phase needs verification'). 15 Oct intake: asset 'type052d' REJECTED, 'the destroyers are too far to identify'. catalogue.js photo_subject_gaps: 'Type 052D destroyer', research_query intitle:"Kunming" 172. That query finds the baseline lead ship, which is the wrong phase for this unit. All six 052D unit IDs (p1, p2_1, p2_2, p3, p4, rsa) are photo_gap.
- **Licence:** Chinese state media (Xinhua, CCTV, chinamil.com.cn) is all rights reserved. Australian Defence and NZDF photos of the 2025 Zunyi (107) task group are Crown copyright, and Zunyi is the wrong batch anyway. Japan Joint Staff photos are fine but need attribution.

### `_narco_speedboat` - Go-Fast Boat-class (SMUGGLING) - *any representative photo*

- **Where:** 2 mission(s), opponent
- **Find:** An open, low-freeboard smuggling go-fast of about 10-15 m with several outboards and no armament, ideally shown whole at sea during a USCG or US Navy interdiction (Eastern Pacific or Caribbean). These would be WRONG: a recreational offshore racing powerboat (only a weak family stand-in), an armed Iranian Boghammar or IRGCN FIAC, a narco semi-submersible (that is _narco_narcosub_adv), or a close-up of cocaine bales with no boat in view.
- **If not found:** Any US federal photo of an interdicted go-fast, captioned 'Go-fast smuggling boat (representative of the type)'.
- **Leads:** DVIDS: https://www.dvidshub.net/image/6222383/coast-guard-cutter-james-interdicts-go-fast-vessel-eastern-pacific-ocean (May 2020: the cutter's 26 ft boat alongside a go-fast off Central America) [public domain (US Coast Guard)] (seen); DVIDS: https://www.dvidshub.net/image/5567952/us-coast-guard-cutter-munro-crew-interdicts-suspected-drug-smuggling-vessel. Also search DVIDS for 'go-fast vessel' / 'go-fast'. Rely on the official caption, not the auto-generated descriptions. [public domain (US Coast Guard)] (seen); Wikimedia Commons: Category:Helicopter Interdiction Tactical Squadron, which holds the file 'USCG pursuing gofast boat.jpg' (1625x1950). Open it to confirm the source and the PD-USGov tag. [probably public domain (USCG); not yet confirmed] (seen); Wikimedia Commons: Category:Go-fast boat (a subcategory of Category:Speedboats; 2 subcats, 4 files). These may be recreational boats, not smugglers. [check each file] (seen)
- **Already tried:** catalogue.js photo_subject_gaps has 'Go-fast boat — hull reference' (asset speedboat, query intitle:"go-fast boat"): no reusable photo passed. Nothing in the 14 Oct master, curated_sources.tsv or the 15 Oct intake. existing-profiles.tsv only has the mod's own 512x170 profile art from 3413868677, which is not a photo.
- **Licence:** Avoid AP/Reuters/AFP news photos and Philippine Coast Guard or Navy Facebook images unless a free licence is shown. The Commons 'File:Cutter Bertholf drug interdiction DVIDS1092140.jpg' shows a cocaine bale, not the boat.

### `civ_fv_okean_surprise` - Okean Covert-class Trawler - *no real photo can exist*

- **Where:** 2 mission(s), opponent; sold in sest-southern-watch; sest-southern-watch-open; sest-sulu-line; sest-sulu-line-open
- **Find:** No photo of a covert torpedo-launching trawler can exist. The honest stand-in is the real hull it is built on: an Okean-type ocean-going side trawler, best shown as a Soviet Okean-class small intelligence ship (converted Okean trawler, Cold War). These would be WRONG: a small beam trawler (the 5 Oct check already rejected the Belgian beam trawler 'White Horse' for civ_fv_okean_armed), a stern trawler (BMRT/Atlantik/Mayakovskiy), a large purpose-built AGI (Primorye, Balzam, Vishnya), or a modern purse seiner.
- **If not found:** The Okean-class AGI photo (LINZA, 1986), captioned 'Okean-type side trawler hull (Soviet Okean-class AGI shown). The covert torpedo conversion is fictional.' The same photo would also fill the vanilla civ_fv_okean and civ_fv_okean_armed. Another honest option is an in-game screenshot the user takes, or asking the 3399699218 author for a render.
- **Leads:** Wikimedia Commons: Category:Okean class small intelligence ship [mostly US Navy / DoD public domain; check each file] (seen); Wikimedia Commons: File:Soviet Okean class intelligence collection ship LINZA.JPEG (US Navy, PH1 Jeff Hilton, 1 Sep 1986, Northern Wedding '86, starboard beam). Also File:Okean class intelligence collection ship LINZA -3.JPEG [public domain (US Navy)] (seen); Wikimedia Commons: File:Soviet intelligence gathering trawler Gidrofon, a photo from aboard USS Lipan (3).jpg [probably public domain (US Navy); confirm the tag] (seen)
- **Already tried:** Nothing for this unit in the 14 Oct master, curated_sources.tsv, the 15 Oct intake or photo_subject_gaps; the catalogue has it as photo_gap. profiles.tsv (5 Oct) rejected the gallery's generic 'trawler' photo as wrong_subject for the same hull (civ_fv_okean_armed): 'small Belgian beam trawler, not the much larger Soviet Okean-class side trawler or intelligence ship'. existing-profiles.tsv only has the mod's 512x237 profile art.
- **Licence:** Shipspotting.com, fleetphoto.ru and marinetraffic photos are all rights reserved. Do not use the mod's Workshop render without the author's permission.

### `pla_aaa_type55` - Chinese Type 55 37 mm towed anti-aircraft gun. It is a singl

- **Where:** 2 mission(s), opponent
- **Find:** A single-barrel 37 mm Type 55 towed AA gun on its four-wheel carriage with the gun shield. Chinese or PLA examples are best: a museum piece, or one in service or captured. A Soviet 61-K is the same design and an honest same-design image, but label it '61-K'. These would make the photo wrong: the twin-barrel Type 65 or Type 74 37 mm gun (two barrels side by side), the 57 mm S-60 or Type 59 (longer barrel, bigger carriage), the ZPU or 23 mm ZU-23 guns, or a naval 37 mm mount.
- **If not found:** A Soviet 61-K (M1939) photo labelled 'Soviet 61-K, the design the Type 55 copies (family)'. If neither can be found, use an in-game screenshot the user takes himself.
- **Leads:** Wikimedia Commons: Category:37 mm automatic air defense gun M1939 (61-K). The name follows the en-wiki article title, so search '61-K 37 mm' if it does not resolve. [mixed: PD (US military) and CC BY-SA from museum visitors; check each file]; Wikimedia Commons search: "Type 55" 37mm anti-aircraft gun; also the Chinese name 55式37毫米高射炮 [CC BY-SA (visitor photos, e.g. the Military Museum of the Chinese People's Revolution, Beijing)]; DVIDS / defense.gov / NARA files on Commons: captured 37mm anti-aircraft gun Iraq (1991/2003) or Vietnam. Many Iraqi 37 mm guns were Chinese-built; check whether the caption says single or twin. [Public domain (US federal)]
- **Already tried:** Nothing found. The unit id and the class name (Type 55, 61-K, 37 mm) do not appear in SEST_IMAGE_MASTER_20261014.csv, curated_sources.tsv, commons-review-20261015.csv, the catalogue.js photo_subject_gaps or the catalogue assets. This is a vanilla unit the gallery never indexed. The research budget for web searches ran out, so none of the Commons categories above could be confirmed.
- **Licence:** Do not use PRC state media (81.cn / China Military Online, Xinhua, CCTV); they are all rights reserved. Vietnamese state media is not usable either. Use Commons visitor photos or US federal photos only.

### `pla_spaag_type63` - Chinese Type 63 self-propelled anti-aircraft gun: a T-34(-85

- **Where:** 2 mission(s), opponent
- **Find:** A T-34 hull with the boxy open-topped turret and twin 37 mm barrels. Museum examples exist in Beijing and Hanoi. Watch the name clash: the 'Type 63' light amphibious tank and the 'Type 63' (YW531) armoured personnel carrier are far more common photos, and both are WRONG. Also wrong: the ZSU-57-2 (on a T-54 chassis, twin 57 mm), the ZSU-23-4 Shilka, the Type 80 or PGZ SPAAGs, and any closed-turret SPAAG.
- **If not found:** A Type 65 or Type 74 twin 37 mm towed gun photo labelled 'twin 37 mm gun family carried by the Type 63 (towed version)'. Do not reuse the Shilka photo; it is a different vehicle and gun. The last resort is the user's own in-game screenshot.
- **Leads:** Wikimedia Commons search: "Type 63" anti-aircraft T-34 37mm; also 'Type 63 SPAAG'. Reject light-tank and APC hits. [CC BY-SA (museum visitor photos)]; Wikimedia Commons: Category:Vietnam Military History Museum (Hanoi) and Category:Military Museum of the Chinese People's Revolution. Browse the armour and air-defence subcategories. [CC BY-SA / CC BY; check each]; English Wikipedia article on the Type 63 SPAAG: Open the infobox image and check its Commons licence page [varies; only use it if the Commons page shows PD or CC BY(-SA)]
- **Already tried:** Nothing found. The unit id and 'Type 63' appear in none of the 14 Oct master, curated_sources.tsv, the 15 Oct review or the catalogue.js gaps and assets. The gallery's only SPAAG photos are 'shilka' (ZSU-23-4, PD), 'gepard' and 'pgz09', and none of them is this vehicle. The research budget for web searches ran out, so nothing could be confirmed.
- **Licence:** Avoid PRC and Vietnamese state media and tank-enthusiast sites (all rights reserved). Use Commons visitor photos only.

### `ru_50n6` - 50N6 Search & Track Radar

- **Where:** 2 mission(s), opponent
- **Find:** The real 50N6 / 50N6A (export 50N6E) radar of the S-350 Vityaz: one flat rectangular phased-array antenna on a rotating mast, on a BAZ-6909 8x8 truck. Russian service or an exhibition example (MAKS 2013 showed the 50N6E) both fit. Wrong photos: the 30N6 Flap Lid or 64N6 Big Bird (S-300), the 92N6 Grave Stone or 96L6 (S-400), the Buk 9S36, and the 'S-350 Vityaz scale models at ARMY-2022' file, which shows scale models, not the real system. Do not choose a Flap Lid photo to match the in-game mesh: the gallery shows the real class.
- **If not found:** A photo of another S-350 component that shows the system, e.g. the 50P6E launcher, labelled 'S-350 Vityaz system (50P6E launcher shown); 50N6 radar not pictured'. If nothing real passes, use an in-game screenshot labelled as such. Do not reuse the S-300 Flap Lid photo.
- **Leads:** Wikimedia Commons: Category:50N6E (search shows 7 files in it) [varies by file: Vitaly Kuzmin uploads are usually CC BY-SA 3.0/4.0, but some Kuzmin pages say copyrighted, so check each file] (seen); Wikimedia Commons, inside Category:50N6E: files 'S-350E Vityaz - MAKS2013part4-08.jpg' and 'MAKS2013firstpix04.jpg' (names from the search summary of the category; file pages not opened, so the subject is unconfirmed) [probably CC BY-SA (Kuzmin MAKS 2013 series); check]; Wikimedia Commons: Category:S-350E (parent category, includes the 50N6E subcategory) [varies by file] (seen); Russian MoD (function.mil.ru / mil.ru photo galleries), then Commons: "С-350 Витязь" or "50Н6" in MoD news photos; on Commons search 'S-350 mil.ru' [CC BY 4.0 (mil.ru template on Commons)]
- **Already tried:** Nothing found. Neither the 14 Oct master CSV nor curated_sources.tsv has a row for it, the 15 Oct intake has nothing, and catalogue.js photo_subject_gaps has no query. The gallery entry 3524446392:land_units/ru_50n6 is photo_gap. The gallery has S-300/S-400 radar assets (bigbird, gravestone, 96l6), but they are other systems and not substitutes.
- **Licence:** Almaz-Antey brochure or press images are not allowed. Do not use the ARMY-2022 scale-model photo (a model, not the radar). Kuzmin files carry mixed terms, so read each file's licence block.

### `ru_spaa_mt-lb_sosna` - MTLB Sosna

- **Where:** 2 mission(s), opponent
- **Find:** A Sosna vehicle on the MT-LB chassis: a low flat tracked hull with six road wheels, carrying the Sosna turret module with two packs of six thin missile tubes either side of a central optronic sight. Exhibition photos (Army-2018/2021/2022) are fine. Wrong photos: the Strela-10 / 9K35 (also MT-LB-based, but four large box launchers), the Osa, and the Sosna module on a BMP-3 chassis (reportedly the serial version). A BMP-3 photo is a different configuration and must be labelled as such, not presented as this unit.
- **If not found:** A Sosna on the BMP-3 chassis labelled 'Sosna system, BMP-3-chassis version'. Otherwise a plain MT-LB photo labelled 'MT-LB chassis reference (Sosna module not shown)'. Do not use a Strela-10 photo.
- **Leads:** Wikimedia Commons: Category:Sosna surface-to-air missile system [varies by file] (seen); Wikimedia Commons: File:Sosna surface-to-air missile system 01.jpg and File:Sosna surface-to-air missile system 02.jpg (own-work uploads, Aug 2021) [probably CC BY-SA 4.0 (own work); check, and check the chassis is MT-LB] (seen); Wikimedia Commons: File:Sosna surface-to-air missile system - Army-2022 22.jpg [unknown, check the file page] (seen); Wikimedia Commons: Category:Army-2021 and Category:Army-2022 (browse for further Sosna frames) [varies (own work CC BY-SA, or mil.ru CC BY 4.0)] (seen)
- **Already tried:** The 14 Oct master CSV and curated_sources.tsv queued only a Commons MediaSearch for "Sosna air defense system on MT-LB" (family_reference, note "Model match needs check"). It was never imported, and the 15 Oct intake has no row. catalogue.js has a related gap, asset 'mtlb' ("MT-LB — chassis reference", query intitle:"MT-LB"), which is also unfilled. The gallery entry is photo_gap. The mod author's in-game profile picture exists (existing-profiles.tsv, 530x160) but is not a photo.
- **Licence:** Vysokotochnye Kompleksy / KBP marketing images are not allowed. Check each Army-forum file: some are own work, some come from news agencies.

### `ru_vityaz-lr_tel` - S-350 Vityaz-LR TEL

- **Where:** 2 mission(s), opponent
- **Find:** The real S-350 launcher, 50P6 / 50P6A (export 50P6E): a BAZ-6909 8x8 truck carrying a rectangular block of 12 missile canisters that is raised vertically to fire. Wrong photos: the S-300 5P85 (four large tubes), the S-400 51P6, Buk TELARs, the ARMY-2022 scale models, and the shipborne Redut/Poliment VLS (which uses the same 9M96 missiles). One 50P6 photo can serve all three Vityaz TELs (LR, MR, SR).
- **If not found:** If only an S-350 radar or command-post photo passes, label it 'S-350 Vityaz system (launcher not shown)'. Otherwise use an in-game screenshot. Do not use an S-300 or S-400 launcher photo for this unit.
- **Leads:** Wikimedia Commons: File:S-350E Vityaz - MAKS2013part4-29.jpg (50P6E TEL at MAKS 2013, source vitalykuzmin.net) [CC BY-SA 3.0 per the search snippet; confirm on the file page; credit Vitaly V. Kuzmin] (seen); Wikimedia Commons: Category:S-350E (other MAKS2013part4 frames) [probably CC BY-SA (Kuzmin); check] (seen); Russian MoD mil.ru photo galleries, then Commons: "С-350 Витязь пусковая установка 50П6" [CC BY 4.0 (mil.ru)]
- **Already tried:** Nothing found. The 14 Oct master, curated_sources.tsv and the 15 Oct intake have no row, and catalogue.js has no gap query. The gallery entry 3524446392:land_units/ru_vityaz-lr_tel is photo_gap. The gallery s300 and s400 assets show different systems.
- **Licence:** Kuzmin files carry mixed terms (some pages say copyrighted), so confirm the CC licence block. Almaz-Antey or Obukhov plant promotional images are not allowed.

### `wp_shahed238_launcher` - Shahed 238 TEL

- **Where:** 2 mission(s), opponent
- **Find:** The Shahed-238 airframe: a Shahed-136-style delta wing with a turbojet engine pod on top of the rear fuselage and no pusher propeller, photographed in Iran in 2023 or later. A real Shahed-238 launch truck or rail would be ideal, but no free photo of one is known. Wrong: Shahed-136/Geran-2 (propeller; this is what the gallery's shahed136 asset shows), Shahed-131, Shahed-191/Saeqeh, a Silkworm/HY-2 launcher (matches the in-game mesh but is a different system), and wreckage photos of unidentified 'Shahed' drones.
- **If not found:** The Commons Shahed-136 rally photo (Meghdad Madadi, CC BY 4.0) captioned 'Shahed family (Shahed-136 shown; the 238 is the jet version)'.
- **Leads:** Wikimedia Commons: Category:Shahed 238 (one file; parent Category:Shahed UAVs) [CC BY 4.0] (seen); Wikimedia Commons: File:August 2024 National Aerospace Park tour for journalists (20).jpg (15 Aug 2024, 800x557) [CC BY 4.0 (Tasnim, Masoud Shahrestani)] (seen); Wikimedia Commons search: "August 2024 National Aerospace Park tour for journalists" (other numbers in the set, e.g. (30) (cropped), may show other angles) [CC BY 4.0 (Tasnim)] (seen); Wikimedia Commons search: Shahed-238 at the 19 Nov 2023 IRGC Aerospace exhibition, Ashura Aerospace University (khamenei.ir or Tasnim) [CC BY 4.0 if the file is on Commons]
- **Already tried:** Nothing for the 238. It is not in the 14 Oct master, has no 15 Oct row and no gap entry, and catalogue.js lists it as photo_gap. Related Shahed-136 work exists: the 14 Oct rows shahed_tel_black and shahed_tel_white queued a search for 'Shahed-136 mobile launcher Iran' as a family reference, never reviewed; photo_subject_gaps has 'shahed136_weapon' (intitle:"Shahed-136"). On 5 Oct the gallery's shahed136 asset was replaced by a 392x220 image supplied by the SEST author, with no credit in added-photo-credits.csv. It replaced File:Military equipment displayed for the 44th Iranian revolution anniversary rally - Shahed 136.jpg (Meghdad Madadi, CC BY 4.0). The mod's ods_shahed238 profile (1200x650) is the author's render.
- **Licence:** Use only images that carry Tasnim's CC BY 4.0 on the Commons file page. Not usable: photos on CSIS Missile Threat (credited to the Operational Environment Data Integration Network), TWZ, Army Recognition, Militarnyi, and the Ukrainian GUR war-sanctions site. Ukrainian police wreckage photos on Commons are CC BY 4.0 but show debris that cannot be identified as a 238.

### `civ_as-350` - AS.350B

- **Where:** 1 mission(s), opponent; sold in sest-sulu-line; sest-sulu-line-open
- **Find:** A civilian AS350 B/BA/B2/B3 Ecureuil (AStar or H125 also fine), single engine, in a plain charter or utility livery, preferably flying. A Philippine RP-C registered or Southeast-Asian civil example would be ideal. Wrong photos: the AS355 Ecureuil 2 or TwinStar (twin engines, two exhausts), AS550/AS555 Fennec military versions or armed police H125s (e.g. the PNP H125 at PFDX 2023), and the EC130/H130 (wider cabin, fenestron tail). A police or air-ambulance AS350 is only acceptable as a labelled type reference.
- **If not found:** Any clear civilian AS350/H125 photo, labelled 'AS350 Ecureuil (civil), type reference' with the actual operator and registration in the caption.
- **Leads:** Wikimedia Commons: Category:Aerospatiale AS350 [mixed; check each file] (seen); Wikimedia Commons: Category:Airbus Helicopters H125 Écureuil [mixed; check each file] (seen); Wikimedia Commons: File:VH-VCZ Aerospatiale AS350BA Ecureuil Professional Helicopter Services (8546324796).jpg (Australian civil charter AS350BA, Flickr import) [Flickr import, probably CC BY-SA 2.0; check page] (seen); Wikimedia Commons: File:Eurocopter AS350B.jpg [unknown; check page] (seen)
- **Already tried:** Nothing found. No row in the 14 Oct master or curated_sources.tsv, no 15 Oct intake decision, no photo_subject_gaps entry, and the gallery holds no AS350 asset.
- **Licence:** Files named '... ANnnnnnnn.jpg' (Airliners.net) and '... JPnnnnnnn.jpg' (JetPhotos) are frequently GFDL-1.2-only, which is not on SEST's allowed list. Flickr imports must be CC BY or BY-SA, not NC. Airbus Helicopters press images are manufacturer marketing: not allowed.

### `ir_aor_delvar` - ir_aor_delvar

- **Where:** 1 mission(s), opponent; sold in sest-southern-watch; sest-southern-watch-open
- **Find:** A Delvar-class auxiliary under the IRIN flag, preferably a cargo/ammunition ship (Delvar 471, Sirjan 472, Charak 481, Chiroo 482, Souru 483) rather than the round-sterned water-carrier version. These would be WRONG: IRIS Shahid Rais-Ali Delvari (a different ship despite the name), the Kharg or Bandar Abbas-class replenishment ships, the Hendijan class, or Hengam-class landing ships.
- **If not found:** The US Navy 2010 Chiroo photo is an exact-class photo. Caption it 'IRIS Chiroo (482), Delvar class'.
- **Leads:** Wikimedia Commons: Category:Delvar-class ships (subcategories IRIS 471 Delvar, IRIS 472 Sirjan, IRIS 481 Charak, IRIS 482 Chiroo, IRIS 483 Soroo, IRIS 424 Deylam) [mixed: US Navy PD, or Tasnim/Fars/Mehr CC BY 4.0 if tagged] (seen); Wikimedia Commons: File:US Navy 100820-N-6003P-637 Eight mariners board the Iranian navy ship Chiroo from a rigid-hull inflatable boat from the aircraft carrier USS Harry S. Truman (CVN 75).jpg (Arabian Sea, Aug 2010, after a fire aboard). Check that the ship is in full view and not dominated by fire damage. [public domain (US Navy)] (seen); Wikimedia Commons, Tasnim / Fars / Mehr imports: Files inside the Delvar-class subcategories credited to Tasnim, Fars or Mehr (naval parades, Bandar Abbas) [CC BY 4.0 (only where the Commons file carries that tag)]
- **Already tried:** 14 Oct master row 48: P2 - fill/review, asset delvar, search 'Iranian navy supply ship Delvar', operator_family_reference, 'Exact hull identification needs verification', status 'search candidate; photo and licence need review'. curated_sources.tsv line 46 has the same entry. Nothing in the 15 Oct intake or photo_subject_gaps. The catalogue has it as photo_gap with label 'ir_aor_delvar'.
- **Licence:** IRNA, Press TV and globalsecurity.org images are not free. Iranian agency photos are usable only via a Commons file carrying the Tasnim/Fars/Mehr CC BY 4.0 tag, with credit.

### `irinavy_bell-212` - IRINAVYBell-212

- **Where:** 1 mission(s), opponent; sold in sest-sulu-line; sest-sulu-line-open
- **Find:** A twin-engine Bell 212 / AB 212 in Islamic Republic of Iran Navy markings, e.g. at Bandar Abbas or during a Velayat exercise or on a frigate deck. An IRIN AB 212 ASW (roof radome) is also fine. Wrong photos: the Bell 214A/C (Iran's most common Bell: bigger, single engine, broad-chord blades), the Bell 205/UH-1H (single engine), the Bell 412 (four-blade rotor), IRIAA Army camouflage aircraft (acceptable only labelled as the Army variant), and the 2024 Varzaqan crash wreckage.
- **If not found:** The existing ab212.jpg or another Bell 212 / AB 212 photo, labelled 'Bell 212 / AB 212 type reference (not an Iranian Navy aircraft)'.
- **Leads:** Wikimedia Commons: Category:Islamic Republic of Iran Navy (browse its naval-helicopter subcategory) [Tasnim / Fars / Mehr CC BY 4.0 with credit; check each] (seen); Wikimedia Commons: Category:Agusta Bell AB 212 [mixed; check each] (seen); Wikimedia Commons: Category:Bell 212 [mixed; check each] (seen); SEST gallery (already on disk): images/aircraft/ab212.jpg = File:Bell AB212. Sunset Air Show. Festival Aereo Internacional De Gijón. 2023. (53105227640).jpg (already mapped to mm_ab212, mm_ab212_91, spa_ab212) [CC BY 2.0 (David Alvarez Lopez)] (seen)
- **Already tried:** Nothing found for this unit. No row in the 14 Oct master or curated_sources.tsv, no 15 Oct intake decision, no photo_subject_gaps entry. The gallery's only related asset is ab212.jpg (Spanish AB212, Gijon 2023), which is mapped to other AB212 units, not this one.
- **Licence:** Only Tasnim, Fars and Mehr files carrying CC BY 4.0 on Commons are usable, with credit to the agency. Avoid IRNA, PressTV and Iranian MoD website images without an explicit licence.

### `pla_h-200a_radar` - H-200A FCR

- **Where:** 1 mission(s), opponent
- **Find:** The HQ-22 / FK-3 battery's engagement radar vehicle: a truck-mounted flat phased-array panel (H-200 family), PLA HQ-22/HQ-22A or Serbian FK-3, 2015+. Wrong photos: the HQ-22 TEL with missile canisters (the gallery already has that as hq22.jpg); the HQ-9 HT-233 radar (the 14 Oct query wrongly said 'HQ 9'); the HQ-16 radar; the JSG-100 / LCQ-776 search radar; and KS-1A's towed H-200 unless captioned as family.
- **If not found:** A Serbian FK-3 radar photo captioned 'FK-3 (export HQ-22) engagement radar, Serbian Armed Forces (family reference)'. Failing that, reuse hq22.jpg captioned 'HQ-22 battery launcher (family reference; radar not shown)'.
- **Leads:** Wikimedia Commons: File:HQ-22 20250921.jpg (颐园居, CC BY-SA 4.0, PLAAF Aviation Open Day / Changchun Air Show, Sept 2025). It shows the TEL only. Browse the same uploader's other uploads from that day for the radar vehicle displayed with the battery [CC BY-SA 4.0] (seen); Wikimedia Commons / Serbian Ministry of Defence (mod.gov.rs): FK-3 (export HQ-22) in Serbian service: MoD images released 30 Dec 2024 of the system in operational configuration; FK-3 shown at the 'Power of Unity' parade, Belgrade, 20 Sept 2025. Search Commons for 'FK-3 Serbia' / 'Snaga jedinstva 2025' [Check: attendee own-work photos are usually CC BY-SA; the MoD site licence is unconfirmed]; Wikimedia Commons: Category:HQ-22 / search 'H-200 radar', 'HQ-22 radar', '红旗-22 雷达' [CC BY / BY-SA per file]
- **Already tried:** 14 Oct master row 53 / curated_sources: search 'H-200A radar China HQ 9 launcher' (family_reference, P2, 'Exact radar scarce'). The query names the wrong system, HQ-9. Nothing reached the 15 Oct intake, and there is no catalogue.js photo_subject_gaps entry. The gallery's hq22 asset (File:HQ-22 20250921.jpg) is mapped to pla_hq-22a_tel / pla_sam_site_hq-22a but not to this radar. The mod's own 256x256 profile picture (existing-profiles.tsv) is a render, not a photo.
- **Licence:** The US-built HQ-22 replica photos are 'courtesy of Torch Technologies', a contractor, so they are not usable without permission and would show a replica in any case. Army Recognition, Defence Blog, The Defense Post and Chinese state media are all rights reserved. The Serbian MoD site's terms need checking before any of its images are used.

### `plaaf_j36` - J-36 Tailless Fighter

- **Where:** 1 mission(s), opponent
- **Find:** The Chengdu three-engine tailless diamond/double-delta prototype itself (serial 36011 or a later prototype), 2024 or later. The caption must say it is a prototype and that the name is unofficial. Wrong subjects: the J-20 or J-20S chase aircraft, J-35, the Shenyang 'J-50', the GJ-11 drone, fan CGI, model kits and AI images.
- **If not found:** An in-game screenshot the user takes of Workshop mod 3801549552, with the mod author's permission, captioned 'in-game model (J-36 prototype, unofficial designation)'. Do not use a J-20 as a 'family' stand-in: it is a different aircraft and would mislead.
- **Leads:** Wikimedia Commons search: "J-36" / "Chengdu J-36" / "36011" (web searches found no Commons category or file) [None free known]; en.wikipedia.org/wiki/Chengdu_J-36: Check whether the article's image is a Commons file with a free licence or a local non-free (fair-use) upload. Fair use cannot go to Steam. [Probably non-free; check]; Wikimedia Commons, after Airshow China (Zhuhai, Nov 2026) or any public display: New uploads of the J-36 by photographers who chose a CC licence. Check each file's own licence. [CC BY / CC BY-SA if one appears]
- **Already tried:** 14 Oct master and curated_sources: plaaf_j36, HOLD, concept_reference ('Only verified prototype photo or authorized game render'). Nothing in the 15 Oct intake or photo_subject_gaps. The catalogue shows photo_gap.
- **Licence:** Every known J-36 image is Chinese social-media or spotter footage, or PLA official media (China Military Bugle / 81.cn, reportedly first released June 2026). All are copyrighted, with no free licence. Reposts on TWZ, The Aviationist or migflug are not usable either. No renders and no AI images.

### `plan_j-50` - J-50

- **Where:** 1 mission(s), opponent
- **Find:** The Shenyang twin-engine tailless lambda-wing prototype in flight test, 2024 or later. The caption must say: prototype, unofficial designation, carrier role unconfirmed. Wrong subjects: J-35/J-35A, J-15/J-15T, the Chengdu J-36 (three engines), the GJ-11 drone, renders and AI images.
- **If not found:** An in-game screenshot the user takes of Workshop mod 3670643788, with the author's permission, captioned 'in-game model; real aircraft is an unacknowledged Shenyang prototype'. No family photo is honest here.
- **Leads:** Wikimedia Commons search: "J-50" / "J-XDS" / "Shenyang tailless" (web searches found no Commons file; one site credits Commons for a picture that is really a J-20) [None free known]; en.wikipedia.org/wiki/Shenyang_J-50: Check whether the article image is a freely licensed Commons file or a non-free local upload [Probably non-free; check]; Wikimedia Commons, after any public display (e.g. Airshow China, Zhuhai, Nov 2026): New CC-licensed uploads of the aircraft [CC BY / CC BY-SA if one appears]
- **Already tried:** 14 Oct master and curated_sources: plan_j-50, HOLD, concept_reference ('Concept/prototype verification required'). Nothing in the 15 Oct intake or photo_subject_gaps. The catalogue shows photo_gap.
- **Licence:** Reporting (Breaking Defense, TWZ, migflug) says only social-media and test-flight imagery exists, with no official release, so there is no free licence. News reposts, Weibo and X images cannot be used. No renders and no AI images.

### `plan_ss_type_039` - Type 039 Song-class

- **Where:** 1 mission(s), opponent; sold in sest-southern-watch; sest-southern-watch-open
- **Find:** A PLAN Song-class submarine, 1999 to 2010s, ideally surfaced. Any Type 039G (hulls 321-325 and 314-316) is right for the class. Hull 320, the original Type 039 with its stepped sail, would match the mission's variant exactly. Wrong: Type 039A/B/C Yuan (a larger AIP boat with a different sail), Type 035 Ming, the Kilo class (Project 877/636, which the PLAN also operates) and the 'Type 041' alias.
- **If not found:** File:Song Class submarine 324.jpg should serve as an exact class photo, captioned 'Type 039G Song-class, hull 324'. If it fails review, do not use a Yuan photo; ask for an in-game screenshot instead.
- **Leads:** Wikimedia Commons: File:Song Class submarine 324.jpg (hull 324, during the PLAN's Hong Kong visit, May 2003) [CC BY-SA 3.0, by Kazec (en.wikipedia)] (seen); Wikimedia Commons: Category:Type 039G submarines (10 files; this is the Commons category Wikidata gives for the Type 039) [mixed; check each file] (seen); Wikimedia Commons: File:Song-class Submarine 3.jpg and File:Song-class Submarine 5.jpg (check they show a real boat, not a model) [CC BY-SA 3.0 / GFDL (SteKrueBe, own work, 2005) for no. 3; no. 5 not seen] (seen); DVIDS / navy.mil: "Song class" submarine (for example US Navy or ONI recognition photos) [public domain (US federal)]
- **Already tried:** The 14 Oct master (row 74) and curated_sources.tsv (row 60) queued a Commons MediaSearch for 'Chinese Type 039 Song-class submarine', marked exact_class_photo. It was never reviewed. The 15 Oct intake has no row. The gallery's photo_subject_gaps lists asset 'song' (query intitle:"Type 039" submarine): no photo passed.
- **Licence:** CC BY-SA 3.0 requires a credit and a ShareAlike notice: credit 'Kazec / Wikimedia Commons, CC BY-SA 3.0'. Do not use Chinese state media (China Military Online, Xinhua, CCTV), Weibo or forum photos, or the mod's side-view renders.

### `plan_ss_type_039b` - Type 039B

- **Where:** 1 mission(s), opponent; sold in sest-southern-watch; sest-southern-watch-open
- **Find:** A PLAN Type 039B Yuan-class boat (hulls around 334-347), 2010 or later: the Yuan hull with the redesigned, smoothed conning tower blended into the hull at its base, and flank-array fairings along the lower hull. Wrong: Type 039A (hulls 330-333, 2006, original sail), Type 039C (2021 or later, with a raked sail fairing like Sweden's A26), the Song class, Pakistan's Hangor and Thailand's S26T (export derivatives), and line drawings such as the Commons SVG.
- **If not found:** Reuse the gallery's yuan_family photo (Mullen at Zhoushan, 2011, US DoD, public domain) captioned 'Yuan-class (Type 039A/B family; exact batch not confirmed)'. This matches the 15 Oct decision for the 039C and needs only an alias or also_units entry.
- **Leads:** Wikimedia Commons: Category:Type 039A submarines (the Yuan class; contains File:Yuan class 039B mod SS.svg, which is a drawing, not a photo) [mixed] (seen); Wikimedia Commons / war.gov: File:Mike Mullen departs the Chinese Navy submarine Yuan at the Zhoushan Naval Base.jpg (13 Jul 2011; war.gov igphoto 2002030374). Already in the gallery as yuan_family; the batch is not confirmed [public domain (US DoD)] (seen); DVIDS / war.gov: Mullen Zhoushan submarine July 2011 (other frames from the same visit that may show the sail profile) [public domain (US DoD)]; Wikimedia Commons: File:Yuan (Type 039A) Class Attack Submarine.JPG (2010 US Navy photo used in a CRS report; 039A family only) [public domain (US Navy)] (seen)
- **Already tried:** Nothing for the 039B itself. The 14 Oct master and curated_sources have only a 039C row (Category:Type 039A submarines, family_reference, 'do not claim exact 039C'). The 15 Oct intake approved yuan_family (the Mullen/Zhoushan photo) as same_family for plan_ss_type_039c only; its also_units field is empty, so the approval does not cover the 039B. The gallery's photo_subject_gaps still lists 'yuan' (intitle:"Type 039A"). File:Chinese Type 039A submarine.jpg in that category is doubtful: its upload history describes a Type 093, so do not use it.
- **Licence:** US DoD and US Navy photos are public domain and fine. Not usable: Chinese state media (China Military Online, Xinhua, CCTV, Global Times), Weibo or forum photos, and the mods' side-view profile renders. The Commons 039B SVG is CC BY-SA 4.0 but is a drawing, not a photo.

### `shahed_tel_white` - Shahed-136-white

- **Where:** 1 mission(s), opponent
- **Find:** Same subject as shahed_tel_black: a Shahed-136 on a ground or truck launcher. The Iranian light-grey or white drone suits this unit best, so the Tehran 2023 Tasnim pickup-launcher photo fits it more closely than a black Geran-2. Wrong photos are the same as for the black unit: debris, LUCAS, Shahed-238, renders.
- **If not found:** Reuse whatever photo is approved for shahed_tel_black (one shared asset), with the same 'family reference' label.
- **Leads:** Wikimedia Commons: File:Military equipment displayed for the 44th Iranian revolution anniversary rally - Shahed 136.jpg [CC BY 4.0 (Tasnim); confirm] (seen); Wikimedia Commons: Category:Shahed 136 [varies by file] (seen)
- **Already tried:** 14 Oct master and curated_sources.tsv: acquisition_mode=reuse of shahed_tel_black ("Share Shahed TEL photo; colour only in mod config"), waiting on the parent, which was never approved. The 15 Oct intake has nothing. The gallery entry is photo_gap.
- **Licence:** Same as shahed_tel_black: Iranian agency files (Tasnim/Mehr/Fars) are CC BY 4.0. No news-wire images, renders or the uncredited existing 'shahed136' asset.

### `usn_f-14a` - F-14A Tomcat (US Navy, base game)

- **Where:** 1 mission(s), player
- **Find:** US Navy F-14A Tomcat in flight, 1970s-80s (not F-14B/D)
- **Leads:** DVIDS / navy.mil archive, Commons "Category:Grumman F-14A Tomcat" [Public domain (US Navy)]

### `wp_emad_tel` - EMAD

- **Where:** 1 mission(s), opponent
- **Find:** An Emad missile, ideally on its road-mobile TEL, at an IRGC parade or display, or an Emad launch. The Emad is identified by the Ghadr-style 'baby-bottle' nose with small steering fins on the re-entry vehicle. Wrong photos: Shahab-3 or Ghadr-110 without the finned RV (often mislabelled), Sejjil (two-stage solid), Khorramshahr, Kheibar Shekan, and Scud/Shahab-1/2 TELs (e.g. 'Iranian scud missile launcher.jpg'). Either camouflage scheme is fine.
- **If not found:** An Emad missile on display without the TEL, labelled 'Emad missile (launcher not shown)'. Failing that, a Ghadr-110 on its TEL labelled 'Ghadr family TEL (context; Emad is a derivative)'.
- **Leads:** Wikimedia Commons: Category:Emad (missile) [mostly Iranian agencies (Tasnim/Mehr), CC BY 4.0] (seen); Wikimedia Commons: File:Emad missile by Tasnimnews 03.jpg (758x525) [CC BY 4.0 (Tasnim), per the search snippet] (seen); Wikimedia Commons: File:Emad missile by Tasnimnews 01.jpg (751x532; the category also lists 02 and 04) [CC BY 4.0 (Tasnim)] (seen); Wikimedia Commons, inside Category:Emad (missile): the 2022 Quds Day Emad display photo credited to Mehr News (file name not seen) [CC BY 4.0 (Mehr); check]
- **Already tried:** Nothing found. The 14 Oct master, curated_sources.tsv and the 15 Oct intake have no row, and catalogue.js has no Emad gap query (its nearby gap is 'sejjil', query intitle:"Sejjil", also unfilled). Gallery entries 3493115616:land_units/wp_emad_tel and ammunition/ods_emad are both photo_gap, so one photo could fill both. The mod author's profile picture exists (existing-profiles.tsv, 1842x364).
- **Licence:** The Tasnim files are small (about 750 px wide), so check they are acceptable at gallery size. IRNA, Sepah News and Iranian state TV stills are not automatically CC, so check each one. Do not use CSIS Missile Threat graphics or news-wire photos.

### `wp_fattah1_tel` - Fattah-1

- **Where:** 1 mission(s), opponent
- **Find:** The IRGC Fattah (Fattah-1) missile, photographed in 2023 or later. Best is the missile on or beside its wheeled TEL. A display from the 6 June 2023 unveiling (the missile, often with its separate re-entry vehicle and second-stage motor beside it) is acceptable as the weapon reference. Wrong subjects that look alike: Fateh-110, Fateh-313, Zolfaghar, Haj Qasem and Kheibar Shekan (all Fateh-110-family airframes). Also wrong: Fattah-2 (glide-vehicle nose with small wings), the 'Fatah' MLRS, Tasnim infographics and posters (not photographs), and Getty/AP/Reuters parade shots.
- **If not found:** If no photo shows the TEL, use a Fattah unveiling photo of the missile alone, captioned 'Fattah-1 missile (launcher not shown)'.
- **Leads:** Wikimedia Commons: Category:Fattah (missile) (71 files, mostly 'Unveiling ceremony of Fattah hypersonic missile (NN).jpg') [CC BY 4.0 (Tasnim, photographer Hossein Zohrevand; some files from Fars)] (seen); Wikimedia Commons: File:Unveiling ceremony of Fattah hypersonic missile (28).jpg (also (09), (10), (30), (35); pick one that shows the launcher) [CC BY 4.0, source tasnimnews.ir] (seen); Wikimedia Commons: File:August 2024 National Aerospace Park tour for journalists (10).jpg (listed in Category:Fattah (missile)) [CC BY 4.0 if it matches the rest of the Tasnim set (Masoud Shahrestani); this file's own licence was not seen] (seen); Wikimedia Commons search: "Sacred Defense Week" parade 2024 Fattah (Tasnim or Mehr photos of the 21 Sep 2024 Tehran parade, where a truck carried Fattah) [CC BY 4.0 if the photo is from Tasnim or Mehr; the Getty version is not usable]
- **Already tried:** Nothing found. The unit is not in SEST_IMAGE_MASTER_20261014.csv or curated_sources.tsv, has no row in commons-review-20261015.csv, and has no photo_subject_gaps entry. catalogue.js lists it as mapping_status photo_gap with no asset. The only image on file is the mod author's own profile render (existing-profiles.tsv wp_fattah_tel, 1768x807, from 3672497668/3673703427), which cannot be reused without the author's permission.
- **Licence:** Iranian agency images need a file-by-file check. Tasnim's CC BY 4.0 covers photographs credited to its own photographers (one Commons note warns that images without an agency or photographer credit may not be covered). Fars files rely on an archived site footer, which Commons accepts only for uploads made on or before 13 Feb 2024. Credit both the photographer and the agency. Do not use Getty, AP, Reuters, AFP or WANA images, army-technology.com pictures, or the mod's own profile render.

### `wp_fattah2_tel` - Fattah-2

- **Where:** 1 mission(s), opponent
- **Find:** The Fattah-2 missile as displayed in November 2023 or later: a winged glide-vehicle nose section on a booster. No free photo of a Fattah-2 on a TEL is known, so a photo of the displayed missile is the realistic target. Wrong: Fattah-1, whose nose is a conical re-entry vehicle with no glide body (usable only as a labelled family fallback). Also wrong: photos of the 2023 exhibition in which the missile cannot be identified, and Getty/Reuters/WANA images.
- **If not found:** A Fattah-1 unveiling photo (Category:Fattah (missile)) captioned 'Fattah family: Fattah-1 shown; Fattah-2 has a glide-vehicle nose', or an in-game screenshot the user takes himself.
- **Leads:** Wikimedia Commons: File:Ali Khamenei at IRGC Aerospace Force 2023.jpg (19 Nov 2023, khamenei.ir); check whether Fattah-2 is visible [khamenei.ir content is usually CC BY 4.0 on Commons; this file's licence was not seen] (seen); Wikimedia Commons search: IRGC Aerospace Force exhibition November 2023 / Ashura Aerospace University / khamenei.ir 2023-11-19 [CC BY 4.0 (khamenei.ir, Tasnim, Mehr)]; Wikimedia Commons: Category:Fattah (missile) (check its 71 files for Fattah-2; none is titled Fattah-2) [CC BY 4.0 (Tasnim, Fars)] (seen); tasnimnews.ir, then Commons: فتاح ۲ (Fattah 2) photo galleries of 19-20 Nov 2023; upload to Commons or cite only if the gallery carries the Tasnim CC BY 4.0 footer [CC BY 4.0 (Tasnim)]
- **Already tried:** Nothing found. The unit is not in the 14 Oct master or curated_sources, has no 15 Oct intake row and no photo_subject_gaps entry, and catalogue.js lists it as photo_gap. The only image on file is the mod author's wp_fattah_tel profile render (existing-profiles.tsv), which cannot be reused without the author's permission.
- **Licence:** Same rules as Fattah-1: check each file for the Tasnim, Mehr or khamenei.ir CC BY 4.0 licence, and accept the Fars footer only for uploads made on or before 13 Feb 2024. No Getty, Reuters, WANA or news-site images, and no mod profile render.

### `wp_kraz_tel` - 5P85TE TEL

- **Where:** 1 mission(s), opponent
- **Find:** An S-300PMU-family 5P85T/5P85TE semi-trailer launcher with four canisters, towed by a KrAZ-260 (a long-bonneted 6x6 Ukrainian tractor), Russian or export, 1990s to 2010s. Wrong: the self-propelled 5P85S/D on the cab-forward MAZ-543 8x8 truck (this is what the gallery's existing s300 photo shows); the tracked S-300V/Antey; S-400 and later PMU2 5P85SE2/TE2 trailers on BAZ-64022 tractors (close family only); the 5P85-1 'Towed S-300PT' museum piece (older PT variant); the Chinese HQ-9; HobbyBoss model box art.
- **If not found:** Reuse the gallery's s300 asset (File:S-300 launcher, 2009.jpg) captioned 'S-300P family launcher (self-propelled 5P85 shown; this unit is the KrAZ-towed 5P85TE)'.
- **Leads:** Wikimedia Commons: Category:S-300PMU2 (about 55 files; subcategories 64N6 and 96L6) [mixed: several 2005 MAKS uploads are PD-release; check each file] (seen); Wikimedia Commons: File:S-300PMU2 with tractor-trailer KrAZ-260V.jpg (2000x1435, listed in Category:S-300PMU2) [not seen; check the file page] (seen); Wikimedia Commons: File:S-300PMU2&KrAZ-260-MAKS-2007.jpg (2592x1944, listed in Category:S-300PMU2) [not seen. One 2007 MAKS file in this category is marked as copyrighted, with reuse permission tied to a third-party site; confirm the licence before use] (seen); Wikimedia Commons: File:5P85SE2 of the SAM system S-300 PMU-2.jpg (Vitaly V. Kuzmin, MAKS 2009; a BAZ-towed 5P85SE2, so a family reference) [probably CC BY-SA 4.0 under the Vitaly Kuzmin permission template; check] (seen)
- **Already tried:** Nothing for this unit in the 14 Oct master, curated_sources, the 15 Oct intake or photo_subject_gaps, and catalogue.js lists it as photo_gap. The gallery already holds two related assets. The first is 's300' (File:S-300 launcher, 2009.jpg, by Archlinux, CC BY-SA 3.0): a self-propelled 5P85 on a MAZ-543, mapped as a family reference to pla_sam_site_hq_15 and wp_sam_site_sa_20a/b. The second is 'bigbird' (File:S-300PMU2 64N6E2.jpg), used for wp_big_bird from the same mod.
- **Licence:** Check each file in Category:S-300PMU2: some are PD-release, and at least one 2007 MAKS photo carries a third-party permission that needs checking. The Vitaly Kuzmin template covers only photos published on his site before 30 Aug 2017. Army Recognition, ausairpower and hobby-kit images are all rights reserved.

### `wp_sejjil_tel` - Sejjil

- **Where:** 1 mission(s), opponent
- **Find:** A Sejjil or Sejjil-2 on its TEL (a long semi-trailer, with the missile horizontal or erected), Iran, 2008 or later. A launch photo is acceptable if the launcher is visible, and so is a museum display at the IRGC National Aerospace Park. Wrong: Shahab-3, Ghadr and Emad (liquid-fuel, single-stage, 'baby-bottle' or conical nose), Kheibar Shekan and Haj Qasem. Two other systems share the name: the Sedjil air-to-air missile and the Sejjil UAV.
- **If not found:** A November 2008 Fars launch photo captioned 'Sejjil launch, Nov 2008 (TEL partly visible)'.
- **Leads:** Wikimedia Commons: Category:Sejjil (ballistic missile) (57 files; subcategories 'Sejjil missiles in museums' (65), 'Sejjil-2' (12) and 'Ashoura (missile)') [CC BY 4.0 (Fars, Tasnim, Mehr); check each file] (seen); Wikimedia Commons: File:Sejjil missile launch - November 2008 (21).jpg (series (01) to (23); choose a frame that shows the TEL) [CC BY 4.0 (Fars, Esmaeil Davari; based on the archived Fars footer)] (seen); Wikimedia Commons: File:Sejjil missile launch - November 2008 (18).jpg (avoid unless resolved: its description points to Alamy, which conflicts with the Fars source) [tagged CC BY 4.0, but the source is disputed] (seen); Wikimedia Commons: File:Sejjil-2 missile (1).jpg and File:Sejjil-2. two stage solid propellant ballistic missile.jpg [not seen; check] (seen)
- **Already tried:** The 14 Oct master (row 68) and curated_sources.tsv queued a Commons MediaSearch for 'Sejjil missile Iranian mobile launcher', marked exact_class_photo with the note 'Launcher system, verify from photo'. It was never reviewed. The 15 Oct intake has no row. The gallery's photo_subject_gaps lists asset 'sejjil' (query intitle:"Sejjil"): no photo passed. The only image on file is the mod author's profile render (existing-profiles.tsv, 1868x382), which cannot be reused without the author's permission.
- **Licence:** Fars-sourced files are CC BY 4.0 only through the archived footer, which Commons accepts for uploads made on or before 13 Feb 2024. Skip any file whose description points to Alamy or another stock agency. Credit both the photographer and the agency.

### `wp_silkworm_launcher` - A static coastal rail launcher for the Chinese SY-1, which i

- **Where:** 1 mission(s), opponent
- **Find:** A Silkworm-family (SY-1, HY-1 or HY-2) coastal missile on its single land launch rail or launcher trailer: a museum display or captured equipment, with the missile on the rail if possible. Chinese-built examples, which Iraq and North Korea also operated, are good. These would make the photo wrong: the ship box launchers on Type 051 destroyers or missile boats, the modern truck-mounted YJ-62, YJ-12 or C-802 coastal systems (different missile), and the Soviet 4K51 Rubezh truck. The Rubezh shares the P-15 family but is a Soviet system, so use it only as a labelled family image.
- **If not found:** Reuse the existing 'styx' asset labelled 'P-15 Termit missile, the Soviet original of the SY-1 (missile family; launcher not shown)'. Alternatively, use a captured Iraqi HY-2 site photo labelled as HY-2 family.
- **Leads:** Wikimedia Commons search: HY-2 Silkworm; Seersucker missile; SY-1 missile (上游一号); Silkworm missile launcher museum [CC BY-SA (museum visitors) / PD (US DoD)]; defense.gov / navy.mil / NARA files on Commons: captured Iraqi Silkworm missile launcher (Desert Storm 1991 or Iraq 2003, al-Faw / Umm Qasr area) [Public domain (US federal)]; Commons, Tasnim / Fars uploads: Iranian HY-2 / Silkworm or Raad coastal missile. Only as an operator-mismatch family image, labelled as Iranian. [CC BY 4.0]
- **Already tried:** There is no row for the launcher in the 14 Oct master, curated_sources.tsv, the 15 Oct review or the catalogue.js gaps. The gallery already holds the asset 'styx' (File:P-15 Termit missile 2012 G2.jpg by George Chernilevsky, PD, a P-15M in the Black Sea Fleet Museum), mapped as a family reference for plan_sy-1 and wp_ss-n-2. It shows the missile, not the launcher. The research budget for web searches ran out, so nothing could be confirmed.
- **Licence:** Avoid PRC state media and IHS/Janes images. Iranian agency photos are only usable where Commons shows CC BY 4.0.

### `wp_son-9` - The Soviet SON-9 (NATO 'Fire Can') gun-laying radar: a towed

- **Where:** 1 mission(s), opponent
- **Find:** A SON-9 or SON-9A trailer: a two-axle box van with the parabolic dish on top, preserved in a museum or captured. Polish, Hungarian, Czech, Vietnamese or Iraqi examples are all fine because the radar itself is the subject. These would make the photo wrong: the RPK-1 Vaza (Flap Wheel), the SNR-75 or SNR-125 SAM radars, P-12, P-15 or P-18 search radars, or the S-60 gun alone without the radar.
- **If not found:** An S-60 57 mm battery photo in which a SON-9 trailer is visible, labelled 'S-60 battery with SON-9 fire-control radar'. Otherwise use the user's own in-game screenshot.
- **Leads:** Wikimedia Commons search: SON-9; SON-9A radar; "Fire Can" radar [CC BY-SA (museum visitor photos)]; Wikimedia Commons search (Polish museums): SON-9 radar muzeum. Poland fielded SON-9 with the S-60, and museum photos are common. [CC BY-SA 3.0/4.0]; defense.gov / NARA files on Commons: captured Iraqi or North Vietnamese 'Fire Can' fire control radar [Public domain (US federal)]
- **Already tried:** Nothing found. The terms SON-9 and Fire Can appear in none of the 14 Oct master, curated_sources.tsv, the 15 Oct review or the catalogue.js gaps and assets. The research budget for web searches ran out, so nothing could be confirmed.
- **Licence:** Many radar photos on hobby sites (e.g. radartutorial, militaryfactory) are all rights reserved. Use only Commons PD, CC BY or CC BY-SA files.

### `wp_tombstone` - 30N6E2 Tomb Stone

- **Where:** 1 mission(s), opponent
- **Find:** A 30N6E2 radar (S-300PMU2/PM2), 2000s or later: a flat phased-array face on a mast above a MAZ-7910 8x8 truck. Wrong: the 64N6E2 Big Bird (a large double-sided rotating array; this is the gallery's bigbird asset), the 76N6 Clam Shell, the 96L6, the 92N6 Grave Stone (S-400) and the 9S32 Grill Pan (S-300V). The older trailer-mounted 5N63/30N6 Flap Lid A matches the in-game model but not the unit's name, so it is a family reference only.
- **If not found:** A Category:30N6 or 5N63 Flap Lid photo (for example the ShinePhantom Tolyatti photo) captioned '30N6 family (earlier Flap Lid shown)'.
- **Leads:** Wikimedia Commons: Category:30N6E2 [mostly CC BY-SA (Vitaly V. Kuzmin); check] (seen); Wikimedia Commons: File:30N6E2 radar (S-300PMU2) - 100th Anniversary VVS-R -01.jpg (also -02 and -03; 10 Aug 2012, 2250x1500) [CC BY-SA 4.0 under the Vitaly Kuzmin template (probably); check] (seen); Wikimedia Commons: File:30N6E2 radar for S-300PM2 system - ParkPatriot2015part8-08.jpg (also -09; Aug 2015) [CC BY-SA (search snippet said 3.0); check] (seen); Wikimedia Commons: File:30N6E2 radar MAKS 2009 -02.jpg [not seen; check] (seen)
- **Already tried:** Nothing found. There is no 14 Oct row, no 15 Oct row and no photo_subject_gaps entry, and catalogue.js lists it as photo_gap (category Sensors & equipment). The gallery's only photo from this battery is the 64N6E2 Big Bird (bigbird asset, File:S-300PMU2 64N6E2.jpg), which is a different radar.
- **Licence:** The Vitaly Kuzmin permission template covers only photos published on vitalykuzmin.net before 30 Aug 2017; the 2009, 2012 and 2015 photos should qualify, but confirm on each file page and credit 'Vitaly V. Kuzmin'. Ausairpower and Army Recognition radar photos are not usable.


## P3 - background traffic, roster-only, or no real photo possible

### `civ_fv_sterntrawler_a` - Stern trawler A (base game) - *any representative photo*

- **Where:** 16 mission(s), neutral/opponent
- **Find:** modern stern trawler
- **Leads:** Commons "Category:Stern trawlers" [per file]

### `civ_ms_ritina` - Supertanker (base game) - *any representative photo*

- **Where:** 16 mission(s), neutral/player
- **Find:** VLCC crude tanker
- **Leads:** Commons "Category:Very large crude carriers" [per file]

### `civ_ms_bulk` - Bulk carrier (base game) - *any representative photo*

- **Where:** 12 mission(s), neutral
- **Find:** bulk carrier at sea
- **Leads:** Commons "Category:Bulk carriers" [per file]

### `wp_agi_okean` - Okean-class AGI (base game)

- **Where:** 11 mission(s), opponent; sold in sest-southern-reach; sest-southern-reach-open
- **Find:** Soviet Okean-class intelligence trawler (AGI); US Navy shadowing photos exist
- **Leads:** Commons "Category:Okean class intelligence ships"; US Navy archive [Public domain (US Navy) or per file]

### `civ_fv_sterntrawler_c` - Stern trawler C (base game) - *any representative photo*

- **Where:** 10 mission(s), neutral/opponent
- **Find:** as above
- **Leads:** Commons "Category:Stern trawlers" [per file]

### `civ_fv_okean` - Side trawler (base game, Okean hull) - *any representative photo*

- **Where:** 9 mission(s), neutral/opponent
- **Find:** Soviet-era side trawler
- **Leads:** Commons "Category:Side trawlers" [per file]

### `civ_ms_encounter` - Encounter-class merchant (base game) - *any representative photo*

- **Where:** 9 mission(s), neutral/opponent/player
- **Find:** general cargo ship; context
- **Leads:** Commons "Category:Cargo ships" [per file]

### `civ_ms_roro_c` - RO-RO ship C (base game) - *any representative photo*

- **Where:** 9 mission(s), neutral/player
- **Find:** RO-RO cargo ship
- **Leads:** Commons "Category:Ro-ro ships" [per file]

### `civ_ms_ivan_franko` - Ivan Franko-class liner (base game) - *any representative photo*

- **Where:** 8 mission(s), neutral
- **Find:** Soviet Ivan Franko-class passenger liner
- **Leads:** Commons "Category:Ivan Franko class ships" [per file]

### `civ_fv_sterntrawler_d` - Stern trawler D (base game) - *any representative photo*

- **Where:** 3 mission(s), neutral/opponent
- **Find:** as above
- **Leads:** Commons "Category:Stern trawlers" [per file]

### `civ_ms_roro_a` - Base-game 'RORO A', a cargo ro-ro with a stern quarter ramp.

- **Where:** 3 mission(s), neutral
- **Find:** A Cape Ducato-class (ex-Barranduna-class) ro-ro, as a ScanCarriers ship or as a Cape D-class RRF ship, ideally showing the stern quarter ramp. These would be WRONG: the passenger cruise ferry Lev Tolstoy (already rejected), other MSC ro-ros (Bob Hope/Watson LMSRs, Cape H/Cape T classes), or Australian Strait-class ro-ros.
- **If not found:** Any Cape D-class sister (Cape Douglas, Domingo, Decision or Diamond) as an exact-class photo, captioned with its name. Otherwise a generic stern-quarter-ramp ro-ro captioned 'representative ro-ro'.
- **Leads:** Wikimedia Commons: Category:Cape Ducato (ship, 1972) (ex-Barranduna, Eriksbergs Mekaniska Verkstad) [mixed, check each file] (seen); Wikimedia Commons: File:Cape Ducato.JPEG (MSC-chartered ship at Lambert Point Pier, Norfolk, after Desert Storm; DoD caption style) [probably public domain (US DoD); confirm the tag] (seen); NavSource / MARAD: navsource.org/archives/09/54/545052.htm (Cape Douglas, ex-Lalandia) and vesselhistory.marad.dot.gov ship records for the Cape D class. Use only images credited to the US Navy or MARAD. [public domain only if US-government credited] (seen)
- **Already tried:** Nothing for civ_ms_roro_a in the 14 Oct master, curated_sources.tsv, the 15 Oct intake or photo_subject_gaps, and it is not in the gallery. The gallery's generic 'roro' photo (the Soviet cruise ferry Lev Tolstoy) was rejected as wrong_subject on 5 Oct for ran_ms_roro_a and civ_ms_roro_b_armed (profiles.tsv lines 82 and 398).
- **Licence:** NavSource pages mix US Navy photos with private contributors' photos. Check each credit.

### `wp_ms_mercur_decoy` - Mercur-class merchant as radar decoy (base game)

- **Where:** 3 mission(s), opponent
- **Find:** general cargo ship; context
- **Leads:** Commons "Category:Cargo ships" [per file]

### `civ_fv_crabboat` - A generic ocean-going crab-fishing vessel of the Bering Sea  - *any representative photo*

- **Where:** 2 mission(s), neutral
- **Find:** A large steel crab vessel (Alaska or Bering Sea type) with the house forward, a pot deck aft, and crab pots stacked or a crane visible. Any era works and a colour photo is best. The photo must match the in-game model, not the mission labels. Australian or NZ 'cray boats' are much smaller inshore lobster boats, so a small rock-lobster boat is the WRONG subject. A trawler with a stern gantry or ramp is also wrong.
- **If not found:** A NOAA or USCG photo of any large Alaskan fishing vessel, labelled 'Ocean-going crab boat (representative)'. Do not use the White Horse beam trawler photo for this one; the profile checks already called that rig a mismatch for non-trawler hulls.
- **Leads:** Wikimedia Commons search: crab boat Dutch Harbor; Bering Sea crab vessel; king crab fishing vessel [mixed; NOAA uploads are PD, user photos CC BY-SA]; NOAA Photo Library (photolib.noaa.gov): crab vessel / crab pots Bering Sea [Public domain (US federal, NOAA)]; DVIDS: Coast Guard crab vessel Bering Sea boarding / fishing vessel safety exam [Public domain (USCG)]
- **Already tried:** Nothing found. 'crab' and 'civ_fv_crabboat' appear in none of the 14 Oct master, curated_sources.tsv, the 15 Oct review or the catalogue.js gaps. The gallery's only fishing photo is the asset 'trawler' (File:Fishing trawler "White Horse" beached in Seaford, July 1989 (1).jpg, Barry Lewis, CC BY 2.0). It is a small Belgian beam trawler, not a crabber. The research budget for web searches ran out, so nothing could be confirmed.
- **Licence:** Do not use Discovery 'Deadliest Catch' stills, or photos from the Alaska Department of Fish and Game (a US state agency, so NOT public domain).

### `wp_tu-142m` - Tu-142M Bear-F (base game)

- **Where:** 2 mission(s), opponent; sold in sest-southern-reach; sest-southern-reach-open
- **Find:** Soviet/Russian Tu-142M maritime patrol, often photographed by US/UK/JASDF interceptors
- **Leads:** Commons "Category:Tupolev Tu-142"; DVIDS "Tu-142" [Public domain (US DoD) or JASDF/JMOD terms]

### `Coal_PowerPlant` - Coal Power Plant - *any representative photo*

- **Where:** 1 mission(s), neutral
- **Find:** Any real coal-fired power station that shows the features of the type: boiler house, tall chimney stack, coal yard or conveyors. Ideally it is in Southeast Asia or Indonesia, to fit the setting. Wrong photos: a nuclear plant or cooling towers only (the gallery has a separate nuclearplant asset), gas, hydro or solar plants, and shots where the plant is a speck or hidden by wires.
- **If not found:** Map the existing coalplant.jpg, labelled 'Coal-fired power station: representative photo (Mae Mo, Thailand)'. A sharper Indonesian plant photo would be an upgrade, not a necessity.
- **Leads:** SEST gallery (already on disk): images/bases/coalplant.jpg = File:Mae Mo Coal power station.jpg (Thailand; asset_id coalplant, mapped to no unit) [CC BY-SA 4.0] (seen); Wikimedia Commons: Category:Coal-fired power plants in Indonesia (subcategories Ombilin, Rembang; files of Paiton, Suralaya, Batam, Indramayu and others) [mixed; check each] (seen); Wikimedia Commons: Category:Coal-fired power plants [mixed; check each] (seen)
- **Already tried:** 14 Oct master row 112 and curated_sources.tsv line 32: asset group 'coalplant', P4, a search for 'coal fired power station', context_reference, 'Generic objective, low priority'. Nothing in the 15 Oct intake, no photo_subject_gaps entry. The gallery already holds coalplant.jpg (Mae Mo, CC BY-SA 4.0, quality note: hazy, with foreground wires), but it is mapped to no unit.
- **Licence:** Avoid utility-company press photos (PLN, EGAT and the like) unless they are explicitly CC-licensed.

### `all_life_raft` - A generic 12-person inflatable canopied life raft (the SOLAS - *any representative photo*

- **Where:** 1 mission(s), neutral
- **Find:** A round or octagonal inflatable life raft with an orange or red canopy, afloat at sea, ideally with survivors or rescuers. A deployed raft photo from an abandon-ship drill or a rescue is ideal. These would make the photo wrong: a rigid lifeboat or enclosed davit lifeboat, an open canopy-less raft (that is the separate all_life_raft_open unit), a RHIB or rescue boat, or a raft still packed in its canister.
- **If not found:** Any deployed canopied inflatable life raft photo from USCG or USN, labelled 'Inflatable life raft (representative)'.
- **Leads:** Wikimedia Commons: Category:Life rafts [mixed; many are PD US Navy or US Coast Guard]; DVIDS (dvidshub.net): life raft (US Coast Guard rescue; US Navy abandon-ship drill) [Public domain (US federal; USCG is federal)]; navy.mil photo gallery: inflatable life raft training [Public domain]
- **Already tried:** Nothing found. 'life raft' and 'all_life_raft' appear in none of the 14 Oct master, curated_sources.tsv, the 15 Oct review or the catalogue.js gaps and assets. The research budget for web searches ran out, so nothing could be confirmed.
- **Licence:** Do not use liferaft manufacturer marketing images (Viking, Survitec, Zodiac and similar) or stock-photo sites. AMSA (Australia) images are Crown copyright unless the Commons page shows CC BY.

### `civ_fv_fishingboat_c` - Small fishing boat (base game) - *any representative photo*

- **Where:** 1 mission(s), neutral
- **Find:** small coastal fishing boat; Southeast Asian if possible
- **Leads:** Commons "Category:Fishing boats" [per file]

### `civ_fv_sidetrawler` - Medium seiner (base game) - *any representative photo*

- **Where:** 1 mission(s), neutral
- **Find:** purse seiner fishing vessel
- **Leads:** Commons "Category:Purse seiners" [per file]

### `civ_radiostation` - Civilian radio station (base game) - *any representative photo*

- **Where:** 1 mission(s), neutral
- **Find:** a coastal radio/antenna station; context only
- **Leads:** Commons "Category:Radio masts and towers" [per file]

### `civ_spar_rig` - Oil platform, spar type (base game) - *any representative photo*

- **Where:** 1 mission(s), neutral
- **Find:** a spar-type offshore oil platform
- **Leads:** Commons "Category:Spar platforms" [per file]

### `civ_spar_rig_helo` - Armed oil rig with helo - Iran - *any representative photo*

- **Where:** 1 mission(s), neutral
- **Find:** An offshore oil or gas production platform with a visible helideck: intact, at sea, a whole-structure view. Check the in-game model first to see whether it is a spar (one large floating cylinder) or a fixed jacket platform, and match that. The most specific honest real subject is an IRGC-armed Iranian Persian Gulf platform of the 1987-88 Tanker War (Sassan, Sirri or Rostam/Reshadat), but the surviving US Navy photos show them burning under attack. Wrong photos: jack-up drilling rigs, drillships, onshore rigs, and company PR shots.
- **If not found:** A representative intact offshore production platform with a helideck, captioned 'Offshore oil platform (representative)'. Alternatively the Sassan photo, captioned 'IRGC-armed Iranian oil platform, Persian Gulf, 1988 (context)'. Do not caption either as Rig Seventeen or as a Timor Sea platform.
- **Leads:** US Navy history image gallery (usnhistory.navylive.dodlive.mil): igphoto 2002764073: Sassan platform main building burning after an AH-1 TOW strike, Operation Praying Mantis, 18 Apr 1988, 880418-N-ZZ999-002, Cpl. John Hyp, USMC [Public domain (US federal work)] (seen); Wikimedia Commons / DoD (DVIDS legacy): Search 'DM-SN-93-00987' or '880418-N-ZZ999-002'; Category:Operation Praying Mantis; Operation Nimble Archer (Rostam platforms, Oct 1987) [Public domain]; Wikimedia Commons: Generic intact platform: search 'oil platform helideck' or 'spar platform', and US BSEE / US Coast Guard / NOAA photos of Gulf of Mexico production platforms [PD for US federal files; CC BY / BY-SA otherwise. Check each]
- **Already tried:** 14 Oct master row 40 / curated_sources: search 'offshore spar oil platform helicopter landing' (context_reference, P2; note 'Exact armed fictional installation does not exist'). Nothing reached the 15 Oct intake. catalogue.js photo_subject_gaps 'Offshore oil platform — reference' (asset oilrig), query intitle:"oil platform", is still unfilled. One photo would also cover the vanilla civ_spar_rig.
- **Licence:** Operator photos (Woodside, Santos, INPEX, Shell, NIOC), Getty and Shutterstock are not usable. Tasnim / Fars / Mehr images on Commons are CC BY 4.0 if a modern Iranian platform view is wanted, but confirm the Commons file licence.

### `pla_z21` - Z-21 - *no real photo can exist*

- **Where:** 1 mission(s), opponent
- **Find:** There is no freely licensed photo of the subject. The only real images are leaked 2024 spotter or Weibo photos of the prototype (authors unknown, all rights reserved), and the mod's 2028 service configuration is projected. Anything presented as a 'Z-21' photo must be either a properly licensed photo of the prototype itself (none known) or clearly labelled context. Wrong photos: a Z-10 or Z-19 captioned as Z-21, a Z-20 passed off as Z-21, fan CGI or AI images, and the mod's Workshop preview without permission.
- **If not found:** Either the user's own in-game screenshot labelled 'In-game model (Z-21 prototype; no released photo)', or the existing z20.jpg labelled 'Z-20: the utility helicopter the Z-21 prototype is reportedly derived from; context, not a Z-21'.
- **Leads:** SEST gallery (already on disk): images/aircraft/z20.jpg = File:Z-20 Airshow China 2022 fly.jpg (already mapped to planaf_z-20j and plan_z-20f) [CC BY 4.0 (China News Service)] (seen); Wikimedia Commons: Category:Harbin Z-20 (the parent airframe, context only); no Z-21 category or file found on Commons [mixed; check each] (seen); Steam Workshop item 3774746803 (PLA Z-21 mod author): ask permission to use the author's own preview render or screenshot [only with the author's written permission]; In-game: the user's own screenshot of pla_z21 (Squadron1 desert livery) [user's own work (game screenshot); label as in-game]
- **Already tried:** 14 Oct master row 77 and curated_sources.tsv line 53: asset group 'z21', P2, acquisition_mode 'hold', concept_reference, 'HOLD: do not mislabel conceptual or unidentified hardware', 'Model/prototype photo not confirmed'. Nothing in the 15 Oct intake, no photo_subject_gaps entry. The gallery's z20.jpg is mapped to the Z-20J/Z-20F units only.
- **Licence:** The March 2024 Weibo / spotter photos (republished by The Aviationist, TWZ, Janes, Army Recognition) are copyrighted and must not be used. So must not CGI or AI images, or the mod author's renders without permission.

### `plan_ap_qiongsha` - Qiongsha-class transport (PLAN, base game)

- **Where:** 1 mission(s), opponent; sold in sest-sulu-line; sest-sulu-line-open
- **Find:** PLAN Qiongsha-class (Type 074) troop/supply transport
- **Leads:** Commons "Category:Qiongsha class" [per file]

### `plan_cvn_004` - Type 004 Zhejiang-class - *no real photo can exist*

- **Where:** 1 mission(s), opponent
- **Find:** No real photograph of a finished Type 004 can exist. Press reports up to late Aug 2026 say the hull is still under construction at Dalian, has not been launched, and is known only from commercial satellite imagery. The names Zhejiang/Guangdong/Jiangsu/Shaanxi and the CVN-19 to 22 numbers are unofficial. Anything sold as a 'Type 004 photo' is a render, an AI image, or a copyrighted satellite or shipyard picture.
- **If not found:** Reuse the existing 'type003' Fujian asset, or the JSO Fujian photo, labelled: 'Type 003 Fujian, the conventionally powered predecessor with electromagnetic catapults. Type 004 not yet launched (2026); family/context only.' Or use an in-game screenshot of the mod's model that the user takes, with the OK of the mod author (Workshop 3486502935).
- **Leads:** Wikimedia Commons (family stand-in only): Category:PLANS Fujian (CV-18) [varies; Japan Joint Staff files use the Japan Government Standard Terms of Use (CC BY 4.0 compatible)] (seen); Wikimedia Commons (family stand-in only): File:PLAN CV-18 Fujian 20250911.jpg (Japan Joint Staff photo of Fujian at sea, East China Sea, 11 Sep 2025) [Japan Government Standard Terms of Use (CC BY 4.0 compatible); confirm on the file page] (seen)
- **Already tried:** 14 Oct master + curated_sources: 'type004' set to HOLD / concept_reference, 'Type 004 fictional/future depiction; do not mislabel a carrier'. Not in the 15 Oct intake, and no photo_subject_gaps entry. Related: the gallery already has asset 'type003' (File:Chinese aircraft carrier Fujian flight deck.jpg), used for plan_cv_fujian as a family reference. The 15 Oct intake rejected another 'fujian' candidate ('a shipyard from the air; no carrier identifiable').
- **Licence:** Satellite imagery from Maxar, Planet or Airbus (as used by CSIS, TWZ and Asia Times) is copyrighted. So are X/Weibo shipyard leak photos, Chinese state media (Xinhua, chinamil.com.cn) and concept renders. AI images are not allowed.

### `usa_steelfin_launcher` - A stationary four-cell container launcher for Anduril's Stee - *no real photo can exist*

- **Where:** 1 mission(s), player
- **Find:** No real photo can exist: Steelfin has not flown and no fielded container launcher exists. Only Anduril renders or mock-ups exist, and they are not usable. Any 'Steelfin' photo found online will be a company render or a news photo.
- **If not found:** Best is an in-game screenshot you take yourself, labelled 'In-game model (Steelfin is in development; no photograph exists)'. Second best is a context photo of an M903 Patriot or Typhon launcher, labelled 'Context: launcher family Steelfin is designed for; not Steelfin'; it matches poorly, because the mod shows a container launcher. It is player-side, so do the screenshot early even though no research can succeed.
- **Leads:** Wikimedia Commons (context only, not Steelfin): File:2024-01-05 Typhon MRC 001.jpg (US Army Typhon launcher, one of Anduril's stated host launchers) [probably public domain (US Army); confirm] (seen); SEST gallery (already held): asset 'patriot' (JASDF M901 launcher, CC BY-SA 4.0), context for the M903 launcher Steelfin is meant to use [CC BY-SA 4.0 (already credited in the catalogue)] (seen); DVIDS (dvidshub.net): "M903 launcher" or "Patriot launching station" (context only) [public domain (US federal)]
- **Already tried:** Nothing found. There is no row in the 14 Oct master, curated_sources.tsv or the 15 Oct intake, and no catalogue gap query. Status is NOT IN GALLERY: the gallery was compiled 5 Oct, before this mod (workshop 3820576916) existed.
- **Licence:** Anduril press renders, videos and booth images are manufacturer marketing and not allowed without permission. Photos from TWZ, Breaking Defense and Defense News are copyrighted. If 3820576916 is not your own mod, get the author's permission before publishing a screenshot of their model.

### `usaf_rq-180` - RQ-180 “White Bat” - *no real photo can exist*

- **Where:** 1 mission(s), player
- **Find:** No real photo of this configuration can exist. The real RQ-180 itself is known only from distant, copyrighted spotter shots: 2020 north of Edwards, and Oct 2021 at Groom Lake (Joerg Arnu / Dreamland Resort). Wrong: any B-21, B-2, RQ-170 or X-47B photo presented as the RQ-180.
- **If not found:** Best: an in-game screenshot taken with the mod author's permission (mod 3796113927), captioned 'in-game model: fictional carrier UCAV derived from the unacknowledged RQ-180'. If a photo is wanted, use a US Navy public-domain X-47B photo, clearly captioned 'Context: Northrop Grumman X-47B carrier demonstrator, not the RQ-180'.
- **Leads:** In-game, Workshop mod 3796113927: A screenshot the user takes, after asking the mod author's permission [Needs author permission (the model is a third-party Sketchfab asset; SOURCE_LICENSE.txt is not in the repo copy)]; navy.mil / dvidshub.net (context image only): "X-47B" carrier, e.g. USS George H.W. Bush 2013 trap or launch: the real Northrop Grumman carrier-tested unmanned flying wing [Public domain (US Navy)]
- **Already tried:** 14 Oct master and curated_sources: usaf_rq-180, HOLD, concept_reference ('Public real photography unverified'). Nothing in the 15 Oct intake or photo_subject_gaps. The catalogue shows photo_gap.
- **Licence:** The 2020/2021 sighting photos (TWZ, The Aviationist, Dreamland Resort, Aviation Week) are copyrighted. Northrop Grumman concept art and Sketchfab renders need permission. The mod's own CREDITS limit it to non-commercial modding, so ask before shipping a screenshot on Steam. No AI images.

### `wp_ka-27` - Ka-27PL Helix-A (base game)

- **Where:** 1 mission(s), opponent; sold in sest-southern-reach; sest-southern-reach-open
- **Find:** Russian/Soviet Ka-27PL ASW helicopter
- **Leads:** Commons "Category:Kamov Ka-27"; mil.ru [CC BY 4.0 (mil.ru) or per file]

### `wp_mig-23a` - MiG-23 (base game "MiG-23A")

- **Where:** 1 mission(s), opponent
- **Find:** Soviet/Warsaw Pact MiG-23 early variant
- **Leads:** Commons "Category:Mikoyan-Gurevich MiG-23" [check per file]

### `wp_tu-95rt` - Tu-95RT Bear-D (base game)

- **Where:** 1 mission(s), opponent; sold in sest-southern-reach; sest-southern-reach-open
- **Find:** Tu-95RT Bear-D reconnaissance, intercept photos 1960s-80s
- **Leads:** Commons "Category:Tupolev Tu-95RT"; US Navy archive intercept photos [Public domain (US Navy)]

### `ae_ffg_bonifaz` - Bonifaz-class

- **Where:** 0 mission(s); sold in sest-southern-reach-open; sest-southern-watch-open
- **Find:** The lead ship F-111 Bonifaz (Spanish Navy F110 class), from the 11 Sep 2025 launch at Ferrol or later fitting-out or trials: a long flush-decked hull with one large integrated mast carrying flat SPY-7 array faces, a hangar aft, pennant F-111. Wrong photos: Navantia or Lockheed Martin CGI renders (the 15 Oct reject); trade-show scale models (only usable if labelled 'model'); Alvaro de Bazan F100 frigates F101-F105 (SPY-1D on the deckhouse, different mast); Hobart or Nansen class (F100 derivatives, wrong operator). Searches for 'F110' or 'F-111' also return the GE F110 engine and the F-111 Aardvark aircraft.
- **If not found:** A Moncloa launch photo of the real hull, labelled 'F-111 Bonifaz at her launch, Ferrol, Sep 2025 (fitting out)'. Otherwise a user-taken in-game screenshot labelled as the in-game model. An F100 Alvaro de Bazan photo only works as 'predecessor class, context only' and is weak.
- **Leads:** Wikimedia Commons: Category:Bonifaz (F-111) (6 launch photos, 11 Sep 2025, Pool Moncloa / Borja Puig de la Bellacasa) [Moncloa legal notice (reuse and modification allowed with credit 'Ministry of the President. Government of Spain'); licence review on Commons still pending] (seen); Wikimedia Commons: File:Botadura fragata F111 Bonifaz 01.jpg [Moncloa attribution terms (confirm on the file page)] (seen); Wikimedia Commons: Category:F110 class frigates (mostly photos of a scale model at the Lockheed Martin booth, JA2024 Tokyo) [per file, own-work uploads; model photos only] (seen); lamoncloa.gob.es photo gallery: Botadura fragata F-111 Bonifaz, 11 septiembre 2025 [Moncloa legal notice, attribution]
- **Already tried:** 14 Oct master (row 80) and curated_sources.tsv queued Category:F110 class frigates as concept_reference, noted 'May be a planned hull/model; real ship not assured'. The 15 Oct intake rejected asset 'bonifaz' as 'a render'. Not in catalogue photo_subject_gaps. The existing ui profile (existing-profiles.tsv) is the mod author's render, not a photo.
- **Licence:** The Moncloa images are not CC. Commons applies Moncloa legal-notice attribution terms and the files have not been licence-reviewed yet, so confirm on each file page and credit the Ministry of the Presidency / Pool Moncloa photographer. Do not use Navantia press images (manufacturer) or Lockheed Martin renders.

### `ae_lpd_galicia` - Galicia_L50-class L50

- **Where:** 0 mission(s); sold in sest-southern-reach-open; sest-southern-watch-open
- **Find:** Galicia (L-51) or Castilla (L-52) in Spanish Navy service, 1998 onward, ideally 2010s or later: a 160 m LPD with a large boxy superstructure forward, flight deck aft and stern dock, pennant L-51 or L-52. Castilla has the larger command superstructure. Wrong photos: the Cold War 'Galicia (L31)', ex-US LSD (that is the separate unit ae_lsd_galicia); the Cold War 'Castilla (L20/L21)' attack transport (ae_lpa_castilla); Dutch Rotterdam-class L800 (same design, wrong operator); the civil ferry Galicia (ship, 2003); Juan Carlos I (L61).
- **If not found:** None is needed. Either sister is an exact class photo, so a Castilla (L52) photo is fine for the class entry.
- **Leads:** Wikimedia Commons: Category:Galicia class landing platform dock (subcats Galicia (L-51) and Castilla (L-52)) [mixed; check each file] (seen); Wikimedia Commons: File:Buque de Asalto Anfibio Clase Galicia (L-51) Spanish Navy (6784578215).jpg [CC BY 2.0 (Flickr; uploader later stopped offering it, but the licence cannot be revoked)] (seen); Wikimedia Commons: File:Galicia delivering humanitarian supplies to Iraq.jpg (2003) [Public domain (PD-USGov-Military)] (seen); Wikimedia Commons: File:Ship LPD-Castilla-(L52)-01.jpg ; File:Castilla y Galicia.JPG (both ships at Rota, 2008) [own work, check each] (seen)
- **Already tried:** 14 Oct master (row 84) and curated_sources.tsv queued a Commons search 'Spanish Navy L50 Galicia amphibious ship' (exact_class_photo; licence not checked). There is no decision on it in the 15 Oct intake. catalogue photo_subject_gaps has 'Galicia class LPD' (asset galicia), query intitle:"Galicia" L51: no photo passed compilation.
- **Licence:** Avoid Armada Espanola and Navantia website images unless the specific file carries a free licence. The Flickr CC BY 2.0 file needs credit to the Flickr author.

### `ger_ffg_f124_mlu` - F124 Sachsen-class MLU - *no real photo can exist*

- **Where:** 0 mission(s); sold in sest-southern-reach-open; sest-southern-watch-open
- **Find:** Any of F219 Sachsen, F220 Hamburg or F221 Hessen (German Navy), with the whole ship identifiable, preferably 2020s. Recognition: APAR panels on the forward mast and the big SMART-L on the aft mast. No photo of the modelled MLU fit can exist, and the visible differences (NSM canisters, 30 mm guns) are small. Wrong photos: group shots where the F124 cannot be picked out (the 15 Oct reject); Dutch De Zeven Provincien class and Danish Iver Huitfeldt class (also APAR + SMART-L, easily confused, wrong operator); F123 Brandenburg; F125 Baden-Wuerttemberg. A photo showing a rotating TRS-4D instead of SMART-L is the real post-upgrade ship and differs from the mod's model.
- **If not found:** Reuse the existing gallery asset 'sachsen' (images/ships/sachsen.jpg, already credited), labelled 'Sachsen-class (F124), pre-upgrade configuration: family reference'. This needs no new research. A recent DVIDS photo of Sachsen or Hamburg from 2026 would be the better upgrade.
- **Leads:** Wikimedia Commons: Category:Sachsen class ; Category:F219 Sachsen (ship, 2004) ; Category:F220 Hamburg (ship, 2004) ; Category:F221 Hessen (ship, 2006) [mixed CC BY-SA / PD; check each file] (seen); DVIDS: https://www.dvidshub.net/image/9766060/fgs-sachsen-departs-fleetex-250 (June 2026) [Public domain (US Navy)] (seen); DVIDS: https://www.dvidshub.net/image/9778582/uss-mount-whitney-fgs-hamburg-sail-baltic-sea (June 2026) [Public domain (US Navy)] (seen); DVIDS: https://www.dvidshub.net/image/4527066/straits-transit (FGS Hessen with Truman CSG, 2018) [Public domain (US Navy)] (seen)
- **Already tried:** 14 Oct master (row 82) and curated_sources.tsv queued Category:Sachsen class as family_reference, noted 'MLU variant not visual-proof'. The 15 Oct intake rejected asset 'f124': 'the F124 cannot be picked out of the group'. Not in photo_subject_gaps. The base unit ger_ffg_f124 is already mapped to images/ships/sachsen.jpg (File:F219 Fregatte SACHSEN - geograph.org.uk - 5092439.jpg) as a family reference.
- **Licence:** geograph.org.uk images are CC BY-SA 2.0 and need credit. Bundeswehr website images marked (c) Bundeswehr are not free; use only CC-licensed Flickr or Commons copies.

### `ita_fs_ppx` - Vivaldi Class

- **Where:** 0 mission(s); sold in sest-southern-reach-open; sest-southern-watch-open
- **Find:** P440 Ugolino Vivaldi, from the Feb 2026 launch or the trials: a 95 m grey OPV with a 76 mm gun forward, an integrated mast, and a flight deck and hangar aft. Wrong photos: the WWII destroyer Ugolino Vivaldi of the Navigatori class (e.g. File:Nave vivaldi.jpg); File:PPX Marina Militare Italiana.jpg in the same category, which is probably a render (check); Thaon di Revel PPA class (143 m); Comandanti class OPVs (P490 series); Fincantieri marketing renders.
- **If not found:** The CC0 launch photo, labelled 'P440 Ugolino Vivaldi at her launch, Riva Trigoso, Feb 2026 (before completion)'.
- **Leads:** Wikimedia Commons: Category:Vivaldi class patrol boat (2 files) [per file] (seen); Wikimedia Commons: File:Varo di nave Ugolino Vivaldi (P440).jpg (launch at Riva Trigoso, 21 Feb 2026, author FabioskyStifler) [CC0 (own work)] (seen); marina.difesa.it / Marina Militare social and Flickr: Nave Ugolino Vivaldi prove in mare Golfo della Spezia ottobre 2026 [check; Italian MoD content may be NC or all rights reserved]
- **Already tried:** 14 Oct master (row 93) and curated_sources.tsv put it on HOLD as concept_reference: 'PPX Vivaldi actual configuration uncertain'. Nothing was queued, it is not in the 15 Oct intake and not in photo_subject_gaps. The hold is out of date: the ship is real, launched and on trials.
- **Licence:** The CC0 launch photo is safe. Do not use Fincantieri or Leonardo press images (manufacturer). Check Marina Militare images individually; do not assume they are free.

### `ko_ffg-828` - Chungnam Class

- **Where:** 0 mission(s); sold in sest-southern-reach-open; sest-southern-watch-open
- **Find:** ROKS Chungnam (FFG-828) or a later sister such as ROKS Gyeongbuk (FFG-829), 2023 onward: an integrated mast with four fixed flat AESA faces, the Korean CIWS-II on the hangar roof, and a 127 mm gun forward. Wrong photos: File:Ulsan Class FFX-Batch-III.jpg (a render, the 15 Oct reject); ROKS Chungnam (FF-953), an old Ulsan-class frigate with the same name; Daegu class FFG-818 to 825 (similar hull but a rotating radar and Phalanx); Incheon class FFG-811 to 816.
- **If not found:** No good family photo exists: the Daegu class (ko_ffg-818) also has no photo. Use a user-taken in-game screenshot labelled as the in-game model until a KOGL Type 1 or CC photo turns up.
- **Leads:** Wikimedia Commons: Category:Chungnam class frigates (currently holds only the render File:Ulsan Class FFX-Batch-III.jpg) [n/a] (seen); Flickr 'Republic of Korea Armed Forces' (대한민국 국군) photostream: 충남함 / FFG-828 commissioning Dec 2024, or 경북함 delivery June 2026 [usually CC BY-SA 2.0; check each]; Korea.net / navy.mil.kr (KOGL): 충남함 진수식 2023 / 취역 2024 [KOGL Type 1 (attribution) is usable; Types 2-4 are not]; DVIDS: search 'ROKS Chungnam' / 'FFG 828': nothing found 20 Oct (only Daegu-class hits) [n/a] (seen)
- **Already tried:** 14 Oct master (row 81) and curated_sources.tsv queued Category:Chungnam class frigates as exact_class_photo. The 15 Oct intake rejected asset 'chungnam' as 'a render' (that category's only file). catalogue photo_subject_gaps has 'Chungnam class frigate', query intitle:"ROKS Chungnam" FFG.
- **Licence:** Korean news agency images (Yonhap, news sites) and HD Hyundai Heavy Industries / SK Oceanplant press photos are not usable. KOGL is usable only for Type 1.

### `phl_ff_hamilton` - Del Pilar-class

- **Where:** 0 mission(s); sold in sest-sulu-line; sest-sulu-line-open
- **Find:** BRP Gregorio del Pilar (PF/PS-15, ex-USCGC Hamilton WHEC-715), BRP Ramon Alcaraz (PF/PS-16, ex-Dallas WHEC-716) or BRP Andres Bonifacio (FF/PS-17, ex-Boutwell WHEC-719), in Philippine Navy grey, 2011 onward. Wrong photos: white-hulled USCG Hamilton-class cutters before transfer (wrong operator and livery); USCGC Hamilton (WMSL-753), the Legend-class cutter that shares the name; the newer PN frigates BRP Jose Rizal / Miguel Malvar; Knox-class frigates (the stand-in mesh).
- **If not found:** None is needed; several exact public-domain photos exist.
- **Leads:** Wikimedia Commons: Category:Gregorio del Pilar class frigate (subcats BRP Gregorio del Pilar (PF-15), BRP Ramon Alcaraz (PF-16), BRP Andres Bonifacio (FF-17)) [mixed; many PD US Navy] (seen); Wikimedia Commons: File:US Navy 110727-N-RI884-064 BRP Gregorio del Pilar (PF 15) arrives at Joint Base Pearl Harbor-Hickam during a scheduled port visit.jpg [Public domain (US Navy)] (seen); DVIDS: https://www.dvidshub.net/image/4512539/brp-andres-bonifacio-ff-17-enters-pearl-harbor-preparation-rimpac-2018 [Public domain (US Navy)] (seen); DVIDS: https://www.dvidshub.net/image/8562193/uss-mobile-conducts-maritime-cooperative-activity-with-brp-ramon-alcaraz (2024) [Public domain (US Navy)] (seen)
- **Already tried:** Nothing found: there is no entry in the 14 Oct master, curated_sources.tsv, the 15 Oct intake or photo_subject_gaps. The catalogue lists it as photo_gap.
- **Licence:** On DVIDS, check the credit line names a US service member or civilian, not a Philippine Navy handout. Avoid Philippine Navy Facebook images.

### `phl_fs_pohang` - Pohang-class

- **Where:** 0 mission(s); sold in sest-sulu-line; sest-sulu-line-open
- **Find:** BRP Conrado Yap (PS-39 / PS-30) in Philippine Navy service, 2019 onward: an 88 m Pohang-class corvette with 76 mm guns fore and aft and twin 40 mm mounts. Wrong photos: Bayandor/Tapi PF-103 corvettes (the in-game stand-in mesh); other Pohang-class ships in ROK Navy service (only acceptable as a labelled family photo); ROKS Cheonan; the older patrol craft BRP Conrado Yap (PG-840).
- **If not found:** A ROK Navy Pohang-class photo from Category:Pohang class corvette, labelled 'Pohang class in ROK Navy service (family)'. ROKS Chungju (PCC-762), the same hull before transfer, is ideal. This would also fill ko_pcc-756.
- **Leads:** Wikimedia Commons: Category:BRP Conrado Yap (PS-39) (7 files), parent Category:Pohang class corvette [mixed; check each] (seen); Wikimedia Commons: File:BRP Conrado Yap (PS-39).jpg (ship sailing to the Philippines, 2019) [PD-PhilippinesGov (Philippine Navy)] (seen); DVIDS: https://www.dvidshub.net/image/7745930/uss-chung-hoon-conducts-underway-training-with-brp-conrado-yap (Apr 2023, South China Sea) [Public domain (US Navy)] (seen); DVIDS: https://www.dvidshub.net/image/7745899/uss-chung-hoon-sailors-render-honors-brp-conrado-yap [Public domain (US Navy)] (seen)
- **Already tried:** Not in the 14 Oct master, curated_sources.tsv or the 15 Oct intake. catalogue photo_subject_gaps has 'Pohang class corvette' (asset 'pohang', shared with the Korean ko_pcc-756), query intitle:"Pohang" corvette: no photo passed compilation.
- **Licence:** PD-PhilippinesGov images are public domain in the Philippines, but RA 8293 s.176 requires prior approval for commercial exploitation. SEST is free, but prefer the public-domain DVIDS US Navy photos.

### `tha_aor_chula` - Chula-class

- **Where:** 0 mission(s); sold in sest-sulu-line; sest-sulu-line-open
- **Find:** HTMS Chula (831), Royal Thai Navy coastal oiler (1981 build), with hull number 831 visible. Wrong photos: the WWII-era Thai tankers Chula and Matra (1940s; shipscribe photos from 1970); HTMS Similan (871), a large Chinese-built AOR; HTMS Phutthayotfa Chulalok and Chulachomklao Fort (name collisions); Iranian Delvar-class ships (the in-game stand-in mesh).
- **If not found:** No honest family photo exists for a single-ship class. Leave it as no-photo, or use a user-taken in-game screenshot labelled 'in-game model (stand-in Delvar-class mesh), not HTMS Chula'.
- **Leads:** Wikimedia Commons: search 'HTMS Chula' / Category:Royal Thai Navy: no Chula (831) photo found on 20 Oct [n/a] (seen); DVIDS: search 'HTMS Chula' / '831': nothing found on 20 Oct [n/a] (seen); Flickr (licence filter: commercial use and mods allowed): "HTMS Chula" OR "เรือหลวงจุฬา" OR "Chula 831" Sattahip [CC BY / CC BY-SA if found]
- **Already tried:** Nothing found: there is no entry in the 14 Oct master, curated_sources.tsv, the 15 Oct intake or photo_subject_gaps. The catalogue lists it as photo_gap.
- **Licence:** Royal Thai Navy (navy.mi.th) and Thai press photos are copyrighted; do not use them without permission. Ship-spotter sites such as ShipSpotting and MarineTraffic are all rights reserved.

### `tha_s-70b-7_seahawk` - S-70B-7

- **Where:** 0 mission(s); sold in sest-sulu-line; sest-sulu-line-open
- **Find:** A Royal Thai Navy S-70B-7 Seahawk: the 302 Squadron ASW Seahawk that flies from Thai frigates and HTMS Chakri Naruebet, in RTN markings, 1997 or later. Reported side numbers are in the 32xx range (3202 = 70-2297, 3204 = 70-2374), so check the number on the aircraft. Wrong subjects: the RTN's plain S-70B of 203 Squadron (SAR/VIP), RTN MH-60S, US Navy SH-60B or MH-60R, the Australian S-70B-2, and any Thai Army or Air Force UH-60/S-70A Black Hawk.
- **If not found:** Reuse the existing gallery asset s70b2 (images/aircraft/s70b2_commons.jpg: an RAN Seahawk, Chris Phutully, CC BY 2.0), captioned 'Sikorsky S-70B Seahawk family (Australian S-70B-2 shown), not a Royal Thai Navy aircraft'.
- **Leads:** clwp.navy.mil (US Navy Pacific Partnership gallery) igphoto 2002148969: Thai S-70B getting ready to launch from USS Antietam (CG 54), CARAT Thailand, 6 June 2019, VIRIN 190606-N-QD718-0312, MC1 Toni Burton. Check the side number to confirm it is a 302 Sqn S-70B-7. [Public domain (US Navy)] (seen); allhands.navy.mil Media/Gallery igphoto 2002354439 (sibling IDs 2002354438, 2002354400, 2002354397, 2002354435): Same CARAT Thailand 2019 shoot: Thai and US sailors doing deck-landing qualifications with the Thai S-70B (VIRIN 190606-N-QD718-0323) [Public domain (US Navy)] (seen); dvidshub.net: "CARAT Thailand" helicopter / "Royal Thai Navy" Seahawk / "Guardian Sea" / "Cobra Gold" Thai Navy helicopter (a 2009 CARAT photo captions an RTN 'SH-60 Seahawk') [Public domain (US military)]; Wikimedia Commons search: "Royal Thai Navy" Seahawk OR "S-70B" Thailand (searches found no Thai Seahawk category; Commons only returned Harrier and Chakri Naruebet files) [Check each file (US Navy PD or CC BY/BY-SA)]
- **Already tried:** No row for this unit id in SEST_IMAGE_MASTER_20261014.csv or curated_sources.tsv, none in the 15 Oct intake, none in photo_subject_gaps. The catalogue shows mapping_status photo_gap with an empty asset_id. Related: the S-70B-2_Seahawk row (Category:S-70B-2 Seahawk in service with Australia) produced the approved s70b2 asset (15 Oct: same_family, 'Seahawk with a swimmer; the exact operator is not visible').
- **Licence:** Not usable: JetPhotos, airliners.net and helis.com photos, and Royal Thai Navy website or Facebook images (all rights reserved, no free licence). Thai government images are not public domain. Use only US Navy/DVIDS frames of RTN Seahawks or files under a genuine CC licence.


## Already in the gallery, not shown in briefings (54) - my fix

SEST now ships its own copy of these units (a fix or a fork), and the gallery's photo is attached to the original mod's copy, so `build_pack.recognition` skips it. The fix is to carry the photo across to the copy the game loads; it waits for GPT's work to be merged because it touches `build_pack.py`.

- `usn_p8` (35 missions): photo p8a
- `plan_type_054a_p5` (25 missions): photo type054a
- `plan_type_056a` (14 missions): photo type056a
- `civ_ms_sealift_pacific` (7 missions): photo tanker
- `usn_ea-18g` (5 missions): photo ea18g
- `usn_fa-18f_blk3` (3 missions): photo fa18f
- `dts_b-52h` (2 missions): photo b52h
- `jmsdf_ddg_maya` (2 missions): photo maya
- `js_ffg_mogami` (2 missions): photo mogami
- `ko_ddg-991` (2 missions): photo sejong
- `ae_lhd_juan_carlos` (1 missions): photo juan_carlos
- `fr_rafale_m_l` (1 missions): photo rafale_m
- `ger_ffg_f124` (1 missions): photo sachsen
- `hdms_iver_huitfeldt` (1 missions): photo huitfeldt
- `ita_ffg_fremm_asw` (1 missions): photo bergamini_modern
- `jmsdf_dd_asahi` (1 missions): photo asahi
- `rfn_cvt_20380_7-12` (1 missions): photo steregushchiy
- `rn_ddg_type45` (1 missions): photo type45
- `rnn_ffg_karel_mlu` (1 missions): photo karel_doorman
- `ru_cv_kuznetsov` (1 missions): photo kuznetsov
- `usa_a-10c` (1 missions): photo a10c
- `usa_ah-64d` (1 missions): photo ah64d
- `usa_ah-64e` (1 missions): photo ah64e
- `usaf_b-1b_dts` (1 missions): photo b1b
- `usaf_b-52o` (1 missions): photo b52h
- `usaf_f-16cm-bl52d` (1 missions): photo f16c
- `usaf_mq-9a` (1 missions): photo mq9
- `usn_cvn_ford` (1 missions): photo ford
- `usn_cvn_ford_jsf` (1 missions): photo ford
- `usn_cvn_nimitz_2025` (1 missions): photo nimitz
- `usn_ea-18g_2020` (1 missions): photo ea18g
- `usn_f-35c` (1 missions): photo f35c
- `usn_ssn_virginia` (1 missions): photo virginia_ssn
- `ae_ffg_alvaro_bazan` (0 missions): photo bazan
- `ae_opv_meteoro` (0 missions): photo meteoro
- `fr_rafale_b_l` (0 missions): photo rafale_b
- `ger_ffg_f123_2025_mlu` (0 missions): photo brandenburg
- `ita_ddg_orizzonte_18` (0 missions): photo doria_modern
- `ita_ffg_fremm` (0 missions): photo bergamini_modern
- `ita_ffg_ppa` (0 missions): photo ppa
- `jmsdf_ddg_atago` (0 missions): photo atago
- `knm_cor_skjold` (0 missions): photo skjold
- `ko_ddg-995` (0 missions): photo jeongjo
- `ko_ddh-971` (0 missions): photo gwanggaeto
- `ko_ddh-975_kvls` (0 missions): photo chungmugong
- `rn_ddg_type45_26` (0 missions): photo type45
- `rn_ff_type23` (0 missions): photo type23
- `rn_opv_river_batch2` (0 missions): photo river
- `rnn_ddg_zeven_mlu` (0 missions): photo zeven
- `rnn_ffg_karel_eol` (0 missions): photo karel_doorman
- `usaf_mq-9_er` (0 missions): photo mq9
- `usn_cvn_gerald_r_ford` (0 missions): photo ford
- `usn_fa-18e` (0 missions): photo fa18e
- `usn_lhd_wasp` (0 missions): photo wasp
