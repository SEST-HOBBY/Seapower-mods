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
17. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
18. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
19. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
20. **Flight Deck Ops** — above carriers
21. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
22. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

23. 1143.5 Kuznetsov
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
35. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
36. Italian Navy Mod
37. Kirov-class (Pyotr Velikiy Upgrade)
38. Merchants Expanded
39. Modern US Navy
40. Mogami-class Frigate
41. Nimitz Expanded
42. PLAN Submarines
43. PLAN Type 001 Aircraft Carrier Liaoning
44. PLAN Type 071 Amphibious Transport Dock
45. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
46. Russian Navy 21
47. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
48. Type 003 Aircraft Carrier - PLANS Fujian CV-18
49. Type 003 Fujian / Type 004 CVN Aircraft Carriers
50. United States Naval Aviation
51. Virginia-, Seawolf-, and Ohio-class Submarines
52. **SEST RAN Fleet** — LOCAL — below the Euromod packs it clones from

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

53. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
54. <<E-3G>>
55. <<Tu-16N>>
56. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
57. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
58. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
59. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
60. A-10A Thunderbolt II
61. A-10C
62. AH-64 Apache
63. Apex Predators MIG-29A & F-16A
64. Armed Oil Rig with Helo MOD
65. AVIC HARBIN Z-21
66. B-1B Lancer
67. B-2 Spirit
68. B-52H Stratofortress
69. Boeing P-8 Poseidon
70. Buildings and Targets for Missions
71. ChengDu J-10C Vigorous Dragon
72. Civil Aircraft Mod (Airbus Family)
73. Dassault Rafale
74. Eurofighter Typhoon
75. F-117 Nighthawk
76. F-15 EX Eagle II
77. F-16C Fighting Falcon (modern)
78. F-22 Raptor
79. French Army Vehicles
80. French Helicopter Package
81. General Atomics MQ-9 Reaper
82. Humpback Whale
83. IL-78 TANKER
84. Iskander TBM
85. J-20 (歼-20 威龙)
86. Ka-27RLD
87. KC-135 STRATOTANKER
88. KC-46A Pegasus - Strategic Tanker
89. Lockheed AC-130 Pack
90. McDonnell Douglas KC-10A Extender - Strategic Tanker
91. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
92. Mi-8 T/TV
93. Mi-8EW
94. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
95. MiG-35 Fulcrum-F (米格-35 支点-F)
96. Mil Mi-24 Hind
97. MORE SU-24M VARIANTS
98. Pickup truck extension
99. PLA Shenyang J-11BS
100. PLA Sukhoi Su-27UBK
101. RAAF F-35A Lighting II
102. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
103. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
104. SAAB AEW&C PACK
105. SCUD-B
106. Sea Lynx
107. SEJJIL (Iran Ballistic Missiles)
108. Shahed-136 Kamikaze Drone (Geran-2)
109. Shenyang J-11
110. Shenyang J-16A (歼-16A 潜龙)
111. Shenyang J-50 (沈阳航空工业 歼-50)
112. Shenyang J-8
113. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
114. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
115. Su-25 Frogfoot
116. Su-30SM2
117. SU-57 Felon (重刑犯)
118. Sukhoi Flanker Family (苏霍伊侧卫家族)
119. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
120. TU-160 Blackjack
121. Tu-214R Family (图-214R家族)
122. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
123. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
124. Type 12 SSM-ER Anti-Ship Missile System
125. U-2 "Dragon Lady"
126. VH-3D Marine One MOD
127. XIAN JH-7A (歼轰-7A 飞豹)
128. Y-20 / KJ-3000
129. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

130. Modern Chinese Airbase (Large)
131. Modern Russian Airbase (Large)
132. Modern US Airbase
133. **SEST RAAF Bases** — LOCAL — additive; bottom by convention

