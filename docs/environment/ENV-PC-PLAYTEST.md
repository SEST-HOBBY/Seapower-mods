# ENV-PC-PLAYTEST: Weather Lab, first environment gate (PC-08)

For the owner's Windows PC. Proves only that Sea Power applies **scenario-wide** native weather
changes at fixed times. It does not test spatial weather, GCO, overlays or any physics effect.
Nothing is marked PASS without the evidence listed.

## Quick version (about 10 minutes)

Close Sea Power. Open **Windows PowerShell** (Start menu, type PowerShell, Enter) and paste the
blocks below one at a time. They put this branch in its own folder,
`C:\Users\<you>\Seapower-mods-env`, so your normal clone `Seapower-mods` and its branch are not
touched.

**First time only** (makes the separate folder):

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Seapower-mods"
git fetch origin sest-dev/serene-bardeen-nvnmk9
git worktree add "$env:USERPROFILE\Seapower-mods-env" FETCH_HEAD
```

**Later, to pick up new work** (instead of the block above):

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Seapower-mods"
git fetch origin sest-dev/serene-bardeen-nvnmk9
git -C "$env:USERPROFILE\Seapower-mods-env" checkout --detach FETCH_HEAD
```

**Every time**, go into that folder:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Seapower-mods-env"
```

Then pick **one** test and paste it:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick
```

(scripted test front: the table below), or

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick -RealWeather
```

(the weather that was **recorded** at Hormuz's map centre on the scenario's own date, 21 July
1987, from 10:00 local: ECMWF ERA5 reanalysis and ERA5 ocean waves, one real hour per minute;
needs internet for one download), or

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick -Forecast
```

(today's ECMWF forecast at the same place).

Each finds the game through Steam, reads the installed Hormuz mission (never writes to it),
and copies one file, `MNO Weather Lab - Hormuz.ini`, into
`Sea Power_Data\StreamingAssets\user\missions\user_missions\`. It refuses if that file
already exists (run `-Uninstall` first, below). For the real-weather runs the expected stages
are printed in `integration\environment\out\Hormuz-<time>\MNO-Environmental-Playtest\PLAYTEST_META.json`;
the table below is for the scripted `-Quick` run.

In the game: open the user/custom missions list, start **MNO Weather Lab: Hormuz**, stay at
1x, and watch the sky and sea for 8 minutes. Take a screenshot at each change if you can.

| Test | Mission time | Expect |
|---|---|---|
| W1 | 0:00 | Broken clouds, sea state 3, dry |
| W2 | 1:00 | Broken_3, sea 4, rain starts |
| W3 | 2:00 | Overcast, sea 5, rain |
| W4 | 3:00 | Overcast, sea 7, rain, thunderstorm |
| W5 | 4:00 | Overcast, sea 8, rain, fog, thunderstorm: **guess the wave height in metres** |
| W6 | 5:00 | Broken_3, sea 6, rain and fog, no thunderstorm |
| W7 | 6:00 | Broken_2, sea 4, dry, fog clears |
| W8 | 7:00 | Scattered, sea 2, dry |
| W11 | after | Quit to menu, start normal Hormuz: its own weather (Broken, sea 4), not the lab's last state |

Then, game closed, from the same folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -CollectLogs
```

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Uninstall
```

`-CollectLogs` writes `Downloads\MNO-WeatherLab-results-<time>.zip` (Player.log, BepInEx log, the
build receipt, a RESULTS.txt to fill in). If short on time, just reply with which W numbers did
not happen. `-Uninstall` removes only the Weather Lab file, and only if it still matches the
build receipt.

If the mission is not in the list: say so, and send the ZIP. That alone tells us whether the
`user_missions` route works on 0.9.3.

## Full version (about 45 minutes, later)

Same commands without `-Quick`, with `-Install -MissionTime 10,0`: stages are 5 minutes apart,
so you can also check:

| Test | Expect |
|---|---|
| W9 | Hormuz's own weather changes (40, 80, 120, 140 min) do not happen |
| W10 | objectives, convoy and end of mission work as in normal Hormuz |
| W12 | a GCO or authored campaign mission afterwards starts with its own weather |

Breakthrough: `-Mission Breakthrough` (uninstall the Hormuz file first, or both can coexist:
the names differ). Procedural weather instead of the scripted front: `-Mode procedural`.

## If something goes wrong

- *"StreamingAssets was not found"*: add `-StreamingAssetsDir 'D:\...\Sea Power_Data\StreamingAssets'`.
- *"Python 3 is required"*: install Python from python.org with "Add to PATH" ticked.
- *"Builder refused"*: copy the message; it names the rule that stopped it. Nothing was installed.
- Offline checks, if you want them: `py -3 -m unittest discover -s integration\environment\tests -t integration\environment\tests` (expect `Ran 80 tests ... OK`).

## Rollback

Only one file is ever added. `-Uninstall` removes it; deleting
`user_missions\MNO Weather Lab - Hormuz.ini` by hand is equally safe. Vanilla files, MNO, R15 and
Workshop folders are never written.
