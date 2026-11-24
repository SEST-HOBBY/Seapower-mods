using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using Mono.Cecil;
using Mono.Cecil.Cil;
using Sest.RuntimeFixes;

// Sea ice on Dynamic Campaign Mod's campaign map and in its movement
// (runtime/CampaignIceRules.cs, runtime/CampaignIce.cs), under Mono without
// Unity or Noesis, against the captured Dynamic Campaign Mod 1.0.2 (18a2416e):
// 1 the raster matches SeaIceModel at every pixel centre and uses DCM's own
//   WeatherFrame layout (WaterOf's pixel centres); the ice edge (15 %) and
//   heavy-pack (60 %) lines; the paint and the straight-alpha composite;
//   the per-date cache and the size limit;
// 2 the hover readout text; the group speed factor (ice class none,
//   submarines under, the beset floor), the cap on FULL speed and the
//   "(ice)" / "(out of fuel, ice)" texts;
// 3 every DCM and game member the runtime binds (CampaignIce.Bind, hash
//   lock), and the IL facts the design rests on (Cecil): Build writes every
//   pixel through Pixel, TakeBuilt uploads after Build, Frame drapes
//   off when hidden and reads MapPerf.HideWeather, Detach lets the slot go,
//   UpdateCaps rewrites WeatherKnots (twice a step), WeatherKnots' only
//   readers (WeatherCapOf, and the AI's Rhythm.ClosingHours / Hold, which
//   take min(Logistics.SpeedOf, WeatherKnots)), SpeedText's "(heavy seas)",
//   FleetViewModel.Line's own out-of-fuel text, the RGBA32 texture; the
//   movement pass without reflection invokes or boxing;
// 4 the composite on a real WeatherFrame.Build of the polar-north theatre,
//   through the runtime's own Harmony postfix, byte for byte against this
//   test's raster, after a frame without ice that is not counted, and the
//   forecast date changing the ice; the drape decision with DCM's weather
//   toggle, and the overlay's failure count per map;
// 5 movement on real TaskForce objects with a stand-in IUnitCatalog: the
//   runtime's UpdateCaps adapter, DCM's own Logistics.SpeedOf /
//   Movement.SpeedOf / SpeedText / HoursToRoutePoints and the AI's
//   Rhythm.ClosingHours after it (a slow or stopped group capped on its full
//   speed), the per-group cache, the out-of-fuel fleet text, and the
//   runtime's SpeedText and FleetViewModel.Line postfixes;
// 6 the polar test campaigns: the ice edge in view at the start, the
//   transit group's line into the pack reaching 30 % ice more than DCM's
//   contact range short of its target, and the transit pair's separation
//   from every opposing group and from the other tests' contact points;
// 7 the runtime's install order (before CumulativeCombatCosts' return) and
//   the switches; a DCM image with another hash binds nothing.
//   mono CampaignIceTests.exe <flat refs> SEST.RuntimeFixes.dll DynamicCampaignMod.dll <test dynamic_campaigns folder>
static class CampaignIceTests
{
    const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    static int checks;
    static TextWriter console;
    static StringWriter log;
    static void Check(bool ok, string why)
    {
        checks++;
        if (!ok)
        {
            Console.SetOut(console);
            Console.WriteLine(log.ToString());
            throw new Exception("FAILED: " + why);
        }
    }
    static string N(double v, string f = "0.0") => v.ToString(f, CultureInfo.InvariantCulture);
    static object Get(object value, string field)
    {
        Type t = value as Type ?? value.GetType();
        var f = t.GetField(field, All) ?? throw new MissingFieldException(t.FullName, field);
        return f.GetValue(value is Type ? null : value);
    }
    static void Set(object value, string field, object data)
    {
        Type t = value as Type ?? value.GetType();
        FieldInfo f = null;
        for (var x = t; x != null && f == null; x = x.BaseType) f = x.GetField(field, All);
        (f ?? throw new MissingFieldException(t.FullName, field)).SetValue(value is Type ? null : value, data);
    }
    static object Call(object target, string name, Type[] types, params object[] args)
    {
        Type t = target as Type ?? target.GetType();
        var m = t.GetMethod(name, All, null, types, null) ?? throw new MissingMethodException(t.FullName, name);
        try { return m.Invoke(target is Type ? null : target, args); }
        catch (TargetInvocationException e) { throw e.InnerException; }
    }
    static int Lines(string text) => log.ToString().Split('\n').Count(l => l.Contains(text));
    static DateTime Utc(int y, int m, int d, int h = 12) => new DateTime(y, m, d, h, 0, 0, DateTimeKind.Utc);

