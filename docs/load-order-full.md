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

10. **U.S. Navy 2027 Capabilities mod** — above the US mods it edits
11. **SEST F-15EX Revamp** — LOCAL — above the F-15EX mod ("F-15SE")
12. **SEST F-35C JATM** — LOCAL — above every other usn_f-35c source (the four below it here)
13. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
14. **SEST RAAF F-35A JATM** — LOCAL — above the RAAF F-35A mod
15. **SEST JMSDF Mogami** — LOCAL — above the Mogami-class Frigate mod
16. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
17. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
18. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
19. **Flight Deck Ops** — above carriers
20. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
21. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

22. 1143.5 Kuznetsov
23. Auxilliary Merchant Pack
24. Charles De Gaulle & Modern French Navy Pack (WIP)
25. Chinese Navy (PLAN)
26. Euromod - Cold War Spanish Navy
27. Euromod - Modern British Navy
28. Euromod - Modern Dutch navy
29. Euromod - Modern German Navy
30. Euromod - Modern Italian Navy
31. Euromod - Modern Japanese Maritime Self Defence Force
32. Euromod - Modern Nordic Navy
33. Euromod - Modern Spanish Navy
34. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
35. Italian Navy Mod
36. Kirov-class (Pyotr Velikiy Upgrade)
37. Merchants Expanded
38. Modern US Navy
39. Mogami-class Frigate
40. Nimitz Expanded
41. PLAN Submarines
42. PLAN Type 001 Aircraft Carrier Liaoning
43. PLAN Type 071 Amphibious Transport Dock
44. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
45. Russian Navy 21
46. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
47. Type 003 Aircraft Carrier - PLANS Fujian CV-18
48. Type 003 Fujian / Type 004 CVN Aircraft Carriers
49. United States Naval Aviation
50. Virginia-, Seawolf-, and Ohio-class Submarines
51. **SEST RAN Fleet** — LOCAL — below the Euromod packs it clones from

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

52. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
53. <<E-3G>>
54. <<Tu-16N>>
55. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
56. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
57. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
58. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
59. A-10A Thunderbolt II
60. A-10C
61. AH-64 Apache
62. Apex Predators MIG-29A & F-16A
63. Armed Oil Rig with Helo MOD
64. AVIC HARBIN Z-21
65. B-1B Lancer
66. B-2 Spirit
67. B-52H Stratofortress
68. Boeing P-8 Poseidon
69. Buildings and Targets for Missions
70. ChengDu J-10C Vigorous Dragon
71. Civil Aircraft Mod (Airbus Family)
72. Dassault Rafale
73. Eurofighter Typhoon
74. F-117 Nighthawk
75. F-15 EX Eagle II
76. F-16C Fighting Falcon (modern)
77. F-22 Raptor
78. French Army Vehicles
79. French Helicopter Package
80. General Atomics MQ-9 Reaper
81. Humpback Whale
82. IL-78 TANKER
83. Iskander TBM
84. J-20 (歼-20 威龙)
85. Ka-27RLD
86. KC-135 STRATOTANKER
87. KC-46A Pegasus - Strategic Tanker
88. Lockheed AC-130 Pack
89. McDonnell Douglas KC-10A Extender - Strategic Tanker
90. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
91. Mi-8 T/TV
92. Mi-8EW
93. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
94. MiG-35 Fulcrum-F (米格-35 支点-F)
95. Mil Mi-24 Hind
96. MORE SU-24M VARIANTS
97. Pickup truck extension
98. PLA Shenyang J-11BS
99. PLA Sukhoi Su-27UBK
100. RAAF F-35A Lighting II
101. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
102. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
103. SAAB AEW&C PACK
104. SCUD-B
105. Sea Lynx
106. SEJJIL (Iran Ballistic Missiles)
107. Shahed-136 Kamikaze Drone (Geran-2)
108. Shenyang J-11
109. Shenyang J-16A (歼-16A 潜龙)
110. Shenyang J-50 (沈阳航空工业 歼-50)
111. Shenyang J-8
112. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
113. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
114. Su-25 Frogfoot
115. Su-30SM2
116. SU-57 Felon (重刑犯)
117. Sukhoi Flanker Family (苏霍伊侧卫家族)
118. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
119. TU-160 Blackjack
120. Tu-214R Family (图-214R家族)
121. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
122. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
123. Type 12 SSM-ER Anti-Ship Missile System
124. U-2 "Dragon Lady"
125. VH-3D Marine One MOD
126. XIAN JH-7A (歼轰-7A 飞豹)
127. Y-20 / KJ-3000
128. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

129. Modern Chinese Airbase (Large)
130. Modern Russian Airbase (Large)
131. Modern US Airbase
132. **SEST RAAF Bases** — LOCAL — additive; bottom by convention

