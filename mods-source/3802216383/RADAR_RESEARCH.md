R10.21 auxiliary navigation radar test

Research findings
- OPS-20C has a main scanner and a smaller auxiliary navigation scanner. A firsthand Hyuga tour identifies the thin auxiliary scanner opposite the lower NORA-1C satellite dome. The main scanner is higher in the middle of the mast, beneath the helicopter datalink dome.
- FCS-3 is the ship's air-search/multifunction radar, using fixed panels around the forward and aft island structures. The larger panels perform search/tracking; they must not mechanically rotate. They are already modeled. No extra spinning air-search dish is added.

Sources
https://minkara.carview.co.jp/userid/1224622/blog/27837293/ (firsthand ship tour and mast photograph; labels contain some other inconsistencies, so used with the user's visual references)
https://www.mod.go.jp/atla/research/gaibuhyouka/pdf/FCS-3_25.pdf (official FCS-3 radar architecture/search and tracking research)
https://aobamil.sakura.ne.jp/shasin/hyuga/hyuga.html (ship photographs locating FCS-3 panels above island windows)
https://www.youtube.com/watch?v=XCrMHDw4AaA&t=460s (user-selected mast video)

Changes
Navigation SensorSystem9 now rotates a native scanner on the existing lower side-platform gearbox, opposite the lower satellite dome. Position: 0.09457609,0.32325208,0.13545359. Native mesh scaled to 0.7 as an approximate visual size, not a verified real dimension. Removed the old static scanner plate (20 faces) to avoid overlap. Main OPS-20 scanner remains at the user-confirmed position.
Air-search arrays remain stationary. Existing eu_OPY-1 performance remains a documented Asahi-derived stand-in for FCS-3; no unverified actual ranges were added. Navigation retains stock Nav_Radar performance. R10.20 flag test retained; its in-game result is still pending.

Replace the previous test folder; do not merge. Offline checks pass; navigation rotation, size, height and clearance require in-game verification. No direct game installation performed.
