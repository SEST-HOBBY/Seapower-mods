# Profile Image 1024

AnchorChain/Harmony DLL mod for Sea Power. It changes the `save_profile`,
`save_all_profiles`, and `save_plan` commands' render width from 512 to 1024 pixels.
The height continues to be calculated from the selected object's bounding-box
aspect ratio, so neither axis is stretched.

Variant indices are deliberately omitted for both profile and plan images. Even
when the selected object uses a variant, the output filename is the vessel/INI name
without `_0`, `_1`, or another numeric suffix.
