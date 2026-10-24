# Combat costs: not yet confirmed (24 Oct 2026)

Historical research snapshot. The owner's subsequent request authorizes estimates for complete coverage. All 381 rows (377 unique references) now have prices in `cost-list.csv`, from preserved checked research or labelled SEST models. That does not confirm the original candidate figures. The research decisions below remain unchanged; see `backlog-resolution.md` for the installed-price crosswalk.

381 weapons, land units, ships and aircraft that SEST's campaigns field or carry, with no checked price yet. "Candidate" is the researcher's figure in USD (service-entry price / 2026 price) where one was found. It ships only once a second agent confirms the source. "Not researched" and "not confirmed" mean the session's web-search allowance (200 per turn, shared by all agents) ran out or the source sites were blocked by the environment's network policy - not that the item cannot be priced.

| Group | Items | With a candidate figure |
|---|---:|---:|
| Missiles | 9 | 1 |
| Torpedoes | 25 | 12 |
| Bombs and depth charges | 27 | 20 |
| Rockets, guns and launchers | 23 | 0 |
| Sonobuoys, chaff, flares, noisemakers and decoys | 58 | 0 |
| Fuel tanks, rocket pods and gun pods | 102 | 0 |
| Land vehicles and systems | 50 | 10 |
| Land installations | 39 | 5 |
| Ships (second attempt) | 21 | 0 |
| Aircraft and SEST weapons (second attempt) | 27 | 0 |
| **Total** | **381** | **48** |

| Why | Items |
|---|---:|
| not researched | 293 |
| no source found | 40 |
| found, not confirmed | 37 |
| refuted | 11 |

