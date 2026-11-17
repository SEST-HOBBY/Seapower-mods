# ENV-PC-PLAYTEST: Weather Lab, first environment gate

For the owner's Windows PC. About 45 minutes. Proves only that Sea Power applies
**scenario-wide** native weather changes at fixed times. It does not test spatial weather,
GCO, overlays or any physics effect. Nothing is marked PASS without the evidence listed.

## 0. Before

- Sea Power closed. Note the build: Steam > Sea Power > Properties > Betas (public beta or None).
- Python 3 installed (`py -3 --version`).
- Repository clone on branch `sest-dev/serene-bardeen-nvnmk9` (or the branch this lands on).
- The default game path is `C:\Program Files (x86)\Steam\steamapps\common\Sea Power`; if yours
  differs, add `-GameRoot 'D:\real\path\Sea Power'` to every command below.

## 1. Offline checks (no game)

```powershell
py -3 -m unittest discover -s integration\environment\tests -t integration\environment\tests
```

Expected: `Ran 79 tests ... OK` (a few vanilla tests skip only if the repository export is missing).

## 2. Build, inspect, install

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Mission Hormuz -MissionTime 10,0
```

Expected: a JSON summary, `Vanilla source unchanged: <hash>`, and
`Built (not installed): ...\integration\environment\out\MNO-Environmental-Playtest`. Open its
`PLAYTEST_META.json`: `source_sha256`, `mission_sha256`, eight stages at 0, 300 ... 2100 s.
`-MissionTime 10,0` starts the mission at 10:00 local so the sky is visible (Hormuz starts at
02:20 otherwise). Then:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Mission Hormuz -MissionTime 10,0 -Install
```

Expected: `Installed: ...\Sea Power_Data\StreamingAssets\content\MNO-Environmental-Playtest`.
The script refuses if that folder already exists.

## 3. In the game

Start Sea Power. If the Mod Manager lists "MNO - Environmental Playtest", enable it. Open
Scenarios and start **MNO Weather Lab: Hormuz**. Leave time compression at 1x for the first two
stages, then you may use up to 4x (note the setting). Screenshot each stage from the same camera.

| Test | Mission time | Expect | Record |
|---|---|---|---|
| W1 | 0:00 | Broken clouds, sea state 3, dry; the scenario's ships, briefing and start message as in normal Hormuz | screenshot, PASS/FAIL |
| W2 | 5:00 | Broken_3, sea 4, rain starts | screenshot |
| W3 | 10:00 | Overcast, sea 5, rain | screenshot |
| W4 | 15:00 | Overcast, sea 7, rain, thunderstorm (lightning) | screenshot |
| W5 | 20:00 | Overcast, sea 8, rain, fog, thunderstorm. Note the wave height you see: this is the first evidence for the SeaState-to-wave mapping | screenshot, your estimate in metres |
| W6 | 25:00 | Broken_3, sea 6, rain and fog continue, no thunderstorm | screenshot |
| W7 | 30:00 | Broken_2, sea 4, dry, fog clears | screenshot |
| W8 | 35:00 | Scattered, sea 2, dry | screenshot |
| W9 | any | Hormuz's own weather changes (40, 80, 120, 140 min) do not happen | note |
| W10 | to the end | Objectives, convoy and end-of-mission work as in normal Hormuz | note |
| W11 | after | Exit, start normal Hormuz: its own weather (Broken, sea 4), not the lab's last state | screenshot |
| W12 | after | A GCO or authored campaign mission starts with its own weather | note |

## 4. Logs

After closing the game, keep:

- `%USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\Player.log`
- `<game>\BepInEx\LogOutput.log`
- `out\MNO-Environmental-Playtest\PLAYTEST_META.json`
- the screenshots.

Send them with the W1-W12 results. A stage that did not change is a FAIL with its screenshot.

## 5. Remove

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Uninstall
```

It removes only `Sea Power_Data\StreamingAssets\content\MNO-Environmental-Playtest`, and only if
its `PLAYTEST_META.json` is a Weather Lab receipt. It never touches `original\`, MNO, R15 or
Workshop folders. Breakthrough: repeat with `-Mission Breakthrough` (uninstall first).

## Rollback

Nothing else was changed. If the game misbehaves after the test, run `-Uninstall` and verify the
folder is gone; the vanilla mission's hash printed in step 2 can be compared with
`Get-FileHash` at any time.
