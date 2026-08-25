# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 129 active subscriptions plus 15 SEST local packs. Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — SEST local packs (must stay above everything)

1. **SEST Growler NGJ + MALICE** — above U.S. Navy 2027, F/A-18E/F, Murder Hornet, US Naval Aviation
2. **SEST F-15EX Revamp** — above the F-15EX mod ("F-15SE")
3. **SEST B-52H ARRW** — above Dingtools and the B-52H mod - AGM-183A loft + W62
4. **SEST Allied Fixes** — above U.S. Navy 2027 - repairs the P-8 anti-ship fit
5. **SEST F-35C JATM** — above every other usn_f-35c source
6. **SEST RAAF F-35A JATM** — above the RAAF F-35A mod
7. **SEST Rafale F5** — above the Dassault Rafale mod - JATM/MALICE/LRASM fits
8. **SEST JMSDF Mogami** — above the Mogami-class Frigate mod
9. **SEST RAAF Wedgetail** — above the E-7A Wedgetail mod
10. **SEST Raptor Squadrons** — above the F-22 mod (which promises 7 squadrons, defines 1)
11. **SEST Zumwalt CPS Fix** — above Modern US Navy (repairs the DDG-1000 CPS hull)
12. **SEST TacMap Colors** — overrides the vanilla tactical-map UI colours
13. **SEST RAN Fleet** — contests nothing - additive RAN hulls
14. **SEST ADF Persistent ISR** — contests nothing - MQ-4C Triton, mesh from the MQ-9 mod
15. **SEST RAAF Bases** — contests nothing - additive RAAF airfields

## Tier 1 — loader

16. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

17. **Custom Loadout Editor** — code mod — position not order-sensitive
18. **AI Doctrine Overhaul** — code mod — changes AI globally
19. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

20. **SAM Pack** — author: "top of TOE"
21. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
22. **Dingtools Weapon Pack** — author: "above any of my mods"
23. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
24. **Euromod - Main Pack** — above all Euromod addons
25. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

26. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
27. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
28. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
29. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
30. **Flight Deck Ops** — above carriers
31. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
32. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

33. 1143.5 Kuznetsov
34. Auxilliary Merchant Pack
35. Charles De Gaulle & Modern French Navy Pack (WIP)
36. Chinese Navy (PLAN)
37. Euromod - Cold War Spanish Navy
38. Euromod - Modern British Navy
39. Euromod - Modern Dutch navy
40. Euromod - Modern German Navy
41. Euromod - Modern Italian Navy
42. Euromod - Modern Japanese Maritime Self Defence Force
43. Euromod - Modern Nordic Navy
44. Euromod - Modern Spanish Navy
45. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
46. Italian Navy Mod
47. Kirov-class (Pyotr Velikiy Upgrade)
48. Merchants Expanded
49. Modern US Navy
50. Mogami-class Frigate
51. Nimitz Expanded
52. PLAN Submarines
53. PLAN Type 001 Aircraft Carrier Liaoning
54. PLAN Type 071 Amphibious Transport Dock
55. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
56. Russian Navy 21
57. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
58. Type 003 Aircraft Carrier - PLANS Fujian CV-18
59. Type 003 Fujian / Type 004 CVN Aircraft Carriers
60. United States Naval Aviation
61. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

62. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
63. <<E-3G>>
64. <<Tu-16N>>
65. [DEPRECATED] Boeing F/A-18E/F Super Hornet — *kept for now — below Murder Hornet*
66. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
67. [DEPRECATED] Lockheed Martin F-35C Lighting II — *kept for now — must stay below SEST F-35C JATM (any tier below 3 satisfies this)*
68. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
69. A-10A Thunderbolt II
70. A-10C
71. AH-64 Apache
72. Apex Predators MIG-29A & F-16A
73. Armed Oil Rig with Helo MOD
74. ARRW (AGM-183)
75. AVIC HARBIN Z-21
76. B-1B Lancer
77. B-2 Spirit
78. B-52H Stratofortress
79. Boeing P-8 Poseidon
80. Buildings and Targets for Missions
81. ChengDu J-10C Vigorous Dragon
82. Civil Aircraft Mod (Airbus Family)
83. Dassault Rafale
84. David's Sling
85. Eurofighter Typhoon
86. F-117 Nighthawk
87. F-15 EX Eagle II
88. F-16C Fighting Falcon (modern)
89. F-22 Raptor
90. French Army Vehicles
91. French Helicopter Package
92. General Atomics MQ-9 Reaper
93. Humpback Whale
94. IL-78 TANKER
95. Iskander TBM
96. J-20 (歼-20 威龙)
97. Ka-27RLD
98. KC-135 STRATOTANKER
99. KC-46A Pegasus - Strategic Tanker
100. Lockheed AC-130 Pack
101. McDonnell Douglas KC-10A Extender - Strategic Tanker
102. MH-60R Seahawk — *watchlist: order vs other MH-60 sources decides which wins*
103. Mi-8 T/TV
104. Mi-8EW
105. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
106. MiG-35 Fulcrum-F (米格-35 支点-F)
107. Mil Mi-24 Hind
108. MORE SU-24M VARIANTS
109. Pickup truck extension
110. PLA Shenyang J-11BS
111. PLA Sukhoi Su-27UBK
112. RAAF F-35A Lighting II
113. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
114. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
115. SAAB AEW&C PACK
116. SCUD-B
117. Sea Lynx
118. SEJJIL (Iran Ballistic Missiles)
119. Shahed-136 Kamikaze Drone (Geran-2)
120. Shenyang J-11
121. Shenyang J-16A (歼-16A 潜龙)
122. Shenyang J-50 (沈阳航空工业 歼-50)
123. Shenyang J-8
124. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
125. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
126. Su-25 Frogfoot
127. Su-30SM2
128. SU-57 Felon (重刑犯)
129. Sukhoi Flanker Family (苏霍伊侧卫家族)
130. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
131. TU-160 Blackjack
132. Tu-214R Family (图-214R家族)
133. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
134. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
135. Type 12 SSM-ER Anti-Ship Missile System
136. U-2 "Dragon Lady"
137. VH-3D Marine One MOD
138. XIAN JH-7A (歼轰-7A 飞豹)
139. Y-20 / KJ-3000
140. Y-8/Y-9 Special Mission Aircraft Family

## Tier 6 — airbases last

141. Modern Chinese Airbase (Large)
142. Modern Russian Airbase (Large)
143. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

144. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

