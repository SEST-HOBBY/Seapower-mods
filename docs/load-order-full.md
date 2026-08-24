# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 126 active subscriptions plus 6 SEST local packs. Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 1 — loader

1. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

2. **Custom Loadout Editor** — code mod — position not order-sensitive
3. **AI Doctrine Overhaul** — code mod — changes AI globally
4. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

5. **SAM Pack** — author: "top of TOE"
6. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
7. **Dingtools Weapon Pack** — author: "above any of my mods"
8. **Euromod - Main Pack** — above all Euromod addons
9. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

10. **SEST Growler NGJ + MALICE** — LOCAL — above U.S. Navy 2027, F/A-18E/F and US Naval Aviation
11. **U.S. Navy 2027 Capabilities mod** — above the US mods it edits
12. **SEST F-15EX Revamp** — LOCAL — above the F-15EX mod ("F-15SE")
13. **SEST F-35C JATM** — LOCAL — above every other usn_f-35c source (the four below it here)
14. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
15. **SEST RAAF F-35A JATM** — LOCAL — above the RAAF F-35A mod
16. **SEST JMSDF Mogami** — LOCAL — above the Mogami-class Frigate mod
17. **SEST RAAF Wedgetail** — LOCAL — above the E-7A Wedgetail mod
18. **SEST Raptor Squadrons** — LOCAL — above the F-22 mod (which promises 7 squadrons, defines 1)
19. **SEST TacMap Colors** — LOCAL — overrides the vanilla tactical-map UI colours
20. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
21. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
22. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
23. **Flight Deck Ops** — above carriers
24. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
25. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

26. 1143.5 Kuznetsov
27. Auxilliary Merchant Pack
28. Charles De Gaulle & Modern French Navy Pack (WIP)
29. Chinese Navy (PLAN)
30. Euromod - Cold War Spanish Navy
31. Euromod - Modern British Navy
32. Euromod - Modern Dutch navy
33. Euromod - Modern German Navy
34. Euromod - Modern Italian Navy
35. Euromod - Modern Japanese Maritime Self Defence Force
36. Euromod - Modern Nordic Navy
37. Euromod - Modern Spanish Navy
38. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
39. Italian Navy Mod
40. Kirov-class (Pyotr Velikiy Upgrade)
41. Merchants Expanded
42. Modern US Navy
43. Mogami-class Frigate
44. Nimitz Expanded
45. PLAN Submarines
46. PLAN Type 001 Aircraft Carrier Liaoning
47. PLAN Type 071 Amphibious Transport Dock
48. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
49. Russian Navy 21
50. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
51. Type 003 Aircraft Carrier - PLANS Fujian CV-18
52. Type 003 Fujian / Type 004 CVN Aircraft Carriers
53. United States Naval Aviation
54. Virginia-, Seawolf-, and Ohio-class Submarines
55. **SEST RAN Fleet** — LOCAL — below the Euromod packs it clones from

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

56. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
57. <<E-3G>>
58. <<Tu-16N>>
59. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
60. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
61. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
62. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
63. A-10A Thunderbolt II
64. A-10C
65. AH-64 Apache
66. Apex Predators MIG-29A & F-16A
67. Armed Oil Rig with Helo MOD
68. AVIC HARBIN Z-21
69. B-1B Lancer
70. B-2 Spirit
71. B-52H Stratofortress
72. Boeing P-8 Poseidon
73. Buildings and Targets for Missions
74. ChengDu J-10C Vigorous Dragon
75. Civil Aircraft Mod (Airbus Family)
76. Dassault Rafale
77. Eurofighter Typhoon
78. F-117 Nighthawk
79. F-15 EX Eagle II
80. F-16C Fighting Falcon (modern)
81. F-22 Raptor
82. French Army Vehicles
83. French Helicopter Package
84. General Atomics MQ-9 Reaper
85. Humpback Whale
86. IL-78 TANKER
87. Iskander TBM
88. J-20 (歼-20 威龙)
89. Ka-27RLD
90. KC-135 STRATOTANKER
91. KC-46A Pegasus - Strategic Tanker
92. Lockheed AC-130 Pack
93. McDonnell Douglas KC-10A Extender - Strategic Tanker
94. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
95. Mi-8 T/TV
96. Mi-8EW
97. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
98. MiG-35 Fulcrum-F (米格-35 支点-F)
99. Mil Mi-24 Hind
100. MORE SU-24M VARIANTS
101. Pickup truck extension
102. PLA Shenyang J-11BS
103. PLA Sukhoi Su-27UBK
104. RAAF F-35A Lighting II
105. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
106. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
107. SAAB AEW&C PACK
108. SCUD-B
109. Sea Lynx
110. SEJJIL (Iran Ballistic Missiles)
111. Shahed-136 Kamikaze Drone (Geran-2)
112. Shenyang J-11
113. Shenyang J-16A (歼-16A 潜龙)
114. Shenyang J-50 (沈阳航空工业 歼-50)
115. Shenyang J-8
116. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
117. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
118. Su-25 Frogfoot
119. Su-30SM2
120. SU-57 Felon (重刑犯)
121. Sukhoi Flanker Family (苏霍伊侧卫家族)
122. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
123. TU-160 Blackjack
124. Tu-214R Family (图-214R家族)
125. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
126. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
127. Type 12 SSM-ER Anti-Ship Missile System
128. U-2 "Dragon Lady"
129. VH-3D Marine One MOD
130. XIAN JH-7A (歼轰-7A 飞豹)
131. Y-20 / KJ-3000
132. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

133. Modern Chinese Airbase (Large)
134. Modern Russian Airbase (Large)
135. Modern US Airbase
136. **SEST RAAF Bases** — LOCAL — additive; bottom by convention

