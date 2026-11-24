# Sensor View — extensions for other mods

Three files any mod can ship next to its `_info.ini` (Sensor View reads them from its own folder and every ticked mod; the first
mod in the load order wins), plus a code API:

| File | What |
|---|---|
| `SensorViewLayout.ini` | how each kind of label is laid out: which values, in what order, on which row, colours, offset, row spacing |
| `SensorViewText.ini` | every word Sensor View shows (labels, end markers, notes, button, options menu), find-and-replace, capitalising |
| `SensorViewExceptions.ini` | per-radar / weapon / unit switches and `[Rule:]` label logic |

Templates with every layout field and every text key: options menu, **Mods** tab, **Write the templates** (they land in Sensor
View's folder as `SensorViewLayout.template.ini` and `SensorViewText.template.ini`). **Read the files again** reloads all three.

## Layouts

```ini
[Layout:unit]                                  ; ships, submarines, aircraft, ground units (or [Layout:ship] etc. for one type)
Row = {name} + ({lost}) + ({detected})
Row = SPD: {speed}kts | RTS: {relspeed}kts
Row = Noise: {noise} dB | Emission: {emission} | {visible}
Row = Depth: {depth}ft + {surfaced}
Row = Alt: {altitude}ft
```

- `|` splits a row into segments (each its own colour, `Separator` between them); `+` splits a segment into parts (`Join` between).
- A part with a `{field}` that has no value right now drops out; `{field?}` is optional. An empty row is left out.
- `{self._flightStage}`, `{target.ClassNameShort}`, `{Namespace.Type.Member.path}`: any game value, as in rules.
- `Color.<field> = cyan`, `OffsetX` / `OffsetY` (pixels from the usual place), `LineSpacing` (pixels per row).
- One unit or weapon only: `[Layout:wp_rkr_slava]`, `[Layout:wp_ss-n-*]`.
- Types: unit (ship, submarine, aircraft, helicopter, ground), missile (bomb, rocket), torpedo, failed, compact (with "One stat
  per label line" off), unguided, survivors, sonobuoy, mine, countermeasure, paratrooper, marker (end markers), towed.
- Example, everything on one line: `[Layout:unit]` / `Row = {name} | {speed}kts | {altitude?}{depth?}ft`.

## Text

```ini
[Text]
label.surfaced = AUFGETAUCHT
end.shot_down_by = abgeschossen von {0}
menu.tab.general = Allgemein
button.main = "Sensoransicht: {0}  [{1}]"

[Replace]
Slava = Слава                 ; on every label, note and end marker as drawn (game names too)

[Options]
TitleCase = false             ; no automatic "Each Word Capitalised"
```

Code: `SensorViewApi.SetText(key, text)`, `GetText(key)`, `AddTextReplace(find, replace)`, `SetTitleCase(bool?)`,
`SetLayout(name, sectionLines)`, `RegisterField(name, (obj, insider) => text or null)` - a field any layout can then use as `{name}`.

Three ways for another mod to add **new logic** to the sensor view, and to **change its labels** (rename, replace, hide, recolour,
add lines anywhere). Both are switched off together with the options menu's Mods tab switch (`[Display] ModExtensions`); each code
extension also has its own switch there (`[Display] ModExtensionsOff`).

## 1. Rules (no code)

`[Rule:name]` sections in a `SensorViewExceptions.ini` in your mod's folder (next to its `_info.ini`). The format and every key are
described at the top of Sensor View's own `SensorViewExceptions.ini`. Example — Resolute's Pike afterburner (would go in
Resolute's own file, not Sensor View's):

```ini
[Rule:pike_afterburner]
Weapon = rsl_ashm
When   = ResoluteUpgrade.Combat.PikeAfterburner71.States.Powered
Label  = afterburner on
Draw   = cone 0.3 8
Color  = orange
```

Label changes (2026-11-03), all optional, all following `When`:

```ini
[Rule:my_labels]
Unit           = wp_rkr_slava
Rename         = Slava {self._name}      ; the name line (keeps "(lost)" etc. only if you put it back)
Hide           = noise, emission         ; remove every line of these kinds
Replace.speed  = SPD {self._speed}       ; new text for the first line of a kind (its colour stays)
Color.altitude = cyan                    ; recolour every line of a kind
LabelColor     = white                   ; the whole label in one colour (applied before Color.<kind>)
Label          = flagship                ; a new line ...
Position       = top                     ; ... after the name row (top), at the end (bottom, default), or "after <kind>"
```

A line's kind is the first layout field in it (see Layouts below): `name`, `lost`, `detected`, `destroyed`, `speed`, `relspeed`,
`noise`, `emission`, `visible`, `depth`, `altitude`, `damage`, `activesonar`, `cavitating`, `notching`, `impact`, `phase`, `seekeron`,
`guidance`, `spoofed`, `failure`, `wire`, `fuel` ...; lines added by mods: `mod` (or the kind they gave). These rules change a
label after its layout; to move things around, write a layout instead.

The path walks from a static member of any loaded type; a table keyed by the missile on the way (a `ConditionalWeakTable` or
`Dictionary`) is looked up for that missile automatically. If the type is renamed in an update, the rule stops applying (one info
line in LogOutput.log) instead of breaking anything.

## 2. Code (C#)

Reference `SensorView.dll` (from Sensor View's folder) and register an extension once, e.g. from your plugin's start:

```csharp
using SeaPower;
using SensorView;
using UnityEngine;

sealed class MyView : ISensorViewExtension
{
    public void Label(SensorViewLabel label)
    {
        // label.Object = the unit or weapon; label.Insider = own side or Show all units (fair mode: keep enemy internals hidden)
        if (label.IsWeapon && label.Insider && MyMod.TryGetPhase(label.Object, out string phase))
            label.Add("phase " + phase, new Color(1f, 0.6f, 0.15f));
        // change the view's own lines, by kind
        if (MyMod.IsFlagship(label.Object))
        {
            label.Rename(label.Text(0) + " *");
            label.Hide("noise");
            label.SetColor("altitude", Color.cyan);
            label.Insert(1, "flagship", Color.yellow);      // after the name row
        }
    }

    public void Draw(SensorViewCanvas canvas)
    {
        for (int i = 0; i < canvas.Count; i++)
        {
            if (!canvas.InsiderAt(i) || !MyMod.IsSprinting(canvas.ObjectAt(i))) continue;
            Vector3 p = canvas.PositionAt(i);
            canvas.Ring(p, 1f, Color.yellow);                       // 1 nm ring
            canvas.Note(p, "sprint", Color.yellow);
        }
    }
}

// once:
SensorViewApi.RegisterExtension("mymod.view", new MyView());
```

Label: `Count`, `Text(i)`, `Kind(i)`, `ColorOf(i)`, `IsInline(i)`, `Find(kind)`; `Set(i, text[, colour])`, `SetColor(i, colour)`,
`Remove(i)`, `Insert(i, text, colour, inline, kind)`, `Add(text[, colour])`, `AddInline(text[, colour])`; by kind `Rename(text)`,
`Replace(kind, text)`, `Hide(kind)`, `SetColor(kind, colour)`, `ColorAll(colour)`; `Object`, `IsWeapon`, `Insider`, `Failed`,
`SensorViewLabel.BuiltInKinds`. Line 0 is the name. Colour `default` (all zero) = the label's own colour.

Canvas: `Line`, `Dashed`, `Ring` (nm), `Cone` (from / to points, radii in nm), `Note` (text at a point); `Count`, `ObjectAt`,
`PositionAt` (where the view draws it — in fair mode a track's estimate), `InsiderAt`, `DeadAt`, `ShowAllUnits`, `FullMode`,
`UnitsPerNm`, `Camera`. Both calls run every frame while the view is on; keep them cheap. An extension that throws is switched off
until the game restarts, with the error in LogOutput.log.

## 3. Modules (C#, API 2, 2026-11-04)

A **module** is one brick of the view: derive from `SensorViewModule` and override only what you need. Same reference as above;
register it from your mod's entry point (put `after: new[] { "local.sensorview" }` on your `[ACPlugin]` so Sensor View loads
first). A full example that builds: `examples/ThreatPanel` (weapons coming at the selected unit with their time to impact, a ring
round each, the last weapon ends). Design and later stages: `DESIGN-extensions-v2.md`.

```csharp
public sealed class MyModule : SensorViewModule
{
    public override string Name => "My module";
    public override string Description => "What it adds, one line.";
    private SensorViewSetting<bool> _show;
    private SensorViewSetting<float> _size;
    private SensorViewColour _colour;

    public override void Settings(SensorViewSettings s)          // once: rows under its switch in the Mods tab
    {
        _show = s.Switch("Show", "Show the thing", true, "Help line under the menu.");
        _size = s.Slider("SizeNm", "Ring size (nm)", 2f, 0.5f, 20f, 0.5f);
        _colour = s.Colour("Colour", "Ring colour", Color.yellow);
    }

    public override void Frame(SensorViewInfo info) { }           // after the view collected what it shows, before drawing
    public override void Draw(SensorViewCanvas canvas) { }        // world shapes (as in section 2)
    public override void Label(SensorViewLabel label) { }         // label lines (as in section 2)

    public override void DrawScreen(SensorViewScreen screen)      // pixels, over the labels
    {
        Rect r = screen.Panel(SensorViewCorner.TopRight, 200f, screen.LineHeight + 8f);   // stacks with other modules' panels
        screen.Box(r, new Color(0f, 0f, 0f, 0.5f));
        screen.Text(r.x + 6f, r.y + 4f, "contacts " + screen.Info.Count, _colour.Value);
    }

    public override void OnEvent(SensorViewEvent e)               // MissionStart / MissionEnd / ContactAppeared / ContactLost / WeaponEnded
    {
        if (e.Kind == SensorViewEventKind.WeaponEnded) Debug.Log(e.Name + ": " + e.Reason);
    }
}

SensorViewApi.RegisterModule("mymod.thing", new MyModule());
```

- **What the view knows** - `SensorViewApi.Info` (also `screen.Info`, `e.Info`), read-only, cached per frame, fair-mode safe:
  `Count`, `ObjectAt`, `PositionAt` (where the view draws it), `InsiderAt`, `DeadAt`, `IsWeaponAt`, `DomainAt`, `OwnAt`, `IndexOf`,
  `IsShown`, `DrawnAt`, `Insider`; `Selected`, `Followed`, `Camera`, `ViewOn`, `ShowAllUnits`, `FullMode`, `HasExtendedGuidance`,
  `UnitsPerNm`, `Nm(a, b)`, `Feet(y)`; weapons: `TargetOf`, `WeaponsAimedAt(target, list)`, `TimeToImpact` (s, below 0 = not
  known), `Guidance` (ExtendedGuidance's state line), `Notching`; beams: `IlluminatedBy(target, list)`, `Illuminating(unit)`;
  `Colour("Hostile")` (any SensorViewColors.cfg key). A weapon's target / time / guidance is given for your side's weapons (or with
  Show all units), and for other weapons only when they come at your units - nothing a player could not know.
- **Screen**: `Width`, `Height`, `LineHeight`, `Measure`, `Text`, `Box`, `Line`, `Outline`, `Ring` (pixel radius), `ToScreen(world,
  out px)`, `At(i, out px)`, `Panel(corner, w, h)`. Pixels from the top-left of the game's image. All boxes are drawn first, then
  all lines, then all text (Sensor View's labels included), so a panel never covers a label's text.
- **Settings**: `Switch`, `Slider` (store game units: nm, ft, kts, deg), `Choice<TEnum>`, `Colour`, `Heading`. Saved in
  `SensorViewExtensions.cfg` under `[ext.<id>]` (never in Sensor View's own file), shown with the module's name, not part of Sensor
  View's presets or "Reset tab". Text keys for translators: `menu.row.ext.<id>.<key>`, `menu.help.ext.<id>.<key>`,
  `menu.ext.<id>.description`.
- **Contract**: `SensorViewApi.ApiVersion` (5 now) only grows and nothing it gave is taken away; `SensorViewApi.Has("screen")` etc.
  (labels, canvas, rules, text, layouts, fields, modules, info, screen, events, settings, timing; API 3: features, tabrows, presets; API 4: truth, filters; API 5: crosssections, guidance, canvas2); `MinApi` above ours = the module
  is not loaded and the Mods tab says so. The Mods tab shows each module's time per frame; the Perf log line has "extensions ...
  slowest ...". A call that throws switches the module off until the game restarts, with the error in the Mods tab.

## 4. Taking over a feature, rows in Sensor View's tabs, offered presets (API 3, 2026-11-04)

```csharp
public sealed class DotTrails : SensorViewModule
{
    public override int MinApi => 3;
    public override string[] Replaces => new[] { "trails" };      // "I draw trails, switch yours off"

    public override void Settings(SensorViewSettings s)
    {
        s.InTab("Etc", "Dotted trails");                           // these rows go to a card at the end of the Etc tab
        _dot = s.Slider("DotPixels", "Dot size (pixels)", 2f, 1f, 6f, 0.5f);
    }

    public override void DrawScreen(SensorViewScreen screen)
    {
        if (!Owns("trails")) return;                               // the user may have given trails back to Sensor View
        ...
    }
}

SensorViewApi.OfferPreset("mymod.dottrails", "Dotted trails, no wakes", "General|Display|WakeBubbles = false");
```

- **Features** (`SensorViewApi.FeatureIds`): terrain, grid, models, symbols, labels, trails, wakes, fans, layer, fires, cavitation,
  pings, beams (radar beams on targets), ciwsbeams, seekercones, links (datalink / command / wire lines), routes, cables (towed gear),
  jamming, lasers, rounds, explosions, endmarkers, radarrings; and since API 6 the towed kinds one at a time: cables.towed (towed
  sonar arrays), cables.vds, cables.dipping, cables.mad (towed bird and fixed boom), cables.decoys - `Replaces => { "cables" }` still
  takes all five (and the user's owner choice for "cables" applies to each kind that has none of its own). While your running module owns one, Sensor View does not draw it and
  its menu rows are greyed with "handled by <your module>". `SensorViewApi.FeatureOwner(id)` = the owner's id or "sensorview".
- **Several mods on one feature**: the Mods tab's "Features drawn by mods" card has a button for Sensor View and one per claiming
  module; the user's pick is kept in `[Display] FeatureOwners`. Default: the first claimant in the load order.
- **Rows in a built-in tab**: `settings.InTab(tab, section)` - tab "Surface / Ground", "Subsurface", "Air", "General" or "Etc" (null /
  "Mods" = back to the Mods tab); a card titled "section (module name)" at the end of that tab. Not in search, presets or Reset tab.
- **Offered presets**: shown in the Mods tab with "Save to my presets"; the user loads it in the General tab. A mod never changes
  Sensor View's settings by itself. Preset lines: `General|<cfg section>|<key> = value` (colours `Colours|...`), as a saved preset.
- The Mods tab says in which order extensions change labels (after Sensor View's own layout: load order).

## 5. Answering the view's questions, and cosmetic filters (API 4, 2026-11-04)

A guidance mod can tell Sensor View what is true; a look mod can restyle shapes. Override any of these on your module (return null
= no answer: the next module is asked, then Sensor View's own rule - the game's state and ExtendedGuidance's, which is the built-in
provider, asked last). Modules are asked in load order and the first answer wins; answers are cached for the frame. Example:
examples/ThreatPanel `TerminalSarh` ("SARH illuminates only at terminal"). A look-only example: examples/CosmeticSearch (search
cones get their own colour, strength and shape through `FilterShape` and `CrossSection`, nothing is taken over).

| Call | Question | Used for |
|---|---|---|
| `bool? IsLighting(radar, target)` | does this radar light this target now | radar beams on targets (true = drawn whatever the dish aim, false = none; a held beam ends at once) |
| `bool? Illuminator(missile, out radar, out target)` | which radar illuminates this semi-active missile | the illuminator beam (false = none) |
| `bool? SeekerTracking(weapon)` | is its seeker tracking now | false: no cone onto the target, its search cone instead |
| `string GuidanceState(weapon)` | its guidance state ("SARH track", "coast / notch (4s)") | the label's guidance line, end-marker causes ("what / why" = not tracking) |
| `bool? DatalinkOnly(radar)` | does this radar only carry a datalink | no beam on targets, only its line to the missile |

`void FilterShape(SensorViewShape shape)` - every beam, cone and link just before it is drawn: `Kind` (RadarBeam, CiwsBeam,
CommandBeam, TrackingCone, SearchCone, ReceiveCone, Datalink, Wire), `From`, `Weapon`, `Target` (links: the launcher / guiding
unit), `Radar`; set `Hidden`, or change `Color` / `Opacity`. Cosmetic only - it never changes what is true (labels, end markers,
SensorViewInfo stay the same). The Mods tab marks modules that answer questions and those that filter.

Answers are about the truth; what the player may see is still Sensor View's call (fair mode), so a provider cannot leak anything.

## 6. Cone shapes, guidance types, previews (API 5, 2026-11-04)

A cone or beam can get a cross-section instead of the round one. Return an outline as points round the axis, in units of the
cone's own radius (x across, y up), or null for round. The first module with an outline wins; it is resampled once per array. A
shaped cone has flat ends; the sea, sea-skimmer strip and fan ceiling cuts still apply. Kinds: RadarBeam, CiwsBeam, CommandBeam,
TrackingCone, SearchCone, ReceiveCone. `SensorViewApi.Rectangle(halfX, halfY)` gives a rectangle (a pyramid from a seeker).

```csharp
public override Vector2[] CrossSection(SensorViewShape shape)
{
    if (shape.Kind != SensorViewShapeKind.ReceiveCone) return null;
    return SensorViewApi.Rectangle(1f, 0.4f);          // 2.5 times wider than tall, flat ends
}
```

A guidance type can be described without code in a `[Guidance:name]` section (ours, any ticked mod, or
`SensorViewApi.SetException("Guidance", ...)`). It is the built-in module `SensorView.Guidance` and obeys the "Mod extensions"
master switch.

| Key | What |
|---|---|
| `Weapon` | ammunition file name, `*` / `?` allowed |
| `MidCourse` | `none`, `datalink`, `radiocommand`, `wire`, `satcom`, or its index number |
| `Seeker` | the guidance type name (`SemiActiveRadarHoming`, `ActiveRadarHoming`, `IRHoming` ...) |
| `When` | a `[Rule:]` condition on the weapon |
| `Label` | the label's guidance line, `{path}` values allowed |
| `Tracking` | `true` / `false`: its seeker is tracking (false: no cone onto the target, the search cone instead) |
| `Illuminator` | `none`: no illuminator beam for it |
| `Link` | `none`: no datalink / wire / command line or command beam for it |
| `Cone` | `round` or `rect W H` (W, H in cone radii) |
| `Color` | its cones' and links' colour |

The first matching section (by name) wins; matches are cached per weapon until the exceptions change. Example (docs only - never
put mod-specific sections in our own SensorViewExceptions.ini):

```ini
[Guidance:satcom_example]
MidCourse = satcom
Label     = SATCOM
Link      = none
Cone      = rect 1 0.4
```

`SensorViewSettings.Preview(title, text, sizeNm, draw)` puts a "?" on the last declared row: a live picture on a sea grid around
(0, 0, 0), with `Count` 0, `Camera` null and no dashed lines. The preview page shows all the module's rows and a Reset view button.
New canvas calls: `Line(a, b, colorA, colorB)`, `Triangle(a, b, c, color)` and a colour per corner, `HorizonFade(p)` (1 near,
0 at the horizon), `PixelSize(at)` and `SymbolPixels`.

Without a compile-time reference, a mod can still set exceptions and rules through
`SensorView.SensorViewApi.SetException(kind, name, key, value)` by reflection (kind `Rule` for rules).

## 7. API changes and deprecation (rule, 2026-11-05)

- `SensorViewApi.ApiVersion` says which version you build against; check it (or `SensorViewApi.Has(...)`) before using anything
  newer. A module whose `MinApi` is above it is not loaded, and that shows in Etc / Problems.
- Nothing is removed at once. A changed or renamed member keeps working as a thin wrapper over the new one for at least **two API
  versions**, marked `[Obsolete("use X; removed in API n")]`. The wrapper calls
  `Problems.Deprecated("SensorViewApi.OldName", Assembly.GetCallingAssembly())` (wrapper marked
  `[MethodImpl(MethodImplOptions.NoInlining)]`): the first call per addon logs one warning and lists the addon in **Etc / Problems**
  ("… uses old Sensor View API").
- Every change goes in the API changelog below, with the version it came in and, for a deprecation, the version it goes away.

### API changelog

| API | Change |
| --- | --- |
| 1 | ISensorViewExtension, labels, canvas, rules, text, layouts |
| 2 | SensorViewModule (Frame, DrawScreen, OnEvent, Settings), SensorViewInfo, SensorViewScreen |
| 3 | features, tab rows, offered presets |
| 4 | answering the view's questions (Truth), cosmetic filters |
| 5 | cone shapes, guidance types, previews |
| 6 | 2026-11-05: "cables" split - cables.towed / .vds / .dipping / .mad / .decoys can be taken over alone; capability "cablekinds" |
| 7 | 2026-11-09: OfferColourPreset - palettes from addons in General / Colour presets; capability "colourpresets" (example: examples/ColourBlindPalette) |
| 8 | 2026-11-09: GuidanceColour, Notching, SeekerLook, LossCause, ChaffState (module answers); ReportProblem / ClearProblems / TrustEngagePatch; mod support moved to addons (SensorViewAddons/) |
| — | 2026-11-09: SensorViewInfo.HasExtendedGuidance deprecated in 8, removed in 10 (use the ExtendedGuidance addon) |
