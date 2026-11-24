using System;
using System.Collections.Generic;

namespace Sest.RuntimeFixes
{
    // Pure rules of the ice-features drop-in (IceShelves=1 in [Runtime], default OFF):
    // Antarctic ice-shelf containment, distance to the shelf front, the navigation rule of
    // mno_env/iceshelves.py, and a speed cap that keeps ships and submarines out of the no-go
    // zone. No Unity or game types: IceFeaturesTests.exe runs all of it under Mono.
    //
    // Data: IceFeaturesData.g.cs, made by integration/environment/tools/make_ice_features_data.py.
    // - Shelf outlines: Natural Earth 1:10m Antarctic ice shelves (public domain), simplified
    //   (Douglas-Peucker, IceFeaturesData.ShelfToleranceKm = 0.5 km). Containment therefore
    //   differs from the full outline only within 0.5 km of its edge (the golden test checks it).
    // - Fronts: Natural Earth 1:10m ice-shelf edge lines, NOT simplified, so the front distance
    //   equals mno_env.iceshelves.distance_to_front_nm.
    // - The fronts are a fixed past position, about 2003-2012 (estimate). Later calvings are not
    //   shown (docs/environment/ICE-SHELVES.md lists them).

    internal static class IceFeatureGeo
    {
        internal const double EarthRadiusNm = 3440.065;   // mno_env/geo.py
        internal const double KnotsPerMs = 1.943844;       // mno_env/ice.py MS_TO_KNOTS
        internal const double KmPerNm = 1.852;
        private const double DegToRad = Math.PI / 180.0;  // CPython math.radians
        private const double RadToDeg = 180.0 / Math.PI;  // CPython math.degrees

        internal static double Radians(double d) => d * DegToRad;
        internal static double Degrees(double r) => r * RadToDeg;

        // Python's float modulo (the sign follows the divisor).
        internal static double PyMod(double a, double b)
        {
            double m = a % b;
            if (m != 0) { if ((b < 0) != (m < 0)) m += b; }
            else m = b < 0 ? -0.0 : 0.0;
            return m;
        }

        // geo.wrap_lon: [-180, 180)
        internal static double WrapLon(double lon) => PyMod(lon + 180.0, 360.0) - 180.0;
        internal static double LonDelta(double a, double b) => WrapLon(a - b);

        // geo.great_circle_nm (haversine)
        internal static double GreatCircleNm(double lat1d, double lon1d, double lat2d, double lon2d)
        {
            double lat1 = Radians(lat1d), lon1 = Radians(lon1d), lat2 = Radians(lat2d), lon2 = Radians(lon2d);
            double s1 = Math.Sin((lat2 - lat1) / 2), s2 = Math.Sin((lon2 - lon1) / 2);
            double h = s1 * s1 + Math.Cos(lat1) * Math.Cos(lat2) * s2 * s2;
            return 2 * EarthRadiusNm * Math.Asin(Math.Sqrt(Math.Min(1.0, Math.Max(0.0, h))));
        }

        // geo.destination: the point dist_nm along an initial true bearing.
        internal static void Destination(double latd, double lond, double bearingDeg, double distNm, out double lat, out double lon)
        {
            double lat1 = Radians(latd), lon1 = Radians(lond), brg = Radians(bearingDeg);
            double d = distNm / EarthRadiusNm;
            double lat2 = Math.Asin(Math.Sin(lat1) * Math.Cos(d) + Math.Cos(lat1) * Math.Sin(d) * Math.Cos(brg));
            double lon2 = lon1 + Math.Atan2(Math.Sin(brg) * Math.Sin(d) * Math.Cos(lat1), Math.Cos(d) - Math.Sin(lat1) * Math.Sin(lat2));
            lat = Degrees(lat2);
            lon = WrapLon(Degrees(lon2));
        }

        // geo.displace: move east/north by nautical miles along the great circle of that bearing.
        internal static void Displace(double latd, double lond, double eastNm, double northNm, out double lat, out double lon)
        {
            double dist = Math.Sqrt(eastNm * eastNm + northNm * northNm);
            if (dist == 0) { lat = latd; lon = lond; return; }
            Destination(latd, lond, PyMod(Degrees(Math.Atan2(eastNm, northNm)), 360.0), dist, out lat, out lon);
        }

