# World Sandbox 2028 Regional Expansion: PC check, 24 October 2026

This build is the World Sandbox branch, `feature/world-sandbox-regional-expansion-20261024` (PR #44, merged into `sest-dev/jolly-ride-rptj4t` on 24 Oct as `8fd13774`), with all of `sest-dev/jolly-ride-rptj4t` merged in. It includes everything in `campaign-costs-panel-20261024.md`, whose steps still apply. Only its start has been seen (Result, below); static checks are not a game test. Never overwrite an existing save.

## Install

1. Close Sea Power. Run the playtest installer from this ZIP against your clone, then check the green `IN LINE` commit and file count (4,297).
2. Enable Anchor Chain, Dynamic Campaign Mod 0.25.0, Combat Cost Tracker and SEST, then restart the game fully.

## The campaigns

3. The Campaign menu lists both *SEST World Sandbox 2028 (draft)* and *SEST World Sandbox 2028 - Regional Expansion (preview)*.
4. Start **Regional Expansion** as a **new** campaign. START CAMPAIGN must reach the strategic map with no "this game has no ..." error. Repeat as RED.
5. Start the original World Sandbox as a new campaign too: it still starts. If you have an old World Sandbox save, open a **copy** of it and check that it loads.

## In the Regional Expansion

6. As RED, check these appear and can take orders:
   - the new bases: Kronstadt, Chernyakhovsk, Krymsk, Pskov, Tobruk, Al-Khadim, Al-Jufra, Bamako, Niamey, Bangui, Tartous, Hmeimim, Chabahar, Konarak and Shiraz;
   - their forces;
   - purchases at those bases.
7. Let several days pass:
   - the Baltic, Tobruk, Tartous, Makran and Gulf of Aden patrols follow their routes;
   - aircraft at the new air bases fly;
   - nothing spawns endlessly;
   - the world does not end early.
8. **Replenishment.** Bring a regional surface group within 5 NM of the Pashin (Tobruk or Tartous) or the Delvar (Chabahar). Its fuel and ammunition rise, the supply ship's cargo falls, and nothing restocks for free.
9. **A battle.** Let a contact become a battle. The forces match the map, and survivors, losses and ammunition expended come back to it.
10. **Persistence.** Save, quit to the menu, reload. Positions, damage, purchases, fuel, stocks and losses survive. Run more than one combat and supply cycle.

## Result, 24 October 2026

The owner's report on the live Workshop build (`8e72f353`, 4,297 files). It was a yes, with no log or screenshot:

- **Step 4: pass.** Regional Expansion starts as a new campaign.

Not reported: playing it as RED, step 3's listing of the original, and steps 5 to 10 (the original's start, the new bases, patrols, replenishment, a battle, saves).

## What to send

The `IN LINE` commit and count, the step number, screenshots of any error, `Player.log` and `BepInEx/LogOutput.log`.
