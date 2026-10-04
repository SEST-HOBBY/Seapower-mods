# Mod tiers — every active mod by tier

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 180 active subscriptions plus the SEST Integration Pack (20 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

This is a tier grouping, NOT the load order. The canonical Mod Manager order is `data/load-order.tokens.txt` (181 entries: SEST_Integration plus the 180 Workshop mods); the pack ships it as LOAD-ORDER.txt and SETUP writes it. Where the numbering below differs, the canonical order wins (for example, its last four are **Sea Venom - Aquilon**, **EUROMOD-Armada de Chile**, **Philippines: The Luzon Line** and **RE-power: the resupply mod**).

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are listed alphabetically here — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **Better TacMap** — code mod — UI
5. **Coordinated Strike Tool** — code mod — time-on-target planner (F8); no game data, one _info.ini
6. **Automatic SAR** — code mod — right-click SAR; the campaign pays for survivors
7. **Identify Expanded** — code mod — identification and challenge orders; reads its own ini
8. **Operation STEADFAST LANTERN** — third-party campaign; its nation-flag table (ui/Default/Settings_UI_General.ini) must outrank every other copy, and it is a strict superset of the previous winner's

## Tier 2 — weapon/system databases (this exact order)

9. **SAM Pack** — author: "top of TOE"
10. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
11. **Dingtools Weapon Pack** — author: "above any of my mods"
12. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
13. **Euromod - Main Pack** — above all Euromod addons
14. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

15. **F-35C Lightning II Alt. Loadouts** — KEEP — SEST F-35C JATM is built from it and loadouts hang a round it ships; must stay below the SEST pack
16. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
17. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
18. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
19. **Flight Deck Ops** — above carriers
20. **Air Deck Operations Upgrade - Nimitz (2000s)** — KEEP — the campaigns place its carrier (Flight Deck Day)
21. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

22. 1143.5 Kuznetsov
23. [DEPRECATED] Anzac Class Frigate — *KEEP — the only source of the RAN Anzac hull the campaigns use; since 20 Sep 2026 SEST RAN Fleet patches this mod's own vessels/ran_ffh_anzac.ini, so its real ASMD hull is what loads*
24. Auxilliary Merchant Pack
25. Charles De Gaulle & Modern French Navy Pack (WIP)
26. Chinese Navy (PLAN)
27. Clemenceau-class Aircraft Carrier
28. Euromod - Cold War Spanish Navy
29. Euromod - Modern British Navy
30. Euromod - Modern Dutch navy
31. Euromod - Modern German Navy
32. Euromod - Modern Italian Navy
33. Euromod - Modern Japanese Maritime Self Defence Force
34. Euromod - Modern Nordic Navy
35. Euromod - Modern Spanish Navy
36. EUROMOD-Armada de Chile — *canonical order puts it below RADF and far below <<E-3G>> ([AN/APY-2])*
37. Euromod-Brazilian Armed Forces(2000)
38. Euromod-India-Navy
39. Euromod-Philippine-Navy
40. Euromod-South Korea Navy
41. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
42. Italian Navy Mod
43. Kirov-class (Pyotr Velikiy Upgrade)
44. Merchants Expanded
45. Modern US Navy
46. Mogami-class Frigate
47. Moloti's Armed Merchantmen — *beside Merchants Expanded; no collision with anything, position free*
48. Nimitz Expanded
49. Philippines: The Luzon Line — *canonical order puts it below RADF and below KC-135 ([MK22])*
50. PLAN Submarines
51. PLAN Type 001 Aircraft Carrier Liaoning
52. PLAN Type 071 Amphibious Transport Dock
53. RE-power: the resupply mod — *canonical order puts it last, below the Luzon Line, with which it shares no files*
54. Royal Australian Defence Forces — *canonical order puts it in the bottom block above The Royal Navy: it loses every duplicate*
55. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
56. Russian Navy 21
57. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
58. Saronic Corsair ASV
59. The Royal Navy — *canonical order puts it in the bottom block below RADF; SEST Collection Fixes restores the game files it ships stale*
60. Type 003 Aircraft Carrier - PLANS Fujian CV-18
61. Type 003 Fujian / Type 004 CVN Aircraft Carriers
62. United States Naval Aviation
63. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

64. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
65. <<E-3G>>
66. <<Tu-16N>>
67. [DEPRECATED] E-7A Wedgetail — *KEEP — the only source of E7A_Wedgetail, which the campaigns place; SEST RAAF Wedgetail and SEST RAAF Bases depend on it*
68. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — the only source of S-70B-2_Seahawk, which the campaigns place; SEST RAN Fleet and SEST RAAF Bases depend on it*
69. A-10A Thunderbolt II
70. A-10C
71. AH-64 Apache
72. Anduril FQ-44 Fury US Navy Carrier Wingmen
73. Apex Predators MIG-29A & F-16A
74. Armed Oil Rig with Helo MOD
75. ARRW (AGM-183)
76. AVIC HARBIN Z-21
77. B-1B Lancer
78. B-2 Spirit
79. B-52H Stratofortress
80. Boeing P-8 Poseidon
81. Bréguet Br.1050 Alizé — *canonical order puts it below The Royal Navy and RADF, above Aquilon*
82. Buildings and Targets for Missions
83. CH-53E Standalone v0.1.0
84. ChengDu J-10C Vigorous Dragon
85. Civil Aircraft Mod (Airbus Family)
86. David's Sling
87. EC-2 Stand Off Jammer
88. Etendard Family Jets — *canonical order puts it below French Air Force, whose Magic 2 the Mirage 2000s keep*
89. Eurofighter Typhoon
90. Euromod - Anchorchain Expansion Pack
91. F-117 Nighthawk
92. F-15 EX Eagle II
93. F-15E StrikeEagle
94. F-15J Peace Eagle
95. F-16C Fighting Falcon (modern)
96. F-22 Raptor
97. F-2A 'Viper Zero'
98. F-8 Crusader — *canonical order puts it below French Air Force and the Etendards: its Magic 2 is an outlier*
99. French Air Force — *canonical order puts it in the bottom block, below THE REDFOR MOD and above the Etendard, F-8 and Gripen packs: its 12 shared rounds are identical or older copies of the MQ-9 Reaper's, the French Navy pack's and the Soviet AEW&C pack's, and it loses every one; the Rafale and Mirage 2000 families load from it alone*
100. French Army Vehicles
101. French Helicopter Package
102. General Atomics MQ-9 Reaper
103. Ground Upgrade: IFV — *below KC-135 so the game's [TOW_M2] holds*
104. Ground Upgrade: MBT
105. Humpback Whale
106. IL-78 TANKER
107. Iskander TBM
108. ISKANDER-M — *above THE REDFOR MOD (ss-26 mesh)*
109. J-20 (歼-20 威龙)
110. J-36 Tailless Fighter
111. JAS-39 Gripen — *canonical order puts it below French Air Force ([Damoncles]) and above Ultimate Missile Workshop (its AIM-120C-7)*
112. Ka-27RLD
113. KC-135 STRATOTANKER
114. KC-46A Pegasus - Strategic Tanker
115. Lockheed AC-130 Pack
116. Mare Nostrum '28
117. McDonnell Douglas KC-10A Extender - Strategic Tanker
118. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
119. Mi-8 T/TV
120. Mi-8EW
121. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
122. MiG-31 Foxhound
123. MiG-35 Fulcrum-F (米格-35 支点-F)
124. Mil Mi-24 Hind
125. MORE SU-24M VARIANTS
126. MV-22B Osprey Tiltrotor / JGSDF V-22B
127. MV-75 Cheyenne II — *beside the MV-22B; no collision with anything, position free*
128. NATO E-3A Sentry
129. NATO Ground Enhancement Series 2: Artillery
130. NEBO-U
131. Pakistani Pack — *canonical order puts it below Red Storm Arsenal, whose [KLC-7] the SEST-fielded KJ-600 uses*
132. Pickup truck extension
133. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
134. PLA Shenyang J-11BS
135. PLA Sukhoi Su-27UBK
136. PLAAF Aircraft Pack — *canonical order puts it in the bottom block, below the Gripen and above Ultimate Missile Workshop and Red Storm Arsenal: 56 shared files all lost to the specialist PLAAF mods above it, so only its H-6 family, J-7s, J-10A and 39 rounds load; SEST Collection Fixes restores the English loading tips its language_en folder overwrites*
137. RAAF F-35A Lighting II
138. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
139. Rebuilt J-16 / J-16D — *duplicate platform with Shenyang J-16A — different unit ids, both load*
140. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
141. RQ-180 White Bat Airframe
142. Russian Ground Enhancement Series 1: Artillery
143. S-300PMU2 — *above S-400, S-500 and THE REDFOR MOD*
144. S-500 — *below S-400 SAM (the Flap Lid SEST places)*
145. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
146. SAAB AEW&C PACK
147. SCUD-B
148. Sea Lynx
149. Sea Venom - Aquilon — *canonical order puts it below The Royal Navy and RADF (shared rack ids)*
150. SEJJIL (Iran Ballistic Missiles)
151. Shahed-136 Kamikaze Drone (Geran-2)
152. Shenyang J-11
153. Shenyang J-16A (歼-16A 潜龙)
154. Shenyang J-50 (沈阳航空工业 歼-50)
155. Shenyang J-8
156. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
157. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
158. Su-25 Frogfoot
159. Su-30SM2
160. SU-57 Felon (重刑犯)
161. Sukhoi Flanker Family (苏霍伊侧卫家族)
162. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
163. The Second Northern War
164. TU-160 Blackjack
165. Tu-214R Family (图-214R家族)
166. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
167. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
168. Type 12 SSM-ER Anti-Ship Missile System
169. U-2 "Dragon Lady"
170. VH-3D Marine One MOD
171. XIAN JH-7A (歼轰-7A 飞豹)
172. Y-20 / KJ-3000
173. Y-8/Y-9 Special Mission Aircraft Family
174. YF-23 Black Widow II

## Tier 6 — airbases last

175. Modern Chinese Airbase (Large)
176. Modern Russian Airbase (Large)
177. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

178. **THE REDFOR MOD** — consolidation pack below the specialists it copied (S-300PMU2, ISKANDER-M, Su-27, TU-16N, P-750, Russian Navy 21, Euromod): loses every shared file
179. **wp_sattelite_center** — below THE REDFOR MOD, whose byte-identical copies win
180. **Ultimate Missile Workshop** — below everything it duplicates, on the player's call: its author's 'above all' would take 91 rounds and break the Gripen's AIM-120C-7
181. **Red Storm Arsenal** — near the bottom - 638 unique files kept, 13 duplicated ones all lose; only the Pakistani Pack, the two Commonwealth packs, the Cold War rocket carriers, Chile, the Luzon Line and RE-power sit below it

