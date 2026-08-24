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
18. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
19. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
20. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
21. **Flight Deck Ops** — above carriers
22. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
23. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

24. 1143.5 Kuznetsov
25. Auxilliary Merchant Pack
26. Charles De Gaulle & Modern French Navy Pack (WIP)
27. Chinese Navy (PLAN)
28. Euromod - Cold War Spanish Navy
29. Euromod - Modern British Navy
30. Euromod - Modern Dutch navy
31. Euromod - Modern German Navy
32. Euromod - Modern Italian Navy
33. Euromod - Modern Japanese Maritime Self Defence Force
34. Euromod - Modern Nordic Navy
35. Euromod - Modern Spanish Navy
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
46. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
47. Russian Navy 21
48. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
49. Type 003 Aircraft Carrier - PLANS Fujian CV-18
50. Type 003 Fujian / Type 004 CVN Aircraft Carriers
51. United States Naval Aviation
52. Virginia-, Seawolf-, and Ohio-class Submarines
53. **SEST RAN Fleet** — LOCAL — below the Euromod packs it clones from

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

54. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
55. <<E-3G>>
56. <<Tu-16N>>
57. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
58. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
59. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
60. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
61. A-10A Thunderbolt II
62. A-10C
63. AH-64 Apache
64. Apex Predators MIG-29A & F-16A
65. Armed Oil Rig with Helo MOD
66. AVIC HARBIN Z-21
67. B-1B Lancer
68. B-2 Spirit
69. B-52H Stratofortress
70. Boeing P-8 Poseidon
71. Buildings and Targets for Missions
72. ChengDu J-10C Vigorous Dragon
73. Civil Aircraft Mod (Airbus Family)
74. Dassault Rafale
75. Eurofighter Typhoon
76. F-117 Nighthawk
77. F-15 EX Eagle II
78. F-16C Fighting Falcon (modern)
79. F-22 Raptor
80. French Army Vehicles
81. French Helicopter Package
82. General Atomics MQ-9 Reaper
83. Humpback Whale
84. IL-78 TANKER
85. Iskander TBM
86. J-20 (歼-20 威龙)
87. Ka-27RLD
88. KC-135 STRATOTANKER
89. KC-46A Pegasus - Strategic Tanker
90. Lockheed AC-130 Pack
91. McDonnell Douglas KC-10A Extender - Strategic Tanker
92. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
93. Mi-8 T/TV
94. Mi-8EW
95. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
96. MiG-35 Fulcrum-F (米格-35 支点-F)
97. Mil Mi-24 Hind
98. MORE SU-24M VARIANTS
99. Pickup truck extension
100. PLA Shenyang J-11BS
101. PLA Sukhoi Su-27UBK
102. RAAF F-35A Lighting II
103. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
104. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
105. SAAB AEW&C PACK
106. SCUD-B
107. Sea Lynx
108. SEJJIL (Iran Ballistic Missiles)
109. Shahed-136 Kamikaze Drone (Geran-2)
110. Shenyang J-11
111. Shenyang J-16A (歼-16A 潜龙)
112. Shenyang J-50 (沈阳航空工业 歼-50)
113. Shenyang J-8
114. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
115. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
116. Su-25 Frogfoot
117. Su-30SM2
118. SU-57 Felon (重刑犯)
119. Sukhoi Flanker Family (苏霍伊侧卫家族)
120. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
121. TU-160 Blackjack
122. Tu-214R Family (图-214R家族)
123. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
124. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
125. Type 12 SSM-ER Anti-Ship Missile System
126. U-2 "Dragon Lady"
127. VH-3D Marine One MOD
128. XIAN JH-7A (歼轰-7A 飞豹)
129. Y-20 / KJ-3000
130. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

131. Modern Chinese Airbase (Large)
132. Modern Russian Airbase (Large)
133. Modern US Airbase
134. **SEST RAAF Bases** — LOCAL — additive; bottom by convention

