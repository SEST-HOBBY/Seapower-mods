using System;
using System.Linq;
using System.Reflection;
using Sest.RuntimeFixes;
using SeaPower;
using UnityEngine;

// IceFeaturesBattle.cs against the stub game types (tests/stubs/GameStubs.cs): switches and
// fail-closed install, the Harmony target, the no-go postfix on own and AI units (surface ship and
// submarine driven toward the Ross front), the far-from-Antarctica skip, the cliff and berg
// objects, drift and melt in a battle, and the clean-up when the battle ends. The stubs follow
// r16's use of the game's members; that the real members match is a PC test (README).
internal static class BattleTests
{
    private static void Check(bool ok, string why) => IceFeaturesTests.Check(ok, why);

    private static readonly string[] Off = { "[Runtime]", "SeaIce=1" };
    private static readonly string[] On = { "[Runtime]", "IceShelves=1", "Icebergs=1", "IceFeaturesDiagnostics=1", "IcebergSstC=0.5" };

    internal static void Run()
    {
        Switches();
        NoGo();
        Visuals();
        FailClosed();
        Console.WriteLine("battle part (stub game types): switches, fail-closed install, no-go postfix, cliffs, bergs, drift, melt and clean-up checked");
    }

    private static void Switches()
    {
        IceFeaturesBattle.ResetForTests(); Api.Patches.Clear(); Api.Lines.Clear();
        IceFeaturesBattle.Install(Off, Api.FindType);
        Check(IceFeaturesBattle.State == "off" && Api.Patches.Count == 0 && IceFeaturesBattle.Root == null, "OFF unless IceShelves=1 or Icebergs=1: nothing patched, no driver");
        IceFeaturesBattle.Install(new[] { "[Runtime]", "IceShelves=0", "Icebergs=0", "[Other]", "IceShelves=1" }, Api.FindType);
        Check(IceFeaturesBattle.State == "off", "a switch outside [Runtime] does not count");

        IceFeaturesBattle.ResetForTests(); Api.Patches.Clear(); Api.Lines.Clear();
        IceFeaturesBattle.Install(On, n => n == "SeaPower.Compartments" ? throw new MissingMemberException(n) : Api.FindType(n));
        Check(!IceFeaturesBattle.NoGoOn && IceFeaturesBattle.VisualsOn && Api.Patches.Count == 0, "a missing game type leaves only that part out");
        Check(Api.Lines.Any(l => l.Contains("no-go rule for ships and submarines not installed; native behaviour kept")), "and says so in one log line");

        IceFeaturesBattle.ResetForTests(); Api.Patches.Clear(); Api.Lines.Clear();
        IceFeaturesBattle.Install(new[] { "[Runtime]", "Icebergs=1" }, Api.FindType);
        Check(IceFeaturesBattle.BergsOn && !IceFeaturesBattle.ShelvesOn && Api.Patches.Count == 0, "Icebergs=1 alone: no speed patch");

        IceFeaturesBattle.ResetForTests(); Api.Patches.Clear(); Api.Lines.Clear();
        IceFeaturesBattle.Install(new[] { "[Runtime]", "IceShelves=1", "IceShelfStandoffNm=99", "IcebergMaxDrawn=abc" }, Api.FindType);
        Check(IceFeaturesBattle.StandoffNm == IceFeaturesData.SubmarineStandoffNm && IceFeaturesBattle.MaxDrawn == 400, "out-of-range options fall back to the defaults");

        IceFeaturesBattle.ResetForTests(); Api.Patches.Clear(); Api.Lines.Clear();
        IceFeaturesBattle.Install(On, Api.FindType);
        Check(IceFeaturesBattle.NoGoOn && IceFeaturesBattle.VisualsOn && IceFeaturesBattle.Root != null && IceFeaturesBattle.Root.GetComponent<IceFeaturesDriver>() != null, "IceShelves=1 Icebergs=1: rule and visuals installed, driver attached");
        Check(Api.Patches.Count == 1 && Api.Patches[0].Target.DeclaringType == typeof(Compartments) && Api.Patches[0].Target.Name == "UpdateWantedVelocityInKnots" && Api.Patches[0].Callback == "SpeedPostfix", "one postfix on Compartments.UpdateWantedVelocityInKnots (the hook SeaIceBattle caps speed in)");
        Check(Api.Lines.Any(l => l.Contains("ice features installed")), "install logged");
    }

    private static void Postfix(Compartments c)
    {
        c.UpdateWantedVelocityInKnots();
        var p = Api.Patches[0];
        p.Owner.GetMethod(p.Callback, Api.All).Invoke(null, new object[] { c });
    }

