# Sea Power Mod Catalog

133 subscribed Workshop mods, grouped by faction. Generated from `data/mod-catalog.json` by `tools/generate_catalog.py` — edit the JSON, not this file.

See `docs/conflicts-and-load-order.md` for the conflict watchlist, dependency audit, and recommended mod order.

## United States (37)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Modern US Airbase | King_Achilles_Berlin | airbase | Airbase with modern US jets and helicopters. Author lists 'Integrated Aircrafts' (AC-130J, A-10, AV-8A, F-15C, F/A-18F, F-22, F-35C, B-52G, B-1, F-117, B-2, E-3, MQ-9, VH-3D, AH-64...) — unclear whether these are bundled into the mod or referenced from other mods (the F-15C matches no subscribed mod). If referenced, its F-35C / F/A-18F could point at the deprecated MyGo standalones — verify before unsubscribing those. Recommendation: keep below the aircraft mods. |
| <<E-3G>> | SKIBIDI_RIZZLER123 | fixed-wing | USAF E-3 Block 40/45 AWACS upgrade. |
| [DEPRECATED] Boeing F/A-18E/F Super Hornet ⚠️ **DEPRECATED** | MyGo!!!!!鼓手椎名立希 | fixed-wing | Integrated into Modern US Navy. Unsubscribe candidate — BUT F/A-18 Murder Hornet targets the E/F; verify compatibility before removing. |
| [DEPRECATED] Lockheed Martin F-35C Lighting II ⚠️ **DEPRECATED** | MyGo!!!!!鼓手椎名立希 | fixed-wing | Integrated into Modern US Navy. Unsubscribe candidate — BUT F-35C Alt. Loadouts was written against THIS mod; verify compatibility before removing. |
| A-10A Thunderbolt II | misaka | fixed-wing | Author: 'Need SeaLifter, if unable to open, please ensure that SeaLifter is installed correctly.' **Requires:** sealifter |
| A-10C | misaka | fixed-wing | Based on the A-10A mod; adds GBU-31/38/39, AIM-9M, GBU-10/12, Litening and ALQ-184 pods. **Requires:** a-10a (inferred from 'Based on A-10A mod'); sealifter (presumed via A-10A) |
| B-1B Lancer | dingtools | fixed-wing | Supersonic variable-sweep heavy bomber. **Load order:** Keep Dingtools Weapon Pack ABOVE all dingtools mods |
| B-2 Spirit | Stroh Vogel | fixed-wing | Author: 'Requires AnchorChain and SeaLifter to be correctly installed. Subscribing isn't enough. You need the preloader.' **Requires:** anchor-chain; sealifter |
| B-52H Stratofortress | dingtools | fixed-wing | Long-range strategic bomber, TF33 engines. **Load order:** Keep Dingtools Weapon Pack ABOVE all dingtools mods **Overlaps:** b-52g-agm-86 (both carry AGM-86-family ALCM data) |
| F-117 Nighthawk | misaka | fixed-wing | Stealth attack aircraft with GBU-31. |
| F-15 EX Eagle II | dingtools | fixed-wing | 4.5-gen F-15 variant. **Load order:** Keep Dingtools Weapon Pack ABOVE all dingtools mods |
| F-15E StrikeEagle | dingtools | fixed-wing | Adds the F-15E: 2 aircraft plus 3 new ammunition files. Its other 8 shipped files are deliberately outranked by the Dingtools Weapon Pack and F-15SE, which is the author-mandated arrangement - placed below both so the shared dts_ ammunition (including the anaaq-13 pod the SEST F-15EX uses) keeps coming from the weapon pack. **Overlaps:** dingtools-weapon-pack (7 dts_ ammunition files); f-15-ex-eagle-ii (dts_anaaq-13 targeting pod) |
| F-16C Fighting Falcon (modern) | Zero Two | fixed-wing | Multiple modern F-16C blocks. **Overlaps:** apex-predators-mig-29-f-16 (different F-16 generation, complementary) |
| F-22 Raptor | misaka | fixed-wing | Fifth-generation air-superiority fighter. |
| KC-135 STRATOTANKER | SKIBIDI_RIZZLER123 | fixed-wing | USAF aerial refueling tanker, Vietnam era to modern. **Overlaps:** kc-46a; kc-10a (US tanker overlap — complementary types) |
| KC-46A Pegasus - Strategic Tanker | Zero Two | fixed-wing | Modern USAF tanker, dual-configuration package. **Overlaps:** kc-135; kc-10a (US tanker overlap — complementary types) |
| Lockheed AC-130 Pack | MyGo!!!!!鼓手椎名立希 | fixed-wing | AC-130 gunship family. |
| McDonnell Douglas KC-10A Extender - Strategic Tanker | Zero Two | fixed-wing | Cold War and modern USAF tanker configurations. **Overlaps:** kc-135; kc-46a (US tanker overlap — complementary types) |
| U-2 "Dragon Lady" | ManeuverWarfare | fixed-wing | Modern and 1960s U-2 models plus a Chinese weather/spy balloon. Kitbashes; explicitly do NOT require SeaLifter or third-party software. |
| United States Naval Aviation | misaka | fixed-wing | US Naval Aviation pack (SH-60B/F, HH-60H, MH-60R and more); presented jointly by Sea Power China Test Group & Euromod. **Overlaps:** modern-us-navy (helicopters/aircraft); mh-60r-2154545636 |
| Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included) | Obiwonkanblomi | land | Anti-ballistic-missile system with AN/TPY-2 radar. **Overlaps:** sam-pack (US air defense overlap) |
| Air Deck Operations Upgrade - Nimitz (2000s) | sgtobliterator | patch | Deck-ops upgrade applied to F/A-18 and the Nimitz (2000s); adds deck models and MH-60R. Long carrier load time. Verify it does not fight Flight Deck Ops over the same carrier files. Wording ('adds the Air Deck Operations Upgrade to... the Nimitz (2000s)') suggests it may be an APPLICATION of the ADO/FDO mod rather than a competitor — verify whether it depends on Flight Deck Ops before treating the pair as pick-one. **Overlaps:** flight-deck-ops; nimitz-expanded |
| B-52G with AGM-86 (realistic nuke) | aaaaaaaaaaaaaaaabcd | patch | Adds 8 loadouts to the VANILLA B-52G; adds AGM-86B/C plus fictional anti-ship AGM-86E variants. Modifies vanilla unit — load-order sensitive. **Overlaps:** b-52h (both carry AGM-86-family ALCM data) |
| F-35C Lightning II Alt. Loadouts | Prof_CH4OS | patch | Adds loadout variants, GPS datalink, AN/APG-81 offensive ECM to the MyGo F-35C. Its target is deprecated — needs retargeting/verification against Modern US Navy's F-35C. Top integration-fix candidate. Recommendation (not author instruction): keep above its target F-35C mod. **Requires:** f-35c-mygo (deprecated — now integrated into Modern US Navy; compatibility unverified) |
| F/A-18 Murder Hornet with AIM-174B | Cropgun | patch | Adds Murder Hornet loadouts, AIM-174B, AIM-9X, AIM-120D, AGM-84D, JDAMs/GBU-24 (F model); canopy and afterburner fixes. Its target F/A-18E/F mod is unconfirmed (candidates: the deprecated MyGo standalone, or Modern US Navy's integrated Super Hornet) — identify it before unsubscribing the MyGo pair. Recommendation: keep above whichever F/A-18 mod it targets. **Requires:** an F/A-18E/F source (inferred — the author names no target mod; E/F models implied by 'Fixed Green Canopy on E Model' / 'GBU-24 to F model') |
| Flight Deck Ops | ossesek | patch | Renamed continuation of the Air Deck Operations upgrade ('Formerly, the FDO was known as the Air deck operations upgrade'): activates all elevators, simultaneous launch/recovery, reworked taxi/landing paths and deck crew. **Overlaps:** ado-nimitz-2000s; nimitz-expanded (its eight hulls likely clone the Nimitz data both deck mods override) |
| U.S. Navy 2027 Capabilities mod | Prof_CH4OS | patch | Compilation of edits to many US Navy mods to reflect near-real capabilities. Highly load-order sensitive; overlaps with Dingtools Weapon Pack and Murder Hornet on modern US weapons. Recommendation (not author instruction): keep above the mods it modifies; if its edits touch weapons also defined by Dingtools Weapon Pack, it must sit above that pack too — test. **Requires:** the US Navy mods it edits (compilation of edits to multiple Workshop mods) |
| AH-64 Apache | misaka | rotary | Attack helicopter. |
| MH-60R Seahawk | 2154545636 | rotary | Standalone MH-60R. FOUR sources of MH-60-family helicopters in this list — duplicate/ID-conflict watch. **Overlaps:** us-naval-aviation (MH-60R); modern-us-navy (MH-60); ado-nimitz-2000s (adds MH-60R) |
| VH-3D Marine One MOD | plasm@n | rotary | Presidential transport helicopter. Workshop ID 3478767194. |
| Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies) | ManeuverWarfare | ship | UPDATE 2026-08-11: now requires Modern US Navy for its F-35, F/A-18 and MH-60 air wing (replacing previous third-party aircraft dependencies). **Requires:** modern-us-navy |
| Modern US Navy | Mitchell600 | ship | Arleigh Burke, Wasp, Freedom LCS, Zumwalt and more; now also includes the F-35C, F/A-18E/F and MH-60 (absorbed the MyGo aircraft mods). Required by Ford-class CVN. **Overlaps:** us-naval-aviation (SH-60/MH-60 family); mh-60r-2154545636; ado-nimitz-2000s (MH-60R); f-35c-alt-loadouts and murder-hornet (patch targets after the MyGo integration) |
| Nimitz Expanded | Username | ship | Adds the last eight Nimitz-class carriers with custom hull numbers and liveries. **Overlaps:** ado-nimitz-2000s; flight-deck-ops (both override Nimitz-class deck/data its eight hulls likely clone) |
| Virginia-, Seawolf-, and Ohio-class Submarines | ManeuverWarfare | submarine | Ohio SSBN/SSGN, Seawolf and Jimmy Carter, Virginia (incl. dry deck shelter version) kitbashes. |
| General Atomics MQ-9 Reaper | MyGo!!!!!鼓手椎名立希 | uav | Armed reconnaissance UAV. |
| ARRW (AGM-183) |  | weapons | Workshop 3502273861. Adds its OWN AGM-183 ammunition - it does NOT collide with the Dingtools Weapon Pack's dts_agm-183a that the F-15EX Strike183 fits use. Verified with tools/check_mod_conflicts.py: zero whole-file collisions. |
| Dingtools Weapon Pack | dingtools | weapons | Standalone weapon data pack: AIM-9X, AIM-120B/C/C-7/D-3, AIM-260A, GBU series and more. **Load order:** Author: 'Put this mod ABOVE any of my mod' (B-52H, F-15EX, B-1B, SAAB AEW&C) **Overlaps:** us-navy-2027; murder-hornet (all define modern US missiles like AIM-9X / AIM-120D — duplicate weapon-ID watch) |