## Missiles (9)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `jp_aam-3` | Mitsubishi AAM-3 (Type 90), a short-range IR AAM, 1991 per the config header, on the JASDF F-2A late (owner 3755769170). |  | not researched: no web searches left / sites blocked |
| `jp_aam-4` | Mitsubishi AAM-4 (Type 99), an active-radar medium-range AAM, 1999 per the config header, on the JASDF F-2A late (owner 375576917… |  | not researched: no web searches left / sites blocked |
| `jp_asm-3` | Mitsubishi ASM-3, a supersonic ramjet anti-ship missile (940 kg, 161 nm in the config), on the JASDF F-2A late (owner 3755769170). |  | not researched: no web searches left / sites blocked |
| `pla_akd-10-z21` | AKD-10 (Blue Arrow 7), a 45 kg semi-active-laser HEAT helicopter ATGM on the PLA Z-21 (owner 3774746803); uses the Z-21 source's … |  | not researched: no web searches left / sites blocked |
| `pla_akk-90a-z21` | AKK-90A / TY-90A (Tianyan-90A), a helicopter-launched short-range IR AAM on the PLA Z-21 (owner 3774746803). |  | no source found: Config: '# AKK-90A / Tianyan-90A', an 84 kg IR AAM; the English name confirms it. A catalog grep for TY-90, Tianyan or … |
| `sest_aim-424` | SEST's AIM-424 MALICE long-range AAM (680 kg). Its flight model is aligned with usn_aim-174b. It is fitted to the RAAF F-35A, F-3… |  | not researched: no web searches left / sites blocked |
| `usn_aim-424` | AIM-424 Malice LRAAM, 680 kg (mod 3606774881, US Navy 2027), carried by usn_f-35c and F/A-18E/F; a tracker catalog id whose autho… |  | not researched: no web searches left / sites blocked |
| `usn_steelfin_air` | Air-launched store of Anduril's Steelfin interceptor family (unveiled 12 Oct 2026 at AUSA, flight tests planned 2027, no orders);… | $2,340,000 / $2,340,000 | found, not confirmed: no web searches left / sites blocked |
| `yf23_aim424_internal` | AIM-424 Malice for the YF-23's internal bay, 680.4 kg; name text says 'Imagined YF-23 integration' (mod 3796349767). |  | not researched: no web searches left / sites blocked |

## Torpedoes (25)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `eu_mu_90_ship` | MU90 Impact, a Franco-Italian EuroTorp 324 mm third-generation lightweight ASW torpedo, ship-launched (Euromod 3629144864; 304 kg… | $1,990,000 / $3,050,000 | found, not confirmed: no web searches left / sites blocked |
| `fr_a244s_mod1` | A244/S Mod 1, Whitehead (Italy) 324 mm lightweight ASW torpedo, 230 kg, air-dropped (French pack 3567228449). Carried by fr_as-56… |  | not researched: no web searches left / sites blocked |
| `fr_canto` | CANTO, Naval Group's expendable anti-torpedo acoustic decoy. The game treats it as Type=Torpedo with WarheadType=-1 and GuidanceT… |  | not researched: no web searches left / sites blocked |
| `fr_e15` | E15, a 1950s-60s French 550 mm passive-homing anti-surface heavyweight torpedo (vanilla; FOCDate 1960; 1650 kg; AirLaunched). In … |  | no source found: Identity confirmed: vanilla fr_e15.ini, FOCDate=1960, Mass=1650, AirLaunched. 3417801942 plan_z-18f.ini lines 266-267 a… |
| `fr_mu_90_air` | MU90 Impact, air-dropped. The file is '#!alias ammunition/eu_mu_90_air.ini' (Euromod 3629144864; eu_mu_90_air is 314.1 kg, AirLau… | $1,990,000 / $3,050,000 | found, not confirmed: no web searches left / sites blocked |
| `fr_mu_90_ship` | MU90 Impact, ship-launched (French pack 3567256221; FOCDate 2004). Carried by fr_ddg_horizon and fr_ffg_aquitaine_asw. | $1,990,000 / $3,050,000 | found, not confirmed: no web searches left / sites blocked |
| `ger_mu_90_ship` | MU90 Impact, ship-launched. The file is '#!alias ammunition/eu_mu_90_ship.ini' (Euromod 3629144864). Carried by hdms_iver_huitfel… | $1,990,000 / $3,050,000 | found, not confirmed: no web searches left / sites blocked |
| `it_canto` | CANTO anti-torpedo decoy, Italian copy. Its config is byte-identical to fr_canto (diff empty) and it has no English name entry. O… |  | no source found: diff of 3629144864/ammunition/fr_canto.ini and it_canto.ini is empty (byte-identical). Same reasoning as fr_canto; cate… |
| `mm_mu_90_ship` | MU90 Impact, ship-launched. The file is '#!alias ammunition/eu_mu_90_ship.ini' (Euromod 3629144864). Carried by ita_ddg_orizzonte… | $1,990,000 / $3,050,000 | found, not confirmed: no web searches left / sites blocked |
| `plan_yu-12_air` | Yu-12, China's latest 324 mm lightweight ASW torpedo (thermal pump-jet, active/passive seeker, 242 kg), air-dropped, 3775128499. … | $1,990,000 / $3,050,000 | refuted: The model estimate copies the MU90 pair, whose only source (Senate search excerpts) could not be re-verified in this ch… |
| `plan_yu-12_ship` | Yu-12 324 mm lightweight ASW torpedo, ship-launched, 3775128499. Carried by plan_type_052d_p3. | $1,990,000 / $3,050,000 | refuted: Same as plan_yu-12_air: the donor MU90 figure is unverifiable in this check. Re-queue with eu_mu_90_ship. |
| `plan_yu-12a` | Yu-12A, the anti-torpedo-capable (ATT) variant of the Yu-12 324 mm lightweight torpedo, 3775128499. Carried by plan_cv_type_003. | $1,990,000 / $3,050,000 | refuted: Same as plan_yu-12_air: the donor MU90 figure is unverifiable in this check. Re-queue with eu_mu_90_ship. |
| `plan_yu-5` | Yu-5, an older Chinese 533 mm wire-guided ASW heavyweight torpedo ('improves on the YU-3'), owner 3417801942. It reuses the wp_te… | $1,680,000 / $4,220,000 | refuted: Two problems. (1) The historical figure rests on the unverifiable GAO search excerpt. (2) The comparison does not hold.… |
| `plan_yu-7_air` | Yu-7, a 324 mm lightweight ASW torpedo, air-dropped (3775128499, 230 kg). The names files call it a licence derivative of the Mk … |  | no source found: Identity confirmed. The 3775128499 names file describes licensed production of the Mk46 Mod 2 under a 1985 agreement, a… |
| `plan_yu-7_ship` | Yu-7 324 mm lightweight ASW torpedo, ship-launched (3775128499). A Mk 46 Mod 2 licence derivative. Carried by plan_ddg_luda_typ_0… |  | no source found: Same as plan_yu-7_air; identity confirmed in 3775128499 names file. |
| `plan_yu-7c_ship` | Yu-7C, an improved Yu-7 lightweight torpedo that the names file rates 'roughly equivalent to the Mk46 Mod 5(SW)', ship-launched (… |  | no source found: Identity confirmed: 3775128499 names file, 'improved variant featuring enhanced propulsion efficiency and upgraded homi… |
| `rfn_m15at` | M15 anti-torpedo of the Russian Paket-NK system: 324 mm, about 100-800 m range, 385 kg in the config (3597650470). Carried by rfn… |  | no source found: Identity confirmed: 3597650470 names file 'M15 antitorpedo from Paket NK'; config Mass=385, GuidanceType=7. The Nationa… |
| `rfn_mtt` | MTT, the small-size thermal 324 mm lightweight ASW torpedo of the Russian Paket-NK system (3597650470). Its names file says 'Ligh… | $1,990,000 / $3,050,000 | found, not confirmed: no web searches left / sites blocked |
| `rn_stingray_air` | Sting Ray Mod 0, the Royal Navy's 324 mm air-dropped lightweight ASW torpedo (Euromod 3629144864, 267 kg; in service from about 1… |  | not researched: no web searches left / sites blocked |
| `usa_v280_copperhead_100m` | Anduril Copperhead-100M: an autonomous 324 mm undersea munition (torpedo-like UUV), air-dropped with a parachute from the MV-75 (… |  | no source found: Identity: 3810611344 config is the air-dropped Copperhead-100M from the MV-75, IOCDate 2025, FOCDate 2026; its weight a… |
| `wp_53-65K` | 53-65K Soviet 533 mm wake-homing anti-ship torpedo (IOCDate 1969, FOCDate 1972; 2,200 kg in game). On PLAN Kilo and the disguised… | ? / $2,010,000 | found, not confirmed: no web searches left / sites blocked |
| `wp_65-76` | 65-76 'Kit' Soviet 650 mm heavyweight anti-ship wake-homing torpedo (1970s-80s). On Akula (wp_ssn_akula). |  | not researched: no web searches left / sites blocked |
| `wp_at-2` | AT-2M Soviet 533 mm air-dropped ASW torpedo (1960s-70s; 980 kg in game). On Tu-142M. |  | not researched: no web searches left / sites blocked |
| `wp_set-65` | SET-65 Soviet 533 mm electric ASW torpedo (1960s; 1,740 kg in game). On Sovremenny (PLAN), 11356, Udaloy, Kirov. | ? / $2,010,000 | found, not confirmed: no web searches left / sites blocked |
| `wp_umgt-1` | UMGT-1 (Orlan) Soviet/Russian 400 mm air-dropped ASW torpedo (720 kg in game). On Ka-27 and PLAN Ka-28. |  | no source found: Identity: vanilla config 'UMGT-1', 720 kg, air-launched ASW (the config notes it is currently a copy of the Mk 46 air e… |

## Bombs and depth charges (27)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `am_kb44` | KB 44 anti-armour bomblet from the West German MW-1 dispenser on the Tornado IDS (Euromod 3629144864, carried by am_tornado_ids f… |  | not researched: no web searches left / sites blocked |
| `am_stabo` | STABO runway-cratering bomblet from the West German MW-1 dispenser on the Tornado IDS (Euromod 3629144864, carried by am_tornado_… |  | not researched: no web searches left / sites blocked |
| `b-2_gbu-57` | GBU-57A/B Massive Ordnance Penetrator, the 30,000 lb GPS-guided penetrator bomb carried by usaf_b-2_spirit (3480965706). The file… | $3,500,000 / $5,200,000 | found, not confirmed: no web searches left / sites blocked |
| `dts_b-61` | B61 nuclear gravity bomb (dts 3760871384; its header comment was copied from the GBU-32 file). Carried by dts_b-52h and by SEST's… | $24,000,000 / $24,000,000 | found, not confirmed: no web searches left / sites blocked |
| `fr_samp_t25` | SAMP Type 25, a French 250 kg (230 kg in the file) unguided general-purpose bomb (vanilla; carried by fr_rafale_m). The vanilla d… | $500 / $1,200 | found, not confirmed: no web searches left / sites blocked |
| `pla_type-3-250` | Chinese Type-250-3 250 kg (227 kg in the file) unguided general-purpose bomb (vanilla; carried by plaaf_h-6k_late). The vanilla d… | $500 / $1,200 | found, not confirmed: no web searches left / sites blocked |
| `plaaf_250-Ⅲ` | Chinese 250-III, a 250 kg Type III low-drag unguided bomb (3436170138; Mass=250). Carried by plaaf_j-8f and plaaf_jh7a. | $500 / $1,200 | found, not confirmed: no web searches left / sites blocked |
| `plaaf_500-Ⅱ` | Chinese 500-II, a 500 kg Type II high-drag unguided bomb (3812111085; Mass=500, header comment '#FAB-500-M62'). Carried by plaaf_… | $1,000 / $2,500 | found, not confirmed: no web searches left / sites blocked |
| `plaaf_500-Ⅲ` | Chinese 500-III, a 500 kg Type III low-drag unguided bomb (3436170138; Mass=500). Carried by plaaf_j-11bg and plaaf_j-8f. | $1,000 / $2,500 | found, not confirmed: no web searches left / sites blocked |
| `plaaf_gb-1000` | Chinese GB-1000, a 1,000 kg free-fall laser-guided bomb (3812111085; Mass=950, GuidanceType=5). Carried by plaaf_j16. | $22,000 / $54,000 | found, not confirmed: no web searches left / sites blocked |
| `plan_ksb-2_dc` | 'KSB-2', a fictional designation for a 115 kg free-fall aerial depth charge (Type=AirDepthCharge) on the PLAN Y-9FQ (3775128499).… |  | no source found: Identity checked. The file (3775128499, identical in 3637954857) has the header '#USN Mark 54 depth bomb', Type=AirDept… |
| `usaf_cbu-24` | CBU-24 cluster bomb (SUU-30 dispenser, 665 BLU-26 fragmentation bomblets), USAF Vietnam-era anti-personnel/SAM-site weapon; vanil… |  | not researched: no web searches left / sites blocked |
| `usaf_m117` | M117 750-lb (340 kg) general-purpose bomb, Korean War vintage, used by B-52s in Vietnam; vanilla, FOCDate 1950; carried by usaf_b… | $620 / $5,600 | found, not confirmed: no web searches left / sites blocked |
| `usn_gbu-10` | GBU-10 Paveway II laser-guided 2,000-lb bomb (Mk 84 + Paveway II kit), vanilla, FOCDate 1977; carried by A-10C, A-10C+, B-2, F-11… | $4,700 / $28,000 | found, not confirmed: no web searches left / sites blocked |
| `usn_gbu-16` | GBU-16 Paveway II laser-guided 1,000-lb bomb (Mk 83 + Paveway II kit), vanilla, FOCDate 1977; carried by jp_f-2a_late, mm_av-8b_p… | $4,200 / $25,000 | refuted: There is no source for the GBU-16 itself. The value is the midpoint between the shipped GBU-12D and the GBU-10 ratio mo… |
| `usn_mk-82` | Mk 82 500-lb low-drag general-purpose bomb (241 kg), United States Naval Aviation mod 3737267013 (vanilla FOCDate 1960); carried … | $440 / $4,000 | found, not confirmed: no web searches left / sites blocked |
| `usn_mk-82_snakeye` | Mk 82 Snakeye: Mk 82 500-lb bomb with Mk 15 high-drag retarding fins (230 kg), vanilla, FOCDate 1960; carried by spa_av-8b_plus, … | $440 / $4,000 | refuted: This row copies the usn_mk-82 pair, which is refuted: the TWZ excerpt cannot be re-surfaced or read, its quote wording … |
| `usn_mk-83` | Mk 83 1,000-lb general-purpose bomb (459 kg), United States Naval Aviation mod 3737267013 (vanilla FOCDate 1960); carried by Torn… | $980 / $11,000 | found, not confirmed: no web searches left / sites blocked |
| `usn_mk-84` | Mk 84 2,000-lb general-purpose bomb (925 kg), United States Naval Aviation mod 3737267013 (vanilla FOCDate 1960); carried by B-52… | $1,700 / $16,000 | found, not confirmed: no web searches left / sites blocked |
| `usn_rockeye` | CBU-100 / Mk 20 Rockeye II anti-armour cluster bomb (247 bomblets, 222 kg), mod 3395022688 file (vanilla FOCDate 1968); carried b… |  | not researched: no web searches left / sites blocked |
| `wp_fab-1500_m54` | FAB-1500 M-54 Soviet 1,500 kg high-explosive bomb (1954 pattern), vanilla (no service date); carried by plaaf_h-6k_late | $2,800 / $26,000 | refuted: The donor (USAF FY2021 Mk 84 USD 16,000, TWZ search excerpt) and CPI 2021 cannot be re-verified, as explained under usn… |
| `wp_fab-250` | FAB-250 M-62 Soviet 250 kg high-explosive bomb (game mass 227 kg), vanilla (no service date); carried by Ka-28, Ka-27, Mi-8TV, Mi… | $410 / $3,800 | refuted: The donor Mk 82 USD 4,000 (TWZ excerpt) and CPI 2021 = 270.970 cannot be re-verified; see usn_mk-82. The 1960 donor yea… |
| `wp_fab-3000_m54` | FAB-3000 M-54 Soviet 3,000 kg high-explosive bomb (1954 pattern), vanilla (no service date); carried by plaaf_h-6k_late | $5,700 / $52,000 | refuted: The donor Mk 84 USD 16,000 (TWZ excerpt) and CPI 2021 cannot be re-verified; see usn_mk-84. The arithmetic is correct (… |
| `wp_fab-500` | FAB-500 M-62 Soviet 500 kg high-explosive bomb, vanilla (no service date); carried by Mi-8TV, MiG-23, MiG-29K, Su-25SM3, Su-33, T… | $910 / $8,300 | refuted: The donor Mk 82 USD 4,000 (TWZ excerpt) and CPI 2021 cannot be re-verified; see usn_mk-82. The arithmetic is correct (8… |
| `wp_plab-100` | PLAB-100 Soviet 100 kg anti-submarine depth bomb (Type=AirDepthCharge, 42 kg explosive), vanilla; carried by plan_ka-28, wp_ka-27 | $180 / $1,700 | refuted: The donor Mk 82 USD 4,000 (TWZ excerpt) and CPI 2021 cannot be re-verified; see usn_mk-82. Scaling a GP bomb price to a… |
| `wp_rbk-250` | RBK-250 Soviet 250 kg cluster bomb (game mass 273 kg), mod 3395022688 file; carried by plan_ka-28, wp_ka-27 |  | not researched: no web searches left / sites blocked |
| `wp_rn-40` | RN-40 nuclear gravity bomb (500 kg, Power=2000, nuclear explosion effects; file comment 'PLA KB-1 Nuke Bomb'), Su-30SM2 mod 37620… |  | no source found: The identity matches the file: Mass=500, Power=2000, display name RN-40, with a comment that names a PLA bomb instead. … |

## Rockets, guns and launchers (23)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `ir_107mm_rocket` | Haseb-1, the Iranian version of the Chinese Type 63 107 mm artillery rocket. Fired from the stock Boghammar and Peykaap-3 craft. … |  | not researched: no web searches left / sites blocked |
| `pla_airdrop_type63` | Cosmetic Type=Paratrooper load: the hull mesh of a Type 63 light tank on an extraction platform, dropped from the Y-20A cargo ram… |  | not researched: no web searches left / sites blocked |
| `pla_paratrooper` | Cosmetic Type=Paratrooper load: PLA airborne infantry dropped from the Y-20A cargo ramp (3782020901, plaaf_y-20a). Mass=120 kg (t… |  | not researched: no web searches left / sites blocked |
| `plaaf_90-Ⅰ_rocket` | Chinese 90-I (Type 90-1) 90 mm HEAT air-to-ground FFAR made by NORINCO. Shenyang J-11 mod (3436170138). Carried by plaaf_j-8f and… |  | not researched: no web searches left / sites blocked |
| `plan_fqf-2500` | FQF-2500 Chinese anti-submarine rocket (RBU) round. Its name file calls it a 213 mm launcher based on the Soviet RBU-2500; its co… |  | not researched: no web searches left / sites blocked |
| `plan_mss-01` | MSS-01 Chinese self-propelled, wire-guided submarine acoustic decoy. Modern PLAN Systems (3775128499). Carried by plan_ss_type_03… |  | not researched: no web searches left / sites blocked |
| `plan_mss-02` | MSS-02 Chinese 324 mm mobile acoustic decoy. Modern PLAN Systems (3775128499). Carried by plan_cv_type_003. Config Type=MOSS, Mas… |  | not researched: no web searches left / sites blocked |
| `plan_rbu2000` | FQF-2000 173 mm rocket depth charge from the RJZ-726-4 multifunction launcher (anti-submarine and anti-torpedo). Modern PLAN Syst… |  | not researched: no web searches left / sites blocked |
| `plan_rgb-81` | Type 81 rocket depth charge for the Chinese FQF-3200 system (H/WHH-003 launcher). Modern PLAN Systems (3775128499). Carried by pl… |  | not researched: no web searches left / sites blocked |
| `su_rgb-12` | RGB-12 anti-submarine rocket for the RBU-12000 launcher. Mod 3438479626. Carried by ru_cv_kuznetsov and plan_type_001. Config Typ… |  | not researched: no web searches left / sites blocked |
| `usn_hydra` | Stock Hydra 70 2.75 in folding-fin aircraft rocket, normally carried in pods of up to 19. Config Type=AerialRocket, Mass=11 kg, W… |  | not researched: no web searches left / sites blocked |
| `usn_moss` | Stock Mk 57 MOSS (Mobile Submarine Simulator), a 10 in submarine-launched decoy. Config FOCDate=1980, Mass=450 kg. Carried by the… |  | not researched: no web searches left / sites blocked |
| `usn_zuni` | Stock 5.0 in Zuni folding-fin aircraft rocket (config comment: 'Mk32 warhead + Mk16 motor'), usually fired from the 4-round LAU-1… |  | not researched: no web searches left / sites blocked |
| `wp_dc_shell` | Stock Soviet BB-1 depth charge, modelled as an RBU round. Config Type=RBU, Mass=165 kg. Carried by the Luda Type 051D/051DT. |  | not researched: no web searches left / sites blocked |
| `wp_grad` | Stock 122 mm M-21OF rocket for the BM-21 Grad MLRS. Config Type=MLRS, Mass=67 kg. The batch lists ran_ms_super_p as the carrier. |  | not researched: no web searches left / sites blocked |
| `wp_mg-44` | Stock MG-44 Korund self-propelled hydroacoustic submarine simulator, launched from 400 mm tubes. Config Type=MOSS, Mass=497 kg. C… |  | not researched: no web searches left / sites blocked |
| `wp_rgb-10` | Stock RGB-10 300 mm ASW rocket depth charge for the RBU-1000. Config Type=RBU, Mass=195 kg. Carried by plan_em_sovremenny and wp_… |  | not researched: no web searches left / sites blocked |
| `wp_rgb-60` | Stock RGB-60 213 mm ASW rocket depth charge for the RBU-6000. Config Type=RBU, Mass=113 kg. Carried by rfn_ffg_11356, wp_bpk_udal… |  | not researched: no web searches left / sites blocked |
| `wp_s-24` | Stock S-24 240 mm Soviet aircraft rocket, carried singly. Config Type=AerialRocket, Mass=235 kg. Carried by wp_mig-23a. |  | not researched: no web searches left / sites blocked |
| `wp_s-25` | Stock S-25-O, the largest Soviet unguided aircraft rocket, carried singly. Config Type=AerialRocket, Mass=370 kg. Carried by wp_s… |  | not researched: no web searches left / sites blocked |
| `wp_s-5` | Stock S-5KO 57 mm Soviet aircraft rocket, carried in pods of up to 32. Config Type=AerialRocket, Mass=3.86 kg. Carried by plan_ka… |  | not researched: no web searches left / sites blocked |
| `wp_s-8` | Stock S-8KOM 80 mm Soviet aircraft rocket, carried in pods of up to 20. Config Type=AerialRocket, Mass=11.2 kg. Carried by the J-… |  | not researched: no web searches left / sites blocked |
| `z21_type-70_rocket` | Generic 70 mm unguided aerial rocket for the AVIC Harbin Z-21 helicopter mod (3774746803, pla_z21). Config Type=AerialRocket, Mas… |  | not researched: no web searches left / sites blocked |

## Sonobuoys, chaff, flares, noisemakers and decoys (58)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `071_726_4_chaff` | Type 726-4 shipborne passive radar chaff round (PLAN, Chinese 726-series decoy launcher), fitted to the PLAN Type 071 LPD (mod 37… |  | not researched: no web searches left / sites blocked |
| `all_air_chaff_heavy` | Stock generic aircraft chaff cartridge, 'heavy' type (Mass 0.1 kg, SpoofChance 0.6), carried by large PLA/Soviet aircraft (KJ-600… |  | not researched: no web searches left / sites blocked |
| `all_air_chaff_standard` | Stock generic aircraft chaff cartridge, standard type (Mass 0.1 kg, SpoofChance 0.4), carried by EC-2, J-16, J-35, Ka-27/28/31, Z… |  | not researched: no web searches left / sites blocked |
| `all_ship_chaff_late` | Stock generic late-era shipborne chaff round (RCS VeryLarge, SpoofChance 0.5), on Santa Maria, Mogami, Type 004, Adelaide, Kitty … |  | not researched: no web searches left / sites blocked |
| `chaff_dircm` | Not a store: the AH-64E's directed infrared countermeasure (laser jammer) emulated as a 9999-round chaff magazine (WeaponMagazine… |  | not researched: no web searches left / sites blocked |
| `fr_ngds_sealem_chaff` | French NGDS (New Generation Dagaie System) launcher firing SEALEM RF / SEALIR IR decoy rounds, on Horizon-class DDG and Aquitaine… |  | not researched: no web searches left / sites blocked |
| `fr_sonoflash` | Thales SonoFlash passive and active sonobuoy (French), on the Atlantique 2 (mod 3567256221). |  | not researched: no web searches left / sites blocked |
| `fr_sylena_chaff` | French SYLENA new-generation RF/IR decoy launcher round (SEALEM/SEALIR compatible), on La Fayette modernised and Mistral (mod 356… |  | not researched: no web searches left / sites blocked |
| `ger_MASS_ATD_noisemaker` | Rheinmetall MASS ATD anti-torpedo expendable acoustic effector (Euromod 3629144864), on F123/F124/F125 MLU fits. |  | not researched: no web searches left / sites blocked |
| `ger_MASS_omnitrap` | Rheinmetall MASS OmniTrap multispectral (RF/IR/EO) decoy round, config says 81 mm, Mass 3.5 kg; on F123/F124/F125 MLU, Skjold, Ka… |  | not researched: no web searches left / sites blocked |
| `ita_canto-v` | Naval Group CANTO-V anti-torpedo acoustic decoy fired from the CONTRALTO-V system (Euromod 3629144864), on Orizzonte and Italian … |  | not researched: no web searches left / sites blocked |
| `plan_726_4_chaff` | Type 726-4 shipborne passive radar chaff round (PLAN) on the Type 001 Liaoning (mod 3774859959); identical name/parameters to 071… |  | not researched: no web searches left / sites blocked |
| `plan_726_chaff` | PLAN Type 726-series decoy launcher chaff rounds (Modern PLAN Systems 3775128499), on Type 003, 052D, 054A, 056A. |  | not researched: no web searches left / sites blocked |
| `plan_skf-16` | SKF-16 passive directional (DIFAR-type) sonobuoy, 2020s PLAN; another mod (3637954857) calls the designation fictional. On Y-9FQ … |  | not researched: no web searches left / sites blocked |
| `plan_skf-18` | SKF-18 passive sonobuoy (PLAN, 2020s; config header copied from SSQ-77 VLAD), on Y-9FQ and Z-20F. |  | not researched: no web searches left / sites blocked |
| `plan_skf-20` | SKF-20 active omni (DICASS-type) sonobuoy, 2020 PLAN; another mod (3637954857) calls the designation fictional. On Y-9FQ and Z-20… |  | not researched: no web searches left / sites blocked |
| `plan_sq-4` | SQ-4 DIFAR-type passive sonobuoy (Chinese; mod 3417801942, uses SSQ-53 sonar), on the Z-18F. |  | not researched: no web searches left / sites blocked |
| `rfn_pk10_chaff` | Russian PK-10 (Smely) 120 mm ship decoy launcher chaff round (Russian Navy 21, 3597650470), on Project 20380 corvettes and Projec… |  | not researched: no web searches left / sites blocked |
| `rn_jezebel` | Dowty Mini-Jezebel passive sonobuoy (UK, Cold War; mod 3373356293 describes it as DIFAR), on the German Sea Lynx Mk 88. |  | not researched: no web searches left / sites blocked |
| `rn_ssq-906g` | SSQ-906G F-size (mini) LOFAR passive sonobuoy (UK, 2010s; FOCDate 2010), on the Merlin HM2 (Euromod 3629144864). |  | not researched: no web searches left / sites blocked |
| `rn_ssq-926` | SSQ-926 high-power active sonobuoy (UK, FOCDate 2002; named ALFEA, described as the AN/SSQ-101 ADAR equivalent and uses the SSQ-1… |  | not researched: no web searches left / sites blocked |
| `rn_ssq-955b` | SSQ-955B HIDAR F-size passive DIFAR sonobuoy (UK, FOCDate 2012; described as roughly AN/SSQ-53G), on the Merlin HM2 (Euromod 3629… |  | not researched: no web searches left / sites blocked |
| `rn_ssq-963d` | SSQ-963D CAMBS VI active sonobuoy (UK, FOCDate 2004; described as the AN/SSQ-62E equivalent), on the Merlin HM2 (Euromod 36291448… |  | not researched: no web searches left / sites blocked |
| `usn_adc_mk1_noisemaker` | Stock ADC Mk 1 acoustic device countermeasure (generic torpedo decoy), on Santa Maria, Charles de Gaulle, La Fayette, Mistral, Iv… |  | not researched: no web searches left / sites blocked |
| `usn_adc_mk2_mod3_noisemaker` | ADC Mk 2 Mod 3 3-inch expendable acoustic torpedo decoy (config: introduced 2007, Virginia-class launch compatibility), on RAN Co… |  | not researched: no web searches left / sites blocked |
| `usn_adc_mk2_mod4_noisemaker` | ADC Mk 2 Mod 4 3-inch surface-ship hand-launched acoustic torpedo decoy (Euromod 3629144864), on Alvaro de Bazan. |  | not researched: no web searches left / sites blocked |
| `usn_adc_mk2_mod5_noisemaker` | ADC Mk 2 Mod 5 3-inch submarine acoustic torpedo decoy launched from the internal countermeasure launcher (Euromod 3629144864), o… |  | not researched: no web searches left / sites blocked |
| `usn_adc_mk2_mod7_noisemaker` | ADC Mk 2 Mod 7 3-inch acoustic torpedo decoy with thermal lithium battery (newest Mk 2 variant; Euromod 3629144864), on Bonifaz, … |  | not researched: no web searches left / sites blocked |
| `usn_adc_mk2_noisemaker` | ADC Mk 2 Mod 0 acoustic torpedo decoy (Euromod 3629144864), on JMSDF, Korean, Philippine, RN Type 45/Type 23, Dutch ships and USS… |  | not researched: no web searches left / sites blocked |
| `usn_adc_mk2_noisemaker_rsa` | ADC Mk 2 Mod 0 acoustic torpedo decoy in mod 3413868677 (same item and description as usn_adc_mk2_noisemaker), on usn_cvn_gerald_… |  | not researched: no web searches left / sites blocked |
| `usn_LEAD_noisemaker` | LEAD (Launched Expendable Acoustic Decoy), a surface-ship acoustic torpedo decoy fired from the Mk 36 SRBOC launcher (config: int… |  | not researched: no web searches left / sites blocked |
| `usn_mk182_chaff` | Mk 36 SRBOC round modelled as a combined Mk 182 chaff and Mk 186 TORCH IR decoy (Euromod 3629144864); on Alvaro de Bazan, Meteoro… |  | not researched: no web searches left / sites blocked |
| `usn_mk214_chaff` | Sea Gnat round modelled as a combined Mk 214 seduction chaff and Mk 245 GIANT IR decoy (Euromod 3629144864); on 21 hulls incl. F1… |  | not researched: no web searches left / sites blocked |
| `usn_mk216_chaff` | Sea Gnat Mk 216 distraction chaff round (Euromod 3629144864), on the 2027 Arleigh Burke Flight IIA/III fits. |  | not researched: no web searches left / sites blocked |
| `usn_mk234_nulka` | Mk 234 Nulka active offboard rocket-powered RF decoy launched from the Mk 53 Decoy Launching System (US/Australia), on Hobart, An… |  | not researched: no web searches left / sites blocked |
| `usn_mk234_nulka_adap` | Mk 234 Nulka with the Advanced Decoy Architecture Program (ADAP) payload, same carriers as usn_mk234_nulka (Euromod 3629144864). |  | not researched: no web searches left / sites blocked |
| `usn_rr144_chaff` | Stock 'Chaff' round under an RR-144 id, carried by ships in SEST (Juan Carlos, Galicia, Charles de Gaulle, Italian DDG/FFG, Phili… |  | not researched: no web searches left / sites blocked |
| `usn_ssq-101` | AN/SSQ-101A ADAR (Air Deployed Active Receiver) multistatic sonobuoy (US), on the P-8A / P-8A 2027 (Euromod 3629144864). Same ite… |  | not researched: no web searches left / sites blocked |
| `usn_ssq-53` | Stock AN/SSQ-53 DIFAR passive sonobuoy (US; IOCDate 1972, FOCDate 1980), on S-70B-2, Thai S-70B-7 and the MV-75 Army. |  | not researched: no web searches left / sites blocked |
| `usn_ssq-53d` | AN/SSQ-53D DIFAR passive sonobuoy (US, 1992 per config), on the JMSDF SH-60J (Euromod 3629144864). |  | not researched: no web searches left / sites blocked |
| `usn_ssq-53f` | AN/SSQ-53F DIFAR passive sonobuoy (US, 2002 per config), on SH-60K, RAN MH-60R, CH-53 standalone and P-8A (Euromod 3629144864). S… |  | not researched: no web searches left / sites blocked |
| `usn_ssq-53h` | AN/SSQ-53H DIFAR passive sonobuoy (US, 2024 per config), on NH90 (NL), USN MH-60R and P-8A 2027 (Euromod 3629144864). |  | not researched: no web searches left / sites blocked |
| `usn_ssq-62` | AN/SSQ-62 DICASS active sonobuoy; the winning owner 3390330875 names it AN/SSQ-62A (config comment: 1980). On S-70B-2, Thai S-70B… |  | not researched: no web searches left / sites blocked |
| `usn_ssq-62c` | AN/SSQ-62C DICASS active sonobuoy (US, 1997 per config), on the JMSDF SH-60J (Euromod 3629144864). |  | not researched: no web searches left / sites blocked |
| `usn_ssq-62e` | AN/SSQ-62E DICASS active sonobuoy (US, 2004 per config), on SH-60K, RAN MH-60R, CH-53 standalone and P-8A (Euromod 3629144864). S… |  | not researched: no web searches left / sites blocked |
| `usn_ssq-62g` | AN/SSQ-62G DICASS active sonobuoy (US, current production variant), on NH90 (NL), USN MH-60R and P-8A 2027 (Euromod 3629144864). |  | not researched: no web searches left / sites blocked |
| `usn_ssq-77` | Stock AN/SSQ-77 VLAD (vertical line array DIFAR) passive sonobuoy (US; IOCDate 1980, FOCDate 1986), on the RAN MH-60R. |  | not researched: no web searches left / sites blocked |
| `usn_ssq-77b` | AN/SSQ-77B VLAD passive sonobuoy (US; config comment mislabels it 'SSQ-77C VLAD (1994)'), on the JMSDF SH-60J (Euromod 3629144864… |  | not researched: no web searches left / sites blocked |
| `usn_ssq-77c` | AN/SSQ-77C VLAD passive sonobuoy (US, 1999 per config), on SH-60K, USN MH-60R, P-8A and P-8A 2027 (Euromod 3629144864). Same item… |  | not researched: no web searches left / sites blocked |
| `usn_ssq_101` | AN/SSQ-101A ADAR sonobuoy in mod 3413868677 (same item as usn_ssq-101), on usn_p_8a. |  | not researched: no web searches left / sites blocked |
| `usn_ssq_53f` | AN/SSQ-53F DIFAR sonobuoy in mod 3413868677 (same item as usn_ssq-53f), on usn_p_8a. |  | not researched: no web searches left / sites blocked |
| `usn_ssq_62e` | AN/SSQ-62E DICASS sonobuoy in mod 3413868677 (same item as usn_ssq-62e), on usn_p_8a. |  | not researched: no web searches left / sites blocked |
| `usn_ssq_77c` | AN/SSQ-77C VLAD sonobuoy in mod 3413868677 (same item as usn_ssq-77c), on usn_p_8a. |  | not researched: no web searches left / sites blocked |
| `wp_aircraft_chaff` | Stock generic aircraft chaff cartridge (Mass 0.1 kg, SpoofChance 0.5), the most widely carried countermeasure in SEST (93 aircraf… |  | not researched: no web searches left / sites blocked |
| `wp_noisemaker` | Stock Soviet/Chinese submarine acoustic noisemaker (generic torpedo countermeasure), on Kilo, Type 039/039B/039C, Type 093B, Yase… |  | not researched: no web searches left / sites blocked |
| `wp_rgb-1` | Stock Soviet RGB-1 passive omnidirectional sonobuoy, on the Tu-142M. |  | not researched: no web searches left / sites blocked |
| `wp_rgb-3` | Stock Soviet RGB-3 active sonobuoy, on the Tu-142M. |  | not researched: no web searches left / sites blocked |
| `wp_rgb-nm1` | Stock Soviet RGB-NM-1 passive omnidirectional sonobuoy (Baku suite), on Ka-27 and PLAN Ka-28. |  | not researched: no web searches left / sites blocked |

## Fuel tanks, rocket pods and gun pods (102)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `am_boz` | BOZ-101 chaff/flare dispenser pod for Tornado (300 kg; 28 x wp_aircraft_chaff, priced separately), Italian Navy Mod 3505420313; c… |  | not researched: no web searches left / sites blocked |
| `am_tornado_ids_tank` | Tornado IDS external drop tank, named '1800 l. Droptank' (Fuel=1800 kg), Italian Navy Mod 3505420313; carried by am_tornado_ids |  | not researched: no web searches left / sites blocked |
| `bel_hmp-250` | FN Herstal HMP-250 12.7 mm gun pod (116.5 kg; 250 x usn_cal_05in rounds), stock file; carried by phl_h-76 |  | not researched: no web searches left / sites blocked |
| `cft_f-16` | F-16 Block 52+ conformal fuel tanks, pair (Mass=408, Fuel=1380), F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus |  | not researched: no web searches left / sites blocked |
| `dts_anaaq-13` | AN/AAQ-13 LANTIRN navigation pod (208 kg; visual sensor), mod 3636386513; carried by usaf_f-15e_SE, usaf_f-15ex_SEII |  | not researched: no web searches left / sites blocked |
| `dts_anaaq-14` | AN/AAQ-14 LANTIRN targeting pod (laser designator + visual), mod 3553116604; carried by usaf_f-15e_SE |  | not researched: no web searches left / sites blocked |
| `dts_anaaq-33` | AN/AAQ-33 Sniper Advanced Targeting Pod, mod 3652097318; carried by usaf_b-1b_dts, usaf_f-15ex_SEII |  | not researched: no web searches left / sites blocked |
| `dts_gbu-39_quad` | BRU-61/A-type four-place carriage loaded with 4 x dts_gbu-39 SDB (rack Mass=10), mod 3760871384; carried by usaf_f-15e_SE |  | not researched: no web searches left / sites blocked |
| `dts_gbu-53_quad` | Four-place carriage (BRU-61/A type) loaded with 4 x GBU-53/B StormBreaker, mod 3760871384; carried by usaf_b-1b_dts, usaf_f-15ex_… |  | not researched: no web searches left / sites blocked |
| `eu_litening` | Litening targeting pod (systems AN/AAQ-28 + Litening), Eurofighter mod 3587877691; carried by eu/raf_ef2000_fgr4_late |  | not researched: no web searches left / sites blocked |
| `eu_tank_1000` | Eurofighter Typhoon 1,000 l external fuel tank (Fuel=1000), Eurofighter mod 3587877691; carried by eu/raf_ef2000_fgr4_late |  | not researched: no web searches left / sites blocked |
| `f16_anaaq-33` | AN/AAQ-33 Sniper Advanced Targeting Pod, F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus, usaf_f-16cm-bl52d |  | not researched: no web searches left / sites blocked |
| `f16_gbu-39_quad` | Four-place carriage (BRU-61/A type) with 4 x f16_gbu-39 SDB, F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus, usaf_f-1… |  | not researched: no web searches left / sites blocked |
| `f16_gbu-53_quad` | Four-place carriage (BRU-61/A type) with 4 x f16_gbu-53 StormBreaker, F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus,… |  | not researched: no web searches left / sites blocked |
| `fr_damoncles` | Damocles targeting pod (Thales), French Air Force mod 3758943352; carried by fr_rafale_m |  | not researched: no web searches left / sites blocked |
| `fr_talios` | TALIOS targeting pod (Thales), French Air Force mod 3758943352; carried by fr_rafale_b_l, fr_rafale_m_l |  | not researched: no web searches left / sites blocked |
| `fr_tank_1200` | Rafale 1,200 l class external fuel tank, named '1200L Fueltank' (Fuel=1200), French Air Force mod 3758943352; carried by fr_rafal… |  | not researched: no web searches left / sites blocked |
| `jp_jaaq-2` | J/AAQ-2 targeting pod for the F-2 (202 kg; uses the AN/AVQ-23 designator system), F-2A mod 3755769170; carried by jp_f-2a_late |  | not researched: no web searches left / sites blocked |
| `jp_tank_300_f-2a` | Mitsubishi F-2A ~300 US gal external tank (Fuel=908 kg; no display name), F-2A mod 3755769170; carried by jp_f-2a_late |  | not researched: no web searches left / sites blocked |
| `jp_tank_610_f-2a` | Mitsubishi F-2A 2,310 l (~600 US gal) external drop tank (Fuel=1800 kg), F-2A mod 3755769170; carried by jp_f-2a_late |  | not researched: no web searches left / sites blocked |
| `jp_ter_rockeye_3` | Triple ejector rack with 3 x Mk 20 Rockeye (rack Mass=50), F-2A mod 3755769170; carried by jp_f-2a_late |  | not researched: no web searches left / sites blocked |
| `nl_tank_685` | Lynx-type helicopter auxiliary tank, 685 l (Fuel=685, Mass=5), Euromod South Korea Navy 3789208859; carried by rok_mk99_a (ROKN S… |  | not researched: no web searches left / sites blocked |
| `pla_gun_pod_qjk-99_left` | QJK-99 12.7 mm gun pod, left (300 kg; 1,000 x wp_cal_05in), Modern PLAN Systems 3775128499; carried by plan_z-9c |  | not researched: no web searches left / sites blocked |
| `pla_gun_pod_qjk-99_right` | QJK-99 12.7 mm gun pod, right (300 kg; 1,000 x wp_cal_05in), Modern PLAN Systems 3775128499; carried by plan_z-9c |  | not researched: no web searches left / sites blocked |
| `pla_pod_kg-800` | KG-800 airborne ECM jamming pod (260 kg), mod 3486502935; carried by plaf_j16d, plan_j-15d |  | not researched: no web searches left / sites blocked |
| `plaaf_1400l_fueltank_new` | Shenyang J-8F 1,400 l external fuel tank (Fuel=1240), J-8 mod 3433577445; carried by plaaf_j-8f |  | not researched: no web searches left / sites blocked |
| `plaaf_4xgj` | Internal-bay four-round composite launcher for BBM-2 glide bombs (122 kg), mod 3801549552; carried by plaaf_j36, plan_j-35, plan_… |  | not researched: no web searches left / sites blocked |
| `plaaf_800l_fueltank_new` | Shenyang J-8F 800 l external fuel tank (Fuel=610), J-8 mod 3433577445; carried by plaaf_j-8f |  | not researched: no web searches left / sites blocked |
| `plaaf_hf-6` | HF-6 7-tube 90 mm rocket pod (Type 90-I rockets; 47 kg), mod 3436170138; carried by plaaf_j-8f, plaaf_jh7a |  | not researched: no web searches left / sites blocked |
| `plaaf_J10_fueltank_new` | Chengdu J-10C wing external fuel tank (Fuel=610; no display name), J-10C mod 3481228992; carried by plaaf_j10c |  | not researched: no web searches left / sites blocked |
| `plaaf_J10_fueltank_under` | Chengdu J-10C centreline external fuel tank (Fuel=610; no display name), J-10C mod 3481228992; carried by plaaf_j10c |  | not researched: no web searches left / sites blocked |
| `plaaf_j16_yings-iii` | YINGS-III electro-optical targeting / laser designation pod (205 kg), J-16 mod 3769142422; carried by plaaf_j16 |  | not researched: no web searches left / sites blocked |
| `plaaf_JH7A_fueltank_new` | Xian JH-7A external fuel tank (Fuel=610; no display name), JH-7A mod 3526982088; carried by plaaf_jh7a |  | not researched: no web searches left / sites blocked |
| `plaaf_JH7A_fueltank_under` | Xian JH-7A underwing/centreline external fuel tank (Fuel=610; no display name), JH-7A mod 3526982088; carried by plaaf_jh7a |  | not researched: no web searches left / sites blocked |
| `plaaf_kd-88_pod` | KD-88 missile data-link (command guidance) pod (350 kg), mod 3812111085; carried by plaaf_h-6k_late |  | not researched: no web searches left / sites blocked |
| `plaaf_mer_ls-6_250_6` | H-6K six-place multiple ejector rack with 6 x LS-6 250 kg glide bombs (rack 120 kg), mod 3812111085; carried by plaaf_h-6k_late |  | not researched: no web searches left / sites blocked |
| `plaaf_mer_ls-6_500_4l` | H-6K four-place multiple ejector rack (left) with 4 x LS-6 500 kg, mod 3812111085; carried by plaaf_h-6k_late |  | not researched: no web searches left / sites blocked |
| `plaaf_mer_ls-6_500_4r` | H-6K four-place multiple ejector rack (right) with 4 x LS-6 500 kg, mod 3812111085; carried by plaaf_h-6k_late |  | not researched: no web searches left / sites blocked |
| `plaaf_mer_type-3-250_6` | H-6K six-place multiple ejector rack with 6 x Type-3 250 kg bombs (rack 100 kg), mod 3812111085; carried by plaaf_h-6k_late |  | not researched: no web searches left / sites blocked |
| `sest_agr-30_pod` | SEST 7-tube 70 mm rocket pod (LAU-68 class) for the fictional AGR-30 Redback. Type=Container, 10 kg. Carried by the S-70B-2, A-10… |  | not researched: no web searches left / sites blocked |
| `sest_agr-30_pod19` | SEST 19-tube 70 mm rocket pod (LAU-61/LAU-3/M261 class) for the AGR-30 Redback. Type=Container, 10 kg. Carried by the MH-60R, A-1… |  | not researched: no web searches left / sites blocked |
| `spa_av-8b_gau12` | AV-8B GAU-12/U 25 mm gun pack (300 kg; 300 x spa_cal_25mm_m2), Euromod Modern Spanish Navy 3731208477; carried by spa_av-8b_plus |  | not researched: no web searches left / sites blocked |
| `spa_av-8b_tank_left` | AV-8B Harrier II 1,135 l (300 US gal) drop tank, left (Fuel=910), Euromod Modern Spanish Navy 3731208477; carried by spa_av-8b_pl… |  | not researched: no web searches left / sites blocked |
| `spa_av-8b_tank_right` | AV-8B Harrier II 1,135 l (300 US gal) drop tank, right (Fuel=910), Euromod Modern Spanish Navy 3731208477; carried by spa_av-8b_p… |  | not researched: no web searches left / sites blocked |
| `spa_ef2000_fueltank` | Eurofighter Typhoon 1,000 l drop tank (Fuel=800), Euromod Modern Spanish Navy 3731208477; carried by spa_ef2000 |  | not researched: no web searches left / sites blocked |
| `spa_litening` | Litening targeting pod (systems eu_AN/AAQ-28 + eu_Litening, 209 kg), Euromod Modern Spanish Navy 3731208477; carried by spa_av-8b… |  | not researched: no web searches left / sites blocked |
| `su_l004` | Russian ECM jamming pod named 'L-004' (260 kg), mod 3434072450; carried by plaaf_su-27ubk, plaf_j16a/d, wp_su-30sm2 |  | not researched: no web searches left / sites blocked |
| `uav_mq-9_pod` | MQ-9 self-protection pod: ECM (borrowed AN/ALQ-99 system) plus a chaff dispenser with 15 x wp_aircraft_chaff (260 kg), MQ-9 mod 3… |  | not researched: no web searches left / sites blocked |
| `uav_tank_mq-9` | MQ-9 Reaper underwing external fuel tank (Fuel=567), MQ-9 mod 3503670861; carried by usaf_mq-9_er |  | not researched: no web searches left / sites blocked |
| `usa_lau-3a_apache` | 19-tube 2.75 in Hydra launcher on Apache (LAU-3/A file; Army M261 class), mod 3820759806; carried by adf_ah-64e, usa_ah-64d/e |  | not researched: no web searches left / sites blocked |
| `usaf_aaq-28_litening` | AN/AAQ-28 Litening targeting pod, Italian Navy Mod 3505420313; carried by mm_av-8b_plus |  | not researched: no web searches left / sites blocked |
| `usaf_alq-184` | AN/ALQ-184(V) ECM pod, long version, F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus, usaf_f-16cm-bl52d |  | not researched: no web searches left / sites blocked |
| `usaf_alq-184_2` | AN/ALQ-184(V) ECM pod, A-10C mod 3459682829; carried by usa_a-10c, usaf_a-10c_plus |  | not researched: no web searches left / sites blocked |
| `usaf_anasq-213` | AN/ASQ-213 HARM Targeting System pod (ESM, 208 kg), F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus, usaf_f-16cm-bl52d |  | not researched: no web searches left / sites blocked |
| `usaf_gbu-54_double` | Two-place smart rack (BRU-57/A-type) with 2 x usaf_gbu-54 Laser JDAM, F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus,… |  | not researched: no web searches left / sites blocked |
| `usaf_litening` | AN/AAQ-28 Litening targeting pod, A-10C mod 3459682829; carried by usa_a-10c, usaf_a-10c_plus |  | not researched: no web searches left / sites blocked |
| `usaf_pave_spike` | AN/AVQ-23 Pave Spike laser designator pod (1970s), stock file; here carried by rok_f-50_ph and wp_su-30sm2 as a stand-in |  | not researched: no web searches left / sites blocked |
| `usaf_tank_150_f-5` | F-5 150 US gal (567 l) drop tank, stock file (Fuel=465); here carried by rok_f-50_ph (FA-50PH stand-in) |  | not researched: no web searches left / sites blocked |
| `usaf_tank_300_f16` | F-16 300 US gal centreline drop tank (Fuel=1135), F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus, usaf_f-16cm-bl52d |  | not researched: no web searches left / sites blocked |
| `usaf_tank_370_f-16` | F-16 370 US gal (1,400 l) wing drop tank (Fuel=1148), Apex Predators MiG-29A & F-16A mod 3416372890; carried by usaf_f-16a |  | not researched: no web searches left / sites blocked |
| `usaf_tank_370_f16` | F-16 370 US gal (1,400 l) wing drop tank (Fuel=1148), F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus, usaf_f-16cm-bl5… |  | not researched: no web searches left / sites blocked |
| `usaf_tank_600_f16` | F-16 600 US gal wing drop tank, F-16C modern mod 3758320372; carried by pol_f-16c-bl52plus, usaf_f-16cm-bl52d |  | not researched: no web searches left / sites blocked |
| `usaf_tank_610_f-15` | F-15 610 US gal (2,309 l) external tank, stock file; carried by usaf_f-15e_SE, usaf_f-15ex_SEII |  | not researched: no web searches left / sites blocked |
| `usmc_25mm_gunpod` | AV-8B GAU-12/U 25 mm gun pack (300 kg; 300 x mm_cal_25mm), Italian Navy Mod 3505420313; carried by mm_av-8b_plus |  | not researched: no web searches left / sites blocked |
| `usmc_alq-164` | AN/ALQ-164 defensive ECM pod (AV-8B), Italian Navy Mod 3505420313; carried by mm_av-8b_plus |  | not researched: no web searches left / sites blocked |
| `usmc_tank_230_av-8b` | AV-8B 871 l (230 US gal) drop tank (Fuel=705), Italian Navy Mod 3505420313; carried by mm_av-8b_plus |  | not researched: no web searches left / sites blocked |
| `usn_agr-20b` | 7-tube 2.75 in APKWS launcher (LAU-68/LAU-131 class; 7 x usa_apkws_2_m282), A-10C mod 3459682829; carried by usa_a-10c, usaf_a-10… |  | not researched: no web searches left / sites blocked |
| `usn_agr-20b_apache` | 7-tube 2.75 in APKWS launcher on Apache (M260 class; 7 x usa_apkws_2_m282), mod 3820759806; carried by adf_ah-64e, usa_ah-64d/e |  | not researched: no web searches left / sites blocked |
| `usn_bru-61a` | BRU-61/A four-place carriage with 4 x usn_gbu-39 SDB (122 kg), F-22 mod 3418252667; carried by usaf_f-22_s6 |  | not researched: no web searches left / sites blocked |
| `usn_bru-61a_10` | BRU-61/A four-place carriage with 4 x usn_gbu-39_10 SDB (122 kg), A-10C mod 3459682829; carried by usa_a-10c, usaf_a-10c_plus |  | not researched: no web searches left / sites blocked |
| `usn_d-704` | D-704 (A/A42R-1 class) 300 US gal buddy aerial-refuelling store (318 kg, Fuel=908, RefuelSystem), mod 3606134711; carried by usn_… |  | not researched: no web searches left / sites blocked |
| `usn_f-35_gun_pod` | F-35B/C GAU-22/A 25 mm missionized gun pod (220 x usn_cal_25mm_m2), US Naval Aviation mod 3737267013; carried by usn_f-35c |  | not researched: no web searches left / sites blocked |
| `usn_ft600_10` | A-10C external fuel tank (file name 'ft600'; Fuel=753; no display name), A-10C mod 3459682829; carried by usa_a-10c, usaf_a-10c_p… |  | not researched: no web searches left / sites blocked |
| `usn_lau-10a` | LAU-10/A 4-tube 5 in Zuni rocket launcher, stock file; carried by mm_av-8b_plus |  | not researched: no web searches left / sites blocked |
| `usn_lau-3a` | LAU-3/A 19-tube 2.75 in rocket launcher (Hydra), stock file; carried by jp_f-2a_late, usaf_f-15e_SE, usaf_f-16a |  | not researched: no web searches left / sites blocked |
| `usn_lau-3a_APKWS` | 19-tube 2.75 in launcher loaded with APKWS (usa_apkws_2_m282), mod 3820759806; carried by adf_ah-64e |  | not researched: no web searches left / sites blocked |
| `usn_lau-68` | LAU-68 7-tube 2.75 in rocket launcher (Hydra), stock file; carried by phl_h-76 |  | not researched: no web searches left / sites blocked |
| `usn_sh60_tank` | SH-60/MH-60 auxiliary external fuel tank (Fuel=610; no display name), US Naval Aviation mod 3737267013; carried by jmsdf_sh-60j/k… |  | not researched: no web searches left / sites blocked |
| `usn_tank_267_f-14` | F-14 267 US gal (1,010 l) external tank, stock file; carried by usn_f-14a |  | not researched: no web searches left / sites blocked |
| `usn_tank_60gal_sh-2` | SH-2 60 US gal-class (227 l) auxiliary tank, stock file; here carried by phl_h-76 (S-76 stand-in) |  | not researched: no web searches left / sites blocked |
| `usn_tank_610_f-18` | 'F/A-18E/F Fuel Tank': the Super Hornet's underwing or centreline external drop tank (Fuel=1800 kg; the '600 gallon / F-4D' comme… |  | not researched: no web searches left / sites blocked |
| `usn_ter_mk82_3` | TER-9/A-type triple ejector rack with 3 x Mk 82, stock file; carried by jp_f-2a_late |  | not researched: no web searches left / sites blocked |
| `wp_apk-9` | APK-9 data-link pod for the Kh-59M (stock file; 260 kg); carried by wp_su-30m, wp_su-30sm2 |  | not researched: no web searches left / sites blocked |
| `wp_b8m-1` | B-8M1 20-tube 80 mm S-8 rocket pod, stock file; carried by J-11BG, J-15, Mi-24P, MiG-23, MiG-29K, Su-25SM3, Su-33 |  | not researched: no web searches left / sites blocked |
| `wp_fantasmagoria` | L-080 Fantasmagoria ARM targeting / ESM pod (stock file; 260 kg); carried by wp_su-24mp |  | not researched: no web searches left / sites blocked |
| `wp_fueltank3000_w` | Soviet PTB-3000 (3,000 l) wing drop tank, stock file (Fuel=2470); carried by wp_su-24mp and msdvd_tu-214r |  | not researched: no web searches left / sites blocked |
| `wp_fueltank400_w` | Soviet PTB-400 (400 l) wing drop tank, stock file; here carried by tha_S-70B-7_Seahawk as a stand-in |  | not researched: no web searches left / sites blocked |
| `wp_fueltank800_f` | Soviet PTB-800 (800 l) fuselage drop tank, stock file; carried by wp_mig-23a |  | not researched: no web searches left / sites blocked |
| `wp_fueltank800_w` | Soviet PTB-800 (800 l) wing drop tank, stock file; carried by wp_mig-23a |  | not researched: no web searches left / sites blocked |
| `wp_pod_delta_fcr` | Delta-NG radio-command guidance pod for Kh-23 (stock file; 200 kg); carried by wp_mig-23a |  | not researched: no web searches left / sites blocked |
| `wp_pod_rfk-t_vrecon` | RFK-T visual reconnaissance camera pod (stock file; 200 kg); carried by wp_mig-23a |  | not researched: no web searches left / sites blocked |
| `wp_pod_tangazh_elint` | Tangazh ELINT pod (stock file; 200 kg); carried by wp_su-24mp |  | not researched: no web searches left / sites blocked |
| `wp_s-25_pod` | O-25 single launch tube for the S-25 240 mm rocket (stock file; 50 kg); carried by wp_su-25sm3 |  | not researched: no web searches left / sites blocked |
| `wp_tank_1150_mig-29` | MiG-29 1,150 l wing drop tank (Fuel=820), MiG-29K mod 3417446309; carried by wp_mig-29k |  | not researched: no web searches left / sites blocked |
| `wp_tank_1200mig-35` | MiG-35 1,200 l drop tank (named '1200L'), MiG-35 mod 3659742367; carried by wp_mig-35 |  | not researched: no web searches left / sites blocked |
| `wp_tank_1500_mig-29` | MiG-29 1,500 l centreline drop tank (Fuel=1050), MiG-29K mod 3417446309; carried by wp_mig-29k |  | not researched: no web searches left / sites blocked |
| `wp_ua` | BDZ-UMK2-B pylon adaptor mass placeholder for the MiG-23 (stock file comment: 'Mass for BDZ-UMK2-B adaptor'; Mass=60, no weapon, … |  | not researched: no web searches left / sites blocked |
| `wp_ub-16-57KV` | UB-16-57KV 16-tube 57 mm S-5 rocket pod, stock file; carried by plan_ka-28, wp_ka-27 |  | not researched: no web searches left / sites blocked |
| `wp_ub-16-57UM` | UB-16-57UM 16-tube 57 mm S-5 rocket pod, stock file; carried by plan_ka-28, wp_ka-27 |  | not researched: no web searches left / sites blocked |
| `wp_ub-32` | UB-32 32-tube 57 mm S-5 rocket pod, mod 3465256032; carried by wp_mi-8tv |  | not researched: no web searches left / sites blocked |
| `wp_upk_23-250` | UPK-23-250 23 mm GSh-23L gun pod (300 kg; 250 x wp_cal_23mm), stock file; carried by plan_ka-28, wp_ka-27, wp_mi-24p |  | not researched: no web searches left / sites blocked |
| `z21_type-70_launcher` | Seven-tube 70 mm rocket pod for the Z-21 (32 kg), mod 3774746803; carried by pla_z21 (concept attack helicopter) |  | not researched: no web searches left / sites blocked |

## Land vehicles and systems (50)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `de_pzh2000` | PzH 2000 155 mm tracked self-propelled howitzer (KMW). mods-source/3603367264/land_units/de_pzh2000.ini (MobileUnit, Mass 23.8, g… | $10,700,000 / $19,900,000 | found, not confirmed: the checker had no searches left |
| `fr_afv_jaguar` | EBRC Jaguar 6x6 armoured reconnaissance and combat vehicle (KNDS France/Arquus/Thales) with 40CTC gun and Akeron missiles. mods-s… | $6,310,000 / $7,210,000 | found, not confirmed: the checker had no searches left |
| `fr_apc_griffon` | VBMR Griffon 6x6 multirole armoured vehicle (KNDS France/Arquus/Thales) with an M2 RWS. mods-source/3736147136/land_units/fr_apc_… | $1,710,000 / $1,690,000 | found, not confirmed: the checker had no searches left |
| `fr_apc_vab_top` | VAB TOP: French Army VAB 4x4 APC (Renault Trucks Defense/Arquus, service 1979) with a remote weapon station (tourelleau téléopéré… |  | not researched: no web searches left / sites blocked |
| `fr_vl-mica_tel` | VL MICA vertical-launch SAM TEL (MBDA). mods-source/3437105712/land_units/fr_vl-mica_tel.ini. Variants: France, Italy, Ukraine (S… |  | not researched: no web searches left / sites blocked |
| `idf_dsws` | David's Sling (Rafael/Raytheon) launcher with 12 Stunner cells (SIM-X). mods-source/3558173926/land_units/idf_dsws.ini, Israel. I… |  | no source found: Leave-unknown stands. The identity is confirmed from the names file (Davids Sling TEL, Israel). The researcher's Finlan… |
| `idf_dsws_radar` | David's Sling battery radar vehicle carrying the EL/M-2084 multi-mission radar plus the IDF/DSWS-FCR. mods-source/3558173926/land… | $15,600,000 / $20,400,000 | found, not confirmed: the checker had no searches left |
| `jp_12ssmht` | JGSDF Type 12 SSM (improved, ER) coastal anti-ship missile launcher truck, 'Type-12-SSM-ER-System-2024' (MHI). mods-source/347064… |  | not researched: no web searches left / sites blocked |
| `kr_k9` | K9 Thunder 155 mm/52 tracked self-propelled howitzer (Hanwha). mods-source/3603367264/land_units/kr_k9.ini. Names: 'K9 Self-Prope… | $4,840,000 / $9,120,000 | found, not confirmed: the checker had no searches left |
| `pla_9k331` | Tor-M1 (9K331, SA-15) self-propelled short-range SAM vehicle in PLA service. mods-source/3733719765/land_units/pla_9k331.ini. Nam… | $24,100,000 / ? | found, not confirmed: the checker had no searches left |
| `pla_aaa_type55` | 37 mm Type 55 towed anti-aircraft gun (Chinese licence copy of the Soviet 61-K). Vanilla: mods-source/_vanilla/original/language_… |  | not researched: no web searches left / sites blocked |
| `pla_apc_zbl-08` | ZBL-08 (Type 08) 8x8 IFV, PLA. mods-source/3733719765/land_units/pla_apc_zbl-08.ini. Variants: base, Sand, Snow. |  | not researched: no web searches left / sites blocked |
| `pla_df-21c_tel` | DF-21C MRBM TEL, PLA. mods-source/3733719765/land_units/pla_df-21c_tel.ini. |  | not researched: no web searches left / sites blocked |
| `pla_df-26b_tel` | DF-26B IRBM TEL, PLA. mods-source/3733719765/land_units/pla_df-26b_tel.ini. |  | not researched: no web searches left / sites blocked |
| `pla_df-41_tel` | DF-41 ICBM road-mobile TEL, China (Mass 40, ammunition pla_df-41). Source mods-source/3571718093/land_units/pla_df-41_tel.ini; th… |  | not researched: no web searches left / sites blocked |
| `pla_h-200a_radar` | H-200A fire-control radar vehicle, PLA SAM battery. mods-source/3733719765/land_units/pla_h-200a_radar.ini. |  | not researched: no web searches left / sites blocked |
| `pla_spaag_type63` | Type 63 SPAAG: a T-34 hull with twin 37 mm guns, retired by the PLA in 1990. Vanilla (no config path). |  | not researched: no web searches left / sites blocked |
| `ru_50n6` | 50N6 multifunction search-and-track radar of the S-350 Vityaz, Russia. mods-source/3524446392/land_units/ru_50n6.ini. |  | not researched: no web searches left / sites blocked |
| `ru_spaa_mt-lb_sosna` | Sosna short-range SAM on an MT-LB chassis, Russia. mods-source/3508275114/land_units/ru_spaa_mt-lb_sosna.ini. |  | not researched: no web searches left / sites blocked |
| `ru_vityaz-lr_tel` | S-350 Vityaz TEL (long-range load-out), Russia. mods-source/3524446392/land_units/ru_vityaz-lr_tel.ini. |  | not researched: no web searches left / sites blocked |
| `shahed_tel_black` | Road-mobile Shahed-136 loitering-munition launch truck, black scheme (Mass 20, one Shahed-136 container), Iran (Variant1 flagged … |  | not researched: no web searches left / sites blocked |
| `shahed_tel_white` | Road-mobile Shahed-136 launch truck, white scheme. Same system as shahed_tel_black. mods-source/3497601759/land_units/shahed_tel_… |  | not researched: no web searches left / sites blocked |
| `thaad_tel` | THAAD truck-mounted launcher, US Army. mods-source/3683253079/land_units/thaad_tel.ini (LandUnitSubType=SAM, weapon THAAD). The n… | $12,500,000 / $18,200,000 | found, not confirmed: the checker had no searches left |
| `usa_an_mpq-65_radar` | AN/MPQ-65 Patriot (PAC-3) radar set. mods-source/3437105712/land_units/usa_an_mpq-65_radar.ini. Variants: US, Germany, Greece and… | ? / $112,500,000 | found, not confirmed: the checker had no searches left |
| `usa_car_hemtt` | HEMTT heavy tactical truck, US Army (Mass 31, carries TruckSupplySystem in this fork). mods-source/3605013271/land_units/usa_car_… | $333,000 / $517,000 | found, not confirmed: the checker had no searches left |
| `usa_pac-3_launcher` | Patriot PAC-3 launching station (M903 type). mods-source/3437105712/land_units/usa_pac-3_launcher.ini. Variants: US, Germany, Gre… |  | no source found: Leave-unknown stands. The identity is confirmed from the names file (PAC-3 Launcher, six variants). The researcher's pa… |
| `usa_steelfin_launcher` | Anduril Steelfin four-cell stationary container launcher paired with a battery radar. mods-source/3820576916/land_units/usa_steel… |  | no source found: Leave-unknown stands. The readme quote was found verbatim at line 9 of mods-source/3820576916/Readme.txt, and the names… |
| `wp_2s19` | 2S19 Msta-S 152 mm tracked self-propelled howitzer, Soviet/Russian. mods-source/3603306548/land_units/wp_2s19.ini. |  | not researched: no web searches left / sites blocked |
| `wp_2s43` | 2S43 Malva 152 mm wheeled self-propelled howitzer, Russia. mods-source/3603306548/land_units/wp_2s43.ini. |  | not researched: no web searches left / sites blocked |
| `wp_an_tpy_2` | AN/TPY-2 X-band radar of the THAAD battery, US (Type Radar,ESM). mods-source/3683253079/land_units/wp_an_tpy_2.ini. | $182,000,000 / $303,000,000 | found, not confirmed: the checker had no searches left |
| `wp_buk-m3` | Buk-M3 self-propelled launcher with its own fire-control radar (9S36), Russia. Source mods-source/3564792549/land_units/wp_buk-m3… |  | not researched: no web searches left / sites blocked |
| `wp_bukslave` | Buk-M3 9A316M launcher (TEL) of the Buk-M3 complex. Source mods-source/3564792549/land_units/wp_bukslave.ini; the batch path is t… |  | not researched: no web searches left / sites blocked |
| `wp_car_ural_command` | Ural truck mobile command centre. Vanilla (no config path). |  | not researched: no web searches left / sites blocked |
| `wp_emad_tel` | Emad MRBM TEL, Iran (green and desert variants). mods-source/3493115616/land_units/wp_emad_tel.ini. |  | not researched: no web searches left / sites blocked |
| `wp_fattah1_tel` | Fattah-1 hypersonic MRBM TEL, Iran. mods-source/3673703427/land_units/wp_fattah1_tel.ini. |  | not researched: no web searches left / sites blocked |
| `wp_fattah2_tel` | Fattah-2 HGV-armed MRBM TEL, Iran. mods-source/3672497668/land_units/wp_fattah2_tel.ini. |  | not researched: no web searches left / sites blocked |
| `wp_iskander_m` | Iskander-M (9K720) TEL with two wp_9k720_he missiles, Russia. mods-source/3681748718/land_units/wp_iskander_m.ini; 3732654992 shi… |  | not researched: no web searches left / sites blocked |
| `wp_kraz_tel` | 5P85TE towed TEL of the S-300PMU2 on a KrAZ tractor. mods-source/3732654992/land_units/wp_kraz_tel.ini. Variants: Soviet, DDR, Cz… |  | not researched: no web searches left / sites blocked |
| `wp_nebou` | Nebo-U (55Zh6U) VHF surveillance radar, Russia. mods-source/3551621846/land_units/wp_nebou.ini. |  | not researched: no web searches left / sites blocked |
| `wp_sa-21_40n6_tel` | S-400 (SA-21) long-range TEL (40N6 load-out). mods-source/3392434750/land_units/wp_sa-21_40n6_tel.ini. |  | not researched: no web searches left / sites blocked |
| `wp_sa-21_flaplid` | '36H6 Flaplid' engagement radar (30N6-family Flap Lid) for the SA-21 set. mods-source/3496055699/land_units/wp_sa-21_flaplid.ini;… |  | not researched: no web searches left / sites blocked |
| `wp_sam_site_sa-21` | SA-21 SAM site: one land unit bundling two Tin Shield and one Big Bird radar with 12 four-round launcher groups (48N6E3, 40N6, 9M… |  | not researched: no web searches left / sites blocked |
| `wp_scud_9k72` | 9K72 Elbrus (SCUD-B) MAZ-543 TEL. mods-source/3461519690/land_units/wp_scud_9k72.ini. Variants: Soviet, Iraq. |  | not researched: no web searches left / sites blocked |
| `wp_sejjil_tel` | Sejjil solid-fuel MRBM TEL, Iran. mods-source/3551676319/land_units/wp_sejjil_tel.ini. |  | not researched: no web searches left / sites blocked |
| `wp_shahed238_launcher` | Shahed-238 jet-drone launcher (one ods_shahed238), Iran. mods-source/3686449681/land_units/wp_shahed238_launcher.ini (LandUnitSub… |  | not researched: no web searches left / sites blocked |
| `wp_silkworm_launcher` | SY-1 / CSSC-1 Scrubbrush coastal anti-ship missile site. Vanilla (no config path). |  | not researched: no web searches left / sites blocked |
| `wp_son-9` | SON-9 (Fire Can) anti-aircraft gun fire-control radar site. Vanilla (no config path). |  | not researched: no web searches left / sites blocked |
| `wp_ss-26_tel` | SS-26 (Iskander, 9K720) TEL, Soviet flag, ammunition wp_ss-26. mods-source/3408662804/land_units/wp_ss-26_tel.ini. The same syste… |  | not researched: no web searches left / sites blocked |
| `wp_ss-27_tel` | SS-27 Topol-M road-mobile ICBM TEL (Mass 40, ammunition wp_ss-27). Source mods-source/3571718093/land_units/wp_ss-27_tel.ini; the… |  | not researched: no web searches left / sites blocked |
| `wp_tombstone` | 30N6E2 Tomb Stone fire-control radar of the S-300PMU2. mods-source/3732654992/land_units/wp_tombstone.ini. |  | not researched: no web searches left / sites blocked |

## Land installations (39)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `4tentgroup` | Buildings and Objectives (3600788156) '4 Tent Group': four general-purpose military tents with fuel barrels, LandUnitSubType=Inst… | $26,400 / $48,000 | found, not confirmed: the checker had no searches left |
| `airbase_raaf_amberley` | SEST_RAAF_Bases clone of the Modern US Airbase template named RAAF Base Amberley (Queensland, est. 1938), Nation=Australia, capac… |  | not researched: no web searches left / sites blocked |
| `airbase_raaf_butterworth` | SEST_RAAF_Bases clone named RAAF Base Butterworth (the RAAF presence at RMAF Butterworth, Malaysia), Nation=Australia, air group … |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Butterworth', Nation=Australia. There is no tracker… |
| `airbase_raaf_curtin` | SEST_RAAF_Bases clone named RAAF Base Curtin (Bare Base), near Derby WA, Nation=Australia, air group F-35A x8, KC-46A x2. Built 1… | $50,000,000 / $142,000,000 | found, not confirmed: the checker had no searches left |
| `airbase_raaf_darwin` | SEST_RAAF_Bases clone named RAAF Base Darwin (shared with Darwin International Airport), Nation=Australia, air group F-35A x8, F-… |  | not researched: no web searches left / sites blocked |
| `airbase_raaf_east_sale` | SEST_RAAF_Bases clone named RAAF Base East Sale (Victoria, training base), Nation=Australia, air group F-35A x4, MQ-9A x4. Fielde… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base East Sale', Nation=Australia. There is no tracker l… |
| `airbase_raaf_edinburgh` | SEST_RAAF_Bases clone named RAAF Base Edinburgh (South Australia, P-8A main operating base), Nation=Australia, air group P-8A x8,… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Edinburgh', Nation=Australia. Leave-unknown is corr… |
| `airbase_raaf_gingin` | SEST_RAAF_Bases clone named RAAF Base Gingin (WA; in reality a small satellite airfield of RAAF Base Pearce), Nation=Australia, a… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Gingin', Nation=Australia. There is no sourced figu… |
| `airbase_raaf_learmonth` | SEST_RAAF_Bases clone named RAAF Base Learmonth (Bare Base), Exmouth WA, Nation=Australia, air group P-8A x4, U-2 x2, KC-135 x2. … |  | not researched: no web searches left / sites blocked |
| `airbase_raaf_pearce` | SEST_RAAF_Bases clone named RAAF Base Pearce (WA, training and P-8A forward base), Nation=Australia, air group F-35A x8, KC-46A x… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Pearce', Nation=Australia. There is no sourced figu… |
| `airbase_raaf_richmond` | SEST_RAAF_Bases clone named RAAF Base Richmond (NSW, air mobility base), Nation=Australia, air group KC-130T x6, MH-60R x2. Shipp… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Richmond', Nation=Australia. There is no sourced fi… |
| `airbase_raaf_scherger` | SEST_RAAF_Bases clone named RAAF Base Scherger (Bare Base), near Weipa on Cape York, Nation=Australia, air group F-35A x8, F-15EX… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Scherger (Bare Base)', Nation=Australia. The RAAF h… |
| `airbase_raaf_tindal` | SEST_RAAF_Bases clone named RAAF Base Tindal (near Katherine NT), Nation=Australia, air group F-35A x12, B-52H x4, B-2 x2, KC-135… | $147,000,000 / $473,000,000 | found, not confirmed: the checker had no searches left |
| `airbase_raaf_townsville` | SEST_RAAF_Bases clone named RAAF Base Townsville (Queensland), Nation=Australia, air group AH-64E x8, MH-60R x4, S-70B-2 x4, KC-1… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Townsville', Nation=Australia. There is no sourced … |
| `airbase_raaf_williamtown` | SEST_RAAF_Bases clone named RAAF Base Williamtown (NSW, F-35A and E-7A base), Nation=Australia, air group F-35A x24, E-7A x3. Fie… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Base Williamtown', Nation=Australia. An estate-wide gros… |
| `airbase_raaf_woomera` | SEST_RAAF_Bases clone named RAAF Woomera Airfield (South Australia, test range airfield), Nation=Australia, air group U-2 x2, MQ-… |  | no source found: The identity is confirmed: a SEST_RAAF_Bases clone named 'RAAF Woomera Airfield', Nation=Australia. There is no sourced… |
| `airbase_rnzaf_auckland` | SEST_RAAF_Bases clone named RNZAF Base Auckland (Whenuapai), Nation=New Zealand, added for Southern Reach (Kiwi 05 P-8A). Fielded… |  | no source found: Its mods-source file was not found; it is generated by SEST (docs/FEATURES.md lists Auckland among the named bases), an… |
| `airbase_rnzaf_ohakea` | SEST_RAAF_Bases clone named RNZAF Base Ohakea, Nation=New Zealand, added for Southern Reach as a New Zealand recovery field for t… |  | no source found: It is a SEST-generated named base, like Auckland. A programme capital cost for partial works is not a replacement figur… |
| `airbase_us` | Modern US Airbase (3592460366): generic template, Default 'U.S. Air Force Base', Variant1 'Eglin Air Force Base' (US), Variant2 '… |  | no source found: The identity is confirmed: in 3592460366 the Default is 'U.S. Air Force Base', Variant1 'Eglin Air Force Base' and Vari… |
| `airfield_a-10` | A-10 mod (3414146266) 'A-10 Airbase (USA)' (DisplayClassName Akureyri Airbase), Nation=US, air group F-15C x12, A-10A x12, P-3C x… |  | no source found: The identity is confirmed: 3414146266 'A-10 Airbase (USA)'. docs/campaigns/southern-watch/review-disposition.md shows i… |
| `airfield_small_1` | Vanilla small airfield ('Airbase - small'), variants USA, North Vietnam, PLAAF, PLAN and others, capacity 48. SEST uses it as a s… |  | no source found: The identity is confirmed: the vanilla 'Airbase - small', with USA, North Vietnam and other variants. It is used as a s… |
| `airfield_us` | MiG-29A & F-16A mod (3416372890) 'US aviation base' (DisplayClassName Akureyri Airbase), Nation=US, air group F-15C x12, F-16A x1… |  | no source found: The identity is confirmed: 3416372890 'US aviation base'. There is no sourced figure. |
| `china_large_airbase` | Red Storm Arsenal (3413868677) 'PRC Airbase' (PLAAF and PLAN variants); SEST_Collection_Fixes ships a corrected copy. Generic; no… |  | no source found: The identity is confirmed: 3413868677 'PRC Airbase', with PLAAF and PLAN variants. There is no sourced figure. |
| `civ_car_pickup_1983` | Pickup mod (3681873198) 'Technical': an unarmed 1983-style civilian pickup (4.9 m, cargo load, no weapon systems), MobileUnit, na… |  | not researched: no web searches left / sites blocked |
| `civ_car_pickup_1983_assault_civ` | Pickup mod (3681873198) 'Assault Technical': the same 1983 pickup carrying armed civilians (crew, AK-47 and RPG meshes); no weapo… |  | no source found: The identity is confirmed: 3681873198 'Assault Technical' ('Technical with Assault'). The riders are not part of the ve… |
| `civ_radiostation` | Vanilla 'Radiostation (Civilian)': a radio station with mast (LandUnitSubType Radar, Role Radar/ESM), Nation=US. Southern Reach u… |  | no source found: The identity is confirmed: vanilla 'Radiostation (Civilian)', subtype Radar. Installation is the right category for a c… |
| `civ_spar_rig` | Vanilla 'Oil Platform' (OilRig subtype; spar hull, two superstructures, accommodation house with helipad and drilling tower; desc… |  | not researched: no web searches left / sites blocked |
| `civ_spar_rig_helo` | Armed Oil Rig with helo (3403993583): an Iranian (or Iraqi) oil platform with a working helicopter deck and three weapon systems … |  | not researched: no web searches left / sites blocked |
| `coal_powerplant` | Buildings and Objectives (3600788156) 'Coal Power Plant' (Coal_PowerPlant.ini): a generic coal-fired power station, Installation,… | ? / $2,930,000,000 | found, not confirmed: the checker had no searches left |
| `fob` | Buildings and Objectives (3600788156) 'Forward Operating Base' (FOB.ini; green and desert variants): 'big enough for a few squads… |  | not researched: no web searches left / sites blocked |
| `nato_large_pvo_airbase1` | arrw mod (3502273861) large airbase whose layout is based on Olenegorsk/Olenya but whose names file calls it 'Barksdale Air Force… | ? / $3,950,000,000 | found, not confirmed: the checker had no searches left |
| `oil_pump` | Buildings and Objectives (3600788156) 'Oil Pump' (Oil_pump.ini): 'a single oil pump used by the hundreds in oil fields', i.e. a b… |  | not researched: no web searches left / sites blocked |
| `pla_airbase_modern` | Modern Chinese Airbase (3631042692) 'Modern Chinese airforce base', Variant1 'Wugong Air base'; SEST_Collection_Fixes ships a cor… |  | no source found: The identity is confirmed: 3631042692 'Modern Chinese airforce base', Variant1 'Wugong Air base'. There is no sourced f… |
| `plaaf_airlift_airbase` | Y-20 / KJ-3000 mod (3782020901) 'PLAAF Airlift Base'; SEST_Collection_Fixes ships a corrected copy. Generic; not fielded in a cam… |  | no source found: The identity is confirmed: 3782020901 'PLAAF Airlift Base'. There is no sourced figure. |
| `sest_uav_forward` | SEST_Allied_Fixes field UAV team site using FallschimJager705's Field Drone Squad model (3601891050): Airbase subtype, capacity 1… |  | no source found: SEST's docs describe this field UAV team site (docs/playtests/o10-field-team-preparation-20261020.md, docs/campaign-cov… |
| `tgt_ammo_depot_small` | Vanilla 'Ammo Depot' (temporary ammunition storage: buildings, cargo stacks and cranes), Installation that replenishes nearby uni… |  | no source found: The identity is confirmed: vanilla 'Ammo Depot' ('Ammo depot replenishes ammunition of nearby units.'). There is no sou… |
| `tgt_fueltanks_medium` | Vanilla 'Fueltanks Medium Depot' (industrial tank-farm module), Installation, Nation=Vietnam. Fielded in Southern Watch and sest-… |  | no source found: The identity is confirmed: vanilla 'Fueltanks Medium Depot'. With no capacity stated, no per-size figure can be applied. |
| `usa_airbase` | Red Storm Arsenal (3413868677) 'USA Airbase' (variants 'Naval Air Station' and 'Air Force Base'); SEST_Collection_Fixes ships a c… |  | no source found: The identity is confirmed: 3413868677 'USA Airbase', with variants 'Naval Air Station' and 'Air Force Base'. There is n… |
| `wp_airbase_modern` | Modern Russian Airbase (3629269283) 'Modern Russian airforce base', Variant1 'Engels airforce base'; SEST_Collection_Fixes ships … |  | no source found: The identity is confirmed: 3629269283 'Modern Russian airforce base', Variant1 'Engels airforce base'. It is used as a … |

## Ships (second attempt) (21)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `civ_humpback` | A humpback whale: a biological contact (UnitType=Submarine, Type=BIO, Nation=Unknown), Workshop 3384079999. It is fielded in Red … |  | not researched: no web searches left / sites blocked |
| `phl_ff_hamilton` | Philippine Navy Gregorio del Pilar (Del Pilar) class: ex-USCG Hamilton-class high-endurance cutters, built in the 1960s, 115 m, 3… |  | not researched: no web searches left / sites blocked |
| `phl_lpd_tarlac` | Philippine Navy Tarlac-class LPD (PT PAL, a Makassar-class derivative), 123 m, 11,583 t. ServiceDate 2017. SEST_Replenishment for… |  | not researched: no web searches left / sites blocked |
| `phl_pb_jose_andrada` | Philippine Navy Jose Andrada-class coastal patrol boat (Halter Marine, 22 boats ordered in the late 1980s), 24 m, 56 t. ServiceDa… |  | not researched: no web searches left / sites blocked |
| `phl_pt_jacinto` | Philippine Navy Emilio Jacinto class: ex-Royal Navy Peacock-class Hong Kong patrol corvettes (Hall Russell, 1983-84), 62.6 m, 645… |  | not researched: no web searches left / sites blocked |
| `plan_aor_type901` | PLAN Type 901 Fuyu-class fast combat support ship (CNS Hulunhu 965, Chaganhu 967). A SEST clone on the Sacramento hull as a model… |  | not researched: no web searches left / sites blocked |
| `plan_aor_type903a` | PLAN Type 903A Fuchi-class replenishment oiler (Taihu 889, Chaohu 890, Honghu 963, Luomahu 964). A SEST clone on the Boris Chilik… |  | not researched: no web searches left / sites blocked |
| `ran_aor_supply` | RAN Supply-class AOR (Navantia, Cantabria-derived). A SEST_RAN_Fleet clone on the Teide oiler as a model stand-in. ServiceDate 20… |  | not researched: no web searches left / sites blocked |
| `ran_ffh_anzac` | RAN Anzac-class (MEKO 200ANZ) FFH. A SEST_RAN_Fleet clone on the Type 23 MLU as a model stand-in, 4,900 t. ServiceDate 1996/2045. |  | not researched: no web searches left / sites blocked |
| `ran_lsd_choules` | HMAS Choules: an ex-RFA Largs Bay, Bay-class LSD(A), built 2006 and bought by Australia in 2011. A SEST_RAN_Fleet clone on the Ga… |  | not researched: no web searches left / sites blocked |
| `ran_opv_arafura` | RAN Arafura-class OPV (Luerssen OPV 80). A SEST_RAN_Fleet clone on the Meteoro BAM as a model stand-in. ServiceDate 2022/2060. |  | not researched: no web searches left / sites blocked |
| `ran_ssg_collins` | RAN Collins-class SSG (ASC, six boats). A SEST_RAN_Fleet clone on the S-80 Plus family as a model stand-in. ServiceDate 1996/2040. |  | not researched: no web searches left / sites blocked |
| `tha_aor_chula` | Royal Thai Navy Chula-class small coastal tanker (HTMS Chula 831, HTMS Matra 836), 67 m, 1,200 t. ServiceDate 1981/1982 (Workshop… |  | not researched: no web searches left / sites blocked |
| `tha_ff_makut_rajakumarn` | HTMS Makut Rajakumarn (433): a Yarrow-built frigate (Glasgow, 1971), 97.6 m, 1,900 t, original 1973 fit. ServiceDate 1973/1988. |  | not researched: no web searches left / sites blocked |
| `tha_ff_makut_rajakumarn_88` | The same HTMS Makut Rajakumarn after its 1985-88 modernisation. ServiceDate 1988. |  | not researched: no web searches left / sites blocked |
| `tha_fs_khamronsin` | Royal Thai Navy Khamronsin-class corvette: a Vosper design built in Thailand, 62 m, 630 t, three ships commissioned 1992. Service… |  | not researched: no web searches left / sites blocked |
| `tha_pt_chonburi` | Royal Thai Navy Chonburi-class gun patrol craft (Breda MV 400 type), 60.4 m, 450 t, two 76 mm guns. ServiceDate 1983. |  | not researched: no web searches left / sites blocked |
| `tha_pt_hua_hin` | Royal Thai Navy Hua Hin-class patrol gunboat (a modified Khamronsin design), 62 m, 645 t, commissioned 2002-2004. ServiceDate 200… |  | not researched: no web searches left / sites blocked |
| `tha_ptg_ratcharit` | Royal Thai Navy Ratcharit-class missile FAC: Breda-built, 270 t, MM38 Exocet, three boats. ServiceDate 1979/1980. |  | not researched: no web searches left / sites blocked |
| `usn_take_lewis_clark` | MSC Lewis and Clark-class T-AKE dry cargo/ammunition ship (T-AKE 1, 2, 6, 11). A SEST clone on the Kilauea AE as a model stand-in… |  | not researched: no web searches left / sites blocked |
| `usn_taoe_supply` | MSC Supply-class T-AOE fast combat support ship (T-AOE 6, 7, 8, 10). A SEST clone on the Sacramento AOE as a model stand-in. Serv… |  | not researched: no web searches left / sites blocked |

## Aircraft and SEST weapons (second attempt) (27)

| Id | What it is | Candidate (then / 2026) | Why not confirmed |
|---|---|---|---|
| `jasdf_ec-2` | Kawasaki EC-2 stand-off electronic warfare aircraft, converted from the first production C-2 transport. First flight 17 Mar 2026;… |  | not researched: no web searches left / sites blocked |
| `knm_terne_shell` | Terne III anti-submarine mortar round (Norway, Kongsberg): unguided, Type=RBU, TargetType=ASW, 135 kg in the SEST copy. Same cont… |  | not researched: no web searches left / sites blocked |
| `msdvd_tu-214r` | Tupolev Tu-214R strategic ELINT/SIGINT reconnaissance aircraft, flown in this mod as an EW variant (Russia; first flight 2009). |  | not researched: no web searches left / sites blocked |
| `phl_h-76` | Sikorsky AUH-76, the armed S-76 of the Philippine Air Force (12 delivered in 1983). Squadron2 of the same file is an AW109 LAH, s… |  | not researched: no web searches left / sites blocked |
| `pla_z21` | Z-21 attack helicopter (China, ServiceDate 2026, empty mass 5,500 kg); a new or near-concept type with no description in the mod. |  | not researched: no web searches left / sites blocked |
| `plaaf_j36` | Chengdu J-36 tailless three-engine stealth prototype (first flight Dec 2024, ServiceDate 2025). After normalisation it already ma… |  | not researched: no web searches left / sites blocked |
| `plaaf_jh7a` | Xi'an JH-7A Flying Leopard (Flounder) fighter-bomber, PLAAF/PLANAF. The JH-7 first flew in 1988 and the improved JH-7A was announ… |  | not researched: no web searches left / sites blocked |
| `plaaf_y-20a` | Xi'an Y-20A four-engine strategic transport (PLAAF), empty mass 100 t. |  | not researched: no web searches left / sites blocked |
| `plan_j-50` | 'J-50' concept sixth-generation stealth carrier fighter (China); no service date. |  | not researched: no web searches left / sites blocked |
| `raaf_f-35_gun_pod` | F-35 GAU-22/A 25 mm gun pod (Type=Container, 300 kg, holds 220 rounds of usn_cal_25mm_m2), hung on the SEST RAAF F-35A. The price… |  | not researched: no web searches left / sites blocked |
| `raaf_mq-4c_triton` | RAAF MQ-4C Triton HALE maritime ISR UAV, a new SEST unit (SEST_ADF_Persistent_ISR) cloned onto the MQ-9 ER mesh. The borrowed mes… |  | not researched: no web searches left / sites blocked |
| `rn_squid_shell` | Royal Navy Squid ahead-throwing ASW mortar bomb (1940s): unguided, Type=RBU, 200 kg in the SEST copy. |  | not researched: no web searches left / sites blocked |
| `sest_agr-30_pod` | SEST 7-tube 70 mm rocket pod (LAU-68 class) for the fictional AGR-30 Redback. Type=Container, 10 kg. Carried by the S-70B-2, A-10… |  | not researched: no web searches left / sites blocked |
| `sest_agr-30_pod19` | SEST 19-tube 70 mm rocket pod (LAU-61/LAU-3/M261 class) for the AGR-30 Redback. Type=Container, 10 kg. Carried by the MH-60R, A-1… |  | not researched: no web searches left / sites blocked |
| `sest_aim-424` | SEST's AIM-424 MALICE long-range AAM (680 kg). Its flight model is aligned with usn_aim-174b. It is fitted to the RAAF F-35A, F-3… |  | not researched: no web searches left / sites blocked |
| `usa_mv75_army` | Bell MV-75 Cheyenne II (FLRAA, developed from the V-280 Valor), US Army; pre-production/LRIP. ServiceDate 2019/2050. |  | not researched: no web searches left / sites blocked |
| `usaf_kc-10a_extender` | McDonnell Douglas KC-10A Extender, a DC-10-30-derived USAF tanker/transport (ServiceDate 1980-1985 squadrons). |  | not researched: no web searches left / sites blocked |
| `usaf_kc-46a_boom` | Boeing KC-46A Pegasus (boom-only fit), a 767-derived USAF tanker; fielded in five SEST missions. |  | not researched: no web searches left / sites blocked |
| `usaf_rq-180` | Fictional carrier-capable unmanned combat derivative of the classified, unconfirmed RQ-180 HALE flying wing (ServiceDate 2010/). |  | not researched: no web searches left / sites blocked |
| `usaf_yf-23_black_widow_ii` | Northrop YF-23 ATF prototype (first flight 1990), recast as a fictional carrier fighter ('the path not taken'). |  | not researched: no web searches left / sites blocked |
| `usmc_ch53_standalone` | Sikorsky CH-53E Super Stallion (USMC livery) in a fictional mission conversion (anti-ship/ASW stores such as ch53sa_nsm_air and a… |  | not researched: no web searches left / sites blocked |
| `usn_fury_escort` | Anduril FQ-44 Fury escort version: a fictional US Navy carrier version of the USAF YFQ-44A CCA Increment 1 (first flight 31 Oct 2… |  | not researched: no web searches left / sites blocked |
| `usn_fury_ew` | Anduril FQ-44 Fury EW version: a fictional unarmed US Navy carrier CCA carrying a directional jammer and ELINT receivers. Service… |  | not researched: no web searches left / sites blocked |
| `usn_ssq-47` | AN/SSQ-47 JULIE range-only active sonobuoy (US Navy, 1960s era). Type=Sonobuoy, 10 kg in mod 3628203171 (16.3 kg in the SEST copy… |  | not researched: no web searches left / sites blocked |
| `usn_tank_1200_f-18` | 'F/A-18E/F Center Mount Tank': a notional 1,200 US gal centreline drop tank (Fuel=4500 kg) drawn with the F-15C 610 gal tank mesh… |  | not researched: no web searches left / sites blocked |
| `usn_tank_610_f-18` | 'F/A-18E/F Fuel Tank': the Super Hornet's underwing or centreline external drop tank (Fuel=1800 kg; the '600 gallon / F-4D' comme… |  | not researched: no web searches left / sites blocked |
| `wp_mig-31bm` | MiG-31BM Foxhound interceptor (Russia, ServiceDate 2012): a modernisation of existing MiG-31 airframes. |  | not researched: no web searches left / sites blocked |

