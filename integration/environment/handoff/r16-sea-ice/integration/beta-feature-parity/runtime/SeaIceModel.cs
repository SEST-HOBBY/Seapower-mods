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
//
// Marginal seas (weather branch B1, docs/environment/SEA-ICE-MARGINAL-SEAS.md):
// inside the Sea of Okhotsk (with the Sea of Japan / Tatar Strait), the
// Bering Sea and the Chukchi Sea, seaice.ice_at uses a regional logistic in an "ice order" field
// (seaice.ice_order, ported below as IceOrder) over a per-date regional edge
// solved against NSIDC G02135 regional monthly extent (SeaIceData.CommonMarginal
// / LeapMarginal). Everywhere else the hemispheric model is unchanged.
internal static class SeaIceModel
{
    internal const double NorthEdgeCap = 80.5;
    internal static readonly double EdgeX15 = Math.Log(98.0 / 15.0 - 1.0);
    internal const double MaxPercent = 98.0; // 98 / (1 + e^-x) never reaches 100

    internal struct Edges
    {
        internal double North, South, ShSummer;
        internal double Okhotsk, Bering, Chukchi; // regional edges (SeaIceData.MarginalNoIce = ice-free)
    }

    internal static Edges EdgesOn(DateTime date)
    {
        int month = date.Month, day = date.Day;
        bool leap = DateTime.IsLeapYear(date.Year);
        int index = new DateTime(leap ? 2028 : 2029, month, day).DayOfYear - 1;
        double[] rows = leap ? SeaIceData.Leap : SeaIceData.Common;
        double[] marginal = leap ? SeaIceData.LeapMarginal : SeaIceData.CommonMarginal;
        return new Edges
        {
            North = rows[index * 3], South = rows[index * 3 + 1], ShSummer = rows[index * 3 + 2],
            Okhotsk = marginal[index * 3], Bering = marginal[index * 3 + 1], Chukchi = marginal[index * 3 + 2],
        };
    }

    // Percent 0..98 at (lat, lon) on the calendar date of utc.
    internal static double Concentration(double lat, double lon, DateTime utc) => IceAt(lat, lon, EdgesOn(utc));

    internal static double IceAt(double lat, double lon, Edges e)
    {
        if (double.IsNaN(lat) || double.IsNaN(lon)) return 0.0;
        if (Math.Abs(lat) < 40) return 0.0;
        bool south = lat < 0;
        if (!south)
        {
            int sea = MarginalSea(lat, lon);
            if (sea >= 0) return Math.Min(100.0, MarginalConcentration(sea, lat, lon, sea == SeaOkhotsk ? e.Okhotsk : sea == SeaBering ? e.Bering : e.Chukchi));
        }
        return Math.Min(100.0, Concentration(south, lat, lon, south ? e.South : e.North, south ? e.ShSummer : 0.0));
    }

    internal const int SeaOkhotsk = 0, SeaBering = 1, SeaChukchi = 2;
    private static readonly double MarginalX15 = Math.Log(SeaIceData.MarginalMax / 15.0 - 1.0);

    // seaice.marginal_sea: index of the regionally calibrated sea at this point, or -1.
    internal static int MarginalSea(double lat, double lon)
    {
        if (!(lat >= 40.0 && lat < 80.0)) return -1;
        int j = (int)Math.Floor(lat);
        int i = (int)Math.Floor(LonDelta(lon, 0.0));
        if (InRows(SeaIceData.MarginalRowsOkhotsk, j, i)) return SeaOkhotsk;
        if (InRows(SeaIceData.MarginalRowsBering, j, i)) return SeaBering;
        if (InRows(SeaIceData.MarginalRowsChukchi, j, i)) return SeaChukchi;
        return -1;
    }

    private static bool InRows(int[] rows, int j, int i)
    {
        for (int k = 0; k + 2 < rows.Length; k += 3)
            if (rows[k] == j && rows[k + 1] <= i && i <= rows[k + 2]) return true;
        return false;
    }

    // seaice.ice_order (hand port; procedural shape, not data: see seaice.py).
    internal static double IceOrder(int sea, double lat, double lon)
    {
        if (sea == SeaOkhotsk)
        {
            if (lat < 52.0 && lon < (lat >= 46.0 ? 142.0 : 141.5)) // Sea of Japan and Tatar Strait
                return lat + 4.0 - 3.0 * Math.Max(0.0, 48.5 - lat);
            double s = lat - 0.35 * (lon - 140.0);
            double a = (lat - 54.5) / 0.8, b = (lon - 139.7) / 2.5;
            s += 3.0 * Math.Exp(-(a * a) - b * b); // Shantar Islands, Sakhalin Gulf
            double c = (lat - 61.5) / 1.0, d = (lon - 162.5) / 2.0;
            s += 4.0 * Math.Exp(-(c * c) - d * d); // Shelikhov Gulf
            double u = Math.Max(0.0, Math.Min(1.0, (lat - 56.5) / 1.5)), w = (lon - 143.0) / 8.0;
            s -= 2.5 * u * u * (3.0 - 2.0 * u) * Math.Exp(-(w * w)); // north coast clears early
            if (lat >= 44.0 && lat <= 54.5) // East Sakhalin Current ice tongue
            {
                double t = (lon - 143.6) / 2.5;
                s = Math.Max(s, 52.9 + 0.3 * (lat - 44.5) - t * t);
            }
            return s;
        }
        if (sea == SeaChukchi) return lat - 0.05 * (LonDelta(lon, 0.0) + 160.0);
        double east = LonDelta(lon, 180.0); // negative west of 180
        return lat + 0.235 * Math.Max(0.0, east) + 0.12 * Math.Max(0.0, -east);
    }

    // seaice.marginal_concentration: exactly 15 % where IceOrder == sEdge.
    internal static double MarginalConcentration(int sea, double lat, double lon, double sEdge)
    {
        if (sEdge >= SeaIceData.MarginalNoIce) return 0.0;
        double x = (IceOrder(sea, lat, lon) - sEdge) / SeaIceData.MarginalWidth - MarginalX15;
        return SeaIceData.MarginalMax / (1.0 + Math.Exp(-Math.Max(-35.0, Math.Min(35.0, x))));
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
