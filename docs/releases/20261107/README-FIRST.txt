SEST R12 - RIBBON EXPANSION
10 November 2026 | SEST-DEV
Runtime 1.6.3 / UI 1.4.13

WHAT IS NEW
The catalogue now contains 43 distinct awards across the world and authored
campaigns: 37 fictional SEST awards and six real-award representations.
Not every award belongs to every campaign or commander nationality.

- World Operations has 25 fictional awards for battle service, distinct
  battle days, theatre experience and completed accepted Admiralty duties.
  Open the world report, then Service. F11 still opens Combat Costs first.
- Native Task Force Service Records retain the four completion ribbons and
  add eight fictional operation ribbons across the authored campaigns.
- Southern Watch and Southern Reach add six Australian/US real-award
  representations, nation filters and modern fictional-operation citations.
  Australia remains the default. New commanders can also select US through
  native onboarding. Existing committed commanders keep their nationality.
- Existing world service progress and earned native award IDs are retained.
  The service file stays v1. Task service does not increase battle or USD
  counts, or add credits, renown or supplies.

RIBBONS.txt lists every qualification and where the awards appear.
R12-RIBBON-EXPANSION.txt contains the implementation and validation review.
The new displays and national award grants still need PC gameplay checks.

PREPARE AND CHECK
1. Close Sea Power. Keep SEST and the collection subscribed. Extract this
   COMPLETE toolkit into a NEW folder and run Prepare-PC.cmd. Keep the
   printed release checkout, backup path and verified UPLOAD FOLDER.
   Prepare-PC installs both code and campaign/loadout data; Repair-PC alone
   only repairs code. The author-update guard and original restore journal
   remain in place. Steam branch, subscriptions and saves are unchanged.
2. Load an existing world. Open the report and select Service. Check the
   existing awards/progress, longer ribbon list, scrolling and citations.
   Complete an accepted Admiralty order and return to the map. The order
   count should rise once; the battle count and combat USD totals must not.
3. Check new Australian and US commanders in Southern Watch or Southern
   Reach. The default stays Australian. Confirm the native Service Record
   shows the appropriate awards/citations after a qualifying mission result.
   A failed mission must not grant the mission award. Reopen the campaign
   to check persistence. Full mission mappings are in RIBBONS.txt.
4. Recheck the retained opening brief, world Combat Costs sidebar and direct
   F11 totals. In Starting Airborne Flights select the RAAF E/A-18G and
   confirm HARM (AGM-88C), AARGM (AGM-88E) and AARGM-ER (AGM-88G) choices.
   These three loadouts were data-tested previously; the revised selector
   still awaits an owner PC check. Quit the game after testing.
5. Run R12\Capture-Repair-Results.cmd and retain the capture. The automated
   checks passed; they do not establish native Noesis rendering or gameplay.

POST AFTER THE PC CHECKS
6. Run Upload-PC.cmd. It creates a verified publishing copy under
   StreamingAssets and puts STEAM-CHANGE-NOTE.txt on the clipboard. Keep
   this temporary Local mod disabled.
7. Open Sea Power > Mod Manager > Create Mod > Update Existing. Select
   Workshop item 3812461539 and the EXACT folder printed by Upload-PC.cmd.
   Paste the change note and submit. Confirm success and a non-zero size.
8. Update the page description with STEAM-PAGE-DESCRIPTION.txt (Steam BBCode).
   Separate short and collection copy is included if needed.
9. Quit and run Finish-Upload.cmd to move the temporary publishing copy out
   of the game. After Steam downloads the update, open the subscribed pack
   and run SETUP - double-click me.cmd with the game closed. This restores
   the reviewed features if Steam refreshed the normal plugin files.

RETAINED FEATURES
- Global Maritime Operations 2028: 196 bases, 293 force groups, 54 patrols
  and 1,586 recruitment entries; 40 added airfields and 37 reviewed positions.
- Eight coalition command stages, varied native Admiralty rewards and
  recruitment progression; no new base-construction mechanic is claimed.
- Paused battle preparation, clear native end-battle/debrief flow, readable
  opening brief, world-map Combat Costs and direct cumulative F11 USD totals.
- Three conventional Growler starting-flight fits, coordinated strike
  presentation, current Topography/Pop-Out support and Identify preservation.
- Reviewed beta features inside the normal Workshop SETUP flow, upgrade
  recovery and rollback. Normal active release plugins stay in the upload;
  the installer selects the five reviewed files for the supported beta.

The owner accepted the previous four briefing/costs/page changes on
9 November. This ribbon revision has not been played on that PC yet.
No Steam upload or GitHub push has been performed for this revision.
