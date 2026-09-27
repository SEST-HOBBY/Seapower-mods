# Thermal glow material

Add this to the ammunition INI's existing `[Models]` section:

```ini
ThermalGlowMaterial=assets/europack/materials/thermal_glow/thermal_glow.ini
ThermalGlowMaxIntensity=3
Stage2GlowMesh=YOUR_GLOW_MESH
Stage2InheritGlow=False
Stage2GlowFadeInTime=2
```

`YOUR_GLOW_MESH` is a placeholder: use the name of your actual overlay mesh.
The stage must exist in your stage configuration. No ammunition is changed by
installing this material alone. The same material serves every stage and debris.

The supplied 512 x 512 RGBA PNG has white RGB, an opaque centre, soft fades on
all four sides and a transparent outer gutter. Map each glowing mesh region's
UVs inside 0..1. Put the hottest surface in the central area (roughly 0.26..0.74
on each axis) and map its boundary toward the transparent border (outer 4%).
The mask fades at UV boundaries, not automatically at arbitrary geometry edges.
For a cylinder seam that should stay bright, keep that seam's UVs in the opaque
centre or use a custom mask; do not place it on the transparent texture border.

Default color is warm orange-red (`FF5020FF`). Change `_TintColor` in
`thermal_glow.ini` to recolor every weapon using this material. The final two hex
digits are alpha; leave them `FF`. Use `ThermalGlowMaxIntensity` to tune brightness.
The shader is additive, so the overlay is brightest against dark backgrounds.
It adds no point light. Place the glow mesh slightly above the solid surface to
avoid z-fighting. `_InvFade=100000` narrows the shader's optional soft-particle
depth-fade band so a close-fitting overlay is less likely to disappear against
the underlying missile. Check the authored overlay and brightness in game.

Paths, PNG alpha and material syntax checked offline. Actual shader appearance
and brightness have not been tested in a Unity/Sea Power scene.
