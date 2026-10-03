# Full Load Order — every active mod, top to bottom

Generated from `data/mod-catalog.json` by `tools/generate_load_order.py` — 145 active subscriptions plus the SEST Integration Pack (20 packs consolidated). Top of the Mod Manager = highest priority: the higher-listed mod wins file conflicts.

Tier 0 is the SEST block and must stay unbroken at the top. Tiers 1–3 are ordered deliberately (position changes behavior). Tiers 4–6 are alphabetical — within them, order only matters between mods flagged in the conflict watchlist (`docs/conflicts-and-load-order.md`).

## Tier 0 — the consolidated SEST pack (must stay above everything)

1. **SEST Integration Pack** — ALL SEST content consolidated into one entry by tools/consolidate_packs.py - one Mod Manager slot at the very top carries every patch, so nothing can jump over an individual pack again

## Tier 1 — loader

2. **Anchor Chain** — loader — SeaLifter loads via its preloader alongside

## Tier 1b — code mods (Anchor Chain family; position among themselves is free)

3. **Custom Loadout Editor** — code mod — position not order-sensitive
4. **Better TacMap** — code mod — UI
5. **Coordinated Strike Tool** — code mod — time-on-target planner (F8); no game data, one _info.ini
6. **Automatic SAR** — code mod — right-click SAR; the campaign pays for survivors
7. **Identify Expanded** — code mod — identification and challenge orders; reads its own ini

## Tier 2 — weapon/system databases (this exact order)

8. **SAM Pack** — author: "top of TOE"
9. **PLA Land Unit Pack** — author: "above any other PLA-related mods"
10. **Dingtools Weapon Pack** — author: "above any of my mods"
11. **U.S. Navy 2027 Capabilities mod** — above Euromod - it ships better RIM-116/RIM-66/RIM-174 than Euromod's
12. **Euromod - Main Pack** — above all Euromod addons
13. **Modern PLAN Systems** — above PLAN ships

## Tier 3 — patches, each above what it modifies (this exact order)

14. **F-35C Lightning II Alt. Loadouts** — kept for now — MUST stay below SEST F-35C JATM
15. **F/A-18 Murder Hornet with AIM-174B** — above other F/A-18E/F sources
16. **B-52G with AGM-86 (realistic nuke)** — patches the vanilla B-52G
17. **Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke)** — global munition edits — treat as a patch, not an aircraft
18. **Flight Deck Ops** — above carriers
19. **Air Deck Operations Upgrade - Nimitz (2000s)** — if kept after the FDO test
20. **Ground Upgrade: SPAA** — edits ground-unit values

## Tier 4 — fleets, ships, submarines

21. 1143.5 Kuznetsov
22. [DEPRECATED] Anzac Class Frigate — *KEEP — SEST RAN Fleet dependency; SEST wins both ran_ffh_anzac files, so this mod's hull is masked until the pack is rebased onto it*
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
34. Euromod-South Korea Navy
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
45. RE-power: the resupply mod
46. Royal Navy Type 23 'Duke Class' Frigate [OLD] — *verified additive — position free*
47. Russian Navy 21
48. Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes)
49. Type 003 Aircraft Carrier - PLANS Fujian CV-18
50. Type 003 Fujian / Type 004 CVN Aircraft Carriers
51. United States Naval Aviation
52. Virginia-, Seawolf-, and Ohio-class Submarines

## Tier 5 — aircraft, helicopters, UAVs, land units, weapons, civilian

