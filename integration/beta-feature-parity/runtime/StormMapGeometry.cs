using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Sest.RuntimeFixes;

// The Weather map layer's geometry (WorldStormsMap.cs draws it): pure C#, no
// game, Noesis or DCM types, so the managed tests run all of it under Mono.
// Everything is in geo (degrees, nm); the game's map projects geo to view
// itself (MapBase.TryLocationToView), so no battle-frame conversion is needed.

// One storm as the layer draws it at one battle time.
internal sealed class MapStorm
{
    internal string Id, Label;
    internal bool Placed, Tropical;
    internal double Lat, Lon, WindKn, GaleNm, CoreNm, ReachNm;
    internal readonly List<MapStormLead> Leads = new List<MapStormLead>();
}

// The storm's centre a whole number of hours ahead of the battle time.
internal struct MapStormLead
{
    internal double Hours, Lat, Lon, WindKn;
}

internal static class StormMapGeometry
{
    // Forecast points drawn ahead of the battle time (hours), while the storm lives.
    internal static readonly double[] LeadHours = { 1, 3, 6, 12 };
    internal const double EarthNm = 3440.065;
    internal const int RingSegments = 72;
    // Storms further than this from the battle centre, now and at every
    // forecast point, are not drawn.
    internal const double DrawWithinNm = 1500;

    internal static DateTime BattleUtc(DateTime engagementAt, double missionElapsedSeconds) =>
        DateTime.SpecifyKind(engagementAt, DateTimeKind.Utc).AddSeconds(Math.Max(0, missionElapsedSeconds));

    internal static DateTime Hour(DateTime utc) => new DateTime(utc.Ticks - utc.Ticks % TimeSpan.TicksPerHour, DateTimeKind.Utc);

    // (-180, 180]
    internal static double NormalLon(double lon)
    {
        lon %= 360;
        if (lon > 180) lon -= 360;
        if (lon <= -180) lon += 360;
        return lon;
    }

    private static double Rad(double d) => d * Math.PI / 180;
    private static double Deg(double r) => r * 180 / Math.PI;

    internal static double DistanceNm(double lat1, double lon1, double lat2, double lon2)
    {
        double p1 = Rad(lat1), p2 = Rad(lat2), dp = p2 - p1, dl = Rad(lon2 - lon1);
        double h = Math.Sin(dp / 2) * Math.Sin(dp / 2) + Math.Cos(p1) * Math.Cos(p2) * Math.Sin(dl / 2) * Math.Sin(dl / 2);
        return 2 * EarthNm * Math.Asin(Math.Min(1, Math.Sqrt(h)));
    }

    // Initial great-circle bearing, degrees true [0, 360).
    internal static double BearingDeg(double lat1, double lon1, double lat2, double lon2)
    {
        double p1 = Rad(lat1), p2 = Rad(lat2), dl = Rad(lon2 - lon1);
        double b = Deg(Math.Atan2(Math.Sin(dl) * Math.Cos(p2), Math.Cos(p1) * Math.Sin(p2) - Math.Sin(p1) * Math.Cos(p2) * Math.Cos(dl)));
        return (b + 360) % 360;
    }

    // The great-circle point distanceNm from (lat, lon) on a bearing.
    internal static void Destination(double lat, double lon, double bearingDeg, double distanceNm, out double outLat, out double outLon)
    {
        double d = distanceNm / EarthNm, b = Rad(bearingDeg), p1 = Rad(lat), l1 = Rad(lon);
        double p2 = Math.Asin(Math.Sin(p1) * Math.Cos(d) + Math.Cos(p1) * Math.Sin(d) * Math.Cos(b));
        double l2 = l1 + Math.Atan2(Math.Sin(b) * Math.Sin(d) * Math.Cos(p1), Math.Cos(d) - Math.Sin(p1) * Math.Sin(p2));
        outLat = Deg(p2);
        outLon = NormalLon(Deg(l2));
    }

    // A closed ring of RingSegments + 1 points (the last repeats the first),
    // every point radiusNm from the centre along a great circle.
    internal static List<double[]> Ring(double lat, double lon, double radiusNm, int segments = RingSegments)
    {
        var ring = new List<double[]>(segments + 1);
        for (int i = 0; i <= segments; i++)
        {
            Destination(lat, lon, 360.0 * (i % segments) / segments, radiusNm, out double a, out double b);
            ring.Add(new[] { a, b });
        }
        return ring;
    }

    // 0 below gale (34 kn), 1 gale, 2 storm (48 kn), 3 hurricane force
    // (64 kn, DCM's TyphoonKn), 4 major (96 kn, category 3 and up).
    internal static int Severity(double windKn) => windKn >= 96 ? 4 : windKn >= 64 ? 3 : windKn >= 48 ? 2 : windKn >= 34 ? 1 : 0;

    private static string N(double v) => Math.Round(v).ToString("0", CultureInfo.InvariantCulture);

    internal static string LeadText(double hours) => "+" + hours.ToString("0.#", CultureInfo.InvariantCulture) + " h";

