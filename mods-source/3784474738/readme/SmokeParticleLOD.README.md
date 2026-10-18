# Smoke Particle LOD 0.4

Place `SmokeParticleLOD.dll` and `SmokeParticleLOD.ini` together in the enabled mod folder. Uses the existing AnchorChain loader; no dependency on other custom mods. Restart Sea Power after replacing the DLL. All INI settings reload within two seconds, including rules for existing effects. No menu yet.

## Global settings

`[Global] Enabled=False` disables thinning and restores surviving partially faded particles. `DiscoveryIntervalSeconds=1` scans active scene particle systems once per second (range 0.25â€“10). Native resource loading and INI creation also register systems before use. Short-lived systems created outside those paths may finish between scans.

`ProtectSingleParticles=True` protects systems limited to one particle. `ProtectSubEmitters=True` protects parent systems that trigger other particle systems. Child smoke systems can still be reduced. `Exclude=*nuclear*,*my_effect*` excludes matching effects, overriding category and rule settings.

## Categories and defaults

`[Defaults]` supplies settings inherited by `[Smoke]`, `[Dust]`, `[Bubbles]`, `[Sparks]`, `[Debris]`, `[Flame]`, `[Flash]`, `[Other]`. Categories use emitter and material names, not visual analysis. Unrecognized systems go to `Other`; use explicit rules if automatic classification is wrong. Flashes and flames take priority over smoke keywords. Default settings enable Smoke/Dust/Bubbles/Sparks/Debris; Flame/Flash/Other remain unchanged.

Each category supports:

| Key | Meaning / range |
| --- | --- |
| Enabled | True / False |
| FullQualityPixels | Projected particle diameter at full density; greater than MinimumQualityPixels |
| MinimumQualityPixels | Diameter at minimum density; at least 0.1 pixels |
| MinimumFraction | Fraction retained for small particles; 0.1â€“1 |
| MinimumParticles | At least this many surviving particles per system are protected; 1â€“10000 |
| UpdateIntervalSeconds | Inspection interval; 0.05â€“1 seconds |
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


## Local missile flame LOD

The separate [FlameLOD] section preserves the approved smoke rules. [Flame] Enabled=False still disables particle thinning for flames; it does not disable this new freeze/proxy controller.

    [FlameLOD]
    Enabled=True
    FreezeBelowPixels=18
    ResumeAbovePixels=26
    ProxyBelowPixels=5
    ProxyAbovePixels=8
    CheckIntervalSeconds=0.2
    WarmupSeconds=0.5
    ProxySizeMultiplier=1
    Match=*effects/weapons/emitters/*/exhaust_*.ini,*sam_*effect*,*aam_*effect*,*asm_*effect*,*rocket*effect*,*missile*effect*

Eligible effects are named missile/rocket flame leaf systems in Local simulation space, attached below a running particle-system driver. Smoke, hot gas, heat distortion, explosions, systems with sub-emitters, and World/Custom simulation space are excluded. Matching native game effects are supported when they meet these conditions; this is not blanket coverage of every base-game effect. Global Enabled and Exclude also apply.

Thresholds refer to the projected diagonal of the complete managed flame group's bounds, using all relevant active game and reflection cameras. They are conservative bounds, not the bright texture's exact outline. At <=18 pixels the original particle systems pause after warm-up. At <=5 pixels their renderers hide and one larger paused billboard represents the entire group, using an existing flame material. Original particles remain in memory for recovery. At >=8 pixels the original frozen flame returns; at >=26 pixels its simulation resumes. Lowering these thresholds preserves more animation/detail.

ProxySizeMultiplier scales that single distant glow (0.25-2, default 1). Its brightness and shape approximate the original flame; no new texture or material asset is installed. Different missile materials can look different and require in-game visual review.

Required ordering: 0.1 <= ProxyBelowPixels < ProxyAbovePixels < FreezeBelowPixels < ResumeAbovePixels <= 1000. CheckIntervalSeconds: 0.05-1. WarmupSeconds: 0.35-10. INI changes reload within two seconds.

Only pauses owned by the mod are resumed. Engine stop/clear, inactive parents, game pause and finite emission duration are respected. Driver and smoke systems continue running. Freeze primarily reduces simulation work; the distant proxy also reduces the rendered flame particle count. No measured FPS gain is claimed.

## Effects outside camera views

[FlameLOD] PauseOffscreen=True pauses eligible local missile flames after warm-up when their full bounds are outside all matching active game/reflection cameras. A 10% screen-edge margin helps avoid flicker. The original particles remain attached to the missile. Returning to view restores normal distance LOD within CheckIntervalSeconds (0.2 by default), respecting game pause and engine shutdown. Unknown camera/bounds data keeps the effect running. Set PauseOffscreen=False to retain only distance LOD.

[Global] OffscreenSmokeIntervalSeconds=1 reduces the frequency of this mod's per-particle smoke inspection outside camera views (range 0.05-5 seconds). Smoke emission, simulation and aging are not paused or cleared by this feature; existing native culling settings are retained. Visible parts of long trails count even if the emitter is outside the screen. Returning to view restores the configured normal inspection interval (0.2-0.25 seconds here). Set this value to 0.05 to disable the extra delay.

Rendering still uses Unity's camera culling. This feature does not change effect materials, emission rates, lighting or game AI. No combat FPS improvement has yet been measured for 0.4.