    private static void RossFront(out double lat, out double lon)
    {
        for (int l = 0; l < IceFeaturesData.FrontFeature.Length; l++)
        {
            int s = IceShelves.ShelfOfFeature(IceFeaturesData.FrontFeature[l]);
            if (s >= 0 && IceFeaturesData.ShelfName[s] == "Ross Ice Shelf" && IceFeaturesData.FrontStart[l + 1] - IceFeaturesData.FrontStart[l] > 50)
            {
                int k = (IceFeaturesData.FrontStart[l] + IceFeaturesData.FrontStart[l + 1]) / 2;
                lat = IceFeaturesData.FrontPts[2 * k + 1] / 1000.0; lon = IceFeaturesData.FrontPts[2 * k] / 1000.0;
                return;
            }
        }
        throw new Exception("no Ross front line");
    }

    private static void NoGo()
    {
        var env = new SeaPower.Environment { DateTime = new DateTime(2029, 1, 20, 12, 0, 0), SeaState = 3 };
        Singleton<SeaPower.Environment>.Set(env);
        RossFront(out double flat, out double flon);
        foreach (bool sub in new[] { false, true })
        {
            ObjectBase ob = sub ? new Submarine { name = "test submarine" } : new ObjectBase { name = "test frigate", IsPlayerObject = true };
            IceFeatureGeo.Destination(flat, flon, 0, 6.0, out double lat, out double lon);
            ob._geoPosition = new GeoPosition { _latitude = lat, _longitude = lon };
            ob.transform.eulerAngles = new Vector3(0, 180, 0); // due south, toward the front
            var c = new Compartments(ob) { Ordered = 30 };
            double least = double.PositiveInfinity;
            int holdsBefore = IceFeaturesBattle.Holds;
            for (int t = 0; t < 3600; t++)
            {
                GameTime.Mission = 1000 + t;
                Postfix(c);
                least = Math.Min(least, IceShelves.Clearance(ob._geoPosition._latitude, ob._geoPosition._longitude, 20));
                IceFeatureGeo.Destination(ob._geoPosition._latitude, ob._geoPosition._longitude, 180, c.WantedVelocityInKnots / 3600.0, out lat, out lon);
                ob._geoPosition._latitude = lat; ob._geoPosition._longitude = lon;
            }
            double limit = sub ? IceFeaturesData.SubmarineStandoffNm : ShelfSpeedState.SurfaceLimitNm;
            Check(IceFeaturesBattle.Holds > holdsBefore && least >= limit - 30.0 / 3600 - 1e-6, (sub ? "submarine" : "surface ship") + " driven at 30 kn toward the Ross front stops at its limit (least clearance " + least.ToString("0.000") + " nm, limit " + limit + ")");
            if (!sub) Check(least - 150.0 / 1852 > 0, "surface ship: even the bow of a 300 m hull (150 m ahead of the centre) stays seaward of the front (" + (least * 1852 - 150).ToString("0") + " m to spare)");
            Check(c.WantedVelocityInKnots == 0, "held: no speed toward the front");
            ob.transform.eulerAngles = new Vector3(0, 0, 0); // turn north
            GameTime.Mission += 2;
            Postfix(c);
            Check(c.WantedVelocityInKnots == 30, "turned away: the ordered speed is given back");
        }
        Check(Api.Lines.Any(l => l.Contains("held at the ice-shelf front") && l.Contains("player unit")) && Api.Lines.Any(l => l.Contains("held at the ice-shelf stand-off")), "diagnostics name the hold");
        // far from Antarctica: never capped, and the check is skipped until a fast hull could be near
        var far = new ObjectBase { name = "far" };
        far._geoPosition = new GeoPosition { _latitude = 45, _longitude = -49 };
        var fc = new Compartments(far) { Ordered = 30 };
        int holds = IceFeaturesBattle.Holds;
        for (int t = 0; t < 100; t++) { GameTime.Mission = 10000 + t; Postfix(fc); }
        Check(fc.WantedVelocityInKnots == 30 && IceFeaturesBattle.Holds == holds, "far from any front: native speed");
        var sinking = new Compartments(new ObjectBase()) { Ordered = 30, _isSinking = true };
        Postfix(sinking);
        Check(sinking.WantedVelocityInKnots == 30, "a sinking hull is left alone");
    }

    private static void Camera(double lat, double lon)
    {
        UnityEngine.Camera.main = UnityEngine.Camera.main ?? new UnityEngine.Camera();
        Globals._currentCenterTile = new Vector2((float)lon, (float)lat);
        Utils.OriginLat = lat;
        UnityEngine.Camera.main.transform.position = new Vector3(0, 0.5f, 0);
    }