    // "Cyclone DARYA 90 kn" (DCM's own label, as the campaign map shows it).
    internal static string CentreText(MapStorm s) => (string.IsNullOrEmpty(s.Label) ? s.Id : s.Label) + " " + N(s.WindKn) + " kn";

    // "gale 160 nm, core 24 nm" (no gale ring when under 34 kn).
    internal static string RingText(MapStorm s) =>
        (s.GaleNm > 0 ? "gale " + N(s.GaleNm) + " nm" : "below gale force") + (s.CoreNm > 0 ? ", core " + N(s.CoreNm) + " nm" : "");

    private static readonly string[] Points = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };
    internal static string Compass(double bearingDeg) => Points[(int)Math.Floor(((bearingDeg % 360 + 360) % 360 + 22.5) / 45) % 8];

    // The motion from now to the first forecast point: "moving NW 14 kn",
    // or "" without a forecast point.
    internal static string MotionText(MapStorm s)
    {
        if (s.Leads.Count == 0 || s.Leads[0].Hours <= 0) return "";
        var l = s.Leads[0];
        double d = DistanceNm(s.Lat, s.Lon, l.Lat, l.Lon);
        if (d < 0.5) return "stationary";
        return "moving " + Compass(BearingDeg(s.Lat, s.Lon, l.Lat, l.Lon)) + " " + N(d / l.Hours) + " kn";
    }

    // Worth drawing near this battle: within DrawWithinNm now or at a forecast point.
    internal static bool Near(MapStorm s, double lat, double lon)
    {
        if (DistanceNm(s.Lat, s.Lon, lat, lon) <= DrawWithinNm) return true;
        foreach (var l in s.Leads) if (DistanceNm(l.Lat, l.Lon, lat, lon) <= DrawWithinNm) return true;
        return false;
    }

    // The hover readout for a map point: the nearest storm whose reach (or
    // gale ring) holds it, or null.
    internal static string Hover(IList<MapStorm> storms, double lat, double lon)
    {
        MapStorm best = null;
        double bestD = double.MaxValue;
        foreach (var s in storms)
        {
            double d = DistanceNm(s.Lat, s.Lon, lat, lon);
            if (d <= Math.Max(s.ReachNm, s.GaleNm) && d < bestD) { best = s; bestD = d; }
        }
        if (best == null) return null;
        string where = best.CoreNm > 0 && bestD <= best.CoreNm ? "in the core" : best.GaleNm > 0 && bestD <= best.GaleNm ? "inside the gale ring" : "outside the gale ring";
        string motion = MotionText(best);
        return CentreText(best) + "\n" + N(bestD) + " nm from the centre, " + where + "\n" + RingText(best) + (motion.Length > 0 ? "\n" + motion : "");
    }

    // A view position for a geo point, false when the map cannot show it
    // (the far side of the globe).
    internal delegate bool Project(double lat, double lon, out double x, out double y);

    // Path mini-language for polylines: "M x,y L x,y ..." (invariant culture),
    // a new figure after an unprojectable point or a jump longer than
    // maxJump view units (a wrap or the globe's edge). closeEach closes a
    // figure that is the whole polyline (a ring).
    internal static void AppendPolyline(StringBuilder data, IList<double[]> points, Project project, double maxJump, bool closeEach = false)
    {
        bool open = false, broken = false;
        double px = 0, py = 0;
        int drawn = 0;
        foreach (var p in points)
        {
            if (!project(p[0], p[1], out double x, out double y) || double.IsNaN(x) || double.IsNaN(y))
            {
                open = false; broken = true;
                continue;
            }
            bool jump = open && (Math.Abs(x - px) > maxJump || Math.Abs(y - py) > maxJump);
            if (jump) broken = true;
            data.Append(open && !jump ? " L " : (data.Length > 0 ? " M " : "M "));
            data.Append(x.ToString("0.#", CultureInfo.InvariantCulture)).Append(',').Append(y.ToString("0.#", CultureInfo.InvariantCulture));
            open = true; px = x; py = y; drawn++;
        }
        if (closeEach && open && !broken && drawn > 2) data.Append(" Z");
    }

    // A small square marker of half-size h around a view point.
    internal static void AppendMarker(StringBuilder data, double x, double y, double h)
    {
        string F(double v) => v.ToString("0.#", CultureInfo.InvariantCulture);
        data.Append(data.Length > 0 ? " M " : "M ").Append(F(x - h)).Append(',').Append(F(y - h))
            .Append(" L ").Append(F(x + h)).Append(',').Append(F(y - h))
            .Append(" L ").Append(F(x + h)).Append(',').Append(F(y + h))
            .Append(" L ").Append(F(x - h)).Append(',').Append(F(y + h)).Append(" Z");
    }

    // The forecast line: the centre now, then each forecast point.
    internal static List<double[]> TrackAhead(MapStorm s)
    {
        var line = new List<double[]> { new[] { s.Lat, s.Lon } };
        foreach (var l in s.Leads) line.Add(new[] { l.Lat, l.Lon });
        return line;
    }
}
