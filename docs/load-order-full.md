# Mod tiers — every active mod by tier

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 198 active subscriptions plus the SEST Integration Pack (24 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

This is a tier grouping, NOT the load order. The canonical Mod Manager order is `data/load-order.tokens.txt` (199 entries: SEST_Integration plus the 198 Workshop mods); the pack ships it as LOAD-ORDER.txt and SETUP writes it. Where the numbering below differs, the canonical order wins (for example, its last four are **Philippines: The Luzon Line**, **Thailand: The Siam Shield**, **RE-power: the resupply mod** and **Real photos of airplanes and helicopters**).

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are listed alphabetically here — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader, with its preloader (SeaLifter is not needed)

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
24. Anduril Maritime Drones
25. Auxilliary Merchant Pack
26. Charles De Gaulle & Modern French Navy Pack (WIP)
27. Chinese Navy (PLAN)
28. Clemenceau-class Aircraft Carrier
29. Euromod - Cold War Spanish Navy
30. Euromod - Modern British Navy
31. Euromod - Modern Dutch navy
32. Euromod - Modern German Navy
33. Euromod - Modern Italian Navy
34. Euromod - Modern Japanese Maritime Self Defence Force
35. Euromod - Modern Nordic Navy
36. Euromod - Modern Royal Australian Navy Mod
37. Euromod - Modern Spanish Navy
38. EUROMOD-Armada de Chile — *canonical order puts it below RADF and far below <<E-3G>> ([AN/APY-2])*
39. Euromod-Brazilian Armed Forces(2000)
40. Euromod-India-Navy
41. Euromod-Philippine-Navy
42. Euromod-South Korea Navy
43. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
44. Italian Navy Mod
45. JMSDF Hyūga Class — Hyūga & Ise
46. Kirov-class (Pyotr Velikiy Upgrade)
47. Merchants Expanded
48. Modern US Navy
49. Mogami-class Frigate
50. Moloti's Armed Merchantmen — *beside Merchants Expanded; no collision with anything, position free*
51. Nimitz Expanded
52. Philippines: The Luzon Line — *canonical order puts it below RADF and below KC-135 ([MK22])*
53. PLAN Submarines
54. PLAN Type 001 Aircraft Carrier Liaoning
55. PLAN Type 071 Amphibious Transport Dock
56. Project 2498 Zyetseth Class Assault Vessel
57. RE-power: the resupply mod — *canonical order puts it last, below the Luzon Line and the Siam Shield, with which it shares no files*
58. Royal Australian Defence Forces — *canonical order puts it in the bottom block above The Royal Navy: it loses every duplicate*
59. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
60. Russian Navy 21
61. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
62. Saronic Corsair ASV
63. Thailand: The Siam Shield — *canonical order puts it below the Luzon Line (same author), which keeps the 11 rounds and textures both ship*
64. The Royal Navy — *canonical order puts it in the bottom block below RADF; SEST Collection Fixes restores the game files it ships stale*
65. Type 003 Fujian / Type 004 CVN Aircraft Carriers
66. United States Naval Aviation
67. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

68. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
69. <<E-3G>>
70. <<Tu-16N>>
71. [DEPRECATED] E-7A Wedgetail — *KEEP — the only source of E7A_Wedgetail, which the campaigns place; SEST RAAF Wedgetail and SEST RAAF Bases depend on it*
72. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — the only source of S-70B-2_Seahawk, which the campaigns place; SEST RAN Fleet and SEST RAAF Bases depend on it*
73. A-10A Thunderbolt II
74. A-10C
75. AH-64 Apache
76. Anduril FQ-44 Fury US Navy Carrier Wingmen
77. Apex Predators MIG-29A & F-16A
78. Armed Oil Rig with Helo MOD
79. ARRW (AGM-183)
80. AVIC HARBIN Z-21
81. B-1B Lancer
82. B-2 Spirit
83. B-52H Stratofortress
84. Boeing P-8 Poseidon
85. Bréguet Br.1050 Alizé — *canonical order puts it below The Royal Navy and RADF, above Aquilon*
86. Buildings and Targets for Missions
87. BUK-M3
88. CH-53E Standalone v0.1.0
89. ChengDu J-10C Vigorous Dragon
90. Civil Aircraft Mod (Airbus Family)
91. Civilian AS350 Ecureuil/AStar MOD
92. David's Sling
93. Dynamic Campaign Mod
94. EC-2 Stand Off Jammer
95. EMAD
96. Etendard Family Jets — *canonical order puts it below French Air Force, whose Magic 2 the Mirage 2000s keep*
97. Eurofighter Typhoon
98. Euromod - Anchorchain Expansion Pack
99. F-117 Nighthawk
100. F-15 EX Eagle II
101. F-15E StrikeEagle
102. F-15J Peace Eagle
103. F-16C Fighting Falcon (modern)
104. F-22 Raptor
105. F-2A 'Viper Zero'
106. F-8 Crusader — *canonical order puts it below French Air Force and the Etendards: its Magic 2 is an outlier*
107. Fattah-1
108. Fattah-2
109. French Air Force — *canonical order puts it in the bottom block, below THE REDFOR MOD and above the Etendard, F-8 and Gripen packs: its 12 shared rounds are identical or older copies of the MQ-9 Reaper's, the French Navy pack's and the Soviet AEW&C pack's, and it loses every one; the Rafale and Mirage 2000 families load from it alone*
110. French Army Vehicles
111. French Helicopter Package
112. General Atomics MQ-9 Reaper
113. Ground Upgrade: IFV — *below KC-135 so the game's [TOW_M2] holds*
114. Ground Upgrade: MBT
115. Humpback Whale
116. ICBM silos
117. IL-78 TANKER
118. Iran Bell-212
119. Iran UAV Shahed 238
120. Iskander TBM
121. ISKANDER-M — *above THE REDFOR MOD (ss-26 mesh)*
122. J-20 (歼-20 威龙)
123. J-36 Tailless Fighter
124. JAS-39 Gripen — *canonical order puts it below French Air Force ([Damoncles]) and above Ultimate Missile Workshop (its AIM-120C-7)*
125. Ka-27RLD
126. KC-135 STRATOTANKER
127. KC-46A Pegasus - Strategic Tanker
128. Lockheed AC-130 Pack
129. Mare Nostrum '28
130. McDonnell Douglas KC-10A Extender - Strategic Tanker
131. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
132. Mi-8 T/TV
133. Mi-8EW
134. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
135. MiG-31 Foxhound
136. MiG-35 Fulcrum-F (米格-35 支点-F)
137. Mil Mi-24 Hind
138. MORE SU-24M VARIANTS
139. MV-75 Cheyenne II — *beside the MV-22B; no collision with anything, position free*
140. NATO E-3A Sentry
141. NATO Ground Enhancement Series 2: Artillery
142. NEBO-U
143. Pakistani Pack — *canonical order puts it below Red Storm Arsenal, whose [KLC-7] the SEST-fielded KJ-600 uses*
144. Pickup truck extension
145. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
146. PLA Shenyang J-11BS
147. PLA Sukhoi Su-27UBK
148. PLAAF Aircraft Pack — *canonical order puts it in the bottom block, below the Gripen and above Ultimate Missile Workshop and Red Storm Arsenal: 56 shared files all lost to the specialist PLAAF mods above it, so only its H-6 family, J-7s, J-10A and 39 rounds load; SEST Collection Fixes restores the English loading tips its language_en folder overwrites*
149. Prithvi TBM (大地弹道导弹)
150. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
151. Real photos of airplanes and helicopters
152. Rebuilt J-16 / J-16D — *duplicate platform with Shenyang J-16A — different unit ids, both load*
153. Road Mobile ICBMs (Topol-M, DF-41)
154. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
155. RQ-180 White Bat Airframe
156. Russian Ground Enhancement Series 1: Artillery
157. S-300PMU2 — *above S-400, S-500 and THE REDFOR MOD*
158. S-350 Vityaz — *below S-500; loses its 2 shared files to Euromod*
159. S-500 — *below S-400 SAM (the Flap Lid SEST places)*
160. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
161. SAAB AEW&C PACK
162. SCUD-B
163. Sea Lynx
164. Sea Venom - Aquilon — *canonical order puts it below The Royal Navy and RADF (shared rack ids)*
165. SEJJIL (Iran Ballistic Missiles)
166. Shahed-136 Kamikaze Drone (Geran-2)
167. Shenyang J-11
168. Shenyang J-16A (歼-16A 潜龙)
169. Shenyang J-50 (沈阳航空工业 歼-50)
170. Shenyang J-8
171. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
172. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
173. Steelfin
174. Su-25 Frogfoot
175. Su-30SM2
176. SU-57 Felon (重刑犯)
177. Sukhoi Flanker Family (苏霍伊侧卫家族)
178. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
179. The Second Northern War
180. TU-160 Blackjack
181. Tu-214R Family (图-214R家族)
182. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
183. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
184. Type 12 SSM-ER Anti-Ship Missile System
185. U-2 "Dragon Lady"
186. V-22 Osprey / SV-22 2024 ASW prototype
187. VH-3D Marine One MOD
188. XIAN JH-7A (歼轰-7A 飞豹)
189. Y-20 / KJ-3000
190. Y-8/Y-9 Special Mission Aircraft Family
191. YF-23 Black Widow II

## Tier 6 — airbases last

192. Modern Chinese Airbase (Large)
193. Modern Russian Airbase (Large)
194. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

195. **THE REDFOR MOD** — consolidation pack below the specialists it copied (S-300PMU2, ISKANDER-M, Su-27, TU-16N, P-750, Russian Navy 21, Euromod): loses every shared file
196. **ISKANDER-K** — below THE REDFOR MOD, whose fuller wp_iskander and wp_r-500 win
197. **wp_sattelite_center** — below THE REDFOR MOD, whose byte-identical copies win
198. **Ultimate Missile Workshop** — below everything it duplicates, on the player's call: its author's 'above all' would take 91 rounds and break the Gripen's AIM-120C-7
199. **Red Storm Arsenal** — near the bottom - 638 unique files kept, 13 duplicated ones all lose; only the Pakistani Pack, the two Commonwealth packs, the Cold War rocket carriers, Chile, the Luzon Line, the Siam Shield and RE-power sit below it