53. 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala)
54. <<E-3G>>
55. <<Tu-16N>>
56. [DEPRECATED] E-7A Wedgetail — *KEEP — SEST RAAF Bases dependency*
57. [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — *KEEP — SEST RAN Fleet / RAAF Bases dependency*
58. A-10A Thunderbolt II
59. A-10C
60. AH-64 Apache
61. Anduril FQ-44 Fury US Navy Carrier Wingmen
62. Apex Predators MIG-29A & F-16A
63. Armed Oil Rig with Helo MOD
64. ARRW (AGM-183)
65. AVIC HARBIN Z-21
66. B-1B Lancer
67. B-2 Spirit
68. B-52H Stratofortress
69. Boeing P-8 Poseidon
70. Buildings and Targets for Missions
71. CH-53E Standalone v0.1.0
72. ChengDu J-10C Vigorous Dragon
73. Civil Aircraft Mod (Airbus Family)
74. Dassault Rafale
75. David's Sling
76. Eurofighter Typhoon
77. Euromod - Anchorchain Expansion Pack
78. F-117 Nighthawk
79. F-15 EX Eagle II
80. F-15E StrikeEagle
81. F-16C Fighting Falcon (modern)
82. F-22 Raptor
83. F-2A 'Viper Zero'
84. French Army Vehicles
85. French Helicopter Package
86. General Atomics MQ-9 Reaper
87. Humpback Whale
88. IL-78 TANKER
89. Iskander TBM
90. J-16 Multirole Fighter — *duplicate platform with Shenyang J-16A — different unit ids, both load*
91. J-20 (歼-20 威龙)
92. J-36 Tailless Fighter
93. Ka-27RLD
94. KC-135 STRATOTANKER
95. KC-46A Pegasus - Strategic Tanker
96. Lockheed AC-130 Pack
97. McDonnell Douglas KC-10A Extender - Strategic Tanker
98. MH-60R Seahawk — *keep subscribed: ADO Nimitz 2000s draws its deck Seahawks from this mod's usn_sh-60b model folder. The MH-60R squadron table is SEST Collection Fixes' now (United States Naval Aviation's, written for the model that loads, plus 816 Squadron RAN), so its position above US Naval Aviation no longer decides it; unit file stays with U.S. Navy 2027*
99. Mi-8 T/TV
100. Mi-8EW
101. MIG-29 Family — *watchlist: MiG-29/R-series overlap*
102. MiG-31 Foxhound
103. MiG-35 Fulcrum-F (米格-35 支点-F)
104. Mil Mi-24 Hind
105. MORE SU-24M VARIANTS
106. MV-22B Osprey Tiltrotor / JGSDF V-22B
107. Pickup truck extension
108. PLA & PLAN & PLAAF AEP — *Anchorchain expansion — below the loader, with the Euromod one*
109. PLA Shenyang J-11BS
110. PLA Sukhoi Su-27UBK
111. RAAF F-35A Lighting II
112. RC-135V/W Rivet Joint — *above Red Storm Arsenal, whose RC-135W is a different file (usaf_rc_135) — no collision; its sensors.ini merges*
113. Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — *verified additive — position free*
114. RQ-180 White Bat Airframe
115. SA-21/S-400 SAM — *watchlist: land air-defense overlap*
116. SAAB AEW&C PACK
117. SCUD-B
118. Sea Lynx
119. SEJJIL (Iran Ballistic Missiles)
120. Shahed-136 Kamikaze Drone (Geran-2)
121. Shenyang J-11
122. Shenyang J-16A (歼-16A 潜龙)
123. Shenyang J-50 (沈阳航空工业 歼-50)
124. Shenyang J-8
125. Small and Medium-Sized UAV Series [WIP] (中小型无人机系列)
126. Soviet AEW&C + Transport Aircraft (A-50 / Il-76)
127. Su-25 Frogfoot
128. Su-30SM2
129. SU-57 Felon (重刑犯)
130. Sukhoi Flanker Family (苏霍伊侧卫家族)
131. Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included)
132. TU-160 Blackjack
133. Tu-214R Family (图-214R家族)
134. Tu-95K-22 Bear G MOD — *watchlist: see Tu-95 row*
135. Tu-95MS (X-101) — *watchlist: order vs the other Tu-95 mods decides shared files*
136. Type 12 SSM-ER Anti-Ship Missile System
137. U-2 "Dragon Lady"
138. VH-3D Marine One MOD
139. XIAN JH-7A (歼轰-7A 飞豹)
140. Y-20 / KJ-3000
141. Y-8/Y-9 Special Mission Aircraft Family
142. YF-23 Black Widow II

## Tier 6 — airbases last

143. Modern Chinese Airbase (Large)
144. Modern Russian Airbase (Large)
145. Modern US Airbase

## Tier 7 — bulk arsenals, below everything they duplicate

146. **Red Storm Arsenal** — LAST - 638 unique files kept, 13 duplicated ones all lose

