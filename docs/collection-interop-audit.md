# Collection Interoperability Audit

Every file conflict *between workshop mods* in the collection — what differs, who wins,
and what is silently lost. 133 mods load together; unit and ammunition files are whole-file
overrides, so for each of these the loser's version is discarded with no error anywhere.


**113 conflict cohorts · 263 contested files · 68 mods involved**


| Verdict | Cohorts |
|---|---:|
| order-should-change | 11 |
| needs-user-decision | 9 |
| winner-correct | 63 |
| identical-no-impact | 30 |

| Risk | Cohorts |
|---|---:|
| high | 4 |
| medium | 29 |
| low | 47 |
| none | 33 |


## Act on these — order changes with measured cost  (11)


### 1 file in this cohort: aircraft/usn_mh-60r_squadrons.ini - but the defect is the pairing with aircraft/usn_mh-60r.ini, …

**Mods** 3737267013 United States Naval Aviation (pos 59) > 3590477166 MH-60R Seahawk (pos 96). The companion unit file usn_mh-60r.ini is contested by 3606774881 U.S. Navy 2027 (pos 17) > 3737267013 (pos 59) > 3590477166 (pos 96)  

**Winner** 3737267013 (United States Naval Aviation) wins the squadrons file, while 3606774881 (U.S. Navy 2027 Capabilities mod) w… · **Risk** high


The two squadron files are built against different helicopter models. The winner (USNA) declares SerialnumberReferences=Modex, EmblemReference=Emblem, NationFlagReference=Flag1 and NumberOfSquadrons=19 (HSM-35 Magicians, HSM-37, HSM-40, HSM-41, HSL-46, HSM-48, HSM-49, HSM-50, HSM-51 Warlords, HSM-60, HSM-70 through HSM-79), each with ResourcesLiveryFolder=aircraft/usn_mh-60r/ + LiveryTexture=hsm-NN.png, ResourcesEmblemFolder=aircraft/materials/emblem/hsm/, ResourcesSerialnumberFolder=aircraft/materials/modex/ and FlagTexture=flag_usn. The loser (MH-60R Seahawk mod) declares SerialnumberReferences=number and NumberOfSquadrons=3, with serial textures at assets/numbers/HSM-NN.png and no livery or emblem overrides at all. Now the unit file: the winning usn_mh-60r.ini (USN2027) is a derivative of the MH-60R mod's model - ResourcesFolder=assets/models/aircraft/usn_sh-60b/, ResourcesRoot=SH-60.obj, ResourcesMaterial=SH-60_mat.ini, 28+ submodels including SubModel26=number with a [number] section pointing at aircraft/materials/numbers/. It contains no submodel named Modex, Emblem or Flag1 - a case-insensitive grep for modex/emblem/flag over that file returns nothing. USNA's own usn_mh-60r.ini, which loses, is the one that has SubModel33=Modex and SubModel34=Emblem with [Modex] and [Emblem] sections at lines 646-658 and a completely different mesh (assets/models/aircraft/sh60/h60_mat.ini, H60_hull_Parts_* submodels). The USN2027 unit file also modernises the loadout - Station7/8 become usn_mk54_air with MK54Positions/MK54Rotations, sonobuoys become vanilla usn_ssq-53h and usn_ssq-62g - where the MH-60R mod used its own usn_mk50_air_LQS, usn_ssq-75_LQS and usn_ssq-77c_LQS.


**Silently lost** — From the losing squadrons file: the three HSL/HSM serial-number sets keyed to SerialnumberReferences=number - the only squadron definition in the collection that matches the helicopter model that actually loads. Separately, the losing USNA unit file takes with it the entire Modex/Emblem submodel machinery its squadrons file depends on, which is what creates the mismatch.


**Risk** — Confirmed split ownership, and it is the textbook shape: the unit file usn_mh-60r.ini is won by 3606774881 while its companion usn_mh-60r_squadrons.ini is won by 3737267013, and neither mod ships the other half. The winning squadrons file names three model references - Modex, Emblem, Flag1 - that do not exist in the winning unit file's submodel list; vanilla usn_ra-3b_squadrons.ini confirms those names are submodel references that must resolve against the paired model, so squadron modex numbers, emblems and flags have nothing to bind to on the loaded airframe. Expect missing markings rather than a crash - this is not the duplicate-unit-id crash class, since all three mods use the same id usn_mh-60r as a whole-file override. Two things I could NOT verify from this export and am not claiming: whether the livery textures aircraft/usn_mh-60r/hsm-NN.png and the modex/emblem texture folders actually ship (the repo strips binaries and prunes the resulting empty directories, so their absence in the tree proves nothing), and likewise whether the loser's assets/numbers/HSM-NN.png exist. The submodel-name mismatch is verifiable from the .ini alone and stands on its own.


**Mission** — Yes, directly. SEST_RAN_Fleet (top of load order) gives both ran_ffh_anzac.ini (line 70) and ran_ddg_hobart.ini (line 134) the complement usn_mh-60r=Squadron1,1, and the mission fields 2x ran_ffh_anzac and 1x ran_ddg_hobart. So three embarked airframes resolve Squadron1 through the winning squadrons file - HSM-35 'Magicians' with modex/emblem/flag references that the loaded model has no submodels…


**Recommendation** — Move 3590477166 (MH-60R Seahawk) up to sit immediately above 3737267013 (United States Naval Aviation) in data/load-order.tokens.txt. That hands usn_mh-60r_squadrons.ini back to the mod whose serial reference (number) matches SubModel26=number in the unit file that actually loads, and it does not disturb the unit file itself - usn_mh-60r.ini still belongs to 3606774881 (pos 17), which stays above. I checked the cost and it is close to zero: 3590477166 ships only 18 files. animations/animations_SH-60.ini, assets/models/aircraft/usn_sh-60b/SH-60_mat.ini and its four *_LQS ammunition files have no other shipper. Its weapons/usn_mk46/usn_mk50_mat.ini and usn_mk54_mat.ini contest only 3413868677 at pos 139, which already loses. Its systems/sensors.ini merges key-by-key, and for every section it defines a mod above 3737267013 already wins - AN/APG-81, EOTS, AN/ALR-94, AN/APS-153, AN/ALQ-210, AN/ALQ-144 and AN/AQS-22 ALFS are all owned by 3390330875 (pos 44), SSQ-77C_Sonar and SSQ-75_Sonar by Euromod (pos 18), and AN/AAS-44 EOFLIR has no other shipper - so no sensor stat changes for the mission's F-35s or anything else. The only visible side effect is the language merge: the MH-60R mod's [usn_mh-60r] Squadron1-3 names (HSM-51 Warlords, HSM-74, HSM-77) would replace USNA's (HSM-35 Magicians, HSM-37, HSM-40), and USNA's Squadron4-19 name keys would remain merged in with no matching squadron entry - harmless, the game only lists squadrons the .ini defines. If you would rather not touch the order at all, the alternative that fits this repo's stated invariant is a SEST_* pack at the top carrying a corrected usn_mh-60r_squadrons.ini rewritten against SerialnumberReferences=number.


*Sampled: Read both usn_mh-60r_squadrons.ini in full, all three usn_mh-60r.ini (submodel lists, [Models] blocks and the diff between the USN2027 and MH-60R-mod versions), both language_en/aircraft_names.ini entries, the SEST_RAN_Fleet vessels that embark the helicopter…*


### aircraft/usn_mh-60r.ini (1) — but see split ownership: aircraft/usn_mh-60r_squadrons.ini is a separate contest won by a…

**Mods** 3606774881 U.S. Navy 2027 Capabilities mod (line 17) > 3737267013 United States Naval Aviation (line 59) > 3590477166 MH-60R Seahawk (line 96)  

**Winner** 3606774881 U.S. Navy 2027 Capabilities mod (unit file) — with aircraft/usn_mh-60r_squadrons.ini won by 3737267013 Unite… · **Risk** high


The winner is a light re-tune of the standalone 3590477166 (95-line diff): Mk46 swapped for Mk54 (Station7/8 = usn_mk54_air, and the MK46Positions/MK46LPositions groups renamed MK54Positions/MK54LPositions), sonobuoys upgraded from usn_ssq-75_LQS / usn_ssq-77c_LQS to usn_ssq-53h / usn_ssq-62g, torpedo station coordinates moved, Station7/8 rotations added. Its loadout set is Default / Empty / ASW / Strike (4x usn_agm-114k_LQS) / AntiShip (2x knm_penguin_mk2). USNA's losing copy is a different and much richer aircraft: a different model (assets/models/aircraft/sh60/usn_sh_60.obj, h60_mat.ini vs the winner's usn_sh-60b/SH-60.obj, SH-60_mat.ini), loadouts Default / Empty / Ferry (usn_sh60_tank drop tanks) / ASW / ASWLongRange / ASWPatrol (9 buoys over 3 stations including usn_ssq-77) plus AGM-119 Penguin and 4x usa_agm-114l_mm / usa_agm-114k_hh on TER rails, 7 sensor systems (Optics, 3rd_Gen_FLIR, MH-60_laser designator, APS-147, AQS-22F, ALQ-210 ESM, ALQ-210_RWR), and 19 named HSM squadrons with modex/emblem/livery. Flight model also diverges: winner 180 kt / 520 nm / 14,700 ft ceiling / 1214 kg fuel vs USNA 146 kt / 397 nm / 19,000 ft / 1835 kg. The winner's sensor list is inherited from the standalone and is frankly implausible for a Seahawk — AN/APG-81 (the F-35 AESA), AN/ALR-94 (the F-22's ESM) and EOTS alongside AN/APS-153, AN/AQS-22 ALFS, AN/ALQ-210, AN/ALQ-144, AN/AAS-44 EOFLIR.


**Silently lost** — USNA's entire MH-60R: the Ferry/ASWLongRange/ASWPatrol loadouts, the drop tanks, the TER-mounted 4x Hellfire fit, the AGM-119, the laser designator and dedicated FLIR sensor systems, the APS-147/AQS-22F sensor naming, and its model. The standalone's copy is fully lost too. What the player gets instead is a Mk54/SSQ-53H-armed 2027 Seahawk on the older SH-60B model with 5 loadouts.


**Risk** — Genuine split ownership with a verified mismatch. The winning unit file (3606774881) declares SubModel26=number and a [number] block, and has no Modex, no Emblem and no Flag1 submodels. The winning squadrons file (3737267013) declares SerialnumberReferences=Modex, EmblemReference=Emblem, NationFlagReference=Flag1 and 19 squadrons whose liveries are authored against USNA's h60 model (LiveryTexture=hsm-XX.png in aircraft/usn_mh-60r/, SpecularTexture=sh60_SpecTex.png). Every one of those three references misses the model that actually loads, so modex numbers and squadron emblems have nothing to bind to. The loser 3590477166's squadrons file — SerialnumberReferences=number, 3 squadrons, assets/numbers/HSM-XX.png — is the copy that matches the winning unit file, and it is outranked. Second, verifiable defect inside the winner itself: [WeaponSystem1AntiShip] still has Station9=knm_penguin_mk2|MK46, but the winner deleted MK46Positions/MK46Rotations when it renamed them to MK54 — that position group no longer exists in the file. Third, hidden dependencies on the mod that loses both its files: assets/models/aircraft/usn_sh-60b/ is shipped only by 3590477166, usn_agm-114k_LQS is defined only by 3590477166, and the sensor key AN/AAS-44 EOFLIR has exactly one definer collection-wide (3590477166's systems/sensors.ini). Disabling the standalone would leave the winning MH-60R modelless, with an undefined Hellfire and an undefined FLIR. No id collision and no crash class here — usn_mh-60r, usn_mh-60r_26 and usmc/usn SH-60 variants are distinct ids. Livery/emblem PNG folders could not be verified: this mods-source export is text-only (10,341 .ini, no .obj/.png).


**Mission** — Yes, indirectly but really. usn_mh-60r is embarked by usn_cg_ticonderoga_vls_2027 and by usn_ddg-1000_cps, both fielded in NORTHERN FRONT III FINAL NEWEST. (The Ford in the mission embarks usn_mh-60r_26 instead — a different id from 3390330875, not this cohort.) So the mission's Ticonderoga and Zumwalt helo detachments fly the winner's aircraft with the loser's squadron/livery table.


**Recommendation** — Keep 3606774881's unit file — Mk54 and SSQ-53H/62G are exactly right for 2026-era ASW and it is the reason that mod sits at line 17. Fix the companion instead. Cheapest reorder: move 3590477166 (MH-60R Seahawk) from line 96 to immediately above 3737267013 at line 59, so its usn_mh-60r_squadrons.ini (SerialnumberReferences=number) wins and matches the model that loads. I checked the cost across all 36 mods it would jump: the only whole-file override that changes hands is usn_mh-60r_squadrons.ini (usn_mh-60r.ini stays with 3606774881 at line 17); everything else is merge-type language_en/* and systems/sensors.ini, and its only three real shared sensor keys — AN/APG-81, AN/ALR-94, EOTS — are already won by 3390330875 at line 44, above the new slot, so nothing moves there either. The price is dropping from USNA's 19 HSM squadrons to the standalone's 3. Better fix, and the one that matches this repo's idiom: add aircraft/usn_mh-60r_squadrons.ini to SEST_Integration with USNA's 19 squadron entries but SerialnumberReferences=number and the standalone's serial-number folder, which keeps both the squadron list and working modex. Either way, also repair Station9=knm_penguin_mk2|MK46 in mods-source/3606774881/aircraft/usn_mh-60r.ini (point it at MK54 or restore an MK46Positions group), and keep 3590477166 subscribed permanently — it is load-bearing for the model, the Hellfire and the EOFLIR sensor.


*Sampled: All three copies of aircraft/usn_mh-60r.ini (705 / 769 / 703 lines) inspected; winner diffed in full against both losers. Both copies of usn_mh-60r_squadrons.ini read in full. Also resolved every ammunition and sensor id the winner references, checked which m…*


### ammunition/usn_agm-88.ini

**Mods** 3430135740 F/A-18 Murder Hornet with AIM-174B [line 22] > 3758320372 F-16C Fighting Falcon (modern) [line 80]  

**Winner** 3430135740 (F/A-18 Murder Hornet with AIM-174B) — and it should not be · **Risk** medium


The winner's file is a Shrike, not a HARM. Its own header comment reads '# AGM-45 Shrike' and its structure matches vanilla ammunition/usn_agm-45.ini: Mass=361, AmmoPoints=620, WarheadType=0 / ImpactSize=Small, no SupplyCategory, no AirLaunched, MaxVelocity=1918.32, AccelerationTime=2.8, MaxTurnRate=40, MinLaunchRange=5 / MaxLaunchRange=50 nm, SeekerGain=5.0, SeekerFOV=60, SeekerPassiveRange=25 nm, PassiveRadarGuidanceFrequencies limited to VHF/UHF/L/S/C/X-Band, TerminalApproachDist=1000, and no kinematics or loft modelling at all. The loser is a faithful copy of the vanilla AGM-88A HARM (I diffed it against mods-source/_vanilla/original/ammunition/usn_agm-88a.ini): header '# AGM-88A HARM - 1985', Mass=360, AmmoPoints=900, SupplyCategory=AdvancedARM, AirLaunched=True, WarheadType=6 (fragmentation — a valid vanilla value, vanilla's own AGM-45 uses it), ImpactSize=Medium, ApplyKinematics=True with MaxVelocity=2100, AccelerationTime=4 / 14.1 G, 20 s sustainer at 3.1 G, DragCoefficient=3.35, TerminalLoft=True, MaxLoftAngle=20 / MaxLoftAlt=35000, MaxLaunchRange=80 nm, MinLaunchAltitude=50 ft, SeekerGain=10, SeekerFOV=90, SeekerPassiveRange=80 nm, PassiveRadarGuidanceFrequencies=All, MaxFlightTime=300.


**Silently lost** — The vanilla-fidelity AGM-88A HARM: 80 nm launch range, 80 nm passive seeker, all-band emitter coverage, terminal loft, full kinematics, MaxFlightTime=300, SupplyCategory=AdvancedARM, AirLaunched=True.


**Risk** — No id collision and no dangling reference — the failure is silent capability loss. The decisive fact: the winning mod never uses this file. Every Murder Hornet airframe arms with usn_agm-88g (usn_fa-18e, usn_fa-18f_blk3, usn_ea-18g), so the only consumers of usn_agm-88 in the entire collection belong to the LOSING mod — haf_f-16c-bl50, haf_f-16c-bl52plus, pol_f-16c-bl52plus, usaf_f-16cm-bl52d, iaf_f-16c-barakII, tuaf_f-16c (Station9/Station10 pairs) — plus the project's own SEST_Integration/aircraft/usaf_f-16cm-bl52d.ini, which still declares 6 usn_agm-88 stations. Net effect: every F-16 SEAD shot in the collection loses 30 nm of launch range (50 vs 80), 55 nm of seeker reach (25 vs 80), drops from ImpactSize=Medium fragmentation to Small blast, loses lofting/kinematics entirely, and loses the AdvancedARM supply category. Related split ownership from the same pair of mods: usaf_f-16cm-bl52d.ini is won by SEST_Integration while usaf_f-16cm-bl52d_squadrons.ini is won by 3758320372.


**Mission** — No F-16 is fielded in NORTHERN FRONT III FINAL NEWEST (checked all 127 Type= values), so nothing in the active mission is degraded today. It matters the moment the project's own SEST F-16CM JATM aircraft flies a SEAD tasking, which is exactly what integration/f-16cm-jatm exists for.


**Recommendation** — Change it, and prefer the surgical fix over reordering. Best: neutralize ammunition/usn_agm-88.ini in 3430135740 (delete the local copy or override it from SEST_Integration with the vanilla HARM stats) — the Murder Hornet mod does not use the id, so it loses nothing. If you would rather move a mod: promoting 3758320372 above 3430135740 (line 80 → above line 22) flips exactly the files it currently loses to the two deprecated/Hornet mods — usn_agm-88 (the fix you want), usn_aim-9l and usn_aim-9m (contents differ; not sampled, so audit before moving), while usn_agm-65d, usn_mk-82, usn_mk-83 and usn_mk-84 are byte-identical between them and would change nothing. That is a 58-position move, so the targeted override is the lower-risk option.


*Sampled: Both usn_agm-88.ini versions diffed in full; the winner diffed against vanilla usn_agm-45.ini and the loser's key values checked against vanilla usn_agm-88a.ini; all consumer station lines located across mods-source and integration/dist; file-overlap between …*


### ammunition/wp_aa-10b.ini, ammunition/wp_aa-10c.ini, ammunition/wp_aa-10d.ini (the R-27 Alamo family)

**Mods** 3481228992 ChengDu J-10C Vigorous Dragon (line 90) > 3526982088 XIAN JH-7A (line 91) > 3436170138 Shenyang J-11 (line 106)  

**Winner** 3481228992 (ChengDu J-10C Vigorous Dragon) — its copy is byte-identical to 3526982088's, so the real contest is J-10C/J… · **Risk** medium


Two entirely different flight-model generations. The winner uses the LEGACY model (MaxVelocity + VelocityBleed + AccelerationTime); the J-11 copy uses the modern engine (ApplyKinematics=True with booster/sustainer burn split, DragCoefficient, MaxFlightTime, CircularErrorRadius, MinAttackAltitude, MaxAttackVelocity). Concrete values — wp_aa-10c (R-27R, GuidanceType=2 semi-active): winner MaxVelocity=2432 kt, MaxLaunchRange=91.89 nm, MaxTurnRate=43, Power=20, SeekerPassiveRange=45 nm; J-11 MaxVelocity=1600 kt, MaxLaunchRange=65 nm, MaxTurnRate=30, Power=15, SeekerPassiveRange=30 nm, plus AccelerationTime=3.2/Acceleration=16.1 G then SustainerAccelerationTime=4.8/SustainerAcceleration=7.75 (author's note '#---- Total Δv ≈ 870 ≈ 2.56Ma'), MaxFlightTime=100 s, CircularErrorRadius=10.51 m (8.19 m vs Large aircraft), MaxAttackVelocity=1400 kt, MinAttackAltitude=35 ft. wp_aa-10b: winner 21.6 nm / 2432 kt / Power 20 vs J-11 22.5 nm / 1600 kt / Power 15 / MaxFlightTime=60 / AmmoPoints=470. wp_aa-10d: winner 37.83 nm / MidCourseCorrection=0 vs J-11 50 nm / MidCourseCorrection=2 / AmmoPoints=840. The J-11 copy also adds AmmoPoints (supply-system pricing) and AirLaunched=True (encyclopedia launch altitudes) which the winner omits entirely, and raises AntiCountermeasuresBonus to 0.35 / AntiJammerBonus to 0.2 on the -10c. Model refs differ too: winner falls back to the vanilla AA-7 Apex asset bundle (AssetBundleMesh=wp_aa-7c, wp_aa-7c_mat) with ResourcesFolder=assets/models/ammunition/R27ER/; J-11 uses its own assets/models/weapon/ammunition/r27/ r-27ermi.obj with a sustainer particle effect. The winner's -10c line reads 'MaxLaunchRange=91.89 //80km' — the trailing comment says 80 km but 91.89 nm is 170 km, so the value is roughly double what the author's own comment intends.


**Silently lost** — The J-11 author's entire modern-kinematics tuning is discarded: two-stage boost/sustain burn profiles, drag coefficient, MaxFlightTime battery limits, circular error radii (including the separate large-target CEP), MinAttackAltitude/MaxAttackVelocity engagement envelopes, the AmmoPoints supply pricing, AirLaunched encyclopedia flags, the improved ECCM values, and the mod's own R-27 mesh with its sustainer plume. Also lost is the J-11 copy's internally consistent range set (22.5/65/50 nm).


**Risk** — No id collision (same filename = override, single registration) and no split ownership — plaaf_j-11.ini and its plaaf_j-11_squadrons.ini companion are both owned by 3436170138 uncontested, as are the -11a/-11b/-11bg pairs. The real risk is silent balance corruption in a mission-fielded unit, made worse because the winner's own comment ('//80km' against a 91.89 nm value) shows the number is a unit-conversion slip rather than a deliberate choice. Secondary risk: 3481228992 and 3526982088 ship these three files but never reference them (no wp_aa-10b/c/d appears in plaaf_j10c.ini or plaaf_jh7a.ini) — the winner is arming someone else's aircraft with files it does not itself use, which is exactly the pattern that makes this kind of override invisible in testing. Mesh existence is unverifiable: the mirror strips binaries (0 .obj files repo-wide), so the winner's ResourcesFolder=assets/models/ammunition/R27ER/ could not be confirmed or refuted — do not treat it as a proven dangling ref.


**Mission** — Yes — this is the highest mission impact of any ammunition cohort here. The mission fields Type=pla_airbase_modern, whose [AirGroup] spawns plaaf_j-11=Default,4 and plaaf_j-11a=Default,4. Both aircraft files are owned uncontested by 3436170138, and their loadouts are built on these exact ids: plaaf_j-11.ini mounts wp_aa-10c on Stations 1-6, plaaf_j-11a.ini mounts 8x wp_aa-10c and 6x wp_aa-10d. So…


**Recommendation** — Move 3436170138 (Shenyang J-11) up from line 106 to immediately above 3481228992 at line 90. I computed the exact collateral rather than estimating it: that move flips only FIVE ammunition files in the whole collection — wp_aa-10a, wp_aa-10b, wp_aa-10c, wp_aa-10d, wp_aa-11. Every other file 3436170138 ships (plaaf_pl-15, pl-12, pl-10, pl-8b, yj-91, hf-14, hf-6, ls-6_500, the 130-Ⅱ/250-Ⅲ/500-Ⅲ/90-Ⅰ series, wp_aa-12, and the four J-11 airframes) is unaffected, because those are already won by mods higher than line 90 — notably plaaf_pl-15.ini is currently won by 3486502935 at line 56, not by the J-10C, so the PL-15 that the mission's plaf_j16a block3 fires (26 stations) does not move. Of the two collateral files, wp_aa-11 (R-73) is effectively free: the J-11 and current-winner copies have identical Power=9 / MaxVelocity=1600 / MaxLaunchRange=10.8 / MaxTurnRate=60 and differ only in InFlightEffectStartTime (2.0 vs 5.5). wp_aa-10a is an active improvement: its current winner 3416372890 (Apex Predators MIG-29A & F-16A) has a corrupted line 78 where the key was glued onto a comment and doubled — '#===== Launch stats =====ApplyApplyKinematics=True' — so ApplyKinematics never parses there even though the rest of that file (AccelerationTime=6, Acceleration=10.1, SustainerAccelerationTime=-1, DragCoefficient=-1, MaxLaunchRange=27) is written for the kinematic model; the J-11 copy has the key correctly on its own line. If you would rather not touch the order at all, the alternative that costs nothing is a SEST-style patch pack at the top of the load order carrying just the J-11 author's wp_aa-10b/c/d — that matches the project's existing 'SEST packs block at the top' invariant and leaves all 133 workshop mods where they are.


*Sampled: Full diffs of all three files (winner vs 3436170138), plus a targeted key-stat extraction of guidance/velocity/range/turn-rate/power/seeker for all three in both mods. Confirmed 3481228992 and 3526982088 copies are byte-identical (7457B/85fb7e4184, 7302B/e7ef…*


### vessels/plan_cv_fujian.ini and vessels/plan_cv_fujian_variants.ini

**Mods** 3417801942 Chinese Navy (PLAN) (line 50) > 3486502935 Type 003 Fujian / Type 004 CVN Aircraft Carriers (line 56)  

**Winner** 3417801942 (Chinese Navy (PLAN)) — it wins BOTH files, so ownership is at least not split · **Risk** medium


These are not two tunings of one ship; they are two different ships sharing an id. The winner is a reskinned Soviet carrier. Its [Models] block is AssetBundleMesh=wp_cv_orel / wp_cv_orel_d / wp_cv_orel_mat with ResourcesFolder=ships/wp_cv_orel/, its [Animations] block loads animations_wp_cv_orel, animations_rails-launcher, animations_sa-n-4 and animations_rbu-6000, and its variants file paints it with ResourcesLiveryFolder=ships/wp_cv_orel/, LiveryTexture=wp_cv_orel_tx and hullnumber wp_cv_012. Hull: Length=316 m, Beam=70 m, Displacement=80000 t, AircraftCapacity=60, NumberOfLaunchPoints=8, NumberOfElevators=2, NumberOfTaxiPaths=10. Its armament is a Soviet fit — WeaponSystem1-2 SA-N-7, 3-4 SA-N-4, 5 SS-N-19 Shipwreck, 6-9 RBU-6000, 10-17 eight AK-630 CIWS, 18-21 noisemakers/chaff — and its 27 sensor systems are labelled Top_Pair, Top_Steer, Palm_Frond, Front Dome, Pop_Group and Bass_Tilt. The loser is a purpose-built PLAN carrier: Length=333 m, Beam=76.8 m, AircraftCapacity=85, NumberOfLaunchPoints=11, NumberOfTaxiPaths=17, built on the usn_cvn_nimitz mesh with an 11-part Hull submodel breakdown, DeckParkSlots=24, GroundCrewCount=12 and helicopter hold patterns. Its sensors are Type 346B AESA, Type 346B X-band FCR, Type 366 (Band Stand) and a nav radar; its weapons are 4x HQ-10 (Ammunition=pla_hq-10), 4x Type 1130 CIWS (pla_cal_30mm), plus usn_adc_mk1_noisemaker and usn_rr144_chaff. Air groups differ too: winner plan_j-15a 12+12, plan_kj-600a 4, plan_z-18f 6, plan_z-18j 6 (60 capacity); loser plan_j-15 18+18, plan_j-15d 4, pla_kj-600 3, pla_z-8 12 (85 capacity). The winner's own encyclopedia text in 3417801942/language_en/vessel_names.ini boasts the ship is 'China's first indigenously designed carrier, and its first capable of catapult-assisted take-offs' — while shipping a 1980s Soviet Orel hull with SS-N-19s and RBU-6000s.


**Silently lost** — The entire modern Fujian: the CATOBAR deck geometry (11 launch points, 17 taxi paths, 24 deck park slots, 2 elevators with per-elevator launch-point associations), the 85-aircraft capacity, the Type 346B AESA / Type 366 sensor suite, the HQ-10 and Type 1130 close-in defence, the helicopter hold pattern, and the larger 18+18 J-15 air wing with a dedicated plan_j-15d EW squadron. Also lost is the loser's own display name 'Type 003 Fujian-class' and Variant1 'CV-18 Fujian'.


**Risk** — No id collision — both mods ship the same filename, so only one plan_cv_fujian ever registers. No split ownership in the current state: 3417801942 wins the .ini and the _variants.ini together, which is the good outcome. But the winning pair has an internal defect: plan_cv_fujian_variants.ini declares NumberOfVariants=3 while defining only [Default] and [Variant1] (I counted: exactly 1 [Variant* section in the file), and the matching language block in 3417801942/language_en/vessel_names.ini likewise names only Variant1. Two of the three advertised variants have no definition behind them. The loser's file is self-consistent (NumberOfVariants=1, one variant) but has its own minor internal drift — its variants block says plan_j-15=Squadron1,20|Squadron2,20 while its hull [AirGroup] says 18|18. Because language_* files merge key-by-key rather than override, the [plan_cv_fujian] display name currently comes out as a blend: Default 'Fujian-class' and Variant1 'Fujian Type 003' from the winner, with Type=CV,Aircraft Carrier merged in from the loser. No dangling references either way — I resolved every air-group id and all eight are defined and enabled (plan_j-15a, plan_kj-600a, plan_z-18f, plan_z-18j in 3417801942; plan_j-15, plan_j-15d, pla_kj-600, pla_z-8 in 3486502935).


**Mission** — Not directly. NORTHERN FRONT III FINAL NEWEST never references 'fujian' (0 matches). It fields Type=plan_cv_type_003, supplied uncontested by a third mod (3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18), and Type=plan_cvn_004, supplied uncontested by the LOSER 3486502935 — the loser keeps its Type 004 Zhejiang because nothing else ships that file. There is an indirect tie though: the m…


**Recommendation** — Move 3486502935 (Type 003 Fujian / Type 004 CVN) from line 56 to immediately above 3417801942 at line 50. This is the cleanest reorder in the whole report and I verified the cost is literally zero: the only override-directory files these two mods contest are the two Fujian files themselves, and 3486502935 contests nothing at all with the five mods it would pass (3597650470, 3468260539, 3403661005, 3630495619, 3731208477 — all checked, no overlap). It also creates no split ownership, because every aircraft the promoted air group references (plan_j-15, plan_j-15d, pla_kj-600, pla_z-8) plus the plan_j-15_squadrons.ini, plan_j-15d_squadrons.ini and pla_kj-600_squadrons.ini companions are all owned by 3486502935 uncontested. What it costs: 3417801942 loses its Fujian entry, which is no loss — that mod's other content (Hangzhou-class Sovremenny, Luda Type 051) is untouched. One caveat worth raising with the user: the catalog itself flags 'One of THREE Fujian carriers in this list — pick a primary', and the mission already uses the third one (3663564190's plan_cv_type_003, same author as Modern PLAN Systems). If the intent is to standardise on 3663564190 as the primary Fujian, the better fix is to disable one of the two plan_cv_fujian providers outright rather than reorder them, since the mission never touches that id at all.


*Sampled: Both plan_cv_fujian_variants.ini files in full (860B and 416B). For plan_cv_fujian.ini (74212B/3355 lines vs 242591B/10900 lines) I sampled the [General]/[Physics] hull block, [AirGroup], [FlightDeck], [Animations], [Models], the full [SensorSystems] and [Wea…*


### 6 PLAAF air-launched stores: ammunition/plaaf_pl-12.ini, plaaf_pl-8b.ini, plaaf_hf-6.ini, plaaf_130-Ⅱ_rocket.ini, plaaf…

**Mods** 3486502935 Type 003 Fujian / Type 004 CVN Air (rank 49) > 3481228992 ChengDu J-10C (rank 83) > 3526982088 XIAN JH-7A (rank 84) > 3436170138 Shenyang J-11 (rank 99) > 3433577445 Shenyang J-8 (rank 101)  

**Winner** 3486502935 (Type 003 Fujian / Type 004 CVN Air) wins all six · **Risk** medium


Only three distinct contents exist, not five. {3481228992, 3526982088} are byte-identical to each other and stat-identical to the winner (they differ from it ONLY in ResourcesFolder/ResourcesMaterialFolder). {3436170138, 3433577445} are byte-identical to each other and are a genuinely different weapons model. plaaf_pl-12: winner = Mass 199 kg, no AmmoPoints/AirLaunched, MaxLoftAngle 30, TerminalApproachDist 8.64, legacy flight model (MaxVelocity 2342 kt + VelocityBleed 0.6 + Acceleration 18.0, no ApplyKinematics), SeekerPassiveRange 50 / SeekerActiveRange 9, CounterMeasuresRejection=80 / NoiseRejection=80. J-11/J-8 copy = Mass 205, AmmoPoints 290, AirLaunched=True, MaxLoftAngle 10, ApplyKinematics=True with AccelerationTime 2.5 s @19.9 G + 5 s sustainer @6.4 G, DragCoefficient=-1, MaxFlightTime 80 s, MaxAttackVelocity 1600, SeekerPassive/Active 11/11, AntiCountermeasuresBonus 0.55 / AntiJammerBonus 0.3. MaxLaunchRange is 45.94 nm in both. plaaf_pl-8b: same split — winner legacy (2128 kt, VelocityBleed 0.7, SeekerPassiveRange 12.0, MinLaunchRange 0.7, CounterMeasuresRejection 85); J-11 copy ApplyKinematics=True (0.785 s @33.6 G + 2.85 s sustainer @22 G), MaxFlightTime 40 s, SeekerPassiveRange 7.5, MinLaunchRange 0.12, AntiCountermeasuresBonus 0.35. plaaf_hf-6 (7-tube 90-Ⅰ rocket pod, SalvoFireAmount 4): all four losers byte-identical; winner differs only in ResourcesFolder. plaaf_130-Ⅱ/250-Ⅲ/500-Ⅲ: identical warhead/ballistics; only explosion-effect classes differ (winner RocketShipHitExplosion/SmallWaterSplashes vs losers MediumShipHitExplosion/LargeWaterSplashes on the 130-Ⅱ; winner LargeShipHitExplosion on 250-Ⅲ, MediumGroundHitExplosions on 500-Ⅲ) plus asset paths. Schema check against game 0.8.2: CounterMeasuresRejection/NoiseRejection appear ZERO times in _vanilla; AntiCountermeasuresBonus appears 171 times. The winner's ECCM keys are the dead ones.


**Silently lost** — The J-11/J-8 modern-schema PL-12 and PL-8B are lost entirely: ApplyKinematics boost/sustainer profiles, DragCoefficient, MaxFlightTime (80 s / 40 s hard cutoffs), MaxAttackVelocity, AmmoPoints (supply-system pricing: 290 for PL-12, 150 for PL-8B — the winner ships neither, so both missiles are free in the supply system), AirLaunched=True (encyclopedia launch-altitude display), and the live-key ECCM values (0.55/0.3 and 0.35). Under the winner, PL-12/PL-8B countermeasure and jam resistance fall back to engine defaults because CounterMeasuresRejection=80/NoiseRejection=80 are parsed by nothing in 0.8.2. Nothing else of substance is lost — the J-10C/JH-7A copies are stat-identical to the winner. Display names are NOT lost: language_*/ammunition_names.ini merges key-by-key, so all five mods' PL-12/PL-8B descriptions coexist.


**Risk** — No id collision (all five mods ship distinct unit filenames: pla_ka-28/pla_kj-600/plan_j-15/plan_j-15d vs plaaf_j-11* vs plaaf_j10c vs plaaf_jh7a vs plaaf_j-8*). No split ownership in this cohort — the winner owns both the ammo and the J-15/J-15D that consume it. Two concrete defects in the winning files: (1) 3486502935/ammunition/plaaf_250-Ⅲ.ini line 95 is a bare orphan value 'assets/ammunition/materials/' with the 'ResourcesMaterialFolder=' key deleted, so that bomb has no material-folder key at all; (2) that same file still points ResourcesFolder at assets/models/ammunition/UB-32-57/ (the losers' layout) while every other winning file was rewritten to assets/ammunition/models/ — 3486502935's asset tree contains assets/ammunition/materials/ but no assets/models/ path, so the 250-Ⅲ likely mis-resolves. Winner's referenced material inis (pl-12_mat.ini, pl-8_mat.ini, 500-3_mat.ini) do exist in 3486502935/assets/ammunition/materials/. Mesh .obj files cannot be verified — stripped from this mirror.


**Mission** — Yes, directly. The active mission NORTHERN FRONT III FINAL NEWEST fields 8x plan_j-15d, whose file (3486502935/aircraft/plan_j-15d.ini, uncontested) loads plaaf_pl-12 on every single loadout (Station18-23 across all profiles), and 1x plan_cvn_004 (also 3486502935). So the winner's legacy PL-12 with inert ECCM keys is what 8 mission J-15Ds actually shoot. plaaf_hf-6 references Ammunition=plaaf_90-…


**Recommendation** — Promote 3436170138 (Shenyang J-11) from rank 99 to just above 3486502935 (rank 49, i.e. immediately below 3737267013's slot region — anywhere at rank 48 or better). That single move gives the collection the 0.8.2-schema PL-12/PL-8B that the mission's 8 J-15Ds fire. Exact cost, computed file-by-file: 3436170138 would also take 16 further ammunition files it currently loses — plaaf_pl-15, plaaf_pl-10, plaaf_yj-91, plaaf_hf-14, plaaf_90-Ⅰ_rocket, mbd_pyl_ofab-100, plaaf_130-Ⅱ/250-Ⅲ/500-Ⅲ from 3486502935; plaaf_ls-6_500 and plaaf_pl-12a from 3663564190; wp_aa-10b/c/d from 3481228992; wp_aa-10a and wp_aa-11 from 3416372890 (which also fixes cohort 4 in the same move). wp_aa-12 is unaffected — 3417446309 sits at rank 34, still above. The most consequential collateral is plaaf_pl-15, which arms the mission's J-15Ds and J-16s: I diffed it, and 3436170138's PL-15 is also the modern one (ApplyKinematics=True, 10 s @8.4 G + 4 s sustainer @3.9 G, MaxFlightTime 160 s, TerminalVelocity 3500, AntiCountermeasuresBonus 0.8 / AntiJammerBonus 0.4) versus 3486502935's legacy 2736 kt + VelocityBleed 0.6 with the dead CounterMeasuresRejection=80 — so that flip is an improvement too, though it trades SeekerPassiveRange 110->65 and SeekerActiveRange 25->23. 3436170138's material inis for all these (assets/models/ammunition/textures/pl-12_mat.ini, pl-15_mat.ini, pl-8_mat.ini, pl-10_mat.ini, pl-12a_mat.ini) exist and match its own ResourcesMaterialFolder, so the move resolves cleanly on the text side. If you would rather not disturb 50 ranks of order, the equivalent surgical fix is a SEST ammunition pack carrying the J-11 versions of plaaf_pl-12.ini and plaaf_pl-8b.ini — the collection's SEST-above-everything invariant already guarantees it wins. Either way, also repair the two broken lines in 3486502935/ammunition/plaaf_250-Ⅲ.ini.


*Sampled: Read/diffed all six files across all five mods (md5 grouping first, then full diffs of pl-12, pl-8b, hf-6, 130-Ⅱ, 250-Ⅲ, 500-Ⅲ). Also read 3486502935/aircraft/plan_j-15d.ini loadouts, 3486502935 and 3436170138 asset trees, and _vanilla/original (game 0.8.2) t…*


### ammunition/wp_aa-10a.ini, ammunition/wp_aa-11.ini

**Mods** 3416372890 Apex Predators MIG-29A & F-16A (rank 92) > 3436170138 Shenyang J-11 (rank 99)  

**Winner** 3416372890 (Apex Predators MIG-29A & F-16A) wins both · **Risk** medium


The two files are near-identical — one differing line each. wp_aa-11.ini: InFlightEffectStartTime=2.0 (winner) vs 5.5 (J-11) — purely when the smoke trail starts drawing, no ballistic effect. wp_aa-10a.ini: this is the important one. The winner's line 78 reads '#========================================= Launch stats ============================================================ApplyApplyKinematics=True' — the ApplyKinematics assignment has been concatenated onto the end of the preceding comment banner AND duplicated into the nonsense token 'ApplyApplyKinematics'. Because the line begins with '#', the whole thing is a comment, so ApplyKinematics is never set. The J-11 copy has the identical banner and 'ApplyKinematics=True' on its own line 79, exactly as intended. Everything else in the file is byte-identical between the two: MaxVelocity=1600, AccelerationTime=6, Acceleration=10.1 G, SustainerAccelerationTime/-Acceleration=-1, DragCoefficient=-1, MaxFlightTime=60, MaxTurnRate=30, MinLaunchRange 1.5 / MaxLaunchRange 27 nm, MaxAttackVelocity=1100, SeekerFOV 80 / gimbal 45 / SeekerPassiveRange 30, AntiCountermeasuresBonus 0.35 / AntiJammerBonus 0.2, CircularErrorRadius 10.51 (8.19 vs Large).


**Silently lost** — Nothing of the J-11 pack's content is lost in the ordinary sense — the two files are otherwise identical. What is lost is correctness: the winner's copy silently disables the R-27R's entire kinematic model. The block of tuning below the corrupted line (6 s boost at 10.1 G, no sustainer, drag-derived decay, the author's own annotation 'Total Δv ≈ 595 ≈ 1.75Ma', MaxFlightTime=60 s) is written but inert, because the engine only honours it when ApplyKinematics=True is actually parsed. Schema context: ApplyKinematics appears in 544 files across the collection including 84 vanilla 0.8.2 files, so it is the current, live key.


**Risk** — No id collision, no split ownership, no dangling references. The risk is entirely the malformed line in the winning file: a genuine text-corruption defect that makes a fielded weapon behave differently from what every stat in the file says. It is silent — the engine will not log a missing key, it will simply run the legacy velocity model. Severity is capped by the fact that nothing in the current mission carries this missile, so this is a latent bug rather than a live one.


**Mission** — None. wp_aa-10a is consumed only by MiG-29A/K/M variants (3417446309 and 3416372890) and wp_aa-11 by those plus wp_su-25sm3, wp_su-24sm3, wp_cv_orel, plaaf_j-11 and several vanilla MiG-23/Taifun airframes. The active mission fields no MiG-29, no J-11 and no Su-25/Su-24. Its Su-35S (wp_su-35s, 6 airframes, owned by 3434072450) uses an entirely separate ammunition namespace — su_aa-10c, su_aa-11, s…


**Recommendation** — Two ways to fix, and the first is free if you are already acting on cohort 1. (a) Promote 3436170138 (Shenyang J-11) above 3416372890 — if you make the single move recommended for cohort 1 (3436170138 to just above rank 49), this cohort is repaired in the same step at no extra cost, since 3416372890 sits at rank 92 and would fall below it. (b) Or simply repair the winner in place: split 3416372890/ammunition/wp_aa-10a.ini line 78 so the banner ends at '====' and 'ApplyKinematics=True' starts its own line, dropping the duplicated 'Apply' prefix. Option (b) is the smaller change if you would rather not move 3436170138 at all. wp_aa-11 needs no action either way — a 3.5-second difference in when a smoke trail starts is not worth a reorder.


*Sampled: Full normalized diffs of both files across both mods, plus the winner's lines 70-110 inspected with cat -A to confirm the exact byte layout of the corrupted line. Also traced every consumer of both ids across the collection.*


### ammunition/plaaf_pl-10.ini, plaaf_pl-15.ini, plaaf_yj-91.ini (3 files, 6 contesting mods)

**Mods** 3486502935 (Type 003 Fujian / Type 004 CVN Aircraft Carriers) > 3663564190 (Type 003 Aircraft Carrier - PLANS Fujian CV-18) > 3506979898 (Shenyang J-16A) > 3481228992 (ChengDu J-10C Vigorous Dragon) > 3526982088 (XIAN JH-7A) > 3436170138 (Shenyang J-11)  

**Winner** 3486502935 (Type 003 Fujian / Type 004 CVN Aircraft Carriers) · **Risk** medium


Six mods, three lineages. Lineage A = winner 3486502935 alone. Lineage B = 3663564190, 3506979898, 3436170138 (byte-identical to each other). Lineage C = 3481228992, 3526982088 (byte-identical to each other, and identical to the winner except two asset-path lines: ResourcesFolder=assets/models/ammunition/pl-5b/ and ResourcesMaterialFolder=assets/models/ammunition/textures/ instead of the winner's assets/ammunition/models/ and assets/ammunition/materials/). So functionally there are only TWO versions: winner/C stats, and B stats. PL-10: winner/C Mass=89 kg, no AmmoPoints/AirLaunched, legacy accel model (VelocityBleed=0.7, AccelerationTime=2.5, Acceleration=20), MaxVelocity=2128 kt, MaxTurnRate=30, SeekerPassiveRange=8.0 nm, AntiCountermeasuresBonus=0.05. B: Mass=199 kg, AmmoPoints=195, AirLaunched=True, ApplyKinematics=True (boost 3 s @20.5 G + sustainer 5 s @2.5 G, DragCoefficient=-1 auto), MaxFlightTime=100 s, MaxAttackVelocity=1600, SeekerPassiveRange=12.0 nm, AntiCountermeasuresBonus=0.95. Same Power=11, KillProbability=0.9, GuidanceType=1 (IR). PL-15: winner/C MaxVelocity=2736 kt, no ApplyKinematics and no MaxFlightTime, VelocityBleed=0.6, Acceleration=16.0, MaxTurnRate=42, MaxLoftAlt=60000 ft, SeekerPassiveRange=110 / SeekerActiveRange=25 nm, old-style ECM keys CounterMeasuresRejection=80 and NoiseRejection=80. B: ApplyKinematics=True, MaxVelocity=1600 kt with TerminalVelocity=3500, boost 10 s @8.4 G + sustainer 4 s @3.9 G, MaxFlightTime=160 s, MaxTurnRate=27, MaxLoftAlt=55000, Seeker 65/23 nm, new-style AntiCountermeasuresBonus=0.8 / AntiJammerBonus=0.4, MaxAttackVelocity=1800. Both share MinLaunchRange=1.3 / MaxLaunchRange=108.1 nm, Power=16. YJ-91: both Power=24, GuidanceType=4 (anti-radiation), MaxVelocity=1824 kt, SeekerPassiveRange=40 / SeekerActiveRange=0. Winner/C add CounterMeasuresRejection=100 and NoiseRejection=100, carry DropDuration twice (2 then 0.3), and add a [Debris] block (DebrisProbability=95, DebrisLifeTime=10.0). B has DropDuration=0.5 once, adds TerminalDiveDistance=1000, an active BoosterEffect=effects/weapons/emitters/sam_medium_effect (the winner comments this out), and a SubModel1=Afterburner (Mesh=kh-31_afterburner) plus ResourcesMeshForLaunch=hull / ResourcesMeshCanister=hull / switch at 3 s.


**Silently lost** — From lineage B: the entire full-kinematics rewrite of PL-10 and PL-15 (boost/sustainer profiles, drag, MaxFlightTime energy caps, MaxAttackVelocity), the PL-10's 0.95 flare resistance and 12 nm seeker, the PL-15's newer AntiCountermeasuresBonus/AntiJammerBonus keys, and the YJ-91's afterburner submodel and booster effect. Also lost: AmmoPoints and AirLaunched=True on PL-10/PL-15/YJ-91, which B supplies and the winner omits — the winner's PL-15 therefore has no supply price and no launch-altitude encyclopedia entry. From lineage C: nothing of substance; C is stat-identical to the winner and differs only in which mod's model/material folder the missile is drawn from.


**Risk** — No id collision — ammunition identity is the filename and these files declare no id key. No split ownership between the winner and any loser: pairwise comparison shows 3486502935 vs 3663564190 contest only ammunition files, and 3486502935 vs 3506979898 only ammunition files; no <id>.ini / _squadrons.ini pair is split. Duplicate-content note (not a crash): 3486502935 ships pla_kj-600.ini and 3663564190 ships plan_kj-600.ini — the same real aircraft under two different unit ids, so the KJ-600 appears twice in the encyclopedia; different filenames means different keys, so this is cosmetic, not the 'same key' crash class. Both Fujian mods are live in the mission simultaneously (plan_cv_type_003 comes from 3663564190, plan_j-15d from 3486502935), so neither can be disabled without editing the mission. Asset references: the winner's three files point at assets/ammunition/models/ (pl-10.obj, pl-15.obj, kh-31.obj) and assets/ammunition/materials/; that materials folder exists in 3486502935 and contains pl-10_mat.ini, pl-15_mat.ini and kh-31_mat.ini, so the material side resolves. The models folder is not present in this export — but no .obj files are exported anywhere in mods-source (0 matches repo-wide), so this is not evidence of a dangling model; marked not verifiable.


**Mission** — Yes — plaaf_pl-10 is actively fielded. mods-source/3486502935/aircraft/plan_j-15d.ini (8 airframes, LoadoutVariant=AntiShip) carries plaaf_pl-10 on Station3/Station4, and 'mods-source/3506979898/aircraft/plaf_j16a block3.ini' (6 airframes, LoadoutVariant=AirToAirIntercept) carries plaaf_pl-10 on Station1/Station2 — 28 PL-10 rounds in the mission, all using the winner's AntiCountermeasuresBonus=0.…


**Recommendation** — Move 3663564190 (Type 003 Aircraft Carrier - PLANS Fujian CV-18) from load-order line 58 to immediately above 3486502935 at line 56. Rationale: the winner's PL-10 has AntiCountermeasuresBonus=0.05 against B's 0.95 — a modern IIR dogfight missile that is defeated by flares essentially every time — and that value is live on all 28 PL-10s the mission fields. B also gives PL-10 a 12 nm seeker instead of 8 nm and a proper boost/sustainer/energy model. Cost of the move is unusually small and fully enumerated: 3486502935 and 3663564190 contest exactly five files — plaaf_pl-10.ini, plaaf_pl-15.ini, plaaf_yj-91.ini, plaaf_kd-88.ini, plaaf_90-Ⅰ_rocket.ini — and nothing else in any override directory. The only mod between them, 3378409795 (deprecated RN Type 23), shares no file with 3663564190. 3486502935 keeps all its own units (plan_cv_fujian, plan_cvn_004, plan_j-15, plan_j-15d) untouched. The price you pay: PL-15 becomes energy-limited (MaxVelocity 1600 kt, MaxFlightTime 160 s, seeker 65/23 instead of 110/25), so PLA BVR reach drops — but no mission loadout currently fires PL-15, so that lands as a balance change rather than a mission change. Note B's PL-10 Mass=199 kg is unrealistic for a PL-10 (~105 kg real); if that matters, the surgical alternative is a SEST override of plaaf_pl-10.ini alone, taking B's AntiCountermeasuresBonus and seeker range onto the winner's mass.


*Sampled: All 18 copies md5-compared. Full diffs read for all three files: winner vs 3663564190 and winner vs 3481228992. Read the winner's [Models] blocks for all three, its assets/ tree, both mods' language_en/ammunition_names.ini, and the consuming loadouts in mods-…*


### vessels/usn_cvn_nimitz_variants.ini (1)

**Mods** 3373960386 Flight Deck Ops (order line 25) > 3432592449 Nimitz Expanded (46)  

**Winner** 3373960386 Flight Deck Ops — and this is the one cohort where the current winner is the wrong choice. · **Risk** medium


Flight Deck Ops ships a 57-line variants file with NumberOfVariants=2: [Variant1] CVN-68 Nimitz (hullnumber usn_cvn_068, emblem cvn-68, ServiceDate=1983) and [Variant2] CVN-69 Eisenhower (usn_cvn_069, cvn-69, ServiceDate=1987), each with a CustomAirGroup of usn_f-14a x24, usn_fa-18a x22, usn_a-6e, usn_e-2c, usn_ea-6b, usn_s-3a, usn_sh-3h. Nimitz Expanded ships a 240-line file with NumberOfVariants=10, covering the whole class: CVN-68 and CVN-69 (matching hullnumber textures) plus [Variant3] CVN-70 Vinson, [Variant4] CVN-71 Roosevelt, [Variant5] CVN-72 Lincoln, [Variant6] CVN-73 Washington, [Variant7] CVN-74 Stennis, [Variant8] CVN-75 Truman, [Variant9] CVN-76 Reagan, [Variant10] CVN-77 Bush — each with its own hullnumber texture (usn_cvn_070.png … usn_cvn_077.png), its own emblem, and its own period-appropriate CustomAirGroup (Variant3 adds usn_a-7e and usn_ra-5c to the F-14/A-6E/E-2C/EA-6B mix; Variant4 similar). Both files declare the same [General] block — HullnumberReference=Hullnumber, EmblemReference=Emblem, NationFlagReference=Flag1 — so they bind to the base hull identically.


**Silently lost** — Eight aircraft carriers. Variants 3 through 10 — Carl Vinson, Theodore Roosevelt, Abraham Lincoln, George Washington, John C. Stennis, Harry S. Truman, Ronald Reagan and George H.W. Bush — with their hull numbers, emblems and individually-tailored air wings are discarded outright. This is the entire point of Nimitz Expanded ('adds the last eight Nimitz-class carriers with custom hull numbers and liveries'), and none of it reaches the game. The mod is currently contributing nothing while still occupying a slot in the order.


**Risk** — No id collision: both mods write the same variants file for the same unit id, and no duplicate registration exists. Split ownership is present but benign in this direction — vessels/usn_cvn_nimitz.ini (the hull, 12000+ lines, with the Flight Deck Ops elevator and deck-crew animation work) is owned exclusively by 3373960386, and only the variants file is contested. I verified the challenger's variants file coheres with that hull: it declares the same three references, and the hull defines SubModel13=Hullnumber (section [Hullnumber] at line 12039) and SubModel66=Flag1 (section [Flag1] at line 12812). Two defects to be aware of before promoting: (1) Nimitz Expanded's Variant3 (CVN-70) has a typo — 'sn_s-3a=Squadron8,10' instead of 'usn_s-3a' — a dangling aircraft id, so Vinson's ten S-3A Vikings would not spawn. Every other aircraft id across all ten variants resolves to a vanilla aircraft (usn_a-6e, usn_a-7e, usn_e-2c, usn_ea-6b, usn_f-14a, usn_ra-5c, usn_s-3a, usn_sh-3h all present in mods-source/_vanilla/original/aircraft/). (2) Both files declare EmblemReference=Emblem, but the Flight Deck Ops hull contains no 'Emblem' submodel at all — so the carrier emblem decal is already inert today and would remain so after the swap. Pre-existing and unchanged either way.


**Mission** — No direct impact — the mission's carrier is usn_cvn_ford_jsf (from 3461044389), not usn_cvn_nimitz. But this is exactly the content a 2026 Indo-Pacific theatre wants available for scenario building: Vinson, Lincoln, Stennis, Reagan and Washington are the Pacific Fleet hulls, and right now only Nimitz and Eisenhower — both Atlantic-side, both with 1980s air wings — can be placed.


**Recommendation** — Move 3432592449 (Nimitz Expanded) to sit directly above 3373960386 (Flight Deck Ops) in data/load-order.tokens.txt — i.e. from line 46 to line 25. I measured the cost precisely: exactly ONE file changes winner, vessels/usn_cvn_nimitz_variants.ini itself. Nothing else in Nimitz Expanded contests anything held by the 20 mods it would jump. That is a clean, single-file swap that restores eight carriers while Flight Deck Ops keeps the hull, the animations (animations_usn_cvn_nimitz_fdo.ini, which it owns alone) and all its deck-ops behaviour — the two mods stop fighting and start composing. While making the change, fix the 'sn_s-3a' typo in Variant3 to 'usn_s-3a'. Since the file will now be the live one, that one-character edit is worth doing in the same pass — or, if you prefer not to modify workshop content in place, fold the corrected 240-line variants file into SEST_Integration instead, which achieves the same result with no reordering at all and keeps the fix under version control.


*Sampled: Both contested files in full: mods-source/3373960386/vessels/usn_cvn_nimitz_variants.ini (57 lines, read entirely) and mods-source/3432592449/vessels/usn_cvn_nimitz_variants.ini (240 lines; [General], [Default] and the Variant3/Variant4 blocks read in full, a…*


### ammunition/usn_rim-116.ini, ammunition/usn_rim-162.ini (2)

**Mods** 3461044389 Gerald R. Ford-class CVN Aircraft (load-order line 36) > 3456859157 Mogami-class Frigate (line 45)  

**Winner** 3461044389 Gerald R. Ford-class CVN Aircraft · **Risk** medium


usn_rim-116.ini is byte-identical in both mods — that half of the cohort is a non-event. usn_rim-162.ini differs in exactly two places: a header comment (#ESSM in the winner vs #RIM-7F in Mogami's, i.e. Mogami's copy was derived from a Sea Sparrow file and never re-labelled), and, decisively, Mogami's copy carries three extra lines the winner lacks — a second #ECCM block with AntiCountermeasuresBonus=0.4 and AntiJammerBonus=0.2. Both copies carry the legacy pair CounterMeasuresRejection=60 / NoiseRejection=60. Those legacy keys are dead: the shipped game uses AntiCountermeasuresBonus/AntiJammerBonus exclusively (171 occurrences across mods-source/_vanilla/original/ammunition, zero occurrences of CounterMeasuresRejection), and the modern pair outnumbers the legacy pair 971 to 139 across the workshop mods. So the winner's ESSM has NO effective ECCM credit at all, while the loser's has 0.4 anti-decoy / 0.2 anti-jam.


**Silently lost** — The only ECCM bonuses defined for ESSM anywhere in the collection. There is no third definer: usn_rim-162.ini and usn_rim-116.ini exist in exactly these two mods, vanilla ships neither, and no SEST pack overrides them. Every ESSM fired in the collection therefore currently resolves with AntiCountermeasuresBonus and AntiJammerBonus unset.


**Risk** — Not a crash risk and not an id collision — a silent capability downgrade of the fleet's primary point-defence SAM in exactly the mission being played. Confidence is high that the modern keys are the live ones (vanilla uses them universally and defines no CounterMeasuresRejection at all), but the magnitude of 0.4/0.2 in play is a balance judgement, not something I can measure from the files. No split ownership and no dangling refs in either copy.


**Mission** — High. usn_rim-162 is referenced by twelve mods and by most of the mission's air-defence line: usn_cg_ticonderoga_vls_2027 (2 refs), usn_ddg_arleigh_flt3_2027 (3), usn_ddg_arleigh_flt2A_119_2027, usn_cvn_ford_jsf (2, plus 3 RIM-116 refs), jmsdf_ddg_maya, ran_ddg_hobart and rnn_ddg_zeven_mlu — all fielded in NORTHERN FRONT III FINAL NEWEST. The mission also fields dedicated PLA jamming/ELINT aircra…


**Recommendation** — Move 3456859157 (Mogami-class Frigate) to immediately above 3461044389 (Gerald R. Ford-class CVN Aircraft) — i.e. line 45 to line 36 of data/load-order.tokens.txt. I checked the cost and it is essentially nil: the two mods contest exactly 7 files, of which usn_rim-116.ini is byte-identical, systems/weapons.ini is byte-identical, and systems/sensors.ini + the two language_en files are merge-type (their real sensor keys do not overlap at all — Ford defines SPY-3/SPY-4/AN-APY-9/AN-AAQ-37/AN-ALQ-217, Mogami defines OPY-2/OPY-2_FCR). Mogami would also jump 8 mods (3384079999, 3505420313, 3406985435, 3430106996, 3417446309, 3599752717, 3488139470, 3390330875) but shares only merge-type files (language_en/*, systems/*) with every one of them — no whole-file override changes hands. Alternative, and more in keeping with this repo's SEST-on-top invariant: add ammunition/usn_rim-162.ini to SEST_Integration carrying the winner's body plus the two AntiCountermeasuresBonus/AntiJammerBonus lines, and fix the stale '#RIM-7F' comment while you are there.


*Sampled: Both contested files diffed in full. Also diffed the two mods' systems/weapons.ini (byte-identical) and systems/sensors.ini (merge-safe, see risk), read mods-source/_vanilla/original/ammunition/usn_rim-7m.ini to settle the ECCM-field convention, and grepped R…*


### ammunition/usn_aim-9l.ini, ammunition/usn_aim-9m.ini (2 files)

**Mods** 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet > 3737267013 United States Naval Aviation > 3758320372 F-16C Fighting Falcon (modern) > 3514484654 RAAF F-35A Lighting II  

**Winner** 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) · **Risk** low


AIM-9L — winner (3426791311) and 3737267013 are identical except ResourcesFolder (assets/models/weapon/ammunition/aim-9/ vs assets/models/ammunition/aim-9/; both mods ship their own matching folder, so the winner's path resolves). Both carry ImpactSize=5 and KillProbability=0.80 and omit InterceptSpeedPenaltyMultiplier, where vanilla has ImpactSize=VerySmall, KillProbability=0.85, InterceptSpeedPenaltyMultiplier=0.75. 3758320372 (F-16C) instead has MaxVelocity=1300 (vs 1450), MaxTurnRate=90 (with the original '//30.0' left in the comment), no MaxTurnG, Acceleration 12.8/AccelerationTime 5, SeekerPassiveRange 5.0 (vs 4.5), TypicalTargetAlt/FiringAlt 40000 and TypicalTargetSpeed/LaunchVelocity 850 (vs 20000/300/500), MaxAttackVelocity 1000 (vs 1200), and it drops Min/MaxLaunchAltitude and Min/MaxAttackAltitude entirely. 3514484654 (RAAF F-35A) is stamped 'REQUIRES STATS REVISION' at the top and is an older stat generation: Mass 86, no AmmoPoints, ImpactSize=VerySmall, KillProbability 0.85, MaxVelocity 1433.7, VelocityBleed 0.9, AccelerationTime 2.73, Acceleration 20.0, MaxTurnRate 30.0, MinLaunchRange 0.4, MaxLaunchRange 9.8, TargetRearCone 120 (vs 200), SeekerFOV 2.5 (vs 4), SeekerPassiveRange 12 (vs 4.5), AntiCountermeasuresBonus 0.35 (vs 0.1), BoosterEffect=DefaultMissileInflightEffect. AIM-9M — winner vs 3737267013 differ on exactly three lines: ImpactSize=5 vs VerySmall, the winner is MISSING InterceptSpeedPenaltyMultiplier=0.75, and ResourcesFolder. 3758320372's 9M adds TargetMemory=True and AntiCountermeasuresBonus=0.65 (vs 0.25) with SeekerFOV 2.5 and MaxTurnRate 90. 3514484654's usn_aim-9m.ini is a copy-paste of its own usn_aim-9l.ini — the header still reads '# AIM-9L Sidewinder' and only three lines differ (AntiCountermeasuresBonus 0.15, material name, booster effect).


**Silently lost** — From 3737267013 (the live successor to the deprecated winner): its re-sync of the AIM-9M to the current base game — ImpactSize=VerySmall instead of the winner's ImpactSize=5, and InterceptSpeedPenaltyMultiplier=0.75. ImpactSize=5 is a non-enum value that appears in only 5 files repo-wide (all of them these three mods' AIM-9s) against 372 'Medium'/350 'Large'/167 'VerySmall'; vanilla usn_aim-9l/9m both use VerySmall, and no vanilla ammunition file anywhere uses a numeric ImpactSize. Missing InterceptSpeedPenaltyMultiplier=0.75 (documented as '0.75 for good, 1.0 for average') means the missile loses its favourable speed-penalty modifier against fast targets. From 3758320372: the aggressive modern retune (MaxTurnRate 90, TargetMemory=True, AntiCountermeasuresBonus 0.65 on the 9M). From 3514484654: nothing worth having — it is an unrevised, self-admitted stale copy whose 9M is a mislabelled duplicate of its 9L.


**Risk** — No id collision, no split ownership, no dangling refs — both the winner's model folder (3426791311/assets/models/weapon/ammunition/aim-9/ with usn_aim-9l_mat.ini and usn_aim-9m_mat.ini) and the alternatives exist on disk. The governance risk is that a mod titled [DEPRECATED] is outranking its own live replacement at load-order line 35 vs line 59: if the deprecated mod is ever unsubscribed, the AIM-9 stats silently change under the mission. Caveat: this checkout contains no binary assets at all (0 .obj files repo-wide), so mesh presence behind any ResourcesFolder could not be verified — only the .ini/material side was checked.


**Mission** — YES — indirectly but really. usa_a-10c references usn_aim-9m, and the mission fields usa_a-10c at RAAF Darwin (Squadron1,4|Squadron2,4) and RAAF Scherger (Squadron1,6|Squadron2,6) = 20 airframes. Those A-10Cs are flying the deprecated mod's stale 9M with ImpactSize=5 and no InterceptSpeedPenaltyMultiplier. The mission's fast movers are unaffected: SEST_Integration's usn_fa-18f_blk3 carries usn_ai…


**Recommendation** — 3737267013 (United States Naval Aviation) should sit above 3426791311 ([DEPRECATED] Boeing F/A-18E/F) — or, cleaner, the deprecated mod should be dropped from the collection entirely, since its successor ships the same files re-synced to the current base game. Cost of the move: promoting 3737267013 from line 59 to just above line 35 makes it outrank everything at lines 35-58, which includes 3594891803 (PLAN Submarines, line 47), 3486502935 (Type 003 Fujian air wing, line 56) and 3663564190 (Type 003 carrier, line 58) — those cohorts are Chinese ordnance and do not overlap USN Naval Aviation's file set, but the promotion should be re-run through the conflict scan before committing. If you would rather not move anything, the cheapest fix is a two-line SEST patch of ammunition/usn_aim-9m.ini restoring ImpactSize=VerySmall and InterceptSpeedPenaltyMultiplier=0.75.


*Sampled: Both files read in all four mods (8 files), plus the base-game baselines mods-source/_vanilla/original/ammunition/usn_aim-9l.ini and usn_aim-9m.ini for reference. Also ran a repo-wide census of ImpactSize values and grepped every aircraft consuming usn_aim-9l…*



## Decide these — real trade-offs, no obviously right answer  (9)


### aircraft/usn_f-35c.ini, ammunition/usn_gbu-53.ini (2 files)

**Mods** 3607989779 F-35C Lightning II Alt. Loadouts (line 21) > 3737267013 United States Naval Aviation (line 59) > 3508978375 [DEPRECATED] Lockheed Martin F-35C (line 82)  

**Winner** 3607989779 F-35C Lightning II Alt. Loadouts for usn_gbu-53.ini; for usn_f-35c.ini the workshop contest is MOOT - SEST_I… · **Risk** high


usn_gbu-53: the winner models StormBreaker as a radar-seeking glide weapon - GuidanceType=3 (active radar) with Frequency=X-Band, PeakPower=10 kW, SeekerActiveRange=7 nm, SeekerFOV=135, AntiCountermeasuresBonus=0.95, NoiseRejection=90, ReattackMode=1 (circle), MaxLaunchRange=47 nm, MaxVelocity=530 kt, ApplyKinematics=False, DragCoefficient=0, Power=13 / ImpactSize=Small / Penetration=Moderate, AmmoPoints=150. USNNA's copy is GuidanceType=1 with MidCourseCorrection=3, ApplyKinematics=True, DragCoefficient=1.4, MaxVelocity=1000, MaxFlightTime=160, MaxTurnRate=6, MaxLaunchRange=32 nm, Power=27 / Large / Penetration=Always, AmmoPoints=105 (and Chinese-language comments). The deprecated 3508978375 copy is GuidanceType=1, MidCourseCorrection=1, MaxLaunchRange=60 nm, MaxVelocity=550, Power=27 / Large / Always, with MaxLoftAngle=8.0 and VerticalWobbling. Launch envelope is where they part hardest: winner MinLaunchAltitude=9900 / MaxLaunchAltitude=10100 ft, both losers 500 / 60000 ft. Model paths also differ - winner uses assets/models/weapon/ammunition/gbu-53/ + gbu-53_mat.ini, USNNA uses assets/models/ammunition/gbu-53/ + usn_gbu-53_mat.ini. usn_f-35c: the winner is a 2026-loadout aircraft - AvailableLoadouts=AirToAirAMRAAM,AirToAirJATM,SEADJATM,StrikeAGM-154JSOWSEAD,AGM-158CHeavy,AGM-158DHeavy,StrikeGBU-53,...,StrikeQCSK_38Heavy,Empty (20 entries) firing usn_aim-260a, usn_aim-120d-3, usn_aim-9xb2+, usn_agm-88g, b-2_lrasm, b-2_jassm, b-2_jsow_sead, usn_gbu-31_qcsk, usn_gbu-38_qcsk; USNNA and the deprecated mod both offer the 9 stock loadouts (Empty, Ferry, AirToAir, Strike, StrikeLongRange, StrikePrecision, AntiShip, AntiShipHeavy, CAS). The winner also drops the AN/ALQ-239A DECM ([SensorSystem6] is annotated '#has no DECM') that both losers keep, and it adds 12 internal-bay stations including a dedicated GBU-53 pair.


**Silently lost** — From USNNA: its whole F-35C (assets/models/aircraft/usn_f-35c/ model, carrier_name_modex support, ALQ-239A DECM) and the harder-hitting GBU-53 warhead (Power 27 / Large / Always). From the deprecated mod: its 60 nm StormBreaker and its lofting profile. Note the losses on usn_f-35c.ini are academic - SEST_Integration wins that filename outright, and the SEST copy is itself derived from this winner (same 20-entry AvailableLoadouts string, same ResourcesFolder=assets/models/vechicle/aircraft/f-35/).


**Risk** — 1) LAUNCH-ENVELOPE TRAP (live): MinLaunchAltitude=9900 / MaxLaunchAltitude=10100 gives a 200-foot band in which GBU-53 can be released. Both losing copies allow 500-60,000 ft. Any F-35C or Super Hornet not holding almost exactly 10,000 ft will refuse the weapon. This reads like a hand-tuned test value that shipped. 2) SPLIT OWNERSHIP (confirmed): usn_f-35c_squadrons.ini is NOT shipped by the winner - it is won by 3737267013 (13 squadrons), while the unit file comes from the 3607989779/SEST lineage. USNNA's squadron [General] declares SerialnumberReferences=modex,left_flap_modex,right_flap_modex and EmblemReference=carrier_name_modex, but the winning unit file defines only SubModel17=modex / [modex] Mesh=modex - left_flap_modex, right_flap_modex and carrier_name_modex do not exist on it, so two of three serial references and the emblem reference are dangling. Its per-squadron liveries also point at aircraft/usn_f-35c/vfa-101/*.png (USNNA's own texture set, UV-mapped for USNNA's mesh) while the winning unit renders the MyGo mesh at assets/models/vechicle/aircraft/f-35/. The mission's Squadron11 resolves in both candidate files, so no missing-index failure - the risk is a mismatched livery, not a crash. 3) DEPRECATED-MOD DEPENDENCY: the winner's GBU-53 model path assets/models/weapon/ammunition/gbu-53/ + gbu-53_mat.ini is satisfied by 3508978375 (and 3514484654); the winner's F-35C mesh likewise lives in 3508978375. Unsubscribing that 'deprecated' mod breaks both. 4) No id collision; all 14 of the winner's F-35C loadout ammunition ids resolve to enabled mods.


**Mission** — Yes - the heaviest in my set. The mission fields usn_f-35c=Squadron1,24|Squadron11,10 off usn_cvn_ford_jsf (34 airframes) with no LoadoutVariant set, so the player picks loadouts in-game and StrikeGBU-53 is on the menu; the SEST F-35C's Station7/8 and Station11/12 all read usn_gbu-53. On top of that, 3606774881's usn_fa-18e/f/f_blk3 also carry usn_gbu-53, and 24 usn_fa-18f_blk3 are fielded. Every…


**Recommendation** — Do not reorder - fix the value. Promoting USNNA above 3607989779 would trade a 200-ft release window for a weaker guidance model AND would strip the JATM/AGM-88G/LRASM loadout set that SEST_F-35C_JATM is built on. Instead ship usn_gbu-53.ini in SEST_Integration: keep the winner's radar seeker, ReattackMode and 47 nm reach, but set MinLaunchAltitude=500 / MaxLaunchAltitude=45000, and decide the warhead deliberately (winner's Power=13/Small/Moderate is the more defensible figure for a 93 kg SDB II; the losers' 27/Large/Always is the arcade-ier one). Separately, either add a usn_f-35c_squadrons.ini to SEST that matches the MyGo mesh and defines only the modex node the unit file actually has, or add the missing left_flap_modex/right_flap_modex/carrier_name_modex submodels to the SEST F-35C. Keep 3508978375 subscribed - the winning F-35C and its GBU-53 both read meshes out of it, despite its DEPRECATED label.


*Sampled: usn_gbu-53.ini read/diffed in all three mods. usn_f-35c.ini read in all three (loadout list, sensors, model paths, submodel blocks) plus integration/dist/SEST_Integration/aircraft/usn_f-35c.ini. Also read usn_f-35c_squadrons.ini in 3737267013 and 3508978375, …*


### ammunition/plaaf_kd-88.ini

**Mods** 3486502935 Type 003 Fujian / Type 004 CVN Aircraft Carriers [line 56] > 3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18 [line 58] > 3481228992 ChengDu J-10C Vigorous Dragon [line 90] > 3526982088 XIAN JH-7A (歼轰-7A 飞豹) [line 91]  

**Winner** 3486502935 (Type 003 Fujian / Type 004 CVN Aircraft Carriers) · **Risk** medium


Four genuinely different missiles sharing one id. WINNER: TargetType=ASuW with NO LandAttackCapability line, GuidanceType=1 (IR homing), Mass=680, no AmmoPoints, Power=42 / ImpactSize=Large, MaxVelocity=580, MinLaunchRange 3.5 / MaxLaunchRange=108 nm, seeker 15 nm active / 50 nm passive, CIWSDefenceBonus=5, no sea-skimming block — and its model is the vanilla Exocet: ResourcesFolder=weapons/fr_am-39/, ResourcesRoot=fr_am-39, ResourcesMaterial=fr_am-39_mat (verified identical to vanilla ammunition/fr_am-39.ini's own resource block). LOSER 3663564190: LandAttackCapability=All, Mass=850, AmmoPoints=1575, Power=39 / ImpactSize=Medium, GuidanceType=1, SeaSkimmingAlt=200 ft, MaxVelocity=560, MinLaunchRange=6 / MaxLaunchRange=97 nm, SeekerPassiveRange=10.81, AntiCountermeasuresBonus=0.75, and a real KD-88 model (assets/models/ammunition/kd-88/kd-88.obj). LOSER 3481228992 (J-10C): GuidanceType=6 (TV homing), Power=220 (5× the winner's warhead value), ImpactSize=Large, MaxLaunchRange=200 nm, seeker 15/50, model assets/models/ammunition/KH-31/kd88.obj. LOSER 3526982088 (JH-7A): GuidanceType=6, Power=220, MaxVelocity=560, MaxLaunchRange=97.2 nm, seeker 12/40, model StreamingAssets/JH7A/assets/models/ammunition/KH-31/kd88.obj.


**Silently lost** — Land-attack capability entirely (only 3663564190 grants it), plus that mod's sea-skimming 200 ft terminal profile, AntiCountermeasuresBonus=0.75, AmmoPoints=1575 and its dedicated KD-88 mesh. From the J-10C/JH-7A versions: TV guidance (GuidanceType=6) and a Power=220 warhead — the winner's Power=42 is roughly one-fifth the damage those two mods' authors intended, and the J-10C's 200 nm reach drops to 108 nm.


**Risk** — No id collision (one filename) and no dangling asset — the winner's Exocet resource path is vanilla, so it always resolves; it just means every PLA KD-88 in the collection visually flies as a French AM-39. The substantive risk is capability loss across mods: the three KD-88 consumers are plan_j-15t (in 3663564190), plaaf_j10c (3481228992, in its [WeaponSystem1StrikePrecision] loadout alongside LS-6 glide bombs) and plaaf_jh7a (3526982088, in [WeaponSystem1Strike]) — none of them ship the winning file, and all three were authored against a different missile. Because the winner has TargetType=ASuW and no LandAttackCapability, the J-10C's precision-strike KD-88s and the JH-7A's strike pair are anti-ship-only; the CV-18 version is the only one that grants LandAttackCapability=All. Reordering is not free: 3486502935 also currently beats 3663564190 on ammunition/plaaf_pl-10.ini, plaaf_pl-15.ini, plaaf_yj-91.ini and plaaf_90-Ⅰ_rocket.ini, so promoting the CV-18 mod flips all four of those as well — plaaf_pl-15 in particular is a headline PLA AAM in this collection.


**Mission** — Both contesting carrier mods are mission-load-bearing — NORTHERN FRONT III FINAL NEWEST fields plan_cv_type_003 (owned by 3663564190) and 8× plan_j-15d (owned by 3486502935) — but the carrier's air wing is declared as plan_j-15 (24+24) and plan_j-15d (12), none of which carry KD-88. plan_j-15t, plaaf_j10c and plaaf_jh7a are not in this mission, so there is no direct in-mission effect today.


**Recommendation** — Decide deliberately; do not reorder blind. Cheapest correct fix, and the one that matches this project's own pattern: add ammunition/plaaf_kd-88.ini to SEST_Integration (top of load order) combining the CV-18 mod's LandAttackCapability=All + SeaSkimmingAlt=200 + AntiCountermeasuresBonus=0.75 + real kd-88 model with the Fujian mod's 108 nm range, and pick one warhead value (42 vs 220 is a factual dispute the mod authors never resolved). If you prefer a pure load-order move, promoting 3663564190 above 3486502935 buys land attack and the correct model but costs the flip of plaaf_pl-10, plaaf_pl-15, plaaf_yj-91 and plaaf_90-Ⅰ_rocket to the CV-18 mod's versions, which I have not audited.


*Sampled: All 4 versions key-extracted (general/warhead/guidance/seeker/model blocks); winner's [General] and [Models] blocks read in full; vanilla fr_am-39.ini resource block compared; consumer loadout blocks read in plaaf_j10c.ini, plaaf_jh7a.ini and plan_j-15t.ini; …*


### ammunition/plaaf_akf-98a.ini, plaaf_ls-6_500_zc.ini, plaaf_pl-17.ini (3 files)

**Mods** 3663564190 Type 003 Aircraft Carrier - PLANS > 3506979898 Shenyang J-16A (歼-16A 潜龙)  

**Winner** 3663564190 (Type 003 Aircraft Carrier - PLANS) · **Risk** medium


plaaf_ls-6_500_zc.ini and plaaf_pl-17.ini are byte-identical between the two mods. plaaf_akf-98a.ini differs on exactly ONE line, line 66: winner has GuidanceType=4 (Anti-Radiation Homing per the file's own legend at lines 54-64), loser has GuidanceType=3 (Active Radar Homing). Everything else is identical: Type=Missile, TargetType=ASuW, Mass=1000, AmmoPoints=2550, WarheadType=0, Power=47, MaxLaunchRange=320 nm, MidCourseCorrection=1, TerrainFollowFlight=True, SeekerGain=40, SeekerFOV=60,10, SeekerActiveRange=50.0, SeekerPassiveRange=100, Frequency=Ku-Band, PeakPower=35 kW, SecondaryPassiveRadarGuidanceType=Full, PassiveRadarGuidanceFrequencies=All.


**Silently lost** — The loser's GuidanceType=3. That single value is what makes the rest of the file coherent: SeekerActiveRange=50.0, Frequency=Ku-Band, PeakPower=35 and especially SecondaryPassiveRadarGuidanceType=Full — whose own in-file comment reads 'Used with Active or SemiActive radar seeker' — are only consulted for an active/semi-active seeker. Under the winner's GuidanceType=4 those keys go inert and the missile becomes a pure emitter-homer: it can only engage a target that is radiating, and gets no active terminal lock. Under the loser's =3 it gets active radar terminal homing PLUS passive home-on-emissions during midcourse, i.e. strictly more capability on a 320 nm ASuW weapon.


**Risk** — No id collision (same filename = override, single registration). No split ownership. No dangling refs — the file's ammunition/effects/mesh references are intact. The real risk is functional: four enabled aircraft consume plaaf_akf-98a and all four now get the anti-radiation build — 3506979898/aircraft/plaf_j16a.ini and 'plaf_j16a block3.ini', plus 3663564190/aircraft/plan_j-15t.ini and plan_j-15dt.ini. Against an EMCON or non-radiating surface group the weapon will simply fail to acquire. Note this is the winner's own aircraft too, so it is the carrier mod author's deliberate choice, not an accident of load order — which is why this needs a human call rather than a mechanical fix.


**Mission** — None directly. The mission fields Type=plan_j_15t ×12 as a CVN air group, but that id belongs to 3413868677 (Red Storm Arsenal), file mods-source/3413868677/aircraft/plan_j_15t.ini — a different unit from 3663564190's plan_j-15t.ini (underscore vs hyphen), and it contains zero references to akf-98a (grep count 0). No J-16A is fielded. So this weapon is not in the current mission's order of battle.


**Recommendation** — Do not reorder — 3506979898 sits at line 87 and 3663564190 at line 58, and dragging the J-16A mod 29 places up to flip one value would churn its other files for no gain, while the other two files in the cohort are identical so there is nothing else to win. If you want the missile to behave as an active-radar anti-ship weapon (which is what the rest of its own stat block is written for), do it as a one-line SEST patch: ship ammunition/plaaf_akf-98a.ini with GuidanceType=3 above both mods. If you accept the carrier author's intent that AKF-98A is an ARM, leave it and remember it needs an emitting target.


*Sampled: All 3 files diffed in full. Read mods-source/3663564190/ammunition/plaaf_akf-98a.ini end-to-end (General, Guidance, Seeker blocks). Grepped every consumer of plaaf_akf-98a across all 133 mods, and checked mods-source/3413868677/aircraft/plan_j_15t.ini for akf…*


### ammunition/usa_agm-114k.ini (1 file)

**Mods** 3567228449 French Helicopter Package > 3559495372 Lockheed AC-130 Pack  

**Winner** 3567228449 (French Helicopter Package) · **Risk** medium


Winner (French Helicopter Package): no AmmoPoints, Power=21, no kinematics block — VelocityBleed=0.7, Acceleration=5, MaxTurnRate=13; MaxLaunchRange=5.94 nm; MinLaunchAltitude=100 ft, MaxLaunchAltitude=2000 ft; model ResourcesFolder=assets/models/ammunition/agm-114/, ResourcesMesh=agm-114b, ResourcesMaterial=agm-114b_mat.ini (verified present), no submodels. Loser (AC-130 Pack): AmmoPoints=65, Power=18, ApplyKinematics=True with AccelerationTime=3, Acceleration=12.85, SustainerAccelerationTime=35 at SustainerAcceleration=0.825, VelocityBleed=0.8, MaxFlightTime=60, MaxTurnRate=4.0, WobblingStrength=5 / WobblingSpeed=2, TypicalTargetAlt/FiringAlt/LaunchVelocity all 0; MaxLaunchRange=4.32 nm; MinLaunchAltitude=0 ft, MaxLaunchAltitude=6000 ft; model ResourcesFolder=assets/models/weapon/ammunition/agm-114/, ResourcesMesh=agm-114, ResourcesMaterial=agm-114k_mat.ini plus a 'Glas' seeker-window submodel.


**Silently lost** — From the AC-130 Pack: the sustainer-motor kinematics, the wobbling flight model, the AmmoPoints=65 supply cost, the seeker-window submodel — and, critically, MaxLaunchAltitude=6000 ft. The winner replaces that with 2000 ft. What the winner gives in exchange is a far more agile missile (MaxTurnRate 13 vs 4.0 deg/s) with longer reach (5.94 vs 4.32 nm) and more warhead (Power 21 vs 18), which is the right trade for the helicopter fleet but the wrong one for a gunship.


**Risk** — No id collision, no split ownership, and the winner's model path is verified present (3567228449/assets/models/ammunition/agm-114/agm-114b_mat.ini). The defect is an altitude-envelope mismatch created by the override. mods-source/3559495372/aircraft/usaf_ac-130j.ini has CruiseAltitude=20000 ft and its selectable altitude band is Altitudes=200,500,1000,1500,2000,3000,5000,7000,10000 — with Station1=usa_agm-114k|AGM-114. Under the winning file the gunship's Hellfire station is gated to MaxLaunchAltitude=2000 ft, the second-lowest rung of its own altitude list and one tenth of its cruise altitude, so the AC-130J will be unable to employ its only precision weapon from anywhere near where it normally orbits. The AC-130 pack's own 6000 ft was already low, but it at least reached the middle of the aircraft's band. Worth noting the winner's stats are otherwise the better ones — a 4.0 deg/s turn rate would make the missile nearly useless against anything manoeuvring.


**Mission** — YES. Type=usaf_ac-130j is fielded in NORTHERN FRONT III FINAL (1 unit), and its Station1 is usa_agm-114k — the exact contested id. That gunship is currently carrying a Hellfire it can only launch below 2000 ft. Other consumers are unaffected or absent: 3425450153's usa_ah-64d/e and 3567228449's HAD-E and EC-725 family are helicopters (2000 ft is a non-issue for them) and none are in the mission; …


**Recommendation** — Do NOT reorder. Promoting 3559495372 (line 95) above 3567228449 (line 84) would fix the gunship but hand every Hellfire-armed helicopter in the collection a 4.0 deg/s turn rate, a 4.32 nm reach and a weaker warhead — a bad trade to rescue one airframe. The right fix is a SEST patch of ammunition/usa_agm-114k.ini: take the French Helicopter Package's file verbatim and raise MaxLaunchAltitude from 2000 to at least 10000 ft (20000 to cover the AC-130J's full cruise altitude), and add back AmmoPoints=65 so the weapon has a supply cost. That keeps the better kinematics for the helicopter fleet and restores the mission's AC-130J to usable. This is the second-highest-priority item in my nine cohorts, after the F-35A AMRAAM dependency.


*Sampled: Both versions read and diffed in full. Read mods-source/3559495372/aircraft/usaf_ac-130j.ini (loadout stations, CruiseAltitude, selectable altitude band). Verified 3567228449/assets/models/ammunition/agm-114/ exists with agm-114b_mat.ini. Grepped every consum…*


### 1 file: ammunition/usn_gbu-12d.ini

**Mods** 3607989779 F-35C Lightning II Alt. Loadouts (line 14) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (line 28) > 3505420313 Italian Navy Mod (line 31) > 3737267013 United States Naval Aviation (line 52)  

**Winner** 3607989779 F-35C Lightning II Alt. Loadouts · **Risk** medium


THE THREE LOSERS ARE NEARLY IDENTICAL TO EACH OTHER; THE WINNER IS THE OUTLIER. Losers 3426791311, 3505420313 and 3737267013 all use Mass=363, WarheadType=0 (blast-frag), Power=32, ImpactSize=Medium, Penetration=Moderate, MinLaunchRange=1, MaxLaunchRange=10, MinLaunchAltitude=500, MaxLaunchAltitude=60000, LaunchReliability=97, SeekerFOV=10.0, SeekerActiveRange=0.0, SeekerPassiveRange=10.0. Their only differences among themselves: 3505420313 drops AmmoPoints entirely and uses MaxTurnRate=3 (the other two use 6); 3737267013 uses ResourcesFolder=assets/models/ammunition/mk82/ while the other two use assets/models/weapon/ammunition/mk82/. The winner is a genuine re-stat: Mass=275 (vs 363), WarheadType=1 armour-piercing (vs 0 blast-frag), Power=23 (vs 32), Penetration=Heavy (vs Moderate), MinLaunchRange=0.2 / MaxLaunchRange=8 (vs 1/10), MinLaunchAltitude=2000 (vs 500), MaxLaunchAltitude=65000, LaunchReliability=98, SeekerFOV=45.0, SeekerActiveRange=4 and SeekerPassiveRange=4 (vs 0.0/10.0). For reference, vanilla usn_gbu-12.ini is Mass=250, WarheadType=0, Power=28, Penetration=Moderate, MinLaunchAltitude=500, SeekerFOV=90, SeekerActiveRange=0.0, SeekerPassiveRange=10.0 - so the losers follow the vanilla laser-guided-bomb convention (active range 0, passive range 10) and the winner does not. The winner's Mass=275 is the most accurate figure for a 500 lb Paveway II; 363 kg is closer to a 1000 lb GBU-16.


**Silently lost** — The blast-fragmentation warhead at Power=32 with Penetration=Moderate, the 500 ft minimum release altitude, the 10 nm launch range, and the vanilla-convention 10 nm passive seeker range. Also lost: 3426791311's and 3505420313's ResourcesFolder=assets/models/weapon/ammunition/mk82/ - though the winner uses that same path, so no change there. No display name is lost: the winner ships NO language_en entry for usn_gbu-12d at all, and because language files merge key-by-key the name and description still come from a loser (3426791311's 'GBU-12D,Paveway II,AGM,...' being highest of the three, ahead of 3505420313's description-less 'GBU-12D,,Guided Bomb' and 3737267013's 'GBU-12D,Paveway II,Guided Bomb,...'). That is a nice illustration that stats and display name can end up sourced from different mods.


**Risk** — No id collision and no split ownership - single ammunition file, four plain overrides. One cross-mod asset dependency: the winner's ResourcesFolder=assets/models/weapon/ammunition/mk82/ with ResourcesRoot=gbu-12d.obj and ResourcesMaterial=gbu-12d_mat.ini is NOT shipped by 3607989779 (its assets tree contains only models/weapon/ammunition/aim-9 and models/ammunition/gbu-31). That folder is provided by 3426791311 and 3413868677 - both of which carry assets/models/weapon/ammunition/mk82/gbu-12d_mat.ini. So the winning GBU-12D's model comes from the deprecated Super Hornet mod or Red Storm Arsenal; disabling both would dangle it. Binary assets are stripped from this mirror so I could confirm only the _mat.ini, not the .obj. The substantive concern is gameplay, not breakage: WarheadType=1/Power=23/Penetration=Heavy converts the GBU-12 from an area blast-frag weapon into a low-yield penetrator, and MinLaunchAltitude=2000 forbids low-level release, on every aircraft in the collection that carries the id - not just the F-35C the winning mod is about.


**Mission** — Yes. usn_gbu-12d is carried by the mission-fielded usn_f-35c (34 airframes off usn_cvn_ford_jsf) and usn_fa-18f_blk3 (24 airframes, Squadron3/4/5), in both cases via the SEST_Integration copies of those aircraft files, which reference usn_gbu-12d 12 and several times respectively. The mission's ground target set includes tgt_fueltanks_small, tgt_ammo_depot_small, wp_sejjil_tel, shahed_tel_black/w…


**Recommendation** — This one is worth a decision rather than a default. The winner has the right mass (275 kg) but has re-roled the weapon as a penetrator with a 2000 ft release floor and a shorter, narrower seeker than vanilla convention - and it applies that to every GBU-12 carrier in the collection, including USNA's AV-8B+ and the mission's Super Hornets, not just the F-35C the mod is named for. If the intent is a conventional Paveway II, move 3737267013 United States Naval Aviation above 3607989779 (or, less disruptively, put the desired stats in a SEST ammunition patch, which is the pattern this repo already uses and costs nothing in load order). COST OF THE REORDER, measured exactly: 3607989779 and 3737267013 share five override files - aircraft/usn_f-35c.ini (irrelevant, SEST wins it anyway), ammunition/usn_agm-88g.ini, ammunition/usn_gbu-12d.ini, ammunition/usn_gbu-31v4.ini and ammunition/usn_gbu-53.ini. So promoting USNA would also flip GBU-31(V)4 (see the separate cohort) plus AGM-88G and GBU-53, the latter two of which I did not sample. The SEST-patch route avoids all of that; I would recommend it over a reorder.


*Sampled: All four versions read via key-field extraction over the whole file (they are 156-160 lines each, so this covers essentially everything substantive); plus the vanilla baseline mods-source/_vanilla/original/ammunition/usn_gbu-12.ini for convention, all four la…*


### 1 file: ammunition/usn_cal_30mm.ini

**Mods** 3629144864 Euromod - Main Pack (line 11) > 3559495372 Lockheed AC-130 Pack (line 88)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** medium


The winner is a stripped-down definition. Winner: MuzzleVelocity=1109 m/s, MaxRange=4000 m, CircularErrorProbable=12 m, Power=0.85, ImpactSize=Tiny, Penetration=Minor, DecalClass=GunImpacts, HitShipExplosion=impact_small_shell_multi. Loser: MuzzleVelocity=1080 m/s, MaxRange=4500 m, CircularErrorProbable=25 m, same Power/ImpactSize/Penetration, DecalClass=GunImpactsSmall, HitShipExplosion=impact_small_shell. Crucially the loser ALSO defines five things the winner omits entirely: Mass=4.5, AmmoPoints=4.5, GravityFactor=4, FuzeProximityDistance=25 (metres), KillProbability=0.0002, and a complete [Models] block (ResourcesFolder=weapons/shells/, ResourcesRoot=shell_small, ResourcesMesh=shell_small, ResourcesMaterial=shell_mat) plus HitDefaultExplosion. The winner has no [Models] section at all. Display names differ too: winner '30mm,,Gun', loser '30mm,Shell,,' - resolved by language merge, not by this override.


**Silently lost** — The proximity fuze (FuzeProximityDistance=25) on a projectile whose primary TargetType is AAW, the missile-intercept KillProbability=0.0002, the ballistic GravityFactor=4, the supply-system Mass/AmmoPoints, and the shell mesh itself. The AC-130 pack authored all of those specifically for a gunship firing 30mm from an orbit; the winner's version was written for European ship mounts (Euromod's own consumers are PresetSystems/Weapons/Mk38_Mod4.ini and 'DS30M A1 (with EO).ini') and drops them.


**Risk** — No id collision, no split ownership - the two mods share exactly one override file. But the winner is a partial definition winning over a complete one, which is the classic whole-file-override trap: because the loser's copy is silently ignored, there is no fallback for the keys the winner omits, and the engine will use its defaults. Two concrete consequences to expect: (1) with no [Models] block the 30mm rounds have no shell mesh/material, so tracers may not render - a visible regression for a gunship whose whole point is watching rounds walk onto the target; (2) with FuzeProximityDistance absent on an AAW-primary projectile, airburst behaviour is lost and hits become contact-only. Note the winner is NOT uniformly worse - CEP 12 m vs 25 m makes it noticeably more accurate at max range, and MuzzleVelocity is slightly higher; it is shorter-ranged (4000 vs 4500 m). Important correction to a plausible misreading: the AH-64E does NOT use this id - it uses usn_cal_30mm_hedp (a separate, uncontested file from 3425450153). Only substring matching makes it look contested. Binary assets are stripped from this mirror so I could not verify whether weapons/shells/shell_small exists.


**Mission** — Yes, on two mission-fielded units. usaf_ac-130j (mod 3559495372, the loser) defines [WeaponMagazine40mm] with Ammunition1=usn_cal_30mm and Ammunition1_Count=230, and the mission fields it three times - Type=usaf_ac-130j at line 1649 plus air-base squadron allocations 'usaf_ac-130j=Squadron1,8' and 'usaf_ac-130j=Squadron1,6'. And usn_ddg-1000_cps - fielded as Taskforce1Vessel2 and owned by SEST_In…


**Recommendation** — Worth changing, but do it with a patch rather than a reorder. The cleanest fix is to re-add the missing keys - Mass, AmmoPoints, GravityFactor=4, FuzeProximityDistance=25, KillProbability=0.0002 and the [Models] block - to a SEST ammunition patch for usn_cal_30mm, keeping Euromod's better CEP=12 and its MuzzleVelocity. If a patch is not wanted, moving 3559495372 Lockheed AC-130 Pack above 3629144864 Euromod - Main Pack is a small, contained change: the two mods share ONLY this one override file, so nothing else flips between them. The cost of that move is that Euromod's ship mounts (Mk 38 Mod 4, DS30M A1) would inherit the gunship's CEP=25 and 4500 m range instead of 12 m / 4000 m, and the AC-130 pack would then also outrank whatever sits between lines 11 and 88 for its other two currently-shadowed files (usa_agm-114k.ini, usn_mk-82.ini), which I did not sample.


*Sampled: Both versions read in full (they are short - 26 and 36 lines). Also read: 3559495372/aircraft/usaf_ac-130j.ini magazine block, integration/dist/SEST_Integration/vessels/usn_ddg-1000_cps.ini reference, integration/dist/SEST_Integration/aircraft/usa_ah-64e.ini …*


### ammunition/usn_aim-9x.ini (1 file, 7 contesting mods)

**Mods** 3606774881 (U.S. Navy 2027 Capabilities mod) > 3430135740 (F/A-18 Murder Hornet with AIM-174B) > 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) > 3737267013 (United States Naval Aviation) > 3758320372 (F-16C Fighting Falcon (modern)) > 3508978375 ([DEPRECATED] Lockheed Martin F-35C) > 3514…  

**Winner** 3606774881 (U.S. Navy 2027 Capabilities mod) · **Risk** low


Five distinct versions. Reading Power / KillProbability / MaxVelocity kt / MaxTurnRate deg-s / MaxFlightTime s / MaxLaunchRange nm / SeekerFOV / SeekerPassiveRange nm / AntiCountermeasuresBonus: - 3606774881 (winner): 9 / 0.95 / 1475 / 45 / 70 / 19.4 / 180 / 15 / 0.95. Full kinematics rewrite — ApplyKinematics=True, AccelerationTime=5 @14.4 G, DragCoefficient=7.16, LiftFactor=0.001, VelocityBleed=1, TimeLimited=True, plus Typical* range calibration. Also WarheadType=6 with Penetration=Minor, MidCourseCorrection=3, DropDuration=0.1, MaxLoftAngle=30 / MaxLoftAlt=65000, MinLaunchRange=0.2, MaxAttackVelocity=1500, launch envelope 200–65000 ft, AntiJammerBonus=0.6, ResourcesFolder=assets/models/weapon/ammunition/aim-9/ with usn_aim-9x_mat.ini and an added 'Glas' submodel. - 3430135740: 10 / 0.98 / 1740 / 80 / – / 15 / 300 / 20 / 0.80. Legacy asset path weapons/usn_aim-9/ with ResourcesRoot=usn_aim-9l, MidCourseCorrection=0, InFlightEffectStartTime=40.0. - 3426791311 and 3508978375 (identical): 9 / 0.85 / 1600 / 150 (with MaxTurnG=50) / 40 / 12.5 / 2.5 / 8 / 0.95. - 3737267013: 9 / 0.9 / 1600 / 70 / 40 / 12 / 5 (with SeekerGimbalFOV=150) / 12 / 0.95, plus TargetMemory=True and ResourcesFolder=assets/models/ammunition/aim-9/. - 3514484654: 9 / 0.85 / 1433.7 / 180 / – / 12.8 / 2.5 / 12 / 0.05. The standout is MaxTurnRate: the winner's 45 deg/s is the lowest of all five by a wide margin, against 70, 80, 150 and 180 elsewhere. The winner also has the longest reach (19.4 nm vs 12–15), the widest bare SeekerFOV (180, with no SeekerGimbalFOV), the longest seeker range (15 nm) and the joint-best anti-countermeasures value.


**Silently lost** — 3426791311/3508978375's MaxTurnG=50 hard-G limiter and the narrow-FOV-plus-gimbal seeker idiom (SeekerFOV=2.5 + gimbal), which is the newer engine convention; 3737267013's TargetMemory=True (lock retention through spoofing) and its SeekerGimbalFOV=150; 3430135740's 1740 kt top speed and 20 nm seeker. Note 3514484654's AntiCountermeasuresBonus=0.05 is also discarded, which is a good thing — it is the same suspicious near-zero value seen on the PL-10 winner in cohort 2.


**Risk** — No id collision (no id key; the file declares no unit id). No split ownership within this file. The winner's material reference resolves: assets/models/weapon/ammunition/aim-9/usn_aim-9x_mat.ini exists in 3426791311, 3508978375, 3514484654, 3758320372, 3503670861 and 3413868677, all enabled — though note 3606774881 does not ship it itself. Cosmetic sloppiness in a loser worth knowing about if it is ever promoted: 3737267013's copy has a mangled line where a section banner ran into a comment ('SelfDestructDelay=4.0 // delay in seconds for self destructi[---------- Mesh definitions----------]'); it is inside a comment so it parses harmlessly, but it signals hand-editing. Same adjacent split-ownership defects as the Mk-83/84 cohort apply to this mod set: usn_fa-18e.ini and usn_ea-18g.ini won by 3606774881 (line 17) while their _squadrons.ini companions are won by 3430135740 (line 22); none of those units are mission-fielded.


**Mission** — None. No unit fielded in NORTHERN FRONT III FINAL NEWEST carries usn_aim-9x. I resolved all 127 mission unit ids to 137 unit files and searched every one: zero references. The closest case is usa_a-10c x2, whose SEST_REDBACK loadout (defined in the top-of-order SEST_Integration override) carries usn_aim-9m, not usn_aim-9x.


**Recommendation** — Do not reorder on my say-so — decide what you want the AIM-9X to be. The winner is defensible as the deliberate modern rewrite (full kinematics, longest reach, best ECCM) and it comes from the 2027 Capabilities mod, which is the right era anchor for a 2026 Indo-Pacific collection. But MaxTurnRate=45 deg/s is a real outlier for a thrust-vectoring high-off-boresight dogfight missile, and it applies collection-wide to every US and allied airframe that carries usn_aim-9x. Two options: (a) accept it, on the theory that the winner models WVR reach rather than turn performance; or (b) leave the order alone and raise MaxTurnRate in a SEST override, which costs nothing since 3606774881 is already top of this stack at line 17. Reordering to reach a higher turn rate would mean giving up 19.4 nm reach, SeekerFOV 180 and the 15 nm seeker, which is a bad trade. Low urgency either way — nothing in the active mission fires this weapon.


*Sampled: All 7 copies md5-compared (5 distinct versions; 3426791311 and 3508978375 are byte-identical). Full diffs read: winner vs 3430135740, winner vs 3737267013, winner vs 3426791311. Key stats extracted from all seven. Cross-checked every mission-fielded unit file…*


### ammunition/usn_gbu-39.ini (1 file)

**Mods** 3737267013 (United States Naval Aviation) > 3418252667 (F-22 Raptor)  

**Winner** 3737267013 (United States Naval Aviation) · **Risk** low


Two genuinely different Small Diameter Bombs. Winner ('GBU-39 SDB 122kg GPS guided bomb. by dts'): Mass=122 kg, AmmoPoints=250, Power=12, ImpactSize=Medium, Penetration=Moderate, IRSignature=VeryTiny. Glide kinematics — ApplyKinematics=True, MaxVelocity=1000 kt, AccelerationTime=999 @0.02 G, DragCoefficient=1.4, MaxFlightTime=160 s, TypicalTargetAlt=0. MaxTurnRate=6, MinLaunchRange=2 / MaxLaunchRange=32 nm, DropDuration=4, InitialFlightPhaseDuration=3.0, CircularErrorRadius=15 m, SelfDestructDelay=5.0, HitDefaultExplosionClass=MediumMissileExplosions, HitWaterSplashClass=SmallWaterSplashes. Loser ('gbu-39 for A10, low range'): Mass=110 kg, AmmoPoints=75, AirLaunched=True, Power=27, ImpactSize=Large, Penetration=Always, IRSignature=VerySmall. MaxVelocity=550 kt, Acceleration=0.01, MaxTurnRate=2, MinLaunchRange=3 / MaxLaunchRange=44.8 nm, DropDuration=1, InitialFlightPhaseDuration=0, TerminalApproachDist=3.5 / TerminalDiveDistance=3.5 nm, SupportsBanking=True, TerminalVerticalTurnRate=2, VerticalWobblingStrength=8.0, CircularErrorRadius=1.5 m, TargetMemory=True, HitDefaultExplosionClass=MediumGroundHitExplosions, HitWaterSplashClass=LargeWaterSplashes. Net: the winner is faster and far more manoeuvrable (6 vs 2 deg/s) but 10x less accurate (CEP 15 m vs 1.5 m), less than half as destructive (Power 12 vs 27, ImpactSize Medium vs Large) and 12.8 nm shorter-ranged.


**Silently lost** — The loser's 1.5 m CEP, Power=27 / ImpactSize=Large warhead, 44.8 nm standoff range, TargetMemory=True, and its terminal-dive and banking behaviour (TerminalDiveDistance, SupportsBanking, TerminalVerticalTurnRate, vertical wobble) — i.e. essentially all of the precision-attack modelling. Also lost is AirLaunched=True, which the winner omits.


**Risk** — No id collision (no id key). No split ownership: the only files these two mods contest are usn_agm-88g.ini and usn_gbu-39.ini. Asset side resolves — the winner's ResourcesFolder=assets/models/ammunition/gbu-39/ with ResourcesMaterial=usn_gbu-39_mat.ini exists in 3737267013 (which also holds bru-61a_mat.ini and usn_bru-61_mat.ini), and 3418252667 ships the same-named material too. One probable visual defect, marked as inference: the winner sets ResourcesMesh=launch with ResourcesMeshForLaunch=bomb and ResourcesMeshSwitchTime=3, which is the inverse of the loser's ResourcesMesh=bomb / ResourcesMeshForLaunch=launch / switch at 0.7 s. Going by the mesh names one of the two has them swapped, and the winner reads like the swapped one — but .obj files are not exported to this repo, so I could not verify what those meshes actually are. Not sampled: the mesh geometry itself.


**Mission** — None. usn_gbu-39 reaches the battlefield only through dispensers: mods-source/3418252667/ammunition/usn_bru-61a.ini (used by usaf_f-22_s6 in its StrikePrecision loadout) and, separately, mods-source/3459682829/ammunition/usn_bru-61a_10.ini, which dispenses usn_gbu-39_10 — a different ammunition id, defined by 3459682829 and uncontested. In the mission all 8 usaf_f-22_s6 fly AirToAirIntercept (6x …


**Recommendation** — Leave the order as it is, but be aware the collection's SDB is currently the low-precision one. If you ever fly an SDB strike — the F-22's StrikePrecision loadout is the obvious candidate — a 15 m CEP against point targets will badly underperform the 1.5 m version the F-22 author wrote. Do not fix it by reordering: 3737267013 (line 59) and 3418252667 (line 81) also contest usn_agm-88g.ini, and promoting 3418252667 across the ~20 mods between them has unaudited collateral. The cheap fix is a SEST override of usn_gbu-39.ini that keeps the winner's glide kinematics and takes the loser's CircularErrorRadius, Power, ImpactSize and TargetMemory.


*Sampled: Both copies diffed in full. Read the winner's [Models] block, both mods' assets/models/ammunition/gbu-39/ listings, mods-source/3418252667/ammunition/usn_bru-61a.ini and mods-source/3459682829/ammunition/usn_bru-61a_10.ini, the F-22's loadout table, and the A…*


### ammunition/usn_gbu-24.ini, ammunition/usn_tank_1200_f-18.ini (2 files)

**Mods** 3430135740 F/A-18 Murder Hornet with AIM-174B (order line 22) > 3737267013 United States Naval Aviation (order line 59)  

**Winner** 3430135740 F/A-18 Murder Hornet with AIM-174B · **Risk** low


usn_tank_1200_f-18.ini is BYTE-IDENTICAL between the two mods — diff returns zero differences. This half of the cohort has no effect whatsoever. usn_gbu-24.ini is a different story: the winner does not ship a GBU-24 at all, it ships a GBU-27 under the GBU-24's id. Loser (US Naval Aviation): Mass=907 kg, AmmoPoints=2425, WarheadType=0 (blast-fragmentation), Power=62, MaxLaunchRange=15 nm, MaxTurnRate=3, InitialFlightPhaseDuration=2.0, SeekerFOV=90.0, SeekerPassiveRange=10.0, LaunchReliability=97, model assets/models/ammunition/gbu-24/ + usn_gbu24_mat.ini, and one submodel ('Glas', using aircraft/materials/cockpit_glass for the seeker window). Winner (Murder Hornet): Mass=363 kg, no AmmoPoints line at all, WarheadType=1 (armour-piercing) with Power=85 and the comment 'Reflect armor piercing characteristics', MaxLaunchRange=25 nm, MaxTurnRate=5, InitialFlightPhaseDuration=1.0, SeekerFOV=360.0, SeekerPassiveRange=25.0, LaunchReliability=99, model assets/models/ammunition/gbu-27/gbu-27.obj + gbu-27_mat.ini, NumberOfSubModels=0. For reference the vanilla file is Mass=1050, AmmoPoints=1575, WarheadType=0, Power=62, MaxLaunchRange=20, SeekerFOV=90 — i.e. the loser's version is a light refresh of vanilla, while the winner is a substitution of a different weapon.


**Silently lost** — The GBU-24 Paveway III itself. Under the current order no enabled file anywhere in the collection defines a 907-1050 kg blast-fragmentation laser-guided bomb under this id — the loser's copy was the only mod version that kept the weapon's identity. Also lost: AmmoPoints=2425 (the winner has no supply price for this round) and the 'Glas' seeker-window submodel. Nothing is lost from usn_tank_1200_f-18, the files being identical.


**Risk** — No id collision, no dangling reference — the winner's ResourcesMaterialFolder=assets/models/ammunition/gbu-27/textures/ and gbu-27_mat.ini both exist inside 3430135740, so the substituted weapon renders. The defect is semantic, not structural: a weapon named and labelled GBU-24 now weighs 363 kg and penetrates like a GBU-27. Consequence today is nil because nothing enabled fires it, but it is a landmine for any future mission that spawns the vanilla A-6E, and for anyone reading the encyclopedia. Note also that the loser's usn_gbu-24 points at assets/models/ammunition/gbu-24/ which 3737267013 would have to ship — I could not confirm that (this mirror holds .ini files only), so promoting the loser is not risk-free either.


**Mission** — None. After resolution NO enabled mod file consumes usn_gbu-24 — Murder Hornet's own usn_fa-18f and usn_fa-18f_blk3 and US Naval Aviation's usn_fa-18e/f/f_blk3 all lose their airframe files to 3606774881, whose versions carry usaf_gbu-24 (a separate id, separate file) instead. The only remaining consumer anywhere is the vanilla A-6E (mods-source/_vanilla/original/aircraft/usn_a-6e.ini), which no …


**Recommendation** — Do NOT reorder for this. Moving 3737267013 above 3430135740 would fix usn_gbu-24 and change nothing on the identical drop tank, but it would simultaneously flip six other shared files — aircraft/usn_ea-18g_squadrons.ini, usn_fa-18e_squadrons.ini, usn_fa-18f_squadrons.ini, usn_fa-18f_blk3_squadrons.ini, ammunition/usn_aim-174b.ini and ammunition/usn_aim-9x.ini — and usn_aim-9x is live on the mission's Ford air wing. That is a real cost for a weapon nothing fires. The decision for you: either accept that usn_gbu-24 is effectively a GBU-27 (harmless while unused), or drop a two-line SEST override restoring Mass/WarheadType/Power/AmmoPoints on usn_gbu-24.ini. I would take the SEST patch if you ever plan to field the A-6E, and otherwise do nothing.


*Sampled: Both files diffed in full, both versions. Also compared against the vanilla baseline at mods-source/_vanilla/original/ammunition/usn_gbu-24.ini, verified the winner's gbu-27 material asset exists, and resolved live consumers of both ids.*



## Reviewed and correct as-is  (63)


### 4 files: aircraft/usn_f-35c_squadrons.ini, ammunition/usn_f-35_gun_pod.ini, ammunition/usn_jsm.ini, ammunition/usn_jsm_…

**Mods** 3737267013 United States Naval Aviation (line 52) > 3508978375 [DEPRECATED] Lockheed Martin F-35C (line 75)  

**Winner** 3737267013 United States Naval Aviation · **Risk** high


usn_jsm.ini and usn_jsm_land.ini differ by exactly TWO lines each: MaxVelocity 665.0 kn (winner) vs 540.0 kn (loser), and ResourcesFolder assets/models/ammunition/jsm/ (winner) vs assets/models/weapon/ammunition/jsm/ (loser). Everything else - warhead, seeker, range, guidance - is identical. usn_f-35_gun_pod.ini differs by exactly ONE line: ResourcesFolder assets/models/aircraft/usn_f-35c/ (winner) vs assets/models/vechicle/aircraft/f-35/ (loser); the GAU-22 stats are identical. usn_f-35c_squadrons.ini is a total rewrite: winner has NumberOfSquadrons=13 with real named units and per-squadron modex texture sets, carrier emblems and ServiceDate gating - Squadron1 VFA-101 Grim Reapers (NJ) FRS ServiceDate=2012|2018, Squadron2 VX-9 (ED) 2017|, Squadron3 VFA-125 (NJ), Squadron4 VFA-147 (NF) CVN-73, Squadron5 VMFA-314 (NG) CVN-72, Squadron6 VMFA-314 (VW) ashore, Squadron7 VFA-97 (NE) CVN-70, Squadron8 VFA-86 (NH) CVN-71, Squadron9 VMFA-311 (WL), Squadron10 VFA-115 (NA) CVN-68, Squadron11 VFA-101 (AC) fill-in w/ cvn-69w emblem ServiceDate=2012|2018, Squadron12 VMFA-311 (AB) cvn-75w, Squadron13 VFA-125 (AG) cvn-74w; its [General] declares SerialnumberReferences=modex,left_flap_modex,right_flap_modex and EmblemReference=carrier_name_modex, liveries under aircraft/usn_f-35c/<sqn>/. Loser has NumberOfSquadrons=12, unnamed, no ServiceDate at all, SerialnumberReferences=modex and EmblemReference=Emblem only, liveries under aircraft/materials/usn_f-35c/<sqn>/, and its Squadron11 is VMFA-58 rather than VFA-101 (AC).


**Silently lost** — From the deprecated mod: its entire 12-squadron livery table (including the VMFA-58 scheme at Squadron11 and the vmfa-311_cag / vmfa-311_heart variants), its aircraft/materials/usn_f-35c/... livery path scheme, the more conservative 540 kn JSM, and the gun-pod/JSM model paths that point at the assets/models/vechicle/aircraft/f-35/ family. Zooming out: 3508978375 ships 13 override files and 12 of them are already shadowed by higher mods - the only .ini it still contributes to the game is ammunition/usaf_aim-120c7.ini. It is effectively dead weight on the ini side.


**Risk** — SPLIT OWNERSHIP, AND IT IS BROKEN. aircraft/usn_f-35c.ini is shipped by four enabled sources and won by SEST_Integration (line 1), which was built on 3607989779's airframe (ResourcesFolder=assets/models/vechicle/aircraft/f-35/, ResourcesRoot=f-35c.obj) - NOT on 3737267013's. The winning unit file's submodel map ends at SubModel17=modex and it has a [modex] section but NO [carrier_name_modex] section and no 'carrier_name_modex=carrier_name_modex' mapping line. Only 3737267013's own usn_f-35c.ini has those (line 492 mapping, plus the [carrier_name_modex] block pointing at aircraft/materials/emblem/emblem). Meanwhile the WINNING squadrons file (3737267013) declares EmblemReference=carrier_name_modex and hands every squadron an EmblemTexture (cvn-73w.png, cvn-72w.png, cvn-71w.png, cvn-70w.png, cvn-68w.png, cvn-69w.png, cvn-74w.png, cvn-75w.png). That reference has no target on the winning airframe, so the carrier tail emblems should not paint. Second dangling reference in the same [General] line: left_flap_modex and right_flap_modex are declared as serial-number references but are defined on NONE of the three F-35C unit files - they exist only on USNA's usn_fa-18e.ini and usn_ea-18g_2020.ini. Third: the winning gun pod points at assets/models/aircraft/usn_f-35c/ while the winning airframe uses assets/models/vechicle/aircraft/f-35/ - two different model families; the loser's gun-pod path actually matched the winning airframe. Fourth, a removal trap: assets/models/vechicle/aircraft/f-35/ - the folder the winning F-35C airframe loads from - is shipped ONLY by 3508978375 and 3413868677 (Red Storm Arsenal), and their f-35c_mat.ini copies are byte-identical. So the deprecated mod, despite losing every contested ini, must not be disabled unless Red Storm Arsenal stays enabled. No id collisions: ammunition and unit ids are filenames and every contested filename is a plain override. Caveat: this mirror tracks zero .obj/.png files, so I could not confirm that any livery, modex or emblem texture actually exists on disk - the dangling-reference finding rests on the .ini structure, which I did verify.


**Mission** — Yes, directly. Taskforce1Vessel1 is usn_cvn_ford_jsf with CustomAirGroup=True and 'usn_f-35c=Squadron1,24|Squadron11,10' - 34 F-35Cs drawn from exactly the two squadrons the winning file marks ServiceDate=2012|2018, against a mission Date=2026,8,24. Both squadrons exist in both files, so nothing dangles, but the service-date window is eight years stale for this scenario and the losing file had no…


**Recommendation** — Keep 3737267013 above 3508978375 - the deprecated mod contributes exactly one non-shadowed ini and its squadron table is unnamed and undated. Do not reorder. Instead fix the split ownership in the SEST layer: add the 'carrier_name_modex=carrier_name_modex' mapping line and the [carrier_name_modex] section (copy from 3737267013/aircraft/usn_f-35c.ini lines 492 and 607-612) into SEST_Integration/aircraft/usn_f-35c.ini, or strip EmblemReference from the squadrons file. Also drop left_flap_modex,right_flap_modex from SerialnumberReferences in usn_f-35c_squadrons.ini - the F-35C has no flap modex submodel in any version. Separately, decide whether Squadron1/Squadron11's ServiceDate=2012|2018 should be opened to 2012| for a 2026 scenario, and note that 3508978375 cannot be pruned from the collection while the F-35C airframe loads from assets/models/vechicle/aircraft/f-35/ unless 3413868677 remains enabled.


*Sampled: usn_f-35c_squadrons.ini read in full on both sides; usn_jsm.ini, usn_jsm_land.ini and usn_f-35_gun_pod.ini diffed in full. Also read: the winning aircraft/usn_f-35c.ini (SEST_Integration copy) submodel/material blocks, 3737267013/aircraft/usn_f-35c.ini and 36…*


### ammunition/mm_marte.ini (single file, but the one real defect in this cohort)

**Mods** 3629144864 Euromod - Main Pack (line 18, WINNER) > 3505420313 Italian Navy Mod (line 38)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** medium


Exactly one line differs across the whole file. Italian line 7 reads `SupplyCategory=Marte // For Supply System. Makes that presence of such category is required for replenishment of this weapon`. Euromod's copy omits it entirely. Everything else — Type=Missile, TargetType=ASuW, Mass=340, AmmoPoints=680, AirLaunched=True, all sensor/guidance/warhead values, and even the asset block (both use the vanilla ResourcesFolder=weapons/it_seakiller2/, ResourcesMesh=it_seakiller_2) — is byte-identical.


**Silently lost** — The `SupplyCategory=Marte` binding. With Euromod winning, grep across all of mods-source/ and _vanilla/ finds NO enabled ammunition file declaring SupplyCategory=Marte anywhere (remaining hits are Spanish squadron callsigns and a Marconi Martello radar comment — unrelated). Euromod's convention for helo-carried stores is SupplyCategory=AirTorpedo, which is what its own addon 3488139470 uses on the FREMM/PPA/Orizzonte flight decks.


**Risk** — GENUINE SPLIT-OWNERSHIP / DANGLING-REFERENCE DEFECT. Eight Italian vessel files — which are uncontested and therefore load from the LOSING mod — declare an accountable flight-deck pool keyed on the category the winning ammo file just dropped: mm_lha_garibaldi.ini:166, mm_lha_garibaldi_91.ini:166, mm_lha_garibaldi_94.ini:171 (all `FlightDeck_AccountableAmmunitionCategory_1=Marte,24/24`), mm_cgh_vittorio_veneto.ini:156 and mm_cgh_vittorio_veneto_91.ini:156 (Marte,12/12), mm_ddgh_durand_de_la_penne.ini:165, mm_ddgh_durand_de_la_penne_02.ini:167 and mm_ddg_audace_88.ini:164 (Marte,4/4). The four consuming aircraft (3505420313/aircraft/mm_ab212.ini, mm_ab212_91.ini, mm_sh-3.ini, mm_sh-3_91.ini) mount mm_marte. Net effect: those decks advertise a Marte pool that no ammunition claims, so AB-212 and SH-3 Marte rearming from those ships is unbacked by the supply system. No id collision and no crash risk — this is a silent supply-accounting break, not a load failure.


**Mission** — None currently. No mission under integration/missions/ fields any mm_* Italian vessel or Marte-carrying helicopter — the only Italian unit in any mission is ita_sh90 (see the MU-90 cohort). The defect is latent until an Italian Cold War surface group is fielded.


**Recommendation** — Do NOT reorder — moving 3505420313 above 3629144864 to recover one line would cost the asset consolidation on 9 other files and would demote the mission-fielded MU-90 (see that cohort). Instead ship a one-line SEST override of ammunition/mm_marte.ini containing Euromod's file plus `SupplyCategory=Marte` restored at line 7. Cost: one file, no side effects, since the two versions are otherwise byte-identical.


*Sampled: Full diff of both mm_marte.ini files; heads of both read line-by-line; Euromod's sibling eu_mm_marte.ini also read (it likewise has no SupplyCategory); repo-wide grep for the string `Marte`.*


### 1 file: ammunition/usn_agm-65f.ini

**Mods** 3606134711 Custom Loadout Editor (pos 11) > 3505420313 Italian Navy Mod (pos 38) > 3737267013 United States Naval Aviation (pos 59)  

**Winner** 3606134711 (Custom Loadout Editor) · **Risk** medium


This is not three versions of a weapon, it is one stub against two full definitions. The winner is a 17-line file whose first line is '#!alias ammunition/usn_agm-65b.ini' - it inherits everything from the AGM-65B and overrides only Mass=305, AmmoPoints=610, Power=28/ImpactSize=Medium/Penetration=Moderate, SeekerGain=0, SeekerFOV=90, SeekerPassiveRange=20, Zoom=3, TargetMemory=True, AntiCountermeasuresBonus=0.4, and a [Models] block containing nothing but ResourcesMaterialFolder=weapons/usn_agm-65/ + ResourcesMaterial=usn_agm-65f_mat.ini (which that mod does ship). The Italian copy is a full AGM-65B-derived Maverick: GuidanceType=1, MaxVelocity=620, MaxLaunchRange=17nm, MaxTurnRate=30, SeekerFOV=1.5 with SeekerGimbalFOV=90, Power=35/Small/Always, its own agm-65_ir.obj mesh with a SubModel1=IR_Nose (ir_mat.ini), full [Particles] and [Colliders]. The USNA copy is the most modern: full kinematics (ApplyKinematics=True, AccelerationTime=0.5/Acceleration=21.3 booster plus SustainerAccelerationTime=3.5/SustainerAcceleration=4.3, DragCoefficient=-1, TypicalTargetAlt/FiringAlt/LaunchVelocity, MaxFlightTime=100, TerminalLoft=True, TimeLimited=True), GuidanceType=1, MaxVelocity=500, MaxLaunchRange=17nm, MinLaunchAltitude=50ft, TerminalDiveDistance=3.5, Power=35/Medium/Moderate, NightVisionLevel=1.0, Zoom=2, AntiCountermeasuresBonus=0.45, CIWSDefenceBonus=30, MissileDefenceBonus=0.1, its own IR_Nose submodel with usn_ir_mat.ini, effects and colliders. Because the alias resolves to whichever usn_agm-65b.ini wins, and the Italian Navy Mod (pos 38) overrides vanilla's, the effective AGM-65F today = Italian AGM-65B base (GuidanceType=6 TV homing, MaxVelocity=820, MaxLaunchRange=13nm, MaxTurnRate=8, MinLaunchAltitude=20ft, agm-65_tv.obj mesh with a SubModel1=Glas cockpit-glass nose, CIWSDefenceBonus=30) with the Custom Loadout Editor's overrides layered on top.


**Silently lost** — Both full definitions. Concretely: USNA's entire kinematics model (booster + sustainer burn, drag solution, flight-time limit, terminal loft), its IR seeker (GuidanceType=1 - the AGM-65F is an imaging-infrared Maverick, and the effective weapon is now TV-guided via the Italian base's GuidanceType=6), its 17nm launch range (down to the base's 13nm), its NightVisionLevel=1.0, and its IR_Nose submodel. From the Italian copy: the modern gimballed seeker pair SeekerFOV=1.5 + SeekerGimbalFOV=90 and its own IR_Nose. The winner keeps only a material repoint and nine stat lines.


**Risk** — No id collision and no split ownership (a leaf ammunition file with no companion). The real exposure is a chained dependency the load order makes invisible. '#!alias' is not a vanilla construct - zero vanilla files use it, while 7 workshop mods do (Euromod 42 files, Italian-adjacent 3630495619 37, 3731208477 21, U.S. Navy 2027 20, Custom Loadout Editor 19, Dingtools 6, 3642656500 1) - so the winning AGM-65F has no Type=, TargetType=, guidance, kinematics, mesh, colliders or effects of its own and is entirely dependent on that directive resolving. Worse, its target is itself contested: ammunition/usn_agm-65b.ini exists in vanilla and in the Italian Navy Mod, and the Italian override wins, so the AGM-65F's guidance type, range, speed and mesh are set by a mod that is nowhere in this cohort's winner list. Any future reorder that moves the Italian Navy Mod, or an update to its AGM-65B, silently re-specifies the AGM-65F with no log line. Two consequences already visible today: the weapon is TV-guided (base GuidanceType=6) despite being the imaging-infrared variant, and its nose submodel is the base's SubModel1=Glas cockpit-glass rather than an IR seeker head.


**Mission** — No. Under the current order the weapon is not reachable on anything the mission fields. The only aircraft referencing usn_agm-65f are 3737267013's usn_fa-18e / usn_fa-18f / usn_fa-18f_blk3 / usn_fa-18c(n) - all four of which lose their aircraft files to 3606774881 (pos 17), whose usn_fa-18f_blk3.ini mounts usn_agm-65d, not -65f - plus the Custom Loadout Editor's own loadouts/usn_v-19a_loadouts.in…


**Recommendation** — No reorder. The Custom Loadout Editor is a framework mod at pos 11 whose whole purpose is to sit above everything and re-key weapons for its loadout system; demoting it to recover USNA's kinematics would be trading a framework's authority for a weapon no fielded aircraft carries. If you want the better AGM-65F physics anyway, the cheap fix is additive rather than ordinal - extend the Custom Loadout Editor's stub (or a SEST patch above it) with the handful of keys worth keeping: GuidanceType=1, MaxLaunchRange=17.0, and USNA's ApplyKinematics block. That preserves the alias mechanism while restoring IR guidance and range.


*Sampled: Read all three copies in full (1379 / 9700 / 10412 bytes). Followed the winner's alias target through both copies of ammunition/usn_agm-65b.ini (vanilla original and the Italian Navy override). Checked which aircraft actually mount the weapon.*


### 7 ammunition files: usn_rim-116c.ini (RAM Blk 2), usn_rim-162a.ini (ESSM Blk 1), usn_rim-174a.ini (SM-6), usn_rim-66m-2…

**Mods** 3606774881 "U.S. Navy 2027 Capabilities mod" (load-order rank 10 of 133) > 3629144864 "Euromod - Main Pack" (rank 11)  

**Winner** 3606774881 U.S. Navy 2027 Capabilities mod · **Risk** medium


This is not two rival authors; 3606774881 is a derivative re-tune of Euromod's own files (every winning missile file still points ResourcesFolder at assets/europack/models/ and ResourcesMaterialFolder at assets/europack/materials/... which only 3629144864 ships). What changed is the numbers. (1) Lethality: winner sets KillProbability=3.8 (ESSM), 3.6 (SM-6), 3.8 (both SM-2), 8.55 (RAM) against Euromod's 0.9 / 0.90 / 0.85 / 0.80. No vanilla ammunition file exceeds 0.85 (max sampled across all 415 vanilla ammo files). Winner also raises ECCM: RAM AntiCountermeasuresBonus/AntiJammerBonus 0.70/0.70 vs Euromod 0.40/0.35; ESSM 0.98/0.98 vs 0.50/0.55. (2) Warheads: winner switches ESSM and SM-6 to WarheadType=6 (fragmentation) with Power=21 / 52 and Penetration=Always, vs Euromod WarheadType=0 Power=21 / 35, Penetration=Heavy. (3) Kinematics are consistently slower but longer-legged: ESSM MaxVelocity 2250 kt vs 2700, boost 7.2 G / 20 s + 3.2 G / 18.2 s sustain vs 30.5 G / 3.0 s + 12 G / 5.0 s, MaxLaunchRange 30 nmi vs 27, MaxAttackAltitude 50 000 ft vs 120 000, MaxLoftAlt 25 000 ft vs 60 000. SM-6 MaxVelocity 2650 kt vs 3600, MaxLaunchRange 230 nmi vs 260, MaxLoftAlt 164 042 ft vs 110 000, MaxAttackVelocity 7000 kt vs 5000, LocalTerminalOnly=False vs True, TypicalTargetAlt 0 vs 80 000. RAM MaxVelocity 1040 kt vs 1650, MaxLaunchRange 10 nmi vs 7.5, MaxAttackAltitude 20 000 ft vs 50 000. (4) Seeker behaviour changes character on ESSM: winner sets GuidanceType=3 (active radar, SeekerActiveRange=15 nmi, SeekerFOV=45, SecondaryPassiveRadarGuidanceType=HomeOnJam) where Euromod has GuidanceType=2 (semi-active, SeekerActiveRange=0.0, SeekerFOV=90) — the winner's own inline comment reads "supposed to be 2". (5) The two SM-2 files are the least contested: Euromod's usn_rim-66m-2.ini is a 224-byte `#!alias ammunition/usn_rim-66k.ini` stub that only re-points the RIM-66M material, and usn_rim-66m-5.ini is a 608-byte `#!alias ammunition/usn_rim-66m-2.ini` stub carrying KillProbability=0.85 and InterceptSizePenaltyMultiplier=0.40. The winner replaces both with full 12 KB standalone definitions. (6) Sonobuoys are near-identical: DIFAR differs only by Mass 10 vs 9.5 kg and AmmoPoints 5 vs 11.875. DICASS differs by Mass 20 vs 16.3 kg, AmmoPoints 10 vs 20.375, and — materially — by `Sonar=SSQ-62G` (winner, resolving to its own [SSQ-62G] block: ActiveRange 18 km, ActiveGain 29, no ActiveFrequency) versus `Sonar=SSQ-62G_Sonar` (Euromod: ActiveRange 19 km, ActiveGain 30, ActiveFrequency=6500hz). Euromod's DICASS file also carries eight inline SonarAudio* keys the winner drops.


**Silently lost** — Euromod's tighter, vanilla-consistent SAM stat set (KP 0.80–0.90, higher top speeds, higher engagement ceilings, SARH ESSM) and its `#!alias` inheritance structure for the SM-2 pair. Concretely lost and worth noticing: (a) the DICASS ping audio — the winner's buoy points at sensor id SSQ-62G, and 3784474738/systems/SonarAudioClip_Mapping.ini only has a [SSQ-62G_Sonar] entry (verified: no [SSQ-62G] section), while the winner's ammo file also drops Euromod's inline SonarAudioClip=audio/environment/Sonar-AN-SSQ-62-Digital.wav block, so the active buoy is likely silent; (b) ActiveFrequency=6500hz on the DICASS sensor; (c) ESSM's 120 000 ft ceiling and SM-6's 3600 kt / 260 nmi profile. Nothing model- or asset-related is lost — the winner reuses the same europack meshes and materials. Note the systems/ sensor blocks MERGE key-by-key, so Euromod's SSQ-53H NarrowBandCapable=True / SignalProcessing=3 survive alongside the winner's AngularResolution=45.0 / RangeResolution=1000.0; that half is not lost.


**Risk** — No id collision — these are same-filename whole-file overrides of ammunition ids, which the engine handles cleanly. HARD CROSS-MOD DEPENDENCY (verified): the winner ships assets/models/vechicle only, and all five winning missile files reference assets/europack/materials/RIM-116/RIM-116E_mat.ini, RIM-162_ESSM/RIM-162-B1/RIM-162-B1_mat.ini, RIM-174_ERAM/RIM-174A_mat.ini and RIM-66/RIM-66M_mat.ini, none of which exist under 3606774881 — they exist only in 3629144864. 3606774881 cannot be run without Euromod enabled; if Euromod is ever unsubscribed these five missiles lose their materials. BALANCE ASYMMETRY: the 3.6–8.55 KillProbability band applies only to US SAMs; every PLA/Russian/European SAM in the collection sits at or below 1.0, so the winner tilts the AAW exchange sharply toward the US/allied side. SPLIT OWNERSHIP, benign: the DICASS ammunition file is won by 3606774881 while Euromod's [SSQ-62G_Sonar] sensor block still merges in — both sensor ids exist, nothing dangles, but the audio mapping keyed to the Euromod id no longer fires. Stray no-op line noted for the record: none in this cohort.


**Mission** — Yes, heavily. NORTHERN FRONT III FINAL NEWEST fields usn_ddg_arleigh_flt2A_119_2027 (x2), usn_ddg_arleigh_flt3_2027, usn_cg_ticonderoga_vls_2027 and usn_ddg-1000_cps on the US side — verified loadouts include 8x usn_rim-174a + 12x usn_rim-66m-5 (Flt IIA/Flt III) and 2x usn_rim-162a + 4x usn_rim-174a + 7x usn_rim-66m-2 (Ticonderoga). usn_p8_2027 appears twice as a unit plus a Squadron1,8 assignmen…


**Recommendation** — Keep 3606774881 above 3629144864 — inverting it would revert the entire purpose of the 2027 pack and is not recommended. Two targeted edits are worth more than a reorder: (1) in 3606774881/ammunition/usn_ssq-62g.ini change `Sonar=SSQ-62G` to `Sonar=SSQ-62G_Sonar` (or add an [SSQ-62G] section to 3784474738's SonarAudioClip_Mapping.ini) to restore the DICASS ping; (2) decide deliberately whether ESSM Blk 1 should be active-radar (GuidanceType=3) — the file itself flags this as wrong, and it makes ESSM autonomous after launch on every Aegis ship in the mission. If the KillProbability escalation is unwanted, patch the five values rather than moving the mod.


*Sampled: All 7 contested files read in full and diffed both directions. Supporting reads: /home/user/Seapower-mods/mods-source/3606774881/systems/sensors.ini ([SSQ-53H_Sonar] L215, [SSQ-62G] L227), /home/user/Seapower-mods/mods-source/3629144864/systems/sensors.ini ([…*


### aircraft/usn_e-2d.ini, aircraft/usn_e-2d_squadrons.ini, ammunition/usn_tank_370_f-18.ini

**Mods** 3737267013 United States Naval Aviation (rank 52) > 3413868677 Red Storm Arsenal (rank 132)  

**Winner** 3737267013 (United States Naval Aviation) wins all three · **Risk** medium


usn_e-2d.ini: sensors are the same five-plus-one blocks in both, but the winner declares NumberOfSensorSystems=5 while defining SensorSystem1-6, whereas the loser correctly declares 6. Winner adds [OpticalView] (binocular_7x50/10x50) which the loser lacks. Winner MaxFuel=5700 kg / PerEngineMaxPower=3,800,000 W; loser 6100 kg / 3,950,000 W. Winner deletes the loser's [WeaponSystem1] Hardpoint (NumberOfStations=0) so WeaponSystem1 becomes the chaff dispenser and NumberOfWeaponSystems drops 2->1. Winner sets AvailableLoadouts=Recon, loser AvailableLoadouts=AEW — both are valid engine loadout keywords (vanilla uses both). Winner enables SubModel44=CarrierName and a [CarrierName] mesh (usn_e-2c_carrier_name); loser comments that out and instead defines [Radar_Top] with an emblem material. usn_e-2d_squadrons.ini: winner has NumberOfSquadrons=9, all real CVW AEW units with dedicated E-2D liveries — Squadron1 Carl Vinson 600 NE (VAW-113), 2 Theodore Roosevelt 600 NH (VAW-115), 3 Nimitz 600 NA (VAW-116), 4 Abraham Lincoln 600 NG (VAW-117), 5 John C Stennis 600 AG, 6 Eisenhower 600 AC, 7 Gerald R. Ford 600 AJ, 8 George Washington 600 NF, 9 Harry S. Truman 600 AB, plus ServiceDate=2020|. Loser has NumberOfSquadrons=16 but every entry is a copied E-2C placeholder — liveries all point at aircraft/usn_e-2c/vaw-11x/ with LiveryTexture=usn_e-2c_tx, modex given without .png extensions, and the roster is named United States, Alan Shepard, James Monroe, Independence, Franklin D. Roosevelt, Enterprise, Benjamin Franklin, Ulysses S. Grant, Horatio Gates, John F. Kennedy, Shokaku, Zuikaku, Yamato, Musashi, Shinano, Kii. ammunition/usn_tank_370_f-18.ini: functionally identical — Fuel=1148, CircularErrorRadius=2000 in both; the only difference is ResourcesFolder (assets/models/aircraft/usn_fa-18c/ vs assets/models/vechicle/aircraft/fa-18c/), and each resolves inside its own mod.


**Silently lost** — From Red Storm Arsenal: E-2D squadrons 10-16 (JFK, Shokaku, Zuikaku, Yamato, Musashi, Shinano, Kii) and the 6-sensor declaration that actually switches the Defensive ECM on. Also its higher fuel/power numbers (6100 kg, 3.95 MW). The 370-gal tank loses nothing at all.


**Risk** — No id collision. SPLIT OWNERSHIP IS PRESENT AND DOES DANGLE, but between cohorts rather than inside this one: 3413868677 keeps sole ownership of usn_cvn_gerald_r_ford_variants.ini, usn_cvn_united_states_variants.ini, jmsdf_cv_shokaku_late_variants.ini and jmsdf_cvn_yamato_variants.ini (no other mod ships those filenames), and those four files make 10 live references to usn_e-2d Squadron10, Squadron11 (x2), Squadron12, Squadron13 (x2), Squadron14, Squadron15, Squadron16 — every one of which is undefined under the winning 9-squadron roster. Those Red Storm carriers will therefore ask for E-2D squadrons that no longer exist. (3606774881/vessels/usn_cvn_nimitz_2027s_adou_variants.ini line 220 has a Squadron10 reference but it is commented out.) Second defect, in the winner: NumberOfSensorSystems=5 with [SensorSystem6] #Defensive ECM (SystemName=AircraftDECM_Late, which is defined in _vanilla/original/systems/sensors.ini line 597) written but uncounted — the engine reads the first five, so the E-2D silently flies without ECM. Third, minor: the winner advertises AvailableLoadouts=Recon but defines only [WeaponSystem1Default] and [WeaponSystem1AEW]; there is no [WeaponSystem1Recon] block. Because the E-2D has zero weapon stations and both existing blocks carry identical ReadyUpTime=45 / CoolDownTime=120, the practical effect is the loadout label and role tag, not a broken rearm cycle. [AI] Role=AEW,ESM is set correctly in the winner. AN/APY-9 is defined in four enabled mods' systems/sensors.ini; systems merge, so the radar itself is safe.


**Mission** — Yes, hard-coded. The active mission sets a custom air group on its carrier task force at line 138: usn_e-2d=Squadron4,4. Under the winner that resolves to VAW-117 'Abraham Lincoln, 600 NG' with genuine E-2D livery; under the loser it would have been the placeholder 'Independence' in E-2C paint. Squadron4 exists on both sides, so no dangling reference for the mission itself. The mission also field…


**Recommendation** — Keep the order — 3737267013 is unambiguously the right E-2D (real VAW rosters, E-2D-specific liveries and modex, carrier-name decal), and the loser's 16-squadron roster is placeholder junk. Do not promote Red Storm Arsenal to recover squadrons 10-16; that would trade nine correct squadrons for sixteen wrong ones. Make two edits instead: (1) in 3737267013/aircraft/usn_e-2d.ini set NumberOfSensorSystems=6 so the E-2D regains AircraftDECM_Late — this is a one-character fix with direct mission benefit for the four Ford-embarked E-2Ds; (2) either rename AvailableLoadouts=Recon to AEW to match the defined [WeaponSystem1AEW] block, or add a [WeaponSystem1Recon] block. Separately, the four Red Storm carrier variants files need their Squadron10-16 E-2D references remapped into the 1-9 range, or those hulls will request nonexistent squadrons; none of them are fielded in the active mission, so this is a cleanup, not an emergency. usn_tank_370_f-18.ini needs no action whatsoever.


*Sampled: Full normalized diffs of all three files (3413868677's copies are CRLF, so a raw diff shows the whole file — I normalized before comparing). Read both sensor-system blocks, both weapon-system/loadout blocks, both squadron rosters in full, and cross-checked ev…*


### ammunition/usn_aim-120d-3.ini, usn_aim-260a.ini (2 files)

**Mods** 3607989779 (F-35C Lightning II Alt. Loadouts) > 3418252667 (F-22 Raptor)  

**Winner** 3607989779 (F-35C Lightning II Alt. Loadouts) · **Risk** medium


Both files are substantially rewritten, not cosmetic. AIM-120D-3 — winner: Mass=162 kg, AmmoPoints=1820, AirLaunched=True, WarheadType=6 (Fragmentation) with Penetration=Moderate, KillProbability=0.95, MidCourseCorrection=3, MaxLoftAngle=30 / MaxLoftAlt=100000 ft, TerminalApproachDist=14 nm, LocalTerminalOnly=False, IgnoreHeightDifferenceForTargetDist=True, full kinematics block (ApplyKinematics=True, MaxVelocity=2650 kt, MaxTurnRate=40, AccelerationTime=18 @8.367 G, DragCoefficient=5.962, LiftFactor=0.001, VelocityBleed=1, MaxFlightTime=165 s, TerminalLoft=True, TimeLimited=True, plus TypicalTargetAlt/TypicalFiringAlt=36000 range-calibration keys), MinLaunchRange=1.1 / MaxLaunchRange=120 nm, MaxAttackAltitude=80000, MaxAttackVelocity=2100, launch envelope 200–65000 ft, CircularErrorRadius=1.25 m (2.5 vs Large), SeekerGain=50 dB, SeekerFOV=135, seeker 15/15 nm, SecondaryPassiveRadarGuidanceType=HomeOnJam, PeakPower=14 kW. F-22 version: Mass=168, AmmoPoints=710, WarheadType=0 Penetration=Always, KillProbability=0.88, MidCourseCorrection=1, MaxLoftAlt=47000, TerminalApproachDist=11, LocalTerminalOnly=True, ApplyKinematics with MaxVelocity=1600 kt (boost 8 s @12.5 G + sustainer 4 s @3 G, DragCoefficient=-1), MaxFlightTime=130 s, MaxTurnRate=30, MinLaunchRange=0.8 / MaxLaunchRange=89.2 nm, SeekerGain=48, SeekerFOV=60, seeker 13/13 nm, SecondaryPassiveRadarGuidanceType=Full, Frequency=X-Band, PeakPower=10 kW, plus a SustainerEffect emitter. Models also differ: winner usn_aim-120c.obj / usn_aim-120d_mat.ini with Rotation=0,0,45; loser AIM-120C.obj / aim-120d-3_mat.ini. AIM-260A — winner: Mass=154 kg, MinLaunchRange=2.0 / MaxLaunchRange=170 nm, MaxFlightTime=215 s, MaxVelocity=2650 kt, MaxTurnRate=40, MaxLoftAngle=30 / MaxLoftAlt=100000 ft, TerminalApproachDist=14, KillProbability=0.95, WarheadType=6 Penetration=Moderate, AntiCountermeasuresBonus=0.75 / AntiJammerBonus=0.75, SeekerFOV=135, seeker 15/15 nm, PeakPower=15 kW, launch envelope 200–65000 ft, CircularErrorRadius=1.25/2.5 m. F-22 version: MaxLaunchRange=113.5 nm, MaxFlightTime=160 s, MaxVelocity=1600 kt with TerminalVelocity=3600, MaxTurnRate=30, MaxLoftAngle=20 / MaxLoftAlt=52000, TerminalApproachDist=17, KillProbability=0.85, WarheadType=0 Penetration=Always with FuzeProximityDistance=0.5 ('kinetic-energy weapon'), AntiCountermeasuresBonus=0.7 / AntiJammerBonus=0.6, SeekerFOV=45, seeker 19/19 nm, PeakPower=12 kW, MinLaunchRange=5, and MinLaunchAltitude=32000 — a hard high-altitude-only launch gate. The F-22 file also carries a typo, 'MMass=176' instead of Mass=176, so it declares no valid mass key at all.


**Silently lost** — The F-22 mod's own weapon balance for its own aircraft: the 32,000 ft JATM launch floor, the 5 nm minimum range, the narrower SeekerFOV (45/60 vs 135) paired with a longer seeker range (19 nm vs 15 nm), the X-Band/Full passive-radar guidance keys, the kinetic-kill 0.5 yd proximity fuze characterisation, TerminalVelocity=3600, and the AIM-120D-3 sustainer visual effect. Also lost, and this one is a benefit of losing: the MMass=176 typo never loads.


**Risk** — No id collision (no id key in either file). Asset dependency worth recording: 3607989779 ships no aim-120 or aim-260 assets at all — its only asset files are assets/models/weapon/ammunition/aim-9/usn_aim-9xb2+_mat.ini and assets/models/ammunition/gbu-31/textures/gbu-31_mat.ini. Its usn_aim-120d-3.ini points at assets/models/ammunition/aim-120/usn_aim-120d_mat.ini, which exists in exactly one enabled mod, 3737267013 (line 59); its usn_aim-260a.ini points at assets/models/ammunition/aim-260/aim-260a_mat.ini, which exists in exactly one enabled mod, 3418252667 (line 81) — the mod it just beat. Both resolve today, but disabling either 3737267013 or 3418252667 would leave the winning AMRAAM/JATM with no material. Genuine SPLIT OWNERSHIP involving this cohort's winner: usn_f-35c.ini is won by 3607989779 (line 21) while usn_f-35c_squadrons.ini is won by 3737267013 (line 59), and they do not cohere — the winning squadron file declares SerialnumberReferences=modex,left_flap_modex,right_flap_modex and EmblemReference=carrier_name_modex across 13 squadrons, but the winning unit file defines submodels only up to SubModel17=modex and contains no left_flap_modex, right_flap_modex or carrier_name_modex (3737267013's own usn_f-35c.ini does define carrier_name_modex at line 607, so the breakage is created purely by the split). usn_f-35c is not fielded in the active mission, so this is a latent cosmetic defect, not a live one.


**Mission** — High — this is the most mission-consequential cohort of the nine. NORTHERN FRONT III FINAL NEWEST fields usaf_f-22_s6 x8, and every one is LoadoutVariant=AirToAirIntercept, whose [WeaponSystem1AirToAirIntercept] block in mods-source/3418252667/aircraft/usaf_f-22_s6.ini is Station1–6 = usn_aim-260a: 48 JATM rounds. Under the current winner those are 170 nm / 215 s / KillProbability 0.95 / AntiJam …


**Recommendation** — Keep 3607989779 on top, but go in with eyes open. The winner is the better-maintained file — it has the complete drag/lift/Typical* range-calibration model, supply AmmoPoints, explicit CEP values, and it does not carry the loser's MMass typo. Do not promote 3418252667: the two mods contest only usn_agm-88g.ini, usn_aim-120d-3.ini and usn_aim-260a.ini, so a swap is technically cheap, but it would hand the F-22 a JATM that cannot launch below 32,000 ft and would drag usn_agm-88g along with it. What you should decide deliberately is the balance: the current setup gives the mission's blue CAP a ~50 % reach increase (170 vs 113.5 nm) over what the F-22's own author intended, which reshapes the opening air engagement. If you want the F-22 author's envelope without giving up the winner's file quality, add a SEST override of usn_aim-260a.ini that keeps the winner's kinematics but restores MaxLaunchRange=113.5 and MinLaunchAltitude=32000.


*Sampled: Both files diffed in full between the two mods. Read mods-source/3418252667/aircraft/usaf_f-22_s6.ini loadout block, the mission's F-22 entries in 'integration/missions/NORTHERN FRONT III FINAL NEWEST.ini', both mods' asset trees, and the winner's [Models] bl…*


### ammunition/usaf_aim-120c7.ini (1 file)

**Mods** 3508978375 [DEPRECATED] Lockheed Martin F-35C > 3514484654 RAAF F-35A Lighting II  

**Winner** 3508978375 ([DEPRECATED] Lockheed Martin F-35C) · **Risk** medium


The two files disagree about what missile they even are. Winner header: '# AIM-120C-7 AMRAAM'. Loser header: '# AIM-120B AMRAAM' — in a file named usaf_aim-120c7.ini. Winner: AmmoPoints=1720, AirLaunched=True, MidCourseCorrection=3, MaxLoftAngle=15.0, MaxLoftAlt=50000, MaxVelocity=1600, VelocityBleed=0.5, AccelerationTime=4, Acceleration=10.4, MaxTurnRate=30.0, MaxTurnG=35, MaxFlightTime=120, MinLaunchRange=0.8, MaxLaunchRange=65 nm, SeekerGain=55.0, SeekerActiveRange=15, Frequency=X-Band, PeakPower=12.0 kW, AntiCountermeasuresBonus=0.6, AntiJammerBonus=0.6, plus a sustainer effect block (SustainerEffect / SustainerEffectStartTime=2.0). Loser: no AmmoPoints, no AirLaunched, MidCourseCorrection=1, a DUPLICATE KillProbability key (0.85 declared in the warhead block, then KillProbability=0.5 re-declared in guidance), FuzeProximityDistance=10, MaxLoftAngle=50.0, MaxLoftAlt=40000, MaxVelocity=2666 kn, Acceleration=18.0, MaxTurnRate=40.0, MaxLaunchRange=70 nm, SeekerGain=60.0, PeakPower=15.0, AntiCountermeasuresBonus=0.1, AntiJammerBonus=0.1, no sustainer effect.


**Silently lost** — Nothing worth keeping. What is lost is a mislabelled AIM-120B masquerading under the C-7 filename, with a 2666-kn (roughly Mach 4.5) top speed, a duplicated KillProbability key whose two values disagree (0.85 vs 0.5), no supply cost, and countermeasure/jammer resistance of 0.1 against the winner's 0.6 — which in a heavy-ECM Indo-Pacific engagement is the difference between a working AMRAAM and a decoy magnet.


**Risk** — No id collision, no split ownership at the ammunition level. The load-order outcome here is correct, but the DEPENDENCY is fragile and that is the risk: the only live consumer of usaf_aim-120c7 is raaf_f-35a, whose unit file is won by the project's own SEST_RAAF_F-35A_JATM pack — so a SEST-owned aircraft at the very top of the order is reaching down to a workshop mod marked [DEPRECATED] at line 82 for its primary BVR weapon. If 3508978375 is ever unsubscribed or falls below 3514484654, 46 mission F-35As silently swap to a 0.1-ECCM AIM-120B with a duplicate kill-probability key, with no error and no log line. This is exactly the split-ownership failure mode, one level down: SEST owns the aircraft, a deprecated third party owns its missile.


**Mission** — YES — this is the most mission-critical cohort of the nine. raaf_f-35a is fielded at RAAF Darwin (Squadron1,6|Squadron2,6|Squadron3,6) and RAAF Scherger (Squadron2,14|Squadron3,14) — 46 airframes, the backbone of the allied air order of battle — and SEST_RAAF_F-35A_JATM's raaf_f-35a.ini loads usaf_aim-120c7 on Station1. Every one of those aircraft is currently armed by 3508978375's file.


**Recommendation** — Keep 3508978375 above 3514484654 — the current order is right and is actively saving the mission's F-35A force from a broken weapon file. But do not leave this resting on a deprecated mod: pull ammunition/usaf_aim-120c7.ini into a SEST pack (a verbatim copy of 3508978375's version is enough) so the RAAF F-35A's AMRAAM is owned by the same layer that owns the aircraft. That removes the dependency on a mod the collection is already flagging for removal, at zero gameplay cost.


*Sampled: Both versions read and diffed in full (General, Guidance, Kinematics, Seeker, ECCM, Particles blocks). Traced every consumer of usaf_aim-120c7 and confirmed the winning consumer file (mods-source/_vanilla/SEST_RAAF_F-35A_JATM/aircraft/raaf_f-35a.ini, Station1…*


### aircraft/usn_ea-18g.ini, aircraft/usn_fa-18e.ini, aircraft/usn_fa-18f.ini, aircraft/usn_fa-18f_blk3.ini, ammunition/usn…

**Mods** 3606774881 U.S. Navy 2027 Capabilities (order line 17) > 3430135740 F/A-18 Murder Hornet w/ AIM-174B (22) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (35) > 3737267013 United States Naval Aviation (59)  

**Winner** 3606774881 for ammunition/usn_aim-174b.ini ONLY. For all four aircraft/*.ini the stated winner is itself outranked: int… · **Risk** medium


Sampled in full: all four versions of usn_fa-18e.ini and usn_aim-174b.ini; loadout-name lists, station->ammo maps, flight-model and sensor blocks for all four versions of usn_fa-18f.ini, usn_fa-18f_blk3.ini and usn_ea-18g.ini; plus the SEST_Integration copies for line/loadout counts. LOADOUTS (usn_fa-18e.ini): 3606774881 = 25 named loadouts, all Murder-Hornet-family (MH_CAP_120, MH_CAP_120EF, MurderHornetCAP/GunSlinger/FistFight/Interceptor/Penetrator/SEAD/AntiShip, MH_AntiShipEF, MH_LRASM, MH_QCSK31(EF), MH_QCSK38(EF), StrikeJDAM, StrikeGBU, CASAGM, MH_CASAGMEF, CASSDB, MH_CASSDBEF, Empty). 3430135740 = 10 (Default, MurderHornet* set incl. StrikeHeavy/CAS). 3426791311 = 8 generic (Default, AirToAir, AirToAirLongRange, Strike, Antiship, AntishipLongRange, CAS, SEAD). 3737267013 = 21 (adds AirToAirIntercept, Strike2, StrikePrecision1-3, AntiShip2, AntiShipHeavy, CAS2, CASHeavy, SEAD2, SEAD3 and a Tanker loadout). SEST_Integration = 38 loadouts, 1521 lines vs 3606774881's 1422 — a superset rebuild. WEAPONS: 3606774881 arms 18 distinct stores incl. usn_aim-120d-3, usn_aim-9x, usn_aim-174b, usn_agm-88g, usn_agm-84n, usn_gbu-53, usn_gbu-75_jdam_lr, usn_gbu-31_qcsk/usn_gbu-38_qcsk (Quicksink), b-2_lrasm, b-2_jsow(_clus). 3737267013 uniquely carries usn_agm-158b-2 (JASSM-ER), usn_agm-158c-3, usn_adm-160b (MALD, F-model), usn_aim-424, usn_agm-65f, usn_gbu-32v2, usn_d-704 buddy-refuel store. 3426791311 is a 2010s fit (usaf_aim-120c, usn_aim-9m, usn_agm-88e). 3430135740 is the smallest set (9-11 stores). FLIGHT MODEL (usn_fa-18e): 3606774881/3430135740/3426791311/SEST all agree — EmptyMass 12701 kg, MaxFuel 6052 kg, 79380 N per engine AB, Ceiling 60000 ft, MaxSpeedAtSeaLevel 620 kt. 3737267013 is the outlier: EmptyMass 13900, MaxFuel 5100, 98000 N, Ceiling 55000, 710 kt. Radar is AN/APG-79(V) in both 3606774881 and 3737267013. ammunition/usn_aim-174b.ini — four genuinely different missiles: 3606774881 (WINNER): MaxLaunchRange 316 nm, MaxVelocity 2650 kt, Mass 705 kg, MaxLoftAlt 150000 ft, MaxFlightTime 368 s, SustainerAccelerationTime 65 s, WarheadType 6 / Power 52, MidCourseCorrection=3, SecondaryTargetType=ASuW, MinLaunchAltitude 200 ft, KillProbability 1.02, AntiCM/AntiJammer 0.98/0.98, SeekerActiveRange 15 nm. 3430135740: 130 nm, 2333 kt, MaxLoftAlt 99000, MidCourseCorrection=1, SeekerActiveRange 65 nm, AntiCM 0.90. 3426791311: 250 nm, 1600 kt, MinLaunchAltitude 40000 ft, MinLaunchRange 20 nm, MaxFlightTime 240 s. 3737267013: 216 nm, 1600 kt, staged motor (22 G for 2 s then 4.7 G for 28 s), MinLaunchAltitude 35000 ft, KillProbability 0.9. English display name is identical across all three that define it ("AIM-174B, Gunslinger, AAM") so the language merge is harmless.


**Silently lost** — From 3737267013 (United States Naval Aviation): the entire long-range strike set for the Super Hornet — usn_agm-158b-2 JASSM-ER, usn_agm-158c-3, usn_adm-160b MALD decoys on the F-model, usn_aim-424, usn_gbu-32v2 — plus the WeaponSystem1Tanker loadout built around usn_d-704 (organic buddy tanking is gone from the air wing) and the graduated Strike2/StrikePrecision1-3/SEAD2-3/CASHeavy ladder. From 3426791311: the 2010s-era AIM-120C/AIM-9M/AGM-88E fit, useful only for pre-2020 scenarios. From 3430135740: nothing of substance in the aircraft files — its content survives in the 2027 pack, which is a direct descendant (identical Murder Hornet loadout names). Because SEST_Integration wins all four aircraft files, 3606774881's own 25 loadouts are ALSO silently lost; the player gets SEST's 38. Most consequential loss is in a companion file, not a cohort file: aircraft/usn_fa-18e_squadrons.ini is NOT shipped by SEST_Integration or by 3606774881, so it falls to 3430135740, which declares NumberOfSquadrons=20 but defines only 2 [Squadron] blocks (VFA-115, VFA-143). 3737267013's 49-squadron version — the full VFA roster with separate CAG and line-bird entries keyed to specific hulls (VFA-14/25/27/31/34/37/81/83/87/94/105/106/113/122/131/136...) — is the loser and is discarded.


**Risk** — No id collisions: all four mods ship the same filenames, no mod registers a duplicate unit id. No dangling ammunition: every StationN target in all four versions resolves to either a mod-supplied ammunition/*.ini or a vanilla one (usaf_tank_610_f-15, usn_gbu-10, usn_gbu-12 are vanilla; usn_tank_1200_f-18 and usn_tank_610_f-18 are supplied by SEST_Integration). SPLIT OWNERSHIP (confirmed, four instances): (1) aircraft/usn_fa-18e.ini won by SEST_Integration but aircraft/usn_fa-18e_squadrons.ini won by 3430135740 — and that file is internally incoherent (NumberOfSquadrons=20, 2 defined). (2) aircraft/usn_fa-18e_late.ini won by 3606774881 while usn_fa-18e_late_squadrons.ini exists only in 3426791311, a mod flagged deprecated/unsubscribe-candidate. (3) aircraft/usn_ea-18g_2020s.ini won by SEST_Integration while usn_ea-18g_2020s_squadrons.ini exists only in 3426791311. (4) aircraft/usn_ea-18g_2020.ini won by SEST_Integration while usn_ea-18g_2020_squadrons.ini exists only in 3737267013. Unsubscribing 3426791311 as the catalog suggests would strip the squadron definitions out from under two units that SEST/2027 still register. The F/F-blk3/EA-18G squadron files are coherent — SEST's copies declare 9/8/6 squadrons and define exactly 9/8/6. Not verifiable here: mods-source is an .ini-only export (10341 .ini, zero binary assets, and empty directories are dropped), so livery/emblem texture presence — e.g. 3430135740's ResourcesLiveryFolder=assets/textures/fa-18e/ vs 3737267013's aircraft/usn_fa-18e/ — cannot be confirmed from this repo.


**Mission** — YES, directly. The active mission NORTHERN FRONT III FINAL NEWEST fields usn_cvn_ford_jsf as Taskforce1Vessel1 with VariantReference=Variant1, whose CustomAirGroup is usn_fa-18e=Squadron1,12|Squadron2,12 + usn_fa-18f=Squadron1,12 + usn_ea-18g=Squadron1,6 + usn_f-35c=Squadron1,24. So 24 Super Hornets, 12 F-model and 6 Growlers spawn from these exact files every run, and their AIM-174B is the 316 n…


**Recommendation** — Do NOT reorder. The four aircraft files are decided by SEST_Integration regardless of how these four workshop mods are arranged, and for usn_aim-174b.ini the 2027 pack is the right winner: it is the only version whose parameters match the loadouts SEST actually fields (Station32/33 AIM-174B on MurderHornetCAP), it has no MinLaunchAltitude floor so carrier-launched shots work at any altitude, and it adds SecondaryTargetType=ASuW. If 316 nm / Mach 4.5 reads as too hot for your balance, edit that one file's MaxLaunchRange in place rather than promoting a loser — promoting 3737267013's 216 nm version would drag 11 other files with it (see cohort risk maths below). The one change worth making: add aircraft/usn_fa-18e_squadrons.ini to SEST_Integration, copied from mods-source/3737267013/aircraft/usn_fa-18e_squadrons.ini (49 squadrons). Cost: one new file in the pack that already sits at the top of the order, zero load-order churn, and it restores the full VFA roster to the mission's 24 Super Hornets. The alternative — moving 3737267013 above 3430135740 — I measured: it flips 12 files, and 11 of them are collateral (usn_aim-9l, usn_aim-9m, usn_mk-82/83/84, usn_agm-65d, usn_agm-88e taken from 3426791311; usn_gbu-24 from 3430135740; usmc_25mm_gunpod, usmc_alq-164, usmc_tank_230_av-8b from 3505420313). Those are shared vanilla-named stores used across many aircraft, so that reorder is the worse trade.


*Sampled: Read in full: mods-source/{3606774881,3430135740,3426791311,3737267013}/aircraft/usn_fa-18e.ini and .../ammunition/usn_aim-174b.ini. Read selectively (section lists, WeaponSystem names, StationN->ammo maps, [Performance]/[SensorSystem] blocks): the four versi…*


### aircraft/usn_ea-18g_squadrons.ini, usn_fa-18e_squadrons.ini, usn_fa-18f_blk3_squadrons.ini, usn_fa-18f_squadrons.ini (4…

**Mods** 3430135740 F/A-18 Murder Hornet with AIM-174B (line 22) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (line 35) > 3737267013 United States Naval Aviation (line 59)  

**Winner** 3430135740 F/A-18 Murder Hornet with AIM-174B - but only for usn_fa-18e_squadrons.ini; SEST_Integration (line 8) outran… · **Risk** medium


Two different lineages. Murder Hornet's files are small and point at the MyGo texture layout: usn_fa-18e_squadrons has [Squadron1] #VFA-115 and [Squadron2] #VFA-143 with ResourcesLiveryFolder=assets/textures/fa-18e/; fa-18f has 10 squadrons that are mostly Ace Combat fiction (mobius.png/Nation=ISAF, erusea.png/Nation=Erusea, blekan.png/Nation=Belkan, golem_1..4.png/Nation=Osea) plus vfa-122, vfa-103 and raaf_f18f; ea-18g has 5-6 VAQ liveries; fa-18f_blk3 has 7 (vfa-22/41/97/102/103/106/122) and is BYTE-IDENTICAL to the deprecated 3426791311 copy. USNNA's files are an order of magnitude richer and use its own layout: 49 named F/A-18E squadrons (e.g. [Squadron1] #VFA-14 Top Hatters (NG) 'CAG' CVN-72 with ResourcesSerialnumberFolder=aircraft/usn_fa-18e/vfa-14/modex_cag/, SerialnumberTextures=200.png..214.png, EmblemTexture=cvn-72.png, LiveryTexture=vfa-14_cag.png), 24 F/A-18F, 24 F/A-18F Blk3 (with per-squadron FueltankTextures) and 16 EA-18G, plus ServiceDate gates (fa-18e ServiceDate=1999|, blk3 2020|). The [General] blocks disagree: Murder Hornet declares SerialnumberReferences=Modex,Left_Flap_Modex,Right_Flap_Modex,Rudder_Modex and EmblemReference=Emblem; USNNA declares modex,left_flap_modex,right_flap_modex and EmblemReference=carrier_name_modex. Two counting bugs in the winner: usn_fa-18e_squadrons declares NumberOfSquadrons=20 but defines only 2 sections, and usn_ea-18g_squadrons declares 5 but defines 6.


**Silently lost** — USNNA's entire real-squadron database for the Super Hornet family - 49 + 24 + 24 + 16 squadron entries with modex serial-number sheets, carrier emblems (cvn-70/71/72/75), CAG vs TPS scheme pairs and per-squadron fuel-tank textures - is silently ignored. The deprecated 3426791311 loses 6 more F/A-18E liveries (vfa-27/31/94/105 etc.) and 4 more F/A-18F liveries (vfa-22/41/97/102). In practice only the fa-18e loss is live, because SEST_Integration wins the other three files.


**Risk** — SPLIT OWNERSHIP, confirmed and real: aircraft/usn_fa-18e.ini, usn_fa-18f.ini, usn_fa-18f_blk3.ini and usn_ea-18g.ini are all won by 3606774881 (U.S. Navy 2027 Capabilities, line 17) - ABOVE all three mods in this cohort - and 3606774881 ships no *_squadrons.ini. Its unit files add 12 modex references each (SubModel entries modex / left_flap_modex / right_flap_modex / carrier_name_modex with [carrier_name_modex] Mesh=carrier_name_modex, ResourcesMaterialFolder=aircraft/materials/emblem/), i.e. they are written for a USNNA-style squadron file. The winning Murder Hornet squadron file supplies no ResourcesSerialnumberFolder, no SerialnumberTextures and EmblemTexture=transparent from textures/Misc/, and its [General] names Rudder_Modex and Emblem, which do not exist as submodels in the 2027 unit file at all. Result: the 2027 Hornets' modex and carrier-name decal nodes get no per-squadron textures and fall back to the generic aircraft/materials/numbers/ material - cosmetic, not a crash. Note also that neither 3430135740 nor 3426791311 defines any modex submodel in its own fa-18e/f files (grep count 0), so those references were already inert in the MyGo lineage. No id collision - all four are same-filename overrides. Livery paths are not dangling: assets/textures/fa-18e|fa-18f|fa-18f_blk3|ea-18g belong to 3426791311, which is still enabled - so if that deprecated mod is ever unsubscribed, the winning squadron files lose their textures AND 3606774881 loses the f-18e/f-18f/ea-18g meshes it points at (assets/models/vechicle/aircraft/f-18e/). Texture files themselves could not be verified: this export contains zero .png files.


**Mission** — Indirect. The mission's CustomAirGroup on Taskforce1Vessel1 (usn_cvn_ford_jsf) fields usn_ea-18g=Squadron1,6|Squadron2,6 and usn_fa-18f_blk3=Squadron3,8|Squadron4,8|Squadron5,8, and two more taskforce entries use ea-18g Squadron2/Squadron3 and fa-18f_blk3 Squadron1-5. Those three squadron files are won by SEST_Integration (6, 9 and 8 squadrons respectively, Murder-Hornet-derived liveries with the…


**Recommendation** — Do not reorder. The winner is the coherent choice - Murder Hornet's texture paths match the MyGo/2027 model lineage that actually wins the base unit files, whereas promoting USNNA would pair aircraft/usn_fa-18e/vfa-14/*.png (UV-mapped for USNNA's own mesh at assets/models/aircraft/usn_fa-18e/) with the MyGo mesh, which is the classic split-ownership livery break. Instead, extend SEST_Integration with a usn_fa-18e_squadrons.ini exactly as it already does for the other three: keep Murder Hornet's assets/textures/fa-18e/ paths, fix NumberOfSquadrons to match the sections present, and add the modex/carrier-name keys the 2027 unit file expects. Also fix ea-18g's declared 5-vs-6 in the SEST copy if it inherited it. Keep 3426791311 subscribed until 3606774881 stops referencing assets/models/vechicle/aircraft/f-18e/.


*Sampled: All four squadron files read in full in 3430135740; diffed against 3426791311 and 3737267013. Also read the base unit files usn_fa-18e.ini in 3606774881, 3430135740, 3426791311 and 3737267013, and integration/dist/SEST_Integration/aircraft/{usn_ea-18g,usn_fa-…*


### ammunition/plan_cal_100mm.ini, ammunition/plan_cal_130mm.ini (2 files)

**Mods** 3775128499 Modern PLAN Systems (line 19) > 3413868677 Red Storm Arsenal (line 139)  

**Winner** 3775128499 Modern PLAN Systems · **Risk** medium


plan_cal_100mm: winner has MuzzleVelocity=880 (RSA 870), MaxRange=15000 m (RSA 17000 - the winner is SHORTER-ranged), CircularErrorProbable=52 m (RSA 100), FuzeProximityDistance=5 m (RSA 15), KillProbability=0.01 per round vs RSA 0.002 - a 5x better anti-missile chance - and adds Mass=28 / AmmoPoints=28 for the supply system. plan_cal_130mm: the winner FLIPS the role - TargetType=AAW with SecondaryTargetType=ASuW, where both RSA and vanilla have TargetType=ASuW / SecondaryTargetType=AAW. It also raises MaxRange to 29500 m (RSA 25540, vanilla 27080), MuzzleVelocity 880 (RSA 850, vanilla 950), CEP 45 m (RSA and vanilla 100/140), Power 7 (RSA/vanilla 6), KillProbability 0.07 (RSA/vanilla 0.01), adds Mass=41 / AmmoPoints=41, and downgrades HitGroundExplosionClass from MediumGroundHitExplosions to SmallGroundHitExplosions.


**Silently lost** — From Red Storm Arsenal: the longer 17 km reach of the 100 mm and the ASuW-primary targeting plus the Medium ground-impact effect class on the 130 mm. RSA's copies carry no content the winner lacks - both are single-purpose ballistics files with identical section structure.


**Risk** — No id collision, no dangling refs, no split ownership - Modern PLAN Systems owns both the ammo and the hulls that fire it, which is exactly the pairing you want. Two things to be aware of. First, the 130 mm TargetType=AAW flip is a behavioural change, not just a stat change: it makes the H/PJ-38 an air-defence weapon first on every 055/052D in the mission (and on the vanilla Luda), so those ships will commit main-gun rounds against aircraft/missiles by preference. Combined with KillProbability=0.07 (7x vanilla) this measurably stiffens PLAN air defence - intended by the author, but it is the single biggest live consequence in this cohort. Second, the winner's 100 mm is 2 km shorter-ranged than RSA's; harmless here because no 100 mm ship is fielded.


**Mission** — Yes, directly fielded. plan_cal_130mm is the main gun round of four plan_type_055_2026 and of plan_type_052d_p3 and plan_type_052d_p4 (2 each) in NORTHERN FRONT III FINAL NEWEST - all three hulls come from 3775128499 itself and reference Ammunition1=plan_cal_130mm. It also overrides a VANILLA ammunition id, so the base-game plan_dd_luda1 is re-statted too. plan_cal_100mm is not fielded - its cons…


**Recommendation** — Keep as is. Modern PLAN Systems is the 2020s PLAN systems database and the direct owner of the mission's Type 055/052D hulls, so its ballistics must outrank Red Storm Arsenal's generic copies - and RSA is correctly parked at the bottom of the order (line 139) for exactly this reason. No change warranted. If the AAW-primary 130 mm proves too strong in play, edit TargetType in a SEST pack rather than promoting RSA, which would also pull in its downgraded CEP=100 and its weaker KillProbability.


*Sampled: Both files read in both mods (full diff). Also diffed plan_cal_130mm against the vanilla copy at mods-source/_vanilla/original/ammunition/plan_cal_130mm.ini, and read the gun mounts of mods-source/3775128499/vessels/plan_type_055_2026.ini and plan_type_052d_p…*


### ammunition/dts_gbu-31.ini (1 file)

**Mods** 3760871384 Dingtools Weapon Pack (line 16) > 3652097318 B-1B Lancer (line 66) > 3741944366 B-52H Stratofortress (line 68) > 3553116604 F-15E StrikeEagle (line 79)  

**Winner** 3760871384 Dingtools Weapon Pack · **Risk** medium


Four near-identical files with a handful of meaningful deltas. LandAttackCapability: winner and B-52H say Installation; B-1B and F-15E say All - i.e. the losers let the JDAM be assigned to MOBILE land targets, the winner restricts it to fixed installations. MidCourseCorrection: winner 3, all three losers 0. TerminalApproachDist: winner 10 nm; B-1B and F-15E 1000 nm (effectively 'seeker always on'); B-52H 2 nm. MaxTurnRate: winner 15 deg/s vs 6 in the B-1B and F-15E copies (B-52H matches the winner). Seeker block: winner SeekerFOV=1 and SeekerPassiveRange=1 nm vs 0.01 and 50.0 nm in the B-1B/F-15E copies. The B-52H copy is otherwise the closest to the winner - it differs only in MidCourseCorrection, TerminalApproachDist and whitespace. Warhead, mass, model and effects are identical across all four.


**Silently lost** — From the B-1B and F-15E copies: LandAttackCapability=All - the ability to task this JDAM against mobile land units - plus their 50 nm passive-seeker range and always-on terminal seeker. From the B-52H copy: nothing of consequence (MidCourseCorrection=0 and a 2 nm terminal-seeker turn-on).


**Risk** — No id collision, no split ownership, no dangling references - dts_gbu-31 is not a vanilla id and the winner's model/effects paths are the same as the losers'. The live risk is purely behavioural: the winner narrows what the mission's B-1Bs and F-15EXs may be tasked against. Two smaller oddities worth recording: MidCourseCorrection=3 sits outside the range the file's own comment documents (0=None, 1=Radio Command, 2=Wire Guided) - the same value USNNA uses on its GBU-53, so it is probably a newer datalink mode rather than a typo, but it is unverified; and the B-1B/F-15E copies' TerminalApproachDist=1000 nm is itself clearly a placeholder, so those copies are not credible alternatives even where they are more permissive.


**Mission** — Yes, on both mission-fielded carriers of this weapon. Two usaf_b-1b_dts are fielded and their StrikeJDAM loadout is Station1=dts_gbu-31|MK-84 (three station blocks). Four usaf_f-15ex_SEII are fielded and mods-source/_vanilla/SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII.ini also loads dts_gbu-31. The mission is full of MOBILE land targets - four pla_df-26b_tel, seven shahed_tel, three wp_sejjil_te…


**Recommendation** — Keep the order - it is the author-mandated arrangement (both the B-1B and B-52H catalogue entries quote 'Keep Dingtools Weapon Pack ABOVE all dingtools mods', and the F-15E entry records that its dts_ files are deliberately outranked). The winner is also the more defensible model: a GPS-guided JDAM against a relocatable TEL is exactly what LandAttackCapability=Installation is meant to prevent. But make the call knowingly - if this mission is meant to be a TEL hunt with heavy bombers, either set LandAttackCapability=All in a SEST-owned dts_gbu-31.ini (keeping the winner's other values), or give the B-1Bs a weapon that is allowed against mobile targets. Do not reorder to get there: promoting the B-1B copy above Dingtools would violate the author instruction and would also import TerminalApproachDist=1000 and MaxTurnRate=6.


*Sampled: All four copies (156 lines each, four distinct md5s) read and diffed against the winner. Also read the JDAM stations of mods-source/3652097318/aircraft/usaf_b-1b_dts.ini and enumerated every consumer of dts_gbu-31 across enabled mods and SEST packs.*


### vessels/plan_ss_type_039a.ini, plan_ss_type_039a_variants.ini, plan_ss_type_039b.ini, plan_ss_type_039b_variants.ini (4…

**Mods** 3775128499 Modern PLAN Systems (order line 19) > 3594891803 PLAN Submarines (order line 47)  

**Winner** 3775128499 Modern PLAN Systems · **Risk** medium


Hull/physics: loser 77.6 m x 8.4 m, 3500 t, 16.0 kt surfaced, CrushDepth 1800 ft, PeriscopeDepth 45 ft, LinearDrag 0.92, MaxAccelerationFactor 2.4, battery Capacity=80000, UnitScoreValue=5. Winner 74.9 m x 8.6 m, 3600 t, 13 kt surfaced (telegraph -5,0,3,5,10,14,17 vs ...,15,20), CrushDepth 1300 ft, PeriscopeDepth 35 ft, LinearDrag 0.96, MaxAccelerationFactor 0.52, battery Capacity=20500 (matching its own '20.5 miles at top underwater speed' comment — the loser's 80000 contradicts the identical comment), UnitScoreValue=3, plus CavitationParameters=20, MachineryRaftingGeneration=4, PropellerType=Skewback, TrimDepth=-3/TrimAngle=-1.8. Acoustics: loser BaseNoise 120 (039A) / 118 (039B), FlowNoise 0.9, CavitationNoise 20, TargetReflectionStrength 15. Winner 110 (039A) / 105 (039B), FlowNoise 0.85, CavitationNoise 5, TargetReflectionStrength 10 — a materially quieter, harder-to-ping boat. Classification: loser sets Role=SSN on both Yuan-class SSKs (wrong — they are diesel-electric/AIP boats) with AAW=0/ASuW=4/ASW=3; winner sets Role=SS with ASuW=6/ASW=6 and, on the 039B, Silent_Capability=6. Sensors: loser uses generic/Soviet placeholders — FLIR_Periscope, Snoop_Tray, Submarine_ESM, MGK-400 (039A) / MGK-400EM + DUUX-5 (039B), 5-6 systems. Winner ships 7 named PLAN systems — ZQQ-5A periscope (with NightVisionLevel=0.3), LQK-359A surface-search radar, SQZ-265A bow sonar, SQG-207 flank array, RQL-927A_ESM, SQZ-265A_Interceptor acoustic intercept — plus an [OpticalView] block (standard_morden_periscope, shipped at mods-source/3775128499/optical_views/standard_morden_periscope.ini) that the loser has no equivalent of. Loadout: loser gives both boats one WeaponMagazine_533mm of 16x pla_yu-6 + 8x pla_yj-18 (24 rounds, 2 types). Winner gives the 039A 6x plan_yu-6 + 4x plan_yu-9 + 6x plan_yj-18 + 2x plan_mss-01 (18 rounds, 4 types) and gives the 039B TWO selectable magazines — WeaponMagazine_533mmEarly (plan_yu-6/yu-9/yj-18/mss-01) and WeaponMagazine_533mmLate (4x plan_yu-6a, 6x plan_yu-10, 6x plan_yj-19, 2x plan_mss-01). Model: loser reskins the vanilla Victor I SSN (AssetBundleMesh=wp_ssn_victor1, ResourcesFolder=ships/wp_ssn_victor1/); winner uses a purpose-built hull (assets/models/vessels/039/039.obj, 23 submodels, per-tube colliders coll_tube533_1..6, coll_torpedoroom, coll_periscope, coll_radar_mast, coll_esm_mast). Variants files: both declare the same NumberOfVariants (4 for 039A, 14 for 039B). The winner drops the loser's ResourcesHullnumberFolder=textures/Misc/ + HullnumberTexture=transparent lines from every block, so hull numbers are no longer forced transparent. The winner's 039B defines all 14 [Variant] blocks; the loser's 039B defines only 13 against its declared NumberOfVariants=14 — so on this file the winner is the more internally consistent of the two.


**Silently lost** — 3594891803's Victor-I-based 039A/039B: the deeper 1800 ft crush depth, the 16 kt surfaced dash, the fatter 24-round single magazine, the Soviet sensor fit, and the hull-number-transparency variant lines. Nothing referenced elsewhere is lost — pla_yu-6 and pla_yj-18 remain defined by 3594891803's own ammunition/ files and are still consumed by its 039, 039C, 093/093A/093B, 094/094A and the mission's 09x and 096.


**Risk** — (1) SPLIT LINEAGE, not split ownership: all four contested files go to the same mod, so no unit/companion mismatch — but the sibling classes 039 and 039C remain on the loser's data, which is the incoherence to watch. (2) SOFT CROSS-MOD DEPENDENCY: the winner's 039B mounts SystemName=NTA_533mm, which 3775128499 does NOT define in its own systems/weapons.ini; it resolves only because 3715323261, 3716049886, 3722749887 and 3762023575 are all enabled and systems/ merges key-by-key. Disabling all four would break the 039B's launchers. (The loser's 039B has the same dependency, so this is not a regression.) (3) VERIFIED CLEAN: ZQQ-5A, LQK-359A, SQZ-265A, SQG-207, RQL-927A_ESM and SQZ-265A_Interceptor are all defined in mods-source/3775128499/systems/sensors.ini; plan_yu-6, plan_yu-6a, plan_yu-9, plan_yu-10, plan_yj-18, plan_yj-19 and plan_mss-01 all have ammunition/ files in 3775128499 (plan_yj-18 also in 3502273861, merge-safe). No dangling refs found. (4) COSMETIC DEFECT IN THE WINNER: plan_ss_type_039b_variants.ini [Variant4] omits ResourcesFlagFolder and FlagTexture (every other block has them), so that one variant may render without a PRC ensign. (5) POSSIBLE DUPLICATE-ID VECTOR, hedged: mods-source/3594891803/ contains a nested 'PLAN mod test/' subtree (99 files vs 55 at top level, with a MergeReport.txt dated 2026-07-03) that duplicates vessels/, ammunition/ and aircraft/ — including a second plan_ssn_type_09x.ini. Sea Power normally scans only <mod>/vessels etc., so this is probably inert, but if the loader ever recurses this is exactly the 'An item with the same key has already been added' shape. I did not confirm loader recursion behaviour; flagging it as worth deleting the subfolder rather than as a confirmed crash.


**Mission** — Not directly fielded — the mission uses plan_ssn_type_09x and plan_ssbn_type_096, both uncontested and owned by 3594891803. But this cohort splits the Yuan family across two data lineages inside one collection: 039A and 039B are now Modern-PLAN boats (Role=SS, PLAN sensors, plan_yu-* magazines, custom hull), while 039 (Song) and 039C — shipped only by 3594891803 — stay Role=SSN Victor-I reskins w…


**Recommendation** — Keep 3775128499 above 3594891803. Correcting Role=SSN to Role=SS on two SSKs alone justifies it, and the winner adds the named PLAN sensor fit, the periscope optical view, the early/late magazine split and a purpose-built hull in place of a Victor I reskin. Two cheap follow-ups: (a) add ResourcesFlagFolder/FlagTexture to [Variant4] of plan_ss_type_039b_variants.ini; (b) delete mods-source/3594891803/'PLAN mod test'/ from the deployed mod folder — it is a consolidator work product, not shipped content, and it is the only duplicate-id surface I found in either mod.


*Sampled: plan_ss_type_039a.ini diffed in full (911 vs 936 lines); plan_ss_type_039b.ini diffed with a key-field filter (987 vs 1220 lines) plus both magazine blocks and both full sensor lists read; both _variants files read end-to-end in both versions. Also verified e…*


### aircraft/usn_fa-18e_late.ini (1 file)

**Mods** 3606774881 U.S. Navy 2027 Capabilities mod (order line 17) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (order line 35)  

**Winner** 3606774881 U.S. Navy 2027 Capabilities mod · **Risk** medium


The winner is not a Hornet definition at all — it is a 12-line alias patch. Its entire content is: '#!alias aircraft/usn_fa-18e.ini', then [General] HideIn=Encyclopedia,MissionEditor,Signatures, then [SensorSystem2] SystemName=AN/APG-79(V), then [WeaponSystem1] ExternalGuidingSystems=AN/APG-79(V),GPS_Receiver. Everything else is inherited from 3606774881's own usn_fa-18e.ini, which the same mod also wins. So the effective usn_fa-18e_late is the 2027 Super Hornet: AN/APG-79(V) AESA, and 29 named loadouts (MurderHornetCAP, MH_CAP_120/120EF, MurderHornetGunSlinger, FistFight, Interceptor, Penetrator, SEAD, AntiShip, MH_AntiShipEF, MH_LRASM, MH_QCSK31/31EF/38/38EF, MH_GBU-75, MH_AGM-154JSOW/154EF/JSOWclus/clusEF, StrikeJDAM, MH_GBU-31EF, StrikeGBU, MH_GBU-24EF, CASAGM, MH_CASAGMEF, CASSDB, MH_CASSDBEF, Empty) firing usn_aim-174b, usn_aim-120d-3, usn_aim-9x, usn_gbu-53 (SDB-II), usn_gbu-75_jdam_lr, usn_gbu-31_qcsk, usn_gbu-38_qcsk, usn_gbu-31v4, b-2_lrasm, b-2_jsow/jsow_clus, usn_agm-88g, usn_agm-84n, usn_agm-65d, usn_gbu-12d, usn_tank_1200_f-18. The loser is a self-contained 868-line early Block I/II jet: AN/APG-73 mechanical radar, 9 loadouts (Default, AirToAir, AirToAirLongRange, Strike, Antiship, AntishipLongRange, CAS, SEAD) firing usaf_aim-120c, usn_aim-9m, usn_agm-84d, usn_agm-88e, usn_agm-65d, usaf_gbu-24, usn_gbu-12d and the 610-gallon tank usn_tank_610_f-18; GroundedPitchAngle=0 and GroundPivot=0,-0.0298,-0.0182 versus the winner's 1.4 and 0,-0.028336,-0.0182. Both point at the same airframe art (ResourcesFolder=assets/models/vechicle/aircraft/f-18e/, fa-18e.obj, hull, f-18e_mat.ini, the same two damage models), so this is a data swap, not a model swap.


**Silently lost** — The entire 868-line standalone late-model F/A-18E: its APG-73 radar fit, its 9 legacy loadouts, its AIM-120C/AIM-9M/AGM-84D/AGM-88E weapon set, its 610-gallon tank stations and its taxi geometry. Practically more important than any of that: because the winner's alias sets HideIn=Encyclopedia,MissionEditor,Signatures, usn_fa-18e_late is no longer selectable in the mission editor or visible in the encyclopedia. It still spawns where an existing mission or air wing names it, but a player cannot place one by hand any more. That behaviour change is not obvious from the file name and is the single most surprising consequence in this whole audit.


**Risk** — SPLIT OWNERSHIP CONFIRMED, and it is benign on inspection: aircraft/usn_fa-18e_late.ini is won by 3606774881 while its companion aircraft/usn_fa-18e_late_squadrons.ini is shipped ONLY by the loser 3426791311 (8 squadrons — VFA-27, 31, 94, 105, 115, 137, 143, 195 — with SerialnumberReferences=Modex,Left_Flap_Modex,Right_Flap_Modex,Rudder_Modex, EmblemReference=Emblem, NationFlagReference=Flag1 and liveries at assets/textures/fa-18e/vfa-*.png). It still coheres because the winner's resolved base uses the identical mesh, the identical material and the identical reference names, so the livery/modex slots line up. The one thing I could not verify is whether the vfa-*.png files still resolve, since this mirror carries .ini files only and 3426791311 has no textures/ tree in it — if 3426791311 were ever unsubscribed (it is marked DEPRECATED and is an unsubscribe candidate in the catalog) the squadrons file would vanish and the eight liveries with it. A SECOND, ADJACENT SPLIT in the same family is worth knowing about: aircraft/usn_fa-18e.ini is won by 3606774881 but aircraft/usn_fa-18e_squadrons.ini is won by 3430135740 (Murder Hornet), and that Murder Hornet file declares NumberOfSquadrons=20 while defining only 2 [Squadron] blocks (VFA-115, VFA-143) in its 23 lines — a count/blocks mismatch on the mission's most-fielded aircraft. No id collision here, and both AN/APG-79(V) and GPS_Receiver resolve (defined in 3426791311, 3606774881 and 3737267013 systems/sensors.ini, merged).


**Mission** — Not fielded directly. usn_fa-18e_late is referenced only by 3606774881's own usn_cvn_nimitz_2027s_adou / _variants, which the mission does not use — the mission's carrier is usn_cvn_ford_jsf (3461044389), whose air wing is 24x usn_fa-18e, 12x usn_fa-18f, 24x usn_f-35c, 6x usn_ea-18g, 4x usn_e-2d, 10x usn_mh-60r_26. Indirect but real: because the winner is an alias of usn_fa-18e, whatever you do t…


**Recommendation** — Keep 3606774881 above 3426791311 — the winner turns usn_fa-18e_late into the 2027 Super Hornet with AIM-174B, AIM-120D-3, GBU-53 and LRASM, which is exactly the capability set a 2026 Indo-Pacific theatre needs, against an APG-73 jet carrying AIM-120C and AIM-9M. Two things to do rather than reorder: (1) decide deliberately whether HideIn=...,MissionEditor is what you want — if you ever intend to place a usn_fa-18e_late by hand, that line needs overriding in a SEST pack; (2) do NOT unsubscribe 3426791311 while usn_fa-18e_late is in use, because it is the sole source of usn_fa-18e_late_squadrons.ini and its eight VFA liveries. Separately, fix NumberOfSquadrons=20 down to 2 in Murder Hornet's usn_fa-18e_squadrons.ini (or add the missing 18 blocks) — that one touches 24 mission aircraft.


*Sampled: Both versions of usn_fa-18e_late.ini read in full (12 vs 868 lines). Because the winner is an alias, also read the resolved base aircraft/usn_fa-18e.ini from 3606774881 (1422 lines) — its full station list, loadout list, sensor list and [Models] block — and c…*


### 5 files: ammunition/plan_726_chaff.ini, ammunition/plan_hq-10a.ini, ammunition/plan_skf-16.ini, ammunition/plan_skf-20.…

**Mods** 3775128499 Modern PLAN Systems (load-order line 12) > 3663564190 Type 003 Aircraft Carrier - PLANS (line 51)  

**Winner** 3775128499 Modern PLAN Systems · **Risk** medium


THREE OF FIVE ARE BYTE-IDENTICAL: plan_726_chaff.ini (544 B), plan_skf-16.ini (7404 B), plan_skf-20.ini (7403 B) - zero difference, no impact either way. plan_hq-10a.ini (HQ-10A point-defence SAM): winner KillProbability=0.95 vs loser 1.0; winner adds SmartFuse=True; InterceptSpeedPenaltyMultiplier 0.7 vs 0.6; winner adds InterceptSizePenaltyMultiplier=0.1 (much smaller size penalty, i.e. better against small sea-skimmers) and MaxTurnG=35, neither of which the loser has. plan_yu-12_air.ini (Yu-12 air-dropped lightweight ASW torpedo): winner adds SecondaryTargetType=ASuW; GuidanceType=10 (combined active+passive sonar; 152 other files in the collection use type 10, so it is a valid engine value) vs loser GuidanceType=7 (active sonar only); winner replaces the flat MaxLaunchRange=8 with SpeedSettings=38,50 kn and SpeedSettingRanges=8,5.2 nm and adds TerminalVelocity=50; winner enables SeekerPassiveRange=1 (commented out in loser) and raises SeekerGain 11.0 -> 38.0; winner adds FractionOfRangeToActivateSeeker=0.8; SearchVelocity 36 -> 38 kn. Display names/descriptions live in language_en/ammunition_names.ini, which merges, so no name is lost either way.


**Silently lost** — Only two things: the loser's HQ-10A tuning (guaranteed-intercept KillProbability=1.0, no smart fuse, no G-limit) and the loser's simpler single-speed Yu-12 with active-only homing. Both are strictly less detailed than the winner's. The loser's 726 chaff and SKF-16/SKF-20 copies are identical, so nothing at all is lost there. Nothing unique to the Type 003 mod exists in any of these five files.


**Risk** — No id collisions and no split ownership between this pair: their aircraft/ and vessels/ filename sets are completely disjoint (3775128499 ships escorts/subs/land-based aircraft, 3663564190 ships only plan_cv_type_003 plus the carrier air wing), and ammunition ids are the filenames, so the five overlaps are plain overrides. THE REAL RISK IS IN systems/, WHICH MERGES: both mods ship systems/weapons.ini and systems/sensors.ini and both define the same ids with DIFFERENT bodies. weapons.ini: [Type_1130] CIWS - winner has MissileInterceptChance=115, AircraftInterceptChance=95, RoundsLoaded=2560, ReloadTime=25, MinimumMissileInterceptTime=2, MoveToRestPositionTime=10, EffectPosition=0,0.002,0.012; loser has MissileInterceptChance=90, RoundsLoaded=5000, ReloadTime=120, MoveToRestPositionTime=0.5, EffectPosition=0,0,0. [HHQ10A] launcher - both define 18 attachment points but with entirely different coordinates (winner 0.004516,0.004677,0.002477... plus FireRate=30 and MoveToRestPositionTime=20; loser 0.0050,0.00745,0 ... MoveToRestPositionTime=5), i.e. geometry tuned to two different launcher meshes. [726-4A] and [726-4A_Noisemaker_Ejector] are identical in both. sensors.ini: 24 ids are defined in both with differing bodies, including KLC-18 (winner Role=AirAndSurface, TargetChannels=60, MaxRange=270 km vs loser Role=Surface, TargetChannels=1, WeaponChannels=1), IR-XX_IRS (winner VIDRangeMultiplier 16.0 / MaxRangeMultiplier 20.0 / NightVisionLevel 1 vs loser 4.0 / 6.0 / 0.85), J-15_IRST, J-35_EOTS, KLJ-15, KLJ-35, LJG-346A, RKL-*, RJZ-* and others. Assuming key-by-key merge resolves in load-order favour, every one of these resolves to 3775128499's values - generally a large capability uplift for the Type 003's own air wing and CIWS, but the [HHQ10A] attachment coordinates are geometry for a different launcher model, so HQ-10 rounds may sit visibly off the Type 003's launcher. I did not verify merge-precedence direction empirically and the repo's own history (commit 'Retract the duplicate-unit-id crash claim it turned out we invented') says the duplicate-key crash claim was withdrawn, so I am NOT claiming a crash here - only value drift. Binary assets (.obj/.png) are stripped from this mirror (0 files tracked), so model/texture presence could not be checked.


**Mission** — Yes, heavily. NORTHERN FRONT III FINAL NEWEST (Date=2026,8,24) fields plan_cv_type_003 as Taskforce2Vessel28 with no CustomAirGroup, so it uses the carrier file's own [AirGroup]: plan_j-35 x16, plan_j-15t x30, plan_j-15dt x4, plan_kj-600 x4, plan_z-18ja x2, plan_z-18fa x4, plan_z-18y x2, plan_z-9d x2. plan_z-18fa is the ASW helo that carries plan_yu-12_air, and plan_cv_type_003.ini itself referen…


**Recommendation** — Keep the order as is. 3775128499 is the correct winner for a 2026 Indo-Pacific setting: it gives the smart-fused, G-limited HQ-10A with a realistic sea-skimmer size penalty, and a dual-mode active/passive Yu-12 with selectable 38/50 kn speed settings, while three of the five files are identical anyway. Do not reorder. The one thing worth a targeted fix is the systems/ overlap: if HQ-10 rounds render off-position on the Type 003, copy 3663564190's [HHQ10A] attachment block into a small SEST patch rather than moving the whole mod, since promoting 3663564190 would also downgrade the KLC-18/IR-XX_IRS/J-35_EOTS sensor definitions used by the mission's 055s and 052Ds.


*Sampled: All five contested files diffed in full on both sides. Additionally read: both mods' systems/weapons.ini and systems/sensors.ini (section-by-section comparison via script), 3663564190/vessels/plan_cv_type_003.ini [AirGroup] block, both mods' language_en/ammun…*


### 2 files: ammunition/usn_agm-65e.ini, ammunition/usn_aim-120a.ini

**Mods** 3606134711 Custom Loadout Editor (line 4) > 3737267013 United States Naval Aviation (line 52)  

**Winner** 3606134711 Custom Loadout Editor · **Risk** medium


usn_agm-65e.ini: the winner is not a full definition at all - it is a 907-byte overlay whose first line is '#!alias ammunition/usn_agm-65b.ini' (a mechanism used by 144 files across 8 mods here, so it is a real engine/loader feature, not a typo). It overrides only Mass=285, AmmoPoints=570, WarheadType=0 / Power=28 / ImpactSize=Medium / Penetration=Moderate, GuidanceType=5, and four [Models] keys. The loser is a 9671-byte standalone file with Mass=209, WarheadType=2 (HEAT) / Power=35 / ImpactSize=Small / Penetration=Always, GuidanceType=5, MaxVelocity=620, MaxLaunchRange=17 nm, MinLaunchAltitude=200, SeekerFOV=1.5, SeekerPassiveRange=20. So the winner turns the AGM-65E into a 285 kg blast-frag/semi-AP weapon (correct for the E's 300 lb warhead; 209 kg is the A/B/D mass) but inherits its entire flight model from whatever wins usn_agm-65b.ini - currently 3505420313 Italian Navy Mod (line 31), giving MaxVelocity=820 kn, MaxLaunchRange=13 nm, MinLaunchAltitude=20 ft, MaxTurnRate=8, SeekerFOV=90, SeekerPassiveRange=6.5. usn_aim-120a.ini: both are full files. Winner Mass=148, AmmoPoints=592, Power=19, KillProbability=0.85, MaxVelocity=2200 kn, MaxLaunchRange=60 nm, MaxTurnRate=25, SeekerFOV=50, Seeker active/passive 8/8 nm, AntiJammerBonus=0.15, and it adds CircularErrorRadius=1.25 / CircularErrorRadiusLarge=2.5, PassiveRadarGuidanceFrequencies=All, plus TypicalFiringAlt/TypicalLaunchVelocity documentation and a sustainer effect. Loser Mass=153, AmmoPoints=300, Power=15, KillProbability=0.8, MaxVelocity=1600 kn, MaxLaunchRange=43.2 nm, MaxTurnRate=35, SeekerFOV=60, Seeker active/passive 9/9 nm, AntiJammerBonus=0.4, PassiveRadarGuidanceFrequencies=S/X/C/Ku-Band. Language descriptions for usn_aim-120a are word-for-word identical in both mods; the AGM-65E descriptions differ in wording only.


**Silently lost** — USNA's fully-specified AGM-65E (its own 17 nm / 620 kn flight model and narrow 1.5-degree seeker, and its HEAT/Penetration=Always warhead) and its more conservative AIM-120A (43.2 nm, 1600 kn) with the much stronger AntiJammerBonus=0.4 and band-limited passive-radar guidance. Note the winner's AIM-120A is roughly 40% longer-legged and 37% faster than USNA's, which is a large swing for a 1991-era AMRAAM. Also lost: USNA's asset paths (assets/models/ammunition/aim-120/, assets/models/ammunition/agm-65/) in favour of CLE's weapons/usn_aim-120/ and weapons/usn_agm-65/.


**Risk** — ALIAS-BASE DRIFT is the real defect here. CLE's usn_agm-65e overlay sets ResourcesRoot=usn_agm-65.obj, ResourcesMesh=usn_agm-65e, ResourcesMaterialFolder=weapons/usn_agm-65/ and ResourcesMaterial=usn_agm-65e_mat.ini - but it does NOT set ResourcesFolder, so that key comes from the alias base. Vanilla usn_agm-65b.ini has ResourcesFolder=weapons/usn_agm-65/, which matches CLE's usn_agm-65.obj; but the base is no longer vanilla - 3505420313 Italian Navy Mod wins usn_agm-65b.ini and sets ResourcesFolder=assets/models/weapon/ammunition/agm-65/ with ResourcesRoot=agm-65_tv.obj. The effective composite therefore asks for assets/models/weapon/ammunition/agm-65/usn_agm-65.obj, a folder+root pair no mod appears to author together. I could not confirm this because binary assets are stripped from this mirror (0 .obj/.png tracked), so treat it as a to-verify, not a proven break - but the folder/root mismatch in the .ini text is real. The same alias chain continues downstream: CLE's usn_aim-120b.ini is '#!alias ammunition/usn_aim-120a.ini', so the 2200 kn / 60 nm figures propagate to the AIM-120B as well. No id collisions and no split ownership: both are plain ammunition overrides and CLE ships no aircraft/ or vessels/ file that would separate a unit from its companion.


**Mission** — No. Neither id is fielded by NORTHERN FRONT III FINAL NEWEST - the mission has no agm-65e or aim-120a reference anywhere in its 3031 lines. usn_agm-65e is consumed only by USNA's usn_fa-18a+.ini and usn_fa-18d.ini (Station14) and CLE's usn_v-19a / usn_fa-18a loadouts - none of which the mission spawns (it flies usn_fa-18f_blk3). usn_aim-120a is referenced by no aircraft station file at all in the…


**Recommendation** — Leave the order alone. CLE is at line 4 because it is a loadout-editor framework that needs to sit above the mods it patches, and demoting it below USNA would be a far larger change than these two files justify. The winner's AGM-65E mass and warhead type are the more accurate of the two, and neither id touches the 2026 mission. Two cheap follow-ups worth doing: (1) add an explicit 'ResourcesFolder=weapons/usn_agm-65/' line to CLE's usn_agm-65e.ini overlay so it stops inheriting a model path from whichever mod happens to win usn_agm-65b.ini; (2) sanity-check the 60 nm / 2200 kn AIM-120A - it is hotter than USNA's 43.2 nm figure and hotter than an AIM-120A should be, and via the alias it also sets the AIM-120B.


*Sampled: Both contested files read in full on both sides. Also read: the alias base ammunition/usn_agm-65b.ini in both the winning owner (3505420313 Italian Navy Mod) and vanilla, CLE's ammunition/usn_aim-120b.ini, CLE's loadouts/ directory, and a full reference sweep…*


### 1 file: ammunition/usn_gbu-31v4.ini

**Mods** 3607989779 F-35C Lightning II Alt. Loadouts (line 14) > 3737267013 United States Naval Aviation (line 52)  

**Winner** 3607989779 F-35C Lightning II Alt. Loadouts · **Risk** medium


Both are 2000 lb-class JDAMs with GuidanceType=1 (IR/inertial per this engine's numbering), LandAttackCapability=Installation, ImpactSize=Large, Penetration=Always and Power=62, and both use the same model (assets/models/ammunition/gbu-31/, gbu-31.obj, mesh JDAM). The differences: WARHEAD TYPE - winner WarheadType=1 (armour-piercing, matching the BLU-109 penetrator its own description names) vs loser WarheadType=0 (blast-fragmentation). Mass 946 kg (winner) vs 907 kg (loser). AmmoPoints 1000 vs 1700 - the loser prices it 70% higher in the supply system. Envelope: winner MinLaunchRange=1 / MaxLaunchRange=15 / MinLaunchAltitude=2000 / MaxLaunchAltitude=65000 / LaunchReliability=98 / MaxTurnRate=5; loser MinLaunchRange=1.5 / MaxLaunchRange=17 / MinLaunchAltitude=500 / MaxLaunchAltitude=60000 / LaunchReliability=97 / MaxTurnRate=3 and it additionally sets MaxVelocity=1000 and Acceleration=0, which the winner omits. Seeker: winner SeekerFOV=45, SeekerActiveRange=10, SeekerPassiveRange=10, and it adds CircularErrorRadius=2; loser SeekerFOV=1, SeekerActiveRange=0.0, SeekerPassiveRange=1 and no CircularErrorRadius. Material file differs (gbu-31_mat.ini vs usn_gbu-31v4_mat.ini) though the folder and mesh are the same. Names: winner ' GBU-31(V)4/B,JDAM,Land Strike,...BLU-109A/B penetrating bomb with a 240 kg Tritonal warhead' (note the leading space in the name string); loser 'GBU-31(V)4,JDAM,Land Strike,2,000-pound class...'.


**Silently lost** — USNA's blast-fragmentation warhead, its 500 ft minimum release altitude, its 17 nm launch range, its explicit MaxVelocity=1000/Acceleration=0 terms, and its AmmoPoints=1700 supply price. Also lost is USNA's usn_gbu-31v4_mat.ini material reference - the winner points at gbu-31_mat.ini in the same folder, which 3607989779 does ship (its assets tree contains models/ammunition/gbu-31/ with a textures subfolder), so this one is self-consistent, unlike the GBU-12D case.


**Risk** — No id collision, no split ownership - single ammunition override. The winner is internally coherent and self-hosting on assets (unlike its GBU-12D, whose model folder it does not ship). The judgement call is the same one as GBU-12D but lands the other way: for the (V)4 variant, which is specifically the BLU-109 hard-target penetrator, WarheadType=1 / Penetration=Always is the RIGHT model and USNA's WarheadType=0 blast-frag is arguably the mis-stat. The winner's MinLaunchAltitude=2000 ft is again a restriction the loser did not impose, and its 15 nm range is 2 nm shorter. Its SeekerActiveRange=10 / SeekerPassiveRange=10 / FOV=45 are far more generous than the loser's 0.0/1/1, which matters for how forgiving the weapon is against a moving or offset aimpoint. Binary assets are stripped from this mirror, so mesh/texture presence was not verifiable for either version.


**Mission** — Yes. usn_gbu-31v4 is carried by the mission-fielded usn_f-35c (34 airframes off usn_cvn_ford_jsf) and usn_fa-18f_blk3 (24 airframes), both via their SEST_Integration airframe files, which reference the id 8 times and several times respectively. It is also on usn_fa-18e/usn_fa-18f in SEST. The mission's hard-target set - tgt_ammo_depot_small, tgt_fueltanks_small, the RAAF/PLA base structures and h…


**Recommendation** — Keep the order. For a 2026 Indo-Pacific strike scenario the winner's armour-piercing (V)4 with a 10 nm seeker is the better weapon model and matches what the (V)4 designation actually means, and its asset references are self-consistent. Do not reorder for this file. Be aware, though, that this cohort and the GBU-12D cohort pull in opposite directions on the same mod pair: if you decide to promote 3737267013 above 3607989779 to fix GBU-12D, you would also flip THIS file back to a blast-frag JDAM, plus ammunition/usn_agm-88g.ini and ammunition/usn_gbu-53.ini (the full five-file overlap between the pair, the fifth being aircraft/usn_f-35c.ini which SEST wins regardless). That coupling is the main argument for fixing GBU-12D with a SEST ammunition patch instead of a load-order move.


*Sampled: Both versions read via key-field extraction across the whole file, plus both language_en/ammunition_names.ini entries and a reference sweep for carrying aircraft across mods-source and integration/dist.*


### aircraft/ita_sh90.ini, ammunition/it_marte_mk2.ini (2 files) — plus the uncontested companion aircraft/ita_sh90_squadro…

**Mods** 3488139470 Euromod - Modern Italian Navy (line 43, WINS) > 3567228449 French Helicopter Package (line 84)  

**Winner** 3488139470 (Euromod - Modern Italian Navy) · **Risk** medium


it_marte_mk2.ini differs by exactly one line: AmmoPoints 810 (winner) vs 1235 (loser). Everything else — mass, warhead, seeker, guidance, model — is identical. ita_sh90.ini differs in three places: (1) the winner adds an [OpticalView] block (Views=binocular_7x50,binocular_10x50, DefaultView=binocular_7x50) the loser lacks; (2) ASW loadouts are rearmed — where the loser had Station1=it_marte_mk2 + Station2=it_mu_90_air|MU90 and a second loadout of two it_mu_90_air, the winner uses mm_mu_90|MU90 on both stations of both loadouts, and keeps a separate dedicated anti-ship loadout of it_marte_mk2 x2; (3) one submodel mesh name, Mesh=Portes (winner) vs Mesh=Porte (loser), on the cabin door.


**Silently lost** — Very little content-wise: the loser's it_mu_90_air torpedo drops out of the SH-90's loadouts (the ammunition file itself stays loaded — 3567228449 is the only mod that defines it — it is simply no longer referenced by this airframe), and the Marte's AmmoPoints supply cost changes. The winner adds capability rather than removing it.


**Risk** — This is a genuine split-ownership case plus a cross-mod asset dependency. (1) SPLIT OWNERSHIP: aircraft/ita_sh90_squadrons.ini is shipped ONLY by the loser, 3567228449, so the airframe file comes from the Italian pack while its squadron file comes from the French pack. It still coheres — NumberOfSquadrons=1, Nation=Italy, EmblemReference=Emblem and SerialnumberReferences=Numbers all match submodels the winner defines (SubModel24=Emblem, SubModel25=Numbers) — but NationFlagReference=Flag1 points at a [Flag1] submodel that NEITHER version of ita_sh90.ini defines. That dangling flag reference is pre-existing in both, not caused by the ordering, and is cosmetic. (2) ASSET DEPENDENCY: the winning ita_sh90.ini points at assets/models/aircraft/nh-90/ with NH90_IT_mat.ini, and that directory exists only in the loser, 3567228449. The Italian pack ships no SH-90 model of its own, so disabling the French Helicopter Package would leave the winning airframe with no mesh or material. (3) The Mesh=Portes vs Mesh=Porte divergence means one of the two names does not match the shared NH90 mesh; which one is correct is not verifiable here — this export strips all binaries (0 .obj and 0 .png files under mods-source), so the mesh name list could not be checked. (4) Both versions carry the same malformed line 'Mesh=Emblem_portes]' with a stray bracket — again pre-existing, not order-induced. All ammunition the winner references resolves: mm_mu_90 is defined by 3505420313 and 3629144864, it_marte_mk2 by the winner itself.


**Mission** — None. ita_sh90 does not appear anywhere in NORTHERN FRONT III FINAL NEWEST (0 matches), and no Italian frigate that would embark it is fielded. The only French/Italian unit in the mission is fr_ffg_lafayette_version_opv_modernized.


**Recommendation** — Keep the order — the Italian pack should own an Italian airframe, and it adds the optical view the French copy lacks. But record the dependency: 3488139470's SH-90 cannot render without 3567228449's assets/models/aircraft/nh-90/ directory, so those two mods must be enabled together. If the SH-90's cabin door renders wrong in play, the Mesh=Portes/Mesh=Porte line is the first thing to try flipping.


*Sampled: Both ita_sh90.ini files diffed in full (comment-stripped) and the winner's model/submodel blocks read directly; both it_marte_mk2.ini diffed in full; 3567228449/aircraft/ita_sh90_squadrons.ini read in full; asset directories of both mods enumerated.*


### 9 files where the ONLY substantive change is Euromod re-pointing models/materials into its shared europack: ammunition/…

**Mods** 3629144864 Euromod - Main Pack (line 18, WINNER) > 3505420313 Italian Navy Mod (line 38)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** low


Euromod replaces per-weapon asset trees with one consolidated mesh archive. Italian: ResourcesFolder=assets/models/weapon/ammunition/a184/ + ResourcesRoot=mm_a184.obj + ResourcesMesh=Body + ResourcesMaterial=mm_a184_mat.ini, submodels named generically (Mesh=Propeller_left1, Base_left). Euromod: ResourcesFolder=assets/europack/models/ + ResourcesRoot=weapons.obj + ResourcesMesh=eu_torpedo_a184 + ResourcesMaterialFolder=assets/europack/materials/mm_a184/ + ResourcesMaterial=eu_a184_mat.ini, submodels namespaced (eu_torpedo_a184_propeller_left1, eu_torpedo_a184_base_left). Same pattern for mm_a182 (Italian weapons/mm_a182/), mm_alfa (Italian assets/models/ammunition/Alfa_Missile/, ResourcesMesh=Warhead), mm_g6e, mm_milas. On mm_a184_mod1/mod2/mod3 all 23 differing lines are Resources*/Mesh= lines — every [Physics], [Guidance], [WarheadData], [SensorData] and [Propulsion] value is identical. Euromod also fixes two Italian authoring bugs: (a) Italian mm_milas.ini points ResourcesMaterialFolder=weapons/it_otomat_mk1/ and ResourcesMaterial=it_otomat_mk1_mat — a borrowed Otomat Mk1 material with the .ini extension missing; (b) Italian mm_si270_tipo_i.ini sets ResourcesMeshForLaunch=mm_a184_dummy, the wrong weapon's launch dummy. Only mm_si270_tipo_i.ini has real stat deltas: BaseNoise 117 -> 120 dB and MaxVelocity 38 -> 42 kt in Euromod's version.


**Silently lost** — Only cosmetic assets. The Italian mod's own model/material sets go unused — 3505420313/weapons/mm_a182/mm_a182_mat.ini stays on disk but is never read, likewise its assets/models/weapon/ammunition/{a184,g6e,si-270}/ and assets/models/ammunition/Alfa_Missile/ trees. On mm_si270_tipo_i the loser's quieter (117 dB) and slower (38 kt) SI-270 Tipo I is lost — the player gets a slightly noisier, 4 kt faster torpedo.


**Risk** — Split ownership exists but coheres: the vessels that consume these rounds (3505420313/vessels/mm_ddg_audace.ini, mm_ss_toti.ini, mm_ssn_marconi.ini, mm_ssbn_archimede.ini for mm_a184; mm_cg_garibaldi.ini, mm_ssbn_archimede.ini for mm_alfa; mm_ddgh_durand_de_la_penne_02.ini for mm_milas; mm_ff_canopo_50.ini for mm_a182) stay Italian-owned — Euromod ships no vessels/ directory at all, only ships/materials. Because the winner keeps every ammo id and every ballistic/guidance value identical, those magazine entries and loadouts still resolve correctly. Verified every referenced material .ini exists in the winner: assets/europack/materials/{mm_a182,mm_a184,mm_alfa,mm_g6e,mm_milas,mm_si270}/eu_*_mat.ini all present. CAVEAT (not a defect claim): assets/europack/models/weapons.obj could not be verified — this export mirrors .ini files only, `find` returns 0 .obj files across the entire mods-source tree, so mesh presence is unverifiable from the repo and must be confirmed in-game.


**Mission** — None. No mission under integration/missions/ fields any mm_* vessel or references mm_a182/mm_a184/mm_alfa/mm_g6e/mm_milas/mm_si270_tipo_i.


**Recommendation** — Keep the current order. Euromod's version is a strict improvement — same physics, consolidated assets, and it repairs the wrong-launch-dummy and missing-extension bugs in the Italian originals. Do not reorder for these files.


*Sampled: Read full diffs of mm_a182, mm_a184, mm_alfa, mm_g6e, mm_milas, mm_si270_tipo_i. For mm_a184_mod1/mod2/mod3 I filtered the diffs and confirmed 23/23 differing lines are Resources*/Mesh= only (no non-asset lines).*


### ammunition/mm_mu_90.ini and ammunition/mm_mu_90_ship.ini (the pair with live mission exposure)

**Mods** 3629144864 Euromod - Main Pack (line 18, WINNER) > 3505420313 Italian Navy Mod (line 38)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** low


Euromod does not ship a real MU-90 under these names — both winning files are alias stubs: mm_mu_90.ini is 35 bytes containing only `#!alias ammunition/eu_mu_90_air.ini`, mm_mu_90_ship.ini is 36 bytes containing `#!alias ammunition/eu_mu_90_ship.ini`. eu_mu_90_air.ini is itself a second-hop alias to eu_mu_90_ship.ini plus air-drop overrides (AirLaunched=True, SupplyCategory=AirTorpedo, Mass=314.1, a [Physics] parachute block with ParachuteSlowDown=0.99 / ParachuteEndVelocity=100.0 / MaxAngleWithParachute=80.0, and MinLaunchAltitude=100 / MaxLaunchAltitude=1000). Substance of Euromod's eu_mu_90_ship.ini vs the Italian standalone 8.8 KB / 8.4 KB files: adds SecondaryTargetType=ASuW; Mass 314.1 -> 304 and AmmoPoints 628 -> 608; WarheadData Power 42 -> 27; replaces the single MaxVelocity=55.0 + MaxLaunchRange=8.1 nm model with TerminalVelocity=55.0 plus SpeedSettings=29,40,55 kt and SpeedSettingRanges=12.4,9.0,5.9 nm (MaxLaunchRange key removed); MaxDepth 1450 ft -> 3280 ft (1000 m); AntiCountermeasuresBonus 0.35 -> 0.45; MinAfterSpoofEffectTime 5.0 -> 2.0 and Max 12.0 -> 10.0; SearchVelocity 36 -> 29 kt; adds FractionOfRangeToActivateSeeker=0.8. Euromod also drops the Italian AssetBundle fallback block, which pointed the MU-90 at Mk46 art (AssetBundleMesh=usn_mk46, AssetBundleMaterial=usn_mk46_mat, AssetBundleMeshHullCollider=usn_mk46_coll).


**Silently lost** — The Italian standalone MU-90: Power=42 warhead, flat 55 kt / 8.1 nm envelope, 1450 ft depth limit, AntiCM 0.35, and the Mk46 AssetBundle fallback art. Of these only the Power 42 -> 27 warhead drop is a real capability regression; 27 is the more plausible figure for the MU-90's 32.7 kg shaped charge, so this reads as a correction rather than a loss.


**Risk** — Alias chaining is a deliberate, heavily-used Euromod idiom, not an accident: 41 of its ammunition files are alias stubs and 16 of those chain alias-to-alias (e.g. usn_rgm-84q -> 84n -> 84l -> 84g; usn_an_slq_25e -> 25c -> 25b). The mm_mu_90 -> eu_mu_90_air -> eu_mu_90_ship chain matches that pattern and both targets exist inside the winning mod. No id collision: the ids mm_mu_90 and mm_mu_90_ship remain defined (as aliases), so the reference in 3784474738 Euromod - Anchorchain Expansion Pack (line 10) systems/TorpedoAudioClip_Mapping.ini is not orphaned — and systems/ merges key-by-key anyway. The one real dependency to note: the alias is only meaningful while Euromod outranks the Italian mod; inverting the order replaces mm_mu_90 with the flat Italian file and the deeper/CM-hardened/selectable-speed model disappears from a unit that is actually flying.


**Mission** — YES — this is the only cohort in the pair with live mission exposure. ita_sh90 (NH-90 NFH, from 3488139470 Euromod - Modern Italian Navy, load-order line 43) is fielded at integration/missions/'chapter 1 - Merchant Mayham.ini':175 and integration/missions/'chapter 5 - Polar Pickup.ini':76. Its ASW and AntiShip loadouts both mount Station1=mm_mu_90|MU90 and Station2=mm_mu_90|MU90 (3488139470/aircr…


**Recommendation** — Keep the current order — it is load-bearing for fielded content. Euromod's MU-90 is the better fit for a 2026 Indo-Pacific theatre: 1000 m depth limit matches the real weapon, the 29/40/55 kt selectable-speed model gives 12.4 nm of low-speed reach against a deep-diving contact instead of a flat 8.1 nm, AntiCM 0.45 is appropriate against modern countermeasures, and the ASuW secondary role plus the launch-altitude envelope are additive. Treat 3629144864 > 3505420313 as pinned for this pair and record ita_sh90 as the reason.


*Sampled: Both alias stubs read in full (cat -A); eu_mu_90_air.ini read in full; full diff of Italian mm_mu_90_ship.ini against Euromod eu_mu_90_ship.ini; key-stat grep of Italian mm_mu_90.ini; alias graph of all 41 alias files in Euromod's ammunition/ enumerated progr…*


### ammunition/usn_mk14.ini, usn_mk14_torpedo.ini, usn_mk16_mod8.ini, usn_mk16_mod8_torpedo.ini (the four USN torpedoes the…

**Mods** 3629144864 Euromod - Main Pack (line 18, WINNER) > 3505420313 Italian Navy Mod (line 38)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** low


usn_mk14.ini — Euromod: AmmoPoints 4164 -> 3000; BaseNoise 120 -> 115 dB; TransientBaseNoise 180 -> 160; adds a [Physics] block (ParachuteSlowDown=0.99, UnderWaterVelocityDamping=0.985, ParachuteEndVelocity=100.0, MaxAngleWithParachute=80.0); ImpactSize VeryLarge -> Medium; FuzeProximityDistance 10 -> 5 m; Acceleration 12.0 -> 10.0; MinLaunchRange 0.5 -> 0.4 and adds MaxLaunchRange=4.43; SpeedSettings 30.5,31,46 -> 30.5,46 with SpeedSettingRanges 4.4,4.4,2.2 -> 4.43,2.22; adds MinLaunchAltitude=100 / MaxLaunchAltitude=1000; MaxDepth 200 -> 1220 ft; adds search patterns absent from the Italian file (SnakeSearchAngle=30.0, SnakeSearchTurnCycleTime=6.0, SpiralSearchParams=65,900, SpiralSearchRadius=0.25, SpiralSearchAngle=6.0); DefaultDepth 15 -> 200 ft; adds DestructionDepth=1450.0 and SelfDestructDelay=6. usn_mk14_torpedo.ini — Euromod drops the Italian header comments and adds SpeedSettings=30.5,46 / SpeedSettingRanges=4.43,2.22, MaxLaunchRange 4.4 -> 4.43; otherwise equivalent. usn_mk16_mod8.ini — Euromod adds TerminalVelocity=46.2, MaxVelocity 46.0 -> 46.2, MaxLaunchRange 5.67 -> 5.7, adds SpeedSettings=46.2 / SpeedSettingRanges=5.7. usn_mk16_mod8_torpedo.ini — the largest single delta in the cohort: Italian sets TerminalVelocity=66.5 and MaxVelocity=66.5 kt with MaxLaunchRange=11.0 nm (its own header comment concedes it is 'Balanced between the Mk14 and Mk48'); Euromod harmonises to 46.2 kt / 5.7 nm, matching its usn_mk16_mod8.ini. Note the Italian mod is internally inconsistent here — its usn_mk16_mod8.ini says 46.0 kt / 5.67 nm while its usn_mk16_mod8_torpedo.ini says 66.5 kt / 11.0 nm; Euromod makes the pair agree.


**Silently lost** — The Italian mod's 66.5 kt / 11.0 nm 'super Mk16' and its 4164-point Mk14 supply cost, plus VeryLarge Mk14 impact VFX, 3-step Mk14 speed selection (30.5/31/46 kt) and 15 ft default running depth. All of it is unreachable in practice — see mission/reference note below.


**Risk** — No id collision and no dangling references. Both mods ship identical asset paths for these (ResourcesFolder=ammunition/usn_mk16_torpedo/ + mk16_mat.ini, and the matching usn_mk14_torpedo/ + mk14_mat.ini) and BOTH ship those folders with the material .ini present, so the winner's references resolve. Key finding on reach: usn_mk16_mod8 and usn_mk16_mod8_torpedo are ORPHAN ids across the entire enabled set — repo-wide grep finds them only in language_en/language_cn ammunition_names.ini. The vanilla Skipjack/Permit/Sturgeon boats use the different vanilla id `usn_mk16`, not usn_mk16_mod8. So the 66.5 -> 46.2 kt change has no fielded effect today. By contrast usn_mk14 IS widely consumed — vanilla usn_bb_iowa, usn_cgn_virginia, usn_cgn_long_beach_83, usn_dd_spruance_abl, ins_ptg_hetz/aliya, plus mod vessels in 3413868677, 3378409795 (Type 23) and 3390330875, and the Italian mod's own mm_ss_longobardo.ini (WeaponMagazine_Fwd_Torp Ammunition2=usn_mk14 x12, Aft x4) — so Euromod's Mk14 rewrite propagates well beyond Italian content. Separately noted, not caused by this override: mm_ss_longobardo's magazine comments read 'Increased to 2 for Mk37 and Mk16' but the file actually loads usn_mk37_mod2 and usn_mk14 — an Italian-side comment/content mismatch.


**Mission** — None. No mission under integration/missions/ references usn_mk14, usn_mk14_torpedo, usn_mk16_mod8 or usn_mk16_mod8_torpedo, and none fields mm_ss_longobardo or any other mm_* vessel.


**Recommendation** — Keep the current order. Euromod's Mk14 is the materially better model — it adds snake and spiral search patterns the Italian version simply lacks, a realistic 1220 ft depth ceiling with a 1450 ft destruction depth, a sane 200 ft default running depth for submerged targets (vs 15 ft), an air-drop parachute physics block and a launch-altitude envelope. Euromod also repairs the Italian mod's self-contradicting Mk16 pair. The only debatable regressions are cosmetic/economic (ImpactSize VeryLarge -> Medium, AmmoPoints 4164 -> 3000) and are not worth a reorder. WW2-era USN torpedoes are peripheral to a 2026 Indo-Pacific collection in any case; if the Mk16 is ever wanted, note that no unit currently loads it and it would need a vessel-side reference added first.


*Sampled: Full diffs of all four files read line-by-line. Also read the consuming magazine block of 3505420313/vessels/mm_ss_longobardo.ini (lines 435-470) and ran repo-wide reference greps for usn_mk14, usn_mk14_torpedo, usn_mk16_mod8, usn_mk16_mod8_torpedo and usn_mk…*


### 9 French ammunition files: fr__f21.ini, fr__mdcn.ini, fr_cal_100mm.ini, fr_cal_76mm.ini, fr_canto.ini, fr_crotale_vt1.i…

**Mods** 3629144864 Euromod - Main Pack (order pos 18) > 3567256221 Charles De Gaulle & Modern French (pos 30)  

**Winner** 3629144864 (Euromod - Main Pack) wins all 9 · **Risk** low


fr_canto.ini is byte-identical - no conflict at all. The other 8 split into two classes. (a) Warhead scale: CDG pastes real-world kilograms into Power, Euromod uses the vanilla damage scale. fr_mm-40_block3 Power=39/Medium (Euromod) vs 165/Medium (CDG); fr_sm39 Power=39/Medium/Always vs 165/Medium/Heavy; fr__mdcn Power=64/Large/WarheadType=0 vs 450/Medium/WarheadType=1; fr_crotale_vt1 Power=20/SemiSmall vs 13/Medium; fr_mistral Power=9/VerySmall vs 3/Small. Vanilla fr_am-39 and fr_mm-38 (the Exocet family) are Power=39/Medium and vanilla Harpoon usn_rgm-84d is Power=45, so Euromod matches the engine's scale and CDG's Exocet was roughly 4x a Harpoon. (b) Kinematics/seeker rewrites: fr_mm-40_block3 Euromod MaxTurnRate=12, SeaSkimmingAlt=8ft, PopUpAltitude=500/PopUpDistance=5.0, SeekerActiveRange=15nm, PeakPower=3kW, X-Band only, AntiCM 0.25, no CIWSDefenceBonus; CDG had MaxTurnRate=60 + LaunchTurnRate=90, SeaSkimmingAlt=12, SeekerActiveRange=5, PeakPower=35, X-Band,J-band, AntiCM 0.4, CIWSDefenceBonus=30, MissileDefenceBonus=0.25. fr_sm39 Euromod MaxLaunchRange=100nm vs CDG 35nm. fr__mdcn Euromod GuidanceType=0 (INS to coordinates, the vanilla land-attack convention) MaxLaunchRange=900nm, MinLaunchRange=40, MaxLoftAngle=50; CDG GuidanceType=6 (TV terminal), 540nm, loft 25deg, plus AntiCountermeasuresBonus/AntiJammerBonus. fr_crotale_vt1 Euromod GuidanceType=3 (active radar, fire-and-forget), MaxVelocity=2334kt, MaxLaunchRange=15nm, MaxAttackAltitude=29528ft; CDG GuidanceType=2 (SARH, needs an illuminator), 1800kt, 6nm, MaxFlightTime=30s. fr_mistral Euromod uses the modern gimbal seeker model (SeekerFOV=1, SeekerGimbalFOV=90, SeekerPassiveRange=2.16nm, MaxLaunchRange=4.32nm, MaxTurnRate=25) vs CDG's SeekerFOV=90/SeekerPassiveRange=20nm/MaxLaunchRange=5/MaxTurnRate=16. Guns: fr_cal_100mm Euromod MaxRange=20000m vs CDG 12000m; fr_cal_76mm Euromod 20000m vs CDG 30000m - those two files are otherwise identical. (c) Meshes: every Euromod version repoints [Models] to assets/europack/models/weapons.obj with eu_missile_* / eu_launch_* meshes and assets/europack/materials/<weapon>/; CDG pointed at its own assets/models/ammunition/<weapon>/*.obj. Euromod ships the matching europack material folders (mdcn, exocet_mm40_block3, exocet_sm39, mistral, vt_1, F21 all present), so the repoint is self-consistent.


**Silently lost** — Only one real capability loss: fr__f21. CDG's F21 is written for the current torpedo model - SpeedSettings=32,42,50 with SpeedSettingRanges=28,21,15, WireControlsDepth=True, WireCountermeasureBonus=0.5, WireBreakSpeed=20, WireMinSeafloorClearance=40, MaxDepth=3200ft. Euromod's F21 has none of those keys: single MaxVelocity=50kt, MaxLaunchRange=31nm, MaxDepth=2000ft, no wire guidance. Those exact keys are live engine features (vanilla usn_mk48/usn_mk48_mod4/usn_mk48_mod4_adcap all use them), so the winner turns the F21 into a legacy fire-and-forget torpedo with no selectable speed and no wire, for CDG's fr_ssn_suffren, fr_ssn_suffren_dds, fr_ssn_rubis and fr_ssbn_triomphant. Warhead is identical either way (Power=68/Large/Always). Everything else lost is CDG's inflated warhead numbers and its own mesh paths - no unique content.


**Risk** — No id collision: Euromod defines no units at all, so it cannot collide with CDG's French ships. No split ownership - each ammunition file is a self-contained leaf. Two side findings. (1) Dangling reference, pre-existing and not caused by load order: CDG's fr_ffg_lafayette_version_opv_modernized.ini line 287 sets Ammunition=fr_crotale on WeaponSystem2, but no ammunition/fr_crotale.ini exists in any enabled mod or in vanilla (only fr_crotale_vt1.ini does). The launcher's AssociatedMagazine=WeaponMagazineCrotale does load 8x fr_crotale_vt1, so the magazine is fine; the launcher's default round is not. This ship is fielded by the active mission. (2) A third, unlisted copy of fr_cal_100mm.ini exists at mods-source/3594891803/PLAN mod test/ammunition/fr_cal_100mm.ini (MaxRange=17000, WarheadType=6, Power=4). It is buried one directory deep inside a stray 'PLAN mod test/' folder that also contains a MergeReport.txt, so it almost certainly never loads; and 3594891803 sits at pos 47, below Euromod, so it loses regardless. Worth cleaning up as a packaging defect in that mod, not a load-order problem. (3) Mesh/texture presence in assets/europack/models/weapons.obj cannot be verified from this export - binaries are stripped and empty directories were pruned - but the corresponding europack material .ini folders are all present.


**Mission** — Yes. NORTHERN FRONT III FINAL NEWEST fields exactly one French unit, fr_ffg_lafayette_version_opv_modernized (CDG mod). Its fit consumes 4 of the 9 contested files: fr_crotale_vt1 (8 rounds), fr_mistral (2x6 Simbad), fr_mm-40_block3 (2 launchers) and fr_cal_100mm (500 rounds). Under the current order that ship gets a 15nm fire-and-forget Crotale VT-1 that needs no illuminator, a 20km 100mm gun, a…


**Recommendation** — Keep Euromod above the CDG pack - it is a pure weapons library (it ships no vessels/ and no aircraft/ directory at all, only ammunition, systems, effects, PresetSystems and assets), so it is meant to own the shared French ordnance, and on 8 of 9 files it is the more engine-correct version. Do not reorder for the F21: promoting CDG above Euromod to recover the wire guidance would hand it back the 165-vs-39 warhead inflation on both Exocets, the 30km 76mm and the SARH Crotale, and would break Euromod's europack mesh repoint. If the F21's wire guidance matters, patch it the way this repo already patches things - a SEST_* pack at the top of the order carrying Euromod's fr__f21.ini with CDG's SpeedSettings/SpeedSettingRanges/Wire*/MaxDepth=3200 block merged back in.


*Sampled: Diffed all 9 pairs. Deep-read fr__f21.ini, fr__mdcn.ini, fr_mm-40_block3.ini, fr_sm39.ini, fr_crotale_vt1.ini, fr_mistral.ini, plus both gun files. fr_canto.ini compared by md5 only (81af6cd1 both sides = byte-identical). Baseline scale checked against mods-s…*


### ammunition/pla_ahead_pmd062.ini, land_units/pla_spaa_pgz-09.ini, land_units/pla_spaa_pgz-09_variants.ini

**Mods** 3733719765 PLA Land Unit Pack [line 15] > 3508275114 Ground Upgrade: SPAA [line 27]  

**Winner** 3733719765 (PLA Land Unit Pack) · **Risk** low


pla_spaa_pgz-09_variants.ini is byte-identical in both (md5 da7cf895842e1dde9157cbc2dd4245bf) — 3 China variants + Default, Variant2/3 using assets/tex/pgz09_tex_sand.png and pgz09_tex_snow.png. pla_spaa_pgz-09.ini: the winner is a proper land-vehicle build — it renames the [Mount] submodel to [Turret] and adds TurretBlowOffChance=0.5, SecondaryPopPrefab/TurretCookOffEffect/TurretFireEffect (all vanilla 'effects/land units/emitters/...' paths, verified against vanilla land_units), uses VehicleSmokes for Small/Moderate/Severe fire and audio/miscellaneous/MachineNoise1_short at volume 0.4. The loser is a ship-template port: [Mount] naming, SmallShipFire/ModerateShipFire/SevereShipFire classes, AmbientAudioClip=audio/ships/Ship-Turbine-Medium at volume 1.0, no turret blow-off or cook-off. Everything else — 2× PG99 35mm guns, 480 rounds of pla_ahead_pmd062, 4 sensor systems, 35 t / 29.7 kn / DamagePoints=5 — is identical. pla_ahead_pmd062.ini differs on exactly 3 lines, the shell mesh: winner ResourcesRoot=shell_small / Mesh=shell_small / Material=shell_mat vs loser shells_tracer_new / shell_tiny / shell_mat_yellow. Ballistics are identical (MuzzleVelocity 1240 m/s, MaxRange 5000 m, Power 1.2, FuzeProximityDistance 5, KillProbability 0.2).


**Silently lost** — Only the loser's ship-flavoured presentation (ship fire classes, turbine ambient audio) and its vanilla-convention shell mesh reference. No stats, weapons, sensors or variants are lost — the loser's file has no content the winner lacks. Separately, the language merge also favours the winner: its land_units_names.ini names all four entries (Default, Variant1, 'PGZ-09 Sand', 'PGZ-09 Snow') while the loser only names Default and Variant1, so the winner also fixes two blank variant labels.


**Risk** — (1) Cross-mod merge dependency: the winning unit file's SensorSystem4 is SystemName=PGZ-09_Visual (Type=Infrared), and [PGZ-09_Visual] is defined ONLY in the loser's systems/sensors.ini line 22 — the PLA Land Unit Pack does not define it anywhere. It resolves today because systems/ files merge key-by-key and both mods are enabled; disabling Ground Upgrade: SPAA would leave the PGZ-09's FLIR dangling. [PG99_35mm_Gun], [PGZ-09_Search] and [PGZ-09_FC] are defined identically in both mods, so the merge is otherwise a no-op. (2) Cosmetic, unverified: the winner's shell mesh uses ResourcesRoot=shell_small, whereas every vanilla shell file uses ResourcesRoot=shells_tracer_new with shell_small as the MESH name; several other mods (Euromod main pack, others) do use shell_small as a root, so it probably resolves, but binary assets are stripped from this repo so I could not confirm. Worst case is invisible 35 mm tracers. (3) No id collision (same filename = one registration; vanilla has no pgz-09) and no split ownership (both files won by the same mod, variants identical).


**Mission** — PGZ-09 is not fielded in NORTHERN FRONT III FINAL NEWEST. Both mods are nonetheless load-bearing for the mission — it fields pla_apc_zbl-08 and 4× pla_df-26b_tel from the PLA Land Unit Pack and 3× wp_spaa_zsu-23-4 from Ground Upgrade: SPAA — so neither can be disabled to resolve the conflict.


**Recommendation** — Keep the order. If you ever prune Ground Upgrade: SPAA, first copy its [PGZ-09_Visual] sensor block into the PLA Land Unit Pack (or into a SEST systems patch), otherwise the PGZ-09 loses its infrared sensor system silently.


*Sampled: All 3 files diffed in full; winner's pla_spaa_pgz-09.ini read end-to-end; both mods' [PG99_35mm_Gun]/[PGZ-09_Search]/[PGZ-09_FC]/[PGZ-09_Visual] system sections extracted and compared; both language_en/land_units_names.ini [pla_spaa_pgz-09] blocks compared; v…*


### ammunition/usn_agm-65d.ini

**Mods** 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet [line 35] > 3505420313 Italian Navy Mod [line 38] > 3737267013 United States Naval Aviation [line 59] > 3414146266 A-10A Thunderbolt II [line 62] > 3459682829 A-10C [line 63] > 3758320372 F-16C Fighting Falcon (modern) [line 80]  

**Winner** 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) · **Risk** low


Six copies, four distinct versions. All four agree on the core: GuidanceType=1 (IR homing), WarheadType=2 (HEAT), Power=23, SeekerPassiveRange=20 nm. (a) WINNER, byte-identical to the F-16C mod's copy (md5 d47d8a18…): Mass=227, AmmoPoints=520, AirLaunched=True, MaxVelocity=620, Acceleration=20 G, sustainer 4 G, MaxFlightTime=180, MinLaunchRange=2.0 / MaxLaunchRange=17.0, launch window 200–60000 ft, LaunchReliability=97, SeekerGain=0.0 with a flat SeekerFOV=90.0 (no gimbal model), and uniquely Zoom=3 and AntiCountermeasuresBonus=0.4 (flare resistance) — no other version has either. Model assets/models/weapon/ammunition/agm-65/agm-65_ir.obj with an IR_Nose submodel (agm-65d_mat.ini and ir_mat.ini both present in the mod). (b) A-10A/A-10C (identical to each other, md5 d50b4eff…): header actually reads '# AGM-65B Maverick', Mass=209, MaxVelocity=500, Acceleration 21.3 G, DropDuration=1.0, NO MinLaunchRange/MaxLaunchRange/launch-altitude/LaunchReliability keys at all (engine defaults), no ACM bonus, no Zoom, seeker modelled as SeekerFOV=1.5 + SeekerGimbalFOV=90 with SeekerGain=25, own model weapons/usn_agm-65/. (c) United States Naval Aviation: the winner's top-line numbers (227 kg, 520 pts, 620 kn, 17 nm, 200–60000 ft) plus better flight physics — GravityFactor=2, SupportsBanking=True, DragCoefficient=1.525, VelocityBleed=0.3, MaxTurnRate=10, TerminalApproachDist=1000 — and the gimballed seeker (1.5°/90°, gain 25), but LaunchReliability=95, MaxFlightTime=105, AirLaunched=1 (numeric rather than True), and no Zoom/ACM bonus. (d) Italian Navy: Mass=210, AmmoPoints=420, MaxVelocity=500, adds a loft profile (MaxLoftAngle=20, MaxLoftAlt=30000), MaxFlightTime=105, gimballed seeker.


**Silently lost** — The gimballed seeker modelling that three independent mods agree on (SeekerFOV=1.5 + SeekerGimbalFOV=90, SeekerGain=25) — the winner instead gives the Maverick a permanent 90° instantaneous field of view and 0 dB gain, which is more permissive than intended. Also lost: USNA's drag/banking/gravity physics block, the Italian version's loft profile, and the A-10 mods' lighter 209 kg AGM-65B-derived round with its own model.


**Risk** — No id collision. Dangling refs: none — the winner's model path and both material .ini files ship inside the winning mod. Real hygiene finding: 3426791311 is flagged DEPRECATED and every one of its aircraft files is outranked (usn_fa-18e/f/f_blk3/ea-18g → SEST_Integration, usn_fa-18e_late → 3606774881, usn_fa-18e_squadrons → 3430135740), yet it still WINS 12 ammunition files for the whole collection: usn_agm-65d, usn_mk-82/83/84, usn_lrasm, usn_aim-9l/9m, usn_gbu-31_v1, usaf_aim-120d-3, usn_agm-88e. Deleting or disabling it 'because it is deprecated' would silently re-home all 12 — do not do that without re-checking. Split ownership caused by the same mod: it wins aircraft/usn_fa-18e_late_squadrons.ini (8 squadrons, liveries at assets/textures/fa-18e/vfa-27|31|94.png, serial refs Modex/Left_Flap_Modex/Right_Flap_Modex/Rudder_Modex) while the parent usn_fa-18e_late.ini is won by 3606774881 (itself a '#!alias aircraft/usn_fa-18e.ini' patch resolving to SEST's Hornet), and it wins usn_ea-18g_2020s_squadrons.ini while usn_ea-18g_2020s.ini is won by SEST_Integration. I could not verify livery/submodel coherence for those pairs because texture binaries are stripped from this repo — flagging for the aircraft-cohort/SEST pass rather than claiming breakage.


**Mission** — Direct. The mission fields usa_a-10c; that aircraft file is won by SEST_Integration and still carries 6× 'usn_agm-65d|LAU-88' stations, so every Maverick the A-10C shoots in NORTHERN FRONT III FINAL NEWEST uses the deprecated Super Hornet mod's file. The effect is benign-to-positive: an explicit 17 nm / 200–60000 ft envelope, 97% reliability and 0.4 flare resistance instead of the A-10 mod's unde…


**Recommendation** — Keep the order — the winner is the most complete file and the only one with countermeasure resistance and a weapon-camera zoom. Two follow-ups: (1) never prune 3426791311 without first re-homing the 12 ammunition files it owns; (2) if you want realistic Maverick lock behaviour, hand-patch SeekerGain=25 / SeekerFOV=1.5 / SeekerGimbalFOV=90 into the winning file rather than reordering, since promoting 3737267013 above it would also cost Zoom=3, AntiCountermeasuresBonus=0.4 and 75 s of MaxFlightTime.


*Sampled: usn_agm-65d.ini md5-compared across all 6 mods; winner diffed in full against the A-10C, USNA and Italian versions; key-by-key extraction of guidance/seeker/launch keys from four versions; usa_a-10c.ini station lines and the SEST_Integration copy checked; ful…*


### ammunition/fr_mu_90_air.ini

**Mods** 3629144864 Euromod - Main Pack [line 18] > 3575847216 Euromod - Modern German Navy [line 32] > 3567228449 French Helicopter Package [line 84]  

**Winner** 3629144864 (Euromod - Main Pack) · **Risk** low


The winner is not a stat file at all — it is a single line with no trailing newline: '#!alias ammunition/eu_mu_90_air.ini', which itself aliases eu_mu_90_ship.ini (both shipped only by the Main Pack). Resolved, the player gets: GuidanceType=10 (combined active+passive sonar), SpeedSettings=29,40,55 kn at SpeedSettingRanges=12.4,9.0,5.9 nm, MaxDepth=3280 ft, SeekerFOV=90 / gain 42 / output 220, AntiCountermeasuresBonus=0.45, spoof recovery 2–10 s, SmartFuse=True, Power=27, Mass=314.1, AmmoPoints=608, SupplyCategory=AirTorpedo, parachute physics (ParachuteSlowDown 0.99, ParachuteEndVelocity 100 kn), launch window 100–1000 ft, and Euromod's own model (assets/europack/models/weapons.obj). The two losers are near-twins of each other and differ from the winner on the things that matter: both use GuidanceType=7 (active sonar only), SeekerFOV=60, SeekerGain=10, AntiCountermeasuresBonus=0.15, spoof recovery 8–25 s, and the mk46 asset-bundle + assets/models/ammunition/mu-90/mu90.obj model with a spinning Helice submodel. Euromod - Modern German Navy adds AmmoPoints=260, SupplyCategory=AirTorpedo, MaxVelocity=45, MaxLaunchRange=12 nm, MaxDepth=1450 ft, LaunchReliability=85. French Helicopter Package: AmmoPoints=460, no SupplyCategory, Acceleration=13.5, MaxTurnRate=15, SpeedSettings=32,46,53 kn at ranges 20,14,9 nm, launch window 80–1400 ft, MaxDepth=2400 ft, LaunchReliability=93.


**Silently lost** — The French Helicopter Package's deliberately air-launch-tuned envelope: 20/14/9 nm legs (roughly 60% more reach than the winner's 12.4/9/5.9 nm), LaunchReliability=93 vs 85, a wider 80–1400 ft release window, and higher agility (13.5 G / 15°/s). Also lost: its French-language design comments, and the German pack's hard MaxLaunchRange=12 nm cap. In exchange the winner is the better-modelled weapon — dual-mode homing, 3× the counter-countermeasure resistance and far better depth.


**Risk** — No id collision, no split ownership. Alias-chain dependency: fr_mu_90_air → eu_mu_90_air → eu_mu_90_ship, and both intermediate files are shipped exclusively by the Main Pack, so the chain is safe while that mod is enabled but would leave a bare alias pointing at nothing if it were ever disabled or outranked on those two filenames. Consumers are cross-mod: 3567256221 (Charles De Gaulle & Modern French Navy Pack) aircraft/fr_atl2.ini and four NH90 variants in the French Helicopter Package (fr_nh90, de_nh90, nl_nh90, nl_nh90_tth) — all now fire the Euromod torpedo with the Euromod model. SupplyCategory=AirTorpedo is not a regression: it is the vanilla convention for air-dropped torpedoes (usn_mk46_air.ini, it_a-244s_air.ini all use it). Model files themselves are binaries stripped from this repo, so the Euromod mesh's presence is unverified.


**Mission** — None. No NH90 and no Atlantique 2 appear in NORTHERN FRONT III FINAL NEWEST.


**Recommendation** — Keep the order — Euromod Main Pack above its own sub-packs and above the French Helicopter Package is right, and the winner's MU90 is the better weapon on every axis except raw range. If the NH90s ever fly a mission where drop range matters, patch SpeedSettingRanges into eu_mu_90_air.ini rather than reordering, since reordering the French pack above Euromod would drag other Euromod-owned files with it.


*Sampled: All three fr_mu_90_air.ini copies md5-compared; the German and French copies diffed line-by-line; the winner's full alias chain read (fr_mu_90_air.ini → eu_mu_90_air.ini → eu_mu_90_ship.ini); consumer aircraft files located; vanilla air-torpedo supply-categor…*


### 2 ammunition files: ammunition/gre_as11.ini (AS.11 wire-guided ATGM), ammunition/gre_as12.ini (AS.12 wire-guided ASM)

**Mods** 3629144864 "Euromod - Main Pack" (rank 11) > 3455931957 "Sea Lynx" (rank 107)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** low


Guidance model is the real difference. Euromod sets GuidanceType=0 (command/MCLOS, matching vanilla fr_as11.ini and fr_as12.ini which are also GuidanceType=0) with TerminalApproachDist=1000 and no sea-skimming block. Sea Lynx sets GuidanceType=6 (TV homing), TerminalApproachDist=15.0, and adds a four-key sea-skimming profile (SeaSkimmingAlt=10.0, SeaSkimmingMaxDescentAngle=45.0, SeaSkimmingNoseUp=1.0, SeaSkimmingStartDistToTarget=1000) to a 1960s wire-guided missile. Range: Euromod AS.11 MaxLaunchRange=1.62 nmi and AS.12 4.32 nmi (i.e. the real ~3 km / ~8 km, and consistent with vanilla's 2 / 4 nmi); Sea Lynx inflates these to 3.0 and 8.0 nmi. Mass: Euromod AS.12 Mass=76 kg (correct, vanilla fr_as12 is 75 kg); Sea Lynx AS.12 Mass=522 kg, which is roughly seven times the real weapon. Euromod also adds AmmoPoints (45 / 114) that Sea Lynx omits entirely, and fixes Sea Lynx's copy-paste comment where gre_as11.ini is headed "# AS-12". MaxVelocity is 369 vs 370 kt — noise. Both copies point at the identical models: weapons/as_11/ and weapons/as_12/.


**Silently lost** — Only the Sea Lynx author's longer reach and TV-homing/sea-skimming behaviour, plus the 522 kg AS.12 mass. All of it looks like error rather than intent, so nothing valuable is lost. No model, texture or display-name content is lost: the model paths are identical in both copies, and the language_*/ammunition_names.ini entries (gre_as11=AS-11,ASM / gre_as12=AS-12,ASM) merge rather than override, so Sea Lynx's names still apply.


**Risk** — SPLIT OWNERSHIP, confirmed and benign: the ammunition is won by Euromod while the only units that carry it — fr_sea_lynx.ini and fr_sea_lynx_4.ini, each with 4x gre_as12 rails — belong to the loser, 3455931957. The winning file still coheres: same weapon type, same ASuW target type, same mesh paths, so the rails render and fire. ASSET DIRECTION IS INVERTED: Euromod ships no weapons/ folder at all; the winning file's ResourcesFolder=weapons/as_11/ and weapons/as_12/ resolve only because Sea Lynx ships /home/user/Seapower-mods/mods-source/3455931957/weapons/as_11/as_11_mat.ini and .../as_12/as_12_mat.ini. If Sea Lynx were ever disabled, Euromod's copies would be orphaned (and unused anyway). DEAD CONTENT: gre_as11 has no consumer anywhere in the collection — grep across all 133 mods finds it only in the two ammunition definitions and six language_*/ammunition_names.ini lines. Neither Sea Lynx aircraft actually mounts it. No id collision.


**Mission** — None. NORTHERN FRONT III FINAL NEWEST fields no Greek, French, Dutch or West German Lynx; the RN helicopter it does field is rn_sea_lynx_has3 (from 3599752717), which carries rn_sea_skua and the Euromod Stingray variants, not gre_as11/gre_as12.


**Recommendation** — Leave as is. Euromod's version is both more realistic and closer to the vanilla fr_as11/fr_as12 convention, and it is the only one of the two that supplies AmmoPoints for the supply system. No reorder needed.


*Sampled: Both files read in full and diffed. Also read the only consumers, /home/user/Seapower-mods/mods-source/3455931957/aircraft/fr_sea_lynx.ini and .../fr_sea_lynx_4.ini, plus the vanilla equivalents /home/user/Seapower-mods/mods-source/_vanilla/original/ammunitio…*


### 1 ammunition file: ammunition/wp_aa-11_mi.ini (R-73/AA-11 Archer, improved seeker variant)

**Mods** 3481228992 "ChengDu J-10C Vigorous Dragon" (rank 83) > 3526982088 "XIAN JH-7A (歼轰-7A 飞豹)" (rank 84) > 3451166840 "Su-25 Frogfoot" (rank 110)  

**Winner** 3481228992 ChengDu J-10C Vigorous Dragon · **Risk** low


The top two are byte-for-byte identical (md5 58ae41ec99aed36130b5e01e0a58b7c0 for both 3481228992 and 3526982088, 7982 bytes), so the ordering between them is irrelevant. The Su-25 copy (8627 bytes) is the only real variant and differs in three places. First, flight model: the Su-25 copy sets ApplyKinematics=True with AccelerationTime=5.5 / Acceleration=13.35 G / no sustainer and MaxFlightTime=20, while the winner has no ApplyKinematics key and uses the legacy VelocityBleed=0.7 / AccelerationTime=2 / Acceleration=20.0 model with no flight-time cap. Vanilla wp_aa-11.ini uses ApplyKinematics=True, and 84 of the vanilla ammunition files set it. Second, top speed: 1520 kt (winner) vs 1600 kt (Su-25); vanilla is 1700. Third, ECCM keys: the winner writes CounterMeasuresRejection=80 / NoiseRejection=80, the Su-25 copy writes AntiCountermeasuresBonus=0.2. Grep across the entire vanilla data tree finds zero occurrences of CounterMeasuresRejection or NoiseRejection anywhere, while AntiCountermeasuresBonus appears in 169 vanilla ammunition files — the winner's ECCM is expressed in keys the current build appears not to use. Everything else matches: Power=5, KillProbability=0.8, GuidanceType=1 (IR), MaxTurnRate=60, MinLaunchRange=0.1 / MaxLaunchRange=10.8 nmi, SeekerFOV=5, SeekerGimbalFOV=85, SeekerPassiveRange=7.02, and the identical model path assets/models/ammunition/R73/ with r73_mat.ini.


**Silently lost** — The Su-25 author's current-schema tuning: ApplyKinematics=True, the 20-second MaxFlightTime hard cap, and — the one that probably matters — AntiCountermeasuresBonus=0.2. Because the winner expresses countermeasure resistance only through CounterMeasuresRejection/NoiseRejection, keys absent from every vanilla file, the surviving Archer most likely falls back to default (no) countermeasure resistance rather than the 80% the winner intends.


**Risk** — No id collision. SPLIT OWNERSHIP, confirmed: the only unit in the whole collection that mounts wp_aa-11_mi is /home/user/Seapower-mods/mods-source/3451166840/aircraft/wp_su-25sm3.ini, owned by the bottom-ranked mod, so the Su-25's Archer is defined by the J-10C mod. The winning file still coheres with it — same id, same IR guidance, same 10.8 nmi reach, same R73 mesh — so nothing dangles. No dangling asset reference: all three mods ship assets/models/ammunition/R73/textures/, so the mesh path resolves regardless of which copy wins. Latent schema concern only: the winner's obsolete ECCM keys, discussed above.


**Mission** — None directly. NORTHERN FRONT III FINAL NEWEST fields wp_su-35s (x6) and "plaf_j16a block3" (x6) but no Su-25, and grep confirms neither those units nor any mission-fielded aircraft reference wp_aa-11_mi — it is used solely by wp_su-25sm3, which is not in the order of battle.


**Recommendation** — Leave the order as it stands. The theoretically cleaner fix is to move 3451166840 above 3481228992 and 3526982088 — it is cheap, because the only other file Su-25 Frogfoot would then win is ammunition/wp_kab-500kr.ini (currently held by 3417446309, rank 34), and it contests nothing else in the collection. But the payoff is a 0.2 countermeasure bonus and a flight-model style change on a missile no mission unit carries, so it does not justify disturbing a 133-mod order. If you want the effect without the reorder, add `AntiCountermeasuresBonus=0.8` and `AntiJammerBonus=0.8` to 3481228992/ammunition/wp_aa-11_mi.ini alongside the legacy keys — which is exactly what 3606774881 does for its own missiles.


*Sampled: All three copies read and diffed pairwise, with md5 comparison. Also read /home/user/Seapower-mods/mods-source/3451166840/aircraft/wp_su-25sm3.ini (the only consumer) and the vanilla baseline /home/user/Seapower-mods/mods-source/_vanilla/original/ammunition/w…*


### 1 ammunition file: ammunition/rn_stingray_air.ini (air-dropped Sting Ray lightweight torpedo)

**Mods** 3629144864 "Euromod - Main Pack" (rank 11) > 3373356293 "Royal Navy Westland Lynx HAS.3 Kitbash [OLD]" (rank 124, catalogued deprecated)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** low


Mostly cosmetic-plus-supply, with one visual change that matters. The winner gives the weapon a real Sting Ray model — ResourcesFolder=weapons/rn_stingray_air/, ResourcesRoot=rn_stingray_air.obj, ResourcesMesh=Stingray, ResourcesMaterial=rn_stingray_mat.ini, ResourcesMeshForLaunch=Stingray_air, with submodel propellers named Propeller_l / Propeller_r — where the loser is still using the Mk 46 placeholder: ResourcesFolder=weapons/usn_mk46/, ResourcesMesh=usn_mk46, propellers usn_mk46_prop_l/_r plus a usn_mk46_stabilizer submodel. The winner also adds three supply-system keys the loser lacks entirely: AmmoPoints=500, SupplyCategory=AirTorpedo, AirLaunched=True. The loser adds AntiCountermeasuresBonus=75 and AntiJammerBonus=25, which is out of range for those keys — every other file in the collection and in vanilla expresses them as 0…1 (Euromod's own values elsewhere are 0.40 / 0.35). Parachute and in-flight effect positions differ by a couple of thousandths. Torpedo performance keys (speed, search pattern, seeker) are unchanged between the two.


**Silently lost** — The Mk 46 placeholder model, the loser's extra Stabilizer submodel definition, and the two out-of-range ECCM values. None of that is worth keeping. Nothing is lost on the supply or performance side — the winner is a strict improvement there.


**Risk** — No id collision. SPLIT OWNERSHIP, confirmed: the only two consumers of rn_stingray_air are /home/user/Seapower-mods/mods-source/3373356293/aircraft/rn_lynx.ini (6 rounds) and .../rn_wildcat.ini, both owned by the loser; the winning ammunition file still coheres with them (same id, same Type=Torpedo, same ASW role), so the racks stay valid. ASSET REFERENCE I COULD NOT VERIFY: the winner points at weapons/rn_stingray_air/. No mod in the collection ships that folder, and the repository is a text-only export (zero .obj files anywhere, and /home/user/Seapower-mods/mods-source/_vanilla/original has no weapons/ directory at all), so I cannot confirm the mesh exists — `weapons/` is a game-internal bundle root, exactly as vanilla's own usn_mk46_air.ini uses it. Euromod's own rn_stingray.ini uses the same path, so the author clearly believes it resolves; treat this as unverified rather than broken. The loser's path (weapons/usn_mk46/) is definitely a vanilla asset, so if the Sting Ray mesh turned out to be missing, the loser's copy would be the safer one — that is the single scenario in which this order should flip.


**Mission** — None. NORTHERN FRONT III FINAL NEWEST fields rn_lph_ocean_asw_13 and assigns rn_sea_lynx_has3=Squadron1,4 and rn_merlin_hm2=Squadron1,8 — and rn_sea_lynx_has3 (from 3599752717) carries rn_sea_skua x4 plus rn_stingray_mod0_air / rn_stingray_mod1_air, not rn_stingray_air. Neither rn_lynx nor rn_wildcat appears in the order of battle.


**Recommendation** — Leave as is. The winner replaces a Mk 46 stand-in with the correct Sting Ray and adds the supply-system keys the weapon needs for replenishment; the loser is a mod its own author has tagged [OLD] and the catalogue lists as deprecated. If you are pruning the collection, 3373356293 is an unsubscribe candidate on its own merits — but note the catalogue's warning that it is the only source of rn_wildcat, so check that before removing it.


*Sampled: Both copies read in full and diffed. Also read /home/user/Seapower-mods/mods-source/3373356293/aircraft/rn_lynx.ini (6x rn_stingray_air), the sibling Euromod definitions rn_stingray.ini, rn_stingray_mod0_air.ini and rn_stingray_mod1_air.ini, and /home/user/Se…*


### 1 ammunition file: ammunition/plan_hq-10.ini (HQ-10 / FL-3000N point-defence SAM)

**Mods** 3775128499 "Modern PLAN Systems" (rank 12) > 3774859959 "PLAN Type 001 Aircraft Carrier Liaoning" (rank 41)  

**Winner** 3775128499 Modern PLAN Systems · **Risk** low


The winner is a fuller, more modern rewrite (9897 vs 7967 bytes). Flight model: the winner sets ApplyKinematics=True with MaxVelocity=1600 kt, AccelerationTime=3 s at 17 G, no sustainer, DragCoefficient=-1, MaxFlightTime=30, plus the drag-reference keys TypicalLaunchVelocity=0, TypicalFiringAlt=0, TypicalTargetVelocity=1200, TypicalTargetAlt=50; the loser uses the legacy model with MaxVelocity=1345 kt, a flat Acceleration=35.0 and no flight-time cap. Agility: the winner is slower to turn (MaxTurnRate=40.0, MaxTurnG=35) than the loser (MaxTurnRate=60.0). Warhead/intercept: winner KillProbability=0.90 with SmartFuse=True, InterceptSpeedPenaltyMultiplier=0.75 and InterceptSizePenaltyMultiplier=0.2; loser KillProbability=0.95, InterceptSpeedPenaltyMultiplier=0.3 and no SmartFuse or size multiplier. Envelope: the winner adds MaxAttackVelocity=3200 kt (the loser has none) and drops the loser's MinAttackAltitude=8.84 ft. ECCM: AntiJammerBonus 0.85 vs 0.9. Launch envelope is identical in both (MinLaunchRange=0.27, MaxLaunchRange=5.4 nmi, MaxAttackAltitude=20000 ft), as are the seeker block (SeekerFOV=2, SeekerGimbalFOV=75, SeekerPassiveRange=5, GuidanceType=1 IR) and the model definition (assets/ammunition/HQ-10.obj, hq-10_mat.ini).


**Silently lost** — The loser's slightly higher raw KillProbability (0.95) and its much higher MaxTurnRate (60 vs 40 deg/s), plus MinAttackAltitude=8.84 ft — which in practice means the winning HQ-10 has no explicit floor against very low sea-skimmers and relies on the general altitude-penalty machinery instead. Given the winner adds SmartFuse, the size-penalty multiplier and a 3200 kt maximum target speed, the trade clearly favours the winner against modern supersonic ASMs.


**Risk** — MALFORMED LINE IN THE WINNING FILE (verified with cat -A): /home/user/Seapower-mods/mods-source/3775128499/ammunition/plan_hq-10.ini line 108 contains a bare `s` on its own line, immediately after LaunchReliability=98 and before the Seeker header. It is a stray keystroke, not a key=value pair. INI parsers normally skip unrecognised lines, so this has most likely been harmless in play, but it sits in a file loaded by every PLAN escort in the mission and is trivially worth removing. No id collision. No split ownership: 3775128499 also wins plan_type_052d_p3.ini, plan_type_052d_p4.ini, plan_type_055_2026.ini and the other seven consuming hulls, so the missile and its launchers come from the same hand. ASSET DIRECTION IS FAVOURABLE: only 3775128499 ships assets/ammunition/hq-10_mat.ini — 3774859959 references the same path but ships no such material — so the winning copy is also the one whose assets are present. The loser's own consumer, plan_type_001.ini (Liaoning), is not in the mission.


**Mission** — Yes, and broadly. NORTHERN FRONT III FINAL NEWEST fields plan_type_055_2026 (x4), plan_type_052d_p3 (x2), plan_type_052d_p4 (x2), plan_type_054a_p5 and plan_cv_type_003 — all of which carry plan_hq-10 as their inner-layer SAM. Every PLAN close-in engagement in the scenario runs on the winning file, stray `s` line included.


**Recommendation** — Keep the order. 3775128499 is the PLAN systems database — the Chinese-fleet analogue of Euromod Main — and it owns both the missile and nine of the ten hulls that fire it, so it is the right authority. One cleanup is worth making: delete the stray line described below.


*Sampled: Both copies read in full and diffed, plus a cat -A pass over lines 100–125 of the winner. Also enumerated every consumer of the id across the collection and checked asset ownership under assets/ammunition/ in both mods.*


### ammunition/wp_as-17.ini

**Mods** 3417446309 MIG-29 Family (line 41) > 3481228992 ChengDu J-10C (line 90) > 3526982088 XIAN JH-7A (line 91)  

**Winner** 3417446309 (MIG-29 Family) — the two losing copies are byte-identical to each other (9138B/b862c83d6b) · **Risk** low


Same Kh-31A anti-ship missile, differently tuned; the raw byte diff looks total because of CRLF/LF line-ending drift, so I diffed with line endings normalised. Real differences are five: warhead Power=37 (winner) vs 24 (losers); MaxVelocity=2310 kt vs 1824 kt; MaxLaunchRange=59.45 nm vs 37.83 nm. Everything else in the flight profile is shared verbatim — Mass=600, GuidanceType=3 (active radar), CIWSDefenceBonus=2, MinLaunchRange=6.5, SeaSkimmingAlt=50 ft, SeaSkimmingStartDistToTarget=18 nm, MaxLoftAlt=15000 ft, SeekerActiveRange=20 nm, Frequency=Ku-Band, PeakPower=35 kW, AntiCountermeasuresBonus=0.2, LaunchReliability=97. Presentation differs too: the winner adds ResourcesMeshForLaunch/ResourcesMeshCanister=launch with ResourcesMeshSwitchTime=3 and NumberOfSubModels=1 with an [Afterburner] submodel, and uses sam_medium_effect + turbojet_sustainer_small for booster/inflight plumes; the losers drop the launch mesh and afterburner, add a [Debris] block (DebrisProbability=95, DebrisLifeTime=10.0), and use aam_effect + DefaultMissileInflightEffect.


**Silently lost** — Only the losers' weaker tuning (Power 24, 1824 kt, 37.83 nm), their [Debris] block, and the aam_effect plume styling. Nothing functional is lost that any enabled aircraft actually needs.


**Risk** — No id collision and no split ownership — a standalone ammunition file with no companions. The winner owns both the definition and the only two aircraft that reference it, so the file and its consumers come from one author and cohere by construction. The one thing I could not verify: the winner's version references ResourcesMeshForLaunch=launch and an [Afterburner] submodel mesh inside kh-31.obj, and the repo mirror strips binaries (zero .obj files collection-wide) — only kh-31_mat.ini survives in all three mods' assets/models/ammunition/KH-31/textures/. So the launch-mesh and afterburner references are UNVERIFIED here rather than known-good or known-broken; since they ship in the same mod as the ini that names them, they are very likely present. Minor cosmetic detail: the winner writes ResourcesFolder=assets/models/ammunition/kh-31/ in lowercase while its material folder is .../KH-31/textures/ — harmless on Sea Power's Windows-only case-insensitive filesystem.


**Mission** — None. Every consumer of the bare wp_as-17 id belongs to the winning mod itself — 3417446309/aircraft/wp_mig-29m_915.ini and wp_mig-29k.ini, plus its own language_en/language_cn ammunition_names.ini. Neither the J-10C nor the JH-7A references wp_as-17: I grepped both and they use the separate wp_as-17a (Kh-31P anti-radiation) id instead, which is Cohort 1 and identical. No MiG-29 variant is fielde…


**Recommendation** — Keep the current order. The winner is both the stronger and the more coherent choice: it is the only mod whose aircraft actually fire this id, its Power=37 / 2310 kt / 59.45 nm figures are the closer match to a real Kh-31A, and it is the only version that ships the launch-canister and afterburner presentation. The losers' copies are dead weight in 3481228992 and 3526982088 — those mods carry the file but never reference it. No change needed, and nothing here should constrain future moves of 3481228992 or 3526982088.


*Sampled: Full line-ending-normalised diff of 3417446309 vs 3481228992, plus md5 confirmation that 3481228992 and 3526982088 are identical to each other. Also enumerated every consumer of the id and checked the KH-31 asset folder in all three mods.*


### ammunition/b-2_gbu_38.ini

**Mods** 3606774881 U.S. Navy 2027 Capabilities mod (line 17) > 3480965706 B-2 Spirit (line 67)  

**Winner** 3606774881 (U.S. Navy 2027 Capabilities mod) · **Risk** low


Two different modelling philosophies for the same GBU-38 JDAM. Type and targeting: winner Type=Bomb with IsInterceptable=True, LandAttackCapability=Installation and CanNotAttackTypes=Vessel,Submarine; loser Type=Missile with LandAttackCapability=All and no CanNotAttackTypes restriction at all. Signature: winner IRSignature=VerySmall, RCS=VerySmall, VisualIdentificationRange=1 nm; loser IRSignature=0.00000000000001, RCS=0.00000000000001, VisualIdentificationRange=0.1 nm — effectively an undetectable, un-engageable bomb. Mass/supply: 253 kg / AmmoPoints=375 / AirLaunched=True (winner) vs 241 kg / AmmoPoints=241, no AirLaunched flag (loser). Release envelope: winner MinLaunchAltitude=2000 ft, MaxLaunchAltitude=65000 ft, MinLaunchRange=1 nm, MaxTurnRate=5, CircularErrorRadius=5 m, LaunchReliability=98; loser MinLaunchAltitude=80 ft, MaxLaunchAltitude=60000 ft, MinLaunchRange=4 nm, MaxTurnRate=4, CircularErrorRadius=10 m, LaunchReliability=97, plus a legacy kinematics block the winner omits (Acceleration=0, MaxVelocity=1000, VelocityBleed=2, AccelerationTime=0, GroupSize=0) and ECCM keys CounterMeasuresRejection=100 / NoiseRejection=75. The loser also enables HitShipExplosion and HitAirExplosion effects that the winner leaves commented out. Both share MaxLaunchRange=15.0 nm.


**Silently lost** — For the B-2, three real capabilities. Its GBU-38s can no longer be released against ships or submarines (CanNotAttackTypes=Vessel,Submarine) nor against mobile land targets (LandAttackCapability=Installation instead of All) — fixed installations only. They become interceptable (IsInterceptable=True plus a real RCS/IR signature instead of the loser's ~1e-14 stealth values), so SAMs and CIWS can now engage them in flight. And the release floor rises from 80 ft to 2000 ft, ruling out the low-level delivery the B-2 mod's envelope allowed. Also dropped are the loser's ECCM rejection values and its ship/air hit-effect classes.


**Risk** — No id collision — one filename, one registration. There IS a genuine split of a different kind, worth naming precisely: the consuming unit file usaf_b-2_spirit.ini is owned uncontested by 3480965706 (it is the only mod that ships it), while the ammunition its loadouts name is won by 3606774881. That is the classic loser-owns-the-unit, winner-owns-the-weapon pattern. It does not dangle — the id still resolves, so the B-2's four loadout stations (Station1=b-2_gbu_38 on 5x4_Rack_f and 5x4_Rack_b) still populate — but the B-2 now carries a weapon with a materially narrower mission set than its author wrote it for. Because the B-2 is not fielded in the active mission, this is latent rather than live; it would surface the moment someone builds a mission around the B-2 and finds its JDAMs will not attack TELs or ships. Two things I could not verify: the rack ids 5x4_Rack_f / 5x4_Rack_b resolve to no ammunition file anywhere (they appear only inside usaf_b-2_spirit.ini and 3509329205/aircraft/wp_tu-160.ini), which is consistent with them being aircraft-model attachment-point names rather than ammo ids — I am NOT claiming a dangling reference there; and the catalog records the B-2 mod's own author warning that it 'Requires AnchorChain and SeaLifter to be correctly installed. Subscribing isn't enough. You need the preloader.'


**Mission** — Yes, on the winning side — and notably NOT on the B-2's side. I traced this carefully. The B-2 itself is not fielded anywhere in NORTHERN FRONT III FINAL NEWEST: usaf_b-2_spirit is not a mission Type, is not in the Ford's air group, and is not in any of the three RAAF airbase groups the mission uses (I checked airbase_raaf_darwin, _scherger and _townsville — zero B-2 references). But b-2_gbu_38 I…


**Recommendation** — Keep the current order — do not promote 3480965706. The winner is the right choice on three grounds: it is the version the SEST_Integration Hornet loadouts were built against, those Hornets are what the mission actually flies, and its model is the physically honest one (a JDAM is a real object with a real radar cross-section, not a 1e-14 RCS ghost that no defence can engage). Promoting the B-2 mod to line 17 would hand every Ford-based Hornet in the mission an uninterceptable, all-target-class 241 kg bomb with an 80 ft release floor, which is a bigger distortion than the one it fixes. If the user later wants the B-2 to regain anti-ship and anti-mobile capability, the correct fix is a small SEST patch defining a separate id (e.g. b-2_gbu_38_all) referenced only from usaf_b-2_spirit.ini, not a reorder — that keeps the Hornets on the 2027 mod's definition while giving the bomber back its envelope.


*Sampled: Full line-ending-normalised diff of both files, plus consumer traces in both mods, in SEST_Integration, and in the mission's carrier and airbase air groups.*


### ammunition/dts_anaaq-13.ini

**Mods** 3636386513 F-15 EX Eagle II (line 78) > 3553116604 F-15E StrikeEagle (line 79)  

**Winner** 3636386513 (F-15 EX Eagle II) · **Risk** low


Functionally identical, cosmetically renamed. Both files define the AN/AAQ-13 LANTIRN navigation pod identically: Type=Container, Mass=208 kg, one sensor system ([SensorSystem1] Type=Visual, SystemName=AN/AAQ-13, Mount=Dummy, ModuleType=Sensor), no AssetBundle block, same ResourcesFolder=assets/models/weapon/ammunition/anaaq-13/, same ResourcesMesh=hull.001, same ResourcesMaterialFolder. The ONLY two differing lines are the asset filenames: winner ResourcesRoot=dts_anaaq-13.obj and ResourcesMaterial=dts_anaaq-13_mat.ini; loser ResourcesRoot=anaaq-13.obj and ResourcesMaterial=anaaq-13_mat.ini. Nothing about the pod's mass, sensor, or behaviour changes.


**Silently lost** — Nothing of substance — only the loser's alternate asset filenames. No stat, sensor or capability differs.


**Risk** — No id collision, no split ownership on the unit side (usaf_f-15ex_SEII.ini is owned by SEST_Integration at the top of the order, which is by design per the project's SEST invariant). Critically, I verified the asset coherence rather than assuming it: each mod ships the material file its own ini names — 3636386513 ships assets/models/weapon/ammunition/anaaq-13/textures/dts_anaaq-13_mat.ini and 3553116604 ships .../textures/anaaq-13_mat.ini. The two filenames are different, so they do not contest each other and both land in the merged asset folder; the winner's reference therefore resolves. The residual, low-severity concern is the cross-consumer case: 3553116604/aircraft/usaf_f-15e_SE.ini also references dts_anaaq-13 and will now be handed the winner's dts_anaaq-13.obj / dts_anaaq-13_mat.ini rather than its own anaaq-13.* pair. Since both asset sets coexist in the merged folder that should render fine, and in any case the difference is purely a pod model. I must flag one verification limit: the mirror strips binaries (zero .obj files collection-wide), so .obj presence is inferred from the parallel _mat.ini naming in each mod rather than observed directly. Neither version has a display-name entry for dts_anaaq-13 in any language_en/ammunition_names.ini, so the pod will show its raw id in the UI under either winner — a pre-existing cosmetic gap, not caused by this conflict.


**Mission** — Yes, and this is the most directly mission-critical cohort of the nine — but it is currently correct. The mission fields Type=usaf_f-15ex_SEII, and that airframe is additionally spawned from two mission-fielded bases (airbase_raaf_darwin and airbase_raaf_scherger both list f-15ex in their air groups). The F-15EX's loadouts mount this pod heavily: SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII.ini c…


**Recommendation** — Keep the current order. The winner is correct and the ordering is load-bearing: 3636386513 must stay above 3553116604 because the mission-fielded usaf_f-15ex_SEII (via SEST_F-15EX_Revamp, which ships no ammunition of its own) depends on the dts_-prefixed asset naming that only 3636386513 provides. Demoting the F-15EX mod below the F-15E mod would swap in the anaaq-13.* asset names — likely still cosmetic, but it would be a change to a pod mounted on an airframe the mission flies from two bases, for no benefit. Optional low-priority polish unrelated to load order: neither mod names dts_anaaq-13 in its language files, so adding a display-name key in a SEST pack would stop the pod showing as a raw id in the loadout UI.


*Sampled: Full line-ending-normalised diff of both files (1191B vs 1217B), full read of the winner's file, the asset folder contents of both mods, and consumer traces including the SEST pack and the mission's airbase air groups.*


### vessels/usn_cvn_nimitz_2000s.ini, vessels/usn_cvn_nimitz_2000s_variants.ini

**Mods** 3430135740 F/A-18 Murder Hornet with AIM-174B (rank 15) > 3461091581 Air Deck Operations Upgrade - Nimi (rank 19) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (rank 28)  

**Winner** 3430135740 (F/A-18 Murder Hornet with AIM-174B) wins both files · **Risk** low


3461091581 is a completely different animal: 12,064 lines vs 2,076/2,077, with 499 [Elevator*] sections, 189 [TaxiPath*], 155 [F*] and 130 [LaunchPoint*] blocks. Its [FlightDeck] reads AircraftCapacity=85, NumberOfElevators=499, NumberOfLaunchPoints=130, NumberOfRecoveryPoints=4, NumberOfTaxiPaths=284, plus NumberOfDCTeams=4, SpawnInterval=12, LaunchDelay=10, HoldWaypoints (four-point stack at 3000 ft), and slower deck handling (Forwards/Backwards/SlowTaxi 10/-8/8). The winner keeps the stock deck: AircraftCapacity=110, NumberOfElevators=4, NumberOfLaunchPoints=12, NumberOfRecoveryPoints=2, NumberOfTaxiPaths=14, DeckParkSlots=40, GroundCrewCount=12, LaunchDelay=5, taxi 15/-10/10. Air groups differ too — winner: usn_fa-18f_blk3 (Sqn1,15|Sqn9,15), usn_fa-18f, usn_fa-18e, usn_e-2c (Sqn6,4), usn_ea-18g, usn_s-3a, usn_sh-3h (Sqn1,8). 3461091581: usn_fa-18e (Sqn2,25), usn_fa-18f (Sqn9,25), usn_e-2c, usn_ea-18g, usn_s-3a, usn_mh-60r (Sqn1,8) — no Block III, but MH-60R instead of the 1970s SH-3H. Against the deprecated 3426791311 the winner differs by only three lines: it adds usn_fa-18f=Squadron1,15|Squadron9,15 to [AirGroup] and raises AircraftCapacity 85->110. Variants files: winner declares NumberOfVariants=2 while both losers declare 3; all three still contain a fully-written [Variant3] CVN-70 Carl Vinson block. Winner's variants use usn_fa-18f and usn_sh-3h; 3461091581's use usn_fa-18f + usn_mh-60r (Squadron1/2/3 per variant) and add a CustomAirGroup to [Default]; 3426791311's use usn_fa-18f_blk3 and add usn_f-35c=Squadron1,15 to Variant1 plus per-variant FlightDeck_AmmoCapacity=1200000/1200000 and four FlightDeck_AccountableAmmunitionCategory lines (Phoenix 84, Harpoon 48, AirTorpedo 80, AdvancedARM 64).


**Silently lost** — From 3461091581: the entire deck-choreography rework as applied to the stock hull — 499 deck spots, 130 launch points, 284 taxi paths, 4 recovery points, HoldWaypoints, SpawnInterval, NumberOfDCTeams — plus MH-60R in place of SH-3H. From 3426791311: the F-35C in Variant1, and the per-variant deck magazine accounting. The winner also drops NumberOfVariants from 3 to 2, so the CVN-70 Carl Vinson variant of the stock Nimitz 2000s becomes unselectable even though its block is still present in the file. Crucially, the deck-ops work is NOT lost from the collection: 3461091581 also ships usn_cvn_nimitz_2000s_adou.ini and _adou_variants.ini, which no other mod contests, and I confirmed that unit carries the full 85/499/130/284 deck plus the MH-60R air group. Players can still field the deck-ops Nimitz under the id usn_cvn_nimitz_2000s_adou.


**Risk** — No id collision and no split ownership — 3430135740 wins both the hull and its variants file, so they cohere. Air-group references all resolve: usn_fa-18f_blk3, usn_fa-18f, usn_fa-18e and usn_ea-18g are defined by four enabled mods each, usn_mh-60r by three, and usn_sh-3h comes from _vanilla/original/aircraft. FlightDeck_AmmoCapacity=1200000/1200000 and the four accountable-ammunition categories are still present in the winner's main ini (lines 56-58), so dropping the per-variant copies inherits rather than dangles. The only genuine regression is NumberOfVariants=2, which hides a variant the file still defines. Losing the deck-ops rework on the stock hull is a feature loss, not a defect, and it is recoverable via the uncontested _adou unit.


**Mission** — None. The active mission fields no Nimitz-class hull at all (zero 'nimitz' matches); its carriers are usn_cvn_ford_jsf, plan_cv_type_003, plan_cvn_004, ru_cv_varyag and rn_lph_ocean_asw_13. The mission does field usn_fa-18f_blk3 three times, but via its own CustomAirGroup lines on other hulls, and the Block III aircraft file itself is won by 3606774881 at rank 10 (which also carries AIM-174B — 12…


**Recommendation** — Keep 3430135740 on top. It is the mod the collection is built around (AIM-174B), it is the only copy that puts Block III Super Hornets in the stock Nimitz air group, and it raises capacity to 110; the deck-ops content it displaces remains fully playable as usn_cvn_nimitz_2000s_adou. Two cheap fixes are worth making in the winner: set NumberOfVariants=3 to restore the already-written CVN-70 Carl Vinson variant, and swap usn_sh-3h for usn_mh-60r in the [AirGroup] and in Variant1/2/3 — an SH-3H on a 2026 Indo-Pacific deck is two generations stale and MH-60R is defined by three enabled mods. If you decide you would rather have the deck-ops rework on the stock hull instead, the move is unusually cheap: 3461091581 ships only four unit files and already wins two of them, so promoting it above rank 15 flips exactly these two files and nothing else — but you would give up Block III in the default air group and drop capacity 110->85.


*Sampled: Both files from all three mods. Full section census of the three main inis (275 vs 1244 vs 275 sections), full diffs of both variants files, header/[AirGroup]/[FlightDeck] blocks of all three main inis, plus 3461091581/vessels/usn_cvn_nimitz_2000s_adou.ini to…*


### ammunition/plan_yj-18.ini

**Mods** 3775128499 Modern PLAN Systems (rank 12) > 3502273861 ARRW (AGM-183) (rank 116)  

**Winner** 3775128499 (Modern PLAN Systems) · **Risk** low


Two genuinely different missiles sharing a filename. The winner is a purpose-built YJ-18: Mass=2000 kg, AmmoPoints=4800, CIWSDefenceBonus=5 and MissileDefenceBonus=0.2 (anti-intercept manoeuvring), IRSignature=Small with a numeric RCS=0.45, Power=49 / ImpactSize=Large, TerrainFollowFlight=True at SeaSkimmingAlt=45 ft with WobblingStrength 8 / Speed 1, a proper two-speed profile — MaxVelocity 530 kt cruise then a terminal sprint via FinalFlightPhaseAlt=30 / FinalFlightPhaseDistToTarget=35 nm / TerminalAlt=15 / TerminalVelocity=1900 / TerminalApproachDist=23 / TerminalDiveDistance=1.0 / TerminalVerticalTurnRate=30 — MinLaunchRange 25 / MaxLaunchRange 351.3 nm, MaxTurnRate 15 with LaunchTurnRate 50, SeekerFOV 60,30, SeekerActiveRange 20 nm, Ku-Band at PeakPower 35 kW, TargetMemory=True, DefaultIgnoredTypes=LandUnit, UseFinalFlightInLandMode=False, snake search (SearchMode=1, SearchVelocity 1824, SnakeSearchAngle 30, cycle 4.0 s), and modern ECCM keys AntiCountermeasuresBonus=0.6 / AntiJammerBonus=0.6. The loser's copy is annotated '# TASM' at line 5 and is a re-badged Tomahawk anti-ship missile: IRSignature=Tiny / RCS=Tiny (categorical, not numeric), Power=55 / ImpactSize=Medium, no CIWS or missile-defence bonuses, no terrain following, SeaSkimmingAlt=20, no pop-up phase at all, MaxVelocity 550 / MaxLaunchRange 450 nm, MaxTurnRate 30, SeekerFOV 60,10, SeekerActiveRange 30 nm, PeakPower 50 kW, SearchMode=0, a [Debris] block reusing usn_rgm-109_d, the usn_rgm-109 booster effect, and — decisively — the dead legacy keys CounterMeasuresRejection=95 / NoiseRejection=95, which appear zero times in vanilla 0.8.2.


**Silently lost** — From 3502273861: the 450 nm reach, the [Debris] section, and the higher 55-power/30 kW-larger seeker figures. None of it is desirable — it is Tomahawk data wearing a YJ-18 filename, and its ECCM would evaluate to engine defaults because the keys it uses are obsolete.


**Risk** — No id collision, no split ownership — hull and weapon come from the same mod. No dangling references. The only thing worth flagging is the trap: 3502273861 is the ARRW (AGM-183) mod and ships exactly two ammunition files, usn_arrw.ini and plan_yj-18.ini. The YJ-18 is vestigial baggage that has nothing to do with that mod's purpose, and if 3502273861 were ever promoted above rank 12 for the sake of ARRW, it would silently replace the PLAN's primary anti-ship missile on four mission-fielded Type 055s with a Tomahawk clone that has no terminal sprint and non-functional ECCM.


**Mission** — Yes, and the winner is on the right side of it. The active mission fields 4x plan_type_055_2026, 2x plan_type_052d_p3, 2x plan_type_052d_p4, plan_type_051b_2017 and plan_type_054a_p5. plan_yj-18 is referenced by nine vessel files — plan_type_055_2026, plan_type_055_2020, plan_type_052d_p1/p2_1/p2_2/p3/p4, plan_ss_type_039a and plan_ss_type_039b — and every one of those files is owned by 377512849…


**Recommendation** — No change — 3775128499 at rank 12 is correct and should stay well above 3502273861 at rank 116. Record the constraint explicitly in the load-order notes: 3502273861 must never rise above 3775128499. Better still, if you control the local copies, delete 3502273861/ammunition/plan_yj-18.ini outright; the mod does not need it and its presence is a standing hazard to a weapon the mission depends on.


*Sampled: Full normalized diff of both copies, plus the 3502273861 mod inventory and a trace of every vessel that fires the id.*


### ammunition/dts_gbu-32.ini

**Mods** 3760871384 Dingtools Weapon Pack (rank 9) > 3636386513 F-15 EX Eagle II (rank 71) > 3553116604 F-15E StrikeEagle (rank 72)  

**Winner** 3760871384 (Dingtools Weapon Pack) · **Risk** low


Six lines, all functional. LandAttackCapability=Installation (winner) vs All (both losers) — the winner's GBU-32 can only be tasked against fixed installations, not mobile land targets. MidCourseCorrection=3 (winner) vs 0; despite the inline comment listing only 0/1/2, value 3 is legitimate — it appears seven times in vanilla 0.8.2 ammunition. TerminalApproachDist=10 nm (winner) vs 1000 nm, i.e. the winner turns the seeker on at 10 nm rather than at launch. MaxTurnRate=15 vs 6 deg/s. SeekerFOV=1 vs 0.1 degrees. SeekerPassiveRange=1 vs 100 nm. Everything else matches, including GuidanceType=1, ApplyKinematics=True, MinLaunchRange 1 / MaxLaunchRange 15 nm, MinLaunchAltitude 500 / MaxLaunchAltitude 60000 ft, LaunchReliability 95, TargetMemory=True and the vertical wobble parameters.


**Silently lost** — From the two F-15 mods: the unrestricted LandAttackCapability=All and the 100 nm passive seeker range. The 100 nm figure is not credible for a GPS-guided 1000 lb JDAM — it reads as an untuned copy-paste — and the two losers are identical to each other, so only one distinct alternative is actually being discarded.


**Risk** — No id collision, no split ownership, no dangling references — the ammunition is Dingtools' own dts_* namespace and the consuming F-15EX file is won by a SEST pack that is designed around it. The Installation restriction is deliberate and internally consistent, not an accident: across the seven Dingtools GBU files, the pure-GPS weapons dts_gbu-31, dts_gbu-32 and dts_gbu-75 are all set to Installation, while the seeker-equipped dts_gbu-39 (SDB) and dts_gbu-53 (StormBreaker) are set to All. That is a coherent weapons-pack philosophy and it matches how JDAM actually works — a fixed-coordinate weapon cannot service a moving target. The only real risk is player expectation: someone who plans a TEL hunt around the F-15EX's StrikePrecision loadout will find the tasking refused with no explanation.


**Mission** — Yes. The active mission fields 4x usaf_f-15ex_SEII, whose winning file is _vanilla/SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII.ini (a SEST pack, and by the project's stated invariant it outranks every workshop mod). Its [WeaponSystem1StrikePrecision] loadout carries six dts_gbu-32 — Stations 11-14 tagged |JDAM32 plus Stations 18-19. So the winner's LandAttackCapability=Installation is what those…


**Recommendation** — No change. 3760871384 at rank 9 is the author of the dts_* namespace the SEST F-15EX pack is built on, and its GBU-32 is the tuned, internally consistent version; the two F-15 mods are carrying an untuned copy with a nonsensical 100 nm passive seeker on a GPS bomb. Do brief the operational consequence rather than the file: for the mission's mobile-TEL targets the F-15EX needs dts_gbu-39 or dts_gbu-53 (both LandAttackCapability=All) rather than the StrikePrecision GBU-32 loadout — or, if you want GBU-32 usable against TELs, edit the single line in 3760871384/ammunition/dts_gbu-32.ini rather than reordering, since promoting either F-15 mod above rank 9 would hand it the rest of the Dingtools weapon pack as well.


*Sampled: All three copies diffed (the two losers are identical to each other after line-ending normalization). Read the winner's full [Guidance] block, surveyed LandAttackCapability across all seven Dingtools GBU files, checked MidCourseCorrection=3 against vanilla us…*


### ammunition/mbd_pyl_ofab-100.ini, ammunition/plaaf_hf-14.ini (2 files)

**Mods** 3486502935 Type 003 Fujian / Type 004 CVN Air Wing > 3481228992 ChengDu J-10C Vigorous Dragon > 3526982088 XIAN JH-7A (歼轰-7A 飞豹) > 3436170138 Shenyang J-11  

**Winner** 3486502935 (Type 003 Fujian / Type 004 CVN Air Wing) · **Risk** low


For BOTH files, and against ALL THREE losers, the diff is a single line — line 39, ResourcesFolder. Winner: ResourcesFolder=assets/ammunition/models/. All three losers, identically: ResourcesFolder=assets/models/ammunition/UB-32-57/. Every ballistic, attachment and salvo value is identical: mbd_pyl_ofab-100 is a Type=Container, Mass=85, Ammunition=wp_fab-100, NumberOfAttachments=6, SalvoFireAmount=6, ResourcesRoot=mbd2.obj/ResourcesMesh=mbd2; plaaf_hf-14 is a Type=Container, Mass=51.25, Ammunition=plaaf_130-Ⅱ_rocket, NumberOfAttachments=4, SalvoFireAmount=2, ResourcesRoot=hf-14.obj/ResourcesMesh=hf-14. Both share the same AssetBundle block (usn_rim-7 meshes) and ResourcesMaterialFolder=aircraft/wp_mig-21/ in every version.


**Silently lost** — Only the losers' model path. No stat, weapon, loadout, sensor or salvo content is lost — the files are otherwise character-for-character the same.


**Risk** — No id collision, no split ownership. Possible model-path regression, NOT proven: no directory named assets/ammunition/models exists in any mod folder in this checkout (repo-wide find returned nothing — 3486502935 has only assets/ammunition/materials/ and assets/aircraft/), whereas assets/models/ammunition/UB-32-57/ does exist in 3481228992, 3526982088 and 3436170138. Counter-caveat that stops this being a hard dangling-reference call: this mirror strips binary assets entirely (0 .obj and 0 texture files repo-wide), so neither path actually contains mbd2.obj or hf-14.obj here and the real game install may resolve either. Treat as 'winner's path is the suspect one, verify visually in game'. Separately, plaaf_hf-14 is dead content: it is defined by four enabled mods and referenced by ZERO aircraft loadout files anywhere in the collection (grep across all mods, excluding language files, returns only the four ammunition definitions themselves).


**Mission** — None. mbd_pyl_ofab-100 is consumed only by 3436170138/aircraft/plaaf_j-11.ini and plaaf_j-11a.ini — the lowest-priority mod in the cohort — and the mission fields no J-11 (its PLA air is plaaf_jh7a ×4, plaaf_kj-500, plan_j-50 ×3, plus carrier air groups plan_j-15 / j-15d / j_15t / kj600 / z-8). plaaf_hf-14 is consumed by nothing at all.


**Recommendation** — Leave the order as it is — there is nothing to gain, since the stat content is identical and the only consumer (the J-11) is not in the mission. If the J-11's bomb rack or rocket pod renders wrong in game, fix it with a one-line SEST patch setting ResourcesFolder=assets/models/ammunition/UB-32-57/ rather than by reordering four mods. Consider dropping plaaf_hf-14 from the conflict watchlist entirely: it is referenced by no aircraft in the collection.


*Sampled: Both files diffed across all four mods (8 files). Read the winner's copies of both in full (General, Ammunition, Models blocks). Enumerated the assets/ trees of all four mods and ran a repo-wide find for the referenced meshes and for any directory matching as…*


### ammunition/plaaf_pl-5c.ini (1 file)

**Mods** 3486502935 Type 003 Fujian / Type 004 CVN Air Wing > 3481228992 ChengDu J-10C Vigorous Dragon > 3526982088 XIAN JH-7A (歼轰-7A 飞豹) > 3433577445 Shenyang J-8  

**Winner** 3486502935 (Type 003 Fujian / Type 004 CVN Air Wing) · **Risk** low


The winner's copy is byte-identical to 3481228992's and 3526982088's — three of the four mods ship exactly the same file. Only 3433577445 (J-8) differs, and substantially. Winner/majority: InitialFlightPhaseDuration=0.5, MaxVelocity=1337.6, VelocityBleed=0.4, AccelerationTime=2.7, Acceleration=22, MinLaunchRange=0.7, SeekerPassiveRange=10.0, CounterMeasuresRejection=75 + NoiseRejection=80, and no AmmoPoints or AirLaunched keys. J-8 version: adds AmmoPoints=123 and AirLaunched=True; InitialFlightPhaseDuration=0.3; a full kinematics block (ApplyKinematics=True, MaxVelocity=1600, AccelerationTime=3, Acceleration=24, SustainerAccelerationTime=-1, SustainerAcceleration=-1, DragCoefficient=-1, MaxFlightTime=30, annotated '#---- Total Δv ≈ 705 ≈ 2.07Ma'); MinLaunchRange=0.2; adds MaxAttackVelocity=1000; SeekerPassiveRange=6; and replaces CounterMeasuresRejection/NoiseRejection with AntiCountermeasuresBonus=0.25.


**Silently lost** — The J-8 mod's modernised PL-5C: the ApplyKinematics flight model (1600 kn top speed, 30 s hard flight-time limit, explicit drag), the shorter 0.2 nm minimum launch range, the AmmoPoints=123 supply cost, the AirLaunched=True encyclopedia flag, and — most importantly — AntiCountermeasuresBonus=0.25, the countermeasure key the current base game actually reads.


**Risk** — No id collision, no split ownership, no dangling refs. There IS a latent content defect in the winning file, independent of the ordering: it resists countermeasures via CounterMeasuresRejection=75 / NoiseRejection=80, and those keys appear in ZERO base-game ammunition files (mods-source/_vanilla/original/ammunition), whereas AntiCountermeasuresBonus appears in 171 vanilla files and ApplyKinematics in 84. The winning PL-5C is therefore very likely falling back to default flare resistance, and it carries no AmmoPoints so it costs nothing to rearm.


**Mission** — YES, but harmlessly. The mission fields plaaf_jh7a ×4, and 3526982088/aircraft/plaaf_jh7a.ini is one of the two consumers of plaaf_pl-5c. Because 3526982088's own copy is byte-identical to the winner's, the mission's JH-7As get precisely what their author intended — the override changes nothing for them. The other consumers, 3433577445/aircraft/plaaf_j-8e.ini and plaaf_j-8b.ini, are not in the mi…


**Recommendation** — Do not reorder. Promoting 3433577445 (line 108) above 3486502935 (line 56) to rescue one weapon would move an entire J-8 mod 52 places up the stack for a unit the mission never fields, and it would push the J-8's PL-5C onto the mission's JH-7As against their author's intent. If you want the flare resistance to actually take effect, patch it: a SEST copy of ammunition/plaaf_pl-5c.ini identical to the winner's but with AntiCountermeasuresBonus=0.25 replacing the two dead keys, plus AmmoPoints=123.


*Sampled: The file read/diffed across all four mods. Cross-checked the key schema against the base game: counted CounterMeasuresRejection / AntiCountermeasuresBonus / ApplyKinematics occurrences in mods-source/_vanilla/original/ammunition, and confirmed vanilla ships i…*


### ammunition/usn_mk54_air.ini (1 file)

**Mods** 3629144864 Euromod - Main Pack > 3737267013 United States Naval Aviation > 3413868677 Red Storm Arsenal  

**Winner** 3629144864 (Euromod - Main Pack) · **Risk** low


Euromod vs 3737267013: two lines only. ResourcesMaterialFolder=assets/europack/materials/usn_mk46/ (winner, verified present with usn_mk54_mat.ini inside) vs assets/models/ammuntion/mk46/ (loser — note the misspelling 'ammuntion'); and SonarAudioClip=audio/environment/Sonar-MF (winner) vs audio/environment/Sonar-Mk54.wav (loser). Red Storm Arsenal's version is a different generation of the file: MaxVelocity=55 kn vs the winner's 45, MaxTurnRate=20 vs 15, MaxLaunchRange=8 nm vs 4.9, and it has NO TerminalVelocity / SpeedSettings / SpeedSettingRanges — the winner has TerminalVelocity=45.0, SpeedSettings=35,45 and SpeedSettingRanges=5.5,4.9. RSA uses SearchMode=3 (Spiral) with SpiralSearchParams=0,900, SpiralSearchRadius=0.5, SpiralSearchAngle=6.0 and DefaultDepth=200; the winner uses SearchMode=1 (Snake). RSA additionally carries MinAfterSpoofEffectTime=3 / MaxAfterSpoofEffectTime=15.0, AntiJammerBonus=0.6, SearchVelocity=36.0, and an explicit 3-submodel model block (Propeller_Left, Propeller_Right, Stabilizer). Shared across all three: Mass=230, AmmoPoints=460, SupplyCategory=AirTorpedo, Power=27, GuidanceType=10, VesselAttackGuidanceType=8, MaxDepth=1900 ft, SeekerFOV=120, seeker active/passive 2 nm, AntiCountermeasuresBonus=0.35, LaunchReliability=95, ReattackMode=1, ResourcesFolder=weapons/usn_mk46/.


**Silently lost** — From Red Storm Arsenal: the 8 nm air-launch envelope (the winner caps at 4.9 nm), the 55-kn dash, spiral search with an explicit 0-900 ft ceiling/floor and 200 ft default search depth, AntiJammerBonus=0.6, the after-spoof recovery timers, and the propeller/stabilizer submodel definitions. From 3737267013: only the dedicated Sonar-Mk54.wav ping sample — the winner reverts to the generic vanilla Sonar-MF clip.


**Risk** — No id collision, no split ownership. The winner's material path is the only one of the three verified to exist on disk (3629144864/assets/europack/materials/usn_mk46/usn_mk54_mat.ini); the runner-up's path contains a typo ('ammuntion'), so this override is actually cleaning up a bad reference. The only real loss is behavioural: RSA's 8 nm range and spiral search are gone, halving the standoff of every Mk54 air drop in the collection. That is defensible — the winner's SpeedSettings/SpeedSettingRanges pair is a current-engine feature RSA's file predates, and 4.9 nm at 45 kn is the more conservative figure.


**Mission** — Minor but real. jp_sh-60k consumes usn_mk54_air and the mission fields it as a helicopter detachment (jp_sh-60k=Squadron1,1). Other consumers — usn_p_8a, usn_p-3d, usn_mh-60r, usn_sh-60b/f, jp_sh-60j, usn_sh-3j, usn_qh_50e — are not in the current order of battle. Note the mission's usn_mh-60r_26 (10 aboard the CVN) carries usn_mk54_1_air, a different and uncontested file, so it is unaffected.


**Recommendation** — Keep 3629144864 on top. It is the only version whose material path is verified present, and it is the one carrying the modern selectable-speed torpedo model. If you want RSA's longer 8 nm standoff, take it as a targeted SEST edit of MaxLaunchRange (and optionally SpeedSettingRanges) rather than by promoting 3413868677 from line 139 to above line 18 — that move would put Red Storm Arsenal above 120 mods and is far too blunt for one torpedo.


*Sampled: All three versions read in full and diffed pairwise. Verified 3629144864/assets/europack/materials/usn_mk46/ exists and contains usn_mk54_mat.ini. Grepped every aircraft and vessel consuming usn_mk54_air and cross-checked against the mission order of battle.*


### ammunition/pla_cj-10.ini (1 file)

**Mods** 3733719765 PLA Land Unit Pack > 3594891803 PLAN Submarines  

**Winner** 3733719765 (PLA Land Unit Pack) · **Risk** low


Winner (PLA Land Unit Pack): header comment still reads '# TLAM' (copy-paste leftover), Mass=2500, AmmoPoints=5700, CIWSDefenceBonus=5, MissileDefenceBonus=0.05, RCS=Small, Power=77, InitialFlightPhaseDuration=2.0, TerminalApproachDist=2, TerminalAlt=300 and TerminalDiveDistance=0.5 both live, MaxVelocity=520 kn, LaunchTurnRate=50, MinLaunchRange=30.0, MaxLaunchRange=1351.3 nm, CircularErrorRadiusInstallation=12, and a dedicated model (ResourcesFolder=assets/ammunition/, ResourcesRoot=CJ-10.obj, ResourcesMesh=cj-10, ResourcesMaterial=cj-10_mat.ini, with launch/canister meshes and a 1.9 s switch time). Loser (PLAN Submarines): header '#CJ-10 Long Sword', NO Mass, NO AmmoPoints, no CIWS/missile-defence bonuses, RCS=VerySmall, Power=64, InitialFlightPhaseDuration=3.0, TerminalApproachDist=0.5, terminal altitude and dive distance commented out and misspelled ('#TeminalAlt=200', '#TeminalDiveDistance=0.5'), a block of commented-out SeaSkimming keys, MaxVelocity=550 kn, MinLaunchRange=20.0, MaxLaunchRange=1216.0 nm, CircularErrorRadiusInstallation=15, and it borrows the vanilla Tomahawk model wholesale (ResourcesFolder=weapons/usn_rgm-109/, mesh usn_rgm-109, dummy launch/canister meshes) plus a [Debris] block.


**Silently lost** — From PLAN Submarines: the higher 550 kn cruise speed, the tighter 20 nm minimum launch range, the RCS=VerySmall signature, the [Debris] block, and the vanilla-Tomahawk model fallback. Nothing of value — the losing file has no Mass and no AmmoPoints, so under it the CJ-10 would weigh nothing for aircraft carriage and cost nothing to replenish.


**Risk** — No id collision, no split ownership. The losing copy is effectively orphaned inside its own mod: 3594891803's only references to pla_cj-10 outside its language files live under 'PLAN mod test/vessels/plan_ddg_type_052D.ini' and 'PLAN mod test/vessels/plan_ddg_type_055.ini' — a nested folder, not one of the engine's loaded category directories — so PLAN Submarines' top-level vessels/ never uses the weapon it defines. Live consumers are 3733719765/land_units/pla_cj-10_tel.ini and pla_cj-100_tel.ini (the winner's own units) and 3413868677/vessels/plan_ddg_type_055_rsa.ini and plan_ddg_type_055_late_rsa.ini. Side effect worth knowing: RSA's Type 055s now fire a 1351 nm CJ-10 with RCS=Small rather than a 1216 nm one with RCS=VerySmall — slightly longer-legged and slightly easier to shoot down. Mesh presence behind assets/ammunition/CJ-10.obj could not be verified (this checkout ships no binary assets).


**Mission** — None. The mission's Chinese surface combatants are plan_type_055_2026 ×3, plan_type_052d_p4 ×2, plan_type_052d_p3 ×2, plan_type_054a_p5 and plan_type_051b_2017 — all from 3775128499, and plan_type_055_2026.ini's land-attack loadout references yj-18, not pla_cj-10. No CJ-10 TELs and no RSA Type 055 variants are fielded.


**Recommendation** — Leave the order as it is. The PLA Land Unit Pack's version is strictly better formed — it is the only one with a mass, a supply cost and its own model — and it belongs to the mod that actually fields the launcher. No change needed.


*Sampled: Both versions read and diffed in full. Enumerated 3594891803's top-level directory layout, grepped every file referencing pla_cj-10 across the collection, and checked mods-source/3775128499/vessels/plan_type_055_2026.ini (the mission's Type 055) for its land-…*


### ammunition/dts_aim-120c.ini, dts_aim-120c_w.ini, dts_aim-9m.ini, dts_gbu-39.ini, dts_gbu-39_quad.ini (5)

**Mods** 3760871384 Dingtools Weapon Pack (order line 16) > 3553116604 F-15E StrikeEagle (79)  

**Winner** 3760871384 Dingtools Weapon Pack — wins all five. · **Risk** low


Sampled: full normalised diffs of all five file pairs, plus both dts_gbu-39_quad.ini in full and the winner's dts_aim-120c_w.ini in full. dts_aim-120c.ini: winner MaxVelocity 2915.8 kt / MaxTurnRate 40 deg-s / MaxLaunchRange 40 nm / MaxFlightTime 80 s (hard battery limit, absent in loser) / KillProbability 0.5 / CircularErrorRadius 106 m / SeekerActiveRange 9.5 nm / MidCourseCorrection=3 / Mass 153 kg, and adds AmmoPoints=700 and AirLaunched=True. Loser: 2640 kt / 20 deg-s / 43 nm / no flight-time cap / KillProbability 0.87 / no CEP entry / SeekerActiveRange 22 nm / MidCourseCorrection=0 / Mass 157 kg. Net: Dingtools models the AMRAAM as faster and more agile but far less certain to kill and with a much shorter terminal seeker; the F-15E's own copy is the optimistic one. dts_aim-120c_w.ini (the internal-carriage variant): the winner's file is 4 lines — [General] with the engine directive '#!alias ammunition/dts_aim-120c.ini' plus a [Guidance] DropDuration=0.01 override (weapons-bay ejection). It is not a stub; it inherits the full winning AIM-120C. The loser ships a 161-line standalone duplicate. The alias idiom is used 146 times across this collection, so it is well-supported. dts_aim-9m.ini: winner 1450 kt / MaxTurnRate 24 / MaxTurnG 40 / MaxLaunchRange 10 nm / KillProbability 0.9 / MaxFlightTime 60 s / adds InterceptSpeedPenaltyMultiplier and the Typical* kinematics block. Loser 1433.7 kt / MaxTurnRate 30 / 9.8 nm / KillProbability 0.85. Effectively the same missile, retuned. dts_gbu-39.ini: the only difference is five lines — winner Power=12, Penetration=Moderate, GuidanceType=0, MidCourseCorrection=3, CircularErrorRadius=0; loser Power=35, Penetration=Heavy, GuidanceType=1, MidCourseCorrection=0. GuidanceType=1 is IR homing in this engine (it is the value on vanilla usn_aim-9m, usn_aim-9l, fr_r550, pla_pl-2/pl-5) — so the F-15E mod's copy models a GPS/INS glide bomb as a heat-seeker. The winner's GuidanceType=0 + MidCourseCorrection=3 + CEP 0 is the correct SDB model. dts_gbu-39_quad.ini: both are Type=Container, Ammunition=dts_gbu-39, 4 attachments, SalvoFireAmount=1. Differences are the four AttachmentPosition offsets (winner ±0.0015/-0.00132 vs loser ±0.002/-0.0018) and the mesh: winner assets/models/weapon/ammunition/py/dts_bru-61.obj with dts_bru-61_mat.ini; loser assets/models/weapon/ammunition/gbu-39/bru-61.obj with a material borrowed from assets\models\vechicle\aircraft\F-15E\f-15_mat.ini.


**Silently lost** — Only the F-15E mod's own, more forgiving ballistics — a 22 nm AMRAAM seeker instead of 9.5, KillProbability 0.87 instead of 0.5, no 80-second flight-time cap, and a Power 35 / Heavy-penetration SDB instead of Power 12 / Moderate. Nothing unique in capability terms is lost: every id survives under the winner's definition. The loser's bespoke BRU-61 mesh and its F-15E-textured material are also discarded in favour of Dingtools' own rack model.


**Risk** — No id collisions, no split ownership (aircraft/usaf_f-15e_SE.ini is shipped only by 3553116604, so its unit file and these weapon files stay coherent — the ids match). No dangling references: usaf_f-15e_SE's full store list resolves, with usn_aim-7m, usn_aim-9l, usn_gbu-10, usn_gbu-12, usn_lau-3a, usn_mk-82, usn_mk-84, usn_rockeye coming from vanilla. One cosmetic risk I cannot close from this repo: the winner's dts_gbu-39_quad points at assets/models/weapon/ammunition/py/dts_bru-61.obj, which is a binary asset stripped from this .ini-only export. It is Dingtools' own path in Dingtools' own file, so it almost certainly ships, but a quick visual check of an SDB-loaded F-15E would confirm the rack renders. The attachment offsets also shift the four SDBs slightly on the rack — purely visual. The language merge is clean: 3553116604 supplies the English names for all five ids and 3760871384 only the Chinese, so no key fights.


**Mission** — No. The sole consumer of all five files is mods-source/3553116604/aircraft/usaf_f-15e_SE.ini (dts_gbu-39 itself has no direct consumer — it is reached only as the submunition of dts_gbu-39_quad). usaf_f-15e_SE does not appear in the mission. The mission DOES field usaf_f-15ex_SEII, but that unit (won by SEST_Integration) arms dts_aim-120d-3, dts_aim-260, dts_gbu-53_quad, dts_agm-158b-2, dts_agm-1…


**Recommendation** — Leave the order as it is — this is the correct outcome and the catalog note ('its other 8 shipped files are deliberately outranked by the Dingtools Weapon Pack') is borne out. Dingtools winning is not merely tidier, it repairs a real bug: the F-15E mod's dts_gbu-39 has GuidanceType=1 (IR homing) on a GPS/INS glide bomb, which would make the SDB behave like a Sidewinder against ground targets. Keeping one canonical dts_* definition per weapon id also avoids the F-15E flying an AIM-120C with different lethality from every other jet firing the same missile. No change.


*Sampled: All five contested pairs, normalised (comments and blank lines stripped) and diffed: mods-source/3760871384/ammunition/{dts_aim-120c,dts_aim-120c_w,dts_aim-9m,dts_gbu-39,dts_gbu-39_quad}.ini against the same five under mods-source/3553116604/. dts_gbu-39_quad…*


### ammunition/usaf_aim-120d.ini (1)

**Mods** 3758320372 F-16C Fighting Falcon (modern) (order line 80) > 3508978375 [DEPRECATED] Lockheed Martin F-35C Lightning II (82)  

**Winner** 3758320372 F-16C Fighting Falcon (modern) · **Risk** low


Same missile id, two distinctly different weapons. Winner (3758320372): MaxLaunchRange 95 nm, MaxVelocity 1800 kt, MaxTurnRate 35 deg/s, MaxFlightTime 160 s, MinLaunchRange 0.5 nm, MaxAttackVelocity 2000 kt, CircularErrorRadius 1.5 m (0.8 vs large aircraft), SeekerGain 65 dB, SeekerFOV 15 deg with a separate SeekerGimbalFOV 45, SeekerActiveRange 20 nm, PeakPower 45 kW, AntiCountermeasuresBonus 0.88, AntiJammerBonus 0.85, Acceleration 15.0 G with a 4.5 s sustainer at 5.0 G, VelocityBleed 0.45, FuzeProximityDistance 15 m, MidCourseCorrection=1, SelfDestructAfterTargetGone=True. Loser (3508978375): MaxLaunchRange 80 nm, MaxVelocity 1600 kt, MaxTurnRate 30 (plus MaxTurnG 35), MaxFlightTime 130 s, MinLaunchRange 0.8, MaxAttackVelocity 1600, CircularErrorRadius 4.5 m (3.72 large), SeekerGain 62, SeekerFOV 60 with no gimbal entry, SeekerActiveRange 20, PeakPower 30 kW, AntiCM 0.8, AntiJammer 0.75, Acceleration 10.4 G with 3.75 s sustainer at 10.4 G, VelocityBleed 0.5, MidCourseCorrection=3, adds KillProbability=0.5 and SelfDestructDelay=5.0. It also has a duplicated FuzeProximityDistance (20.0 in [WarheadData], then 10 again in [Guidance]) — sloppy authoring. Model: identical folder (assets/models/weapon/ammunition/aim-120/) and material (usaf_aim-120d_mat.ini), but the winner's ResourcesRoot is usaf_aim-120.obj where the loser's is usaf_aim-120c.obj.


**Silently lost** — Only the deprecated F-35C mod's weaker tuning: the 80 nm / Mach 2.7 profile with 4.5 m CEP, 0.75 anti-jam and an explicit KillProbability=0.5 cap. Nothing unique disappears — no capability, station or reference is lost, and the id keeps a full definition. Worth noting the loser's MidCourseCorrection=3 (two-way datalink) is arguably a better guidance model than the winner's MidCourseCorrection=1 (radio command); that single key is the one place the losing version is more modern.


**Risk** — No id collision. No split ownership on the winner's side — the F-16 family's aircraft files and this ammunition file come from the same mod (or, for usaf_f-16cm-bl52d, from SEST_Integration above it, which is deliberate). No dangling references introduced. The live risk sits with the loser rather than the winner: 3508978375 is marked deprecated and an unsubscribe candidate, but the catalog warns that 'F-35C Alt. Loadouts was written against THIS mod'. Removing it is safe as far as this cohort is concerned — its usaf_aim-120d is already dead, and its usn_f-35c.ini is already overridden by SEST_Integration (with 3607989779 and 3737267013 also ahead of it) — but that removal decision needs to be made against the Alt. Loadouts dependency, not against this file. Unverifiable in this repo: the winner's ResourcesRoot=usaf_aim-120.obj. Binary assets are stripped from this export, so I cannot confirm that mesh ships; it is the winner's own file pointing into the winner's own folder, so it very probably does, and both mods write *_mat.ini into the same textures directory.


**Mission** — No. The mission fields no F-16 and no F-35C. But the outcome is not academic: SEST_Integration's usaf_f-16cm-bl52d.ini — the built pack's F-16CM, which outranks 3758320372's own copy — references usaf_aim-120d in 54 places, so this file sets the primary BVR missile for the project's F-16CM whenever a scenario fields it. The loser's only consumer, mods-source/3508978375/aircraft/usn_f-35c.ini, is …


**Recommendation** — Leave the order as it is. For a 2026-era Indo-Pacific theatre the winner is clearly the right AIM-120D: 95 nm rather than 80, Mach ~3 rather than 2.7, a 1.5 m CEP, 45 kW seeker with a modelled 15-degree seeker FOV on a 45-degree gimbal, and materially better countermeasure and jamming resistance (0.88/0.85 vs 0.80/0.75) — which is what the missile needs to stay relevant against PL-15-armed opposition. Promoting the deprecated F-35C mod would be a straight downgrade on a missile it no longer even uses. One optional refinement if you want the best of both: copy MidCourseCorrection=3 from the loser into the winner's file, since two-way datalink midcourse is correct for the D-model and the winner's MidCourseCorrection=1 is the single respect in which it is behind. That is a one-line edit, not a reorder.


*Sampled: Both files in full, normalised and diffed side by side: mods-source/3758320372/ammunition/usaf_aim-120d.ini (172 lines) and mods-source/3508978375/ammunition/usaf_aim-120d.ini (173 lines), including the complete [Guidance] and [Models] blocks. Also grepped ev…*


### ammunition/usn_mk50_air.ini, usn_ssq-53d.ini, usn_ssq-53f.ini, usn_ssq-62c.ini, usn_ssq-62e.ini (5 files)

**Mods** 3629144864 Euromod - Main Pack (load-order line 18) > 3737267013 United States Naval Aviation (line 59)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** low


The two versions share a common ancestor - each file differs by only 3-5 lines. Sonobuoys: Euromod sets LifeTime=28800 s (8 h) on all four buoys and TransmitterRange=60 nm on all four; USNNA differentiates them - SSQ-53D LifeTime=7200/TransmitterRange=30, SSQ-53F 14400/40, SSQ-62C 3600/30, SSQ-62E 3600/40. Euromod sets RCS=VeryTiny and LaunchReliability=99 on the 53D/53F (USNNA: RCS=VerySmall, 97); the 62C/62E differ only in header, LifeTime and TransmitterRange. Euromod also dates the buoys in the header comment (SSQ-53D DIFAR (1992), 53F (2002), 62C (1997), 62E (2004)) and ships fuller encyclopedia text in language_en/ammunition_names.ini; USNNA's copies carry a 'REQUIRES STATS REVISION' banner. Acoustic performance in the ammo files themselves is identical (same Sonar= key, SonarDepth=100). usn_mk50_air differs in exactly 3 values: ResourcesMaterialFolder=assets/europack/materials/usn_mk46/ (Euromod) vs assets/models/ammunition/mk46/ (USNNA); ResourcesMeshForLaunch is COMMENTED OUT in Euromod (it left '#ResourcesMeshForLaunch=it_a-244s_dummy' behind, showing the file was cloned from its A-244S) vs ResourcesMeshForLaunch=usn_mk46_dummy in USNNA; and SonarAudioClip=audio/environment/Sonar-MF vs Sonar-Mk50.wav. All torpedo kinematics, warhead and seeker values are identical.


**Silently lost** — From USNNA: the differentiated buoy endurance/datalink ranges (the realistic 1 h DICASS / 2 h 53D distinction), and usn_mk50_air's ResourcesMeshForLaunch=usn_mk46_dummy - the winner ships no launch-dummy mesh at all, so a Mk 50 released from a pylon has no pre-switch model. Nothing else is lost; the losing file has no content the winner lacks.


**Risk** — No id collision - every contest is a same-filename whole-file override of an id no other enabled mod defines under a different filename. No dangling refs: Euromod's assets/europack/materials/usn_mk46/usn_mk50_mat.ini exists in its own folder, and the Sonar= sensor keys resolve. One cross-file interaction worth knowing: systems/ merges key-by-key, and Euromod also outranks USNNA in systems/sensors.ini, so [SSQ-53F_Sonar] resolves to Euromod's values (AngularResolution=50.0, RangeResolution=750, PassiveRange=15 km, SignalProcessing=3) rather than USNNA's (10.0 / 1000 / 18 km / 4) - i.e. coarser bearing but the ammo file and the sensor it points at stay from the same author, which is the coherent outcome. The mk50 SonarAudioClip change appears to be neutralised anyway: 3784474738 (Euromod Anchorchain Expansion, line 10) ships systems/TorpedoAudioClip_Mapping.ini with [usn_mk50_air] SonarAudioClip=audio/environment/Sonar-Mk50.wav. That file is not a vanilla systems file (vanilla ships only cargo/modules/sensors/weapons/wip_cargo.ini), so whether the engine consumes it is unverified.


**Mission** — Partially fielded. NORTHERN FRONT III FINAL NEWEST fields one usn_p8 (mods-source/3602046770/aircraft/usn_p8.ini), whose ASW stations are Station5=usn_ssq-53f and Station6=usn_ssq-62e - both contested here, so the winner's 8-hour / 60 nm buoys are what that aircraft actually drops. The two usn_p8_2027 and the ten usn_mh-60r_26 use usn_ssq-53h / usn_ssq-62g, which are not contested. usn_mk50_air i…


**Recommendation** — Leave the order alone. Euromod Main is a shared framework that must stay above its eight addons, and the only thing USNNA's copies do better is buoy realism on one fielded aircraft - not worth destabilising the framework block. If you want the realism, patch it in place rather than reordering: set LifeTime back to 14400 (53F) and 3600 (62E) and TransmitterRange to 40 in a SEST pack, and restore ResourcesMeshForLaunch=usn_mk46_dummy to usn_mk50_air. Cost of reordering instead: moving USNNA above Euromod Main would put a fixed-wing pack above the European weapons/sensors database that five enabled Euromod addons declare as a dependency.


*Sampled: All 5 files read in both mods (full diff of each). Also read mods-source/3629144864/systems/sensors.ini [SSQ-53F_Sonar] vs 3737267013 equivalent, both language_en/ammunition_names.ini, mods-source/3784474738/systems/TorpedoAudioClip_Mapping.ini, and consumers…*


### ammunition/plan_hhq-7.ini, plan_yj-83.ini, plan_yu-6.ini, plan_yu-7_air.ini, plan_yu-7_ship.ini (5 files)

**Mods** 3775128499 Modern PLAN Systems (order line 19) > 3417801942 Chinese Navy (PLAN) (order line 50)  

**Winner** 3775128499 Modern PLAN Systems · **Risk** low


The two mods are written against DIFFERENT GAME SCHEMAS, and that is the decisive difference. Every 3417801942 file uses CounterMeasuresRejection=/NoiseRejection= — keys that appear in ZERO of the 415 vanilla ammunition files (mods-source/_vanilla/original/ammunition/). Every 3775128499 file uses the current AntiCountermeasuresBonus=/AntiJammerBonus= (169 of 415 vanilla files), plus ApplyKinematics (84 vanilla files), SpeedSettings/SpeedSettingRanges and GuidanceType=10 (26 vanilla files). Concretely: plan_hhq-7 — loser: MaxVelocity=2300 kt, MaxLaunchRange=10.0 nm, Acceleration=20.0, MaxTurnRate=30, FuzeProximityDistance=8.0 yd, KillProbability=0.55, Power=19, Penetration=Always, MidCourseCorrection=0, no kinematics. Winner: HQ-7B, MaxVelocity=1800 kt with full kinematics (AccelerationTime=2.5 s @ 29.8 G, DragCoefficient=3.18, MaxFlightTime=60 s, TypicalTargetAlt=19685 ft), MaxLaunchRange=8.1 nm, MinLaunchRange 0.36 vs 0.8, MaxTurnRate=35/MaxTurnG=35, FuzeProximityDistance=18.0 m, KillProbability=0.85, Power=17, Penetration=Moderate, ImpactSize VerySmall vs Small, MidCourseCorrection=3, plus InterceptSpeedPenaltyMultiplier=0.85 / InterceptOutOfAltitudePenalty=0.30 / InterceptSizePenaltyMultiplier=0.20, Transient signature block, Mass=84.5 and AmmoPoints=750. plan_yj-83 — loser: Mass=540, Power=45, MaxVelocity=540 kt, MaxLaunchRange=120.0 nm, SeaSkimmingAlt=20 ft, TerminalApproachDist=8.0, terminal pop-up (1 nm/1000 ft/70 deg), Frequency=Ku-Band, CounterMeasuresRejection=80/NoiseRejection=65, mesh = vanilla Harpoon (weapons/usn_agm-84/usn_agm-84). Winner: Mass=850, AmmoPoints=1675, Power=39, MaxVelocity=640 kt, MaxLaunchRange=85 nm, MinLaunchRange 6 vs 3.5, SeaSkimmingAlt=8 ft, MaxLoftAngle=20/MaxLoftAlt=80 ft, TerminalApproachDist=5.4, no pop-up, SupportsBanking=True, Frequency=X-Band, SeekerPassiveRange=20.0 (loser 0), AntiCountermeasuresBonus=0.5/AntiJammerBonus=0.2, RCS=0.25 numeric + Transient block, dedicated yj_83 model + plan_yj-8_booster effect, Large explosion classes vs Medium. plan_yu-6 — loser: Mk-48 clone, Power=68, single MaxVelocity=50 kt, MaxLaunchRange=20 nm, MaxDepth=2624 ft, seeker 1.5 nm/gain 30/power 235, CounterMeasuresRejection=75, mesh usn_mk48 with 1 propeller. Winner: 'Mk-48 mod 5', Power=74, TerminalVelocity=50, SpeedSettings=36,50 kt with SpeedSettingRanges=27,16.2 nm, four new wire keys (WireControlsDepth=True, WireCountermeasureBonus=0.35, WireBreakSpeed=20 kt, WireMinSeafloorClearance=50 ft), MaxDepth=2200 ft, MaxTurnRate 15 vs 10, seeker 2.0 nm/gain 40/power 240, AntiCountermeasuresBonus=0.23, SearchVelocity 50 vs 40, snake 45 deg/5 s vs 30 deg/6 s, dedicated yu-6 model with 2 counter-rotating propellers. plan_yu-7_ship — winner adds SecondaryTargetType=ASuW, GuidanceType=10 (vs 7), TerminalVelocity=45, SpeedSettings=35,43 kt / ranges 7.6,5.0 nm (loser: flat MaxVelocity=45, MaxLaunchRange=8), MaxDepth 1112.34 vs 1450 ft, seeker 0.9 nm active AND passive with gain 28 (loser 1.0 active only, gain 10), AntiCountermeasuresBonus=0.20, FractionOfRangeToActivateSeeker=0.8, dedicated yu-7 mesh vs usn_mk46 reskin. plan_yu-7_air — same seeker/ECCM rework, MaxDepth 1250 vs 1450 ft, ResourcesMeshSwitchTime=0.4 and InFlightEffectStartTime=0.4 added. Display names also change via the merged language_en/ammunition_names.ini (winner's keys win): 'CH-SA-4' -> 'HHQ-7', 'CSS-N-8 Saccade' -> 'YJ-83', 'YU-6' -> 'Yu-6', 'YU-7' -> 'Yu-7', with much longer PLAN-authored encyclopedia text.


**Silently lost** — Everything in 3417801942's five files: the 120 nm YJ-83 (35 nm more reach than the winner's 85 nm), the 10.0 nm / 2300 kt HHQ-7, the YJ-83 terminal pop-up profile (TerminalPopUpDist=1 nm / 1000 ft / 70 deg) which the winner has no equivalent for, the deeper torpedo envelopes (Yu-6 2624 ft, Yu-7 1450 ft), the Ku-band YJ-83 seeker, and the vanilla-mesh fallbacks (usn_agm-84 / usn_mk48 / usn_mk46) that need no add-on art. Nothing unique-and-needed is lost: no id, no station, no launcher block exists only in the loser's copies.


**Risk** — No id collision — both mods define the same five ids in identically-named files, which is a clean override, not a duplicate registration. No dangling references: every winner material .ini it names exists (assets/models/ammunition/yj_83_mat.ini, .../yu-6/yu-6_mat.ini, .../plan_yu-7_ship_mat.ini, weapons/plan_yu-7_ship/plan_yu-7_ship_mat.ini). Cross-mod side effect worth knowing: 3417801942's OWN units now fire the winner's rounds — plan_ddg_luda_typ_051/051d/051dt (plan_yu-7_ship, plan_hhq-7), plan_ss_kilo (plan_yu-6), plan_j-15a (plan_yj-83), plan_z-18f (plan_yu-7_air) all lose the stats their author balanced them around; the J-15A in particular drops from a 120 nm to an 85 nm YJ-83. Only caveat I could not verify: this repo mirrors .ini files only (no .obj/.png), so the winner's mesh files (yj_83.obj, yu-6.obj, yu-7.obj) are not sampled — if the Workshop download is missing them the affected weapons render wrong, whereas the loser's vanilla-mesh copies could not.


**Mission** — None direct. The mission (NORTHERN FRONT III FINAL NEWEST) fields plan_type_055_2026, plan_type_052d_p3/p4, plan_type_054a_p5, plan_type_051b_2017 — all owned by 3775128499 — and their magazines call plan_yj-83a, plan_hq-16/16c, plan_hhq-9b/9c, plan_hq-10a, plan_yu-7c_ship, plan_yu-12_ship, plan_yu-8, plan_yj-17/18a/18c/20, NOT any of the five contested ids. The mission's submarines (plan_ssn_typ…


**Recommendation** — Keep 3775128499 above 3417801942. The winner is the only version written against the current ammunition schema — the loser's CounterMeasuresRejection/NoiseRejection keys are dead in every one of the 415 vanilla files, so those five weapons would be silently running with no countermeasure or jam resistance model at all if 3417801942 won. Do not reorder. Optional follow-up: if you want the loser's 120 nm YJ-83 reach for the Luda/J-15A, raise the winner's MaxLaunchRange in a SEST pack rather than moving the mod.


*Sampled: All 5 files diffed in full, both versions. Also read both mods' language_en/ammunition_names.ini entries for these ids, verified winner's referenced material .ini assets exist, and resolved every live consumer of each id across the 133-mod merged set.*


### ammunition/usn_aim_120d.ini, ammunition/usn_aim_9x.ini (2 files)

**Mods** 3430135740 F/A-18 Murder Hornet with AIM-174B (order line 22) > 3413868677 Red Storm Arsenal (order line 139, last)  

**Winner** 3430135740 F/A-18 Murder Hornet with AIM-174B · **Risk** low


usn_aim_120d — loser (Red Storm, labelled AIM-120D-3): ApplyKinematics=True with a full modern flight model (AccelerationTime=4 s @ 10.4 G boost, SustainerAccelerationTime=3.75 s @ 10.4 G, DragCoefficient=-1, MaxFlightTime=130 s, MaxTurnG=35, VelocityBleed=0.5), MaxVelocity=1600 kt, MaxLaunchRange=80 nm, MaxLoftAngle=15/MaxLoftAlt=50000, TerminalApproachDist=19, LocalTerminalOnly=True, MaxAttackVelocity=1600, CircularErrorRadius=4.5 m (3.72 vs Large), SeekerGain=62, SeekerFOV=60, PeakPower=30 kW, AntiCountermeasuresBonus=0.8 / AntiJammerBonus=0.75, AmmoPoints=320, AirLaunched=True, DecalClass=SAMImpacts, dedicated mesh usn_aim-120d from usn_aim-120.obj, and a sustainer particle effect. Winner (Murder Hornet, labelled AIM-120D, '# Users: usn_f-14e'): NO ApplyKinematics — legacy flight model, MaxVelocity=2667 kt, MaxLaunchRange=97 nm, MaxLoftAngle=45/MaxLoftAlt=60000, AccelerationTime=7, Acceleration=11.0, MaxTurnRate=40, VelocityBleed=0.25, IgnoreHeightDifferenceForTargetDist=True, TerminalApproachDist=12, LocalTerminalOnly=False, MidCourseCorrection=1 (Radio Command) vs the loser's 3, MaxAttackAltitude=82000, CircularErrorRadius=1.25 m (2.5 vs Large), SeekerGain=50, SeekerFOV=120, PeakPower=6 kW, SeekerPassiveRange=16 with SecondaryPassiveRadarGuidanceType=HomeOnJam and PassiveRadarGuidanceFrequencies=All (the loser has no home-on-jam at all), AntiCountermeasuresBonus=0.5 / AntiJammerBonus=0.6, KillProbability=1.05, no AmmoPoints, no AirLaunched, and it borrows the vanilla Sparrow body (ResourcesRoot=usn_aim-7 / ResourcesMesh=usn_aim-7) with a 120C-7 material. usn_aim_9x — loser: Mass=84, Power=9, Penetration=Minor, KillProbability=0.90, MaxVelocity=1800 kt, AccelerationTime=5 s @ 14.0 G, MaxLaunchRange=13.5 nm, MaxTurnRate=40 plus LaunchTurnRate=80, CircularErrorRadius=0.15 m, SeekerFOV=0.1 / SeekerGimbalFOV=270, AntiCountermeasuresBonus=0.47 / AntiJammerBonus=0.0, MinAttackAltitude=1 / MaxAttackAltitude=85000 / MinLaunchAltitude=0 / MaxLaunchAltitude=80000, AmmoPoints=126, AirLaunched=True. Winner ('# Cropgun AIM-9X'): Mass=90, Power=10, Penetration=Always, KillProbability=0.98, MaxVelocity=1740 kt, Acceleration=18.0 with AccelerationTime=120 (effectively disables velocity bleed for the whole flight), MaxLaunchRange=15 nm, MaxTurnRate=150 deg/s (nearly 4x the loser), SeekerFOV=300 / SeekerGimbalFOV=80 (the FOV/gimbal values are swapped in character between the two files), AntiCountermeasuresBonus=0.90 / AntiJammerBonus=0.85, LaunchReliability=99 vs 95, no CircularErrorRadius, no altitude bounds, no AmmoPoints, no AirLaunched. Mesh and material are identical in both (usn_aim-9l body, usn_aim-9x_mat.ini).


**Silently lost** — Red Storm's kinematic AIM-120D-3 — the only version of these two weapons that models drag, a sustainer burn and a 130 s battery life — plus its stronger ECCM on the AMRAAM (0.8/0.75 vs the winner's 0.5/0.6), its dedicated AIM-120D mesh instead of a Sparrow body, its CircularErrorRadius on the AIM-9X, its launch/attack altitude envelopes on the AIM-9X, and — on both files — the AmmoPoints and AirLaunched=True lines. Losing AmmoPoints (320 and 126) means these two rounds carry no supply-system price; losing AirLaunched=True means the encyclopedia stops showing launch altitudes for them.


**Risk** — No id collision — same ids, same filenames, clean override. No dangling refs: both versions point at meshes and materials that exist. The real finding is that this cohort is nearly inert: the winner's files are consumed only by the loser's own aircraft, so Murder Hornet's numbers are being applied to Red Storm airframes and to nothing else. Two data-quality flags on the winner worth recording: KillProbability=1.05 on usn_aim_120d is outside the documented 0..1 range, and AccelerationTime=120 on usn_aim_9x is almost certainly a stand-in for 'never bleed' rather than a real 120-second burn. Adjacent (not caused here): usn_aim-9x — the dash-form id — is shipped by seven enabled mods (3426791311, 3430135740, 3508978375, 3514484654, 3606774881, 3737267013, 3758320372) and is the one the mission's Ford air wing actually fires; that contest is a separate cohort from this one.


**Mission** — None. After the merge these two ids are consumed by exactly ten aircraft, all of them Red Storm Arsenal's own: usaf_f_15c_2040c, usaf_f_47, usmc_av_8b_plus, usn_ea-6b_late, usn_ea_6b_96, usn_f-14e, usn_f_35c, usn_fa_18e_rsa, usn_fa_18f_rsa, usn_fa_xx. Murder Hornet's own usn_fa-18e / usn_fa-18f / usn_fa-18f_blk3 / usn_ea-18g all LOSE their airframe files to 3606774881 (U.S. Navy 2027, line 17), a…


**Recommendation** — Leave the order alone. Red Storm Arsenal is deliberately parked last so it sheds exactly this class of file, and the winner delivers the longer-reaching AMRAAM (97 nm / 2667 kt vs 80 nm / 1600 kt) and a far more agile AIM-9X that suit a 2026 Indo-Pacific fight. Two caveats to accept knowingly: you are trading Red Storm's kinematic AMRAAM model for a legacy one, and both winning files drop AmmoPoints, so these rounds are free in the supply system. If either matters, the surgical fix is a small SEST pack re-adding AmmoPoints=320 / AmmoPoints=126 and AirLaunched=True on top of the winner — not a reorder, which would hand Red Storm eleven other files it is being kept away from.


*Sampled: Both files diffed in full, both versions (172 vs 176 lines, 165 vs 159 lines). Also resolved the winner of every aircraft file that references either id, to establish who actually consumes them after the merge.*


### 2 files: ammunition/usn_an_slq_25a_nixie_decoy.ini, ammunition/usn_mk54_ship.ini

**Mods** 3629144864 Euromod - Main Pack (line 11) > 3413868677 Red Storm Arsenal (line 132)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** low


usn_an_slq_25a_nixie_decoy.ini: 130 lines each, only THREE values differ. Winner BaseNoise=205 dB / TargetReflectionStrength=55 / SpoofChance=0.80; loser BaseNoise=210 / TargetReflectionStrength=50 / SpoofChance=0.95. The winner's Nixie is a quieter, more visible-to-active-sonar and substantially less effective decoy (0.80 vs 0.95 base spoof chance). Structure, colliders, models (weapons/usn_slq-25/) and effects are identical. usn_mk54_ship.ini: winner models the Mk 54 on the modern speed-setting scheme - MaxVelocity=45 kn kept only 'for compatibility with SpeedSettings', SpeedSettings=35,45 with SpeedSettingRanges=5.5,4.9 nm, MaxLaunchRange=4.9 nm, TerminalVelocity=45, SearchVelocity=35, ResourcesMaterialFolder=assets/europack/materials/usn_mk46/, ResourcesMeshForLaunch=usn_mk46_dummy. Loser is the older flat model - MaxVelocity=55 kn, MaxLaunchRange=12 nm, no speed settings, no terminal velocity, SearchVelocity=36, ResourcesMaterial=usn_mk54_mat.ini, ResourcesMeshForLaunch=usn_mk46. Display names also differ (winner 'MK 54', loser 'MK-54') but those live in language files, which merge.


**Silently lost** — Red Storm Arsenal's markedly stronger Nixie (SpoofChance 0.95, i.e. a torpedo is spoofed ~19 times in 20 rather than 4 in 5) and its long-legged 55 kn / 12 nm Mk 54. RSA authored its entire Burke/Ticonderoga/Hobart/DDG(X) line (usn_ddg_arleigh_burke_flight1/2/2a/3 in eight year-variants, usn_cg_kansas_late, usn_ddg_ddgx, ran_ddg_hobart_alt_late) around those numbers, and those ships now fire a torpedo with 40% of the launch range RSA intended and tow a decoy 15 points weaker.


**Risk** — No id collisions and no split ownership - both are plain ammunition overrides, and the two mods share only three override files in total (usn_an_slq_25a_nixie_decoy.ini, usn_mk54_ship.ini, and usn_mk54_air.ini which belongs to an adjacent cohort). No dangling references: the winner's ResourcesMaterialFolder=assets/europack/materials/usn_mk46/ is inside Euromod's own assets/europack tree, and both files keep the same weapons/usn_mk46 and weapons/usn_slq-25 resource roots. The winner's usn_mk54_ship is consumed by mods that never saw it - 3695809489's jmsdf_ddg_maya and jmsdf_dd_asahi as well as RSA's whole destroyer line - so the range change propagates well beyond Euromod's own ships. Note the winner's file also omits the 'REQUIRES STATS REVISION' banner the loser carries, i.e. Euromod treats these as finished stats.


**Mission** — Partially. usn_mk54_ship IS fielded: the mission's usn_cg_ticonderoga_vls_2027 (Taskforce 1, from mod 3606774881) carries usn_mk54_ship, so its ASW torpedo tubes get Euromod's 4.9 nm / 45 kn weapon rather than RSA's 12 nm / 55 kn. usn_an_slq_25a is NOT fielded - the mission's Ticonderoga tows usn_an_slq_25e_nixie_decoy (a Euromod-exclusive, uncontested id) and the mission's Burkes (usn_ddg_arleig…


**Recommendation** — Keep Euromod on top. Its Mk 54 (35/45 kn selectable, 4.9-5.5 nm) is much closer to the real weapon than RSA's 55 kn / 12 nm figure, and its 0.80 Nixie spoof chance is the more defensible number for a 2026 scenario where wake-homing and modern seekers are meant to be a threat. Do not move Red Storm Arsenal: it sits at line 132 and ships 651 override files, only 14 of which are currently shadowed - promoting it above Euromod to win these two files would reshuffle its relationship with roughly 120 other mods. If the longer Mk 54 reach is wanted for RSA's Burkes specifically, patch it in a SEST pack instead.


*Sampled: Both files diffed in full (whitespace-normalised, since the two mods use different line endings) on both sides, plus both mods' language_en/ammunition_names.ini entries and a reference sweep for which vessels consume the two ids.*


### 1 file: ammunition/usa_apkws_2_m282.ini

**Mods** 3459682829 A-10C (line 56) > 3425450153 AH-64 Apache (line 57)  

**Winner** 3459682829 A-10C · **Risk** low


These two are effectively the same file. Every performance value is identical: Type=Missile, TargetType=ASuW, Mass=5, WarheadType=2, Power=8, ImpactSize=Small, GuidanceType=5, MaxVelocity=768.6 kn, Acceleration=140, MaxTurnRate=30.0, MinLaunchRange=0.16, MaxLaunchRange=3.5, MinLaunchAltitude=200, LaunchReliability=97, CircularErrorRadius=1.0, SeekerFOV=70.0, SeekerPassiveRange=2.7, AntiCountermeasuresBonus=0.05, and identical model paths (weapons/usn_hydra70/, usn_hydra_inflight, modular_parts). The language entries are word-for-word identical too. The only differences are: the loser has AmmoPoints=6, the winner has no AmmoPoints line at all; the winner adds MaxLaunchAltitude=6000 ft, which the loser does not set (unlimited); the loser has TerminalDiveDistance=1000, the winner does not; the loser's HitGroundExplosionClass=RocketShipHitExplosion vs the winner's SmallGroundHitExplosions; and a cosmetic case difference, Penetration=moderate (winner, lowercase) vs Penetration=Moderate (loser).


**Silently lost** — Three small things: the supply-system price (AmmoPoints=6, so the rocket is now free or engine-default in the supply model), TerminalDiveDistance=1000, and the beefier RocketShipHitExplosion ground-impact effect. In exchange the winner imposes a 6000 ft launch ceiling that the Apache's version did not have.


**Risk** — No id collision. There IS split ownership in this pair, but it is not caused by this file and it appears benign: 3425450153 loses ALL FIVE of its aircraft unit files - usa_ah-64a.ini, usa_ah-64d.ini, usa_ah-64e.ini, uk_ah_mk_1.ini and usn_ah-64na.ini - to SEST_Integration at line 1, while KEEPING all five matching *_squadrons.ini files (they are unshadowed). So every Apache in the game flies a SEST-owned airframe with an Apache-mod-owned squadron/livery table. I checked the one the mission uses: usa_ah-64e_squadrons.ini declares NumberOfSquadrons=9 with Squadron1-9 present, and the mission indexes Squadron2 (ResourcesLiveryFolder=assets/tex/, LiveryTexture=ah64_south_korea.png, Nation=South_Korea) and Default - both exist, so no dangling squadron reference. Worth a glance that the mission is putting a South-Korea-liveried Apache flight into an Australian-theatre task force; that is a mission-authoring choice, not a mod conflict. No dangling ammunition references: the winner's APKWS is consumed by 3459682829/ammunition/usn_agr-20b.ini and 3425450153/ammunition/usn_agr-20b_apache.ini, and both of those pod files survive (neither is shadowed), and the SEST airframes reference usn_agr-20b (9x on the A-10C) and usn_agr-20b_apache (6x on the AH-64E) respectively.


**Mission** — Yes, but mildly. The mission fields usa_a-10c (Type= at lines 1736 and 1747, plus 'usa_a-10c=Squadron1,4|Squadron2,4' and 'usa_a-10c=Squadron1,6|Squadron2,6') and usa_ah-64e ('usa_ah-64e=Squadron2,8' and 'usa_ah-64e=Default,8'), and both reach usa_apkws_2_m282 through their AGR-20B pods. The winner's new MaxLaunchAltitude=6000 ft is harmless for the Apache, which operates well below that, and for…


**Recommendation** — No action. The two versions are functionally the same weapon and the mods sit adjacent in the load order (lines 56 and 57), so the choice is arbitrary and the current winner is fine. If you want to be tidy, hand-merge the loser's AmmoPoints=6 into the winner so the rocket carries a supply cost - that is the only loss with any mechanical meaning. Do not reorder for this: 3459682829 and 3425450153 contest exactly one file, so a swap would gain AmmoPoints and lose the 6000 ft ceiling and nothing else.


*Sampled: Both versions diffed in full (158 vs 159 lines; the diff is six hunks). Also read: both mods' language_en/ammunition_names.ini entries, the consumers 3459682829/ammunition/usn_agr-20b.ini and 3425450153/ammunition/usn_agr-20b_apache.ini reference lines, the S…*


### ammunition/b-2_jassm.ini, b-2_jsow.ini, b-2_jsow_clus.ini, b-2_jsow_sead.ini, b-2_lrasm.ini (5 files, all contested)

**Mods** 3607989779 F-35C Lightning II Alt. Loadouts (order line 21, WINS) > 3480965706 B-2 Spirit (line 67)  

**Winner** 3607989779 (F-35C Lightning II Alt. Loadouts) · **Risk** low


These are not accidental copies — both mods genuinely fire these ids, so the whole collection gets the F-35C author's rebalance. b-2_jassm: Power 90 -> 77, MaxLaunchRange 1000 -> 450 nm, Mass 1430 -> 1020 kg, GuidanceType 0 (INS only) -> 1 (IR homing) with MidCourseCorrection 0 -> 1, RCS Tiny -> 0.00001 and IRSignature VerySmall -> 0.00001, TransientBaseNoise 130 -> 10 dB, ECM=LRASM_ECM added, sea-skim/terminal profile enabled (SeaSkimmingAlt=20 ft, TerminalAlt 80 -> 20 ft), AntiCountermeasuresBonus/AntiJammerBonus 0.90/0.90. b-2_lrasm: Power 64 -> 77, MaxLaunchRange 500 -> 225 nm, GuidanceType 3 (Active Radar, SeekerActiveRange 20 nm, Frequency=Ku-Band, SecondaryPassiveRadarGuidanceType=Full home-on-jam) -> 1 (IR, SeekerPassiveRange 25 nm, no radar seeker, no HOJ), SeekerFOV 15 -> 90, salvo grouping (GroupSize=2, GroupSpacing 0.05, GroupLeaderAlt/GroupWingmanAlt 20) commented out. b-2_jsow: Power 32 -> 25, Mass 600 -> 468, MaxVelocity 1000 -> 530 kt, MinLaunchAltitude 80 -> 10000 ft, MaxLaunchAltitude 60000 -> 55000 ft, GravityFactor=4 dropped for an ApplyKinematics=False glide model, KillProbability=10 added. b-2_jsow_clus: Power 32 -> 38.2, Penetration Moderate -> Heavy, Mass 450 -> 474, and it loses BombletsEjectAltitude=300 plus FuzeType=1 and all four ClusterGroundHitExplosions effect classes. b-2_jsow_sead: WarheadType 4 (cluster, Power 60) -> 0 (HE, Power 25) — GuidanceType stays 4 (anti-radiation) in both, but SeekerGain=10/SeekerFOV=60 are replaced by CircularErrorRadius=2.0. MaxLaunchRange stays 70 nm on all three JSOWs.


**Silently lost** — From the B-2 mod: the 1000 nm JASSM-XR-style land-attack shot, the LRASM's active Ku-band radar seeker and home-on-jam fallback, its two-missile salvo grouping, the SEAD JSOW's cluster warhead (Power 60 vs 25), and the cluster JSOW's submunition mechanics (BombletsEjectAltitude, FuzeType=1, ClusterGroundHitExplosions). Nothing is lost on the display side: language_en/ammunition_names.ini merges key-by-key, and only the B-2 mod defines names for b-2_jassm/jsow/jsow_clus/jsow_sead/lrasm, so its encyclopedia text survives — which is itself the problem (it still advertises 'range exceeds 500 km' LRASM and 'over 1800km' JASSM against the winner's 225/450 nm files). b-2_lrasm_ER.ini and b-2_jsow_ecm.ini are uncontested and unaffected.


**Risk** — No id collision — the two mods ship the same five ids, which is a whole-file override, not a double registration. Split ownership is real but benign in direction: the B-2 airframe file is owned by 3480965706 while all five of its standoff weapons are owned by 3607989779; station names, rack tokens (5x2_Rack_fl, CSRL) and ammo ids all still resolve, and ECM=LRASM_ECM referenced by the winning files is defined in 3480965706/systems/sensors.ini (systems merge, so it loads regardless). Two genuine defects survive the merge: (1) the B-2's cluster JSOW loses its bomblet-eject and cluster-explosion keys, so it now detonates as a plain WarheadType=4 with no eject altitude — the B-2 author's own comment already flagged this behaviour as unreliable; (2) the B-2's encyclopedia entries now overstate JASSM and LRASM range by roughly 2x.


**Mission** — Live on both sides of the override. NORTHERN FRONT III FINAL NEWEST fields usn_f-35c as squadrons (line 135: Squadron1,24|Squadron11,10) and usaf_b-2_spirit twice (lines 2412, 2470: 6 and 4 airframes). The fielded F-35C unit file is integration/dist/SEST_Integration/aircraft/usn_f-35c.ini, which carries these exact ids (b-2_jsow x8, b-2_jsow_clus x8, b-2_jassm x4, b-2_lrasm x4, b-2_jsow_sead x2),…


**Recommendation** — Keep the order. The winner is the mod the fielded F-35C's loadouts were authored against, and its stealthier, sea-skimming LRASM/JASSM is the better fit for pushing a strike through PLAN Type 055 air defence. If you want the B-2's SEAD and cluster punch back, hand-merge three lines into mods-source/3607989779/ammunition/b-2_jsow_clus.ini (BombletsEjectAltitude=300, FuzeType=1, the four HitXExplosionClass=ClusterGroundHitExplosions lines) and reconsider Power=25 on b-2_jsow_sead — do not reorder, since putting the B-2 mod above 3607989779 would strip the F-35C's own 34 fielded airframes of the loadout balance they were built for.


*Sampled: Read b-2_jassm.ini and b-2_lrasm.ini in full from both mods; comment-stripped diffs plus key extraction on b-2_jsow.ini, b-2_jsow_clus.ini, b-2_jsow_sead.ini. Also read mods-source/3480965706/aircraft/usaf_b-2_spirit.ini loadout stations, mods-source/36079897…*


### ammunition/dts_agm-158b-2.ini, dts_agm-158c-3.ini, dts_agm-183a.ini, dts_agm-183a(w62).ini (4 files)

**Mods** 3760871384 Dingtools Weapon Pack (line 16, WINS) > 3652097318 B-1B Lancer (66) > 3741944366 B-52H Stratofortress (68) > 3636386513 F-15 EX Eagle II (78)  

**Winner** 3760871384 (Dingtools Weapon Pack) — except for both AGM-183A files, where the project's own SEST_Integration outranks … · **Risk** low


Two of the four are non-events. dts_agm-183a(w62).ini is byte-identical in all four mods (md5 ac83e099). dts_agm-183a.ini is byte-identical in Dingtools, B-1B and B-52H (md5 4b2239b4); only the F-15EX copy differs — it replaces the flat Acceleration=6.0 with a staged burn (AccelerationTime=5 at 9.4 G, SustainerAccelerationTime=25 at 5.4 G), lengthens InitialFlightPhaseDuration 20 -> 36 s and ResourcesMeshSwitchTime 15 -> 35 s, and swaps the turbojet in-flight effect for a SustainerEffect. dts_agm-158b-2.ini (JASSM-ER land attack) is identical in Dingtools, B-52H and F-15EX; the B-1B copy differs in flight profile only — the winner terrain-follows and lofts (TerrainFollowFlight=True, MaxLoftAlt=6000, TerminalAlt=6000, TerminalDiveDistance=4), the B-1B copy cruises 'sea-skimming' at 8000 ft with SeaSkimmingStartDistToTarget=1000 and TerminalDiveDistance=10, and carries a stray BombletsEjectAltitude=300 on a WarheadType=0 weapon. dts_agm-158c-3.ini (LRASM-ER) is the only file where all four differ: winner Power=58, MaxLaunchRange=800 nm, MaxLoftAlt=15000, SeekerFOV=25; B-1B Power=45, 565 nm, no loft key; B-52H Power=45, 800 nm; F-15EX Power=45, 565 nm, SeekerFOV=30 plus GroupSize=16 salvo grouping. Mass 1023, IRSignature/RCS VeryTiny, GuidanceType=1, SeekerPassiveRange 15 nm and the shared agm-158 model are the same in all four.


**Silently lost** — Only three things, all small: the B-1B's low-cruise JASSM-ER profile, the F-15EX's staged-burn ARRW kinematics (moot — SEST wins that file anyway), and the F-15EX's GroupSize=16 LRASM-ER salvo grouping, which would have made 16-round shots fly as a formation. Nothing else is unique to a loser. Language entries merge, and the dts_agm-158c-3 / dts_agm-183a encyclopedia text survives from whichever pack defines it.


**Risk** — No id collisions — same-id, same-file overrides across four mods that all bundle the upstream weapon pack's ammunition as a dependency. Worth recording that both AGM-183A files are settled above this cohort: integration/dist/SEST_Integration/ammunition/dts_agm-183a.ini and dts_agm-183a(w62).ini sit at the top of the load order and add MaxLoftAlt=90000, MaxLoftAngle=45, TerminalVelocity=3800 and IgnoreHeightDifferenceForTargetDist=True, so the workshop contest over those two files never reaches the game at all. The only genuine consideration is that the winner's LRASM-ER is a real capability jump for the B-1B and F-15EX (800 nm vs 565 nm, Power 58 vs 45) — intended by the weapon-pack author, but stronger than what those airframe mods were balanced around.


**Mission** — Fields all of it. usaf_b-1b_dts (lines 1535, 1546, plus Squadron2,6 and Squadron2,4) references dts_agm-158b-2 x14 and dts_agm-158c-3 x14; usaf_f-15ex_SEII (4 Type= entries plus squadrons) and dts_b-52h (Squadron1,8 twice) and usaf_b-52o (4 Type= entries) all reference dts_agm-158b-2 and dts_agm-158c-3 through their SEST-owned unit files. So the fielded bomber force fires the Dingtools 800 nm / P…


**Recommendation** — Keep the order. Dingtools is the upstream owner of the dts_ namespace and every other mod ships its files as a vendored copy; letting an airframe mod win one of them would be the anomaly. No change would gain anything: the only unique loser content is the F-15EX's GroupSize=16, and adding that one line to mods-source/3760871384/ammunition/dts_agm-158c-3.ini is cheaper than any reorder.


*Sampled: md5 comparison of all four files across all four mods; comment-stripped diffs of dts_agm-158b-2.ini (Dingtools vs B-1B) and dts_agm-183a.ini (Dingtools vs F-15EX); key extraction of dts_agm-158c-3.ini from all four; plus integration/dist/SEST_Integration/ammu…*


### ammunition/usn_mk48_7.ini, ammunition/usn_ugm-84d.ini (2 files)

**Mods** 3629144864 Euromod - Main Pack (line 18, WINS) > 3433957933 Virginia-, Seawolf-, and Ohio-class (line 60)  

**Winner** 3629144864 (Euromod - Main Pack) · **Risk** low


usn_mk48_7: the winner is a materially richer file. It adds VesselAttackGuidanceType=8 (passive-sonar homing against surface targets), a full selectable-speed model — SpeedSettings=28,40,55,65 kt with SpeedSettingRanges=27.0,21.0,15.0,9.0 nm — and a wire model (WireControlsDepth=True, WireCountermeasureBonus=0.50, WireBreakSpeed=20 kt, WireMinSeafloorClearance=50 ft), raises MaxVelocity 55 -> 65 kt, lowers TerminalVelocity 68 -> 65, and activates the seeker earlier (FractionOfRangeToActivateSeeker 0.8 -> 0.5). Warhead (Power=72, ImpactSize Large), Mass 1565, AmmoPoints 4695, GuidanceType=10, MidCourseCorrection=2, 27 nm range and the shared weapons/usn_mk48/ model are identical. Those keys are all engine-valid — vanilla usn_mk48.ini uses SpeedSettings and WireBreakSpeed. usn_ugm-84d is a different shape of difference: the winner is a 20-line overlay opening with '#!alias ammunition/usn_rgm-84d.ini' and setting only TransientBaseNoise=180, MinDepth=50 and the usn_ugm-84 model/usn_ugm-84c_mat; the loser is a 187-line standalone with explicit Power=45, MaxLaunchRange=120 nm, GuidanceType=3, SeekerActiveRange=20 nm, Frequency=Ku-Band, AntiCountermeasuresBonus=0.25 / AntiJammerBonus=0.15, SupplyCategory=Harpoon, Mass=690, MinDepth=50. The alias resolves against usn_rgm-84d.ini, which in this collection is itself overridden by 3456859157 (line 45): Power=32, 120 nm, SeekerPassiveRange=20, AntiJammerBonus=0.1 — vanilla's is Power=45, 80 nm, MaxTurnRate 15.


**Silently lost** — From the sub mod: nothing on the Mk 48 (its file is a strict subset of the winner's, minus TerminalVelocity=68). On the Harpoon, the loser's explicitly-tuned sub-launched round is replaced by an inherited one — effective warhead drops from Power 45 to Power 32 and AntiJammerBonus from 0.15 to 0.1 if the alias resolves through 3456859157, and the loser's SeekerPassiveRange=0 becomes 20. Display name is fine: language files merge and the Euromod's higher-priority 'UGM-84D, Harpoon Blk IC' entry wins over the sub mod's 'UGM-84D, Harpoon'.


**Risk** — No id collision, no split ownership — 3433957933 keeps all its own vessel files; only these two ammunition ids move. The one thing worth knowing is the hidden coupling the alias introduces: the fired UGM-84D's warhead, seeker and ECCM now come from whichever mod wins ammunition/usn_rgm-84d.ini (today 3456859157, order line 45), so disabling or reordering that unrelated mod silently changes every submarine Harpoon in the collection. The alias itself is sound and widely used — 146 files across mods-source use #!alias — and the alias target exists both in vanilla and as an enabled override, so there is no dangling reference.


**Mission** — None directly. The only submarine NORTHERN FRONT III FINAL NEWEST fields is usn_ssgn_virginia_blk5_vpm, owned by 3390330875 (not either contestant); it arms usn_mk48_8 in its tubes and usn_ugm-109e5/e5a/e5b in the VPM, and never references usn_mk48_7 or usn_ugm-84d. None of 3433957933's boats (usn_ssn_virginia, usn_ssn_seawolf, usn_ssgn_ohio, usn_ssbn_ohio) appear in the mission.


**Recommendation** — Keep the order. The Euromod Mk 48 mod 7 is strictly better — the loser's copy gives the player no speed selection and no wire-break/wire-depth behaviour at all, which on a 2026 submarine mission is the difference between a modelled torpedo and a fire-and-forget one. If you ever want the Harpoon pinned rather than inherited, copy the four stat lines from mods-source/3433957933/ammunition/usn_ugm-84d.ini into the Euromod overlay; do not reorder, since promoting 3433957933 above line 18 would also take the Mk 48's speed and wire model away.


*Sampled: Both files read/diffed in full from both mods; plus mods-source/_vanilla/original/ammunition/usn_rgm-84d.ini (the alias target's vanilla form), mods-source/3456859157/ammunition/usn_rgm-84d.ini (the enabled override of that target), and mods-source/_vanilla/o…*


### ammunition/usaf_aim-120c.ini (1 file)

**Mods** 3430135740 F/A-18 Murder Hornet with AIM-174B (line 22, WINS) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (line 35)  

**Winner** 3430135740 (F/A-18 Murder Hornet with AIM-174B) · **Risk** low


Two different modelling philosophies. The winner uses the legacy flat-performance model: MaxVelocity=2666 kt, Acceleration=18.0, VelocityBleed 0.6, MaxTurnRate=40, MaxLaunchRange=65 nm, MidCourseCorrection=1, MaxLoftAngle=50, and is far more lethal — CircularErrorRadius 5 m (2.5 m vs large aircraft), SeekerFOV 120 degrees, SeekerActiveRange and SeekerPassiveRange both 23 nm, SeekerGain 46, AntiCountermeasuresBonus 0.85 / AntiJammerBonus 0.70, KillProbability 0.95, LaunchReliability 99, FuzeProximityDistance=10 yd. The loser uses the current engine kinematics: ApplyKinematics=True with a staged motor (AccelerationTime 4 s at 10.4 G, SustainerAccelerationTime 3.75 s at 10.4 G), DragCoefficient=-1, MaxTurnG=35, MaxFlightTime=80 s, TypicalTargetAlt/TypicalTargetSpeed/TypicalFiringAlt/TypicalLaunchVelocity envelope anchors, MaxVelocity 1600 kt, MaxLaunchRange 60 nm, MaxAttackVelocity=1600, and much more modest lethality — CEP 106 m (18.72 m vs large), SeekerFOV 60, seeker ranges 15 nm, ECCM 0.5/0.5, KillProbability 0.85, reliability 97. The loser also carries AmmoPoints=1520, AirLaunched=True, a sustainer particle effect, and its own aim-120c-specific model/material (usaf_aim-120c.obj / usaf_aim-120c_mat.ini) where the winner points at the generic usaf_aim-120.obj / usaf_aim-120_mat.ini.


**Silently lost** — The loser's entire modern kinematics description of the AMRAAM — staged boost/sustain, drag, flight-time limit, G-limit and range-envelope anchors — plus AmmoPoints=1520 (the winner sets none, so this round has no supply cost), the AirLaunched=True encyclopedia flag, the sustainer effect, and the C-specific model and material.


**Risk** — No id collision — a straight same-id override, and the loser is explicitly marked [DEPRECATED] by its own author, so it losing is the intended outcome. Two things to note rather than fix: the winner's stat block is markedly more lethal than the engine's current modelling would produce (a 5 m CEP, 23 nm two-way seeker and 0.85/0.70 ECCM on an AIM-120C is closer to a D-model with cheat stats), and it drops AmmoPoints so the round is free to replenish. Both only reach the game through usn_ea-18g_2020s, which nothing currently spawns. The winner also references usaf_aim-120.obj / usaf_aim-120_mat.ini rather than the C-specific pair; asset presence could not be verified because this export contains no binaries.


**Mission** — Effectively none today, and this is the finding worth reporting. The exact id usaf_aim-120c is referenced by only six unit files in the whole collection, all six of them inside the deprecated mod 3426791311 (usn_fa-18e, usn_fa-18e_late, usn_fa-18f, usn_fa-18f_blk3, usn_ea-18g, usn_ea-18g_2020s). Five of those six lose their own filenames to 3606774881 (line 17) or 3430135740 (line 22), and none o…


**Recommendation** — Keep the order — never promote a mod its own author deprecated. If you ever field usn_ea-18g_2020s, expect its four AMRAAM stations to be considerably deadlier than the same aircraft's other missiles; the cheapest correction would be editing mods-source/3430135740/ammunition/usaf_aim-120c.ini (add AmmoPoints=1520, pull CircularErrorRadius back toward the loser's values) rather than reordering, which would also revert the Murder Hornet's own AIM-174B work.


*Sampled: Both usaf_aim-120c.ini files diffed in full (comment-stripped). Also enumerated every unit file in the collection that references the exact id, and checked which of those files win their own filename, including integration/dist/SEST_Integration/aircraft/usn_e…*


### ammunition/usaf_litening.ini (1 file)

**Mods** 3459682829 A-10C (line 63, WINS) > 3758320372 F-16C Fighting Falcon (modern) (line 80)  

**Winner** 3459682829 (A-10C) · **Risk** low


The functional half of the file is identical in both: Type=Container, Mass=208 kg, NumberOfSensorSystems=2, [SensorSystem1] Type=LaserDesignator SystemName=AN/AAQ-28 Mount=Dummy, [SensorSystem2] Type=Visual SystemName=Litening. The only difference in the sensor block is a comment ('#AN/AVQ-23' on the winner's section header). Everything that actually differs is the 3D representation: the winner points at assets/models/weapon/ammunition/litening/ with litening.obj and textures/usaf_litening_mat.ini; the loser points at assets/models/weapon/ammunition/aaq-28/ with aaq-28.obj and aaq-28_mat.ini, and adds a [Submodels] block of two entries (Glas and Glas_Gold, using aircraft/materials/cockpit_glass and cockpit_glass_gold) that gives the pod its gold-tinted optical window.


**Silently lost** — Only the AAQ-28 Sniper-style pod model and its two glass submodels. No sensor, range, designation or mass capability is lost — the pods are mechanically the same object.


**Risk** — No id collision, no split ownership, no stat divergence. Both referenced sensor systems resolve: [Litening] and [AN/AAQ-28] are defined in 3459682829/systems/sensors.ini (and again in 3426791311 and 3505420313 — systems files merge key-by-key, so they load regardless of which ammunition file wins). The winner's model directory exists in its own mod (assets/models/weapon/ammunition/litening/textures/usaf_litening_mat.ini is present). The only consequence is visual: whenever the Israeli F-16C Barak II is spawned it will hang the A-10's LITENING pod model instead of its intended AAQ-28, without the gold-glass submodels. Actual mesh presence could not be confirmed — this export strips all .obj and texture binaries.


**Mission** — Live but cosmetic. usa_a-10c is fielded (Type= at lines 1736 and 1747, plus Squadron1,4|Squadron2,4 and Squadron1,6|Squadron2,6), and its winning unit file — integration/dist/SEST_Integration/aircraft/usa_a-10c.ini — references usaf_litening ten times across its loadouts (Station4=usaf_litening|Litening). The A-10 therefore gets the model from its own mod, which is the correct pairing. The other …


**Recommendation** — Keep the order. The fielded aircraft is the A-10, and it should carry its own mod's pod model; moving 3758320372 above line 63 would swap the model on four-to-twelve fielded A-10s to gain nothing but a nicer pod on an unfielded Israeli F-16. If both models matter to you, the clean fix is for the F-16C mod to use a distinct id (e.g. usaf_aaq-28) rather than a reorder.


*Sampled: Both files diffed in full (comment-stripped) and the winner's sensor block read directly; asset directories of both mods enumerated; systems/sensors.ini checked for the referenced system names; all consumers of the id located.*


### ammunition/usn_haawc_p8.ini (1 file)

**Mods** 3606774881 U.S. Navy 2027 Capabilities mod (line 17, WINS) > 3602046770 Boeing P-8 Poseidon (line 61)  

**Winner** 3606774881 (U.S. Navy 2027 Capabilities mod) · **Risk** low


The winner models HAAWC as what it is — a glide kit on a Mk 54. Header comment '# Mk54 HAAWC Mod 0', Mass=276 kg, AirLaunched=True, and an explicitly unpowered profile: Lofted=False, SeaSkimming=False, FinalFlightPhase=False, ApplyKinematics=False, Acceleration=0 with no booster or sustainer burn, MaxVelocity=530 kt, VelocityBleed 0.75, TerminalApproachDist and TerminalDiveDistance both 50.35 nm, MinLaunchRange 1.0, MaxLaunchRange 40 nm, TypicalFiringAlt=35000. The loser still carries the copy-paste header '# RUM-139 VL-ASROC' and flies like a rocket: Mass=487 kg, no AirLaunched flag, MaxLoftAngle=85 to MaxLoftAlt=3000 ft at MaxLoftVelocity=750, then SeaSkimmingAlt=50 (SeaSkimmingSubAlt=3000) from 10.3 nm, FinalFlightPhaseAlt=3000 at 3.1 nm, TerminalDiveDistance=3, AccelerationTime=4 at 11 G, LaunchTurnRate=135, MaxVelocity=750 kt, MinLaunchRange 2.50, MaxLaunchRange 18 nm. Everything downstream of the glide is identical in both: [Submunition] Ammunition=usn_mk54_asroc with SpawnTime=6, the three launcher position blocks (MK10/MK26/MK13), MinLaunchAltitude=10000 / MaxLaunchAltitude=40000, CircularErrorRadius=0.0, SelfDestructDelay=6.0, and the weapons/haawc/ model.


**Silently lost** — The loser's lofted-and-sea-skimming delivery profile and its 750 kt dash, plus its heavier 487 kg mass. Its encyclopedia entry is not lost — language_en/ammunition_names.ini merges key-by-key and only 3602046770 defines a name for usn_haawc_p8, so the P-8 mod's description still appears (and now describes an 18 nm weapon that flies 40 nm).


**Risk** — No id collision, no split ownership. The submunition reference resolves — usn_mk54_asroc is defined by 3629144864 (Euromod Main Pack), which is enabled at line 18 — and both files point at the same weapons/haawc/ model, so nothing dangles. The only mismatch left is descriptive: the surviving encyclopedia text comes from the mod whose stats lost. Note also that a 40 nm HAAWC is a real capability shift for the mission's ASW picture — it more than doubles the standoff from which the P-8s can prosecute a submarine contact.


**Mission** — Directly live for both P-8 fleets. NORTHERN FRONT III FINAL NEWEST fields usn_p8_2027 (Type= at lines 1390 and 1401, plus usn_p8_2027=Squadron1,8) and usn_p8 (line 1638). Both airframes load five stations of usn_haawc_p8 in their ASW loadouts, so every torpedo shot either P-8 takes uses the winner's 40 nm glide.


**Recommendation** — Keep the order. 40 nm from 35,000 ft is the realistic HAAWC envelope and is what a 2026 Indo-Pacific mission needs: it lets the P-8s drop Mk 54s from outside the engagement rings of the Type 055s and HQ-9 sites the mission fields, whereas the loser's 18 nm profile would force them inside. The winner is also the cleaner file (correct Mk54 header, AirLaunched flag set); the only thing worth touching is the stale 18 nm wording in 3602046770/language_en/ammunition_names.ini.


*Sampled: Both files diffed in full (comment-stripped), both headers and both [Submunition]/[Launchers] sections read directly, and the loadout stations of both usn_p8_2027.ini and usn_p8.ini checked.*


### ammunition/dts_aim-120d-3.ini, dts_aim-120d-3_w.ini, dts_aim-260.ini, dts_aim-260_w.ini, dts_aim-9x.ini (5). Note: the …

**Mods** 3760871384 Dingtools Weapon Pack (load-order line 16) > 3636386513 F-15 EX Eagle II (line 78)  

**Winner** 3760871384 Dingtools Weapon Pack · **Risk** low


Dingtools is a straight newer revision of the same missiles. dts_aim-120d-3: MaxLaunchRange 82 nm vs 65, MaxVelocity 3300 kt vs 2915.8, MidCourseCorrection=3 (two-way datalink) vs 1, TargetMemory=True present vs absent, MaxFlightTime 130 s vs 80, AntiCountermeasuresBonus 0.77 vs 0.66, AntiJammerBonus 0.55 vs 0.62, seeker active/passive 14 nm vs 18, AmmoPoints 920 vs 1800, DragCoefficient=-1 (auto-solve) vs 1.405. dts_aim-260 (JATM): MaxVelocity 3507 vs 3307, MCC=3 vs 1, warhead Power 20 vs 15, KillProbability 0.92/0.55 vs 0.85/0.5, ACM 0.85 vs 0.8, AJ 0.75 vs 0.8, SeekerGain 60 vs 90 dB, PeakPower 30 vs 12 kW, Mass 170 vs 154 kg, AmmoPoints 1340 vs none, and a proper two-stage sustainer (SustainerAccelerationTime=9 / SustainerAcceleration=11.5) vs a commented-out sustainer; both are 125 nm MaxLaunchRange. dts_aim-9x: MaxLaunchRange 13.5 vs 12 nm, MaxTurnG=60 and full Typical-target/firing kinematics block present vs absent, AmmoPoints=350 and AirLaunched=True present vs absent, MaxFlightTime 60 vs 90 s, ACM 0.6 vs 0.8. The two _w files are the real structural difference: Dingtools ships them as 4-line '#!alias ammunition/dts_aim-120d-3.ini' / '#!alias ammunition/dts_aim-260.ini' stubs with a DropDuration override, where F-15EX shipped ~150-line full duplicates. #!alias is engine-supported (also used by mods-source/3731208477 across ~10 files). Display names in language_en/ammunition_names.ini are byte-identical in both mods.


**Silently lost** — Only the F-15EX mod's older tuning: AIM-120D seeker 18 nm (winner gives 14), AIM-120D AntiJammerBonus 0.62 (winner 0.55), AIM-260 AntiJammerBonus 0.8 (winner 0.75), AIM-9X AntiCountermeasuresBonus 0.8 (winner 0.6) and 90 s flight time (winner 60 s), and the AmmoPoints=1800 supply price on the AMRAAM. The lost full-text _w definitions are functionally replaced by the alias stubs — no content loss there. Nothing unique to the loser (no extra ids, no extra sections).


**Risk** — No id collision (all five are same-filename overrides, one loads). No dangling references: the alias targets exist in the winner, and the winner ships the aim-120/aim-9 material folders the files point at. Consistent with the author's own placement instruction recorded in the catalog ('Put this mod ABOVE any of my mod'), and F-15 EX Eagle II is one of that author's mods. Only residual risk is the mild AIM-9X anti-countermeasures downgrade (0.8 -> 0.6) against flare-dropping PLA fighters — a balance nudge, not a defect.


**Mission** — Yes, directly. NORTHERN FRONT III FINAL NEWEST fields 4x usaf_f-15ex_SEII. Its loadouts (both the workshop file and the SEST_F-15EX_Revamp override that actually wins the aircraft file) reference dts_aim-120d-3_w on Stations 1/2/5/6/7, dts_aim-260_w (59 references) and dts_aim-9x (61) — so every F-15EX shot in the mission uses the Dingtools numbers. SEST_Integration ships no dts_aim-* override, s…


**Recommendation** — Leave as is. Order line 16 > 78 already satisfies the author's instruction. If you want the F-15EX's better AIM-9X ECCM number, edit AntiCountermeasuresBonus in mods-source/3760871384/ammunition/dts_aim-9x.ini or add a SEST override — do not reorder, since demoting Dingtools would lose the AIM-120D two-way datalink and the AIM-260 sustainer stage.


*Sampled: All 5 contested files diffed in full (both copies). Also read: both mods' language_en/ammunition_names.ini entries for these ids; mods-source/3636386513/aircraft/usaf_f-15ex_SEII.ini and integration/f-15ex-revamp/SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII.i…*


### aircraft/wp_mig-29a.ini, aircraft/wp_mig-29a_squadrons.ini, ammunition/wp_tank_1500_mig-29.ini (3)

**Mods** 3417446309 MIG-29 Family (load-order line 41) > 3416372890 Apex Predators MIG-29A & F-16A (line 99)  

**Winner** 3417446309 MIG-29 Family · **Risk** low


Near-identical files. wp_mig-29a_squadrons.ini and wp_tank_1500_mig-29.ini are byte-identical (md5 match). wp_mig-29a.ini differs in exactly 5 hunks out of 902 lines, all flight-model/signature, zero loadout changes: RCS=16 (numeric m2) vs RCS=SemiSmall (enum); MaxRollRate 200 deg/s + MaxPitchRate=28 vs MaxRollRate 120 with no pitch-rate key; MaxG=7 vs 9.5; SpeedAndRange_Cruise=0.9,890 vs 0.9,1135.14 (nm of cruise range); gun FiringArcs/ElevationArc -3,3 vs -1,1. Both point at the same model (assets/models/aircraft/mig-29a/mig-29a.obj, mig-29a_mat.ini) and both ship that folder. Loadouts are identical in both: wp_aa-10a, wp_aa-11, wp_aa-8, wp_b8m-1, wp_fab-250, wp_fab-500, wp_tank_1500_mig-29. Language merge: the winner supplies Default=MIG-29A_912 and Squadron1-5 including a Squadron4 'Mig-29G (Luftwaffe)' entry the loser omits, so the merged name table is strictly the winner's.


**Silently lost** — Effectively nothing of substance. Apex's copy differs only in the 5 flight-model values listed above (higher MaxG 9.5, longer 1135 nm cruise, tighter gun arcs, enum RCS) and its shorter name table. Its squadrons file and drop-tank file are byte-identical to the winner's, so the override costs nothing there.


**Risk** — No id collision: same filename, one file loads. Two things to note. (1) The winner's loadouts depend on ammunition no enabled copy of the winner defines — wp_aa-10a and wp_aa-11 come only from 3416372890 (the loser, line 99) and 3436170138 Shenyang J-11 (line 106). Both are enabled so nothing dangles today, but unsubscribing Apex without keeping the J-11 mod would leave the winning MiG-29A with two undefined AAMs. wp_aa-8 / wp_b8m-1 / wp_fab-250 / wp_fab-500 are vanilla. (2) Pre-existing defect inherited by whichever copy loads: wp_mig-29a_squadrons.ini declares NumberOfSquadrons=7 but contains only 5 [SquadronN] blocks (and Squadron4 has an empty SerialnumberTextures= list). Identical in both mods, so no reorder can fix it — it needs an edit or a SEST override if it turns out to misbehave. Livery folder assets/textures/mig-29/ referenced by the squadrons file is png-only and therefore invisible in this text-only mods-source export — not verified.


**Mission** — None. wp_mig-29a does not appear in NORTHERN FRONT III FINAL NEWEST (the Russian/red air order of battle there is wp_su-35s, wp_tu-95ms, wp_a-50u, plaaf_*, plan_*). Neither mod's other units are fielded either.


**Recommendation** — Leave as is. The move would gain only Apex's MaxG=9.5 / 1135 nm cruise numbers and cost the winner's MaxPitchRate, wider gun arcs and the Luftwaffe squadron entry — not worth touching a mod pair the mission never fields. Keep Apex Predators enabled regardless of what you do with it as a MiG-29 source, since it is one of only two definers of wp_aa-10a/wp_aa-11.


*Sampled: All 3 contested files diffed in full. Also read both mods' language_en/aircraft_names.ini [wp_mig-29a] blocks, the winner's full station/loadout list, and both mods' ResourcesFolder lines.*


### ammunition/usmc_25mm_gunpod.ini, ammunition/usmc_alq-164.ini, ammunition/usmc_tank_230_av-8b.ini (3)

**Mods** 3505420313 Italian Navy Mod (load-order line 38) > 3737267013 United States Naval Aviation (line 59)  

**Winner** 3505420313 Italian Navy Mod · **Risk** low


All performance data is byte-identical across all three files. The ONLY divergence is asset routing. usmc_25mm_gunpod.ini: ResourcesFolder=assets/models/aircraft/av-8b/ + ResourcesMaterial=av-8b_mat.ini (winner) vs assets/models/aircraft/usmc_av-8b+/ + av-8b_plus_mat.ini (loser). usmc_alq-164.ini: same folder swap, same material name (av-8b_mat.ini) in both. usmc_tank_230_av-8b.ini: same folder swap, same material (av-8b_plus_mat.ini). ResourcesRoot is av-8b_plus.obj and ResourcesMesh (GunPod / ANALQ_164 / fuel_tank) is the same in every version. Both folders exist in the collection: 3505420313 ships assets/models/aircraft/av-8b/ (and a vestigial duplicate under assets/models/vechicle/aircraft/av-8b/), 3737267013 ships assets/models/aircraft/usmc_av-8b+/.


**Silently lost** — Nothing functional — mass, drag, jamming power, station behaviour are identical byte-for-byte. What is lost is USNA's intent that its own AV-8B+ pods be drawn from its own model folder and, for the gun pod, from the '+'-specific material (av-8b_plus_mat.ini rather than av-8b_mat.ini).


**Risk** — Split ownership, benign but real: usmc_av-8b+.ini is owned solely by USNA, while the three pods it hangs (13 gun-pod, 10 ALQ-164 and 10 drop-tank references in that file) are now owned by the Italian Navy Mod and point into the Italian mod's model folder. It coheres — mesh names match and the path exists — so the worst case is the USMC jet's gun pod rendering with the base AV-8B material instead of the AV-8B+ one. The load-bearing consequence is a hidden dependency: if Italian Navy Mod is ever disabled or unsubscribed, USNA's AV-8B+ pods lose their ResourcesFolder entirely. Note the mods-source export is text-only (no .obj/.dds), so I could not verify av-8b_plus.obj itself exists in the Italian folder — only the material .ini files beside it, which strongly implies it does. No id collision (the two AV-8Bs are distinct ids, mm_av-8b_plus vs usmc_av-8b+).


**Mission** — None. Neither usmc_av-8b+ nor mm_av-8b_plus appears in NORTHERN FRONT III FINAL NEWEST.


**Recommendation** — Leave as is; the reorder would buy nothing since the data is identical. Just do not unsubscribe Italian Navy Mod while USNA is enabled without re-checking these three files, and if you ever see an untextured gun pod on the USMC Harrier, the one-line fix is ResourcesMaterial=av-8b_plus_mat.ini in mods-source/3505420313/ammunition/usmc_25mm_gunpod.ini (that material already exists in the winner's folder).


*Sampled: All 3 contested files diffed in full. Also read mods-source/3505420313/aircraft/mm_av-8b_plus.ini and mods-source/3737267013/aircraft/usmc_av-8b+.ini (resource paths and the pods' station references), plus the asset-folder listings of both mods.*


### ammunition/usn_agm-88g.ini (1)

**Mods** 3607989779 F-35C Lightning II Alt. Loadouts (line 21) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (line 35) > 3737267013 United States Naval Aviation (line 59) > 3418252667 F-22 Raptor (line 81)  

**Winner** 3607989779 F-35C Lightning II Alt. Loadouts · **Risk** low


Four genuinely different AARGM-ER tunings. Winner (F-35C Alt Loadouts): Mass 468 kg, MaxLaunchRange 140 nm, MinLaunchRange 5, MaxVelocity 3775 kt, SeekerPassiveRange 70 nm, MaxTurnRate 30 deg/s, MidCourseCorrection=1, WarheadType=6 Power=35, CIWSDefenceBonus=1, SecondaryPassiveRadarGuidanceType=HomeOnJam, SupplyCategory commented out, no MaxFlightTime cap, TerminalApproachDist 25 nm. 3426791311: Mass 910 kg, 175.67 nm but MinLaunchRange 25 nm, 3300 kt, seeker 50 nm, turn 12, MCC=0, WarheadType=6 Power=42, MaxFlightTime 360 s, SupplyCategory=AdvancedARM active. 3737267013 (USNA): Mass 467 kg, 160 nm, 3775-class accel 22, seeker 80 nm (the best seeker of the four), turn 7, MCC=0, WarheadType=0 Power=42, CIWSDefenceBonus=5, TerminalApproachDist 15, MaxFlightTime 360, AdvancedARM. 3418252667 (F-22 Raptor's own): Mass 910 kg, only 75.67 nm, seeker 50 nm, turn 7, MaxFlightTime 100 s. Winner is the only one with HomeOnJam and the only one with a mid-course correction channel. WarheadType=6 is valid (9 vanilla ammunition files use it). Model path: winner, 3426791311 and 3418252667 all point at assets/models/ammunition/agm-88g/AGM-88G.obj; USNA alone points at assets/models/ammunition/agm-88/agm-88g.obj.


**Silently lost** — USNA's 80 nm passive seeker and CIWSDefenceBonus=5 (the winner gives 70 nm and 1); 3426791311's 175.67 nm reach; the AdvancedARM SupplyCategory that three of the four losers set (the winner comments it out, so AARGM-ER no longer needs a special replenishment category — more forgiving, arguably less correct); and every loser's higher warhead Power=42 (winner 35). Also silently lost: the winner ships NO language_en entry for usn_agm-88g, so the player-facing name merges in from the highest remaining definer, 3426791311 at line 35 — which spells it 'AAGRM-ER' (letters transposed). USNA and F-22 Raptor both spell it correctly but are outranked.


**Risk** — No id collision (one filename, one loads). No dangling refs: the winner's model folder assets/models/ammunition/agm-88g/ is shipped by 3426791311, 3413868677 and 3418252667, so it survives even if the deprecated mod is removed. Two real but minor defects. (1) The display name currently comes from a mod the catalog flags as deprecated and an unsubscribe candidate, and it is misspelled 'AAGRM-ER'. (2) The winner roughly doubles the F-22's ARM reach relative to what the F-22's author tuned — realistic for AARGM-ER, but it is a balance change the F-22 author did not sign off on. Adjacent observation, same mod set, outside this cohort: usn_fa-18e/f/f_blk3 and usn_ea-18g are won by 3606774881 while their *_squadrons.ini files are won by 3426791311 — a split worth checking in whichever cohort covers it.


**Mission** — Yes. NORTHERN FRONT III FINAL NEWEST fields 8x usaf_f-22_s6, whose SEAD loadout carries usn_agm-88g on Stations 7 and 8 (that aircraft file has exactly one definer, 3418252667, and no SEST override). Those Raptors therefore shoot the winner's missile — 140 nm instead of the F-22 mod's own 75.67 nm, with a 70 nm seeker instead of 50 and HomeOnJam added — against the mission's pla_sam_site_hq-9_mor…


**Recommendation** — Keep the order. The winner is the right AARGM-ER for a 2026 SEAD fight: correct mass (~468 kg vs the 910 kg two losers use), HomeOnJam against the mission's PLA emitters, and a mid-course channel none of the others have. Two cheap improvements that need no reorder: add 'usn_agm-88g=AGM-88G,AARGM-ER,ARM,...' to mods-source/3607989779/language_en/ammunition_names.ini (or just unsubscribe the deprecated 3426791311, which fixes the spelling by letting USNA's correct entry merge through), and consider lifting SeekerPassiveRange from 70 to USNA's 80 nm if you want the best of both.


*Sampled: All four copies of usn_agm-88g.ini read and pairwise-diffed against the winner. Also read all four mods' language_en/ammunition_names.ini entries for the id, mods-source/3418252667/aircraft/usaf_f-22_s6.ini station lines, the four ResourcesFolder paths and wh…*


### 3 files: ammunition/dts_agm-154a.ini, ammunition/dts_gbu-53.ini, ammunition/dts_gbu-53_quad.ini

**Mods** 3760871384 Dingtools Weapon Pack (pos 16) > 3652097318 B-1B Lancer (pos 66) > 3636386513 F-15 EX Eagle II (pos 78)  

**Winner** 3760871384 (Dingtools Weapon Pack) wins all 3 · **Risk** none


dts_agm-154a.ini is byte-identical in all three mods (md5 b4f4523a, 6074 bytes) - a pure non-conflict. dts_gbu-53.ini: Dingtools has AmmoPoints=320, WarheadType=6 (Fragmentation), Power=15, ImpactSize=Small, Penetration=Moderate, MidCourseCorrection=3, SeekerGain=20. Both losers have AmmoPoints=250, WarheadType=0, Power=35, ImpactSize=Medium, Penetration=Heavy, MidCourseCorrection=1; the B-1B copy additionally has SeekerGain=0 while the F-15EX copy already has SeekerGain=20 (that single line is the only difference between the two losers). Everything else - Mass=90, GuidanceType=1, DropDuration=4, SeekerFOV=0.1, SeekerPassiveRange=100, and the whole [Models] block (AssetBundleMesh=usn_gbu-12 / usn_gbu-12_mat / usn_gbu-12_coll) - is identical in all three, so there is no mesh divergence. dts_gbu-53_quad.ini is a 4-round rack pointing at Ammunition=dts_gbu-53; the two losers are byte-identical to each other and differ from Dingtools only in the four AttachmentPosition values (Dingtools -0.0015,-0.00132,+/-0.0127/0.013 vs losers -0.002,-0.0018,+/-0.016/0.0165) - purely how tightly the four bombs are spaced on the same mesh.


**Silently lost** — Nothing unique. The losers carry no content the winner lacks - same weapon, same model, same guidance; only the harder-hitting warhead numbers (Power 35 HE/Heavy vs 15 Frag/Moderate) and the wider rack spacing are dropped. The Dingtools numbers are the scale-correct ones: a GBU-53/B StormBreaker carries a ~105 lb warhead, and the losers' Power=35/Medium/Heavy would make it hit harder than a vanilla 500 lb Mk82 (Power=28/Medium). MidCourseCorrection=3 is a valid engine value (7 vanilla ammunition files use it), so the winner's datalink midcourse is not a broken setting.


**Risk** — No id collision (the three files are the same ids by design, and same-filename override is the stable path). No split ownership: the winner owns both dts_gbu-53.ini and its dts_gbu-53_quad.ini rack, so the rack's AttachmentPositions are tuned for the same bomb model the winner defines - had the rack been won by a different mod the spacing would have been the mismatched pair. No dangling references: dts_gbu-53_quad's Ammunition=dts_gbu-53 resolves to the winner's own file, and the [Models] block uses vanilla asset-bundle names. Only cosmetic note: AmmoPoints rises 250 -> 320 per bomb, which raises the supply cost of the F-15EX's 24-round load by ~1680 points per jet.


**Mission** — Yes, heavily. The mission fields 4x usaf_f-15ex_SEII and 2x usaf_b-1b_dts. The F-15EX unit file that actually loads is mods-source/_vanilla/SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII.ini (local pack, top of order), and it mounts dts_gbu-53_quad on Stations 1-4 and 13-14 (six quad racks = 24 StormBreakers per jet). usaf_b-1b_dts.ini mounts dts_gbu-53_quad on Station1. So every GBU-53 dropped in …


**Recommendation** — Leave the order alone. The Dingtools pack is the upstream author of these dts_* weapons and both aircraft mods are shipping stale copies of them; Dingtools sitting at pos 16 above both is exactly the arrangement that keeps one canonical StormBreaker. No change costs anything here.


*Sampled: Read/diffed all three files in all three mods (9 copies). Compared warhead scale against vanilla usn_mk-82 (Power=28/Medium), usn_gbu-12 (28/Medium), usn_gbu-10 and usn_gbu-24 (62/VeryLarge). Checked MidCourseCorrection=3 against vanilla usage.*


### 2 files: ammunition/fr_cal_12,7x99mm.ini, ammunition/fr_cal_7,62x51mm.ini

**Mods** 3567256221 Charles De Gaulle & Modern French (pos 30) > 3567228449 French Helicopter Package (pos 84)  

**Winner** 3567256221 (Charles De Gaulle & Modern French) wins both · **Risk** none


These are near-clones; each file differs by one or two lines. fr_cal_12,7x99mm.ini: CDG has MaxRange=1800m and AmmoPoints=0.134; the helicopter pack has MaxRange=1500m and AmmoPoints=0.002. fr_cal_7,62x51mm.ini: CDG has MaxRange=1500m, the helicopter pack has MaxRange=1800m. Everything else - MuzzleVelocity 930/869, CEP 12.8/38, warhead block, effects - is identical. Note the inversion: the helicopter pack's pair gives the 7.62mm rifle round (1800m) more reach than the .50 cal (1500m), which is backwards; CDG's pair has the .50 cal out-ranging the 7.62mm, which is right.


**Silently lost** — Nothing of substance. The helicopter pack's copies contain no content CDG's lack - no extra sections, no different model or effect references. What is dropped is a 300m range figure on each file and the 0.002 AmmoPoints value for the .50 cal.


**Risk** — No id collision, no split ownership (both are self-contained leaf ammunition files), no dangling references - both consumers' launchers resolve to the winning definitions. One cataloguing oddity worth noting: this collection carries two separate 7.62mm ids with essentially the same content, fr_cal_7,62x51mm (comma form, used only by CDG's EDA-R craft) and fr_cal_762x51mm (plain form, used by the French Army/Helicopter mods). They are different filenames so they do not contest each other, but a consumer referencing the wrong spelling would dangle silently.


**Mission** — No. Neither file is used by anything the active mission fields. fr_cal_12,7x99mm is consumed by the helicopter pack's NH90 family (fr_nh90, de_nh90, nl_nh90, be_nh90, ita_sh90 - each carrying a 2000-round WeaponMagazineM2), by 3488139470's ita_sh90, and by CDG's EDA-R landing craft and fr_lhd_mistral. fr_cal_7,62x51mm is consumed only by CDG's own fr_edar_* landing craft. None of those unit ids a…


**Recommendation** — No change. CDG's version is the physically sensible pair and the winner is stable. The only visible consequence is on the helicopter pack's own NH90 door guns, which gain 300m of reach and cost 0.134 rather than 0.002 supply points per round - with a 2000-round magazine that is 268 points instead of 4 per rearm, which is a fairer price for a full belt, not a defect.


*Sampled: Read/diffed both files in both mods (4 copies, full files - each is ~40 lines).*


### 1 file: ammunition/usaf_gbu-24.ini

**Mods** 3606774881 U.S. Navy 2027 Capabilities mod (pos 17) > 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (pos 35) > 3758320372 F-16C Fighting Falcon (modern) (pos 80)  

**Winner** 3606774881 (U.S. Navy 2027 Capabilities mod) · **Risk** none


The two losers are effectively the same file as each other - the F/A-18E/F copy and the F-16C copy differ only in that the Hornet copy carries AmmoPoints=2425 and the F-16 copy has no AmmoPoints line at all. Against them the winner is a deliberate GBU-24G/B Paveway III rewrite: WarheadType=1 (Armor Piercing) with Power=71 instead of WarheadType=0/Power=62; Mass=1065kg instead of 907; AirLaunched=True added; MaxTurnRate=6 vs 3; MinLaunchRange=0.2 vs 1.0nm; MaxLaunchRange=12 vs 15nm; MinLaunchAltitude=2000ft vs 500ft; MaxLaunchAltitude=65000 vs 60000; LaunchReliability=98 vs 97; seeker narrowed and given a laser range - SeekerFOV=45 vs 90, SeekerActiveRange=8nm (losers 0.0), SeekerPassiveRange=8 vs 10, plus Zoom=3 added; SelfDestructDelay removed. ImpactSize=Large and Penetration=Always are the same in all three, and the [Models] block is identical - no mesh divergence.


**Silently lost** — Nothing unique. The losers hold no sections, models or effects the winner lacks. What is dropped is the shallower 500ft release floor, the 15nm reach and the 90-degree seeker cone. The trade is real but coherent: the winner's GBU-24 is a heavier BLU-109-class penetrator that must be released from 2000ft or above and glides 3nm less.


**Risk** — No id collision, no dangling references. Split-ownership check passes and is worth stating explicitly: the consumers of usaf_gbu-24 are usn_fa-18e / usn_fa-18f / usn_fa-18f_blk3, all three of which are also won by 3606774881, so the ammunition and the loadout stations that mount it were authored together. 3758320372 also merges a usaf_gbu-24 display-name key via language_en/ammunition_names.ini, which is a merge not an override, so no name is lost.


**Mission** — Yes. The mission's CVN air wing embarks 24x usn_fa-18f_blk3 (Squadron3/4/5, 8 each). usn_fa-18f_blk3.ini is itself won by 3606774881, and that same mod's usn_fa-18e.ini, usn_fa-18f.ini and usn_fa-18f_blk3.ini are the files that reference usaf_gbu-24 - so the mission's Hornets carry the winner's version, and ammo and airframe come from the same mod. Aircrew must be above 2000ft to release.


**Recommendation** — No change. The winner is both the more modern definition and the mod that owns the aircraft actually carrying the weapon, so ammunition and carrier stay in sync. One loser is explicitly marked [DEPRECATED] in the catalog and the other (F-16C modern) does not even mount the weapon - it only ships the file plus a language entry.


*Sampled: Read/diffed all three copies in full.*


### ammunition/ger_dm2a4_er.ini

**Mods** 3629144864 Euromod - Main Pack [line 18] > 3731208477 Euromod - Modern Spanish Navy [line 55]  

**Winner** 3629144864 (Euromod - Main Pack) · **Risk** none


Two completely different authoring styles. Winner: a full standalone SeaHake mod4 ER — Mass=2200, AmmoPoints=7600, GuidanceType=10 (combined active+passive sonar) with VesselAttackGuidanceType=8 (wake homing vs surface ships), MidCourseCorrection=2 with WireControlsDepth=True / WireCountermeasureBonus=0.45 / WireBreakSpeed=20 / WireMinSeafloorClearance=20, SpeedSettings=20,35,50 at SpeedSettingRanges=76.0,52.0,32.0 nm, MaxLaunchRange=76.0, MaxDepth=3000 ft, Power=74 / ImpactSize=Large / SmartFuse=True, AntiCountermeasuresBonus=0.50, seeker 2.5 nm active+passive with gain 48, FractionOfRangeToActivateSeeker=0.85, SearchMode=1 (snake), and a full acoustic signature block (BaseNoise=112, FlowNoise=0.32, TransientBaseNoise=170). Loser: a 16-line alias patch — '#!alias ammunition/ger_dm2a4.ini' plus Mass=1800, AmmoPoints=6000, MaxVelocity=35.0, TerminalVelocity=50.0, MaxLaunchRange=75, GuidanceType=10, MidCourseCorrection=2 and a sonar audio clip; everything else inherits from ger_dm2a4.ini (which only the Main Pack ships, so the alias target is safe either way).


**Silently lost** — The Spanish mod's lighter ER profile (1800 kg, 6000 points, 35 kn top speed, 75 nm) and its Spanish/English flavour text tying the weapon to the S-80 class. The language key ger_dm2a4_er also merges in the Main Pack's favour (rank 18 vs 55), so the in-game encyclopedia shows the Main Pack's 'Extended-range SeaHake mod4 derivative…' text, not the Spanish mod's S-80 description.


**Risk** — No id collision (one filename, one registration). No split ownership. No dangling refs — the loser's alias target ammunition/ger_dm2a4.ini exists in the winning mod, and the winner is fully self-contained. Notably, NO enabled unit fires ger_dm2a4_er: the only references anywhere in mods-source are the two mods' language files and 3784474738's systems/TorpedoAudioClip_Mapping.ini. The Spanish S-80 uses ger_dm2a4 (ae_ssk_s80.ini line 421) and the S-80 Plus uses DateBased_HWT=0,ger_dm2a4|2035,ger_dm2a5, not the ER. So this conflict is currently inert in play.


**Mission** — None — no Spanish or German submarine is fielded in NORTHERN FRONT III FINAL NEWEST, and nothing fires this torpedo anywhere in the collection.


**Recommendation** — Keep the order. The Main Pack version is the strictly more complete file and the invariant 'Euromod Main Pack above every Euromod sub-pack' is the right general rule for this family. If you want the S-80 to actually carry the ER round, that is a unit-file edit (add ger_dm2a4_er to ae_ssk_s80's magazine), not a load-order change.


*Sampled: Both versions of ger_dm2a4_er.ini read in full and diffed; the alias target ger_dm2a4.ini ownership confirmed; ae_ssk_s80.ini and ae_ssk_s80_plus.ini torpedo lines read; both language_en/ammunition_names.ini entries read.*


### ammunition/wp_aa-12.ini

**Mods** 3417446309 MIG-29 Family (rank 34) > 3481228992 ChengDu J-10C (rank 83) > 3526982088 XIAN JH-7A (rank 84) > 3436170138 Shenyang J-11 (rank 99)  

**Winner** 3417446309 (MIG-29 Family) · **Risk** none


Three distinct contents. 3481228992 and 3526982088 are byte-identical to each other and are the LEGACY R-77: MaxVelocity=1825 kt with VelocityBleed=0.7, AccelerationTime=10.5, Acceleration=19.0, no ApplyKinematics, MaxTurnRate 45.0, MinLaunchRange 3.1 / MaxLaunchRange 43.7 nm, InitialFlightPhaseDuration 3.0, MaxLoftAngle 50.0 with MaxLoftAlt=Target, LaunchReliability 97, AntiCountermeasuresBonus 0.25 / AntiJammerBonus 0.15, SearchMode=0, plus a [Debris] block and a Tomahawk-derived booster effect. The winner is the modern R-77: ApplyKinematics=True, MaxVelocity 1600 with AccelerationTime=6 at 18.2 G (annotated 'Total Δv ≈ 779 ≈ 2.29Ma'), DragCoefficient=-1, MaxFlightTime=60 s, MaxTurnRate 42.0 plus MaxTurnG=50, MinLaunchRange 0.6 / MaxLaunchRange 40 nm, InitialFlightPhaseDuration 0.8, shallow loft (MaxLoftAngle 5.0, MaxLoftAlt 40000 ft), MaxAttackVelocity=1600, LaunchReliability 95, and better ECCM at AntiCountermeasuresBonus 0.35 / AntiJammerBonus 0.25. It also adds AmmoPoints=1220 and AirLaunched=True, which the J-10C/JH-7A copies lack. 3436170138's copy is essentially the winner with three differences: Acceleration 13.2 instead of 18.2, no MaxTurnG=50, and no InsDrift comment block.


**Silently lost** — From the J-10C/JH-7A pair: the longer 43.7 nm reach, the 50-degree loft-to-target-altitude profile, LaunchReliability 97, and a [Debris] section — none of which is worth having, since all of it rides on the obsolete VelocityBleed model with weaker ECCM. From the J-11 copy: only a softer 13.2 G boost. Nothing of value is lost.


**Risk** — No id collision, no split ownership. The winner's asset chain resolves: ResourcesFolder=assets/models/weapon/ammunition/r77/ with ResourcesMaterial=wp_aa-12_mat.ini, and 3417446309/assets/models/weapon/ammunition/r77/wp_aa-12_mat.ini exists. Mesh .obj not verifiable (binaries stripped from this mirror). Note the contrast with cohort 1: 3481228992 and 3526982088 ship the legacy-schema R-77 here for the same reason they ship legacy-schema PL-12 there — they are a matched pair of older DWZJ mods declaring ApproximateVersion=0.4.0 against a 0.8.2 game.


**Mission** — None. wp_aa-12 is consumed only by 3417446309's MiG-29K/M/SMT family and by 3436170138/aircraft/plaaf_j-11a.ini. The active mission fields neither. Its Su-35S uses su_aa-12_1 / su_aa-12_m from a separate namespace (3434072450), which this cohort does not touch.


**Recommendation** — No change. 3417446309 sits at rank 34, comfortably above all three challengers, and supplies the only copy that uses the live 0.8.2 kinematics and ECCM schema plus supply-system pricing. This is the order working as intended.


*Sampled: md5 grouping across all four mods, then full normalized diffs of the winner against both distinct loser contents, plus verification that the winner's referenced material asset exists.*


### ammunition/plan_cal_30mm.ini (1 file)

**Mods** 3774859959 PLAN Type 001 Aircraft Carrier Liaoning (line 48) > 3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18 (line 58) > 3413868677 Red Storm Arsenal (line 139)  

**Winner** 3774859959 PLAN Type 001 Aircraft Carrier Liaoning · **Risk** none


The winner and Red Storm Arsenal's copy are BYTE-IDENTICAL (zero diff): 26 lines, TargetType=AAW / SecondaryTargetType=ASuW, MuzzleVelocity=1100 m/s, MaxRange=4000 m, CircularErrorProbable=15 m, WarheadType=2 (HEAT), Power=0.85, ImpactSize=Tiny, Penetration=Minor. The Fujian mod's copy is the odd one out: MuzzleVelocity=1250 m/s, MaxRange=5000 m, CircularErrorProbable=100 m, plus Mass=1.06 / AmmoPoints=1.06 for the supply system. Warhead, effects and targeting are the same in all three.


**Silently lost** — From 3663564190 only: the higher 1250 m/s muzzle velocity, the 5 km reach, and the Mass/AmmoPoints supply entries (its CEP of 100 m is worse than the winner's 15 m, so that part is no loss). Red Storm Arsenal loses nothing - its copy is the winner's copy.


**Risk** — No id collision, no split ownership, no dangling refs. Worth noting the shape of this contest for the record: the top and bottom mods ship the same bytes and the middle mod is the only divergent one, so the load order between Liaoning and Red Storm Arsenal is irrelevant for this file - the only decision that matters is Fujian vs the other two, and Fujian loses. Since the Fujian mod's own carrier (plan_cv_type_003) is one of the three consumers, its CIWS now fires the 1100 m/s / 4 km round its author did not write - a stat change on an unfielded ship, nothing more.


**Mission** — None. No consumer of plan_cal_30mm is fielded. Its only users among enabled mods are plan_cv_type_003 (3663564190), plan_type_001 (3774859959) and ten Red Storm Arsenal hulls (Type 054/054A, 052C, 052D, 055, Liaoning, Fujian) - none of which appear in NORTHERN FRONT III FINAL NEWEST. The PLAN ships that ARE fielded (four plan_type_055_2026, plan_type_052d_p3/p4) run their H/PJ-11 CIWS off pla_cal…


**Recommendation** — No change. The winner is the majority version and is more accurate (CEP 15 m vs 100 m); the only thing worth importing from the Fujian copy is the Mass=1.06 / AmmoPoints=1.06 supply-system pair, which is cosmetic for a CIWS round. Reordering would gain nothing and would disturb two carrier mods that sit correctly relative to each other.


*Sampled: All three copies read in full and diffed pairwise. Also enumerated every consumer of plan_cal_30mm among enabled mods and checked the CIWS ammunition id on the mission's plan_type_055_2026.*


### ammunition/usn_rim-66h.ini (1 file)

**Mods** 3629144864 Euromod - Main Pack (order line 18) > 3456859157 Mogami-class Frigate (order line 45)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** none


The winner is a 10-line alias stub: '#!alias ammunition/usn_rim-66g.ini' plus two comment lines ('RIM-66H SM-2MR Block II', 'Mk41 launched, AEGIS') and a [Models] block overriding ResourcesMaterialFolder=assets/europack/materials/RIM-66/ and ResourcesMaterial=RIM-66M_mat.ini. Everything else is inherited from Euromod's own usn_rim-66g: Power=24, KillProbability=0.85, GuidanceType=2, MaxVelocity=2800 kt, MaxLaunchRange=90.0 nm, MaxLoftAlt=70000 ft, MaxAttackAltitude=90000, SeekerPassiveRange=90 nm, SecondaryPassiveRadarGuidanceType=HomeOnJam, AntiCountermeasuresBonus=0.35, and a three-entry [Launchers] block (MK13, MK22, MK26). Euromod's rim-66g is itself a light edit of vanilla — vanilla has MaxAttackAltitude=120000 and SeekerPassiveRange=110, Euromod trims those to 90000 and 90 and adds HomeOnJam and the Europack material. The loser is a fully standalone 195-line SM-2MR Block II: Power=35 (vs 24), ImpactSize=SemiSmall, Penetration=Always, KillProbability=0.90 (vs 0.85), FuzeProximityDistance=15.0 m, MaxVelocity=2350 kt (vs 2800), MaxLaunchRange=90.2 nm (essentially the same 90), MinLaunchRange=0.7, MaxLoftAngle=45 / MaxLoftAlt=45000 (vs 70000) / MaxLoftVelocity=2500, MaxAttackAltitude=140000 (vs 90000), MinAttackAltitude=30, AccelerationTime=40 @ 10.0 G, MaxTurnRate=50, LaunchReliability=98, CircularErrorRadius=2.5 m (5.0 vs Large), SeekerPassiveRange=250 nm (vs 90) with HomeOnJam, AntiCountermeasuresBonus=0.4 / AntiJammerBonus=0.2, TeminalDiveDistance=15, IgnoreHeightDifferenceForTargetDist=True, a Transient signature block, its own two-entry [Launchers] block (MK13, MK26 only), the vanilla usn_rim-66 mesh with ResourcesMeshForLaunch/ResourcesMeshSwitchTime, and explicit particle and collider blocks.


**Silently lost** — The Mogami mod's standalone SM-2MR Block II data: the heavier 35-power warhead, the 0.90 kill probability, the 140000 ft engagement ceiling, the 250 nm passive seeker, the explicit CircularErrorRadius pair, the Transient signature block and the launch-mesh switch. In exchange the winner is faster (2800 vs 2350 kt) and lofts higher (70000 vs 45000 ft). Note the loser's copy is an orphan even inside its own mod — js_ffg_mogami.ini and js_ffg_mogami_variants.ini are the only vessels 3456859157 ships, and their magazines call usn_rgm-84d, usn_rim-116, usn_rim-162, usn_rur-5, usn_mk46_ship, usn_cal_127mm, usn_rr144_chaff and usn_adc_mk1_noisemaker — never usn_rim-66h. The Mogami mod ships this file and then does not use it.


**Risk** — No id collision. The alias resolves cleanly: ammunition/usn_rim-66g.ini exists in both 3629144864 and vanilla, and Euromod's own copy wins at line 18, so usn_rim-66h inherits Euromod-tuned data rather than vanilla data. The material asset it overrides is present at mods-source/3629144864/assets/europack/materials/RIM-66/RIM-66M_mat.ini. The launcher-positioning concern that an alias usually raises does not apply — Euromod's rim-66g carries a superset of the loser's [Launchers] block (MK13, MK22, MK26 vs MK13, MK26), so nothing is left unpositioned, and in any case all three live consumers are Mk41 VLS ships. No dangling references either way.


**Mission** — None. usn_rim-66h has no vanilla consumer at all (no vanilla vessel or aircraft references it) and exactly three live mod consumers, all from 3390330875: usn_cg_ticonderoga_vls_1990, usn_ddg_arleigh_concept and usn_ddg_burke_f1_1996, each loading 8 rounds per magazine. None of the three appear in NORTHERN FRONT III FINAL NEWEST — the mission's Aegis ships are usn_cg_ticonderoga_vls_2027, usn_ddg_…


**Recommendation** — Keep 3629144864 above 3456859157; nothing needs to move. Euromod is the shared European weapons database and owns the whole RIM-66 family (usn_rim-66g/h/j/k/m-2/m-5) as a consistent aliased set with matching Europack materials — letting a single-ship JMSDF frigate mod redefine one member of that family in isolation would fragment it for no benefit, especially since the Mogami itself never fires the round. The only thing genuinely worth considering is the loser's 140000 ft ceiling versus the winner's 90000 ft, which matters against ballistic targets; if you want SM-2 to reach higher, edit Euromod's usn_rim-66g rather than promoting the Mogami file, so all six RIM-66 variants move together.


*Sampled: Both versions read in full (195 vs 10 lines). Because the winner is an alias, also read the resolved target ammunition/usn_rim-66g.ini from 3629144864 including its [Launchers] block, compared it against the vanilla usn_rim-66g, confirmed the RIM-66M_mat.ini …*


### ammunition/dts_b-61.ini (1 file)

**Mods** 3760871384 Dingtools Weapon Pack (order line 16) > 3741944366 B-52H Stratofortress (order line 68)  

**Winner** 3760871384 Dingtools Weapon Pack · **Risk** none


The two files are 157 of 159 lines identical. Exactly two keys differ, both in the seeker block: SeekerGain 0.0 (loser) vs 10.0 (winner), and SeekerFOV 0.1 (loser) vs 80 (winner). Everything else matches byte for byte — Type=Bomb, TargetType=ASuW, LandAttackCapability=All, AirLaunched=True, Mass=454 kg, AmmoPoints=1000, GuidanceType=1 (IR homing), MidCourseCorrection=0, DropDuration=4.0, InitialFlightPhaseDuration=3, GravityFactor=6, ApplyKinematics=True, MaxTurnRate=6, MinLaunchRange=1 nm, MaxLaunchRange=15 nm, MinLaunchAltitude=500 / MaxLaunchAltitude=60000 ft, LaunchReliability=95, VerticalWobblingStrength=2.0 / Speed=1.0, SeekerActiveRange=0.0, SeekerPassiveRange=100, TargetMemory=True, SelfDestructAfterTargetGone=False, SelfDestructDelay=5.0. Worth noting for the record: despite the dts_b-61 filename, the header comment in BOTH copies reads '# GBU-32 JDAM 454kg GPS guibed bomb. by dts' and the mass, guidance and wobble parameters are a JDAM's, not a B61's — the two authors (both 'dingtools') simply shipped the same file twice with a one-line seeker tweak. The winner's SeekerFOV=80 with SeekerGain=10.0 gives the weapon a usable homing cone; the loser's SeekerFOV=0.1 with SeekerGain=0.0 is effectively a pencil-beam with no gain, which on a GuidanceType=1 weapon means it is far more likely to lose the target after release.


**Silently lost** — Nothing of substance. The loser's copy differs only by two seeker values that are strictly worse — a 0.1-degree field of view and zero seeker gain against the winner's 80 degrees and 10 dB. There is no content, no station, no model and no id in 3741944366's version that the winner lacks.


**Risk** — No id collision — one id, two identically-named files, clean override. No dangling references: the files are otherwise identical, so both point at the same model and effects. No split ownership — there is no dts_b-61 companion file. The load-order placement also happens to match the author's own published instruction, recorded in data/mod-catalog.json for 3741944366: 'Keep Dingtools Weapon Pack ABOVE all dingtools mods'. Dingtools Weapon Pack sits at line 16 and B-52H at line 68, so that instruction is already satisfied. The only thing I would flag is cosmetic and affects both copies equally: the file is named for a B61 nuclear bomb but its header, mass (454 kg) and parameters describe a GBU-32 JDAM, so the encyclopedia entry and the F-15EX's 'B61' station label are both misleading about what is actually being dropped.


**Mission** — Mission-relevant, and the winner is the version that helps. NORTHERN FRONT III FINAL NEWEST fields 4x usaf_f-15ex_SEII, which is owned by 3636386513 (order line 70) and mounts the weapon at Station16=dts_b-61|B61 — so this bomb is on the mission's F-15EX loadout right now, and it will use the winner's 80-degree / 10 dB seeker rather than the loser's 0.1-degree / 0 dB one. The other consumer, 3741…


**Recommendation** — No change — keep 3760871384 above 3741944366. The winner is the same file with the only two differing values set correctly, it is what the mod author explicitly asked for, and it is the version the mission's four F-15EXs will actually drop. Nothing to move, nothing to patch. If the B61-versus-JDAM mislabelling bothers you, that is a rename/description issue in both copies rather than a load-order question.


*Sampled: Both versions (159 lines each) diffed in full, and the winner's [General] and [Guidance] blocks read to judge whether the two differing keys matter. Also traced both consumers of the id.*



## Identical — recorded so they are never re-litigated  (30)


### ammunition/su_aa-10a.ini, su_aa-10b.ini, su_aa-10c.ini, su_aa-10c_navy.ini, su_aa-10d.ini, su_aa-11.ini (6 files)

**Mods** 3438479626 (1143.5 Kuznetsov) > 3434072450 (Sukhoi Flanker Family)  

**Winner** 3438479626 (1143.5 Kuznetsov) · **Risk** low


None. All six pairs are byte-identical (e.g. su_aa-10c md5 0386f004869ca343ae971655d21dd76e in both; su_aa-11 md5 2689f517cf70091fcee17df7ce9b64f0 in both). The shared su_aa-10c is the R-27ER (1987) AA-10C Alamo: Mass=350 kg, AmmoPoints=700, WarheadType=0 Power=15, KillProbability=0.85, GuidanceType=3 (active radar), RCS=VerySmall. This is one mod copying the other's ammunition folder verbatim.


**Silently lost** — Nothing. The losing copies are identical byte-for-byte, so the override discards duplicates only.


**Risk** — No id collision: these ammunition .ini files declare no id/Name key — identity is the filename — so a same-filename contest is a pure override and cannot produce the 'item with the same key' crash. No split ownership: the only files 3438479626 and 3434072450 contest at all are these six ammunition files (verified by pairwise directory comparison across aircraft/, vessels/, submarines/, land_units/, helicopters/, biologic/, ammunition/); neither mod's unit or _squadrons files are touched by the other. One live cosmetic defect, via language merge rather than override: mods-source/3434072450/language_en/ammunition_names.ini line 6 reads 'su_aa-10c=R-27ER,,AAM,,The Vympel R-27ER...' — five comma fields where line 10 (su_aa-11) uses the four-field convention. The extra comma likely shifts the description field, so the AA-10C encyclopedia text may render blank. 3438479626 does not define su_aa-10c, so that malformed line is the one that merges in.


**Mission** — None in practice. mods-source/3434072450/aircraft/wp_su-35s.ini (6 airframes in NORTHERN FRONT III FINAL NEWEST) does reference su_aa-10c and su_aa-11, but every mission Su-35S flies LoadoutVariant=AirToAirIntercept, whose [WeaponSystem1AirToAirIntercept] block carries su_aa-12_m x2 and su_aa-13 x2 only — no AA-10/AA-11 is loaded.


**Recommendation** — Leave the order alone. No reorder can change anything here — the two copies are the same bytes. If you ever want to shrink the collection, this is evidence the Kuznetsov mod's ammunition/ folder is redundant with the Flanker Family's for the R-27/R-73 family.


*Sampled: All 6 file pairs md5-compared in both mods (identical hashes, identical line counts: aa-10a 174, aa-10b 183, aa-10c 175, aa-10c_navy 175, aa-10d 184, aa-11 179). Read /home/user/Seapower-mods/mods-source/3438479626/ammunition/su_aa-10c.ini in full. Also read …*


### ammunition/su_kh-35.ini (1 file)

**Mods** 3417446309 (MIG-29 Family) > 3434072450 (Sukhoi Flanker Family)  

**Winner** 3417446309 (MIG-29 Family) · **Risk** low


None. The two copies are byte-identical.


**Silently lost** — Nothing from the .ini override. The one thing genuinely lost sits in the language merge, not the file override — see risk detail.


**Risk** — No id collision (no id key in the file). No split ownership: su_kh-35.ini is the only file these two mods contest across aircraft/, vessels/, submarines/, land_units/, helicopters/, biologic/ and ammunition/. The only live defect is the blank language description described above, and it comes from the merge path rather than the override path.


**Mission** — None in practice. mods-source/3434072450/aircraft/wp_su-35s.ini (6 airframes) references su_kh-35, but all six mission Su-35S fly LoadoutVariant=AirToAirIntercept, which carries su_aa-12_m x2 and su_aa-13 x2 and no Kh-35.


**Recommendation** — No load-order change — reordering these two would flip nothing, since su_kh-35.ini is the only file they both ship in any override directory. There is a worthwhile one-line content fix though: mods-source/3417446309/language_en/ammunition_names.ini line 33 is 'su_kh-35=KH-35,,ASM,' with an empty description, and because language files merge key-by-key with the higher mod winning, that blank entry (line 41 in the order) overrides mods-source/3434072450/language_en/ammunition_names.ini line 41, which supplies the full Zvezda Kh-35 'Harpoonski' description and classifies it AGM rather than ASM. So the player sees a Kh-35 with no encyclopedia text. Fix it in a language patch, not by reordering.


*Sampled: Both copies md5-compared (identical: 8f4c30670f39652e479327b84c566252). Read both mods' language_en/ammunition_names.ini su_kh-35 entries and the Su-35S loadout block in mods-source/3434072450/aircraft/wp_su-35s.ini.*


### ammunition/usn_cal_pgu-14b.ini (1)

**Mods** 3414146266 A-10A Thunderbolt II (order line 62) > 3459682829 A-10C (63)  

**Winner** 3414146266 A-10A Thunderbolt II — immaterial, the two copies are identical. · **Risk** low


Nothing differs. Both copies of usn_cal_pgu-14b.ini are 25 lines with md5 a0d8b68b... and a normalised diff is empty. This is expected: the catalog records that the A-10C mod is 'based on the A-10A mod', and the 30 mm PGU-14/B API round was carried over verbatim. (The two mods also both ship animations/animations_usa_a-10a.ini, which is outside this cohort.)


**Silently lost** — Nothing — the loser's copy is byte-identical to the winner's.


**Risk** — The contested file itself carries no risk. But the cohort surfaces a real split ownership on a mission-fielded unit: aircraft/usa_a-10c.ini is won by SEST_Integration (top of order) while aircraft/usa_a-10c_squadrons.ini exists only in 3459682829 — the loser of this cohort. Two consequences. First, that squadrons file is internally inconsistent: it declares NumberOfSquadrons=7 but defines only [Squadron1] (a-10_81st_tfw.png) and [Squadron2] (a-10_91st_tfw.png). The mission uses Squadron1, so it resolves today, but five declared slots have no definition and would fall back to [Default]. Second, if 3459682829 were ever unsubscribed, SEST's usa_a-10c would lose its squadron definitions entirely while still being fielded by the mission — a hard dependency that is not recorded anywhere. No id collision (usa_a-10a and usa_a-10c are distinct ids, each owned by one mod).


**Mission** — The mission fields two usa_a-10c at lines 1736 and 1747, both with SquadronReference=Squadron1 and LoadoutVariant=SEST_REDBACK. The A-10C's gun therefore uses this file every run — but since both versions are identical the load order is irrelevant to the outcome. I confirmed the mission's references resolve: SEST_Integration's usa_a-10c.ini declares SEST_REDBACK in AvailableLoadouts and defines […


**Recommendation** — No reorder — there is nothing to gain, the files are identical. Two things worth recording instead: (1) note in the catalog that SEST_Integration's usa_a-10c has a hard dependency on 3459682829 for aircraft/usa_a-10c_squadrons.ini, so the A-10C mod must not be unsubscribed while the mission fields it; (2) either correct NumberOfSquadrons to 2 in that file or add the five missing squadron blocks — the latter is a good candidate to fold into SEST_Integration alongside the usn_fa-18e_squadrons.ini fix from the Hornet cohort, since SEST already owns the A-10C unit file and would then own the matched pair.


*Sampled: mods-source/3414146266/ammunition/usn_cal_pgu-14b.ini and mods-source/3459682829/ammunition/usn_cal_pgu-14b.ini in full, md5-compared and normalised-diffed. Also read mods-source/3459682829/aircraft/usa_a-10c_squadrons.ini in full, and checked integration/dis…*


### ammunition/plaaf_90-Ⅰ_rocket.ini (1)

**Mods** 3486502935 Type 003 Fujian / Type 004 CVN Aircraft Carriers (order line 56) > 3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18 (58) > 3481228992 ChengDu J-10C Vigorous Dragon (90) > 3526982088 XIAN JH-7A (91) > 3436170138 Shenyang J-11 (106) > 3433577445 Shenyang J-8 (108)  

**Winner** 3486502935 Type 003 Fujian / Type 004 CVN Aircraft Carriers · **Risk** low


Six copies, three distinct contents. Ballistics, warhead and guidance are effectively the same 90 mm unguided aerial rocket in every version; the diffs are five lines or fewer. Group A — 3486502935 (winner), 3481228992, 3526982088: identical except the model path. ImpactSize=small, Penetration=moderate, HitShipExplosionClass=RocketShipHitExplosion, HitAirExplosionClass=RocketShipHitExplosion, HitDefaultExplosionClass=RocketShipHitExplosion, HitGroundExplosionClass=SmallGroundHitExplosions, BoosterEffect=None, InFlightEffect=effects/weapons/emitters/rocket_small_launch_effect. Group B — 3436170138, 3433577445: drop HitAirExplosionClass entirely and use HitGroundExplosionClass=RocketGroundHitExplosion. Group C — 3663564190: same as B, plus capitalised enum values (ImpactSize=Small, Penetration=Moderate rather than lowercase). The one difference that separates the winner from all five losers is the mesh location: the winner has ResourcesFolder=assets/ammunition/models/ while every loser has ResourcesFolder=assets/models/ammunition/UB-32-57/. Everything else in [Models] is common — ResourcesRoot=plaaf_90mm_rocket.obj, ResourcesMesh=inflight, ResourcesMaterialFolder=ships/materials/, ResourcesMaterial=modular_parts, AssetBundleMesh=usn_rim-7.


**Silently lost** — Almost nothing. The losers' only distinct content is the alternative UB-32-57 model path and, for groups B and C, a slightly different ground-impact effect class (RocketGroundHitExplosion instead of SmallGroundHitExplosions) and the absence of an air-burst class. No weapon capability, range, warhead or guidance value is lost.


**Risk** — NO ID COLLISION between the two Fujian mods, which is the thing worth stating plainly given the catalog's 'THREE Fujian carriers — pick a primary' warning: 3663564190 registers vessels/plan_cv_type_003.ini and 3663564190 alone; 3486502935 registers vessels/plan_cvn_004.ini and 3486502935 alone. They coexist under distinct ids and both are fielded by the mission simultaneously. No crash risk from this pair. No split ownership — each carrier's _variants.ini is owned by the same mod as its unit file. One unverifiable risk: the winner's ResourcesFolder=assets/ammunition/models/ is a path that appears nowhere in this repo, whereas 3481228992 and 3436170138 do carry assets/models/ammunition/UB-32-57/. That is NOT proof the winner's path is wrong — the export is .ini-only and drops directories that held only binary files, so a folder containing just plaaf_90mm_rocket.obj would be invisible here. It is consistent with the winner's own convention (it does ship assets/ammunition/materials/ with ten *_mat.ini). If the rocket ever renders as an invisible or default projectile, this line is the cause. Separate hygiene note: the filename contains U+2160 ROMAN NUMERAL ONE (plaaf_90-Ⅰ_rocket.ini). It works, but it is a portability hazard for any script or archive tool that is not UTF-8 clean.


**Mission** — No. The rocket is reachable only through the pod containers plaaf_hf-6.ini (shipped by 3486502935, 3481228992, 3526982088, 3436170138, 3433577445) and plaaf_hf-20.ini (3663564190). Those pods are carried only by plaaf_j-8b/j-8e/j-8f, plaaf_jh7a and 3663564190's plan_j-15t — none of which the mission fields. The mission does field both PLAN carriers from this cohort's top two mods (plan_cv_type_00…


**Recommendation** — No reorder. Six mods contest this file and five of them would give the player a functionally identical rocket, so the ordering is not worth spending load-order churn on — and moving any of the four fighter mods (order lines 90-108) up past both carrier mods would have a large blast radius for a five-line cosmetic gain. The single thing worth doing is a five-minute visual check: load a J-8F or JH-7A with an HF-6 pod and confirm the rockets have a mesh. If they do not, the fix is a one-line edit to the winner's ResourcesFolder (point it at assets/models/ammunition/UB-32-57/), not a reorder.


*Sampled: All six copies md5-compared; the winner normalised-diffed against 3663564190, 3481228992 and 3436170138 (which covers all three content groups, since 3526982088 hashes identically to 3481228992 and 3433577445 to 3436170138). Read the winner's [Models] and [Ef…*


### ammunition/pla_pod_kg-800.ini (1 file)

**Mods** 3486502935 Type 003 Fujian / Type 004 CVN Air (order line 56) > 3506979898 Shenyang J-16A (歼-16A 潜龙) (order line 87)  

**Winner** 3486502935 Type 003 Fujian / Type 004 CVN Aircraft Carriers · **Risk** low


The two files are BYTE-IDENTICAL — diff exits clean with zero differences. Both are 20-line Type=Container ECM pods, Mass=260, NumberOfSensorSystems=1, [SensorSystem1] Type=ECM SystemName=KG-800 Mount=Dummy ModuleType=Sensor, model assets/ammunition/models/kg-800.obj mesh KG800, material assets/ammunition/materials/kg-800_mat.ini. Structurally they are faithful clones of the vanilla container-pod pattern (mods-source/_vanilla/original/ammunition/usaf_alq-119.ini uses the same Mass=260 and the same one-ECM-system layout). The load order between these two mods therefore changes nothing at all for this file. Where the two mods DO diverge is in the merged systems/sensors.ini [KG-800] entry, which is a key-by-key merge rather than a file override, so the higher mod wins the key: 3486502935 (winning, '#Users: J-15D') gives PeakPower=15.0 kW, MaxRange=90.0 km, Gain=7.0 dB, JamChance=0.4; 3506979898 (losing, '#Users: plaf_j16d') gives PeakPower=19.0 kW, MaxRange=200.0 km, Gain=7.5 dB, JamChance=0.7. Both share Kind=ECM, Type=Universal, JamConeViewArcs=35.0 and the same six jammable bands (UHF, L, S, C, X, Ku).


**Silently lost** — Nothing from the contested file — the versions are identical, so the loser's copy contains no content the winner lacks. The only real loss in this pairing happens in the merged sensors file, not the ammunition file: 3506979898's stronger KG-800 jammer (19 kW / 200 km / JamChance 0.7) is overridden by 3486502935's weaker one (15 kW / 90 km / JamChance 0.4), roughly halving the pod's reach and cutting its base jam chance by 43%.


**Risk** — No id collision, no content difference, no reason to touch the order for this file. One genuine DANGLING REFERENCE surfaced while checking it, and it is worth fixing because the mission fields eight of the affected aircraft: mods-source/3486502935/aircraft/plan_j-15d.ini line 160-163 declares '[SensorSystem4] #ECM / Type=ECM / SystemName=pla_pod_kg-800'. No systems file in any enabled mod — and none in vanilla — defines a [pla_pod_kg-800] block; I grepped the whole mods-source tree including mods-source/_vanilla. The defined sensor id is [KG-800] (in both 3486502935 and 3506979898 systems/sensors.ini). The vanilla convention confirms the mistake: usaf_alq-119.ini is carried as a station loadout and exposes its jammer through the pod's own SystemName=AN/ALQ-119, and no vanilla aircraft ever puts a pod id in a SystemName= field. So the J-15D's built-in ECM system almost certainly fails to resolve; its four podded stations should still work, since those reference the container correctly. This defect belongs to the winning mod and is not caused by the load order — reordering will not fix it.


**Mission** — Mission-relevant, though not through the contested file. NORTHERN FRONT III FINAL NEWEST fields 8x plan_j-15d, which is owned by the winning mod 3486502935 and carries pla_pod_kg-800 on four stations (Station24-27) across its A2A and AntiShip loadouts, plus a [SensorSystem4] ECM entry. So every mission J-15D flies with this pod — but since the two ammunition files are identical, the load order be…


**Recommendation** — Leave the order exactly as it is; the files are identical so there is nothing to gain either way. Two follow-ups that are worth more than any reorder: (1) fix mods-source/3486502935/aircraft/plan_j-15d.ini [SensorSystem4] to SystemName=KG-800 instead of SystemName=pla_pod_kg-800 — that is eight mission aircraft currently flying with an unresolvable built-in jammer; (2) decide which KG-800 jammer profile you want, because the sensors merge silently gives you the weaker one (15 kW / 90 km / JamChance 0.4). If you want 3506979898's 200 km version, that requires moving 3506979898 above 3486502935 in the order, which would also hand it aircraft/plaf_j16d and any other shared file — or, far cheaper, override the [KG-800] key in a SEST systems patch.


*Sampled: Both versions read in full (20 lines each) and diffed. Also read both mods' [KG-800] entries in systems/sensors.ini, and traced every reference to the pod across enabled aircraft.*


### 19 of the 35 are byte-identical: mm_a244_air, mm_a244_ship, mm_a244s_air, mm_a244s_ship, mm_a244s_mod1_air, mm_a244s_mo…

**Mods** 3629144864 Euromod - Main Pack (load-order line 18, WINNER) > 3505420313 Italian Navy Mod (line 38)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** none


None. `diff` reports zero differing bytes on all 19 files, and line counts match exactly (e.g. mm_a244_air 213/213, mm_aspide 183/183, mm_cal_76mm 40/40, mm_otomat_mk2_blk1 184/184). The two mods ship literally the same A-244/A-244S torpedo family, Aspide SAM, Barricada/BAS decoys, 25/40/76/127/135 mm gun rounds, depth charges, Mistral, Otomat Mk2 Blk1/Blk2 and SCLAR HE rounds.


**Silently lost** — Nothing. The Italian mod's copies are shadowed but contain no content the Euromod copies lack.


**Risk** — No id collision (ammunition ids derive from filename, and only one file per name loads, so no duplicate-key registration). No split ownership. No dangling references introduced.


**Mission** — None. No mission under integration/missions/ references any of these ammunition ids.


**Recommendation** — Take no action. Roughly 54% of this cohort is noise — worth recording so the pair is not re-litigated. The two mods clearly share a common Italian-ammunition ancestor.


*Sampled: All 19 compared byte-for-byte with `diff -q` plus line counts; no partial sampling needed.*


### 1 file: ammunition/fr_cal_762x51mm.ini

**Mods** 3629144864 Euromod - Main Pack (pos 18) > 3736147136 French Army Vehicles (pos 83) > 3567228449 French Helicopter Package (pos 84)  

**Winner** 3629144864 (Euromod - Main Pack) - but the choice is immaterial · **Risk** none


None whatsoever. All three copies are 940 bytes and share md5 1092ed23ff4f0b77770f87088d1f2312 - byte-identical. Every value matches: Type=Projectile, TargetType=AAW with SecondaryTargetType=ASuW, CanNotAttackTypes=Missile, MuzzleVelocity=869, MaxRange=1800, CircularErrorProbable=38, Power=0.1, ImpactSize=Tiny, Penetration=Minor, and the same four effect references.


**Silently lost** — Nothing. The two losing copies are the same bytes as the winner.


**Risk** — No id collision, no split ownership, no dangling references. The only thing to keep an eye on is drift: if any one of the three mods updates its copy in a future workshop release, the winner silently decides whose update applies, and because the files are identical today nobody would notice the divergence. Note also the sibling id fr_cal_7,62x51mm (comma spelling) is a separate file with near-identical content owned by CDG and the helicopter pack - two ids for the same round across this collection.


**Mission** — No. Consumers are 3736147136's land vehicles (fr_afv_jaguar, fr_ifv_vbci, fr_arv_amx10 and friends), 3567228449's fr_nh90_tth_special_forces / fr_ec_725 / fr_sa_342_gazelle_special_forces, and CDG's fr_raft_* small craft. None of those ids appear in NORTHERN FRONT III FINAL NEWEST.


**Recommendation** — No action. This cohort is noise in the conflict report, not a conflict - three mods vendoring the identical shared file. Worth recording so it is not re-investigated later, and worth remembering that it means no reordering among these three mods can change 7.62mm behaviour.


*Sampled: Read all three copies in full and hashed them.*


### 9 ammunition files: su_aa-11_LQS.ini, su_aa-12_1_LQS.ini, su_aa-12_m_LQS.ini, su_aa-12_pd_LQS.ini, su_as-14_LQS.ini, su…

**Mods** 3659742367 MiG-35 Fulcrum-F (米格-35 支点-F) [line 100] > 3503594612 SU-57 Felon (重刑犯) [line 119]  

**Winner** 3659742367 (MiG-35 Fulcrum-F) — but the choice is moot, see below · **Risk** none


NONE. All 9 files are byte-identical between the two mods (md5 match on every one, e.g. su_aa-12_pd_LQS.ini = 1928d7cdb4322cf8e963c2527787a03a in both, su_kh-35_LQS.ini = e368ca5970471291a19fb4663b7e3170 in both). Both mods are clearly forks of the same author's shared Russian-weapons library (identical Chinese inline comments, identical '_LQS' author suffix). I also checked the two mods' merged systems/ files: the only section names they share, [GSh-30-1] and [Su-57GuidancePodNoAlignment], are also byte-identical, so the systems merge is a no-op as well.


**Silently lost** — Nothing. The loser's copies are ignored, but they are the same bytes.


**Risk** — No id collision: same filename means one registration, and both registrations would be identical anyway. No split ownership — each mod owns its own aircraft/<id>.ini + <id>_squadrons.ini pair (wp_mig-35 / wp_su-57) and neither contests the other's. No dangling refs: each mod's unique ammunition (SU-57's su_aa-13_LQS.ini R-37M and wp_as-11a_LQS.ini; MiG-35's su_kh-38_LQS.ini, su_as-17a_LQS.ini, wp_tank_1200mig-35.ini) is uncontested and loads normally.


**Mission** — None. NORTHERN FRONT III FINAL NEWEST fields neither wp_mig-35 nor wp_su-57 (checked all 127 Type= values in the mission).


**Recommendation** — Leave the order alone. This cohort is noise — record it as a known-benign duplication so a future pass does not re-open it.


*Sampled: All 9 files md5-compared in both mods; su_aa-12_pd_LQS.ini and su_kh-35_LQS.ini read in full; both mods' systems/sensors.ini + weapons.ini section lists compared and the two shared sections diffed line-by-line.*


### ammunition/usn_mk-82.ini

**Mods** 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet [line 35] > 3737267013 United States Naval Aviation [line 59] > 3758320372 F-16C Fighting Falcon (modern) [line 80] > 3508978375 [DEPRECATED] Lockheed Martin F-35C Lighting II [line 82] > 3559495372 Lockheed AC-130 Pack [line 95] > 3514484654 RA…  

**Winner** 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) · **Risk** none


Effectively none. Five of the six copies are byte-identical (md5 b28534ac02f38950fa844d89a6d1202d: the winner, F-16C, deprecated F-35C, AC-130 Pack and RAAF F-35A). The sixth, United States Naval Aviation, differs on exactly ONE line — ResourcesFolder=assets/models/ammunition/mk82/ instead of the winner's assets/models/weapon/ammunition/mk82/. Mass, warhead, ballistics, effects and colliders are identical throughout.


**Silently lost** — Nothing of substance — one alternate texture-folder path.


**Risk** — No id collision, no split ownership, no dangling reference: the winner's model directory assets/models/weapon/ammunition/mk82/ is shipped by 8 enabled mods including the winner itself (3426791311, 3413868677, 3508978375, 3505420313, 3514484654, 3758320372, 3503670861, 3559495372); USNA's variant path exists only inside USNA. So the surviving path is the better-supported one. Same deprecated-mod hygiene note as the AGM-65D cohort applies (this is one of the 12 ammunition files 3426791311 owns).


**Mission** — Mission-adjacent but inert. NORTHERN FRONT III FINAL NEWEST fields 4× usaf_b-52o, whose winning file (SEST_Integration) has 3× 'usn_mk-82|MK82_Clip' stations, so the winner's Mk-82 is live in the mission — but since the versions are stat-identical there is no behavioural delta. The mission's usaf_ac-130j does not carry Mk-82 (only the AC-130A in that pack does).


**Recommendation** — No change. Record as benign duplication so it is not re-audited.


*Sampled: usn_mk-82.ini md5-compared across all 6 mods; winner diffed in full against the USNA copy; mk82 asset-directory presence enumerated across mods-source; consumer loadouts checked (usaf_ac-130a.ini, usaf_b-52o.ini, SEST_Integration's usaf_b-52o.ini).*


### 3 ammunition files: ammunition/plaaf_4xgj.ini (4-round glide-bomb container), ammunition/plaaf_bbm2.ini (the BBM-2 ASM …

**Mods** 3663564190 "Type 003 Aircraft Carrier - PLANS Fujian CV-18" (rank 51) > 3670643788 "Shenyang J-50 (沈阳航空工业 歼-50)" (rank 82)  

**Winner** 3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18 · **Risk** none


Effectively identical — this is the same content shipped twice by the same lineage. plaaf_4xgj.ini and plan_yj-15.ini are byte-for-byte identical (1595 and 10230 bytes, same size, empty diff). plaaf_bbm2.ini differs by exactly one line: the winner adds `TerminalDiveDistance=3.5 // in N. miles.` at line 69, which the J-50 copy lacks. Everything else — Type=Missile, TargetType=ASuW, LandAttackCapability=All, Mass=130, the whole guidance/kinematics/seeker block and the model definitions — matches.


**Silently lost** — Nothing. The loser's plaaf_bbm2.ini is a strict subset of the winner's (one fewer key); the other two files are identical copies.


**Risk** — No id collision (same filenames = ammunition overrides, and the surviving definitions are the same content). No split ownership: the aircraft that consume these ids — plan_j-50.ini (3670643788), plan_j-15t.ini and plan_j-35.ini (3663564190) — are uncontested between the two mods, and both mods' copies of the ammunition define the same ids with the same stats, so whichever aircraft file wins gets a coherent munition. No dangling references: model paths are identical in both copies.


**Mission** — Marginal but present — plan_j-50 is fielded three times in NORTHERN FRONT III FINAL NEWEST and plan_cv_type_003 is in the order of battle. Because the two versions are the same content, the J-50's BBM-2 simply gains the winner's TerminalDiveDistance=3.5 terminal dive. No behavioural surprise for the player.


**Recommendation** — Leave the order alone. There is no reason to touch these two mods relative to each other for these files.


*Sampled: All 3 files diffed byte-for-byte in both mods. Also read the consuming aircraft: /home/user/Seapower-mods/mods-source/3670643788/aircraft/plan_j-50.ini, /home/user/Seapower-mods/mods-source/3663564190/aircraft/plan_j-15t.ini and .../plan_j-35.ini.*


### 1 ammunition file: ammunition/usn_tank_610_f-18.ini (600 gal / 1800 l external fuel tank for the Super Hornet family)

**Mods** 3426791311 "[DEPRECATED] Boeing F/A-18E/F Super Hornet" (rank 28) > 3737267013 "United States Naval Aviation" (rank 52) > 3413868677 "Red Storm Arsenal" (rank 132)  

**Winner** 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet · **Risk** none


Functionally there is nothing to choose between them. The Red Storm Arsenal copy (1279 bytes) is the winner's file with CRLF line endings — the diff shows all 30 lines as changed but the content is character-for-character the same (Fuel=1800, Type=Fueltank, CircularErrorRadius=2000, same effects block, and even the same ResourcesFolder=assets/models/vechicle/aircraft/f-18e/ with ResourcesRoot=fa-18e.obj, ResourcesMesh=f-18_fuletank, ResourcesMaterial=f-18e_mat.ini). The United States Naval Aviation copy (1245 bytes) differs from the winner on exactly one line: ResourcesFolder=assets/models/aircraft/usn_fa-18e/ instead of assets/models/vechicle/aircraft/f-18e/. Both of those folders exist and both contain f-18e_mat.ini and tank_mat.ini in their respective mods, so both paths resolve. Fuel quantity, mass handling, guidance and effects are identical across all three.


**Silently lost** — Nothing of substance — one alternative asset path and a set of CRLF line endings.


**Risk** — No id collision — three copies of one ammunition filename, resolved by override, and the surviving definition is the same content. No dangling reference: the winner's assets/models/vechicle/aircraft/f-18e/f-18e_mat.ini is shipped by 3426791311 itself (and also by 3413868677). SPLIT OWNERSHIP exists but is harmless: the mission's usn_fa-18f_blk3.ini is won by 3430135740 "F/A-18 Murder Hornet with AIM-174B" (rank 15), a fourth mod that is not in this cohort, while the tank it references comes from 3426791311 — verified that 3430135740/aircraft/usn_fa-18f_blk3.ini does reference usn_tank_610_f-18, and the winning definition satisfies it.


**Mission** — Yes, but with no consequence. NORTHERN FRONT III FINAL NEWEST assigns usn_ea-18g across three taskforces (Squadron1,6 / Squadron2,6 / Squadron2,8 / Squadron3,4 …) and usn_fa-18f_blk3 across four (up to Squadron1–5 at 6–8 aircraft each); both airframes mount usn_tank_610_f-18. Because all three versions carry the same Fuel=1800, the aircraft behave identically whichever mod wins.


**Recommendation** — No change needed for this file. Worth knowing for the wider prune, though: 3426791311 is catalogued deprecated ("Integrated into Modern US Navy") yet at rank 28 it also outranks 3737267013 on usn_fa-18e.ini, usn_fa-18f.ini, usn_ea-18g.ini and their _squadrons companions. If you eventually unsubscribe it, this tank file self-heals — 3737267013's copy takes over and points at its own assets — so the tank is not a reason to keep the deprecated mod.


*Sampled: All three copies read in full and diffed pairwise with md5. Also listed the aircraft directories of all three mods and grepped every consumer of the id.*


### 1 ammunition file: ammunition/plaaf_pl-12a.ini (PL-12A / SD-10A active-radar BVR AAM)

**Mods** 3663564190 "Type 003 Aircraft Carrier - PLANS Fujian CV-18" (rank 51) > 3436170138 "Shenyang J-11" (rank 99)  

**Winner** 3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18 · **Risk** none


One line. Both files are 9347 bytes and the diff is a single key: InitialFlightPhaseDuration=0.8 in the winner versus 1.0 in the loser — the unguided straight-line interval immediately after launch, worth two tenths of a second. Warhead, guidance type, seeker (active radar), kinematics, launch envelope and the model block (assets/models/ammunition/pl-5b/pl-12.obj, mesh PL-12, material assets/models/ammunition/textures/pl-12a_mat.ini) are byte-identical.


**Silently lost** — Nothing beyond 0.2 s of initial unguided flight, which slightly favours the winner.


**Risk** — No id collision. No dangling reference: both mods ship assets/models/ammunition/textures/pl-12a_mat.ini, so the material resolves whichever copy wins. SPLIT OWNERSHIP exists but is inert: the loser's plaaf_j-11bg.ini mounts the winner's PL-12A, and since the definitions are the same content the aircraft is unaffected. The winner's own consumers, plan_j-15t.ini and plan_j-15dt.ini, are self-consistent. Worth noting to avoid a false alarm elsewhere: plan_j-15t (3663564190) and plan_j_15t (3413868677, Red Storm Arsenal) are two distinct ids with different filenames — hyphen versus underscore — not a collision.


**Mission** — None. Grep across the collection shows plaaf_pl-12a is carried only by plan_j-15t, plan_j-15dt (3663564190) and plaaf_j-11bg (3436170138), none of which appear in NORTHERN FRONT III FINAL NEWEST. The mission's PLA fighters are plan_j-15 / plan_j-15d (from 3486502935), plan_j_15t (Red Storm Arsenal), plan_j-50 and "plaf_j16a block3", and none of them reference this id.


**Recommendation** — Leave the order alone. There is no argument either way on this file.


*Sampled: Both copies read and diffed in full (identical 9347-byte files). Also checked model/material ownership in both mods and enumerated every consumer of the id, including a grep of the vanilla data tree.*


### 1 ammunition file: ammunition/dts_anaaq-33.ini (AN/AAQ-33 Sniper targeting pod, carried as a Container with two sensor …

**Mods** 3652097318 "B-1B Lancer" (rank 59) > 3636386513 "F-15 EX Eagle II" (rank 71)  

**Winner** 3652097318 B-1B Lancer · **Risk** none


None whatsoever — the two files are byte-for-byte identical. Both declare Type=Container, Mass=208 kg, NumberOfSensorSystems=2 with SensorSystem1 Type=LaserDesignator SystemName=AN/AAQ-33(L) and SensorSystem2 Type=Visual SystemName=AN/AAQ-33(V), the same model block (assets/models/weapon/ammunition/anaaq-33/dts_anaaq-33.obj, mesh pod, material dts_anaaq-33_mat.ini) and the same Glas submodel using aircraft/materials/cockpit_glass_gold. The backing sensor definitions in the two mods' systems/sensors.ini are also identical line for line (LaserDesignator MaxRange=60 nm, NightCapable=True, TargetChannels=1, WeaponChannels=1000, ViewArcs=360.0; Visual with VIDRangeMultiplier=6.0, MaxRangeMultiplier=6.8, LookDownMultiplier=0.8, NightVisionLevel=1), so even the systems/ merge produces no conflict.


**Silently lost** — Nothing. The files are identical.


**Risk** — No id collision. No dangling reference: both mods ship assets/models/weapon/ammunition/anaaq-33/textures/dts_anaaq-33_mat.ini, and both define the [AN/AAQ-33(L)] and [AN/AAQ-33(V)] sensor blocks the pod's SystemName fields point at (as do 3737267013 and 3758320372, all with the same values, so the key-by-key systems merge is conflict-free). No split ownership problem: the consuming aircraft usaf_b-1b_dts.ini (3652097318) and usaf_f-15ex_SEII.ini (3636386513, and its SEST override in /home/user/Seapower-mods/mods-source/_vanilla/SEST_F-15EX_Revamp/aircraft/usaf_f-15ex_SEII.ini) both reference the pod and both get the same definition.


**Mission** — Both consumers are fielded — NORTHERN FRONT III FINAL NEWEST places usaf_b-1b_dts twice as units plus Squadron2,6 and Squadron2,4 assignments, and usaf_f-15ex_SEII four times — so this file is live in the scenario. Because the two versions are identical, the load order has no effect on either aircraft's targeting pod.


**Recommendation** — No action. This cohort is a false positive from a filename-overlap scan — do not spend reorder budget on it.


*Sampled: Both copies read in full, diffed, and md5-compared (c98783fd205d241484d66774eb2e2e0d for both, 1426 bytes each). Also compared the [AN/AAQ-33(L)] and [AN/AAQ-33(V)] sensor blocks in /home/user/Seapower-mods/mods-source/3652097318/systems/sensors.ini (L59–74) …*


### 7 ammunition files: plaaf_ls-500.ini, wp_aa-10a_mi.ini, wp_aa-10b_mi.ini, wp_aa-10c_mi.ini, wp_aa-10d_mi.ini, wp_aa-12_…

**Mods** 3481228992 ChengDu J-10C Vigorous Dragon (load-order line 90) > 3526982088 XIAN JH-7A 歼轰-7A 飞豹 (line 91)  

**Winner** 3481228992 (ChengDu J-10C Vigorous Dragon) · **Risk** none


No differences whatsoever. All 7 files are byte-for-byte identical between the two mods (md5 and byte-size match on every file: plaaf_ls-500 6580B/5ea11813, wp_aa-10a_mi 7307B/c954f09f, wp_aa-10b_mi 7570B/d00ab803, wp_aa-10c_mi 7309B/93c0529d, wp_aa-10d_mi 7574B/486e2f03, wp_aa-12_mi 10009B/11e42218, wp_as-17a 8068B/e0604394). These are a shared Chinese-authored ammo set carried by both mods: plaaf_ls-500 is a 2268 kg LS-500 LGB (Type=Bomb, TargetType=ASuW), wp_aa-12_mi is the R-77 (Mass=175), wp_aa-10c_mi is the R-27R (Mass=350), wp_as-17a is the Kh-31P ARM (Mass=600, TargetType=ASuW). Several carry the authors' own '#REQUIRES STATS REVISION' banner in both copies.


**Silently lost** — Nothing. The losing copies are identical to the winning ones, so the override discards nothing.


**Risk** — No id collision: ammunition ids are the filename, and only one copy ever loads, so there is no duplicate-key registration. No split ownership: each aircraft file (plaaf_j10c.ini, plaaf_jh7a.ini) is uncontested and owned by its own mod. No dangling references: the winner's material paths (assets/models/ammunition/R27R/textures/r27r_mat.ini, .../KH-31/textures/kh-31_mat.ini) resolve inside both mods. Note the repo mirror contains zero .obj files (binaries stripped), so mesh existence could not be verified for any cohort in this report — that is a limitation of the mirror, not evidence of a broken reference.


**Mission** — Mission-live but harmless. NORTHERN FRONT III FINAL NEWEST fields Type=pla_airbase_modern (mods-source/3631042692/land_units/pla_airbase_modern.ini), whose [AirGroup] spawns plaaf_j10c=Default,6 and plaaf_jh7a=Default,8. Those are precisely the two consumers of this ammo set (3481228992/aircraft/plaaf_j10c.ini and 3526982088/aircraft/plaaf_jh7a.ini, each uncontested). Because the files are identi…


**Recommendation** — Leave the order exactly as it is. This cohort is noise, not a conflict — 3481228992 and 3526982088 ship the same shared ammo library and neither has diverged. Any future reorder of these two mods relative to each other is safe with respect to these 7 files. Worth recording so a later audit does not re-open it.


*Sampled: md5/size compared on all 7 files in both mods; read the winner's plaaf_ls-500.ini, wp_aa-12_mi.ini, wp_aa-10c_mi.ini and wp_as-17a.ini in full detail (header, mass, type, guidance).*


### ammunition/wp_kab-500kr.ini

**Mods** 3417446309 MIG-29 Family (line 41) > 3451166840 Su-25 Frogfoot (line 117)  

**Winner** 3417446309 (MIG-29 Family) · **Risk** none


None. The two files are byte-identical (8566 bytes, md5 72055c2642 in both). The shared definition is the KAB-500Kr TV-guided bomb: Type=Missile, TargetType=ASuW, Mass=520 kg, WarheadType=0 Power=67, GuidanceType=6 (TV-Homing), MaxLaunchRange=15 nm.


**Silently lost** — Nothing — the losing copy is identical.


**Risk** — No id collision (single registration from one filename), no split ownership (this is a standalone ammunition file with no _squadrons or _variants companion), no dangling reference concerns raised by the diff since there is no diff. Note that this file is shared verbatim across several unrelated Russian-aircraft mods, so its load-order position is genuinely irrelevant no matter which of them rises or falls.


**Mission** — None. This ammo id has seven consumers across the collection (3451166840/aircraft/wp_su-25sm3.ini, 3417446309's wp_mig-29m_915/wp_mig-29m2_967/wp_mig-29m_961, 3716049886's wp_su-24sm3 and wp_su-24m2, 3503594612/aircraft/wp_su-57.ini, 3659742367/aircraft/wp_mig-35.ini) and none of those airframes appears in NORTHERN FRONT III FINAL NEWEST — the mission's only Russian fast jet is Type=wp_su-35s, wh…


**Recommendation** — No action. Both mods ship the same upstream KAB-500Kr definition, so the override is a no-op and reordering 3417446309 against 3451166840 for any other reason cannot break this file. Record it as resolved so it does not resurface in the next conflict scan.


*Sampled: Byte/md5 comparison of both copies plus a key-stat read (type, mass, warhead power, guidance type, launch range) of the winner's file.*


### ammunition/usn_gbu-31_v1.ini

**Mods** 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (line 35) > 3508978375 [DEPRECATED] Lockheed Martin F-35C (line 82)  

**Winner** 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) · **Risk** none


None. Byte-identical in both mods (6890 bytes, md5 cb9616870b). The shared definition is the GBU-31(V)1/B JDAM on a Mk 84 body: Type=Missile, TargetType=ASuW, LandAttackCapability=Installation, CanNotAttackTypes=Vessel,Submarine, Mass=961 kg, AmmoPoints=1000, WarheadType=0 Power=97, GuidanceType=0 (inertial/GPS, no seeker), MaxLaunchRange=13 nm.


**Silently lost** — Nothing — the losing copy is identical.


**Risk** — No id collision, no split ownership, no dangling references. Two secondary observations that are collection hygiene rather than defects: (1) both contesting mods are titled [DEPRECATED] in the catalog and both have had their aircraft files superseded by SEST_Integration, so this whole cohort is a conflict between two mods whose relevant content no longer loads — a candidate for the cleanup list rather than the load-order list; (2) the file is orphaned, meaning any future audit that flags it as a conflict is flagging something with no gameplay surface. Neither is a reason to change anything today.


**Mission** — None, and for a second independent reason worth recording. The only consumers of this id anywhere are 3426791311/aircraft/usn_fa-18f.ini, 3426791311/aircraft/usn_fa-18f_blk3.ini and 3508978375/aircraft/usn_f-35c.ini — and every one of those aircraft files is itself overridden by SEST_Integration at the top of the load order. I checked the SEST versions directly: integration/dist/SEST_Integration/…


**Recommendation** — No action on load order. The files are identical, so the override is a no-op, and even if they differed the winner would never be mounted by any enabled aircraft. If the user is pruning the collection, note that 3426791311 and 3508978375 are both marked [DEPRECATED] and both have their aircraft overridden by SEST_Integration — that is a disable-candidate question for the cleanup pass, not an interoperability fix, and it should be decided deliberately rather than as a side effect of this report.


*Sampled: Byte/md5 comparison of both copies, key-stat read of the winner's file, and a full consumer trace across the collection including the SEST packs.*


### ammunition/pla_cal_apfsds_30mm.ini

**Mods** 3733719765 PLA Land Unit Pack (line 15) > 3775128499 Modern PLAN Systems (line 19)  

**Winner** 3733719765 (PLA Land Unit Pack) · **Risk** none


None. Byte-identical in both mods (903 bytes, md5 d301967483). The shared definition is a 30 mm APFSDS round for Chinese CIWS/SPAAG mounts: Type=Projectile, TargetType=AAW with SecondaryTargetType=ASuW, MuzzleVelocity=1000 m/s, MaxRange=5000 m, CircularErrorProbable=21 m at max range, WarheadData Power=1, ImpactSize=Tiny, Penetration=Minor, HitAirExplosionClass=SmallFlakExplosions.


**Silently lost** — Nothing — the losing copy is identical.


**Risk** — No id collision — one filename, one registration. No split ownership: this is a standalone ammunition file, and the vessel files that consume it (plan_type_055_2026.ini and the rest) are owned by 3775128499 with no competing copies in the contested set. No dangling references. This is the reassuring case: a land-unit mod and a naval-systems mod by different authors converging on the same shared ammunition definition, which is what you want when two packs from the same modding ecosystem overlap. The load-order gap between them (lines 15 and 19) is irrelevant for this file.


**Mission** — Mission-live and heavily so, but harmless because the versions match. This round is the CIWS ammunition for 21 warship classes in 3775128499 (Modern PLAN Systems), five of which the mission fields directly: Type=plan_type_055_2026, plan_type_052d_p3, plan_type_052d_p4, plan_type_054a_p5 and plan_type_051b_2017. It is simultaneously the gun ammunition for four land units in the winning mod (pla_ld…


**Recommendation** — No action. Worth flagging positively in the report: because the two mods agree byte-for-byte here, the relative order of 3733719765 and 3775128499 can be changed freely for other reasons without any risk to the mission's PLAN escort CIWS. That is a useful degree of freedom to know about, since Modern PLAN Systems is described in the catalog as the Chinese-fleet analogue of Euromod Main and is likely to be reordered in future passes.


*Sampled: Byte/md5 comparison of both copies, full read of the 903-byte file, and a complete consumer trace across both mods.*


### ammunition/usn_agm-88e.ini

**Mods** 3426791311 [DEPRECATED] Boeing F/A-18E/F Super Hornet (rank 28) > 3737267013 United States Naval Aviation (rank 52)  

**Winner** 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) · **Risk** none


Effectively identical. The diff is two lines, both cosmetic asset plumbing: ResourcesFolder=assets/models/weapon/ammunition/agm-88/ vs assets/models/ammunition/agm-88/, and ResourcesMaterial=usaf_agm-88e_mat.ini vs usn_agm-88e_mat.ini. Every warhead, guidance, seeker, kinematic and ECCM value in the file is byte-for-byte the same. Both material files exist inside their own mods (3426791311/assets/models/weapon/ammunition/agm-88/usaf_agm-88e_mat.ini and 3737267013/assets/models/ammunition/agm-88/usn_agm-88e_mat.ini), so both would have resolved correctly.


**Silently lost** — Nothing. The loser's copy contains no content the winner lacks.


**Risk** — No id collision, no split ownership, no dangling references — this contest has no gameplay consequence. Worth recording, though, that usn_agm-88e is nearly orphaned under the current order: its only consumers are 3426791311's aircraft, and of those, usn_fa-18e.ini, usn_fa-18f.ini, usn_ea-18g.ini and usn_fa-18e_late.ini are all overridden by 3606774881 (rank 10), whose versions carry usn_agm-88g (AARGM-ER) instead. The one live consumer left is usn_ea-18g_2020s.ini, which 3426791311 owns uncontested. So the AGM-88E still exists in the build, but only on a single Growler variant.


**Mission** — None. The active mission fields no AARGM shooter that uses this id.


**Recommendation** — No change, and no action needed. Whichever of these two mods wins produces the same missile. If you are pruning the collection, note that the '[DEPRECATED]' label on 3426791311 is accurate for its aircraft — 3606774881 outranks it on every Super Hornet and Growler file except usn_ea-18g_2020s — but do not disable it without first checking that usn_ea-18g_2020s is not wanted, since removing it would take this ammunition's last live consumer with it.


*Sampled: Full normalized diff of both copies, verification that both mods' referenced material inis exist, and a trace of every consumer of the id together with which mod actually wins each consuming aircraft file.*


### ammunition/wp_cal_12.7mm.ini

**Mods** 3733719765 PLA Land Unit Pack (rank 8) > 3465256032 Mi-8 T/TV (rank 91)  

**Winner** 3733719765 (PLA Land Unit Pack) · **Risk** none


None whatsoever. Both copies hash to 42a4bfee725d221b288f9466562a623b — byte-for-byte identical, same line endings, no whitespace drift. The shared content is a Projectile with TargetType=AAW / SecondaryTargetType=ASuW / CanNotAttackTypes=Missile, MuzzleVelocity 860 m/s, MaxRange 1800 m, CircularErrorProbable 38 m, Power 0.1, ImpactSize Tiny, Penetration Minor, DecalClass GunImpacts.


**Silently lost** — Nothing at all. The override discards an exact duplicate.


**Risk** — No id collision, no split ownership, no dangling references, no possible behavioural difference. There is no version of the load order in which this file matters. This cohort is noise in the conflict report and can be filtered out of future passes.


**Mission** — None. Consumers are 3733719765's own pla_mbt_ztz-99a, pla_mbt_ztz-96, pla_td_ptz-89 and pla_spa_plz-83, plus 3465256032/aircraft/wp_mi-8tv.ini and 3513571010/aircraft/wp_mi-24v.ini. The active mission fields none of these — its ground units are pla_apc_zbl-08, wp_mbt_t-55m, wp_car_ural_command, wp_aaa_ural_zu-23 and assorted TELs and SAM sites, and it fields no Mi-8 or Mi-24.


**Recommendation** — No change. This is two mods shipping the identical vanilla-style 12.7 mm projectile definition because each needed it present; the override is a no-op. If you maintain an ignore-list for the conflict tooling, byte-identical cohorts like this one belong on it so genuine conflicts stay visible.


*Sampled: Both copies read in full (25 lines each) and md5-compared.*


### ammunition/usn_mk-83.ini, usn_mk-84.ini (2 files, 5 contesting mods)

**Mods** 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) > 3737267013 (United States Naval Aviation) > 3758320372 (F-16C Fighting Falcon (modern)) > 3508978375 ([DEPRECATED] Lockheed Martin F-35C) > 3514484654 (RAAF F-35A Lighting II)  

**Winner** 3426791311 ([DEPRECATED] Boeing F/A-18E/F Super Hornet) · **Risk** none


Four of the five mods ship byte-identical copies of both files: 3426791311, 3758320372, 3508978375, 3514484654 (usn_mk-83 md5 f50ee66ddaf7a0d3df856a3c81399eff, usn_mk-84 md5 ec1cec8bc465d7d7e6e888c661675305). 3737267013 differs from them in exactly ONE line per file, and it is a path, not a stat: ResourcesFolder=assets/models/ammunition/mk83/ (and .../mk84/) instead of the winner's assets/models/weapon/ammunition/mk83/ (and .../mk84/). Mass, warhead type and power, impact size, penetration, ballistics, CEP, AssetBundle names, submodel count and particle effects are line-for-line identical. Both paths resolve: mods-source/3426791311/assets/models/weapon/ammunition/mk83/mk-83_mat.ini and mk84/mk-84_mat.ini exist, and so do mods-source/3737267013/assets/models/ammunition/mk83/mk-83_mat.ini and mk84/mk-84_mat.ini.


**Silently lost** — Nothing functional. The only thing discarded is 3737267013's routing of the bomb model to its own asset folder rather than the Super Hornet mod's — both folders contain the same-named material and both mods are enabled.


**Risk** — No id collision (no id key; filename is identity). No split ownership within this file pair. Adjacent split-ownership defect involving the same mod set, outside this cohort but flagged because these mods are the contestants: usn_fa-18e.ini and usn_ea-18g.ini are won by 3606774881 (line 17) while usn_fa-18e_squadrons.ini and usn_ea-18g_squadrons.ini are won by 3430135740 (line 22); usn_cvn_nimitz_2000s.ini and its _variants.ini are both won by 3430135740, which is coherent. None of those units are fielded in NORTHERN FRONT III FINAL NEWEST, so the exposure is low, but they belong to whoever audits the Hornet/Nimitz cohorts.


**Mission** — None in practice. usn_mk-84 is referenced by mods-source/3413868677/aircraft/usaf_b-52o.ini (4 airframes) and mods-source/3652097318/aircraft/usaf_b-1b_dts.ini (2 airframes), but neither flies a Mk-84 loadout: the B-52Os fly LoadoutVariant=Strike183 (the ARRW loadout added by the top-of-order SEST_Integration override of usaf_b-52o.ini) and the B-1Bs fly AntiShipHeavy, which is 8x dts_agm-158c-3.…


**Recommendation** — No change. The winner and three of the four losers are the same bytes, and the fourth differs only in which enabled mod supplies the model. Do not reorder to 'fix' this — there is nothing to fix. Worth noting for collection hygiene rather than load order: a DEPRECATED mod (3426791311, line 35) is sitting above its active successor 3737267013 (line 59), but for these two files that is harmless, and if 3426791311 is ever unsubscribed the files fall through to 3737267013, whose asset path is self-consistent. So this cohort is not a blocker for retiring the deprecated Super Hornet mod.


*Sampled: All 10 copies md5-compared. Full diff of usn_mk-83.ini and usn_mk-84.ini, winner vs 3737267013 (the only mod whose copies differ). Directory listings of both mods' mk83/ and mk84/ material folders.*


### ammunition/pla_yj-83.ini (1 file)

**Mods** 3594891803 (PLAN Submarines) > 3486502935 (Type 003 Fujian / Type 004 CVN Aircraft Carriers)  

**Winner** 3594891803 (PLAN Submarines) · **Risk** none


None. The two copies are byte-identical, and the language entries are identical too — both read 'pla_yj-83=YJ-83,Eagle Strike,ASM,The YJ-83 is a medium-range anti-ship cruise missile... Mach 1.4 supersonic terminal attack velocity.'


**Silently lost** — Nothing. Same bytes on both sides, same encyclopedia text.


**Risk** — No id collision (no id key in the file). No split ownership: pla_yj-83.ini is the only file 3594891803 and 3486502935 contest across all whole-file-override directories.


**Mission** — The weapon is fielded but the contest is inert. mods-source/3486502935/aircraft/plan_j-15d.ini x8 fly LoadoutVariant=AntiShip, whose block carries pla_yj-83 on Station28/Station29 — 16 YJ-83 rounds in the mission. Because the two copies are identical, the override changes nothing about them.


**Recommendation** — No change. Note for context rather than action: it is slightly odd that a submarine mod (3594891803) owns the air-launched YJ-83 that the carrier air wing fires, but since the file is identical to the carrier mod's own copy, ownership is immaterial. If 3594891803 is ever disabled, the file falls through to 3486502935 unchanged.


*Sampled: Both copies md5-compared (identical: 81dfd0066649d707499d5c6d4c5c66b8). Read both mods' language_en/ammunition_names.ini pla_yj-83 entries and the consuming loadout block in mods-source/3486502935/aircraft/plan_j-15d.ini.*


### ammunition/su_rgb-12.ini (1 file)

**Mods** 3438479626 (1143.5 Kuznetsov) > 3774859959 (PLAN Type 001 Aircraft Carrier Liaoning)  

**Winner** 3438479626 (1143.5 Kuznetsov) · **Risk** none


Comments only. The winner carries a 3-line '# REQUIRES STATS REVISION' banner the loser lacks, and their descriptive comments differ: the winner says '# RBU-6000' and '# Users:' where the loser says '# Generic RGB-12-class anti-submarine rocket used by the RBU-12000 launchers.' The winner's file also lacks a trailing newline. Every substantive line is identical, down to Scale=0.005,0.005,0.04291637.


**Silently lost** — Nothing functional — the loser's copy differs only in comment text. The one thing that does change hands is the display name, and that happens through the language merge rather than the override: the winner mod (line 28) publishes 'su_rgb-12=RBU-12000,Smerch-2,ASW,The RBU-12000 Smerch-2 is a Soviet 300mm anti-submarine rocket launcher with a range of approximately 13,000 yards.' and outranks the Liaoning mod (line 48), whose entry reads 'su_rgb-12=RGB-12,anti-submarine rocket,RGB-12 anti-submarine rocket for the RBU-12000 launcher.' So the round is labelled with its launcher's name rather than its own.


**Risk** — No id collision (no id key in the file). No split ownership: su_rgb-12.ini is the only file 3438479626 and 3774859959 contest across every whole-file-override directory, so both carriers keep their own vessel and _variants files intact. No dangling references — both consuming vessel files reference su_rgb-12, which the winner defines.


**Mission** — Fielded but inert. NORTHERN FRONT III FINAL NEWEST fields ru_cv_varyag, and mods-source/3438479626/vessels/ru_cv_varyag.ini lines 1753 and 1760 set Ammunition1=su_rgb-12 for its RBU mounts. Since the two copies are functionally identical, the override changes nothing. The Liaoning's own consumer (mods-source/3774859959/vessels/plan_type_001.ini lines 744 and 751, same Ammunition1=su_rgb-12) is eq…


**Recommendation** — No change. Both carriers' RBU mounts reference the same id and get the same ballistics either way. If you care about the encyclopedia text, note two small inconsistencies in the winning mod: its own inline comment says '# RBU-6000' while its language string says 'RBU-12000 Smerch-2', and the string names the launcher rather than the rocket. Both are one-line language/comment fixes, not load-order matters.


*Sampled: Both copies diffed in full (171 vs 167 lines). Read both consumers — mods-source/3438479626/vessels/ru_cv_varyag.ini and mods-source/3774859959/vessels/plan_type_001.ini — and both mods' language_en/ammunition_names.ini entries.*


### ammunition/plaaf_ld-8a_LQS.ini, plaaf_ls-6_500_LQS.ini, plaaf_pl-10_LQS.ini, plaaf_pl-16_LQS.ini, plaaf_pl-17_LQS.ini, …

**Mods** 3591563716 J-20 (歼-20 威龙) > 3670643788 Shenyang J-50 (沈阳航空工业 歼-50)  

**Winner** 3591563716 (J-20) — but the win is meaningless, see below · **Risk** none


NOTHING. All six files are byte-identical between the two mods (diff exit 0 on every one). Both mods are by the same author (the _LQS suffix is the author tag) and ship the same shared PLAAF weapon set. The J-20 file (plaaf_j-20a.ini) references plaaf_ld-8a_LQS, plaaf_pl-10_LQS, plaaf_pl-15_LQS, plaaf_pl-16_LQS, plaaf_pl-17_LQS, plaaf_tl-20_LQS; the J-50 file (plan_j-50.ini) references plaaf_ld-8a_LQS, plaaf_pl-10_LQS, plaaf_pl-16_LQS, plaaf_pl-17_LQS, plaaf_tl-20_LQS, plaaf_yj-21_LQS. The contested six are exactly the intersection; each mod's unique weapon (pl-15_LQS for the J-20, yj-21_LQS for the J-50) is uncontested and loads from its own mod.


**Silently lost** — Nothing. The losing copies are identical to the winning ones, so no content is lost.


**Risk** — No id collision: 3591563716 ships aircraft/plaaf_j-20a.ini + plaaf_j-20a_squadrons.ini, 3670643788 ships aircraft/plan_j-50.ini + plan_j-50_squadrons.ini — disjoint filenames, so no two enabled mods register the same unit id here. No split ownership: each mod owns both its <id>.ini and its <id>_squadrons.ini. No dangling references: every _LQS ammunition id referenced by either aircraft is defined by one of the two mods, both enabled.


**Mission** — The mission (NORTHERN FRONT III FINAL) fields plan_j-50 three times (Type=plan_j-50 ×3). Because the contested files are identical, the mission's J-50s get exactly the ordnance their author shipped — the load order makes no difference to them.


**Recommendation** — Leave the order alone. This cohort is pure noise in the conflict report and can be suppressed/whitelisted so it stops competing for attention with real conflicts.


*Sampled: All 6 files diffed byte-for-byte between both mods. Also read mods-source/3591563716/aircraft/plaaf_j-20a.ini and mods-source/3670643788/aircraft/plan_j-50.ini ammunition references, and listed both mods' aircraft/ directories.*


### ammunition/wp_sa-n-11.ini, ammunition/wp_sa-n-20.ini (2)

**Mods** 3406985435 Kirov-class (Pyotr Velikiy Upgrade) (order line 39) > 3468260539 Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV) (52)  

**Winner** 3406985435 Kirov-class (Pyotr Velikiy Upgrade) — but the choice is immaterial, see below. · **Risk** none


Nothing differs. Both files are byte-identical between the two mods: wp_sa-n-11.ini is 192 lines with md5 0ed9b318... in both, wp_sa-n-20.ini is 184 lines with md5 2efc1767... in both. A normalised diff (comments and blanks stripped) produces zero output for each pair. The submarine pack is simply carrying a verbatim copy of the Kirov pack's Kashtan (SA-N-11) and Fort-M / S-300F (SA-N-20) definitions.


**Silently lost** — Nothing. The loser's copies are identical to the winner's, so the override discards duplicate bytes and no content at all.


**Risk** — No id collision — same filenames, and neither mod registers a duplicate unit id (the catalog's VERIFIED note that 3406985435 adds only the additive wp_rkr_kirov_improved holds; 3468260539 ships submarine hulls under different ids). No split ownership: vessels/wp_rkr_kirov_improved.ini and wp_rkr_kirov_improved_variants.ini are both owned solely by 3406985435, so the mission's Kirov unit and its variants come from one mod. No dangling references. The only mild oddity is that 3468260539 ships two surface-ship SAM files that none of its own submarines use — dead weight, harmless.


**Mission** — The mission fields wp_rkr_kirov_improved (from 3406985435), which is the sole consumer of both ids anywhere in the collection — no vessel or land unit in 3468260539 or any other enabled mod references wp_sa-n-11 or wp_sa-n-20. Because the files are identical, the mission's Kirov gets exactly the same Kashtan and Fort-M performance under either load order. Zero effect.


**Recommendation** — No action. This cohort is a false positive from filename-level conflict detection: the two mods ship the same bytes. It is worth recording in the interoperability doc as a known-benign overlap so a future pass does not re-investigate it, and so nobody 'fixes' it by reordering 3468260539 upward — that would move a submarine pack above the Kirov for no gain and would need re-checking against everything between order lines 39 and 52.


*Sampled: Both files from both mods: mods-source/{3406985435,3468260539}/ammunition/wp_sa-n-11.ini and .../wp_sa-n-20.ini — md5-compared and normalised-diffed in full. Also grepped every vessels/ and land_units/ file in the collection for consumers of the two ids.*


### ammunition/plan_726_4_chaff.ini (1)

**Mods** 3774859959 PLAN Type 001 Aircraft Carrier Liaoning (order line 48) > 3413868677 Red Storm Arsenal (139)  

**Winner** 3774859959 PLAN Type 001 Aircraft Carrier Liaoning — immaterial, the two are functionally identical. · **Risk** none


No functional difference whatsoever. A normalised diff (comments and blank lines stripped) is empty; the only variance is that Red Storm Arsenal's copy carries the original explanatory comments and a trailing newline (13 lines vs 12). Both define: [General] Type=Chaff, TargetType=AAW; [ECM] SpoofChance=0.6, DefensiveEffectTime=90, ReactionRange=5; [SensorData] IRSignature=VeryLarge, RCS=VeryLarge. Identical values on every key.


**Silently lost** — Nothing but comments. The Type 001 mod's copy has the same six parameter values as Red Storm Arsenal's, so the override costs the player nothing.


**Risk** — No id collision, no split ownership (vessels/plan_type_001.ini and plan_type_001_variants.ini are both owned by 3774859959 alone; the Red Storm destroyers are owned by 3413868677 alone), no dangling references. Red Storm Arsenal's four destroyers keep working under the winner's identical definition. Note that the related id 071_726_4_chaff (3774572038) is a separate file and not part of this contest.


**Mission** — None. The id is consumed by mods-source/3774859959/vessels/plan_type_001.ini (Liaoning) and by four Red Storm Arsenal destroyers — plan_ddg_type_052C_rsa, plan_ddg_type_052D_rsa, plan_ddg_type_055_rsa, plan_ddg_type_055_late_rsa. The mission fields none of those: its PLAN surface units are plan_type_051b_2017, plan_type_052d_p3/p4, plan_type_054a_p5, plan_type_055_2026, plan_lpd_type_071 and the …


**Recommendation** — No action, and worth marking as benign in docs/conflicts-and-load-order.md. Red Storm Arsenal sits at the bottom of the order (line 139) precisely so its 1062-file library acts as a filler layer, and this is that design working as intended: a smaller, more specific mod supplies the definition and the fallback library is harmlessly shadowed with the same bytes. Do not promote 3413868677 to 'fix' this — it would have to jump 90 positions and would displace a large number of genuinely-preferred definitions.


*Sampled: Both files in full: mods-source/3774859959/ammunition/plan_726_4_chaff.ini and mods-source/3413868677/ammunition/plan_726_4_chaff.ini — printed side by side and normalised-diffed. Also grepped every vessels/ and aircraft/ file for consumers of the id.*


### ammunition/plaaf_ls-6_500.ini (1 file)

**Mods** 3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18 (line 58) > 3506979898 Shenyang J-16A (line 87) > 3481228992 ChengDu J-10C Vigorous Dragon (line 90) > 3526982088 XIAN JH-7A (line 91) > 3436170138 Shenyang J-11 (line 106) > 3433577445 Shenyang J-8 (line 108)  

**Winner** 3663564190 Type 003 Aircraft Carrier - PLANS Fujian CV-18 · **Risk** none


Four of the six copies are BYTE-IDENTICAL (md5 a88d051b): the winner, J-16A, J-11 and J-8. Only J-10C and JH-7A carry a different, older variant (md5 4e98f9e4, 154 lines vs 158), which differs in five things: it lacks AmmoPoints=750 and AirLaunched=True (so no supply-system pricing and no launch-altitude entry in the encyclopedia), MaxLoftAlt=0 instead of -50, no TerminalDiveDistance=3.5, and smaller impact effects - HitGroundExplosionClass=SMediumGroundHitExplosions (note the typo, 'SMedium' is not a valid class name), HitDefaultExplosionClass=MediumMissileExplosions and HitWaterSplashClass=SmallWaterSplashes, where the winner has LargeGroundHitExplosions / LargeWaterSplashes.


**Silently lost** — Nothing of value. The two divergent copies (J-10C, JH-7A) lose only an older effects profile and a malformed explosion-class name; the three other losers are byte-identical to the winner, so their loss is a no-op.


**Risk** — No id collision (same-filename override of a single ammunition id), no split ownership (there is no plaaf_ls-6_500 companion file), no dangling references. The only thing worth recording is that six separate enabled mods each carry a private copy of this shared PLA weapon - a maintenance hazard, not a runtime one: if one author updates the LS-6 the change will only take effect if that mod happens to sit highest. The J-10C/JH-7A variant's 'SMediumGroundHitExplosions' would be an invalid effects-class reference if it ever won, which is one more reason the current order is the safe one.


**Mission** — Yes, but with zero consequence. NORTHERN FRONT III FINAL NEWEST fields six plaf_j16a (from 3506979898, whose copy is byte-identical to the winner - Station18/19/20/28/29=plaaf_ls-6_500) and three plan_j-50 (3670643788), which also loads LS-6 500. Because the winning file and the mission supplier's file are the same bytes, the load order makes no observable difference to the mission.


**Recommendation** — No change. The winner is the newest of the two variants in circulation and is bit-for-bit what the mission's own J-16A supplier ships, so the outcome is identical regardless. If you ever want to consolidate, the right move is a single SEST-owned plaaf_ls-6_500.ini above all six, not a reorder among them.


*Sampled: All six copies compared by md5 and line count; the winner fully diffed against 3506979898 (J-16A, the mission's own supplier) and against 3481228992 (J-10C, the divergent variant). Also checked consumers: plaf_j16a.ini, plan_j-50.ini, plaaf_j10c.ini.*


### ammunition/su_kab-1500kr.ini (1 file)

**Mods** 3434072450 Sukhoi Flanker Family (苏霍伊侧卫家族) (line 120) > 3509329205 TU-160 Blackjack (line 124)  

**Winner** 3434072450 Sukhoi Flanker Family · **Risk** none


Effectively identical. The complete diff is one line: the winner writes 'AmmoPoints=2500' followed by the standard trailing comment and a blank line, the Tu-160 copy writes 'AmmoPoints=2500' with no comment and no blank line. Every functional value - warhead, guidance, seeker, kinematics, launch envelope, model and effects references - is the same in both files.


**Silently lost** — Nothing. The losing copy contains no content the winner lacks.


**Risk** — No id collision, no split ownership, no dangling references. This is a duplicate-file cohort with a whitespace-only delta - the single most benign class of override in the collection. The only note for the record: two Russian aircraft mods each carrying a private copy of a shared Russian guided bomb means a future update by either author only takes effect if that mod is the higher one.


**Mission** — None from this contest. The mission fields six wp_su-35s (supplied by the winner, 3434072450) and six wp_tu-95ms, but the Tu-160 itself is not fielded, and in any case the two KAB-1500KR files are functionally the same bytes - the load order cannot change anything the player sees.


**Recommendation** — No change, and no further attention needed. If you are pruning duplicate ammunition to shrink the override surface, this is a safe candidate to consolidate into a single owner - but there is no behavioural reason to touch it.


*Sampled: Both copies read and fully diffed (158 vs 157 lines).*


### ammunition/fr_cal_20mm.ini (1 file)

**Mods** 3629144864 Euromod - Main Pack (line 18, WINS) > 3567256221 Charles De Gaulle & Modern French Navy (line 30) > 3567228449 French Helicopter Package (line 84)  

**Winner** 3629144864 (Euromod - Main Pack) — but the choice is immaterial · **Risk** none


None. All three files are byte-identical — md5 0804e63951 in every mod, 23 lines each, and both diffs return empty. This is one mod's 20 mm cannon round vendored unchanged into two sibling French packs by the same author group.


**Silently lost** — Nothing. There is no content in either losing copy that the winner does not have, byte for byte.


**Risk** — No id collision, no split ownership, no dangling reference, and no possible behavioural difference regardless of load order. This cohort can be dropped from any future conflict report as noise — it is the signature of a mod family shipping a shared dependency file rather than a real contest.


**Mission** — The mission fields fr_ffg_lafayette_version_opv_modernized, which is French and may well use this round, but since all three copies are identical the load order cannot change what it fires.


**Recommendation** — No action. Leave the order exactly as it is; any reordering of these three mods for other reasons can ignore this file entirely.


*Sampled: All three copies: md5 compared and both diffs run in full (comment-stripped).*


### ammunition/usn_mk182_chaff.ini (1)

**Mods** 3629144864 Euromod - Main Pack (line 18) > 3444379330 Euromod - Modern Dutch navy (line 33)  

**Winner** 3629144864 Euromod - Main Pack · **Risk** none


None. The two files are byte-identical, 17 lines, same checksum. This is a shared-dependency file the addon carries a redundant copy of, exactly as the catalog's dependency note predicts (Euromod - Modern Dutch navy declares euromod-main as a requirement).


**Silently lost** — Nothing. The loser's copy is bit-for-bit the same file.


**Risk** — No id collision, no split ownership, no dangling reference, nothing lost. The only thing worth recording is that the correct dependency ordering (Euromod Main above its addons) is already in force at lines 18 and 33, which matches the catalog's recommendation for the Euromod family.


**Mission** — The id is live in the mission — rnn_ddg_zeven_mlu (Euromod Dutch, fielded) and ran_ddg_hobart (SEST_RAN_Fleet, fielded) both reference usn_mk182_chaff, as do rnn_ffg_Van_Galen, rnn_ddg_zeven, ae_ffg_alvaro_bazan and ae_opv_meteoro. But since both copies are identical, the override changes nothing for any of them.


**Recommendation** — No action. Do not spend load-order moves on this pair for this file. Keep Euromod - Main Pack above all Euromod addons for the files where it does matter.


*Sampled: Both copies read and compared by diff and md5 (691824c0e4028cfe1bf116903a0cdf82 in both). Also grepped the collection for units that reference the id.*


### ammunition/fr_am-39_Block2.ini (1)

**Mods** 3567256221 Charles De Gaulle & Modern French Navy Pack (line 30) > 3504168760 Dassault Rafale (line 73) > 3567228449 French Helicopter Package (line 84)  

**Winner** 3567256221 Charles De Gaulle & Modern French Navy Pack (WIP) · **Risk** none


None whatsoever. Three byte-identical copies of the same 184-line Exocet AM39 Block 2 file, shipped redundantly by three French mods that share an author lineage.


**Silently lost** — Nothing. All three copies are the same file.


**Risk** — No id collision, no split ownership, no dangling reference. Worth noting only that the three-way redundancy means this file survives any one of the three mods being removed — including 3567256221, which the catalog marks WIP. The Rafale mod, which is the only actual consumer, ships its own copy, so the weapon cannot be orphaned.


**Mission** — None. The only unit files referencing fr_am-39_Block2 are the six Rafale variants in 3504168760 (fr_rafale_b/b_l/c/c_l/m/m_l), and NORTHERN FRONT III FINAL NEWEST fields no Rafale. The one French unit in the mission, fr_ffg_lafayette_version_opv_modernized (from the winner mod, 3567256221), contains zero references to any am-39.


**Recommendation** — No action. Do not reorder these three mods on account of this file; if you ever reorder the French pack for another reason, this cohort imposes no constraint.


*Sampled: All three copies read and compared by diff and md5 — all three hash to 3212ec7685c58ff093442158ee3f2501, 184 lines. Also grepped the collection for units referencing the id and checked the mission's French unit.*

