# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 146 active subscriptions plus the SEST Integration Pack (20 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **Better TacMap** — code mod — UI
5. **Auto Time-on-Target** — code mod — ships no game data at all, one _info.ini
6. **Coordinated Strike Tool** — code mod — time-on-target planner (F8); no game data, one _info.ini
7. **Automatic SAR** — code mod — right-click SAR; the campaign pays for survivors
8. **Identify Expanded** — code mod — identification and challenge orders; reads its own ini

## Tier 2 — weapon/system databases (this exact order)

9. **SAM Pack** — author: "top of TOE"
10. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
11. **Dingtools Weapon Pack** — author: "above any of my mods"
12. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
13. **Euromod - Main Pack** — above all Euromod addons
14. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

15. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
16. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
17. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
18. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
19. **Flight Deck Ops** — above carriers
20. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
21. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

22. 1143.5 Kuznetsov
23. [DEPRECATED] Anzac Class Frigate — *KEEP — SEST RAN Fleet dependency; SEST wins both ran_ffh_anzac files, so this mod's hull is masked until the pack is rebased onto it*
24. Auxilliary Merchant Pack
25. Charles De Gaulle & Modern French Navy Pack (WIP)
26. Chinese Navy (PLAN)
27. Euromod - Cold War Spanish Navy
28. Euromod - Modern British Navy
29. Euromod - Modern Dutch navy
30. Euromod - Modern German Navy
31. Euromod - Modern Italian Navy
32. Euromod - Modern Japanese Maritime Self Defence Force
33. Euromod - Modern Nordic Navy
34. Euromod - Modern Spanish Navy
35. Euromod-South Korea Navy
36. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
37. Italian Navy Mod
38. Kirov-class (Pyotr Velikiy Upgrade)
39. Merchants Expanded
40. Modern US Navy
41. Mogami-class Frigate
42. Nimitz Expanded
43. PLAN Submarines
44. PLAN Type 001 Aircraft Carrier Liaoning
45. PLAN Type 071 Amphibious Transport Dock
46. RE-power: the resupply mod
47. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
48. Russian Navy 21
49. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
50. Type 003 Aircraft Carrier - PLANS Fujian CV-18
51. Type 003 Fujian / Type 004 CVN Aircraft Carriers
52. United States Naval Aviation
53. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

54. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
55. <<E-3G>>
56. <<Tu-16N>>
57. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
58. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
59. A-10A Thunderbolt II
60. A-10C
61. AH-64 Apache
62. Anduril FQ-44 Fury US Navy Carrier Wingmen
63. Apex Predators MIG-29A & F-16A
64. Armed Oil Rig with Helo MOD
65. ARRW (AGM-183)
66. AVIC HARBIN Z-21
67. B-1B Lancer
68. B-2 Spirit
69. B-52H Stratofortress
70. Boeing P-8 Poseidon
71. Buildings and Targets for Missions
72. CH-53E Standalone v0.1.0
73. ChengDu J-10C Vigorous Dragon
74. Civil Aircraft Mod (Airbus Family)
75. Dassault Rafale
76. David's Sling
77. Eurofighter Typhoon
78. Euromod - Anchorchain Expansion Pack
79. F-117 Nighthawk
80. F-15 EX Eagle II
81. F-15E StrikeEagle
82. F-16C Fighting Falcon (modern)
83. F-22 Raptor
84. F-2A 'Viper Zero'
85. French Army Vehicles
86. French Helicopter Package
87. General Atomics MQ-9 Reaper
88. Humpback Whale
89. IL-78 TANKER
90. Iskander TBM
91. J-16 Multirole Fighter — *duplicate platform with Shenyang J-16A — different unit ids, both load*
92. J-20 (歼-20 威龙)
93. J-36 Tailless Fighter
94. Ka-27RLD
95. KC-135 STRATOTANKER
96. KC-46A Pegasus - Strategic Tanker
97. Lockheed AC-130 Pack
98. McDonnell Douglas KC-10A Extender - Strategic Tanker
99. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
100. Mi-8 T/TV
101. Mi-8EW
102. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
103. MiG-31 Foxhound
104. MiG-35 Fulcrum-F (米格-35 支点-F)
105. Mil Mi-24 Hind
106. MORE SU-24M VARIANTS
107. MV-22B Osprey Tiltrotor / JGSDF V-22B
108. Pickup truck extension
109. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
110. PLA Shenyang J-11BS
111. PLA Sukhoi Su-27UBK
112. RAAF F-35A Lighting II
113. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
114. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
115. RQ-180 White Bat Airframe
116. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
117. SAAB AEW&C PACK
118. SCUD-B
119. Sea Lynx
120. SEJJIL (Iran Ballistic Missiles)
121. Shahed-136 Kamikaze Drone (Geran-2)
122. Shenyang J-11
123. Shenyang J-16A (歼-16A 潜龙)
124. Shenyang J-50 (沈阳航空工业 歼-50)
125. Shenyang J-8
126. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
127. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
128. Su-25 Frogfoot
129. Su-30SM2
130. SU-57 Felon (重刑犯)
131. Sukhoi Flanker Family (苏霍伊侧卫家族)
132. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
133. TU-160 Blackjack
134. Tu-214R Family (图-214R家族)
135. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
136. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
137. Type 12 SSM-ER Anti-Ship Missile System
138. U-2 "Dragon Lady"
139. VH-3D Marine One MOD
140. XIAN JH-7A (歼轰-7A 飞豹)
141. Y-20 / KJ-3000
142. Y-8/Y-9 Special Mission Aircraft Family
143. YF-23 Black Widow II

## Tier 6 — airbases last

144. Modern Chinese Airbase (Large)
145. Modern Russian Airbase (Large)
146. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

147. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

