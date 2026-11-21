using System;

namespace Sest.RuntimeFixes;

// Seasonal sea-ice concentration for a battle: a line-for-line port of the
// weather branch's mno_env/seaice.py (concentration, edge_shape, ice_at,
// NORTH_EDGE_CAP, EDGE_X15) over the per-date base edges that
// tools/make_sea_ice_data.py solved with seaice.edges_on at 12:00 UTC
// (SeaIceData.g.cs). Pure: no Unity or game types, safe on any thread.
//
// What it is: NSIDC G02135 monthly median hemispheric EXTENT (2016-2025)
// turned into a concentration field by a logistic edge whose regional shape
// seaice.py says is "fitted by eye ... not data". It is a climatology for game
// rules, not an ice chart. The rows are keyed by (leap year, month, day), not
// day of year, and are the noon value of the date (no interpolation): the
// Python edges are step functions of time (targets rounded to 0.05 Mkm2).
internal static class SeaIceModel
{
    internal const double NorthEdgeCap = 80.5;
    internal static readonly double EdgeX15 = Math.Log(98.0 / 15.0 - 1.0);
    internal const double MaxPercent = 98.0; // 98 / (1 + e^-x) never reaches 100

    internal struct Edges
    {
        internal double North, South, ShSummer;
    }

    internal static Edges EdgesOn(DateTime date)
    {
        int month = date.Month, day = date.Day;
        bool leap = DateTime.IsLeapYear(date.Year);
        int index = new DateTime(leap ? 2028 : 2029, month, day).DayOfYear - 1;
        double[] rows = leap ? SeaIceData.Leap : SeaIceData.Common;
        return new Edges { North = rows[index * 3], South = rows[index * 3 + 1], ShSummer = rows[index * 3 + 2] };
    }

    // Percent 0..98 at (lat, lon) on the calendar date of utc.
    internal static double Concentration(double lat, double lon, DateTime utc) => IceAt(lat, lon, EdgesOn(utc));

    internal static double IceAt(double lat, double lon, Edges e)
    {
        if (double.IsNaN(lat) || double.IsNaN(lon)) return 0.0;
        if (Math.Abs(lat) < 40) return 0.0;
        bool south = lat < 0;
        return Math.Min(100.0, Concentration(south, lat, lon, south ? e.South : e.North, south ? e.ShSummer : 0.0));
    }

    internal static double Concentration(bool south, double lat, double lon, double baseEdge, double shSummer)
    {
        double edge = baseEdge - EdgeShape(south, lon, shSummer, lat);
        if (!south) edge = Math.Min(edge, NorthEdgeCap);
        if (south != (lat < 0)) return 0.0;
        double x = (Math.Abs(lat) - edge) * 1.0 - EdgeX15;
        return 98.0 / (1.0 + Math.Exp(-Math.Max(-35.0, Math.Min(35.0, x))));
    }

    // Python's float modulo: the result takes the sign of the divisor.
    internal static double PyMod(double a, double b)
    {
        double m = a % b;
        if (m != 0 && ((b < 0) != (m < 0))) m += b;
        return m;
    }

    // geo.wrap_lon: [-180, 180)
    internal static double WrapLon(double lon) => PyMod(lon + 180.0, 360.0) - 180.0;

    // geo.lon_delta(a, b) = wrap_lon(a - b)
    internal static double LonDelta(double a, double b) => WrapLon(a - b);

    private static double G(double lon, double centre, double width)
    {
        double d = LonDelta(lon, centre) / width;
        return Math.Exp(-(d * d));
    }

    private static double Below(double lat, double a, double b)
    {
        double t = Math.Max(0.0, Math.Min(1.0, (lat - a) / (b - a)));
        return 1.0 - t * t * (3 - 2 * t);
    }

    internal static double EdgeShape(bool south, double lon, double shSummer, double lat)
    {
        const double rad = Math.PI / 180;
        if (south)
        {
            double winter = 4.0 * G(lon, -40, 28)
                + 2.5 * G(lon, -175, 25)
                - 1.5 * G(lon, -100, 25)
                + 0.8 * Math.Cos((lon - 5) * rad * 2);
            double summer = 6.0 * G(lon, -55, 15)
                + 4.0 * G(lon, -95, 28)
                - 3.0 * G(lon, -178, 15);
            return (1.0 - shSummer) * winter + shSummer * summer;
        }
        return -9.0 * G(lon, 8, 24)
            - 3.0 * G(lon, 38, 14)
            + 13.0 * G(lon, 22, 5) * Below(lat, 66.5, 68.0)
            + 21.0 * G(lon, 147, 9) * Below(lat, 61.0, 64.0)
            + 5.0 * G(lon, -175, 14) * Below(lat, 64.0, 67.0)
            + 12.0 * G(lon, -85, 12) * Below(lat, 65.0, 68.0)
            + 19.0 * G(lon, -63, 5) * Below(lat, 52.0, 56.0)
            + 3.0 * G(lon, -58, 14)
            + 2.5 * G(lon, -25, 4)
            + 12.5 * G(lon, 28, 4) * Below(lat, 61.5, 63.5)
            + 12.0 * G(lon, 38, 5) * Below(lat, 67.5, 68.5)
            + 31.5 * G(lon, 120.5, 3) * Below(lat, 42.0, 44.0)
            + 6.0 * G(lon, -108, 26) * (1.0 - Below(lat, 66.0, 70.0));
    }
}
