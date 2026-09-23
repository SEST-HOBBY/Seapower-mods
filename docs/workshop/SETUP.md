# Setup, step by step: from this branch to the Steam Workshop

Everything runs on the gaming PC, in PowerShell, from the repo root
(`cd <path>\Seapower-mods`). **Keep Sea Power closed unless a step tells you
to launch it.**

---

## Part A: get the new build onto the PC

**1. Switch to the release branch.** This work is on `sest-dev/peaceful-gauss-e1zvfq`,
which is your deploy branch (`feature/northern-front-iii-export`) plus the Workshop
and briefing-map commits.

```powershell
git fetch origin
git checkout sest-dev/peaceful-gauss-e1zvfq
git pull
```

**2. Install and set the mod order.** `-AnyBranch` is needed because
`data\deploy-branch.txt` still names the old branch; `sync-sest` refuses other
branches without it.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1 -AnyBranch -SkipPull
```

Watch for these lines in the output:

- `briefing   SEST Banda - ... _briefing`, 13 of them. The map folders landed.
- `IN LINE` at the end. The deployed pack matches the build.

**3. Run the pre-flight checks.** Each one must end without errors.

```powershell
python tools\check_load_order.py
python tools\check_dependencies.py
python tools\preflight.py
```

---

## Part B: test in game

**4. Launch Sea Power.** In the Mod Manager, confirm **SEST Integration Pack** is
enabled and at the **very top**.

**5. Open a SEST mission.** In the mission list, open **SEST Banda - Viper Zero**.

- Left pane: the briefing text (this already worked).
- **Right pane: the new map.** It shows the landing group in the Karimata Strait,
  the Kendawangan industrial park on the Kalimantan coast, and VIPER x4 to the south-west.

If the right pane is **still blank**, stop here and report it. The map image's
name or format then needs adjusting before anything goes on the Workshop.

**6. Play one mission to the end.** Viper Zero is a good one to check, because its
positions just moved. You win by sinking the Type 071.

**7. Quit the game.**

---

## Part C: build the Workshop upload folders

**8. Stage both items.**

```powershell
python tools\build_workshop.py
```

This creates, inside `integration\workshop\staging\`:

| Folder | Becomes |
|---|---|
| `SEST_Integration\` | Workshop item 1: *Definitive Modernised Seapower - SEST Integration Pack* |
| `SEST_Southern_Watch\` | Workshop item 2: *Southern Watch* (13 missions + their briefing maps) |

**9. Make two preview images.** Each should be square, PNG and under 1 MB. Save them as
`preview.png` in each staging folder. A cropped briefing map works well for the campaign:
`integration\missions\SEST Banda - Fujian's Shadow_briefing\sest_fujian_s_shadow_map.png`.

---

## Part D: publish the pack (item 1)

**10. Remove the locally installed pack** so the game doesn't list two copies:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1 -Uninstall
```

**11. Copy** `integration\workshop\staging\SEST_Integration\` into
`...\Sea Power_Data\StreamingAssets\`.

**12. Upload it** with the game's Workshop upload tool. Use:

- **Title:** `Definitive Modernised Seapower - SEST Integration Pack`
- **Description:** the BBCode block in `docs\workshop\definitive-modernised-seapower.md`
- **Visibility:** **Unlisted** for now

**13. Add the Required Items.** On the new item's Steam page, open **Add/Remove Required
Items** and add all 46 from the table in that same doc.

**14. Write down the new Workshop ID.** It's the number in the item's URL.

---

## Part E: publish the campaign (item 2)

**15. Copy** `integration\workshop\staging\SEST_Southern_Watch\` into
`StreamingAssets\` and upload it the same way:

- **Title:** `Southern Watch - A Definitive Modernised Seapower Campaign`
- **Description:** the BBCode block in `docs\workshop\southern-watch.md`
- **Visibility:** **Unlisted**

**16. Add the Required Items.** Add the 25 listed mods, plus **the pack from step 14**.

---

## Part F: test like a player, then go public

**17. Remove the local copies** you made in steps 11 and 15 from `StreamingAssets\`.

**18. Subscribe to both items** from their Steam pages and accept the prompt to
subscribe to their Required Items.

**19. Launch the game.** Move the pack to the top of the Mod Manager and check that
**SEST Southern Watch** appears in the mission list with maps on its briefings. Play
one mission.

**20. Set both items to Public.**

**21. Create the collection.** On the Workshop, choose **Create Collection** and name
it *Definitive Modernised Seapower*. Add the two SEST items first, then the mods listed in
`docs\workshop\collection.md`, and publish it.

---

## Part G: after publishing

**22. Point the load order at the Workshop copy.** The pack's load-order token changes
from `SEST_Integration` to its new Workshop ID. Say so in a session and the repo side
(`data\load-order.tokens.txt`, the checkers, `install-sest-packs.ps1`) gets updated
to match. Until then, don't run `sync-sest`: it would reinstall the local copy next
to the subscribed one.

**23. For updates:** rebuild (`python tools\build_all.py`, then
`python tools\build_workshop.py`) and re-upload the changed item to the **same**
Workshop ID.
