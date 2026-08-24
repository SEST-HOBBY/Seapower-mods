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
18. **SEST TacMap Colors** — LOCAL — overrides the vanilla tactical-map UI colours
19. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
20. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
21. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
22. **Flight Deck Ops** — above carriers
23. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
24. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

25. 1143.5 Kuznetsov
26. Auxilliary Merchant Pack
27. Charles De Gaulle & Modern French Navy Pack (WIP)
28. Chinese Navy (PLAN)
29. Euromod - Cold War Spanish Navy
30. Euromod - Modern British Navy
31. Euromod - Modern Dutch navy
32. Euromod - Modern German Navy
33. Euromod - Modern Italian Navy
34. Euromod - Modern Japanese Maritime Self Defence Force
35. Euromod - Modern Nordic Navy
36. Euromod - Modern Spanish Navy
37. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
38. Italian Navy Mod
39. Kirov-class (Pyotr Velikiy Upgrade)
40. Merchants Expanded
41. Modern US Navy
42. Mogami-class Frigate
43. Nimitz Expanded
44. PLAN Submarines
45. PLAN Type 001 Aircraft Carrier Liaoning
46. PLAN Type 071 Amphibious Transport Dock
47. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
48. Russian Navy 21
49. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
50. Type 003 Aircraft Carrier - PLANS Fujian CV-18
51. Type 003 Fujian / Type 004 CVN Aircraft Carriers
52. United States Naval Aviation
53. Virginia-, Seawolf-, and Ohio-class Submarines
54. **SEST RAN Fleet** — LOCAL — below the Euromod packs it clones from

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

55. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
56. <<E-3G>>
57. <<Tu-16N>>
58. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
59. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
60. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
61. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
62. A-10A Thunderbolt II
63. A-10C
64. AH-64 Apache
65. Apex Predators MIG-29A & F-16A
66. Armed Oil Rig with Helo MOD
67. AVIC HARBIN Z-21
68. B-1B Lancer
69. B-2 Spirit
70. B-52H Stratofortress
71. Boeing P-8 Poseidon
72. Buildings and Targets for Missions
73. ChengDu J-10C Vigorous Dragon
74. Civil Aircraft Mod (Airbus Family)
75. Dassault Rafale
76. Eurofighter Typhoon
77. F-117 Nighthawk
78. F-15 EX Eagle II
79. F-16C Fighting Falcon (modern)
80. F-22 Raptor
81. French Army Vehicles
82. French Helicopter Package
83. General Atomics MQ-9 Reaper
84. Humpback Whale
85. IL-78 TANKER
86. Iskander TBM
87. J-20 (歼-20 威龙)
88. Ka-27RLD
89. KC-135 STRATOTANKER
90. KC-46A Pegasus - Strategic Tanker
91. Lockheed AC-130 Pack
92. McDonnell Douglas KC-10A Extender - Strategic Tanker
93. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
94. Mi-8 T/TV
95. Mi-8EW
96. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
97. MiG-35 Fulcrum-F (米格-35 支点-F)
98. Mil Mi-24 Hind
99. MORE SU-24M VARIANTS
100. Pickup truck extension
101. PLA Shenyang J-11BS
102. PLA Sukhoi Su-27UBK
103. RAAF F-35A Lighting II
104. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
105. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
106. SAAB AEW&C PACK
107. SCUD-B
108. Sea Lynx
109. SEJJIL (Iran Ballistic Missiles)
110. Shahed-136 Kamikaze Drone (Geran-2)
111. Shenyang J-11
112. Shenyang J-16A (歼-16A 潜龙)
113. Shenyang J-50 (沈阳航空工业 歼-50)
114. Shenyang J-8
115. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
116. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
117. Su-25 Frogfoot
118. Su-30SM2
119. SU-57 Felon (重刑犯)
120. Sukhoi Flanker Family (苏霍伊侧卫家族)
121. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
122. TU-160 Blackjack
123. Tu-214R Family (图-214R家族)
124. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
125. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
126. Type 12 SSM-ER Anti-Ship Missile System
127. U-2 "Dragon Lady"
128. VH-3D Marine One MOD
129. XIAN JH-7A (歼轰-7A 飞豹)
130. Y-20 / KJ-3000
131. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

132. Modern Chinese Airbase (Large)
133. Modern Russian Airbase (Large)
134. Modern US Airbase
135. **SEST RAAF Bases** — LOCAL — additive; bottom by convention