        // geo._ring_contains over an integer [lon, lat] ring (pts[2k], pts[2k+1]) / scale, points
        // first..end-1 (closed rings repeat the first point, as the JSON does).
        internal static bool RingContains(int[] pts, int first, int end, double scale, double lat, double lon)
        {
            bool inside = false;
            int n = end - first;
            for (int i = 0; i < n; i++)
            {
                int a = first + i, b = first + (i + 1) % n;
                double x1 = pts[2 * a] / scale, y1 = pts[2 * a + 1] / scale, x2 = pts[2 * b] / scale, y2 = pts[2 * b + 1] / scale;
                if (Math.Abs(x2 - x1) > 180) continue; // an edge that wraps the seam is not part of a lon/lat ring
                if ((y1 > lat) != (y2 > lat))
                {
                    double xi = x1 + (lat - y1) * (x2 - x1) / (y2 - y1);
                    if (xi > lon) inside = !inside;
                }
            }
            return inside;
        }

        internal static void Vec(double latd, double lond, out double x, out double y, out double z)
        {
            double la = Radians(latd), lo = Radians(lond);
            x = Math.Cos(la) * Math.Cos(lo); y = Math.Cos(la) * Math.Sin(lo); z = Math.Sin(la);
        }
    }

    internal enum ShelfStatus { Open = 0, Caution = 1, Blocked = 2 }

    // The shelf polygons and front lines, indexed once (thread-safe after Load).
    internal static class IceShelves
    {
        private const double Milli = 1000.0;
        private static readonly object gate = new object();
        private static volatile bool loaded;
        private static double[] bbox;        // per shelf: lon min, lon max, lat min, lat max (outer rings)
        internal static double MinLat = 90, MaxLat = -90; // all shelves
        // front segments: A, B, N (unit vectors; N NaN when degenerate), feature, end points (lat, lon)
        private static double[] segA, segB, segN, segEnds;
        private static int[] segFeature, lineFirstSeg, lineSegEnd;
        private static double[] lineCentre, lineRadius; // per front line: centre unit vector and angular radius (rad)
        private static sbyte[] segSide;                // +1 shelf left of A->B, -1 right (FrontSide; 0 filled from the line's majority)
        internal static int Segments => segFeature == null ? 0 : segFeature.Length;
        internal static int Lines => IceFeaturesData.FrontFeature.Length;