    private static void Visuals()
    {
        RossFront(out double flat, out double flon);
        var env = new SeaPower.Environment { DateTime = new DateTime(2029, 1, 20, 12, 0, 0), SeaState = 3 };
        Singleton<SeaPower.Environment>.Set(env);
        Camera(flat + 0.05, flon); // about 5.5 km north of the front
        Time.realtimeSinceStartup = 100;
        GameTime.Mission = 0;
        IceFeaturesBattle.Tick();
        Check(IceFeaturesBattle.PieceCount > 0, "cliff pieces drawn near the Ross front (" + IceFeaturesBattle.PieceCount + ")");
        foreach (var go in IceFeaturesBattle.PieceObjects())
        {
            var mesh = go.GetComponent<MeshFilter>().sharedMesh;
            var r = go.GetComponent<MeshRenderer>();
            Check(mesh.vertices.Length > 0 && mesh.triangles.Length % 3 == 0 && mesh.triangles.All(i => i >= 0 && i < mesh.vertices.Length) && mesh.normalsDone, "cliff mesh is valid");
            Check(Math.Abs(mesh.vertices.Max(v => v.y) - 30) < 1e-3 && Math.Abs(mesh.vertices.Min(v => v.y) + 190) < 1e-3, "Ross cliff: 30 m above the waterline, 190 m draft below it");
            Check(r.sharedMaterial != null && r.shadowCastingMode == UnityEngine.Rendering.ShadowCastingMode.Off, "material set, no shadow casting");
            Check(Math.Abs(go.transform.localScale.y - IceFeaturesBattle.MetersToUnity(1)) < 1e-9, "metres up through the game's 220.472656 ft per unit");
            Check(go.GetComponent<MeshFilter>() != null && go.Components.Count == 2, "no collider (visual only)");
        }

        // a battle in the Weddell outflow: bergs
        var env2 = new SeaPower.Environment { DateTime = new DateTime(2029, 1, 10, 12, 0, 0), SeaState = 2 };
        Singleton<SeaPower.Environment>.Set(env2);
        Camera(-65.0, -48.0);
        Time.realtimeSinceStartup = 200;
        GameTime.Mission = 50;
        IceFeaturesBattle.Tick();
        Check(IceFeaturesBattle.PieceCount == 0, "the new battle has no cliffs here (open sea)");
        Check(IceFeaturesBattle.BergCount > 20 && IceFeaturesBattle.DrawnCount > 0 && IceFeaturesBattle.DrawnCount <= IceFeaturesBattle.MaxDrawn, "bergs generated (" + IceFeaturesBattle.BergCount + ") and drawn (" + IceFeaturesBattle.DrawnCount + ")");
        var all = IceFeaturesBattle.Bergs().ToList();
        var py = IcebergField.Generate(all.Min(b => b.Lat0) - 1e-9, all.Max(b => b.Lat0) + 1e-9, all.Min(b => b.Lon0) - 1e-9, all.Max(b => b.Lon0) + 1e-9, env2.DateTime, "0");
        var ids = py.Select(b => b.Id).ToList();
        Check(all.All(b => ids.Contains(b.Id)), "the battle's bergs are the generator's for that date and seed (as icebergs.generate)");
        foreach (var go in IceFeaturesBattle.BergObjects())
        {
            var mesh = go.GetComponent<MeshFilter>().sharedMesh;
            Check(mesh.vertices.Length > 0 && mesh.triangles.All(i => i < mesh.vertices.Length), "berg mesh is valid");
        }
        foreach (var b in IceFeaturesBattle.DrawnBergs())
        {
            double km = IceFeatureGeo.GreatCircleNm(-65, -48, b.Lat, b.Lon) * IceFeatureGeo.KmPerNm;
            double see = Math.Max(1.0, IcebergField.VisualDetectionNm((int)b.Category, IceFeaturesBattle.BergViewKm, 15.0, b.HeightM) * IceFeatureGeo.KmPerNm);
            Check(km <= Math.Min(IceFeaturesBattle.BergViewKm, see) + 1e-6, "a berg is drawn only within its class's day visual range (" + b.CategoryName + " at " + km.ToString("0.0") + " km)");
        }
        Check(IceFeaturesBattle.BergObjects().Count() == IceFeaturesBattle.DrawnCount, "one object per drawn berg");
        Check(Api.Lines.Any(l => l.Contains("nearest berg") && l.Contains("design index, not a probability")), "diagnostics report the nearest berg's sensor numbers");

        // drift and melt over an hour of game time
        var one = all.OrderByDescending(b => b.LengthM).First();
        double lat0 = one.Lat, lon0 = one.Lon, len0 = one.LengthM;
        GameTime.Mission = 50 + 3600;
        Time.realtimeSinceStartup = 203; // bergs are stepped and placed at the 2 s layout cadence
        IceFeaturesBattle.Tick();
        double moved = IceFeatureGeo.GreatCircleNm(lat0, lon0, one.Lat, one.Lon);
        double expect = Math.Sqrt(one.U * one.U + one.V * one.V) * IceFeatureGeo.KnotsPerMs;
        Check(Math.Abs(moved - expect) < 1e-6, "drift over one hour of game time: " + moved.ToString("0.000") + " nm (current proxy, estimate)");
        Check(one.LengthM < len0, "melt at IcebergSstC=0.5 shrinks the berg");

        // battle over: everything destroyed
        int before = UnityEngine.Object.Destroyed.Count;
        int objects = IceFeaturesBattle.DrawnCount;
        Singleton<SeaPower.Environment>.Set(null);
        IceFeaturesBattle.Tick();
        Check(IceFeaturesBattle.PieceCount == 0 && IceFeaturesBattle.DrawnCount == 0 && IceFeaturesBattle.BergCount == 0 && UnityEngine.Object.Destroyed.Count >= before + 2 * objects, "battle end: objects and meshes destroyed");
    }

