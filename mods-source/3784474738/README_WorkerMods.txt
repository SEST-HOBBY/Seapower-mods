Experimental worker modules for AC Pack

CombatWorker 0.2.0, ParallelRangeProbe 0.12.0, UiWorkerProbe 0.2.0.

CombatWorker settings: Mods\CombatWorker\settings.ini under the folder below.
Enabled=true
EnableBatches=true
EnableSensorOverlap=true
Workers=6
MaxPairsPerPhase=128
MaxWaitPerFrameMs=3

Workers: 1..12. MaxPairsPerPhase: 4..256. MaxWaitPerFrameMs: 0..10 ms shared
across waits in a rendered frame. Restart after configuration changes.
Each module accepts on, off or status through Mods\<ModuleName>\live\mode.request
and writes status.txt there. The module names are CombatWorker,
ParallelRangeProbe and UiWorkerProbe. Session off does not persist across restarts.
UiWorkerProbe and ParallelRangeProbe use the AC Pack checkbox for startup.

All three modules require AnchorChain and respect the parent AC Pack checkbox.
Use one copy per module in StreamingAssets\AC Pack. Restart after DLL replacement
or Mod Manager changes; an already running process keeps its loaded code.
The same Windows binaries use ordinary threads on Intel and AMD. Existing CPU
affinity is respected; these modules do not pin cores.

There are no game-version, game-file-hash or submod-version approval lists.
Required signatures, data inputs and patch boundaries are checked at startup.
Unsupported modules retain native game behavior with an informational log entry;
no compatibility popup, forced pause or application quit is used. Numerical and
UI outputs also receive native-result comparisons. These are safeguards, not
proof against every possible future semantic change.
MultiStageMissiles is optional. Its current propulsion API is detected at runtime.
If an active propulsion extension has an incompatible API, numerical trajectory
offloading stays off; independent contact, sensor and UI modules can still run.

Persistent settings and session status stay under:
%USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\Mods
Pack updates do not overwrite this folder. No recording starts automatically.
The final binaries passed offline API/behavior and activation tests against the
installed release and available beta. This update has not been tested in-game.
