# MNO development: PC session, 24 Nov 2026

This session collects what the next build (R16, branch `feature/mno-r16`) needs. **It installs nothing new.** Your current install (GPT's 22:12 package) stays as it is, and you can keep playing it.

Use Windows PowerShell and paste one block at a time. Keep the game closed unless a step says otherwise.

**Do not run `Upload-PC.cmd`, ever.**

| Step | What | Time | Send me |
|---|---|---|---|
| 1 | Remove the Arctic preview | 1 min | Nothing |
| 2 | Find GPT's 22:12 source bundle | 2 min | The file |
| 3 | Find the 0.9.2 reference ZIP | 2 min | The file |
| 4 | Fresh mod capture | 10–20 min | The capture ZIP |
| 5 | Photo download kit | 10–30 min | Results ZIP and notes |
| 6 | Optional: the render mod | 1 min | Its Workshop ID |

---

## 0. Before you start

1. Close Sea Power.
2. In Steam, open **Library → Downloads** and let every Sea Power and Workshop download finish.

## 1. Remove GPT's Arctic preview

The preview changed `sest_runtime.ini` inside the MNO Workshop folder. Removing it first keeps the capture clean.

```powershell
Get-ChildItem -LiteralPath "$env:USERPROFILE\Downloads" -Recurse -File -Filter "3-Remove-Preview.cmd" -ErrorAction SilentlyContinue | Select-Object FullName
```

Double-click the file it lists. Wait for it to finish, then confirm the preview block is gone:

```powershell
Select-String -LiteralPath "C:\Program Files (x86)\Steam\steamapps\workshop\content\1286220\3812461539\plugins\sest_runtime.ini" -Pattern "MNO Arctic Preview"
```

**Expect no output.** If it prints a line, send it to me and skip to step 2.

## 2. GPT's 22:12 source bundle

GPT's last source (revision `089527cfa`) exists only inside its toolkit. I need it to bring the GCO/GSCO names and map limits across exactly.

```powershell
Get-ChildItem -LiteralPath $env:USERPROFILE -Recurse -File -ErrorAction SilentlyContinue -Include *.bundle,*source*.zip,*Source*.zip,*.patch | Where-Object { $_.FullName -match 'MNO|GSCO|2212|R15' } | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
```

- If one file looks right (a `.bundle`, or a ZIP with "source" in its name), upload it.
- If nothing shows, find the extracted 22:12 toolkit folder and list its top level:

```powershell
Get-ChildItem -LiteralPath $env:USERPROFILE -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '2212' } | Select-Object FullName
```

Send me that output.

## 3. The 0.9.2 reference ZIP

```powershell
Get-ChildItem -LiteralPath $env:USERPROFILE -Recurse -File -Filter "SEST-Beta-References-20261114*" -ErrorAction SilentlyContinue | Select-Object FullName, Length
```

Upload `SEST-Beta-References-20261114-145515-d8e3ce.zip`. It's about 30 MB; if it's too large to upload, tell me.

## 4. Fresh mod capture

This picks up the new Dynamic Campaign Mod build (652fe464) and every mod updated since 21 Nov. It runs from your Seapower-mods clone on the new branch. **It does not commit or push.** You only upload the ZIP it writes.

**4a. Check the clone is clean.**

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Seapower-mods"
```

```powershell
git status --short
```

**Expect no output.** If files are listed, send me the list and stop here. Don't delete anything.

**4b. Switch to the new branch.**

```powershell
git fetch origin feature/mno-r16
```

```powershell
git checkout -B capture-20261124 origin/feature/mno-r16
```

**4c. Run the capture.**

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\capture-all-mod-updates.ps1
```

It ends with a line naming `Downloads\SEST-Workshop-Capture-<date-time>.zip`. Upload that ZIP. A `SEST CAPTURE PARTIAL` line is fine: send the ZIP anyway.

**4d. Put the clone back.** This undoes the capture's edits to the clone. Your uploaded ZIP keeps them.

```powershell
git checkout -- . ; git clean -fd mods-source data ; git checkout beta
```

If `git checkout beta` says there is no such branch, send me the message. It's harmless.

## 5. Photo download kit (Gemini list, checked)

This uses `SEST-Image-Kit-20261124.zip` from this chat. Before downloading each photo, the kit checks its licence live on Wikimedia Commons, and it refuses anything that isn't a real, freely licensed photograph.

Save the ZIP to Downloads, right-click it and choose **Extract All**, keeping the default folder. Then:

```powershell
Set-Location -LiteralPath "$env:USERPROFILE\Downloads\SEST-Image-Kit-20261124\image-acquisition"
```

```powershell
py -3 .\fetch_images.py --mode verified --master SEST_IMAGE_MASTER_20261124.csv
```

If `py` is not found, use `python` instead of `py -3`.

Then open the contact sheet:

```powershell
Start-Process ".\runs\SEST_IMAGE_MASTER_20261124\CONTACT_SHEET.html"
```

Look through the cards. For any picture that is wrong, note its group name and the reason:

- wrong ship, aircraft or vehicle;
- wrong version or operator;
- a drawing, model or render rather than a photo;
- too poor to use.

Then zip the results:

```powershell
Compress-Archive -LiteralPath ".\runs\SEST_IMAGE_MASTER_20261124" -DestinationPath "$env:USERPROFILE\Downloads\SEST-Image-Results-20261124.zip" -Force
```

Upload `SEST-Image-Results-20261124.zip` with your notes. Nothing goes into the game or the gallery until you've approved it.

## 6. Optional: the render mod

If you know which Workshop mod makes the stock-style unit images, send me its Workshop ID or name. I'll check its licence and how it outputs images before planning anything.

## Playing tonight

You can play your current install (GPT's 22:12 package) as normal. **Don't run `Prepare-PC.cmd` from any older toolkit.** A new author update would stop it again; the next toolkit will be built on tonight's capture.

## What to send me

- [ ] Step 1: any output from the check, only if it printed something
- [ ] Step 2: the 22:12 source bundle, or the folder listing
- [ ] Step 3: `SEST-Beta-References-20261114-145515-d8e3ce.zip`
- [ ] Step 4: `SEST-Workshop-Capture-<date-time>.zip`
- [ ] Step 5: `SEST-Image-Results-20261124.zip` and your notes
- [ ] Step 6: the render mod's ID, if you have it

## What I build once those arrive (R16)

| Order | Work | Depends on |
|---|---|---|
| 1 | Bring in GPT's GCO/GSCO names and the wider map limits | Step 2 |
| 2 | Port to the new Dynamic Campaign Mod; register the new mods | Step 4 |
| 3 | Ice fixes: separate floes in patchy ice; slowing and ice effects only on contact; drawing and slowing start at the same level; ice on the battle and topographic maps; the 87°N scenario date | — |
| 4 | Weather following ships through normal GCO battles | — |
| 5 | MNO Workshop item: MNO content only; required collection; SETUP checks dependencies on Windows and Linux; licence notice; dependency licence table | — |
| 6 | Base game (0.9.2) support | Step 3 |
| 7 | Approved photos into the gallery; the 21 already-held photos wired to their units | Step 5 |
| 8 | Independent review, then one new toolkit and test notes for you | All |
