# Mod tiers — every active mod by tier

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 200 active subscriptions plus the SEST Integration Pack (25 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

This is a tier grouping, NOT the load order. The canonical Mod Manager order is `data/load-order.tokens.txt` (201 entries: SEST_Integration plus the 200 Workshop mods); the pack ships it as LOAD-ORDER.txt and SETUP writes it. Where the numbering below differs, the canonical order wins (for example, its last four are **Philippines: The Luzon Line**, **Thailand: The Siam Shield**, **RE-power: the resupply mod** and **Real photos of airplanes and helicopters**).

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are listed alphabetically here — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader, with its preloader (SeaLifter is not needed)

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **Better TacMap** — code mod — UI
5. **Formation Manager Replacement** — compact formation UI and aircraft map grouping; Anchor Chain
6. **Combat Cost Tracker** — USD expenditure and loss overlay; SEST cost catalog extensions load above it
7. **Coordinated Strike Tool** — code mod — time-on-target planner (F8); no game data, one _info.ini
8. **Automatic SAR** — code mod — right-click SAR; the campaign pays for survivors
9. **Identify Expanded** — code mod — identification and challenge orders; reads its own ini
10. **Operation STEADFAST LANTERN** — third-party campaign; its nation-flag table (ui/Default/Settings_UI_General.ini) must outrank every other copy, and it is a strict superset of the previous winner's

## Tier 2 — weapon/system databases (this exact order)

11. **SAM Pack** — author: "top of TOE"
12. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
13. **Dingtools Weapon Pack** — author: "above any of my mods"
14. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
15. **Euromod - Main Pack** — above all Euromod addons
16. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

17. **F-35C Lightning II Alt. Loadouts** — KEEP — SEST F-35C JATM is built from it and loadouts hang a round it ships; must stay below the SEST pack
18. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
19. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
20. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
21. **Flight Deck Ops** — above carriers
22. **Air Deck Operations Upgrade - Nimitz (2000s)** — KEEP — the campaigns place its carrier (Flight Deck Day)
23. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

24. 1143.5 Kuznetsov
25. [DEPRECATED] Anzac Class Frigate — *KEEP — the only source of the RAN Anzac hull the campaigns use; since 20 Sep 2026 SEST RAN Fleet patches this mod's own vessels/ran_ffh_anzac.ini, so its real ASMD hull is what loads*
26. Anduril Maritime Drones
27. Auxilliary Merchant Pack
28. Charles De Gaulle & Modern French Navy Pack (WIP)
29. Chinese Navy (PLAN)
30. Clemenceau-class Aircraft Carrier
31. Euromod - Cold War Spanish Navy
32. Euromod - Modern British Navy
33. Euromod - Modern Dutch navy
34. Euromod - Modern German Navy
35. Euromod - Modern Italian Navy
36. Euromod - Modern Japanese Maritime Self Defence Force
37. Euromod - Modern Nordic Navy
38. Euromod - Modern Royal Australian Navy Mod
39. Euromod - Modern Spanish Navy
40. EUROMOD-Armada de Chile — *canonical order puts it below RADF and far below <<E-3G>> ([AN/APY-2])*
41. Euromod-Brazilian Armed Forces(2000)
42. Euromod-India-Navy
43. Euromod-Philippine-Navy
44. Euromod-South Korea Navy
45. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
46. Italian Navy Mod
47. JMSDF Hyūga Class — Hyūga & Ise
48. Kirov-class (Pyotr Velikiy Upgrade)
49. Merchants Expanded
50. Modern US Navy
51. Mogami-class Frigate
52. Moloti's Armed Merchantmen — *beside Merchants Expanded; no collision with anything, position free*
53. Nimitz Expanded
54. Philippines: The Luzon Line — *canonical order puts it below RADF and below KC-135 ([MK22])*
55. PLAN Submarines
56. PLAN Type 001 Aircraft Carrier Liaoning
57. PLAN Type 071 Amphibious Transport Dock
58. Project 2498 Zyetseth Class Assault Vessel
59. RE-power: the resupply mod — *canonical order puts it last, below the Luzon Line and the Siam Shield, with which it shares no files*
60. Royal Australian Defence Forces — *canonical order puts it in the bottom block above The Royal Navy: it loses every duplicate*
61. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
62. Russian Navy 21
63. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
64. Saronic Corsair ASV
65. Thailand: The Siam Shield — *canonical order puts it below the Luzon Line (same author), which keeps the 11 rounds and textures both ship*
66. The Royal Navy — *canonical order puts it in the bottom block below RADF; SEST Collection Fixes restores the game files it ships stale*
67. Type 003 Fujian / Type 004 CVN Aircraft Carriers
68. United States Naval Aviation
69. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

70. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
71. <<E-3G>>
72. <<Tu-16N>>
73. [DEPRECATED] E-7A Wedgetail — *KEEP — the only source of E7A_Wedgetail, which the campaigns place; SEST RAAF Wedgetail and SEST RAAF Bases depend on it*
74. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — the only source of S-70B-2_Seahawk, which the campaigns place; SEST RAN Fleet and SEST RAAF Bases depend on it*
75. A-10A Thunderbolt II
76. A-10C
77. AH-64 Apache
78. Anduril FQ-44 Fury US Navy Carrier Wingmen
79. Apex Predators MIG-29A & F-16A
80. Armed Oil Rig with Helo MOD
81. ARRW (AGM-183)
82. AVIC HARBIN Z-21
83. B-1B Lancer
84. B-2 Spirit
85. B-52H Stratofortress
86. Boeing P-8 Poseidon
87. Bréguet Br.1050 Alizé — *canonical order puts it below The Royal Navy and RADF, above Aquilon*
88. Buildings and Targets for Missions
89. BUK-M3
90. CH-53E Standalone v0.1.0
91. ChengDu J-10C Vigorous Dragon
92. Civil Aircraft Mod (Airbus Family)
93. Civilian AS350 Ecureuil/AStar MOD
94. David's Sling
95. Dynamic Campaign Mod
96. EC-2 Stand Off Jammer
97. EMAD
98. Etendard Family Jets — *canonical order puts it below French Air Force, whose Magic 2 the Mirage 2000s keep*
99. Eurofighter Typhoon
100. Euromod - Anchorchain Expansion Pack
101. F-117 Nighthawk
102. F-15 EX Eagle II
103. F-15E StrikeEagle
104. F-15J Peace Eagle
105. F-16C Fighting Falcon (modern)
106. F-22 Raptor
107. F-2A 'Viper Zero'
108. F-8 Crusader — *canonical order puts it below French Air Force and the Etendards: its Magic 2 is an outlier*
109. Fattah-1
110. Fattah-2
111. French Air Force — *canonical order puts it in the bottom block, below THE REDFOR MOD and above the Etendard, F-8 and Gripen packs: its 12 shared rounds are identical or older copies of the MQ-9 Reaper's, the French Navy pack's and the Soviet AEW&C pack's, and it loses every one; the Rafale and Mirage 2000 families load from it alone*
112. French Army Vehicles
113. French Helicopter Package
114. General Atomics MQ-9 Reaper
115. Ground Upgrade: IFV — *below KC-135 so the game's [TOW_M2] holds*
116. Ground Upgrade: MBT
117. Humpback Whale
118. ICBM silos
119. IL-78 TANKER
120. Iran Bell-212
121. Iran UAV Shahed 238
122. Iskander TBM
123. ISKANDER-M — *above THE REDFOR MOD (ss-26 mesh)*
124. J-20 (歼-20 威龙)
125. J-36 Tailless Fighter
126. JAS-39 Gripen — *canonical order puts it below French Air Force ([Damoncles]) and above Ultimate Missile Workshop (its AIM-120C-7)*
127. Ka-27RLD
128. KC-135 STRATOTANKER
129. KC-46A Pegasus - Strategic Tanker
130. Lockheed AC-130 Pack
131. Mare Nostrum '28
132. McDonnell Douglas KC-10A Extender - Strategic Tanker
133. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
134. Mi-8 T/TV
135. Mi-8EW
136. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
137. MiG-31 Foxhound
138. MiG-35 Fulcrum-F (米格-35 支点-F)
139. Mil Mi-24 Hind
140. MORE SU-24M VARIANTS
141. MV-75 Cheyenne II — *beside the MV-22B; no collision with anything, position free*
142. NATO E-3A Sentry
143. NATO Ground Enhancement Series 2: Artillery
144. NEBO-U
145. Pakistani Pack — *canonical order puts it below Red Storm Arsenal, whose [KLC-7] the SEST-fielded KJ-600 uses*
146. Pickup truck extension
147. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
148. PLA Shenyang J-11BS
149. PLA Sukhoi Su-27UBK
150. PLAAF Aircraft Pack — *canonical order puts it in the bottom block, below the Gripen and above Ultimate Missile Workshop and Red Storm Arsenal: 56 shared files all lost to the specialist PLAAF mods above it, so only its H-6 family, J-7s, J-10A and 39 rounds load; SEST Collection Fixes restores the English loading tips its language_en folder overwrites*
151. Prithvi TBM (大地弹道导弹)
152. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
153. Real photos of airplanes and helicopters
154. Rebuilt J-16 / J-16D — *duplicate platform with Shenyang J-16A — different unit ids, both load*
155. Road Mobile ICBMs (Topol-M, DF-41)
156. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
157. RQ-180 White Bat Airframe
158. Russian Ground Enhancement Series 1: Artillery
159. S-300PMU2 — *above S-400, S-500 and THE REDFOR MOD*
160. S-350 Vityaz — *below S-500; loses its 2 shared files to Euromod*
161. S-500 — *below S-400 SAM (the Flap Lid SEST places)*
162. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
163. SAAB AEW&C PACK
164. SCUD-B
165. Sea Lynx
166. Sea Venom - Aquilon — *canonical order puts it below The Royal Navy and RADF (shared rack ids)*
167. SEJJIL (Iran Ballistic Missiles)
168. Shahed-136 Kamikaze Drone (Geran-2)
169. Shenyang J-11
170. Shenyang J-16A (歼-16A 潜龙)
171. Shenyang J-50 (沈阳航空工业 歼-50)
172. Shenyang J-8
173. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
174. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
175. Steelfin
176. Su-25 Frogfoot
177. Su-30SM2
178. SU-57 Felon (重刑犯)
179. Sukhoi Flanker Family (苏霍伊侧卫家族)
180. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
181. The Second Northern War
182. TU-160 Blackjack
183. Tu-214R Family (图-214R家族)
184. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
185. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
186. Type 12 SSM-ER Anti-Ship Missile System
187. U-2 "Dragon Lady"
188. V-22 Osprey / SV-22 2024 ASW prototype
189. VH-3D Marine One MOD
190. XIAN JH-7A (歼轰-7A 飞豹)
191. Y-20 / KJ-3000
192. Y-8/Y-9 Special Mission Aircraft Family
193. YF-23 Black Widow II

## Tier 6 — airbases last

194. Modern Chinese Airbase (Large)
195. Modern Russian Airbase (Large)
196. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

197. **THE REDFOR MOD** — consolidation pack below the specialists it copied (S-300PMU2, ISKANDER-M, Su-27, TU-16N, P-750, Russian Navy 21, Euromod): loses every shared file
198. **ISKANDER-K** — below THE REDFOR MOD, whose fuller wp_iskander and wp_r-500 win
199. **wp_sattelite_center** — below THE REDFOR MOD, whose byte-identical copies win
200. **Ultimate Missile Workshop** — below everything it duplicates, on the player's call: its author's 'above all' would take 91 rounds and break the Gripen's AIM-120C-7
201. **Red Storm Arsenal** — near the bottom - 638 unique files kept, 13 duplicated ones all lose; only the Pakistani Pack, the two Commonwealth packs, the Cold War rocket carriers, Chile, the Luzon Line, the Siam Shield and RE-power sit below it

