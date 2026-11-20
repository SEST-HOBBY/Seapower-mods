# PC playtest, step by step (environment layer, 19 Nov 2026)

For the owner's Windows PC with Sea Power 0.9.3. Steps 3-6 install **one test mission file at most** and remove it
again. Optional step 5b also adds small probe mods and `overrides` folders, which `RUN-LAYER-PROBE.ps1 -Uninstall all`
removes. Nothing here touches vanilla files, R15, Steam or the Workshop. Nothing is "tested in game" until you record what
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

Expect `Ran 164 tests ... OK`. Some may be "skipped" if a file only present here is missing. That is fine.

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
| H-W1 | 0:00 | Broken clouds, sea state 3, dry. If you will do step 5b, write down "Ocean Noise" from the weather panel now: it is the baseline (expect about 75 dB) |
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

## Step 5b - File-layer probes: can a mission carry its own sonar settings? (30-60 min, optional)

These tests decide whether the per-mission `[Sonar]` overrides suggested in the sensor brief can ever reach the game.
Each probe writes a few files, and `-Uninstall` removes exactly those. A probe never overwrites anything. Install and
uninstall only with the game **closed**.

Rules for the whole session:
- One probe at a time: install, start the game, look, quit, uninstall.
- Restart the game after every install. If you see nothing, restart once more and look again before writing "not seen".
- Write one line per probe as you go (Notepad is fine). `-Status` shows what is installed and what to look for.

**1. Scan** (changes nothing; about 1 minute):

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Scan
```

It reads names from the game's code file `Seapower-Scripts.dll` (nothing is run). It also lists every `overrides`
folder in your mods and records your installed `environment.ini`. It makes `Downloads\MNO-LayerProbe-scan-<time>.zip`.
Send that ZIP now if you can: it may name the real per-mission folder, which would replace B1-B3 with one command.

**2. Probe A-mod: does a mod layer work, and how does it merge?**

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install A-mod
```

1. Start the game. Open the Mod Manager, enable **MNO Layer Probe A**, drag it to the **top** of the list (top wins),
   and Apply. Quit and start the game again.
2. In the Mission Editor, place a US carrier and open its air wing, or add an F-14A. The F-14A's name should read
   **F-14A MNO-PROBE-A**.
3. Open the F-14A's description and its squadron choice (VF-14 'Top Hatters' and so on), then look at a few other
   aircraft. Write down which of these you see:
   - Tag shown, F-14A description and squadrons intact, other aircraft normal: layers merge **by key**.
   - Tag shown, F-14A description or squadrons gone: layers replace **whole sections**.
   - Other aircraft names blank: layers replace **whole files**.
4. If the tag does not show after a second restart, also try once with mod 3458148344 (Mi-8EW) disabled. It ships
   its own F-14A name.
5. Disable the probe in the Mod Manager, Apply, quit the game, then uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall A-mod
```

If A-mod showed nothing, try **A-user1**, then **A-user2**, the same way, but with no Mod Manager step. Look for
**F-14A MNO-PROBE-U1** or **-U2**, and uninstall each before the next. Stop step 5b only if all three show nothing.

**3. Probe A2: is `environment.ini` layered at all?** It is GLOBAL while installed: it changes sonar in every mission.

1. Baseline first, with no probe installed: install the Weather Lab (step 3) and start **MNO Weather Lab: Hormuz**.
   Before **1:00** mission time (sea 3, dry), write down "Ocean Noise" from the weather panel and the range of the
   first passive sonar contact. After 1:00 the lab's own rain and sea state change the noise, so readings then prove
   nothing. If you already wrote these down in step 3, reuse them.
2. Install the probe:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install A2
   ```

3. Enable **MNO Layer Probe Env** in the Mod Manager, drag it to the top, Apply, and restart.
4. Start the Weather Lab again. Before 1:00, Ocean Noise should be about **30 dB above** your baseline, and the first
   contact much closer.
5. Night lighting, sky and fog must look normal. If they do not, the file replaced environment.ini whole: quit at once
   and uninstall.
6. This probe cannot tell a key merge from a section merge: the A-mod result answers that.
7. Disable the probe, Apply, quit, then uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall A2
```

**4. Probes B1, B2, B3: where does a per-mission layer go?** Run these whatever A2 showed. The Weather Lab must be
installed (step 3). Try them **one at a time**:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install B1
```