    // No invented inputs: an unreadable battle date gives no bergs; an unbound game clock gives
    // static bergs (no drift, no melt) instead of Unity's Time.time.
    private static void FailClosed()
    {
        IceFeaturesBattle.ResetForTests(); Api.Patches.Clear(); Api.Lines.Clear();
        IceFeaturesBattle.Install(On, Api.FindType);
        Singleton<SeaPower.Environment>.Set(new SeaPower.Environment { DateTime = new DateTime(2029, 1, 10, 12, 0, 0), BrokenDate = true });
        Camera(-65.0, -48.0);
        Time.realtimeSinceStartup = 300; GameTime.Mission = 10;
        IceFeaturesBattle.Tick();
        Check(IceFeaturesBattle.BergCount == 0 && Api.Lines.Any(l => l.Contains("could not be read: no icebergs in this battle")), "unreadable battle date: no bergs, one log line (no made-up date)");
        Singleton<SeaPower.Environment>.Set(null); IceFeaturesBattle.Tick();

        IceFeaturesBattle.ResetForTests(); Api.Patches.Clear(); Api.Lines.Clear();
        IceFeaturesBattle.Install(On, n => n == "SeaPower.GameTime" ? throw new MissingMemberException(n) : Api.FindType(n));
        Check(!IceFeaturesBattle.ClockBound && IceFeaturesBattle.VisualsOn && Api.Lines.Any(l => l.Contains("not bound") && l.Contains("will not drift or melt")), "no game clock: installed, and says the bergs are static");
        Singleton<SeaPower.Environment>.Set(new SeaPower.Environment { DateTime = new DateTime(2029, 1, 10, 12, 0, 0) });
        Time.realtimeSinceStartup = 400; GameTime.Mission = 10; Time.time = 10;
        IceFeaturesBattle.Tick();
        var b = IceFeaturesBattle.Bergs().OrderByDescending(x => x.LengthM).First();
        double lat0 = b.Lat, lon0 = b.Lon, len0 = b.LengthM;
        Time.realtimeSinceStartup = 403; GameTime.Mission = 3610; Time.time = 3610;
        IceFeaturesBattle.Tick();
        Check(b.Lat == lat0 && b.Lon == lon0 && b.LengthM == len0, "no game clock: the bergs neither drift nor melt (Unity Time.time is not used)");
        // the no-go rule still works without the clock: it samples on every call
        RossFront(out double flat, out double flon);
        var ob = new ObjectBase { name = "no-clock frigate" };
        IceFeatureGeo.Destination(flat, flon, 0, 1.0, out double la, out double lo);
        ob._geoPosition = new GeoPosition { _latitude = la, _longitude = lo };
        ob.transform.eulerAngles = new Vector3(0, 180, 0);
        var c = new Compartments(ob) { Ordered = 30 };
        for (int t = 0; t < 1800; t++) // the last nm at steerage way (a tenth of flank)
        {
            Postfix(c);
            IceFeatureGeo.Destination(ob._geoPosition._latitude, ob._geoPosition._longitude, 180, c.WantedVelocityInKnots / 3600.0, out la, out lo);
            ob._geoPosition._latitude = la; ob._geoPosition._longitude = lo;
        }
        Check(c.WantedVelocityInKnots == 0 && IceShelves.Clearance(la, lo, 20) >= ShelfSpeedState.SurfaceLimitNm - 30.0 / 3600 - 1e-6, "no game clock: the no-go rule still stops a ship at the front (" + c.WantedVelocityInKnots + " kn, clearance " + IceShelves.Clearance(la, lo, 20) + " nm)");
        Singleton<SeaPower.Environment>.Set(null); IceFeaturesBattle.Tick();
    }
}
