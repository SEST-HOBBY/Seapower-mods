# Mod tiers — every active mod by tier

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 190 active subscriptions plus the SEST Integration Pack (22 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

This is a tier grouping, NOT the load order. The canonical Mod Manager order is `data/load-order.tokens.txt` (191 entries: SEST_Integration plus the 190 Workshop mods); the pack ships it as LOAD-ORDER.txt and SETUP writes it. Where the numbering below differs, the canonical order wins (for example, its last four are **Philippines: The Luzon Line**, **Thailand: The Siam Shield**, **RE-power: the resupply mod** and **Real photos of airplanes and helicopters**).

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
43. JMSDF Hyūga Class — Hyūga & Ise
44. Kirov-class (Pyotr Velikiy Upgrade)
45. Merchants Expanded
46. Modern US Navy
47. Mogami-class Frigate
48. Moloti's Armed Merchantmen — *beside Merchants Expanded; no collision with anything, position free*
49. Nimitz Expanded
50. Philippines: The Luzon Line — *canonical order puts it below RADF and below KC-135 ([MK22])*
51. PLAN Submarines
52. PLAN Type 001 Aircraft Carrier Liaoning
53. PLAN Type 071 Amphibious Transport Dock
54. Project 2498 Zyetseth Class Assault Vessel
55. RE-power: the resupply mod — *canonical order puts it last, below the Luzon Line and the Siam Shield, with which it shares no files*
56. Royal Australian Defence Forces — *canonical order puts it in the bottom block above The Royal Navy: it loses every duplicate*
57. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
58. Russian Navy 21
59. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
60. Saronic Corsair ASV
61. Thailand: The Siam Shield — *canonical order puts it below the Luzon Line (same author), which keeps the 11 rounds and textures both ship*
62. The Royal Navy — *canonical order puts it in the bottom block below RADF; SEST Collection Fixes restores the game files it ships stale*
63. Type 003 Aircraft Carrier - PLANS Fujian CV-18
64. Type 003 Fujian / Type 004 CVN Aircraft Carriers
65. United States Naval Aviation
66. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

67. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
68. <<E-3G>>
69. <<Tu-16N>>
70. [DEPRECATED] E-7A Wedgetail — *KEEP — the only source of E7A_Wedgetail, which the campaigns place; SEST RAAF Wedgetail and SEST RAAF Bases depend on it*
71. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — the only source of S-70B-2_Seahawk, which the campaigns place; SEST RAN Fleet and SEST RAAF Bases depend on it*
72. A-10A Thunderbolt II
73. A-10C
74. AH-64 Apache
75. Anduril FQ-44 Fury US Navy Carrier Wingmen
76. Apex Predators MIG-29A & F-16A
77. Armed Oil Rig with Helo MOD
78. ARRW (AGM-183)
79. AVIC HARBIN Z-21
80. B-1B Lancer
81. B-2 Spirit
82. B-52H Stratofortress
83. Boeing P-8 Poseidon
84. Bréguet Br.1050 Alizé — *canonical order puts it below The Royal Navy and RADF, above Aquilon*
85. Buildings and Targets for Missions
86. CH-53E Standalone v0.1.0
87. ChengDu J-10C Vigorous Dragon
88. Civil Aircraft Mod (Airbus Family)
89. Civilian AS350 Ecureuil/AStar MOD
90. David's Sling
91. EC-2 Stand Off Jammer
92. EMAD
93. Etendard Family Jets — *canonical order puts it below French Air Force, whose Magic 2 the Mirage 2000s keep*
94. Eurofighter Typhoon
95. Euromod - Anchorchain Expansion Pack
96. F-117 Nighthawk
97. F-15 EX Eagle II
98. F-15E StrikeEagle
99. F-15J Peace Eagle
100. F-16C Fighting Falcon (modern)
101. F-22 Raptor
102. F-2A 'Viper Zero'
103. F-8 Crusader — *canonical order puts it below French Air Force and the Etendards: its Magic 2 is an outlier*
104. Fattah-1
105. Fattah-2
106. French Air Force — *canonical order puts it in the bottom block, below THE REDFOR MOD and above the Etendard, F-8 and Gripen packs: its 12 shared rounds are identical or older copies of the MQ-9 Reaper's, the French Navy pack's and the Soviet AEW&C pack's, and it loses every one; the Rafale and Mirage 2000 families load from it alone*
107. French Army Vehicles
108. French Helicopter Package
109. General Atomics MQ-9 Reaper
110. Ground Upgrade: IFV — *below KC-135 so the game's [TOW_M2] holds*
111. Ground Upgrade: MBT
112. Humpback Whale
113. IL-78 TANKER
114. Iran Bell-212
115. Iran UAV Shahed 238
116. Iskander TBM
117. ISKANDER-M — *above THE REDFOR MOD (ss-26 mesh)*
118. J-20 (歼-20 威龙)
119. J-36 Tailless Fighter
120. JAS-39 Gripen — *canonical order puts it below French Air Force ([Damoncles]) and above Ultimate Missile Workshop (its AIM-120C-7)*
121. Ka-27RLD
122. KC-135 STRATOTANKER
123. KC-46A Pegasus - Strategic Tanker
124. Lockheed AC-130 Pack
125. Mare Nostrum '28
126. McDonnell Douglas KC-10A Extender - Strategic Tanker
127. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
128. Mi-8 T/TV
129. Mi-8EW
130. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
131. MiG-31 Foxhound
132. MiG-35 Fulcrum-F (米格-35 支点-F)
133. Mil Mi-24 Hind
134. MORE SU-24M VARIANTS
135. MV-22B Osprey Tiltrotor / JGSDF V-22B
136. MV-75 Cheyenne II — *beside the MV-22B; no collision with anything, position free*
137. NATO E-3A Sentry
138. NATO Ground Enhancement Series 2: Artillery
139. NEBO-U
140. Pakistani Pack — *canonical order puts it below Red Storm Arsenal, whose [KLC-7] the SEST-fielded KJ-600 uses*
141. Pickup truck extension
142. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
143. PLA Shenyang J-11BS
144. PLA Sukhoi Su-27UBK
145. PLAAF Aircraft Pack — *canonical order puts it in the bottom block, below the Gripen and above Ultimate Missile Workshop and Red Storm Arsenal: 56 shared files all lost to the specialist PLAAF mods above it, so only its H-6 family, J-7s, J-10A and 39 rounds load; SEST Collection Fixes restores the English loading tips its language_en folder overwrites*
146. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
147. Real photos of airplanes and helicopters
148. Rebuilt J-16 / J-16D — *duplicate platform with Shenyang J-16A — different unit ids, both load*
149. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
150. RQ-180 White Bat Airframe
151. Russian Ground Enhancement Series 1: Artillery
152. S-300PMU2 — *above S-400, S-500 and THE REDFOR MOD*
153. S-350 Vityaz — *below S-500; loses its 2 shared files to Euromod*
154. S-500 — *below S-400 SAM (the Flap Lid SEST places)*
155. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
156. SAAB AEW&C PACK
157. SCUD-B
158. Sea Lynx
159. Sea Venom - Aquilon — *canonical order puts it below The Royal Navy and RADF (shared rack ids)*
160. SEJJIL (Iran Ballistic Missiles)
161. Shahed-136 Kamikaze Drone (Geran-2)
162. Shenyang J-11
163. Shenyang J-16A (歼-16A 潜龙)
164. Shenyang J-50 (沈阳航空工业 歼-50)
165. Shenyang J-8
166. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
167. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
168. Su-25 Frogfoot
169. Su-30SM2
170. SU-57 Felon (重刑犯)
171. Sukhoi Flanker Family (苏霍伊侧卫家族)
172. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
173. The Second Northern War
174. TU-160 Blackjack
175. Tu-214R Family (图-214R家族)
176. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
177. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
178. Type 12 SSM-ER Anti-Ship Missile System
179. U-2 "Dragon Lady"
180. VH-3D Marine One MOD
181. XIAN JH-7A (歼轰-7A 飞豹)
182. Y-20 / KJ-3000
183. Y-8/Y-9 Special Mission Aircraft Family
184. YF-23 Black Widow II

## Tier 6 — airbases last

185. Modern Chinese Airbase (Large)
186. Modern Russian Airbase (Large)
187. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

188. **THE REDFOR MOD** — consolidation pack below the specialists it copied (S-300PMU2, ISKANDER-M, Su-27, TU-16N, P-750, Russian Navy 21, Euromod): loses every shared file
189. **wp_sattelite_center** — below THE REDFOR MOD, whose byte-identical copies win
190. **Ultimate Missile Workshop** — below everything it duplicates, on the player's call: its author's 'above all' would take 91 rounds and break the Gripen's AIM-120C-7
191. **Red Storm Arsenal** — near the bottom - 638 unique files kept, 13 duplicated ones all lose; only the Pakistani Pack, the two Commonwealth packs, the Cold War rocket carriers, Chile, the Luzon Line, the Siam Shield and RE-power sit below it