    static int Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll"); return File.Exists(p) ? Assembly.LoadFrom(p) : null; };
        Assembly.LoadFrom(Path.Combine(refs, "0Harmony.dll"));
        var game = Assembly.LoadFrom(Path.Combine(refs, "Seapower-Scripts.dll"));
        var rt = Assembly.LoadFrom(Path.GetFullPath(args[1]));
        var dcm = Assembly.LoadFrom(Path.GetFullPath(args[2]));
        string campaigns = Path.GetFullPath(args[3]);
        console = Console.Out;
        log = new StringWriter();
        Console.SetOut(log);
        try
        {
            Raster();
            Readout();
            Speed();
            Il(Path.GetFullPath(args[2]), Path.GetFullPath(args[1]));
            var ci = rt.GetType("Sest.RuntimeFixes.CampaignIce", true);
            Bindings(ci, dcm, game);
            Frames(ci, dcm, campaigns);
            MapToggles(ci);
            Movement(ci, dcm);
            Campaigns(dcm, campaigns);
            HashLock(rt, ci, Path.GetFullPath(args[1]));
        }
        catch (Exception e)
        {
            Console.SetOut(console);
            Console.WriteLine(log.ToString());
            Console.WriteLine(e.Message);
            Console.WriteLine(e.StackTrace);
            return 1;
        }
        finally { Console.SetOut(console); }
        if (Environment.GetEnvironmentVariable("SEST_ICE_LOG") == "1") Console.Write(log.ToString());
        Console.WriteLine("Campaign ice: " + checks + " checks passed against Dynamic Campaign Mod 1.0.2 (18a2416e); no Unity, no Noesis, no PC gameplay claim.");
        return 0;
    }

    // 1. The raster.
    static void Raster()
    {
        // The polar-north theatre at DCM's weather cell (0.25) on 10 March 2028.
        double s = 58, n = 81, w = 0, e = 60, cell = 0.25;
        IceRaster.SizeOf(s, n, w, e, cell, out int width, out int height);
        Check(width == 240 && height == 92, "SizeOf is WeatherFrame.SizeOf's Ceiling((max - min) / cell): " + width + " x " + height);
        var day = Utc(2028, 3, 10, 8);
        var r = new IceRaster(s, w, cell, width, height, day);
        double worst = 0;
        for (int y = 0; y < height; y++)
            for (int x = 0; x < width; x++)
                worst = Math.Max(worst, Math.Abs(r.Percent[y * width + x] - SeaIceModel.Concentration(s + (y + 0.5) * cell, w + (x + 0.5) * cell, day)));
        Check(worst < 1e-4, "every pixel is SeaIceModel.Concentration at its centre (worst " + worst + ")");
        Check(r.LatOf(0) == 58.125 && r.LonOf(0) == 0.125 && r.North == 81 && r.East == 60, "row 0 south, column 0 west, centres half a cell in");
        var p = r.Paint(null);
        Check(r.IcePixels > 2000 && r.HeavyPixels > 500 && r.HeavyPixels < r.IcePixels, "10 March: " + r.IcePixels + " ice pixels, " + r.HeavyPixels + " heavy");
        // Along 36E (column 144 = 36.125E): open, the edge line, fill, the heavy line, heavy fill.
        int col = 144, edgeRow = -1, heavyRow = -1;
        for (int y = height - 1; y >= 0; y--) // from the pole: the Barents edge, not the White Sea's
        {
            int k = r.KindAt(col, y, null);
            if (k == 2 && edgeRow < 0) edgeRow = y;
            if (k == 3 && heavyRow < 0) heavyRow = y;
        }
        Check(edgeRow > 0 && heavyRow > edgeRow, "36E has the 15 % line south of the 60 % line (rows " + edgeRow + ", " + heavyRow + ")");
        double edgeLat = r.LatOf(edgeRow), heavyLat = r.LatOf(heavyRow);
        Check(Math.Abs(edgeLat - 71.7) < 0.4, "the 15 % edge on 36E at " + N(edgeLat, "0.00") + "N (the review's seaice.py run: about 71.7N)");
        Check(heavyLat > 73.5 && heavyLat < 74.5, "the 60 % line on 36E at " + N(heavyLat, "0.00") + "N (74N is 62.3 %)");
        Check(r.Percent[(edgeRow - 1) * width + col] < 15 && r.Percent[edgeRow * width + col] >= 15, "the edge pixel is the first at or over 15 %");
        Check(r.KindAt(col, edgeRow - 1, null) == 0 && r.KindAt(col, edgeRow + 2, null) == 1, "open water below the line, fill above it");
        int o = (edgeRow * width + col) * 4;
        Check(p[o] == 0 && p[o + 1] == 200 && p[o + 2] == 255 && p[o + 3] == 255, "the edge line is opaque cyan");
        o = (heavyRow * width + col) * 4;
        Check(p[o] == 10 && p[o + 1] == 40 && p[o + 2] == 120 && p[o + 3] == 255, "the heavy-pack line is opaque navy");
        o = ((edgeRow + 2) * width + col) * 4;
        double c2 = r.Percent[(edgeRow + 2) * width + col];
        Check(p[o] == 232 && p[o + 1] == 244 && p[o + 2] == 255 && p[o + 3] == (byte)Math.Round(CampaignIceStyle.FillAlpha(c2) * 255), "fill: pale ice, opacity from concentration");
        o = ((edgeRow - 1) * width + col) * 4;
        Check(p[o + 3] == 0, "open water stays transparent");
        Check(CampaignIceStyle.FillAlpha(14.9) == 0 && Math.Abs(CampaignIceStyle.FillAlpha(15) - 0.30) < 1e-9 && Math.Abs(CampaignIceStyle.FillAlpha(98) - 0.85) < 1e-9 &&
              CampaignIceStyle.FillAlpha(40) < CampaignIceStyle.FillAlpha(80), "fill opacity 0.30 at 15 % rising to 0.85 at the model's 98 %");
        // Land: a water mask without the edge pixel draws nothing there.
        var water = Enumerable.Repeat(true, width * height).ToArray();
        water[edgeRow * width + col] = false;
        Check(r.KindAt(col, edgeRow, water) == 0 && r.Paint(water)[(edgeRow * width + col) * 4 + 3] == 0, "nothing is drawn on land");
        // The season moves the edge: 10 September has far less ice.
        var sep = new IceRaster(s, w, cell, width, height, Utc(2028, 9, 10));
        sep.Paint(null);
        Check(sep.IcePixels < r.IcePixels / 2, "10 September: " + sep.IcePixels + " ice pixels against " + r.IcePixels + " in March");
        // A day later the edge has moved (the creep under time compression).
        var later = new IceRaster(s, w, cell, width, height, Utc(2028, 4, 20));
        int changed = Enumerable.Range(0, width * height).Count(i => Math.Abs(later.Percent[i] - r.Percent[i]) > 0.5);
        var nextDay = new IceRaster(s, w, cell, width, height, Utc(2028, 4, 21));
        int moved = Enumerable.Range(0, width * height).Count(i => later.Percent[i] != nextDay.Percent[i]);
        Check(changed > 100 && moved > 0, "the ice changes with the date: " + changed + " pixels by 0.5 pp from 10 March to 20 April, " + moved + " from 20 to 21 April");

        // Composite over the weather image (straight RGBA32).
        var weather = new byte[width * height * 4];
        for (int i = 0; i < width * height; i++) { weather[i * 4] = 40; weather[i * 4 + 1] = 80; weather[i * 4 + 2] = 120; weather[i * 4 + 3] = (byte)(i % 2 == 0 ? 0 : 160); }
        var before = (byte[])weather.Clone();
        int done = r.Composite(weather, null);
        int kinds = Enumerable.Range(0, width * height).Count(i => r.KindAt(i % width, i / width, null) != 0);
        Check(done == kinds && kinds > 2000, "the composite touches exactly the ice pixels (" + done + ")");
        bool untouched = true, overClear = true, overOpaque = true;
        for (int i = 0; i < width * height; i++)
        {
            int k = r.KindAt(i % width, i / width, null);
            if (k == 0) { untouched &= weather.Skip(i * 4).Take(4).SequenceEqual(before.Skip(i * 4).Take(4)); continue; }
            IceRaster.Colour(k, r.Percent[i], out byte cr, out byte cg, out byte cb, out double a);
            if (before[i * 4 + 3] == 0) overClear &= weather[i * 4] == cr && weather[i * 4 + 1] == cg && weather[i * 4 + 2] == cb && weather[i * 4 + 3] == (byte)Math.Round(a * 255);
            else
            {
                double da = 160 / 255.0, oa = a + da * (1 - a);
                overOpaque &= weather[i * 4 + 3] == (byte)Math.Round(oa * 255) && weather[i * 4] == (byte)Math.Round((cr * a + 40 * da * (1 - a)) / oa);
            }
        }
        Check(untouched, "pixels without ice keep DCM's weather colour and alpha");
        Check(overClear, "over a transparent weather pixel the ice is drawn as is");
        Check(overOpaque, "over a weather colour: straight-alpha over (out_a = a + d_a(1 - a))");
        Check(r.Composite(new byte[16], null) == -1, "a frame of another size is left alone");
        var bytes = new byte[] { 0, 0, 0, 0 };
        IceRaster.Over(bytes, 0, 9, 9, 9, 0);
        Check(bytes.All(b => b == 0), "zero over zero stays zero");

        // The cache: one raster per box and date, shared by the frame builds.
        var cache = new IceRasterCache();
        var a1 = cache.Get(s, w, cell, width, height, Utc(2028, 3, 10, 1));
        var a2 = cache.Get(s, w, cell, width, height, Utc(2028, 3, 10, 23));
        var a3 = cache.Get(s, w, cell, width, height, Utc(2028, 3, 11, 0));
        Check(ReferenceEquals(a1, a2) && !ReferenceEquals(a1, a3) && cache.Builds == 2 && cache.Hits == 1, "one raster per campaign date, hours share it");
        // The overlay cell: 0.1 degrees, coarser when the theatre would pass 1 M pixels.
        Check(IceRaster.CellFor(58, 81, 0, 60, 0.1, 1000000) == 0.1, "a polar theatre is drawn at 0.1 degrees");
        double big = IceRaster.CellFor(-80, 85, -180, 180, 0.1, 1000000);
        IceRaster.SizeOf(-80, 85, -180, 180, big, out int bw, out int bh);
        Check(big > 0.24 && (long)bw * bh <= 1000000, "a world theatre is coarsened to " + N(big, "0.000") + " degrees, " + bw + " x " + bh);
    }

    // 2a. The readout.
    static void Readout()
    {
        Check(CampaignIceStyle.HoverLine(72.4, true) == "Ice 72 % (heavy pack)", "72 %: " + CampaignIceStyle.HoverLine(72.4, true));
        Check(CampaignIceStyle.HoverLine(40, true) == "Ice 40 % (pack ice)" && CampaignIceStyle.HoverLine(8, true) == "Ice 8 % (drift ice)", "pack ice, drift ice");
        Check(CampaignIceStyle.HoverLine(72, false) == null && CampaignIceStyle.HoverLine(0.4, true) == null && CampaignIceStyle.HoverLine(double.NaN, true) == null, "no line on land, under 1 % or for NaN");
        Check(CampaignIceStyle.HoverEffect(72, true) == "Surface groups 10 % speed (beset); submarines pass under", CampaignIceStyle.HoverEffect(72, true));
        Check(CampaignIceStyle.HoverEffect(40, true) == "Surface groups 40 % speed; submarines pass under" && CampaignIceStyle.HoverEffect(20, true) == "Surface groups 70 % speed; submarines pass under",
              "restricted 40 %, caution 70 %");
        Check(CampaignIceStyle.HoverEffect(8, true) == null, "open for class none: no effect line");
    }

    // 2b. The speed rules.
    static void Speed()
    {
        Check(CampaignIceSpeed.Factor(5, 0) == 1.0 && CampaignIceSpeed.Factor(20, 0) == 0.7 && CampaignIceSpeed.Factor(40, 0) == 0.4 && CampaignIceSpeed.Factor(70, 0) == CampaignIceSpeed.BesetFactor,
              "class none: 1.0 under 10 %, 0.7 to 30 %, 0.4 to 60 %, beset (0.1) from 60 %");
        Check(CampaignIceSpeed.Factor(70, IceRules.CapabilityIndex("polar_class")) == 0.7 && CampaignIceSpeed.Factor(70, IceRules.CapabilityIndex("icebreaker")) == 1.0,
              "the ice.py classes: polar_class caution at 70 %, icebreaker open");
        Check(CampaignIceSpeed.GroupFactor(70, new[] { -1, -1 }) == 1.0, "a group of submarines passes under");
        Check(CampaignIceSpeed.GroupFactor(40, new[] { -1, 0 }) == 0.4 && CampaignIceSpeed.GroupFactor(70, new[] { 3, 0 }) == 0.1, "the slowest surface hull sets the pace");
        Check(CampaignIceSpeed.GroupBeset(70, new[] { 0 }) && !CampaignIceSpeed.GroupBeset(70, new[] { -1 }) && !CampaignIceSpeed.GroupBeset(40, new[] { 0 }), "beset only for a blocked surface hull");
        bool b;
        Check(CampaignIceSpeed.Cap(0, 20, 0.4, out b) == 8 && b, "no weather cap (0): ice cap 0.4 x 20 = 8 kn");
        Check(CampaignIceSpeed.Cap(12, 20, 0.4, out b) == 8 && b, "weather 12 kn, ice 8 kn: ice binds");
        Check(CampaignIceSpeed.Cap(6, 20, 0.4, out b) == 6 && !b, "weather 6 kn below the ice cap: weather binds");
        Check(CampaignIceSpeed.Cap(0, 0, 0.4, out b) == 0 && !b && CampaignIceSpeed.Cap(9, 20, 1.0, out b) == 9 && !b, "a group that can make no speed, or open water: unchanged");
        Check(CampaignIceSpeed.Cap(0, 20, 0.1, out b) == 2 && b && CampaignIceSpeed.Cap(0, 20, 0.1, out b) > 0, "beset is never 0 kn (0 = no cap in DCM)");
        Check(CampaignIceSpeed.Text("8 kn (heavy seas)", true) == "8 kn (ice)" && CampaignIceSpeed.Text("8 kn (heavy seas)", false) == "8 kn (heavy seas)" &&
              CampaignIceSpeed.Text("20 kn", true) == "20 kn", "the speed text reads (ice) only where DCM said (heavy seas)");
        Check(CampaignIceSpeed.Text("2 kn (out of fuel, heavy seas)", true) == "2 kn (out of fuel, ice)" && CampaignIceSpeed.Text("2 kn (out of fuel, heavy seas)", false) == "2 kn (out of fuel, heavy seas)" &&
              CampaignIceSpeed.Text("5 kn (out of fuel)", true) == "5 kn (out of fuel)", "the out-of-fuel text reads (out of fuel, ice) when the ice holds the group");
        Check(CampaignIceSpeed.Cap(0, 30, 0.5, out b) == 15 && b, "the ceiling is factor x FULL speed: 0.5 x 30 = 15 kn, whatever the group is ordered");
    }

    static bool Calls(Instruction i, string type, string method) =>
        (i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt) && i.Operand is MethodReference m && m.Name == method && m.DeclaringType.FullName == type;
    static int Index(MethodDefinition m, Func<Instruction, bool> p)
    {
        var list = m.Body.Instructions;
        for (int k = 0; k < list.Count; k++) if (p(list[k])) return k;
        return -1;
    }
    static MethodDefinition Method(TypeDefinition t, string name) => t.Methods.Single(x => x.Name == name);

    // 3b. The IL facts.
    static void Il(string dcmPath, string runtimePath)
    {
        var mod = ModuleDefinition.ReadModule(dcmPath);
        const string ns = "DynamicCampaignMod.";
        var layer = mod.GetType(ns + "UI.Map.WeatherMapLayer");
        var frame = mod.GetType(ns + "Core.Sim.WeatherFrame");
        var drape = mod.GetType(ns + "UI.Map.GlobeDrape");
        string L = ns + "UI.Map.WeatherMapLayer", Fr = ns + "Core.Sim.WeatherFrame", D = ns + "UI.Map.GlobeDrape";
        var take = Method(layer, "TakeBuilt");
        int load = Index(take, i => Calls(i, "UnityEngine.Texture2D", "LoadRawTextureData")), apply = Index(take, i => Calls(i, "UnityEngine.Texture2D", "Apply"));
        Check(load > 0 && apply > load && Index(take, i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "Pixels") < load,
              "TakeBuilt uploads the built frame's Pixels (LoadRawTextureData, Apply) on the main thread: a postfix on WeatherFrame.Build runs before it");
        var start = Method(layer, "StartBuild");
        Check(Index(start, i => Calls(i, "System.Threading.Tasks.Task", "Run")) > 0, "StartBuild runs the frame on Task.Run");
        var closure = layer.NestedTypes.SelectMany(t => t.Methods).Where(m => m.HasBody && Index(m, i => Calls(i, Fr, "Build")) >= 0).ToList();
        Check(closure.Count == 1 && closure[0].DeclaringType.Name.StartsWith("<>c__DisplayClass") && Index(closure[0], i => Calls(i, Fr, "WaterOf")) >= 0,
              "the Task.Run closure computes Request.Water (WaterOf over NavGrid.IsWater), then WeatherFrame.Build(request)");
        Check(mod.Types.SelectMany(t => new[] { t }.Concat(t.NestedTypes)).SelectMany(t => t.Methods).Count(m => m.HasBody && Index(m, i => Calls(i, Fr, "Build")) >= 0) == 1,
              "WeatherFrame.Build has one caller (the weather layer's frame build)");
        var image = frame.NestedTypes.Single(t => t.Methods.Any(m => m.Name == "<Image>b__0"));
        var body = Method(image, "<Image>b__0");
        Check(body.Body.Instructions.Count(i => Calls(i, Fr, "Pixel")) == 1 && Index(body, i => Calls(i, Fr, "Pixel")) < body.Body.Instructions.Count - 5,
              "Image's row body calls Pixel once per pixel, land included (the alpha only fades), so a reused buffer never keeps last frame's ice");
        var attach = Method(layer, "Attach");
        int ctor = Index(attach, i => i.OpCode.Code == Code.Newobj && ((MethodReference)i.Operand).DeclaringType.FullName == "UnityEngine.Texture2D");
        Check(ctor > 2 && attach.Body.Instructions[ctor - 2].OpCode.Code == Code.Ldc_I4_4 && attach.Body.Instructions[ctor - 1].OpCode.Code == Code.Ldc_I4_0,
              "the weather texture is TextureFormat 4 (RGBA32), no mipmaps: four bytes a pixel as Pixel writes them");
        var fr = Method(layer, "Frame");
        int hidden = Index(fr, i => Calls(i, L, "Drape"));
        Check(hidden > 0 && fr.Body.Instructions[hidden - 1].OpCode.Code == Code.Ldc_I4_0 && fr.Body.Instructions.Skip(hidden).Take(10).Any(i => i.OpCode.Code == Code.Ret),
              "Frame with the layer hidden calls Drape(false) and returns: the weather slot is free for the ice");
        var dr = Method(layer, "Drape");
        Check(Index(dr, i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_draped") == 2 && Index(dr, i => Calls(i, D, "Weather")) > 0,
              "Drape(on) returns when _draped == on, else hands GlobeDrape.Weather its texture or null");
        var de = Method(layer, "Detach");
        int dw = Index(de, i => Calls(i, D, "Weather"));
        Check(dw > 0 && de.Body.Instructions.Skip(dw - 8).Take(8).Any(i => i.OpCode.Code == Code.Ldnull), "Detach gives GlobeDrape.Weather null: the slot is let go when the map closes");
        var gw = Method(drape, "Weather");
        Check(Index(gw, i => Calls(i, D, "Changed")) > 0 && Index(gw, i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "_weatherTexture") > 0,
              "GlobeDrape.Weather returns early for the same texture, shown and box, else re-records the drape (Changed)");
        var show = Method(layer, "ShowHover");
        Check(Index(show, i => Calls(i, "MapControl.MapBase", "TryViewToGeoPosition")) > 0 && Index(show, i => Calls(i, "Noesis.TextBlock", "set_Text")) > 0 &&
              Index(show, i => Calls(i, ns + "UI.WeatherPanel.WeatherViewModel", "get_ShownUtc")) > 0,
              "ShowHover reads the point with TryViewToGeoPosition at ShownUtc and writes the body text (the postfix appends)");
        var effects = mod.GetType(ns + "Core.Sim.WeatherEffects");
        var caps = Method(effects, "UpdateCaps");
        Check(caps.Body.Instructions.Count(i => i.OpCode.Code == Code.Stfld && ((FieldReference)i.Operand).Name == "WeatherKnots") == 2 &&
              Index(caps, i => Calls(i, ns + "Core.Sim.WeatherEffects", "CapOf")) > 0,
              "UpdateCaps writes WeatherKnots for every group on every call (CapOf at sea, 0 in port): the postfix never stacks");
        var movement = mod.GetType(ns + "Core.Sim.Movement");
        var cap = Method(movement, "WeatherCapOf");
        Check(cap.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldc_R8 && double.IsPositiveInfinity((double)i.Operand)), "WeatherCapOf: WeatherKnots <= 0 is no cap (+Infinity), so beset is 0.1, never 0");
        Check(Index(Method(movement, "SpeedOf"), i => Calls(i, ns + "Core.Sim.Movement", "WeatherCapOf")) > 0 &&
              Index(Method(movement, "MapKnots"), i => Calls(i, ns + "Core.Sim.Movement", "SpeedOf")) > 0 &&
              Index(Method(movement, "Advance"), i => Calls(i, ns + "Core.Sim.Movement", "MapKnots")) > 0,
              "Advance -> MapKnots -> SpeedOf -> min(OwnSpeedOf, WeatherCapOf): movement sees WeatherKnots");
        var text = Method(movement, "SpeedText");
        Check(text.Body.CodeSize >= 40 && text.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "{0:0} kn (heavy seas)"),
              "SpeedText (52 bytes, above Mono's inline limit) writes \"(heavy seas)\" when held");
        Check(mod.GetType(ns + "UI.CampaignUI").Methods.Any(m => m.HasBody && Index(m, i => Calls(i, L, "Frame")) >= 0),
              "CampaignUI calls WeatherMapLayer.Frame every map frame");
        Check(Index(fr, i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "HideWeather" && ((FieldReference)i.Operand).DeclaringType.Name == "MapPerf") >= 0 &&
              Index(fr, i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "HideWeather") < hidden,
              "Frame reads MapPerf.HideWeather (the Cheats 'weather' toggle) before it drapes off: SEST's ice must follow it");
        // WeatherKnots: who reads it, and how (review finding 1).
        string Tf = ns + "Core.State.TaskForce", Lg = ns + "Core.Sim.Logistics";
        var readers = mod.Types.SelectMany(t => new[] { t }.Concat(t.NestedTypes)).SelectMany(t => t.Methods)
            .Where(m => m.HasBody && m.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "WeatherKnots" && ((FieldReference)i.Operand).DeclaringType.FullName == Tf))
            .Select(m => m.DeclaringType.Name + "." + m.Name).OrderBy(x => x).ToList();
        Check(readers.SequenceEqual(new[] { "Movement.WeatherCapOf", "Rhythm.ClosingHours", "Rhythm.Hold" }), "WeatherKnots is read by Movement.WeatherCapOf and the AI's Rhythm.ClosingHours and Rhythm.Hold only: " + string.Join(", ", readers));
        var rhythm = mod.GetType(ns + "Core.AI.Rhythm");
        var planners = rhythm.Methods.Where(m => m.Name == "ClosingHours" || m.Name == "Hold" && m.Parameters.Count == 4 && m.Parameters[2].ParameterType.Name == "InterceptTask").ToList();
        Check(planners.Select(m => m.Name).OrderBy(x => x).SequenceEqual(new[] { "ClosingHours", "Hold" }), "Rhythm.ClosingHours and Rhythm.Hold(his, arm, chase, others) found");
        foreach (var rm in planners)
        {
            int sp = Index(rm, i => Calls(i, Lg, "SpeedOf") && ((MethodReference)i.Operand).Parameters.Count == 2);
            int wk = Index(rm, i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "WeatherKnots");
            int mn = Index(rm, i => Calls(i, "System.Math", "Min") && rm.Body.Instructions.IndexOf(i) > wk);
            int mf = Index(rm, i => Calls(i, ns + "Core.Sim.Movement", "MapFactor") && rm.Body.Instructions.IndexOf(i) > mn);
            Check(sp >= 0 && wk > sp && mn > wk && mf > mn,
                  "Rhythm." + rm.Name + " plans with min(Logistics.SpeedOf(group, catalogue), WeatherKnots) x MapFactor: WeatherKnots is a ceiling on the group's FULL speed");
        }
        var effects2 = mod.GetType(ns + "Core.Sim.WeatherEffects");
        var stepTo = Method(mod.GetType(ns + "Core.Sim.CampaignSim"), "StepTo");
        Check(Index(Method(effects2, "Update"), i => Calls(i, ns + "Core.Sim.WeatherEffects", "UpdateCaps")) >= 0 &&
              Index(stepTo, i => Calls(i, ns + "Core.Sim.WeatherEffects", "Update")) >= 0 && Index(stepTo, i => Calls(i, ns + "Core.Sim.WeatherEffects", "UpdateCaps")) >= 0,
              "StepTo runs UpdateCaps twice a step (WeatherEffects.Update, then before Movement): the postfix runs twice, so it caches per group");
        var line = Method(mod.GetType(ns + "UI.Strategy.FleetViewModel"), "Line");
        Check(Index(line, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "{0:0} kn (out of fuel, heavy seas)") > Index(line, i => Calls(i, ns + "Core.Sim.Movement", "HeldByWeather")) &&
              Index(line, i => Calls(i, ns + "Core.Sim.Movement", "SpeedText")) > 0 && line.Body.CodeSize > 100,
              "FleetViewModel.Line formats an out-of-fuel group's \"(out of fuel, heavy seas)\" itself (SpeedText only otherwise; 437 bytes, not inlined)");
        Check(mod.Types.SelectMany(t => new[] { t }.Concat(t.NestedTypes)).SelectMany(t => t.Methods)
                 .Count(m => m.HasBody && m.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldstr && ((string)i.Operand).Contains("out of fuel, heavy seas"))) == 1,
              "no other DCM text says \"out of fuel, heavy seas\"");

        var rt = ModuleDefinition.ReadModule(runtimePath);
        var ci = rt.GetType("Sest.RuntimeFixes.CampaignIce");
        Check(ci != null && rt.GetType("Sest.RuntimeFixes.CampaignIceStyle") != null && rt.GetType("Sest.RuntimeFixes.IceRaster") != null, "runtime has the campaign ice types");
        Check(Method(ci, "AfterFrameBuild").Parameters.Select(p => p.Name).SequenceEqual(new[] { "__0", "__result" }), "frame postfix takes the request and the frame");
        Check(Method(ci, "AfterSpeedText").Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName).SequenceEqual(new[] { "__0:System.Object", "__result:System.String&" }), "SpeedText postfix rewrites the result by ref");
        Check(Method(ci, "AfterFleetLine").Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName).SequenceEqual(new[] { "__0:System.Object", "__result:System.String&" }), "fleet-line postfix rewrites the result by ref");
        Check(Index(Method(ci, "AfterLayerFrame"), i => Calls(i, "Sest.RuntimeFixes.CampaignIce", "DrapeAction")) > 0, "AfterLayerFrame decides the drape with DrapeAction (HideWeather included)");
        var applyM = Method(ci, "Apply");
        Check(!applyM.Body.Instructions.Any(i => Calls(i, "System.Reflection.MethodBase", "Invoke") || Calls(i, "System.Reflection.FieldInfo", "SetValue")) &&
              applyM.Body.Instructions.Count(i => Calls(i, "System.Reflection.FieldInfo", "GetValue")) <= 1 && !applyM.Body.Instructions.Any(i => i.OpCode.Code == Code.Box),
              "the per-group movement pass uses compiled delegates: no MethodInfo.Invoke, no FieldInfo.SetValue, no boxing (one FieldInfo read, the group name, in the diagnostics line)");
        foreach (var n in new[] { "AfterLayerFrame", "AfterLayerDetach", "AfterUpdateCaps" })
            Check(Method(ci, n).Parameters.Select(p => p.Name).SequenceEqual(new[] { "__instance" }), n + " takes the instance");
        Check(Method(ci, "AfterShowHover").Parameters.Select(p => p.Name).SequenceEqual(new[] { "__instance", "__0" }), "hover postfix takes the layer and the map");
        var entry = rt.GetType("Sest.RuntimeFixes.RuntimeFixesMod").Methods.Single(m => m.Name == "TriggerEntryPoint");
        int startAt = Index(entry, i => Calls(i, "Sest.RuntimeFixes.CampaignIce", "Start"));
        int costs = Index(entry, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "CumulativeCombatCosts");
        Check(startAt > 0 && costs > startAt, "campaign ice starts before CumulativeCombatCosts' early return");
        Check(Index(entry, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "CampaignIce") > 0, "CampaignIce switch read");
        foreach (var sw in new[] { "CampaignIceDiagnostics", "CampaignIceMap", "CampaignIceMovement" })
            Check(Index(Method(ci, "Start"), i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == sw) > 0, sw + " read");
        Check(Index(Method(ci, "Start"), i => Calls(i, "System.AppDomain", "add_AssemblyLoad")) > 0 && Index(Method(ci, "Start"), i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "SeaPower.GameMain") > 0,
              "campaign ice binds lazily (AssemblyLoad, then a GameMain.Update poll), as WorldStorms");
    }

    static string LastLines(int n) => string.Join(" | ", log.ToString().Split('\n').Where(l => l.Trim().Length > 0).Reverse().Take(n).Reverse());

    // 3a. The bindings.
    static void Bindings(Type ci, Assembly dcm, Assembly game)
    {
        Set(ci, "Diagnostics", true);
        bool ok = (bool)Call(ci, "Bind", new[] { typeof(Assembly), typeof(Assembly) }, dcm, game);
        Check(ok, "CampaignIce.Bind binds Dynamic Campaign Mod 1.0.2: " + LastLines(3));
        Check(Lines("campaign ice bind: Logistics.SpeedOf(TaskForce, IUnitCatalog) : Double ok") == 1 && Lines("campaign ice bind: MapPerf.HideWeather : Boolean ok") == 1 &&
              Lines("campaign ice bind: FleetViewModel.Line(TaskForce, Int64) : String ok") == 1 && Lines("campaign ice bind: movement delegates compiled ok") == 1,
              "the full-speed source, the weather toggle, the fleet line and the compiled delegates bind");
        Check(Lines("campaign ice bind: ") >= 64 && Lines(" MISSING") == 0 && Lines("all members of Dynamic Campaign Mod 1.0.2 (18a2416e) bound") == 1,
              Lines("campaign ice bind: ") + " members bound, none missing");
        Check(Lines("WeatherKnots is [NonSerialized] (saves unchanged) ok") == 1, "WeatherKnots is not saved");
        Set(ci, "Diagnostics", false);
    }

    static Type T(Assembly dcm, string n) => dcm.GetType("DynamicCampaignMod." + n, true);
    static object Bounds(Assembly dcm, double s, double n, double w, double e)
    {
        object b = Activator.CreateInstance(T(dcm, "Core.Data.GeoBounds"));
        Set(b, "latMin", s); Set(b, "latMax", n); Set(b, "lonMin", w); Set(b, "lonMax", e);
        return b;
    }

    // 4. A real weather frame of the polar-north theatre.
    static void Frames(Type ci, Assembly dcm, string campaigns)
    {
        var defType = T(dcm, "Core.Data.CampaignDefinition");
        var modelType = T(dcm, "Core.Sim.WeatherModel");
        var frameType = T(dcm, "Core.Sim.WeatherFrame");
        var requestType = T(dcm, "Core.Sim.WeatherFrame+Request");
        var geoType = T(dcm, "Core.Geo.GeoPoint");
        object def = Call(defType, "Load", new[] { typeof(string) }, Path.Combine(campaigns, "sest-test-polar-north", "campaign.json"));
        object bounds = Get(def, "bounds");
        Check((double)Get(bounds, "latMin") == 58 && (double)Get(bounds, "lonMax") == 60, "DCM loads the polar-north theatre 58-81N 0-60E");
        object theatre = Call(T(dcm, "Core.Sim.WeatherTheatre"), "Of", new[] { defType }, def);
        object model = Activator.CreateInstance(modelType, All, null, new[] { theatre, 77, bounds }, null);
        var size = Call(frameType, "SizeOf", new[] { bounds.GetType(), typeof(double) }, bounds, 0.25);
        int w = (int)Get(size, "Item1"), h = (int)Get(size, "Item2");
        // A water mask with a land block (as WaterOf builds from NavGrid.IsWater).
        Func<object, bool> wet = g => !((double)Get(g, "Lat") > 74 && (double)Get(g, "Lat") < 75 && (double)Get(g, "Lon") > 30 && (double)Get(g, "Lon") < 34);
        var funcType = typeof(Func<,>).MakeGenericType(geoType, typeof(bool));
        var points = new List<double[]>();
        var probe = typeof(CampaignIceTests).GetMethod(nameof(Probe), All).MakeGenericMethod(geoType);
        var del = (Delegate)probe.Invoke(null, new object[] { wet, points });
        var water = (bool[])Call(frameType, "WaterOf", new[] { bounds.GetType(), typeof(double), funcType }, bounds, 0.25, del);
        Check(water.Length == w * h && points.Count == w * h, "WaterOf asks every pixel centre once (" + points.Count + ")");
        var mine = new IceRaster(58, 0, 0.25, w, h, Utc(2028, 3, 10));
        bool same = true;
        for (int i = 0; i < points.Count; i++) same &= points[i][0] == mine.LatOf(i / w) && points[i][1] == mine.LonOf(i % w);
        Check(same, "the raster's pixel centres are WaterOf's, in its row order (row 0 south)");

        object Request(DateTime utc)
        {
            object q = Activator.CreateInstance(requestType);
            Set(q, "Model", model); Set(q, "Area", bounds); Set(q, "StepDeg", 0.5); Set(q, "CellDeg", 0.25); Set(q, "Utc", utc);
            Set(q, "Layer", Enum.ToObject(T(dcm, "Core.Sim.WeatherLayer"), 1)); Set(q, "Zones", false); Set(q, "Water", water);
            Set(q, "Width", w); Set(q, "Height", h); Set(q, "Pixels", null); Set(q, "NoImage", false);
            return q;
        }
        // DCM's own build, without the patch, then the runtime's composite on it.
        var utc = Utc(2028, 3, 10, 8);
        object q1 = Request(utc);
        object f1 = Call(frameType, "Build", new[] { requestType }, q1);
        Check((double)Get(f1, "South") == 58 && (double)Get(f1, "West") == 0 && (double)Get(f1, "CellDeg") == 0.25 && (int)Get(f1, "Width") == w && (int)Get(f1, "Height") == h &&
              (DateTime)Get(f1, "Utc") == utc && !(bool)Get(f1, "NoImage"), "WeatherFrame.Build: South, West, CellDeg, size and Utc are the request's (the drape box)");
        var native = (byte[])((byte[])Get(f1, "Pixels")).Clone();
        int n = (int)Call(ci, "Composite", new[] { typeof(object), typeof(object) }, q1, f1);
        var expect = (byte[])native.Clone();
        int m = mine.Composite(expect, water);
        Check(n == m && n > 1000 && ((byte[])Get(f1, "Pixels")).SequenceEqual(expect), "the runtime composites " + n + " ice pixels into DCM's real frame, byte for byte as this test's raster");
        int landBlock = 0;
        for (int i = 0; i < w * h; i++) if (!water[i] && mine.Percent[i] >= 15) { landBlock++; Check(((byte[])Get(f1, "Pixels")).Skip(i * 4).Take(4).SequenceEqual(native.Skip(i * 4).Take(4)), "land pixel " + i + " keeps DCM's colour"); }
        Check(landBlock > 20, landBlock + " icy land-masked pixels left as DCM drew them");

        // Through the runtime's own Harmony postfix: DCM's Build, then the ice.
        var harmony = Type.GetType("HarmonyLib.Harmony, 0Harmony", true);
        string error = null;
        try
        {
            var api = ci.Assembly.GetType("Sest.RuntimeFixes.Api", true);
            Call(api, "Postfix", new[] { typeof(MethodInfo), typeof(Type), typeof(string), typeof(string) },
                 frameType.GetMethod("Build", All, null, new[] { requestType }, null), ci, "AfterFrameBuild", "sest.test.campaign-ice");
        }
        catch (Exception e) { error = e.GetType().Name + ": " + e.Message; }
        Check(error == null, "the runtime's Build postfix patches under Harmony (" + error + ")");
        // A frame without ice first (a Hormuz-like box, as section 1 of the
        // PC tests runs before the polar ones): not counted, not logged.
        object tropic = Bounds(dcm, 20, 30, 48, 62);
        var tsize = Call(frameType, "SizeOf", new[] { tropic.GetType(), typeof(double) }, tropic, 0.25);
        int tw = (int)Get(tsize, "Item1"), th = (int)Get(tsize, "Item2");
        object qt = Request(Utc(2028, 1, 15, 8));
        Set(qt, "Area", tropic); Set(qt, "Width", tw); Set(qt, "Height", th); Set(qt, "Water", Enumerable.Repeat(true, tw * th).ToArray());
        object ft = Call(frameType, "Build", new[] { requestType }, qt);
        Check(!(bool)Get(ft, "NoImage") && (int)Get(ci, "FramesComposited") == 0 && Lines("composited with sea ice") == 0,
              "a weather frame without ice is neither counted nor logged (FramesComposited " + Get(ci, "FramesComposited") + ")");
        object q2 = Request(utc);
        object f2 = Call(frameType, "Build", new[] { requestType }, q2);
        Check(((byte[])Get(f2, "Pixels")).SequenceEqual(expect), "a patched Build returns the ice already in Pixels (before TakeBuilt would upload them)");
        Check(Lines("campaign ice map: weather frame 2028-03-10 08Z composited with sea ice (" + n + " ice pixels; frame 1)") == 1, "PC log line for the first composited frame: " + LastLines(1));
        // The forecast slider: the frame's own hour decides the ice.
        object f3 = Call(frameType, "Build", new[] { requestType }, Request(Utc(2028, 9, 10, 8)));
        var sep = new IceRaster(58, 0, 0.25, w, h, Utc(2028, 9, 10));
        int sepIce = Enumerable.Range(0, w * h).Count(i => water[i] && sep.Percent[i] >= 15);
        Check(sepIce < n / 2, "a September frame carries September's ice (" + sepIce + " pixels)");
        // A frame without pixels is left alone.
        object q4 = Request(utc); Set(q4, "NoImage", true);
        Check((int)Call(ci, "Composite", new[] { typeof(object), typeof(object) }, q4, Activator.CreateInstance(frameType, true)) == -1, "no image, no ice");
        new HarmonyLibUnpatch(harmony).All("sest.test.campaign-ice");

        // The ice-only overlay (weather layer off): 0.1 degrees over the
        // theatre, water asked only where there is ice.
        int asked = 0;
        IceRaster.SizeOf(58, 81, 0, 60, 0.1, out int ow, out int oh);
        var built = Call(ci, "BuildOverlay", new[] { typeof(double), typeof(double), typeof(double), typeof(int), typeof(int), typeof(DateTime), typeof(Func<double, double, bool>), typeof(string) },
                         58.0, 0.0, 0.1, ow, oh, Utc(2028, 3, 10), (Func<double, double, bool>)((la, lo) => { asked++; return !(la > 74 && la < 75 && lo > 30 && lo < 34); }), "box");
        var raster = (object)Get(built, "Raster");
        int icePx = (int)Get(raster, "IcePixels");
        Check(ow == 600 && oh == 230 && icePx > 10000 && asked < ow * oh / 2 && asked >= icePx, "overlay 600 x 230 at 0.1 degrees, " + icePx + " ice pixels, IsWater asked " + asked + " times");
        var px = (byte[])Get(built, "Pixels");
        int iLand = (int)Math.Floor((74.5 - 58) / 0.1) * ow + (int)Math.Floor(32 / 0.1);
        Check(px.Length == ow * oh * 4 && px[iLand * 4 + 3] == 0, "the overlay leaves land transparent");
        string hover = (string)Call(ci, "HoverText", new[] { typeof(double), typeof(double), typeof(DateTime), typeof(bool) }, 74.0, 36.0, Utc(2028, 3, 10, 8), true);
        Check(hover == "Ice 62 % (heavy pack)\nSurface groups 10 % speed (beset); submarines pass under", "hover at 74N 36E on 10 March: " + hover);
        Check(Call(ci, "HoverText", new[] { typeof(double), typeof(double), typeof(DateTime), typeof(bool) }, 67.0, 6.0, Utc(2028, 3, 10, 8), true) == null, "no ice line in the Norwegian Sea");
    }

    // 4b. The map's switches: DCM's weather toggle, the failure count per map.
    static void MapToggles(Type ci)
    {
        int Act(bool layerDraped, bool hide, bool tex, bool ours, bool shown) =>
            (int)Call(ci, "DrapeAction", new[] { typeof(bool), typeof(bool), typeof(bool), typeof(bool), typeof(bool) }, layerDraped, hide, tex, ours, shown);
        int leave = (int)Get(ci, "Leave"), drape = (int)Get(ci, "DrapeIt"), off = (int)Get(ci, "TakeOff");
        Check(Act(false, false, true, false, false) == drape && Act(false, false, true, true, false) == drape, "weather layer off: the ice texture takes the free slot");
        Check(Act(false, false, true, true, true) == leave && Act(true, false, true, false, false) == leave && Act(false, false, false, false, false) == leave,
              "already draped, the layer's own image in the slot, or no ice: nothing to do");
        Check(Act(false, true, true, false, false) == leave && Act(false, true, true, true, true) == off && Act(true, true, true, false, false) == leave,
              "MapPerf.HideWeather (Cheats: weather): the ice is not draped, and SEST's texture is taken off the slot");
        var overlay = ci.GetNestedType("Overlay", All);
        var builtType = overlay.GetNestedType("Built", All);
        Set(overlay, "Failures", 0);
        Set(overlay, "DateKey", 20280310); Set(overlay, "BoxKey", "box");
        var fromException = typeof(System.Threading.Tasks.Task).GetMethods().Single(m => m.Name == "FromException" && m.IsGenericMethod);
        for (int k = 0; k < 3; k++)
        {
            Set(overlay, "Building", fromException.MakeGenericMethod(builtType).Invoke(null, new object[] { new InvalidOperationException("test build " + k) }));
            Call(ci, "TakeOverlay", Type.EmptyTypes);
        }
        Check((int)Get(overlay, "Failures") == 3 && Lines("campaign ice map: the ice overlay was not built") == 3 &&
              Lines("campaign ice map: the ice-only overlay failed 3 times and is off for this map") == 1, "three failed builds: one line says the ice-only overlay is off for this map");
        Check(Index(Method(ModuleDefinition.ReadModule(ci.Assembly.Location).GetType("Sest.RuntimeFixes.CampaignIce").NestedTypes.Single(x => x.Name == "Overlay"), "Release"),
                    i => Calls(i, "Sest.RuntimeFixes.CampaignIce/Overlay", "Forget")) == 0, "Release starts with Forget (texture, keys, build and failure count)");
        Call(overlay, "Forget", Type.EmptyTypes);
        Check((int)Get(overlay, "Failures") == 0 && (int)Get(overlay, "DateKey") == int.MinValue && Get(overlay, "Building") == null,
              "the next map (Release: a new layer or Detach) starts the count again");
    }

    // A Func<GeoPoint, bool> for WaterOf that records each point it is asked.
    static Func<G, bool> Probe<G>(Func<object, bool> wet, List<double[]> points) => g =>
    {
        object o = g;
        points.Add(new[] { (double)Get(o, "Lat"), (double)Get(o, "Lon") });
        return wet(o);
    };

    sealed class HarmonyLibUnpatch
    {
        readonly Type harmony;
        internal HarmonyLibUnpatch(Type h) { harmony = h; }
        internal void All(string id)
        {
            object hy = Activator.CreateInstance(harmony, id);
            var self = harmony.GetMethod("UnpatchSelf", Type.EmptyTypes);
            if (self != null) self.Invoke(hy, null);
            else harmony.GetMethod("UnpatchAll", new[] { typeof(string) }).Invoke(hy, new object[] { id });
        }
    }

    // A stand-in for DCM's (internal) IUnitCatalog: a transparent proxy that
    // answers ShipSpeedKnots and IsSubmarine from a table, null/0 otherwise.
    sealed class FakeCatalog : System.Runtime.Remoting.Proxies.RealProxy
    {
        readonly Dictionary<string, double> knots;
        internal int SpeedCalls, SubmarineCalls;
        internal FakeCatalog(Type catalog, Dictionary<string, double> knots) : base(catalog) { this.knots = knots; }
        public override System.Runtime.Remoting.Messaging.IMessage Invoke(System.Runtime.Remoting.Messaging.IMessage msg)
        {
            var call = (System.Runtime.Remoting.Messaging.IMethodCallMessage)msg;
            var m = (MethodInfo)call.MethodBase;
            object ret = null;
            string ini = call.InArgs.Length > 0 ? call.InArgs[0] as string : null;
            if (m.Name == "ShipSpeedKnots") { SpeedCalls++; ret = ini != null && knots.TryGetValue(ini, out double k) ? k : 0.0; }
            else if (m.Name == "IsSubmarine") { SubmarineCalls++; ret = ini != null && ini.Contains("_ss_"); }
            else if (m.ReturnType.IsValueType && m.ReturnType != typeof(void)) ret = Activator.CreateInstance(m.ReturnType);
            return new System.Runtime.Remoting.Messaging.ReturnMessage(ret, null, 0, call.LogicalCallContext, call);
        }
    }

    // 5. Movement on real TaskForce objects.
    static void Movement(Type ci, Assembly dcm)
    {
        var tfType = T(dcm, "Core.State.TaskForce");
        var hullType = T(dcm, "Core.State.Hull");
        var geoType = T(dcm, "Core.Geo.GeoPoint");
        var routeType = T(dcm, "Core.State.RoutePoint");
        var movement = T(dcm, "Core.Sim.Movement");
        var moverType = T(dcm, "Core.State.Mover");
        var catalogType = T(dcm, "Core.Data.IUnitCatalog");
        var logistics = T(dcm, "Core.Sim.Logistics");
        // Full speeds: an Oslo 20 kn, a Kobben 15 kn (the catalogue's ShipSpeedKnots).
        var fake = new FakeCatalog(catalogType, new Dictionary<string, double> { { "knm_ffg_oslo", 20 }, { "knm_ss_kobben", 15 } });
        object catalog = fake.GetTransparentProxy();
        Check(catalogType.IsInstanceOfType(catalog), "the stand-in catalogue is an IUnitCatalog");
        object Group(double lat, double lon, double knots, params string[] units)
        {
            object tf = Activator.CreateInstance(tfType, true);
            Set(tf, "Name", "test group"); Set(tf, "Position", Activator.CreateInstance(geoType, lat, lon)); Set(tf, "SpeedKnots", knots);
            Set(tf, "PortId", null);
            var ships = (IList)Get(tf, "Ships");
            foreach (var u in units) { object h = Activator.CreateInstance(hullType, true); Set(h, "UnitIni", u); Set(h, "Fuel", 1.0); ships.Add(h); }
            return tf;
        }
        var day = Utc(2028, 3, 10, 8);
        double Speed(object tf) => (double)Call(movement, "SpeedOf", new[] { moverType }, tf);
        double Full(object tf) => (double)Call(logistics, "SpeedOf", new[] { tfType, catalogType }, tf, catalog);
        string Text(object tf)
        {
            string s = (string)Call(movement, "SpeedText", new[] { moverType }, tf);
            var a = new object[] { tf, s };
            ci.GetMethod("AfterSpeedText", All).Invoke(null, a);
            return (string)a[1];
        }
        void ApplyWith(object tf, object cat) { Set(tf, "WeatherKnots", 0.0); Call(ci, "Apply", new[] { typeof(object), typeof(DateTime), typeof(object) }, tf, day, cat); }
        void Apply(object tf) => ApplyWith(tf, catalog);
        double Knots(object tf) => (double)Get(tf, "WeatherKnots");

        Check((bool)Call(T(dcm, "Core.Sim.TestBattles"), "IsSubmarineIni", new[] { typeof(string) }, "knm_ss_kobben") &&
              !(bool)Call(T(dcm, "Core.Sim.TestBattles"), "IsSubmarineIni", new[] { typeof(string) }, "knm_ffg_oslo"), "DCM's own submarine test (no catalogue): Kobben is one, Oslo is not");
        object pack = Group(74.0, 36.0, 20, "knm_ffg_oslo");                      // 62 %: blocked for class none
        Check(Full(pack) == 20, "DCM's Logistics.SpeedOf through the catalogue: the Oslo's 20 kn (" + Full(pack) + ")");
        Apply(pack);
        Check(Math.Abs(Knots(pack) - 2.0) < 1e-9 && Math.Abs(Speed(pack) - 2.0) < 1e-9, "a frigate in 62 % ice is beset: DCM's SpeedOf 2 kn of 20 (" + Speed(pack) + ")");
        Check(fake.SpeedCalls > 0, "the cap came from the catalogue (Logistics.SpeedOf asked ShipSpeedKnots " + fake.SpeedCalls + " times)");
        Check(Text(pack) == "2 kn (ice)", "the speed text reads " + Text(pack));
        double[] hours = (double[])Call(movement, "HoursToRoutePoints", new[] { moverType }, pack);
        Check(hours.Length == 0, "no route, no ETA");
        var route = (IList)Get(pack, "Route");
        object rp = Activator.CreateInstance(routeType, true); Set(rp, "Point", Activator.CreateInstance(geoType, 74.0, 37.0)); route.Add(rp);
        hours = (double[])Call(movement, "HoursToRoutePoints", new[] { moverType }, pack);
        Check(hours.Length == 1 && hours[0] > 2 && !double.IsInfinity(hours[0]), "HoursToRoutePoints stays finite in the pack: " + N(hours[0]) + " h for 16 nm at 2 kn x the map factor");
        object edge = Group(72.0, 36.0, 20, "knm_ffg_oslo");                      // 18.7 %: caution 0.7
        Apply(edge);
        Check(Math.Abs(Speed(edge) - 14) < 1e-9 && Text(edge) == "14 kn (ice)", "at the ice edge (19 %) 0.7 x 20 = 14 kn, " + Text(edge));
        object sub = Group(74.6, 36.0, 15, "knm_ss_kobben");
        Apply(sub);
        Check(Speed(sub) == 15 && Text(sub) == "15 kn" && Knots(sub) == 0, "a submarine passes under the pack at its own speed");
        object mixed = Group(74.6, 36.0, 15, "knm_ss_kobben", "knm_ffg_oslo");
        Apply(mixed);
        Check(Math.Abs(Speed(mixed) - 1.5) < 1e-9, "a frigate with the submarine sets the group's pace (0.1 x the Kobben's 15 kn, the slower hull: 1.5 kn)");
        object open = Group(67.0, 6.0, 20, "knm_ffg_oslo");
        Apply(open);
        Check(Speed(open) == 20 && Knots(open) == 0 && Text(open) == "20 kn", "the Norwegian Sea control is untouched");
        object storm = Group(74.0, 36.0, 20, "knm_ffg_oslo");
        Set(storm, "WeatherKnots", 1.0);
        Call(ci, "Apply", new[] { typeof(object), typeof(DateTime), typeof(object) }, storm, day, catalog);
        Check(Speed(storm) == 1 && Text(storm) == "1 kn (heavy seas)", "heavy seas below the ice cap keep DCM's text");
        object inPort = Group(74.0, 36.0, 20, "knm_ffg_oslo");
        Set(inPort, "PortId", "home_nor_haakonsvern");
        Apply(inPort);
        Check(Knots(inPort) == 0, "a group in port is left alone");

        // The ceiling is the group's full speed, not its order (review finding 1).
        object slow = Group(72.0, 36.0, 10, "knm_ffg_oslo");                      // ordered 10 of 20, 0.7 ice
        Apply(slow);
        Check(Math.Abs(Knots(slow) - 14) < 1e-9, "a group ordered 10 kn of its 20 in 0.7 ice gets WeatherKnots 14 (0.7 x full speed), not 7 (" + N(Knots(slow)) + ")");
        Check(Speed(slow) == 10 && Text(slow) == "10 kn", "it keeps its ordered 10 kn (under the ceiling): " + Text(slow));
        Set(slow, "SpeedKnots", 20.0);
        Apply(slow);
        Check(Math.Abs(Speed(slow) - 14) < 1e-9 && Text(slow) == "14 kn (ice)", "ordered to its full 20 kn the next step it makes 14 kn, as the cap said: " + Text(slow));
        object stopped = Group(74.0, 36.0, 0, "knm_ffg_oslo");
        Apply(stopped);
        Check(Math.Abs(Knots(stopped) - 2.0) < 1e-9 && Speed(stopped) == 0 && Text(stopped) == "0 kn",
              "a stopped group in the pack is capped too (WeatherKnots 2 kn, for the AI), and stays stopped: " + Text(stopped));
        // DCM's own AI estimate: Rhythm.ClosingHours = min(Logistics.SpeedOf, WeatherKnots) x MapFactor.
        var rhythmType = T(dcm, "Core.AI.Rhythm");
        object rhythm = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(rhythmType);
        Set(rhythm, "_catalog", catalog);
        object target = Group(72.0, 52.0, 0, "knm_ffg_oslo");
        double dist = (double)Call(geoType, "DistanceNm", new[] { geoType, geoType }, Get(edge, "Position"), Get(target, "Position"));
        double mapFactor = (double)Call(movement, "MapFactor", new[] { moverType }, slow);
        double ClosingHours(object arm) => (double)Call(rhythm, "ClosingHours", new[] { tfType, tfType }, arm, target);
        Set(slow, "SpeedKnots", 10.0);
        Apply(slow);
        double h1 = ClosingHours(slow), expect1 = (dist - 100) / (14 * mapFactor);
        Check(dist > 200 && Math.Abs(h1 - expect1) <= 0.11, "DCM's Rhythm.ClosingHours for the 10 kn-ordered group in 0.7 ice: " + N(h1, "0.0") + " h for " + N(dist, "0") +
              " nm (100 nm standoff), the 14 kn ceiling x map factor " + N(mapFactor, "0") + " (" + N(expect1, "0.00") + " h); the old 0.7 x ordered speed (7 kn) gave " + N((dist - 100) / (7 * mapFactor), "0.0") + " h");
        Apply(stopped);
        double h0 = ClosingHours(stopped);
        Set(stopped, "WeatherKnots", 0.0);
        double hFree = ClosingHours(stopped);
        Check(h0 > hFree * 5 && Math.Abs(h0 - Math.Min(24, (dist - 100) / (2 * mapFactor))) <= 0.11 || h0 == 24 && hFree < 24,
              "a stopped group in the pack: ClosingHours " + N(h0, "0.0") + " h with SEST's cap (2 kn), " + N(hFree, "0.0") + " h with none (the AI would have planned 20 kn in heavy pack)");
        // No catalogue (never in a campaign): the ordered speed, as before.
        object bare = Group(72.0, 36.0, 10, "knm_ffg_oslo");
        ApplyWith(bare, null);
        Check(Math.Abs(Knots(bare) - 7) < 1e-9, "without a catalogue the ceiling falls back to 0.7 x the ordered speed (7 kn)");

        // Out of fuel: Logistics.SpeedOf caps at 5 kn; the fleet list's own text.
        object dry = Group(73.5, 36.0, 5, "knm_ffg_oslo");                         // 50 %: restricted 0.4
        Set(((IList)Get(dry, "Ships"))[0], "Fuel", 0.0);
        Apply(dry);
        Check(Full(dry) == 5 && Math.Abs(Knots(dry) - 2) < 1e-9 && Math.Abs(Speed(dry) - 2) < 1e-9 && (bool)Call(movement, "HeldByWeather", new[] { moverType }, dry),
              "an out-of-fuel group (5 kn) in 50 % ice: 0.4 x 5 = 2 kn, held");
        string Line(object tf, string dcmLine) { var a = new object[] { tf, dcmLine }; ci.GetMethod("AfterFleetLine", All).Invoke(null, a); return (string)a[1]; }
        string fuelLine = "Barents Sea \u00b7 holding \u00b7 " + string.Format(CultureInfo.InvariantCulture, "{0:0} kn (out of fuel, heavy seas)", Speed(dry));
        Check(Line(dry, fuelLine) == "Barents Sea \u00b7 holding \u00b7 2 kn (out of fuel, ice)", "the fleet list's out-of-fuel line reads " + Line(dry, fuelLine));
        Check(Line(open, "Norwegian Sea \u00b7 holding \u00b7 5 kn (out of fuel, heavy seas)").EndsWith("(out of fuel, heavy seas)"), "a group the ice does not hold keeps DCM's out-of-fuel text");
        Check(CampaignIceSpeed.Text("2 kn (out of fuel)", true) == "2 kn (out of fuel)", "no change when not held");

        // The runtime's own Harmony postfixes on DCM's SpeedText and FleetViewModel.Line.
        string error = null;
        try
        {
            var api = ci.Assembly.GetType("Sest.RuntimeFixes.Api", true);
            Call(api, "Postfix", new[] { typeof(MethodInfo), typeof(Type), typeof(string), typeof(string) },
                 movement.GetMethod("SpeedText", All, null, new[] { moverType }, null), ci, "AfterSpeedText", "sest.test.campaign-ice-speed");
            Call(api, "Postfix", new[] { typeof(MethodInfo), typeof(Type), typeof(string), typeof(string) },
                 T(dcm, "UI.Strategy.FleetViewModel").GetMethod("Line", All, null, new[] { tfType, typeof(long) }, null), ci, "AfterFleetLine", "sest.test.campaign-ice-speed");
        }
        catch (Exception e) { error = e.GetType().Name + ": " + e.Message; }
        Check(error == null, "the runtime's SpeedText and FleetViewModel.Line postfixes patch under Harmony (" + error + ")");
        Apply(edge);
        Check((string)Call(movement, "SpeedText", new[] { moverType }, edge) == "14 kn (ice)" && (string)Call(movement, "SpeedText", new[] { moverType }, open) == "20 kn",
              "DCM's own SpeedText, patched, reads \"14 kn (ice)\" in ice and \"20 kn\" in open water");
        new HarmonyLibUnpatch(Type.GetType("HarmonyLib.Harmony, 0Harmony", true)).All("sest.test.campaign-ice-speed");
        Check((string)Call(movement, "SpeedText", new[] { moverType }, edge) == "14 kn (heavy seas)", "unpatched again: DCM's own text");
        // DCM rewrote the cap (next UpdateCaps without ice): the text is DCM's again.
        Set(pack, "WeatherKnots", 3.0);
        Check(Text(pack) == "3 kn (heavy seas)", "a stale ice record never relabels DCM's own cap");
        Set(dry, "WeatherKnots", 3.0);
        Check(Line(dry, fuelLine) == fuelLine, "nor DCM's out-of-fuel text");
        // A season later the same spot is open water.
        object autumn = Group(72.0, 36.0, 20, "knm_ffg_oslo");
        Set(autumn, "WeatherKnots", 0.0);
        Call(ci, "Apply", new[] { typeof(object), typeof(DateTime), typeof(object) }, autumn, Utc(2028, 9, 10), catalog);
        Check(Speed(autumn) == 20, "10 September at 72N 36E: open, full speed");

        // The per-group cache: one ice work-out per group, day, tile and hulls.
        var heldOf = ci.GetField("Groups", All).GetValue(null);
        int Refreshes(object tf) { var args = new object[] { tf, null }; heldOf.GetType().GetMethod("TryGetValue").Invoke(heldOf, args); return (int)Get(args[1], "Refreshes"); }
        object cached = Group(73.5, 36.0, 20, "knm_ffg_oslo");
        int subCalls = fake.SubmarineCalls;
        for (int k = 0; k < 50; k++) Apply(cached);
        Check(Refreshes(cached) == 1 && Math.Abs(Knots(cached) - 8) < 1e-9, "50 passes at the same tile and day: the ice worked out once (" + Refreshes(cached) + "), cap 0.4 x 20 = 8 kn each time");
        Check(fake.SubmarineCalls == subCalls, "the hull classes come from the cache, not the catalogue, on every pass");
        Set(cached, "Position", Activator.CreateInstance(geoType, 73.5 + 0.001, 36.0));
        Apply(cached);
        Check(Refreshes(cached) == 1, "a move inside the same 0.05-degree tile keeps the cache");
        Set(cached, "Position", Activator.CreateInstance(geoType, 74.0, 36.0));
        Apply(cached);
        Check(Refreshes(cached) == 2 && Math.Abs(Knots(cached) - 2) < 1e-9, "a new tile is worked out again: 62 %, beset, 2 kn");
        Call(ci, "Apply", new[] { typeof(object), typeof(DateTime), typeof(object) }, cached, day.AddDays(1), catalog);
        Check(Refreshes(cached) == 3, "a new day is worked out again");
        object hull2 = Activator.CreateInstance(hullType, true); Set(hull2, "UnitIni", "knm_ss_kobben"); Set(hull2, "Fuel", 1.0);
        ((IList)Get(cached, "Ships")).Add(hull2);
        Call(ci, "Apply", new[] { typeof(object), typeof(DateTime), typeof(object) }, cached, day.AddDays(1), catalog);
        Check(Refreshes(cached) == 4, "a changed group (a hull joined) is worked out again");
        long before = (long)Get(ci, "GroupPasses");
        object hormuz = Group(26.0, 56.7, 20, "knm_ffg_oslo");
        Apply(hormuz);
        Check((long)Get(ci, "GroupPasses") == before + 1 && Refreshes(hormuz) == 0 && Knots(hormuz) == 0,
              "a group under 39.9 degrees is left after its latitude: no ice work, no cap");

        // The UpdateCaps adapter over a real CampaignState's group list.
        var stateType = T(dcm, "Core.State.CampaignState");
        object state = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(stateType);
        Set(state, "Now", day);
        if (Get(state, "TaskForces") == null) Set(state, "TaskForces", Activator.CreateInstance(typeof(List<>).MakeGenericType(tfType)));
        var list = (IList)Get(state, "TaskForces");
        object a = Group(74.0, 36.0, 20, "knm_ffg_oslo"), b2 = Group(67.0, 6.0, 20, "knm_ffg_oslo");
        list.Add(a); list.Add(b2);
        var effects = (object)System.Runtime.Serialization.FormatterServices.GetUninitializedObject(T(dcm, "Core.Sim.WeatherEffects"));
        Set(effects, "_state", state);
        Set(effects, "_catalog", catalog);
        Set(ci, "Diagnostics", true);
        ci.GetMethod("AfterUpdateCaps", All).Invoke(null, new[] { effects });
        Set(ci, "Diagnostics", false);
        Check(Speed(a) == 2 && Speed(b2) == 20, "the UpdateCaps postfix walks CampaignState.TaskForces");
        Check(Lines("campaign ice @ 2028-03-10 08:00: test group at 74.00, 36.00: ice 63 % (heavy pack), factor 0.1 (beset), full speed 20.0 kn, ordered 20.0 kn, weather cap none -> 2.0 kn (ice)") == 1,
              "the diagnostics line, once per group and campaign hour: " + LastLines(1));
        // Twice a step (StepTo: WeatherEffects.Update, then UpdateCaps before Movement): DCM rewrites, SEST re-applies from the cache.
        for (int k = 0; k < 2; k++) { Set(a, "WeatherKnots", 0.0); ci.GetMethod("AfterUpdateCaps", All).Invoke(null, new[] { effects }); }
        Check(Speed(a) == 2 && Refreshes(a) == 1, "each UpdateCaps pass puts the cap back, the ice worked out once for the group");
    }

    // 6. The polar test campaigns: the ice in view, the transit line into the
    // pack, and the transit pair clear of the other tests' contacts (DCM's
    // own GeoPoint.DistanceNm and ContactRanges.OpenSea).
    static void Campaigns(Assembly dcm, string campaigns)
    {
        var defType = T(dcm, "Core.Data.CampaignDefinition");
        var geoType = T(dcm, "Core.Geo.GeoPoint");
        object openSea = T(dcm, "Core.State.ContactRanges").GetField("OpenSea", All).GetValue(null);
        double contactNm = (double)Get(openSea, "ContactNm"), joinNm = (double)Get(openSea, "SurfaceJoinNm");
        Check(contactNm == 100 && joinNm == 200, "DCM's open-sea contact " + contactNm + " nm, surface join " + joinNm + " nm");
        double Nm(double[] p, double[] q) => (double)Call(geoType, "DistanceNm", new[] { geoType, geoType }, Activator.CreateInstance(geoType, p[0], p[1]), Activator.CreateInstance(geoType, q[0], q[1]));
        foreach (var (folder, blue, red, date) in new[] {
            ("sest-test-polar-north", "Group N5 - Murman coast transit", "Red N3 - Northern Fleet pack picket", Utc(2028, 3, 10, 8)),
            ("sest-test-polar-south", "Group S5 - Elephant Island transit", "Red S3 - Russian Weddell pack picket", Utc(2029, 1, 12, 12)) })
        {
            string file = Path.Combine(campaigns, folder, "campaign.json");
            object def = Call(defType, "Load", new[] { typeof(string) }, file);
            var text = File.ReadAllText(file);
            Check(text.Contains("\"" + blue + "\"") && text.Contains("\"" + red + "\""), folder + " has the transit pair");
            object b = Get(def, "bounds");
            double s = (double)Get(b, "latMin"), n = (double)Get(b, "latMax"), w = (double)Get(b, "lonMin"), e = (double)Get(b, "lonMax");
            double cell = IceRaster.CellFor(s, n, w, e, 0.1, 1000000);
            IceRaster.SizeOf(s, n, w, e, cell, out int ow, out int oh);
            var r = new IceRaster(s, w, cell, ow, oh, date);
            r.Paint(null);
            int edges = 0;
            for (int y = 0; y < oh; y++) for (int x = 0; x < ow; x++) if (r.KindAt(x, y, null) == 2) edges++;
            Check(r.IcePixels > 5000 && edges > 200, folder + ": the overlay at the start has " + r.IcePixels + " ice pixels and " + edges + " ice-edge pixels");

            // The forces as DCM loaded them.
            var forces = ((IList)Get(def, "forces")).Cast<object>().Where(f => Get(f, "at") != null)
                .ToDictionary(f => (string)Get(f, "name"), f => (side: (string)Get(f, "side"), at: (double[])Get(f, "at")));
            var (bSide, bAt) = forces[blue];
            var (rSide, rAt) = forces[red];
            Check(bSide != rSide, folder + ": the transit pair is on opposing sides");
            // The straight line DCM's Movement.Advance runs (linear in lat and lon), every ~2 nm.
            double total = Nm(bAt, rAt);
            int steps = (int)Math.Ceiling(total / 2);
            double run = 0, at30 = -1, left30 = 0, at15 = -1;
            double[] prev = bAt;
            double c0 = SeaIceModel.Concentration(bAt[0], bAt[1], date);
            for (int k = 1; k <= steps; k++)
            {
                double f = (double)k / steps;
                var p = new[] { bAt[0] + (rAt[0] - bAt[0]) * f, bAt[1] + (rAt[1] - bAt[1]) * f };
                run += Nm(prev, p); prev = p;
                double c = SeaIceModel.Concentration(p[0], p[1], date);
                if (at15 < 0 && c >= 15) at15 = run;
                if (at30 < 0 && c >= 30) { at30 = run; left30 = Nm(p, rAt); }
            }
            Check(c0 < 10 && at15 > 0 && at30 > at15, folder + ": " + blue + " starts open (" + N(c0) + " %), crosses 15 % after " + N(at15, "0") + " nm and 30 % after " + N(at30, "0") + " nm");
            Check(left30 > contactNm, folder + ": the 0.4 (30 %) leg starts " + N(left30, "0") + " nm from " + red + ", before DCM's " + contactNm + " nm contact");
            // Neither starts a contact: more than ContactNm from every opposing group.
            foreach (var (name, side, at) in new[] { (blue, bSide, bAt), (red, rSide, rAt) })
            {
                double near = forces.Where(x => x.Value.side != side).Min(x => Nm(at, x.Value.at));
                Check(near > contactNm, folder + ": " + name + " starts " + N(near, "0") + " nm from the nearest opposing group (contact " + contactNm + " nm)");
            }
            // Nor joins the other tests' fights: patrols' first contacts, more than SurfaceJoinNm away.
            foreach (var pr in ((IList)Get(def, "patrols")).Cast<object>())
            {
                string force = (string)Get(pr, "force");
                if (!forces.ContainsKey(force) || force == blue || force == red) continue;
                var pts = ((IList)Get(pr, "points")).Cast<double[]>().ToList();
                var foes = forces.Where(x => x.Value.side != forces[force].side && x.Key != blue && x.Key != red).Select(x => x.Value.at).ToList();
                double[] mid = null;
                for (int k = 0; k + 1 < pts.Count && mid == null; k++)
                    for (int i = 0; i <= 400 && mid == null; i++)
                    {
                        double f = i / 400.0;
                        var q = new[] { pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f };
                        var foe = foes.FirstOrDefault(g => Nm(q, g) <= contactNm);
                        if (foe != null) mid = new[] { (q[0] + foe[0]) / 2, (q[1] + foe[1]) / 2 };
                    }
                if (mid == null) continue;
                double away = Math.Min(Nm(mid, bAt), Nm(mid, rAt));
                Check(away > joinNm, folder + ": " + force + "'s contact at " + N(mid[0], "0.00") + ", " + N(mid[1], "0.00") + " is " + N(away, "0") + " nm from the transit pair (join " + joinNm + " nm)");
            }
        }
    }

    // 7. Another DCM image binds nothing, with one line.
    static void HashLock(Assembly rt, Type ci, string runtimePath)
    {
        int before = Lines("campaign ice unavailable");
        bool ok = (bool)Call(ci, "Bind", new[] { typeof(Assembly), typeof(Assembly) }, rt, null);
        Check(!ok && Lines("campaign ice unavailable; Dynamic Campaign Mod's map and movement unchanged: InvalidOperationException: campaign ice requires the inspected Dynamic Campaign Mod 1.0.2 image (18a2416e)") == before + 1,
              "an image with another hash: nothing bound, one line: " + LastLines(1));
        Check(!(bool)Get(ci, "bound") && (bool)Get(ci, "stopped") && (bool)Get(ci, "mapStopped"), "stopped closed");
    }
}
