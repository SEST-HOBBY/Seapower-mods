# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 128 active subscriptions plus 11 SEST local packs. Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — SEST local packs (must stay above everything)

1. **SEST Growler NGJ + MALICE** — above U.S. Navy 2027, F/A-18E/F, Murder Hornet, US Naval Aviation
2. **SEST F-15EX Revamp** — above the F-15EX mod ("F-15SE")
3. **SEST F-35C JATM** — above every other usn_f-35c source
4. **SEST RAAF F-35A JATM** — above the RAAF F-35A mod
5. **SEST JMSDF Mogami** — above the Mogami-class Frigate mod
6. **SEST RAAF Wedgetail** — above the E-7A Wedgetail mod
7. **SEST Raptor Squadrons** — above the F-22 mod (which promises 7 squadrons, defines 1)
8. **SEST Zumwalt CPS Fix** — above Modern US Navy (repairs the DDG-1000 CPS hull)
9. **SEST TacMap Colors** — overrides the vanilla tactical-map UI colours
10. **SEST RAN Fleet** — contests nothing - additive RAN hulls
11. **SEST RAAF Bases** — contests nothing - additive RAAF airfields

## Tier 1 — loader

12. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

13. **Custom Loadout Editor** — code mod — position not order-sensitive
14. **AI Doctrine Overhaul** — code mod — changes AI globally
15. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

16. **SAM Pack** — author: "top of TOE"
17. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
18. **Dingtools Weapon Pack** — author: "above any of my mods"
19. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
20. **Euromod - Main Pack** — above all Euromod addons
21. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

22. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
23. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
24. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
25. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
26. **Flight Deck Ops** — above carriers
27. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
28. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

29. 1143.5 Kuznetsov
30. Auxilliary Merchant Pack
31. Charles De Gaulle & Modern French Navy Pack (WIP)
32. Chinese Navy (PLAN)
33. Euromod - Cold War Spanish Navy
34. Euromod - Modern British Navy
35. Euromod - Modern Dutch navy
36. Euromod - Modern German Navy
37. Euromod - Modern Italian Navy
38. Euromod - Modern Japanese Maritime Self Defence Force
39. Euromod - Modern Nordic Navy
40. Euromod - Modern Spanish Navy
41. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
42. Italian Navy Mod
43. Kirov-class (Pyotr Velikiy Upgrade)
44. Merchants Expanded
45. Modern US Navy
46. Mogami-class Frigate
47. Nimitz Expanded
48. PLAN Submarines
49. PLAN Type 001 Aircraft Carrier Liaoning
50. PLAN Type 071 Amphibious Transport Dock
51. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
52. Russian Navy 21
53. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
54. Type 003 Aircraft Carrier - PLANS Fujian CV-18
55. Type 003 Fujian / Type 004 CVN Aircraft Carriers
56. United States Naval Aviation
57. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

58. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
59. <<E-3G>>
60. <<Tu-16N>>
61. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
62. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
63. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
64. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
65. A-10A Thunderbolt II
66. A-10C
67. AH-64 Apache
68. Apex Predators MIG-29A & F-16A
69. Armed Oil Rig with Helo MOD
70. ARRW (AGM-183)
71. AVIC HARBIN Z-21
72. B-1B Lancer
73. B-2 Spirit
74. B-52H Stratofortress
75. Boeing P-8 Poseidon
76. Buildings and Targets for Missions
77. ChengDu J-10C Vigorous Dragon
78. Civil Aircraft Mod (Airbus Family)
79. Dassault Rafale
80. David's Sling
81. Eurofighter Typhoon
82. F-117 Nighthawk
83. F-15 EX Eagle II
84. F-16C Fighting Falcon (modern)
85. F-22 Raptor
86. French Army Vehicles
87. French Helicopter Package
88. General Atomics MQ-9 Reaper
89. Humpback Whale
90. IL-78 TANKER
91. Iskander TBM
92. J-20 (歼-20 威龙)
93. Ka-27RLD
94. KC-135 STRATOTANKER
95. KC-46A Pegasus - Strategic Tanker
96. Lockheed AC-130 Pack
97. McDonnell Douglas KC-10A Extender - Strategic Tanker
98. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
99. Mi-8 T/TV
100. Mi-8EW
101. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
102. MiG-35 Fulcrum-F (米格-35 支点-F)
103. Mil Mi-24 Hind
104. MORE SU-24M VARIANTS
105. Pickup truck extension
106. PLA Shenyang J-11BS
107. PLA Sukhoi Su-27UBK
108. RAAF F-35A Lighting II
109. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
110. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
111. SAAB AEW&C PACK
112. SCUD-B
113. Sea Lynx
114. SEJJIL (Iran Ballistic Missiles)
115. Shahed-136 Kamikaze Drone (Geran-2)
116. Shenyang J-11
117. Shenyang J-16A (歼-16A 潜龙)
118. Shenyang J-50 (沈阳航空工业 歼-50)
119. Shenyang J-8
120. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
121. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
122. Su-25 Frogfoot
123. Su-30SM2
124. SU-57 Felon (重刑犯)
125. Sukhoi Flanker Family (苏霍伊侧卫家族)
126. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
127. TU-160 Blackjack
128. Tu-214R Family (图-214R家族)
129. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
130. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
131. Type 12 SSM-ER Anti-Ship Missile System
132. U-2 "Dragon Lady"
133. VH-3D Marine One MOD
134. XIAN JH-7A (歼轰-7A 飞豹)
135. Y-20 / KJ-3000
136. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

137. Modern Chinese Airbase (Large)
138. Modern Russian Airbase (Large)
139. Modern US Airbase

