# PC playtest, step by step (environment layer, 19 Nov 2026)

For the owner's Windows PC with Sea Power 0.9.3. Everything here installs **one test mission file at most**, removes it
again, and never touches vanilla files, R15, Steam or the Workshop. Nothing is "tested in game" until you record what
you saw.

You need about 1 hour for steps 1-6. Step 2 is a background download that runs by itself for about 2 hours a day.

Commands go into **Windows PowerShell** (Start menu, type PowerShell, Enter). Paste one block at a time.

---

## Step 0 - Before you start (2 min)

1. Close Sea Power.
2. Check Python and git:

   ```powershell
   py -3 --version
   ```

   ```powershell
   git --version
   ```

   You need Python 3.10 or newer and any git. If Python is missing, install it from python.org with "Add to PATH" ticked.
3. Start Sea Power once and note the build string on the main menu (expected 0.9.3 Build 261116). Then close it again.
4. Note whether Options > Gameplay > "Restrict air ops by sea state" is on.

---

## Step 1 - Get the latest work into its own folder (3 min)

This uses a separate folder, `Seapower-mods-env`, so your normal clone is not touched.

**If you have never made the folder:**

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Seapower-mods"
git fetch origin sest-dev/serene-bardeen-nvnmk9
git worktree add "$env:USERPROFILE\Seapower-mods-env" FETCH_HEAD
```

**If you already have it** (you do: it was used for the weather download):

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Seapower-mods"
git fetch origin sest-dev/serene-bardeen-nvnmk9
git -C "$env:USERPROFILE\Seapower-mods-env" checkout --detach origin/sest-dev/serene-bardeen-nvnmk9
```

**Then go into the folder** (do this in every new PowerShell window):

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Seapower-mods-env"
```

**Optional self-check** (about 3 minutes, offline):

```powershell
py -3 -m unittest discover -s integration\environment\tests -t integration\environment\tests
```

Expect `Ran 157 tests ... OK`. Some may be "skipped" if a file only present here is missing. That is fine.

---

## Step 2 - Resume the GCO real-weather download (background, 2-2.5 h)

Open a **second** PowerShell window, go into the folder (the `Set-Location` line from step 1), and check progress:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-GCO-WEATHER.ps1 -Status
```

Then start the day's download and leave that window open:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-GCO-WEATHER.ps1
```

- What you already downloaded stays valid. Since 19 Nov the plan covers 24 chokepoints for the whole year and the polar
  seas, so a full year takes about 11 daily runs instead of 6.
- It stops by itself at the free daily limit, and it waits through the per-minute and per-hour limits.
- Shutting the PC down mid-run is safe: the next run continues where it stopped.
- When it prints COMPLETE (or whenever you want to send what you have):

  ```powershell
  powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-GCO-WEATHER.ps1 -Package
  ```

  It puts a ZIP in Downloads. Its name ends `-PARTIAL` if the download is not finished.

Nothing is installed into the game by this step.

---

## Step 3 - Weather Lab: does the game apply weather changes? (10 min)

Back in the first window (in the folder):

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick
```

It copies one file, `MNO Weather Lab - Hormuz.ini`, into `...\StreamingAssets\user\missions\user_missions\`. If it
says the file already exists, run the `-Uninstall` line from step 6 first.

In the game:
1. Open the user/custom missions list.
2. Start **MNO Weather Lab: Hormuz**. Stay at 1x speed and watch the sky and sea for 8 minutes.
3. Take a screenshot at each change if you can.

| # | Mission time | Expect |
|---|---|---|
| H-W1 | 0:00 | Broken clouds, sea state 3, dry |
| H-W2 | 1:00 | Broken_3, sea 4, rain starts |
| H-W3 | 2:00 | Overcast, sea 5, rain |
| H-W4 | 3:00 | Overcast, sea 7, rain, thunderstorm |
| H-W5 | 4:00 | Overcast, sea 8, rain, fog, thunderstorm. **Estimate the wave height in metres** and read "Ocean Noise" in the weather panel if shown |
| H-W6 | 5:00 | Broken_3, sea 6, rain and fog, no thunderstorm |
| H-W7 | 6:00 | Broken_2, sea 4, dry, fog clears |
| H-W8 | 7:00 | Scattered, sea 2, dry |
| W11 | after | Quit to the menu and start the normal Hormuz mission: it must have its own weather (Broken, sea 4), not the lab's last state |

If the mission is not in the list at all, write that down. It is a result in itself.

Then, **game closed**, uninstall before step 4:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -CollectLogs
```

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Uninstall
```

---

## Step 4 - Weather Lab: the model's own weather (10 min)

The same lab, driven by procedural weather model v7 at Hormuz's map centre:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick -Mode procedural
```

The expected stages are printed in
`integration\environment\out\Hormuz-<time>\MNO-Environmental-Playtest\PLAYTEST_META.json` (the `stages` list).
For Hormuz in July, expect a quiet summer Gulf day: scattered cloud, sea state 2-3, dry.

- Play it as in step 3 and check that each stage matches the file.
- Write down anything that looks wrong, for example haze or wind direction.

Then collect and uninstall as at the end of step 3.