        internal static void Load()
        {
            if (loaded) return;
            lock (gate)
            {
                if (loaded) return;
                var d = IceFeaturesData.ShelfPts;
                int shelves = IceFeaturesData.ShelfFeature.Length;
                if (IceFeaturesData.ShelfName.Length != shelves || IceFeaturesData.ShelfPoly.Length != shelves + 1 || IceFeaturesData.ShelfFreeboardM.Length != shelves)
                    throw new InvalidOperationException("ice features: shelf table lengths differ");
                var b = new double[shelves * 4];
                double minLat = 90, maxLat = -90;
                for (int s = 0; s < shelves; s++)
                {
                    double x0 = double.MaxValue, x1 = double.MinValue, y0 = double.MaxValue, y1 = double.MinValue;
                    for (int p = IceFeaturesData.ShelfPoly[s]; p < IceFeaturesData.ShelfPoly[s + 1]; p++)
                    {
                        int r = IceFeaturesData.PolyRing[p]; // outer ring only, as ice.load_shelves
                        for (int k = IceFeaturesData.RingStart[r]; k < IceFeaturesData.RingStart[r + 1]; k++)
                        {
                            double x = d[2 * k] / Milli, y = d[2 * k + 1] / Milli;
                            x0 = Math.Min(x0, x); x1 = Math.Max(x1, x); y0 = Math.Min(y0, y); y1 = Math.Max(y1, y);
                        }
                    }
                    b[4 * s] = x0; b[4 * s + 1] = x1; b[4 * s + 2] = y0; b[4 * s + 3] = y1;
                    minLat = Math.Min(minLat, y0); maxLat = Math.Max(maxLat, y1);
                }
                var fa = new List<double>(); var fb = new List<double>(); var fn = new List<double>(); var fe = new List<double>();
                var ff = new List<int>();
                int lines = IceFeaturesData.FrontFeature.Length;
                var first = new int[lines]; var end = new int[lines]; var centre = new double[lines * 3]; var radius = new double[lines];
                var fp = IceFeaturesData.FrontPts;
                for (int l = 0; l < lines; l++)
                {
                    first[l] = ff.Count;
                    int s0 = IceFeaturesData.FrontStart[l], s1 = IceFeaturesData.FrontStart[l + 1];
                    double cx = 0, cy = 0, cz = 0;
                    for (int k = s0; k < s1; k++)
                    {
                        IceFeatureGeo.Vec(fp[2 * k + 1] / Milli, fp[2 * k] / Milli, out double x, out double y, out double z);
                        cx += x; cy += y; cz += z;
                    }
                    double cm = Math.Sqrt(cx * cx + cy * cy + cz * cz);
                    cx /= cm; cy /= cm; cz /= cm;
                    double rad = 0;
                    for (int k = s0; k + 1 < s1; k++)
                    {
                        double la = fp[2 * k + 1] / Milli, lo = fp[2 * k] / Milli, lb = fp[2 * k + 3] / Milli, lob = fp[2 * k + 2] / Milli;
                        IceFeatureGeo.Vec(la, lo, out double ax, out double ay, out double az);
                        IceFeatureGeo.Vec(lb, lob, out double bx, out double by, out double bz);
                        double nx = ay * bz - az * by, ny = az * bx - ax * bz, nz = ax * by - ay * bx;
                        double m = Math.Sqrt(nx * nx + ny * ny + nz * nz);
                        fa.Add(ax); fa.Add(ay); fa.Add(az); fb.Add(bx); fb.Add(by); fb.Add(bz);
                        if (m > 1e-15) { fn.Add(nx / m); fn.Add(ny / m); fn.Add(nz / m); } else { fn.Add(double.NaN); fn.Add(double.NaN); fn.Add(double.NaN); }
                        fe.Add(la); fe.Add(lo); fe.Add(lb); fe.Add(lob);
                        ff.Add(IceFeaturesData.FrontFeature[l]);
                        rad = Math.Max(rad, Math.Acos(Math.Max(-1.0, Math.Min(1.0, ax * cx + ay * cy + az * cz))));
                        rad = Math.Max(rad, Math.Acos(Math.Max(-1.0, Math.Min(1.0, bx * cx + by * cy + bz * cz))));
                    }
                    end[l] = ff.Count;
                    centre[3 * l] = cx; centre[3 * l + 1] = cy; centre[3 * l + 2] = cz;
                    radius[l] = rad;
                }
                if (IceFeaturesData.FrontSide.Length != ff.Count) throw new InvalidOperationException("ice features: front side table length differs");
                var side = (sbyte[])IceFeaturesData.FrontSide.Clone();
                for (int l = 0; l < lines; l++)
                {
                    int sum = 0;
                    for (int i = first[l]; i < end[l]; i++) sum += side[i];
                    for (int i = first[l]; i < end[l]; i++) if (side[i] == 0) side[i] = (sbyte)Math.Sign(sum);
                }
                segSide = side;
                bbox = b; MinLat = minLat; MaxLat = maxLat;
                segA = fa.ToArray(); segB = fb.ToArray(); segN = fn.ToArray(); segEnds = fe.ToArray(); segFeature = ff.ToArray();
                lineFirstSeg = first; lineSegEnd = end; lineCentre = centre; lineRadius = radius;
                loaded = true;
            }
        }