## Russia / USSR (28)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Modern Russian Airbase (Large) | flankymanga | airbase | Airbase populated from other authors' Russian aircraft mods; mission makers advised to trim aircraft counts. Recommendation (not author instruction): keep below the aircraft mods it references. **Requires:** (inferred) the Russian aircraft mods it references — author credit line says the planes 'belong to their respective authors' |
| <<Tu-16N>> | SKIBIDI_RIZZLER123 | fixed-wing | Probe-and-drogue tanker for Tu-22/Tu-22M, in service 1963. |
| IL-78 TANKER | SKIBIDI_RIZZLER123 | fixed-wing | Il-78 aerial refueling tanker. |
| MIG-29 Family | unknown (added 2026-08-24) | fixed-wing | MiG-29 variant family pack; actively updated. VERIFIED: MiG-29 variants PLUS a carrier — wp_cv_orel_1991 (Soviet CV Orel) — bonus flattop for the red side. **Overlaps:** apex-predators-mig-29-f-16; mig-35 (MiG-29 lineage — now THREE sources); R-series AAM definitions likely duplicated across Russian fighter mods (multiple authors) |
| MiG-35 Fulcrum-F (米格-35 支点-F) | 2154545636 | fixed-wing | Multirole 4th-gen fighter, final MiG-29 evolution. **Overlaps:** apex-predators-mig-29-f-16 (different MiG-29 generation, complementary); R-series AAM definitions likely duplicated across Russian fighter mods (multiple authors) |
| MORE SU-24M VARIANTS | SKIBIDI_RIZZLER123 | fixed-wing | Su-24M2 and other modernized Fencer variants. |
| Soviet AEW&C + Transport Aircraft (A-50 / Il-76) | Zero Two | fixed-wing | A-50 Mainstay (3 liveries), modernized A-50U, Il-76 transport. |
| Su-25 Frogfoot | misaka | fixed-wing | Close air support aircraft. Author: 'Need SeaLifter'. **Requires:** sealifter |
| Su-30SM2 | SKIBIDI_RIZZLER123 | fixed-wing | Modernized twin-seat Su-30 multirole fighter. **Overlaps:** flanker-family (related Flanker airframes); R-series AAM definitions likely duplicated across Russian fighter mods (multiple authors) |
| SU-57 Felon (重刑犯) | 2154545636 | fixed-wing | Fifth-generation stealth fighter; includes an Su-57 airbase land unit. **Overlaps:** R-series AAM definitions likely duplicated across Russian fighter mods (multiple authors) |
| Sukhoi Flanker Family (苏霍伊侧卫家族) | MyGo!!!!!鼓手椎名立希 | fixed-wing | Su-27 Flanker family pack. **Overlaps:** su-30sm2; su-27ubk; j-11; j-11bs; j-16a (Flanker airframes across mods); R-series AAM definitions likely duplicated across Russian fighter mods (multiple authors) |
| TU-160 Blackjack | 2154545636 | fixed-wing | Supersonic variable-sweep strategic bomber. |
| Tu-214R Family (图-214R家族) | 鸣山 | fixed-wing | Tu-214 special-mission family: reconnaissance, EW, AEW&C, ASW patrol variants. |
| Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke) | aaaaaaaaaaaaaaaabcd | fixed-wing | Tu-95MS with FAB-500 or up to 14 AS-15; nuclear and fictional anti-ship derivatives. WARNING: 'Changes to Munitions with VeryLarge impact size' — a global data edit that can conflict with other weapon mods. **Overlaps:** tu-95ms-x-101 (both add Tu-95MS variants); tu-95k-22 |
| Tu-95K-22 Bear G MOD | plasm@n | fixed-wing | Bear G rebuild with Kh-22 (AS-4 Kitchen) missiles. Workshop ID 3411341227. (User re-subscribed 2026-08-24 — same Workshop item, no change.) **Overlaps:** tu-95-as-15; tu-95ms-x-101 |
| Tu-95MS (X-101) | SKIBIDI_RIZZLER123 | fixed-wing | Tu-95MS with Kh-101 (AS-23 Kodiak) stealth cruise missiles. **Overlaps:** tu-95-as-15 (both add Tu-95MS variants); tu-95k-22 |
| Iskander TBM | unknown (added 2026-08-24) | land | 9K720 Iskander tactical ballistic missile launcher. VERIFIED: adds wp_ss-26_tel. |
| SA-21/S-400 SAM | unknown (added 2026-08-24) | land | Russian strategic SAM system; joins the land air-defense watchlist. VERIFIED: adds wp_sa-21_* TELs (9M96E/E2 and more). **Overlaps:** sam-pack and ground-upgrade-spaa (land air-defense overlap watch) |
| SCUD-B | unknown (added 2026-08-24) | land | R-17 Elbrus TBM launcher (Cold War era). VERIFIED: adds wp_scud_9k72. |
| Ka-27RLD | Filip7370 | rotary | Soviet-liveried Ka-31 AEW helicopter (standalone); model credit to the Modern PLAN mod's Ka-31. |
| Mi-8 T/TV | misaka | rotary | Transport/armed transport Hip. Author: 'Need SeaLifter'. **Requires:** sealifter **Overlaps:** mi-8ew (different variant, complementary) |
| Mi-8EW | boli | rotary | EW variant proxied from the Mi-14 in game; Azaliya OECM jammer and detection sensor. **Overlaps:** mi-8-t-tv (different variant, complementary) |
| Mil Mi-24 Hind | MyGo!!!!!鼓手椎名立希 | rotary | Helicopter gunship / assault transport. |
| 1143.5 Kuznetsov | MyGo!!!!!鼓手椎名立希 | ship | Admiral Kuznetsov carrier; ski jump still in testing per author. Sister design of the Liaoning (Project 1143.5/6 family) — different navy, different author, no conflict expected. |
| Kirov-class (Pyotr Velikiy Upgrade) | unknown (added 2026-08-24) | ship | Modernized Pyotr Velikiy battlecruiser refit. VERIFIED 2026-08-24: adds new unit wp_rkr_kirov_improved — additive, no vanilla collision. **Overlaps:** vanilla Kirov-class variants (check for shared unit ids/files) |
| Russian Navy 21 | Pointinthevoid | ship | Projects 20380/20385/21631 corvettes, 11356/22350 frigates, 21956 destroyer, 11780 LHA. |
| Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes) | ManeuverWarfare | submarine | Yasen, Akula, Borei, Oscar II, Belgorod, Sierra I/II, Typhoon, Delta IV kitbashes. |
| 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala) | SKIBIDI_RIZZLER123 | weapons | Soviet experimental long-range strategic cruise missile (Meteorit program, authorized 1976). |