**Optional:** the weather actually recorded at Hormuz on the mission's own date (needs internet once):

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Quick -RealWeather
```

---

## Step 5 - Sensor checks with the existing weather keys (20-30 min, optional)

These answer what the game itself does with weather (docs/environment/SENSOR-PC-TESTS.md). Build each test once in the
Mission Editor and save it as a **new** user mission. Change only the setting named. Record only what you observe.

| # | Set up | Measure |
|---|---|---|
| S-RAIN | Deep water, night, no fog, your frigate with radar off, and a submarine or loud merchant closing from about 15 nm | Range of first passive sonar contact with Weather Rain **off**, then **on**, then Thunderstorm alone |
| S-FOG | Same, but a small boat closing in daylight | First visual/optical detection range with Fog off and on; whether a helicopter launch is refused; any change in bombing accuracy |
| S-SEA | Your frigate with a helicopter, SeaState 3, then 6 | Whether launch is refused (the message names the sea state); the "Ocean Noise" value in the weather panel at each |
| S-LAYER | Water deeper than 1000 m. Read the "Layer" depth, then put a submarine at least 30 m below it, 8 nm from your frigate | Hull-sonar detection with LayerDisabled False, then True |

Write one line per test, for example: `S-RAIN: no rain 14 nm, rain 9 nm, thunderstorm only 14 nm`.

---

## Step 5b - File-layer probes: can a mission carry its own sonar settings? (20-40 min, optional)

These tests decide whether the per-mission `[Sonar]` overrides suggested in the sensor brief can ever reach the game.
Each probe writes a few files and `-Uninstall` removes exactly those. A probe never overwrites anything, and the
game must be closed for install and uninstall. Do them **in order**, and stop at the first one that shows nothing.

**1. Scan** (no change to the game; about 1 minute):

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Scan
```

It reads the game's script assembly (names only; nothing is run), lists every `overrides` folder in your mods, and
records your installed `environment.ini`. Send the `Downloads\MNO-LayerProbe-scan-<time>.zip` it makes. The folder
names a per-mission layer uses are likely to be in it, which replaces the guesses in B1-B3.

**2. Probe A-mod: does a mod layer work, and does it merge by key?**

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install A-mod
```

1. Open the Mod Manager and enable **MNO Layer Probe A**, then Apply.
2. In the Mission Editor, the F-14A should read **F-14A MNO-PROBE-A**.
3. Check that other aircraft still have their normal names. If names went blank, layers replace whole files.

Then close the game and uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall A-mod
```

**3. Probe A2: does a layer merge `environment.ini` by key?** This one is GLOBAL while it is installed.

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install A2
```

1. Enable **MNO Layer Probe Env** in the Mod Manager.
2. In a deep-water mission, passive sonar ranges should collapse (+30 dB ambient noise).
3. Night lighting, sky and fog must look normal. If they do not, the file replaced environment.ini whole: close the
   game and uninstall at once.

Then uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall A2
```

**4. Probes B1, B2, B3: where does a per-mission layer go?**

Install the Weather Lab first (step 3 above), then try B1, B2 and B3 **one at a time**:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install B1
```

1. Start **MNO Weather Lab: Hormuz**. Its Belknap-class cruiser should read **... MNO-PROBE-B1**.
2. Then start a vanilla mission in the same session. Names must be normal there.
3. Close the game and run `-Uninstall B1`.
4. Repeat with B2 and B3. If the scan found a different folder name, you will be given a `-Template` line instead.

**5. Probe C: does a per-mission `environment.ini` work?** Only if a B probe worked; use the B that worked:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install C -From B1
```

1. Before loading, check the game starts without errors.
2. In the Weather Lab mission, passive ranges collapse. Night, sky and fog must stay normal.
3. Then load a vanilla deep-water mission **without restarting**: detection must be normal there (no leak).
4. Close the game and run `-Uninstall C`. If C broke night, sky or fog, try `-Install D -From B1` (a full copy).

**When done, or at any point:**

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Status
```

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall all
```

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Collect
```

`-Collect` makes `Downloads\MNO-LayerProbe-results-<time>.zip`. Write one line per probe in its `RESULTS.txt`, for
example `A-mod: F-14A renamed, others normal` or `B1: not seen`.

---

## Step 6 - Send results and clean up (5 min)

1. Game closed. If you did not already collect logs after each lab run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -CollectLogs
   ```

   It writes `Downloads\MNO-WeatherLab-results-<time>.zip`. Open the `RESULTS.txt` inside and fill in the H-W numbers
   (step 3), the procedural stages (step 4) and any S- lines (step 5). If short on time, just reply with the numbers
   that did **not** happen, for example "H-W4, H-W5 fog".
2. Remove the test mission:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Uninstall
   ```

3. Delete any S- test missions you saved in the Mission Editor.
4. Send the results ZIP, plus the GCO weather ZIP from step 2 when you package it.

## If something goes wrong

- "StreamingAssets was not found": add `-StreamingAssetsDir 'D:\...\Sea Power_Data\StreamingAssets'` to the command.
- "Python 3 is required": install Python from python.org with "Add to PATH" ticked, then open a new PowerShell window.
- "Builder refused": copy the message. It names the rule that stopped it, and nothing was installed.
- "file already exists": run the `-Uninstall` line, then try again.
- The GCO download says it is waiting: that is the free limit. Leave it running or come back tomorrow.

## Rollback

At most one file is ever added to the game: `user_missions\MNO Weather Lab - Hormuz.ini`. `-Uninstall` removes it, and
deleting it by hand is equally safe. The GCO download only writes inside the `Seapower-mods-env` folder and Downloads.