        // ice.IceShelf.contains for shelf s (load order).
        internal static bool Contains(int s, double lat, double lon)
        {
            Load();
            lon = IceFeatureGeo.WrapLon(lon);
            if (!(bbox[4 * s + 2] <= lat && lat <= bbox[4 * s + 3] && bbox[4 * s] <= lon && lon <= bbox[4 * s + 1])) return false;
            var d = IceFeaturesData.ShelfPts;
            for (int p = IceFeaturesData.ShelfPoly[s]; p < IceFeaturesData.ShelfPoly[s + 1]; p++)
            {
                int r0 = IceFeaturesData.PolyRing[p], r1 = IceFeaturesData.PolyRing[p + 1];
                if (!IceFeatureGeo.RingContains(d, IceFeaturesData.RingStart[r0], IceFeaturesData.RingStart[r0 + 1], Milli, lat, lon)) continue;
                bool inHole = false;
                for (int h = r0 + 1; h < r1 && !inHole; h++)
                    inHole = IceFeatureGeo.RingContains(d, IceFeaturesData.RingStart[h], IceFeaturesData.RingStart[h + 1], Milli, lat, lon);
                if (!inHole) return true;
            }
            return false;
        }

        // The first shelf (load order) containing the point, or -1 (open water, land, an ice rise).
        internal static int ShelfAt(double lat, double lon)
        {
            Load();
            if (lat < MinLat || lat > MaxLat) return -1;
            int n = IceFeaturesData.ShelfFeature.Length;
            for (int s = 0; s < n; s++) if (Contains(s, lat, lon)) return s;
            return -1;
        }

        internal static string Name(int s) => s < 0 ? "" : (IceFeaturesData.ShelfLabel[s].Length > 0 ? IceFeaturesData.ShelfLabel[s] : IceFeaturesData.ShelfName[s]);

        internal static int ShelfOfFeature(int feature)
        {
            int n = IceFeaturesData.ShelfFeature.Length;
            for (int s = 0; s < n; s++) if (IceFeaturesData.ShelfFeature[s] == feature) return s;
            return -1;
        }

        // iceshelves._seg_angle
        private static double SegAngle(double px, double py, double pz, int i) => SegAngle(px, py, pz, i, out _);

        private static double SegAngle(double px, double py, double pz, int i, out bool footInside)
        {
            footInside = false;
            double ax = segA[3 * i], ay = segA[3 * i + 1], az = segA[3 * i + 2];
            double bx = segB[3 * i], by = segB[3 * i + 1], bz = segB[3 * i + 2];
            double nx = segN[3 * i], ny = segN[3 * i + 1], nz = segN[3 * i + 2];
            if (!double.IsNaN(nx))
            {
                // cross(A, P) . N >= 0 and cross(P, B) . N >= 0
                double c1x = ay * pz - az * py, c1y = az * px - ax * pz, c1z = ax * py - ay * px;
                double c2x = py * bz - pz * by, c2y = pz * bx - px * bz, c2z = px * by - py * bx;
                footInside = c1x * nx + c1y * ny + c1z * nz >= 0 && c2x * nx + c2y * ny + c2z * nz >= 0;
                if (footInside) return Math.Abs(Math.Asin(Math.Max(-1.0, Math.Min(1.0, px * nx + py * ny + pz * nz))));
            }
            return Math.Min(Math.Acos(Math.Max(-1.0, Math.Min(1.0, px * ax + py * ay + pz * az))), Math.Acos(Math.Max(-1.0, Math.Min(1.0, px * bx + py * by + pz * bz))));
        }

        // iceshelves.nearest_front: great-circle distance (nm) to the nearest front segment and its
        // feature. With withinNm, front lines whose cap lies farther are skipped and the result is
        // +Infinity when nothing is that close (a cheap test far from Antarctica).
        internal static double DistanceToFrontNm(double lat, double lon, out int feature, double withinNm = double.PositiveInfinity) =>
            DistanceToFrontNm(lat, lon, out feature, out _, withinNm);