## China (PLA/PLAN/PLAAF) (21)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Modern Chinese Airbase (Large) | flankymanga | airbase | Airbase populated from other authors' Chinese aircraft mods. Recommendation (not author instruction): keep below the aircraft mods it references. **Requires:** (inferred) the Chinese aircraft mods it references — author credit line says the planes 'belong to their respective authors' |
| ChengDu J-10C Vigorous Dragon | 东武藏境 | fixed-wing | PLAAF multirole fighter; also exported (J-10CE). **Overlaps:** PL-series AAM definitions likely duplicated across Chinese fighter mods (multiple authors) |
| J-20 (歼-20 威龙) | 2154545636 | fixed-wing | Fifth-generation stealth air-superiority fighter. **Overlaps:** PL-series AAM definitions likely duplicated across Chinese fighter mods (multiple authors) |
| PLA Shenyang J-11BS | Not Allaaaan | fixed-wing | Twin-seat localized Flanker-B+ development. **Overlaps:** j-11; flanker-family; su-27ubk (Flanker airframes) |
| PLA Sukhoi Su-27UBK | Not Allaaaan | fixed-wing | PLA twin-seat Flanker-C trainer/fighter. **Overlaps:** flanker-family; j-11; j-11bs (related Flanker airframes) |
| Shenyang J-11 | misaka | fixed-wing | PLA heavy twin-engine fighter based on Su-27SK. **Overlaps:** j-11bs; flanker-family; su-27ubk (Flanker airframes) |
| Shenyang J-16A (歼-16A 潜龙) | kisa希罗 | fixed-wing | Multirole twin-seat strike Flanker derived from J-11B; performance largely estimated by author. **Overlaps:** flanker-family; j-11; j-11bs (related Flanker airframes); PL-series AAM definitions likely duplicated across Chinese fighter mods (multiple authors) |
| Shenyang J-50 (沈阳航空工业 歼-50) | 2154545636 | fixed-wing | Speculative sixth-generation stealth carrier fighter (2030s); comes with PL-10/15/16/17, LD-8a ARM, LS-6 glide bomb, TL-20 weapons. **Overlaps:** PL-series AAM definitions likely duplicated across Chinese fighter mods (multiple authors) |
| Shenyang J-8 | misaka | fixed-wing | High-altitude, high-speed interceptor. |
| XIAN JH-7A (歼轰-7A 飞豹) | 东武藏境 | fixed-wing | Twin-engine two-seat supersonic fighter-bomber, in PLAAF service 2005. **Overlaps:** PL-series AAM definitions likely duplicated across Chinese fighter mods (multiple authors) |
| Y-20 / KJ-3000 | ManeuverWarfare | fixed-wing | Y-20A transport, YY-20A tanker, Y-20B, KJ-3000 AEW&C. |
| Y-8/Y-9 Special Mission Aircraft Family | misaka | fixed-wing | Re-subscribed 2026-08-26. FULLY REDUNDANT with PLAN Pack (3775128499): all 12 of its aircraft files and every one of its ammunition files are shipped there too, so seated directly BELOW PLAN Pack every file it ships is outranked and it loads nothing. Kept because the user re-subscribed it deliberately; harmless in this position. Its only content difference is the KJ-500's Morden_RWR sensor, which PLAN Pack's version does not carry. Historical note: unsubscribed once as the suspected cause of the duplicate-key crash on quit - that crash was later traced to a mission aircraft with no resolvable default loadout, not to this mod. |
| Modern PLAN Systems | 八一of军魂 | framework | 2020s-era PLAN sensors and armaments database; same author as Fujian CV-18. Analogue of Euromod Main for the Chinese fleet. No author placement instruction; recommendation: keep above PLAN ship mods if it acts as a shared systems database (this framework role is itself inferred). |
| PLA Land Unit Pack | misaka | land | PLA air defense (Tor-M1, HQ-17/17A, PGZ-09, HQ-6, LD-2000, HQ-7...) and other land units. Author suggests unsubscribing separate HQ-9&HQ-7 / HQ-6A / DF-15 mods — none of those are in this list, so no action needed. **Load order:** Author: 'Place this mod above any other PLA-related mods in Mod Manager' **Overlaps:** sam-pack (air defense overlap) |
| AVIC HARBIN Z-21 | Meltemi | rotary | Speculative Chinese heavy attack helicopter based on the Z-20 platform. |
| Chinese Navy (PLAN) | ltjgbeam | ship | Fujian-class carrier, Hangzhou-class (Sovremenny), Luda Type 051. One of THREE Fujian carriers in this list. **Overlaps:** type-003-004-maneuverwarfare (Fujian); fujian-cv-18 (Fujian) |
| PLAN Type 001 Aircraft Carrier Liaoning | Meltemi | ship | STOBAR carrier CV-16. Sister design of the Kuznetsov (Project 1143.5/6 family) — different navy, different author, no conflict expected. |
| PLAN Type 071 Amphibious Transport Dock | Meltemi | ship | Yuzhao-class LPD; mothership for air-cushion landing craft. |
| Type 003 Aircraft Carrier - PLANS Fujian CV-18 | 八一of军魂 | ship | Fujian with multiple selectable loadouts. One of THREE Fujian carriers in this list — same author as Modern PLAN Systems; likely pairs with it. **Overlaps:** type-003-004-maneuverwarfare (Fujian); chinese-navy-plan (Fujian) |
| Type 003 Fujian / Type 004 CVN Aircraft Carriers | ManeuverWarfare | ship | Kitbash Fujian plus speculative Type 004. One of THREE Fujian carriers in this list — pick a primary. **Requires:** sealifter; anchor-chain **Overlaps:** chinese-navy-plan (Fujian); fujian-cv-18 (Fujian) |
| PLAN Submarines | ManeuverWarfare | submarine | Type 039G Song, 039A/B/C Yuan, Type 093/093A Shang kitbashes. |

