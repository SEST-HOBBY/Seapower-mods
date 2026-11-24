# Mod tiers — every active mod by tier

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 219 active subscriptions plus the SEST Integration Pack (25 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

This is a tier grouping, NOT the load order. The canonical Mod Manager order is `data/load-order.tokens.txt` (220 entries: SEST_Integration plus the 219 Workshop mods); the pack ships it as LOAD-ORDER.txt and SETUP writes it. Where the numbering below differs, the canonical order wins (for example, its last four are **Mil Mi-26 Halo**, **Soviet Naval Aviation - Beriev Be-12 Chayka (Mail)**, **Marine Fauna Expansion** and **Real photos of airplanes and helicopters**).

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are listed alphabetically here — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader, with its preloader (SeaLifter is not needed)

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **Better TacMap** — code mod — UI
5. **Group Manager** — compact formation UI and aircraft map grouping; Anchor Chain
6. **Contact Log** — code mod — sortable contact-log window; no game data, one _info.ini
7. **Sea Power Topographic Map** — code mod — tactical-map heights and depths; no game data
8. **Sea Power Pop-Out Windows** — code mod — game windows on a second monitor; no game data
9. **Combat Cost Tracker** — USD expenditure and loss overlay; SEST cost catalog extensions load above it
10. **Coordinated Strike Tool** — code mod — time-on-target planner (F8); no game data, one _info.ini
11. **Automatic SAR** — code mod — right-click SAR; the campaign pays for survivors
12. **Identify Expanded** — code mod — identification and challenge orders; reads its own ini
13. **Operation STEADFAST LANTERN** — third-party campaign; its nation-flag table (ui/Default/Settings_UI_General.ini) must outrank every other copy, and it is a strict superset of the previous winner's

## Tier 2 — weapon/system databases (this exact order)

14. **SAM Pack** — author: "top of TOE"
15. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
16. **Dingtools Weapon Pack** — author: "above any of my mods"
17. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
18. **Euromod - Main Pack** — above all Euromod addons
19. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

20. **F-35C Lightning II Alt. Loadouts** — KEEP — SEST F-35C JATM is built from it and loadouts hang a round it ships; must stay below the SEST pack
21. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
22. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
23. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
24. **Flight Deck Ops** — above carriers
25. **Air Deck Operations Upgrade - Nimitz (2000s)** — KEEP — the campaigns place its carrier (Flight Deck Day)
26. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

27. 1143.5 Kuznetsov
28. Anduril Maritime Drones
29. Auxilliary Merchant Pack
30. Charles De Gaulle & Modern French Navy Pack (WIP)
31. Chinese Navy (PLAN)
32. Clemenceau-class Aircraft Carrier
33. Euromod - Cold War Spanish Navy
34. Euromod - Modern British Navy
35. Euromod - Modern Dutch navy
36. Euromod - Modern German Navy
37. Euromod - Modern Italian Navy
38. Euromod - Modern Japanese Maritime Self Defence Force
39. Euromod - Modern Nordic Navy
40. Euromod - Modern Royal Australian Navy Mod
41. Euromod - Modern Spanish Navy
42. EUROMOD-Armada de Chile — *canonical order puts it below RADF and Euromod RAN, whose Type 277Q and Adelaide fire-control sections win*
43. Euromod-Brazilian Armed Forces(2000)
44. Euromod-HD Hyundai Export Ships Mod
45. Euromod-India-Navy
46. Euromod-South Korea Navy
47. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
48. Italian Navy Mod
49. JMSDF Hyūga Class — Hyūga & Ise
50. Kirov-class (Pyotr Velikiy Upgrade)
51. Merchants Expanded
52. Modern US Navy
53. Mogami-class Frigate
54. Moloti's Armed Merchantmen — *beside Merchants Expanded; no collision with anything, position free*
55. Nimitz Expanded
56. Philippines: The Luzon Line — *canonical order puts it below RADF and below KC-135 ([MK22])*
57. PLAN Submarines
58. PLAN Type 001 Aircraft Carrier Liaoning
59. PLAN Type 071 Amphibious Transport Dock
60. Project 2498 Zyetseth Class Assault Vessel
61. RAN / Echidna SRT-01
62. RAN Ghost Shark XL-AUV
63. RE-power: the resupply mod — *canonical order puts it last, below the Luzon Line and the Siam Shield, with which it shares no files*
64. Royal Australian Defence Forces — *canonical order puts it in the bottom block above The Royal Navy: it loses every duplicate*
65. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
66. Russian Navy 21
67. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
68. Saronic Corsair ASV
69. Thailand: The Siam Shield — *canonical order puts it below the Luzon Line (same author), which keeps the 11 rounds and textures both ship*
70. The Royal Navy — *canonical order puts it in the bottom block below RADF; SEST Collection Fixes restores the game files it ships stale*
71. Type 003 Fujian / Type 004 CVN Aircraft Carriers
72. United States Naval Aviation
73. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

74. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
75. <<E-3G>>
76. <<Tu-16N>>
77. [DEPRECATED] E-7A Wedgetail — *KEEP — the only source of E7A_Wedgetail, which the campaigns place; SEST RAAF Wedgetail and SEST RAAF Bases depend on it*
78. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — the only source of S-70B-2_Seahawk, which the campaigns place; SEST RAN Fleet and SEST RAAF Bases depend on it*
79. A-10A Thunderbolt II
80. A-10C
81. AH-64 Apache
82. Anduril FQ-44 Fury US Navy Carrier Wingmen
83. Apex Predators MIG-29A & F-16A
84. Armed Oil Rig with Helo MOD
85. ARRW (AGM-183)
86. AVIC HARBIN Z-21
87. B-1B Lancer
88. B-2 Spirit
89. B-21 Raider
90. B-52H Stratofortress
91. Boeing P-8 Poseidon
92. Bréguet Br.1050 Alizé — *canonical order puts it below The Royal Navy and RADF, above Aquilon*
93. Buildings and Targets for Missions
94. BUK-M3
95. CH-53E Standalone v0.1.0
96. ChengDu J-10C Vigorous Dragon
97. Chinese UAV Collection — Fictional
98. Civil Aircraft Mod (Airbus Family)
99. Civilian AS350 Ecureuil/AStar MOD
100. David's Sling
101. Dynamic Campaign Mod
102. EC-2 Stand Off Jammer
103. EMAD
104. Etendard Family Jets — *canonical order puts it below French Air Force, whose Magic 2 the Mirage 2000s keep*
105. Eurofighter Typhoon
106. Euromod - Anchorchain Expansion Pack
107. F-117 Nighthawk
108. F-15 EX Eagle II
109. F-15E StrikeEagle
110. F-15J Peace Eagle
111. F-16C Fighting Falcon (modern)
112. F-22 Raptor
113. F-2A 'Viper Zero'
114. F-8 Crusader — *canonical order puts it below French Air Force and the Etendards: its Magic 2 is an outlier*
115. Fattah-1
116. Fattah-2
117. French Air Force — *canonical order puts it in the bottom block, below THE REDFOR MOD and above the Etendard, F-8 and Gripen packs: its 12 shared rounds are identical or older copies of the MQ-9 Reaper's, the French Navy pack's and the Soviet AEW&C pack's, and it loses every one; the Rafale and Mirage 2000 families load from it alone*
118. French Army Vehicles
119. French Helicopter Package
120. General Atomics MQ-9 Reaper
121. Ground Upgrade: IFV — *below KC-135 so the game's [TOW_M2] holds*
122. Ground Upgrade: MBT
123. Humpback Whale
124. ICBM silos
125. IL-78 TANKER
126. Iran Bell-212
127. Iran UAV Shahed 238
128. Iskander TBM
129. ISKANDER-M — *above THE REDFOR MOD (ss-26 mesh)*
130. J-20 (歼-20 威龙)
131. J-36 Tailless Fighter
132. JAS-39 Gripen — *canonical order puts it below French Air Force ([Damoncles]) and above Ultimate Missile Workshop (its AIM-120C-7)*
133. Ka-27RLD
134. KC-135 STRATOTANKER
135. KC-46A Pegasus - Strategic Tanker
136. Lockheed AC-130 Pack
137. Mare Nostrum '28
138. Marine Fauna Expansion
139. McDonnell Douglas KC-10A Extender - Strategic Tanker
140. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
141. Mi-8 T/TV
142. Mi-8EW
143. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
144. MiG-31 Foxhound
145. MiG-35 Fulcrum-F (米格-35 支点-F)
146. Mil Mi-24 Hind
147. Mil Mi-26 Halo
148. Mil Mi-6 Hook
149. MORE SU-24M VARIANTS
150. MV-75 Cheyenne II — *beside the MV-22B; no collision with anything, position free*
151. NATO E-3A Sentry
152. NATO Ground Enhancement Series 2: Artillery
153. Pakistani Pack — *canonical order puts it below Red Storm Arsenal, whose [KLC-7] the SEST-fielded KJ-600 uses*
154. Pickup truck extension
155. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
156. PLA Shenyang J-11BS
157. PLA Sukhoi Su-27UBK
158. PLAAF Aircraft Pack — *canonical order puts it in the bottom block, below the Gripen and above Ultimate Missile Workshop and Red Storm Arsenal: 56 shared files all lost to the specialist PLAAF mods above it, so only its H-6 family, J-7s, J-10A and 39 rounds load; SEST Collection Fixes restores the English loading tips its language_en folder overwrites*
159. Prithvi TBM (大地弹道导弹)
160. R.A.T.S. Keel
161. R.A.T.S. Rigging
162. R.A.T.S. Sensor Views
163. RBS 15 KA - Swedish Coastal Missile Battery
164. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
165. Real photos of airplanes and helicopters
166. Rebuilt J-16 / J-16D — *duplicate platform with Shenyang J-16A — different unit ids, both load*
167. Road Mobile ICBMs (Topol-M, DF-41)
168. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
169. RQ-180 White Bat Airframe
170. Russian Ground Enhancement Series 1: Artillery
171. S-300PMU2 — *above S-400, S-500 and THE REDFOR MOD*
172. S-350 Vityaz — *below S-500; loses its 2 shared files to Euromod*
173. S-500 — *below S-400 SAM (the Flap Lid SEST places)*
174. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
175. SAAB AEW&C PACK
176. SCUD-B
177. Sea Lynx
178. Sea Venom - Aquilon — *canonical order puts it below The Royal Navy and RADF (shared rack ids)*
179. SEJJIL (Iran Ballistic Missiles)
180. Sensor View
181. Sensor View (second item)
182. Sensor View - Colour-blind palette
183. Sensor View - Euromod support
184. Sensor View - ExtendedGuidance support
185. Shahed-136 Kamikaze Drone (Geran-2)
186. Shenyang J-16A (歼-16A 潜龙)
187. Shenyang J-50 (沈阳航空工业 歼-50)
188. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
189. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
190. Soviet Naval Aviation - Beriev Be-12 Chayka (Mail)
191. SOVIET/RUSSIAN MODERN RADARS
192. Steelfin
193. Su-25 Frogfoot
194. Su-30SM2
195. SU-57 Felon (重刑犯)
196. Sukhoi Flanker Family (苏霍伊侧卫家族)
197. Swedish Army Air Defence (Tridon Mk2)
198. Swedish Army Air Defence - Giraffe 4A
199. Swedish Army Radar UndE 23 (Giraffe AMB)
200. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
201. The Second Northern War
202. TU-160 Blackjack
203. Tu-214R Family (图-214R家族)
204. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
205. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
206. Type 12 SSM-ER Anti-Ship Missile System
207. U-2 "Dragon Lady"
208. V-22 Osprey / SV-22 2024 ASW prototype
209. VH-3D Marine One MOD
210. XIAN JH-7A (歼轰-7A 飞豹)
211. Y-20 / KJ-3000
212. YF-23 Black Widow II

## Tier 6 — airbases last

213. Modern Chinese Airbase (Large)
214. Modern Russian Airbase (Large)
215. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

216. **THE REDFOR MOD** — consolidation pack below the specialists it copied (S-300PMU2, ISKANDER-M, Su-27, TU-16N, P-750, Russian Navy 21, Euromod): loses every shared file
217. **ISKANDER-K** — below THE REDFOR MOD, whose fuller wp_iskander and wp_r-500 win
218. **wp_sattelite_center** — below THE REDFOR MOD, whose byte-identical copies win
219. **Ultimate Missile Workshop** — below everything it duplicates, on the player's call: its author's 'above all' would take 91 rounds and break the Gripen's AIM-120C-7
220. **Red Storm Arsenal** — near the bottom - 638 unique files kept, 13 duplicated ones all lose; only the Pakistani Pack, the two Commonwealth packs, the Cold War rocket carriers, Chile, the Luzon Line, the Siam Shield and RE-power sit below it