        internal static double DistanceToFrontNm(double lat, double lon, out int feature, out int segment, double withinNm)
        {
            Load();
            segment = -1;
            IceFeatureGeo.Vec(lat, lon, out double px, out double py, out double pz);
            double limit = double.IsInfinity(withinNm) ? double.PositiveInfinity : withinNm / IceFeatureGeo.EarthRadiusNm;
            double best = double.PositiveInfinity;
            feature = -1;
            int lines = lineFirstSeg.Length;
            for (int l = 0; l < lines; l++)
            {
                // lower bound of the angle to any point of this line: centre distance minus the cap radius
                double c = Math.Acos(Math.Max(-1.0, Math.Min(1.0, px * lineCentre[3 * l] + py * lineCentre[3 * l + 1] + pz * lineCentre[3 * l + 2])));
                if (c - lineRadius[l] > Math.Min(limit, best) + 1e-9) continue;
                for (int i = lineFirstSeg[l]; i < lineSegEnd[l]; i++)
                {
                    double a = SegAngle(px, py, pz, i);
                    if (a < best) { best = a; feature = segFeature[i]; segment = i; }
                }
            }
            if (best > limit) { feature = -1; segment = -1; return double.PositiveInfinity; }
            return best * IceFeatureGeo.EarthRadiusNm;
        }

        internal static double DistanceToFrontNm(double lat, double lon) => DistanceToFrontNm(lat, lon, out _);

        // Front segments with any end point within radiusKm of (lat, lon): index list for drawing.
        internal static List<int> SegmentsNear(double lat, double lon, double radiusKm)
        {
            Load();
            var o = new List<int>();
            double nm = radiusKm / IceFeatureGeo.KmPerNm;
            IceFeatureGeo.Vec(lat, lon, out double px, out double py, out double pz);
            double limit = nm / IceFeatureGeo.EarthRadiusNm;
            for (int l = 0; l < lineFirstSeg.Length; l++)
            {
                double c = Math.Acos(Math.Max(-1.0, Math.Min(1.0, px * lineCentre[3 * l] + py * lineCentre[3 * l + 1] + pz * lineCentre[3 * l + 2])));
                if (c - lineRadius[l] > limit) continue;
                for (int i = lineFirstSeg[l]; i < lineSegEnd[l]; i++)
                    if (SegAngle(px, py, pz, i) <= limit) o.Add(i);
            }
            return o;
        }

        internal static void Segment(int i, out double latA, out double lonA, out double latB, out double lonB, out int feature)
        {
            latA = segEnds[4 * i]; lonA = segEnds[4 * i + 1]; latB = segEnds[4 * i + 2]; lonB = segEnds[4 * i + 3]; feature = segFeature[i];
        }

        // +1 when the shelf lies left of the segment's direction, -1 right, 0 unknown.
        internal static int SideOf(int segment) { Load(); return segSide[segment]; }

        // Typical front freeboard and draft (m) of a front feature: iceshelves.front_cliff's
        // 'typical' (the shelf's own value, else the generic front, an estimate).
        internal static void Cliff(int feature, out double freeboardM, out double draftM)
        {
            int s = ShelfOfFeature(feature);
            freeboardM = s >= 0 ? IceFeaturesData.ShelfFreeboardM[s] : IceFeaturesData.GenericFreeboardM;
            draftM = s >= 0 ? IceFeaturesData.ShelfDraftM[s] : IceFeaturesData.GenericDraftM;
        }

        // iceshelves.shelf_navigation (on the simplified outline): a surface ship is blocked inside a
        // shelf and gets a caution within SurfaceCautionNm of a front; a submarine is blocked inside
        // and within SubmarineStandoffNm. Both distances are estimates (ice-shelf-attributes.json).
        internal static ShelfStatus Navigation(double lat, double lon, bool submarine, double standoffNm, double cautionNm, out double distanceNm)
        {
            int s = ShelfAt(lat, lon);
            distanceNm = DistanceToFrontNm(lat, lon);
            if (s >= 0) return ShelfStatus.Blocked;
            if (submarine) return distanceNm < standoffNm ? ShelfStatus.Blocked : ShelfStatus.Open;
            return distanceNm < cautionNm ? ShelfStatus.Caution : ShelfStatus.Open;
        }

        internal static ShelfStatus Navigation(double lat, double lon, bool submarine, out double distanceNm) =>
            Navigation(lat, lon, submarine, IceFeaturesData.SubmarineStandoffNm, IceFeaturesData.SurfaceCautionNm, out distanceNm);

