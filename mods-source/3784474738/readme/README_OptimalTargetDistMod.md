# Optimal Target Distance

AnchorChain/Harmony DLL mod for Sea Power. It adds distance-based preference to the
existing automatic ammunition selection and independently configurable lower/upper
automatic target-altitude gates.

## INI keys

Add the optional keys under the ammunition file's existing `[Guidance]` section:

```ini
OptimalTargetDist=60,180

MinAttackAltitude=15
MaxAttackAltitude=80000
AutoAttackBelowMinAltitude=True
AutoAttackAboveMaxAltitude=False
```

`OptimalTargetDist` accepts one nautical-mile value or a comma-separated minimum and
maximum. Reversed ranges are normalized; malformed values are ignored.

The split altitude values default independently to the existing
`AutoAttackOutsideAltitudes` value. If neither split key exists, the original game
path is left unchanged.

Distance preference is applied only after Sea Power's original automatic launcher,
range, guidance, FCR, arc, availability, and target checks have accepted a candidate.
When ammunition with and without the new distance key is mixed, the legacy result is
retained unless it also has the key and at least two valid configured candidates can
be meaningfully compared.

## Build

```powershell
.\build.ps1
```

The build references the installed `Seapower-Scripts.dll`, the workshop
`AnchorChain.dll`, and the game's existing Harmony/BepInEx/Unity assemblies. It adds
no runtime dependency of its own. The output is `bin\OptimalTargetDist.dll`.

The Harmony transpiler identifies the accepted-candidate block by its member and IL
shape instead of hard-coded local-variable numbers. This lets the same DLL support
both release and beta layouts, including later builds that retain the same behavior.
To verify both supplied game assemblies explicitly:

```powershell
.\build.ps1 -LegacyScriptsPath 'C:\path\to\Seapower-Scripts_legacy.dll'
```