1. Start **MNO Weather Lab: Hormuz** and select the player's lead cruiser. The class should read
   **Belknap-class MNO-PROBE-B1** and the name **Fox CG-33 MNO-PROBE-B1**.
2. Without restarting, start the vanilla **NATO > Hormuz** mission. It has the same ship, which must read
   "Belknap-class" / "Fox CG-33" with **no** tag. A tag there is a leak: write it down.
3. Quit the game and uninstall:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall B1
   ```

4. Repeat with `-Install B2` / `-Uninstall B2`, then B3, and look for MNO-PROBE-B2 / -B3. If the scan finds a
   different folder name, you will get a `-Template` line instead.

**5. Probe C: does a per-mission `environment.ini` work?** Only if a B probe worked. Use the B that worked, here B1:

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install C -From B1
```

1. Start the game and check that it reaches the menu with no new error message.
2. Start the Weather Lab. Before 1:00, Ocean Noise should be about **30 dB above** the baseline from step 3 above.
   Night, sky and fog must look normal.
3. Without restarting, start the vanilla **NATO > Hormuz** mission. Ocean Noise must be back to normal there; if it is
   not, write down the leak.
4. Quit and uninstall:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall C
   ```

5. If C broke night, sky or fog, repeat with a full copy instead:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Install D -From B1
   ```

   Then check it the same way and run `-Uninstall D`.

**6. Finish** (game closed):

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Status
```

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall all
```

```powershell
powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Collect
```

`-Collect` makes `Downloads\MNO-LayerProbe-results-<time>.zip` (manifest, scans, Player.log) and, next to it,
`...-RESULTS.txt`. Fill in the RESULTS.txt in Notepad with one line per probe, for example
`A-mod: tag shown, F-14A squadrons intact, others normal` or `B1: not seen after restart`. Alternatively, reply with
those lines.

---

## Step 6 - Send results and clean up (5 min)

1. Game closed. If you did step 5b, uninstall every probe **before** removing the Weather Lab: first disable MNO Layer
   Probe A / Env in the Mod Manager if they are still enabled, then:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-LAYER-PROBE.ps1 -Uninstall all
   ```

   If you did not already collect logs after each lab run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -CollectLogs
   ```

   It writes `Downloads\MNO-WeatherLab-results-<time>.zip` and `...-RESULTS.txt` next to it. Fill in that RESULTS.txt
   in Notepad (not the copy inside the ZIP) with the H-W numbers
   (step 3), the procedural stages (step 4) and any S- lines (step 5). If short on time, just reply with the numbers
   that did **not** happen, for example "H-W4, H-W5 fog".
2. Remove the test mission:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\integration\environment\RUN-WEATHER-LAB.ps1 -Uninstall
   ```

3. Delete any S- test missions you saved in the Mission Editor.
4. Send:
   - the Weather Lab results ZIP and its RESULTS.txt;
   - the GCO weather ZIP from step 2, when you package it;
   - if you did step 5b, `MNO-LayerProbe-scan-<time>.zip`, `MNO-LayerProbe-results-<time>.zip` and its RESULTS.txt.

## If something goes wrong

- "StreamingAssets was not found": add `-StreamingAssetsDir 'D:\...\Sea Power_Data\StreamingAssets'` to the command.
- "Python 3.10 or newer is required": install Python from python.org with "Add to PATH" ticked, then open a new PowerShell window.
- "Builder refused": copy the message. It names the rule that stopped it, and nothing was installed.
- "file already exists": run the `-Uninstall` line, then try again.
- The GCO download says it is waiting: that is the free limit. Leave it running or come back tomorrow.

## Rollback

Steps 3-6 add one file, `user_missions\MNO Weather Lab - Hormuz.ini`. `RUN-WEATHER-LAB.ps1 -Uninstall` removes it, and
deleting it by hand is equally safe.

Step 5b adds only the files each probe records in `integration\environment\out\layer-probes\manifest.json`:
- the mod folders `StreamingAssets\MNO_LayerProbe` and `StreamingAssets\MNO_LayerProbeEnv` (the second changes sonar
  in every mission while enabled);
- `user\overrides\...` and `user\language_en\aircraft_names.ini` (A-user1 and A-user2);
- folders next to the Weather Lab mission (B1-B3, C and D).

`RUN-LAYER-PROBE.ps1 -Uninstall all` deletes them and any folders it made. It refuses a file you edited, and says
so. If the Mod Manager still lists a probe mod afterwards, disable it there. The GCO download only writes inside the `Seapower-mods-env` folder and Downloads.
