# W88 glow gradient

The W88 uses its own `assets/europack/materials/thermal_glow/w88_mk5_glow.ini` material and `w88_mk5_glow_mask.png` alpha mask. The shared material/texture used by other missiles is unchanged.

The existing overlay mesh and UVs are retained: aft V=0.04, nose V=0.50, U=0.50. The new mask is nearly transparent aft, about 6% at mid-body, 65% at 80% length and 92% at 90% length. These are visual mask values, not temperatures. The forebody stays bright while the rear and middle expose more of the original body material.

Only `ThermalGlowMaterial` is changed in the ammunition INI. Existing intensity, speed thresholds, heating/cooling times, flight settings and effects are preserved. The tint is fixed orange; there is no new temperature-dependent color transition.

Restart Sea Power and launch a fresh weapon to load the new material. Offline checks and the comparison render do not establish the final Unity appearance.