        // Within this distance of a front the inside/outside test of the speed rule uses the side
        // of the nearest front segment (FrontSide, from the FULL outline) instead of the simplified
        // polygon, whose edge may sit up to 0.5 km off the front line. Choice: twice the tolerance.
        internal const double SideNearNm = 0.54;

        // Inside a shelf, for the speed rule: the side of the nearest front segment near a front
        // (when the point lies abreast of that segment, not beyond an end of the front line), the
        // simplified polygon elsewhere.
        internal static bool InsideForRule(double lat, double lon, int segment, double distanceNm)
        {
            if (segment >= 0 && distanceNm <= SideNearNm && segSide[segment] != 0 && !double.IsNaN(segN[3 * segment]))
            {
                IceFeatureGeo.Vec(lat, lon, out double px, out double py, out double pz);
                SegAngle(px, py, pz, segment, out bool abreast);
                if (!abreast) return ShelfAt(lat, lon) >= 0;
                double dot = px * segN[3 * segment] + py * segN[3 * segment + 1] + pz * segN[3 * segment + 2];
                return segSide[segment] > 0 ? dot > 0 : dot < 0;
            }
            return ShelfAt(lat, lon) >= 0;
        }

        // Signed clearance (nm) for the speed rule: the front distance outside a shelf, minus it
        // inside one. Capped at capNm (returned when no front is that close and the point is not
        // inside a shelf), so a query far from Antarctica costs a few cap tests.
        internal static double Clearance(double lat, double lon, double capNm)
        {
            Load();
            if (lat > MaxLat + 1.0 + capNm / 60.0) return capNm;
            double d = DistanceToFrontNm(lat, lon, out _, out int seg, capNm);
            if (double.IsInfinity(d)) return ShelfAt(lat, lon) >= 0 ? -DistanceToFrontNm(lat, lon) : capNm;
            return InsideForRule(lat, lon, seg, d) ? -d : Math.Min(d, capNm);
        }
    }

    // The no-go rule as a speed cap, for one hull. Like SeaIceRules' IceSpeedState it only lowers
    // the speed the native command asked for, and it never traps a hull: a move that keeps or gains
    // clearance is never capped. DESIGN values (not data): the samples, the steerage factor and
    // the margin below.
    internal sealed class ShelfSpeedState
    {
        // Direction-of-travel samples, nm (the nearest catches a slow approach, the farthest a fast one).
        internal static readonly double[] AheadNm = { 0.25, 0.5, 1.0 };
        internal const double MinWayFactor = 0.1;    // steerage way while still outside the limit
        internal const double EpsilonNm = 0.005;     // ~9 m: "the same clearance" (moving along the front)
        // Surface ships stop with their reference point (the hull centre) this far seaward of the
        // front, so the bow does not sit inside the drawn cliff: half of a 100-300 m hull (50-150 m)
        // plus a margin. ESTIMATE (design constant); no hull-length member has been bound.
        internal const double SurfaceLimitNm = 0.1;  // 185 m
        internal bool Capped, Stopped;
        internal double LastHere = double.NaN, LastAhead = double.NaN;

        // wanted: knots from the native command (negative astern); flank: the hull's top speed;
        // here: signed clearance at the hull; ahead: the least signed clearance of the samples along
        // the direction of travel (astern when backing); limitNm: 0 for a surface ship, the
        // stand-off for a submarine, SurfaceLimitNm for a surface ship.
        internal float Cap(float wanted, float flank, double here, double ahead, double limitNm)
        {
            Capped = Stopped = false;
            LastHere = here; LastAhead = ahead;
            if (float.IsNaN(wanted) || Math.Abs(wanted) < 0.01f || !(flank > 0) || double.IsNaN(here) || double.IsNaN(ahead)) return wanted;
            bool breach = ahead < limitNm;
            bool closing = ahead < here - EpsilonNm;
            if (!breach || !closing) return wanted;
            Capped = true;
            float cap;
            if (here > limitNm) cap = (float)(MinWayFactor * flank);
            else { cap = 0f; Stopped = true; }
            if (Math.Abs(wanted) <= cap) { Capped = false; return wanted; }
            return wanted < 0 ? -cap : cap;
        }
    }

