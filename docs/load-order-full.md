# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 137 active subscriptions plus the SEST Integration Pack (17 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **Better TacMap** — code mod — UI

## Tier 2 — weapon/system databases (this exact order)

5. **SAM Pack** — author: "top of TOE"
6. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
7. **Dingtools Weapon Pack** — author: "above any of my mods"
8. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
9. **Euromod - Main Pack** — above all Euromod addons
10. **Modern PLAN Systems** — above PLAN ships
11. **PLA & PLAN & PLAAF AEP** — Anchor Chain #!extend patches over PLA/PLAN/PLAAF rounds - an extend only applies if it outranks the copy it layers onto

## Tier 3 — patches, each above what it modifies (this exact order)

12. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
13. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
14. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
15. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
16. **Flight Deck Ops** — above carriers
17. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
18. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

19. 1143.5 Kuznetsov
20. Auxilliary Merchant Pack
21. Charles De Gaulle & Modern French Navy Pack (WIP)
22. Chinese Navy (PLAN)
23. Euromod - Cold War Spanish Navy
24. Euromod - Modern British Navy
25. Euromod - Modern Dutch navy
26. Euromod - Modern German Navy
27. Euromod - Modern Italian Navy
28. Euromod - Modern Japanese Maritime Self Defence Force
29. Euromod - Modern Nordic Navy
30. Euromod - Modern Spanish Navy
31. Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies)
32. Italian Navy Mod
33. Kirov-class (Pyotr Velikiy Upgrade)
34. Merchants Expanded
35. Modern US Navy
36. Mogami-class Frigate
37. Nimitz Expanded
38. PLAN Submarines
39. PLAN Type 001 Aircraft Carrier Liaoning
40. PLAN Type 071 Amphibious Transport Dock
41. RE-power: the resupply mod
42. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
43. Russian Navy 21
44. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
45. Type 003 Aircraft Carrier - PLANS Fujian CV-18
46. Type 003 Fujian / Type 004 CVN Aircraft Carriers
47. United States Naval Aviation
48. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

49. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
50. <<E-3G>>
51. <<Tu-16N>>
52. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
53. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
54. A-10A Thunderbolt II
55. A-10C
56. AH-64 Apache
57. Apex Predators MIG-29A & F-16A
58. Armed Oil Rig with Helo MOD
59. ARRW (AGM-183)
60. AVIC HARBIN Z-21
61. B-1B Lancer
62. B-2 Spirit
63. B-52H Stratofortress
64. Boeing P-8 Poseidon
65. Buildings and Targets for Missions
66. CH-53E Standalone
67. ChengDu J-10C Vigorous Dragon
68. Civil Aircraft Mod (Airbus Family)
69. Dassault Rafale
70. David's Sling
71. Eurofighter Typhoon
72. Euromod - Anchorchain Expansion Pack
73. F-117 Nighthawk
74. F-15 EX Eagle II
75. F-15E StrikeEagle
76. F-16C Fighting Falcon (modern)
77. F-22 Raptor
78. F-2A 'Viper Zero'
79. French Army Vehicles
80. French Helicopter Package
81. General Atomics MQ-9 Reaper
82. Humpback Whale
83. IL-78 TANKER
84. Iskander TBM
85. J-16 Multirole Fighter
86. J-20 (歼-20 威龙)
87. J-36 Tailless Fighter
88. Ka-27RLD
89. KC-135 STRATOTANKER
90. KC-46A Pegasus - Strategic Tanker
91. Lockheed AC-130 Pack
92. McDonnell Douglas KC-10A Extender - Strategic Tanker
93. MH-60R Seahawk — *resolved (collection audit): sits directly above US Naval Aviation so its squadrons file matches the loading model; unit file stays with U.S. Navy 2027*
94. Mi-8 T/TV
95. Mi-8EW
96. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
97. MiG-31 Foxhound
98. MiG-35 Fulcrum-F (米格-35 支点-F)
99. Mil Mi-24 Hind
100. MORE SU-24M VARIANTS
101. Pickup truck extension
102. PLA Shenyang J-11BS
103. PLA Sukhoi Su-27UBK
104. RAAF F-35A Lighting II
105. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
106. RQ-180 White Bat Airframe
107. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
108. SAAB AEW&C PACK
109. SCUD-B
110. Sea Lynx
111. SEJJIL (Iran Ballistic Missiles)
112. Shahed-136 Kamikaze Drone (Geran-2)
113. Shenyang J-11
114. Shenyang J-16A (歼-16A 潜龙)
115. Shenyang J-50 (沈阳航空工业 歼-50)
116. Shenyang J-8
117. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
118. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
119. Su-25 Frogfoot
120. Su-30SM2
121. SU-57 Felon (重刑犯)
122. Sukhoi Flanker Family (苏霍伊侧卫家族)
123. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
124. TU-160 Blackjack
125. Tu-214R Family (图-214R家族)
126. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
127. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
128. Type 12 SSM-ER Anti-Ship Missile System
129. U-2 "Dragon Lady"
130. VH-3D Marine One MOD
131. XIAN JH-7A (歼轰-7A 飞豹)
132. Y-20 / KJ-3000
133. Y-8/Y-9 Special Mission Aircraft Family
134. YF-23 Black Widow II

## Tier 6 — airbases last

135. Modern Chinese Airbase (Large)
136. Modern Russian Airbase (Large)
137. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

138. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

