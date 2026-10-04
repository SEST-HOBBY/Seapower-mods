# Smoke Particle LOD 0.2

Place `SmokeParticleLOD.dll` and `SmokeParticleLOD.ini` together in the enabled mod folder. Uses the existing AnchorChain loader; no dependency on other custom mods. Restart Sea Power after replacing the DLL. All INI settings reload within two seconds, including rules for existing effects. No menu yet.

## Global settings

`[Global] Enabled=False` disables thinning and restores surviving partially faded particles. `DiscoveryIntervalSeconds=1` scans active scene particle systems once per second (range 0.25–10). Native resource loading and INI creation also register systems before use. Short-lived systems created outside those paths may finish between scans.

`ProtectSingleParticles=True` protects systems limited to one particle. `ProtectSubEmitters=True` protects parent systems that trigger other particle systems. Child smoke systems can still be reduced. `Exclude=*nuclear*,*my_effect*` excludes matching effects, overriding category and rule settings.

## Categories and defaults

`[Defaults]` supplies settings inherited by `[Smoke]`, `[Dust]`, `[Bubbles]`, `[Sparks]`, `[Debris]`, `[Flame]`, `[Flash]`, `[Other]`. Categories use emitter and material names, not visual analysis. Unrecognized systems go to `Other`; use explicit rules if automatic classification is wrong. Flashes and flames take priority over smoke keywords. Default settings enable Smoke/Dust/Bubbles/Sparks/Debris; Flame/Flash/Other remain unchanged.

Each category supports:

| Key | Meaning / range |
| --- | --- |
| Enabled | True / False |
| FullQualityPixels | Projected particle diameter at full density; greater than MinimumQualityPixels |
| MinimumQualityPixels | Diameter at minimum density; at least 0.1 pixels |
| MinimumFraction | Fraction retained for small particles; 0.1–1 |
| MinimumParticles | At least this many surviving particles per system are protected; 1–10000 |
| UpdateIntervalSeconds | Inspection interval; 0.05–1 seconds |
| FadeSeconds | Removal fade in simulated seconds; at least twice the interval, at most 5 |
| ProtectYoungSeconds | Age before thinning may begin; zero or greater |

Sparks and Debris default to a 0.65 fraction and 12 protected particles. Add explicit values in those sections to override them.

## Per-effect rules

```ini
[Rule:OniksSmoke]
Match=*ramjet_large*smoke*
Category=Smoke
MinimumFraction=0.6

[Rule:KeepNuclear]
Match=*nuclear_500kt*
Enabled=False
```

`Match` compares comma-separated, case-insensitive wildcard patterns against source resource/INI path, object hierarchy, emitter name and material names. `*` matches any text; `?` one character. Later matching rules override earlier ones. Optional `Category` starts from that category's settings; other omitted keys retain previous values.

To explicitly include everything, including unidentified systems and flames, add this rule **last**:

```ini
[Rule:AllParticles]
Match=*
Enabled=True
```

Global exclusions and single-particle/sub-emitter protections still apply. Turning on all categories can damage effects whose appearance depends on a small number of billboards. Particle LOD does not control lights, sound, meshes, shader-only effects or physical debris objects.

## Limits and testing

Distance, FOV, resolution and each particle's position determine projected size. Near particles retain full density. Removed particles cannot return after zooming in; newly emitted nearby particles retain full density. Disable LOD and launch a new salvo for a clean comparison. World-space smoke keeps aging offscreen; no simulation freezing is used.

Thinning reduces alive simulation/rendering work, not initial emission cost. Inspection and discovery have CPU overhead. No fixed FPS gain is guaranteed. The included commented smoke stress-test rule deliberately exaggerates reduction.

Old `[SmokeParticleLOD]` configs still work and keep their former diffuse-only folder scope. Use the new schema for global coverage; do not combine old and new sections.
