# SEST World Sandbox 2028 - Regional Expansion (preview)

This is an **optional new-game world**. The original `sest.world_sandbox_2028` campaign and existing save files are unchanged. Do not replace or rename the original campaign; the variant has its own `sest.world_sandbox_2028.regional` ID.

Scope: four European RED sites, six African access/detachment sites, five Middle Eastern sites, plus one additional PLA Gulf of Aden surface patrol. Fifteen scenario nodes, 25 additional forces (all RED), five patrols. No changes to BLUE or RED member-nation lists, purchases, existing base locations, or the original game campaign's force counts.

* Europe: Kronstadt, Chernyakhovsk, Krymsk and Pskov, bolstering Baltic, Black Sea and transport activity.
* Africa: Tobruk, Al-Khadim, Al-Jufra, Bamako, Niamey and Bangui. These are **fictional 2028 Russian operational detachments or access agreements**, not claims of Russian sovereignty or current air orders of battle. The Africa expansion is a **representative game scenario**, especially for host-state access.
* Middle East: Tartous, Hmeimim, Chabahar, Konarak and Shiraz. Syrian access is uncertain and is an explicit **scenario assumption**. Additional Iranian air and naval elements make the region more active.
* Gulf of Aden: additional Chinese escort and replenishment group at the existing Djibouti node.

All force identifiers come from the existing SEST collection and its prior purchase catalogue. Geocoordinates, aviation detachment strength and operational timing are authored game choices. No new third side, invented DLL support, free depot or endless spawned fleet is promised. Some sea patrol geometry is provisional and must pass geographical and game tests.

Source background:
- Russian presence in Libya: https://www.tearline.mil/public_page/libya-russia-develops-air-base-infrastructure-likely-to-secure-military-foothold-in-sahel-region
- Africa security relationships: https://www.everycrsreport.com/reports/IF12389.html
- Eastern Mediterranean access: https://www.al-monitor.com/originals/2026/09/russian-convoy-resupplies-syria-coastal-facilities-first-time-moscow-damascus
- Exact force allocations are not sourced from these references; they are **scenario fiction**.

Rebuild: `python tools/build_all.py --from-scratch`. This regenerates both campaigns and the merged SEST Integration Pack. Run `python -m unittest tools.tests.test_regional_expansion` and existing Python/PowerShell tests, and verify the generated tree has no changes. Then start this **variant as a new campaign** in Sea Power; do not use Continue from the original World Sandbox or overwrite its save. Confirm world start, RED purchases, patrols, service, combat, persistence and reload. No PC/game acceptance test has been performed.