    // Low-poly mesh arrays shared by the cliff and berg meshers: x east, y up, z north, metres.
    // Every face is a flat quad or triangle with its own vertices (flat shading), wound so that
    // cross(b - a, c - a) points out of the solid (Unity's front face; Unity's own docs quad).
    internal sealed class IceMeshData
    {
        internal readonly List<float> V = new List<float>();
        internal readonly List<int> T = new List<int>();
        internal int Vertices => V.Count / 3;
        internal int Triangles => T.Count / 3;

        private int Add(double x, double y, double z) { V.Add((float)x); V.Add((float)y); V.Add((float)z); return V.Count / 3 - 1; }

        // a triangle facing (nx, ny, nz): reversed when its winding faces the other way
        internal void Tri(double[] a, double[] b, double[] c, double nx, double ny, double nz)
        {
            double ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2], vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2];
            double cx = uy * vz - uz * vy, cy = uz * vx - ux * vz, cz = ux * vy - uy * vx;
            if (cx * cx + cy * cy + cz * cz < 1e-12) return; // degenerate
            int i = Add(a[0], a[1], a[2]), j = Add(b[0], b[1], b[2]), k = Add(c[0], c[1], c[2]);
            if (cx * nx + cy * ny + cz * nz >= 0) { T.Add(i); T.Add(j); T.Add(k); }
            else { T.Add(i); T.Add(k); T.Add(j); }
        }

        internal void Quad(double[] a, double[] b, double[] c, double[] d, double nx, double ny, double nz)
        {
            Tri(a, b, c, nx, ny, nz);
            Tri(a, c, d, nx, ny, nz);
        }

        internal static double[] P(double x, double y, double z) => new[] { x, y, z };
    }

    // The ice cliff along a run of front segments: the seaward face from the draft below the
    // waterline up to the freeboard, a flat top strip topWidthM inland (snow surface, visual only),
    // the underside strip at the draft (seen from a periscope or an underwater camera) and the
    // inland end wall. Freeboard and draft are the shelf's typical front values (IceShelves.Cliff).
    internal static class CliffMesher
    {
        // Default inland width of the drawn top, m: visual only (the shelf beyond is not drawn).
        internal const double DefaultTopWidthM = 1500;

        // east/north: the run's points in metres (local plane); side: +1 when the shelf is left of
        // the direction of the points, -1 when right.
        internal static IceMeshData Build(double[] east, double[] north, int side, double freeboardM, double draftM, double topWidthM)
        {
            var m = new IceMeshData();
            int n = east.Length;
            for (int i = 0; i + 1 < n; i++)
            {
                double ax = east[i], az = north[i], bx = east[i + 1], bz = north[i + 1];
                double dx = bx - ax, dz = bz - az, len = Math.Sqrt(dx * dx + dz * dz);
                if (len < 0.5) continue;
                // inland unit normal: left of (dx, dz) is (-dz, dx)
                double ix = -dz / len * side, iz = dx / len * side;
                var aTop = IceMeshData.P(ax, freeboardM, az); var bTop = IceMeshData.P(bx, freeboardM, bz);
                var aBot = IceMeshData.P(ax, -draftM, az); var bBot = IceMeshData.P(bx, -draftM, bz);
                double w = topWidthM;
                var aIn = IceMeshData.P(ax + ix * w, freeboardM, az + iz * w); var bIn = IceMeshData.P(bx + ix * w, freeboardM, bz + iz * w);
                var aInB = IceMeshData.P(ax + ix * w, -draftM, az + iz * w); var bInB = IceMeshData.P(bx + ix * w, -draftM, bz + iz * w);
                m.Quad(aTop, bTop, bBot, aBot, -ix, 0, -iz);     // seaward face
                m.Quad(aTop, bTop, bIn, aIn, 0, 1, 0);           // top
                m.Quad(aBot, bBot, bInB, aInB, 0, -1, 0);        // underside
                m.Quad(aIn, bIn, bInB, aInB, ix, 0, iz);         // inland end wall
            }
            return m;
        }
    }
}