## Europe (multinational / Euromod) (11)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Eurofighter Typhoon | misaka | fixed-wing | European multinational multirole fighter. |
| SAAB AEW&C PACK | dingtools | fixed-wing | Saab AEW&C aircraft (GlobalEye/Erieye family); author notes future updates postponed. **Load order:** Keep Dingtools Weapon Pack ABOVE all dingtools mods |
| Euromod - Anchorchain Expansion Pack | Euromod team | framework | Extends the Anchor Chain framework: three systems files plus ammunition_overwrite/language_overwrite folders (Anchor Chain's own patching mechanic) and a welldeck config. No whole-file collision with anything; placed directly under Anchor Chain so the framework and its expansion stay together. **Requires:** anchor-chain |
| Euromod - Main Pack | Mitchell600 | framework | Shared database of European weapons and sensors. The Euromod dependency is explicitly stated by 5 of the 8 addons in this list (Nordic, Dutch, German, British, Cold War Spanish) and inferred for the other 3 (Italian, JMSDF, Modern Spanish). No author placement instruction; recommendation: keep above all Euromod addons. |
| Royal Navy Westland Lynx HAS.3 Kitbash [OLD] ⚠️ **DEPRECATED** | unknown (added 2026-08-24) | rotary | Tagged [OLD] by its author. VERIFIED: adds rn_lynx AND rn_wildcat — the Wildcat is not in the Sea Lynx pack, which is a reason to keep this despite the tag. **Overlaps:** sea-lynx; french-helicopter-package; euromod-german (Lynx family — now FOUR sources) |
| Sea Lynx | petrouvis01 | rotary | Five Lynx variants: UK, Netherlands, West Germany, France, and more. **Overlaps:** french-helicopter-package (French Navy operated the Lynx — likely a second Lynx source); euromod-german (F123 frigates embark the Super Sea Lynx Mk88A) |
| Euromod - Modern British Navy | 5_12 | ship | Modern Royal Navy addon; author: 'requires Euromod to work as intended'. **Requires:** euromod-main |
| Euromod - Modern Dutch navy | Mitchell600 | ship | De Zeven Provinciën-class LCF AAW frigates (incl. midlife upgrade). **Requires:** euromod-main |
| Euromod - Modern German Navy | Chevron 9 | ship | Type 212A sub, F123, F124, F125 frigates. **Requires:** euromod-main **Overlaps:** sea-lynx (Super Sea Lynx Mk88A on F123) |
| Euromod - Modern Nordic Navy | Mitchell600 | ship | Iver Huitfeldt frigate, Visby corvette (V5/V6), Skjold corvette. **Requires:** euromod-main |
| Royal Navy Type 23 'Duke Class' Frigate [OLD] ⚠️ **DEPRECATED** | unknown (added 2026-08-24) | ship | Tagged [OLD] by its author. VERIFIED 2026-08-24: uses its OWN unit ids (rn_type23, rn_type23_refit) and shares no asset paths with the Euromod British pack — it is additive, NOT a conflict, and no threat to the SEST RAN Anzac clone. Keep or drop purely for menu tidiness. **Overlaps:** euromod-british (redundant Type 23 hulls under different unit ids — clutter, not conflict) |

## France (4)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Dassault Rafale | misaka | fixed-wing | French multirole carrier and land-based fighter. |
| French Army Vehicles | LLinqs | land | Leclerc XLR, VBCI, Jaguar, AMX-10, Griffon, Serval, VBL, VAB, M270 LRU, CAESAR, SAMP/T NG, VLFS. **Overlaps:** sam-pack and ground-upgrade-spaa (SAMP/T NG is a land SAM inside the air-defense overlap watch) |
| French Helicopter Package | misaka | rotary | French Air Force / Navy / ALAT helicopters for assault, fire support, ASW, anti-surface roles. **Overlaps:** sea-lynx (Lynx variants) |
| Charles De Gaulle & Modern French Navy Pack (WIP) 🚧 WIP | LLinqs | ship | CVN Charles de Gaulle and modern French Navy vessels; marked WIP. |

## Italy (2)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Euromod - Modern Italian Navy | Mitchell600 | ship | Modern Italian Navy addon for Euromod. **Requires:** euromod-main (inferred from Euromod addon naming; not stated in the truncated description) |
| Italian Navy Mod | zzocalu | ship | Cold War Italian Navy (post-WW2 through 1960s buildup). **Overlaps:** euromod-italian-modern (different era, complementary) |

## Spain (2)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Euromod - Cold War Spanish Navy | zzocalu | ship | Cold War Spanish Navy addon; author: 'you must have Euromod downloaded and activated'. **Requires:** euromod-main |
| Euromod - Modern Spanish Navy | jabeitor | ship | Modern Spanish Navy addon for Euromod. **Requires:** euromod-main (inferred from Euromod addon naming; not stated in the truncated description) |

## Japan (3)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Type 12 SSM-ER Anti-Ship Missile System | FallschimJager705 | land | JGSDF mobile shore-based anti-ship missile system; base and ER (900 km) variants. |
| Euromod - Modern Japanese Maritime Self Defence Force | Mitchell600 | ship | Modern JMSDF addon for Euromod. **Requires:** euromod-main (inferred from Euromod addon naming; not stated in the truncated description) |
| Mogami-class Frigate | unknown (added 2026-08-24) | ship | JMSDF stealth multirole frigate; natural companion to Euromod JMSDF. VERIFIED: adds js_ffg_mogami. **Overlaps:** euromod-jmsdf (complementary — check for shared JMSDF weapon/sensor definitions) |

## Australia (4)

| Mod | Author | Type | Notes |
|---|---|---|---|
| [DEPRECATED] E-7A Wedgetail ⚠️ **DEPRECATED** | Pog Frog | fixed-wing | RAAF AEW&C, Boeing 737 NG with MESA radar. Marked deprecated by author — unsubscribe candidate. |
| RAAF F-35A Lighting II | Greene | fixed-wing | RAAF fifth-generation multirole stealth fighter. **Overlaps:** modern-us-navy (F-35C — different variant, complementary; possible shared weapon data only) |
| [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles ⚠️ **DEPRECATED** | Pog Frog | rotary | RAN ASW/ASST Seahawk. Marked deprecated by author — unsubscribe candidate. Description body still says 'currently WIP' — the text may predate the [DEPRECATED] title; confirm current state before unsubscribing. |
| Auxilliary Merchant Pack | unknown (added 2026-08-24) | ship | VERIFIED: AUSTRALIAN auxiliary shipping — ran_ms_bulk, ran_msa_act_1, anl_ms_bulk (ANL = Australian National Line). Direct fit for RAN convoy/escort scenarios alongside SEST_RAN_Fleet. **Overlaps:** merchants-expanded (two merchant packs — check for duplicate hulls) |

## Iran (3)

| Mod | Author | Type | Notes |
|---|---|---|---|
| SEJJIL (Iran Ballistic Missiles) | unknown (added 2026-08-24) | land | Iranian MRBM systems. VERIFIED: adds wp_sejjil_tel. |
| Shahed-136 Drone | Obiwonkanblomi | uav | Second Shahed-136 mod; speed fixed at 120 mph; borrows the launcher truck from Zero Two's mod. Redundant with the Zero Two version — pick one. UNSUBSCRIBED by user 2026-08-24 (runbook Phase 2). **Overlaps:** shahed-136-zero-two |
| Shahed-136 Kamikaze Drone (Geran-2) | Zero Two | uav | Land-launched one-way attack drone; black and white variants, two launcher land units. Richer of the two Shahed mods. **Overlaps:** shahed-136-obiwonkanblomi |

## Multi-nation packs (10)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Apex Predators MIG-29A & F-16A | misaka | fixed-wing | Cold War MiG-29A and F-16A pair. **Overlaps:** f-16c-modern (different F-16 generation, complementary); mig-35 (different MiG-29 generation, complementary) |
| Boeing P-8 Poseidon | Kirameki | fixed-wing | Custom-model P-8 with full weapon suite incl. modeled HAAWC; USN, Indian Navy, RAAF liveries. |
| Armed Oil Rig with Helo MOD | unknown (added 2026-08-24) | land | Offshore platform installation with helipad — scenario objective piece. VERIFIED: adds civ_spar_rig_helo installation. |
| David's Sling |  | land | Workshop 3558173926. Israeli SAM battery: 4 land units plus its own ammunition. Zero whole-file collisions. |
| Pickup truck extension | unknown (added 2026-08-24) | land | Technicals / light vehicle extension. VERIFIED: adds civ_car_pickup_1983 variants (incl. armed/medic). |
| SAM Pack | misaka | land | Surface-to-air missile systems pack (incl. MIM-104 Patriot). **Load order:** Author: 'Need on the top of TOE' — place at the top of the mod order **Overlaps:** ground-upgrade-spaa; thaad; pla-land-unit-pack (air defense overlap) |
| Ground Upgrade: SPAA | misaka | patch | Refines ground-unit models and MODIFIES values of some weapons and units — load-order sensitive; watch for overlap with SAM Pack and land unit packs. |
| RE-power: the resupply mod | unknown | ship | Naval resupply mechanics: 23 vessels and 4 land units, every one of them content nothing else in the collection ships. Zero file collisions, so its position is forgiving. |
| Small and Medium-Sized UAV Series [WIP] (中小型无人机系列) 🚧 WIP | FallschimJager705 | uav | Recon quadcopter (China), Forpost-R, Mugin5, Orlan-10 (Russia), RQ-7 (USA); ongoing updates. |
| Red Storm Arsenal |  | weapons | Workshop 3413868677. Largest mod in the collection - 1062 files, 638 of them content nothing else ships (230 vessels, 192 ammunition, 142 aircraft, 74 land units). BOTTOM OF THE ORDER: it also bundles 13 files that specialist mods define better. Its usn_aim_120d is a downgrade (1600 kt / 80 nm and DragCoefficient=-1, vs Murder Hornet's 2667 kt / 97 nm), and it duplicates usn_e-2d, the F-18 drop tanks, Mk54 and Nixie from Euromod, and PLAN gun ammunition. Placed last so it loses all 13 and keeps only its unique content. |

## Civilian (3)

| Mod | Author | Type | Notes |
|---|---|---|---|
| Civil Aircraft Mod (Airbus Family) | Zero Two | civilian | Commercial Airbus air traffic for scenario building. |
| Humpback Whale | unknown (added 2026-08-24) | civilian | Ambience / biologic sonar contact. VERIFIED: adds civ_humpback. |
| Merchants Expanded | unknown (added 2026-08-24) | ship | Expanded civilian merchant traffic. VERIFIED: civilian merchant hulls (civ_ms_*). **Overlaps:** auxilliary-merchant-pack (two merchant packs — check for duplicate hulls) |

## Utility / frameworks (5)

| Mod | Author | Type | Notes |
|---|---|---|---|
| AI Doctrine Overhaul | unknown (added 2026-08-24) | framework | VERIFIED: pure code mod (no unit data files) — Anchor Chain family. Changes AI behavior globally in every engagement. **Requires:** anchor-chain (presumed — code-level behavior mod; verify) |
| Anchor Chain | PrimerGuided | framework | Community chainloader. 'Will not function on its own' — requires the documented manual install. Required by B-2 Spirit and Type 003/004 CVN, and by any code-modifying mod. Recommendation: keep at the very top of the mod order. |
| Better TacMap | unknown (added 2026-08-24) | framework | VERIFIED: pure code mod (settings.cfg only in export) — Anchor Chain family UI overhaul. **Requires:** anchor-chain (presumed — UI code mod; verify) |
| Custom Loadout Editor | unknown (added 2026-08-24) | framework | VERIFIED: Anchor Chain code mod plus *_patch_clm companion units for vanilla-era aircraft/ships (F-14, AV-8A, Tarawa, MiG-27...). All patch files use NEW ids — zero overlap with the SEST loadout patches. **Requires:** anchor-chain (presumed — code-level tool; verify) |
| Buildings and Targets for Missions | unknown (added 2026-08-24) | land | Scenery and target structures for mission building. VERIFIED: land-target structures (oil pump, power plants, bunkers...). |

## ⚠️ Known missing / manual dependencies

- SeaLifter — named as required by: A-10A, Su-25 Frogfoot, Mi-8 T/TV, B-2 Spirit, Type 003/004 CVN (A-10C presumed via A-10A). It is NOT in the pasted subscription list, and it needs a manual preloader install (subscribing alone is not enough). Verify it is installed.
- Anchor Chain preloader — the Anchor Chain workshop item IS subscribed, but per its description it 'will not function on its own' and needs its documented install steps completed.
- F-15C — Modern US Airbase lists an F-15C among its aircraft, and no subscribed mod provides one. Either the airbase bundles its aircraft ('Integrated Aircrafts' may mean self-contained) or this reference is unsatisfied. Verify at file level.
