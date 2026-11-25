using System;
using System.Collections.Generic;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;

namespace Sest.RuntimeFixes
{
    // Pure iceberg logic of the ice-features drop-in (Icebergs=1 in [Runtime], default OFF): the
    // climatology of mno_env/icebergs.py (data/iceberg-climatology.json, status ESTIMATE), its
    // deterministic generator, a drift step, melt decay and the sensor hooks. No Unity or game
    // types: IceFeaturesTests.exe checks all of it against golden values from the Python module.
    //
    // Same bergs as Python: the generator uses Python's own random stream (PyRandom below: the
    // Mersenne Twister with CPython's string seeding), the same cells, the same order of draws and
    // the same land rings (Natural Earth low resolution, as geo.LandMask) and shelf rings (the
    // simplified Natural Earth outline). So icebergs.generate(bbox, date, seed) with that land mask
    // lists the bergs a battle on that date shows, before drift.
    //
    // Realism notes (from docs/environment/ICEBERGS.md):
    // - Size classes: IIP / MANICE scale (high confidence). Giant bergs are never generated.
    // - Densities: order-of-magnitude ESTIMATES, except the Grand Banks season (IIP 48N counts).
    // - Melt: Martin and Adcroft 2010 form of Bigg et al. 1997, coefficients recalled (medium).
    // - Sensor numbers: the growler radar range is sourced; most others are estimates; the sonar
    //   false-contact value is a DESIGN INDEX, not a probability.

    // Python's random.Random for a str seed (version 2): seed bytes = utf8(s) + sha512(utf8(s)),
    // read as a big-endian integer, fed to MT19937 init_by_array as 32-bit words, least
    // significant first; random() = (a >> 5, b >> 6) / 2^53 (CPython Modules/_randommodule.c).
    internal sealed class PyRandom
    {
        private const int N = 624, M = 397;
        private readonly uint[] mt = new uint[N];
        private int mti = N + 1;
        private double gaussNext;
        private bool hasGauss;

        internal PyRandom(string seed)
        {
            byte[] s = Encoding.UTF8.GetBytes(seed);
            byte[] h;
            using (var sha = SHA512.Create()) h = sha.ComputeHash(s);
            var all = new byte[s.Length + h.Length];
            Buffer.BlockCopy(s, 0, all, 0, s.Length);
            Buffer.BlockCopy(h, 0, all, s.Length, h.Length);
            int start = 0;
            while (start < all.Length && all[start] == 0) start++;
            int nbytes = all.Length - start;
            uint[] key;
            if (nbytes == 0) key = new uint[] { 0 };
            else
            {
                key = new uint[(nbytes + 3) / 4];
                for (int i = 0; i < nbytes; i++) key[i / 4] |= (uint)all[all.Length - 1 - i] << (8 * (i % 4));
            }
            InitByArray(key);
        }

        private void InitGenrand(uint s)
        {
            mt[0] = s;
            for (mti = 1; mti < N; mti++) mt[mti] = unchecked(1812433253u * (mt[mti - 1] ^ (mt[mti - 1] >> 30)) + (uint)mti);
        }

        private void InitByArray(uint[] key)
        {
            InitGenrand(19650218u);
            int i = 1, j = 0, len = key.Length;
            for (int k = Math.Max(N, len); k > 0; k--)
            {
                mt[i] = unchecked((mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1664525u)) + key[j] + (uint)j);
                i++; j++;
                if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
                if (j >= len) j = 0;
            }
            for (int k = N - 1; k > 0; k--)
            {
                mt[i] = unchecked((mt[i] ^ ((mt[i - 1] ^ (mt[i - 1] >> 30)) * 1566083941u)) - (uint)i);
                i++;
                if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
            }
            mt[0] = 0x80000000u;
        }

        private uint Next()
        {
            uint y;
            if (mti >= N)
            {
                int kk;
                for (kk = 0; kk < N - M; kk++)
                {
                    y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
                    mt[kk] = mt[kk + M] ^ (y >> 1) ^ ((y & 1u) != 0 ? 0x9908b0dfu : 0u);
                }
                for (; kk < N - 1; kk++)
                {
                    y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
                    mt[kk] = mt[kk + (M - N)] ^ (y >> 1) ^ ((y & 1u) != 0 ? 0x9908b0dfu : 0u);
                }
                y = (mt[N - 1] & 0x80000000u) | (mt[0] & 0x7fffffffu);
                mt[N - 1] = mt[M - 1] ^ (y >> 1) ^ ((y & 1u) != 0 ? 0x9908b0dfu : 0u);
                mti = 0;
            }
            y = mt[mti++];
            y ^= y >> 11;
            y ^= (y << 7) & 0x9d2c5680u;
            y ^= (y << 15) & 0xefc60000u;
            y ^= y >> 18;
            return y;
        }

        internal double Random()
        {
            uint a = Next() >> 5, b = Next() >> 6;
            return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
        }

        // random.gauss (CPython 3.x)
        internal double Gauss(double mu, double sigma)
        {
            double z;
            if (hasGauss) { z = gaussNext; hasGauss = false; }
            else
            {
                double x2pi = Random() * (2 * Math.PI);
                double g2rad = Math.Sqrt(-2.0 * Math.Log(1.0 - Random()));
                z = Math.Cos(x2pi) * g2rad;
                gaussNext = Math.Sin(x2pi) * g2rad;
                hasGauss = true;
            }
            return mu + z * sigma;
        }
    }

    internal enum BergCategory { Growler = 0, BergyBit = 1, Small = 2, Medium = 3, Large = 4, VeryLarge = 5, Tabular = 6 }

    internal sealed class Berg
    {
        internal string Id, Region;
        internal BergCategory Category;
        internal double Lat, Lon, Lat0, Lon0;        // now; as generated
        internal double LengthM, WidthM, HeightM, DraftM, MassT;
        internal double U, V;                        // drift, m/s east and north
        internal int LifeDays = -1;                  // -1: no sea temperature given
        internal bool LifeCapped;
        internal bool Gone;                          // melted below 1 m
        internal uint Shape;                         // shape seed for the mesh (from Id)
        internal string Band => IceFeaturesData.Bands[(int)Category];
        internal string CategoryName => IceFeaturesData.Categories[(int)Category];
    }

    internal static class IcebergField
    {
        internal const double EarthRadiusKm = 6371.0;   // icebergs.EARTH_R_KM
        internal const int Count = 7;
        internal static readonly BergCategory[] BergClasses = { BergCategory.Small, BergCategory.Medium, BergCategory.Large, BergCategory.VeryLarge, BergCategory.Tabular };

        internal static int CategoryIndex(string name)
        {
            int i = Array.IndexOf(IceFeaturesData.Categories, name);
            if (i < 0) throw new ArgumentException("unknown iceberg category " + name);
            return i;
        }

        // ---- climatology ----------------------------------------------------------------------

        private static bool InBox(double lat, double lon, int b)
        {
            var x = IceFeaturesData.RegionBoxes;
            double la0 = x[4 * b], la1 = x[4 * b + 1], lo0 = x[4 * b + 2], lo1 = x[4 * b + 3];
            if (!(la0 <= lat && lat <= la1)) return false;
            lon = IceFeatureGeo.WrapLon(lon);
            if (lo0 <= lo1) return lo0 <= lon && lon <= lo1;
            return lon >= lo0 || lon <= lo1; // box crosses 180
        }

        // icebergs.region_at: the first region holding the point, or -1 (no modelled bergs).
        internal static int RegionAt(double lat, double lon)
        {
            int n = IceFeaturesData.RegionId.Length;
            for (int r = 0; r < n; r++)
                for (int b = IceFeaturesData.RegionBoxStart[r]; b < IceFeaturesData.RegionBoxStart[r + 1]; b++)
                    if (InBox(lat, lon, b)) return r;
            return -1;
        }

        private static double[][] peaks;
        // icebergs._monthly_peak: bergs (small and larger) per 10,000 km2 for each month.
        internal static double[] MonthlyPeak(int r)
        {
            var p = peaks;
            if (p == null)
            {
                int n = IceFeaturesData.RegionId.Length;
                p = new double[n][];
                for (int k = 0; k < n; k++)
                {
                    var s = new double[12];
                    if (IceFeaturesData.RegionIip[k])
                    {
                        double res = IceFeaturesData.IipResidenceMonths, units = IceFeaturesData.IipAreaKm2 / 1e4;
                        for (int m = 0; m < 12; m++) s[m] = IceFeaturesData.IipCrossings48N[m] * res / units;
                    }
                    else for (int m = 0; m < 12; m++) s[m] = IceFeaturesData.RegionDensity[k] * IceFeaturesData.RegionMonthly[12 * k + m];
                    p[k] = s;
                }
                peaks = p;
            }
            return p[r];
        }

        // icebergs._month_value: month 1..12 is mid-month, fractions interpolate (cyclic).
        internal static double MonthValue(double[] series, double month)
        {
            double m = IceFeatureGeo.PyMod(month - 1.0, 12.0);
            int i = (int)m;
            double f = m - i;
            return series[i] * (1 - f) + series[(i + 1) % 12] * f;
        }

        // icebergs.fractional_month: 1.0 on 15 January.
        internal static double FractionalMonth(DateTime when)
        {
            int days = DateTime.DaysInMonth(when.Year, when.Month);
            return when.Month + (when.Day - 15.0) / days;
        }

        // icebergs.density: bergs per 10,000 km2 for each category (ESTIMATE). Land not checked.
        internal static double[] Density(double lat, double lon, double month)
        {
            var o = new double[Count];
            int r = RegionAt(lat, lon);
            if (r < 0) return o;
            double total = MonthValue(MonthlyPeak(r), month);
            int mix = IceFeaturesData.RegionMix[r];
            for (int c = 0; c < BergClasses.Length; c++) o[(int)BergClasses[c]] = total * IceFeaturesData.MixShares[5 * mix + c];
            o[(int)BergCategory.BergyBit] = total * IceFeaturesData.BergyBitsPerBerg;
            o[(int)BergCategory.Growler] = total * IceFeaturesData.GrowlersPerBerg;
            return o;
        }

        // ---- geometry ---------------------------------------------------------------------------

        // Python round(x, n) (half to even; ties of the binary value are rare enough to ignore here).
        internal static double PyRound(double x, int n)
        {
            double f = Math.Pow(10, n);
            return Math.Round(x * f, MidpointRounding.ToEven) / f;
        }

        // float(f"{x:.2g}"): two significant figures (more would be false precision).
        internal static double TwoSig(double x)
        {
            if (x == 0 || double.IsNaN(x) || double.IsInfinity(x)) return x;
            double e = Math.Floor(Math.Log10(Math.Abs(x)));
            double f = Math.Pow(10, e - 1);
            double r = Math.Round(x / f, MidpointRounding.ToEven) * f;
            return double.Parse(r.ToString("G2", CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);
        }

        // icebergs._dims: length, width, height, draft and mass for one berg, in the stream's order.
        internal static void Dims(int cat, PyRandom rng, out double length, out double width, out double height, out double draft, out double massT)
        {
            var d = IceFeaturesData.CategoryDims;
            double t = rng.Random();
            double l0 = d[4 * cat], l1 = d[4 * cat + 1], h0 = d[4 * cat + 2], h1 = d[4 * cat + 3];
            if (cat == (int)BergCategory.Tabular)
            {
                length = Math.Exp(Math.Log(l0) + t * (Math.Log(l1) - Math.Log(l0))); // many small, few big (estimate)
                height = h0 + rng.Random() * (h1 - h0);
                double f0 = IceFeaturesData.TabularFreeboardMin, f1 = IceFeaturesData.TabularFreeboardMax;
                double thick = height / (f0 + rng.Random() * (f1 - f0));
                draft = thick - height;
                width = length * (0.6 + 0.3 * rng.Random());
                massT = length * width * thick * IceFeaturesData.ShelfIceDensity / 1000;
            }
            else
            {
                length = l0 + t * (l1 - l0);
                double u = Math.Min(1.0, Math.Max(0.0, t + 0.3 * (rng.Random() - 0.5))); // height loosely follows length
                height = h0 + u * (h1 - h0);
                double r0 = IceFeaturesData.DraftToLengthMin, r1 = IceFeaturesData.DraftToLengthMax;
                draft = Math.Min(IceFeaturesData.DraftMaxM, Math.Max(1.2 * height, length * (r0 + rng.Random() * (r1 - r0))));
                double w0 = IceFeaturesData.WidthToLengthMin, w1 = IceFeaturesData.WidthToLengthMax;
                width = length * (w0 + rng.Random() * (w1 - w0));
                massT = IceFeaturesData.BlockCoefficient * length * width * (height + draft) * IceFeaturesData.GlacierIceDensity / 1000;
            }
            length = PyRound(length, 1); width = PyRound(width, 1); height = PyRound(height, 2); draft = PyRound(draft, 1);
            massT = TwoSig(massT);
        }

        // ---- melt -------------------------------------------------------------------------------

        // icebergs.sea_state_from_wind (Martin and Adcroft 2010 proxy)
        internal static double SeaStateFromWind(double windMs)
        {
            double w = Math.Abs(windMs);
            return 1.5 * Math.Sqrt(w) + 0.1 * w;
        }

        // icebergs.melt_rates, m/day: basal, buoyant side convection and wave erosion.
        internal static void MeltRates(double sstC, double lengthM, double seaState, double iceFrac, double relWaterMs, out double basal, out double convection, out double wave)
        {
            double tf = IceFeaturesData.FreezingPointC;
            double du = double.IsNaN(relWaterMs) ? IceFeaturesData.DefaultRelativeWaterMs : Math.Abs(relWaterMs);
            double tw = sstC;
            basal = 0.58 * Math.Pow(du, 0.8) * Math.Max(0.0, tw - tf) / Math.Pow(Math.Max(1.0, lengthM), 0.2);
            convection = tw > 0 ? Math.Max(0.0, 7.62e-3 * tw + 1.29e-3 * tw * tw) : 0.0;
            double a = Math.Min(1.0, Math.Max(0.0, iceFrac));
            wave = Math.Max(0.0, (1.0 / 12) * seaState * (1 + Math.Cos(Math.PI * Math.Pow(a, 3))) * (tw + 2));
        }

        // icebergs.remaining_life_days: whole days at a constant sea temperature and sea state,
        // capped at MaxLifeDays (about 5 years, Bigg et al. 1997). seaState NaN: from windMs.
        internal static int RemainingLifeDays(double lengthM, double widthM, double heightM, double draftM, double sstC, double seaState, double windMs, double iceFrac, out bool capped)
        {
            int cap = IceFeaturesData.MaxLifeDays;
            if (double.IsNaN(seaState)) seaState = SeaStateFromWind(double.IsNaN(windMs) ? 0.0 : windMs);
            double L = lengthM, W = widthM, T = heightM + draftM;
            int day = 0;
            while (day < cap)
            {
                MeltRates(sstC, L, seaState, iceFrac, double.NaN, out double basal, out double conv, out double wave);
                double side = conv + wave;
                L -= 2 * side; W -= 2 * side; T -= basal;
                day += 1;
                if (Math.Min(L, Math.Min(W, T)) < 1.0) { capped = false; return day; }
                if (side == 0 && basal == 0) break;
            }
            capped = true;
            return cap;
        }

        // Decay over dtSeconds of game time at a constant sea temperature (the same rates, applied
        // continuously). Height and draft shrink in proportion. Returns false once the berg is gone.
        internal static bool Melt(Berg b, double dtSeconds, double sstC, double seaState, double iceFrac)
        {
            if (b.Gone) return false;
            if (double.IsNaN(sstC) || !(dtSeconds > 0)) return true;
            MeltRates(sstC, b.LengthM, seaState, iceFrac, double.NaN, out double basal, out double conv, out double wave);
            double days = dtSeconds / 86400.0, side = (conv + wave) * days;
            double T = b.HeightM + b.DraftM, T2 = T - basal * days;
            b.LengthM -= 2 * side; b.WidthM -= 2 * side;
            if (T > 0) { b.HeightM *= T2 / T; b.DraftM *= T2 / T; }
            if (Math.Min(b.LengthM, Math.Min(b.WidthM, T2)) < 1.0) b.Gone = true;
            return !b.Gone;
        }

        // ---- drift ------------------------------------------------------------------------------

        // One drift step: the berg's own velocity (the region's current proxy, an estimate, plus the
        // class wind factor times the wind, both m/s) through geo.displace.
        internal static void Drift(Berg b, double dtSeconds, double windU = 0, double windV = 0)
        {
            if (b.Gone || !(dtSeconds > 0)) return;
            double wf = IceFeaturesData.WindFactor[(int)b.Category];
            double u = b.U + wf * windU, v = b.V + wf * windV;
            double eastNm = u * IceFeatureGeo.KnotsPerMs * dtSeconds / 3600, northNm = v * IceFeatureGeo.KnotsPerMs * dtSeconds / 3600;
            IceFeatureGeo.Displace(b.Lat, b.Lon, eastNm, northNm, out double lat, out double lon);
            b.Lat = lat; b.Lon = lon;
        }

        // ---- placement --------------------------------------------------------------------------

        private const double CentiDeg = 100.0;
        private static double[] coastBox;
        // geo.LandMask.is_land over the Natural Earth low-resolution rings (coarse: straits under
        // about 15 nm can read as land, small islands can be missing; geo.py says so too).
        internal static bool Land(double lat, double lon)
        {
            lon = IceFeatureGeo.WrapLon(lon);
            if (lat <= -85.0) return true;
            var box = coastBox;
            var pts = IceFeaturesData.CoastPts;
            int rings = IceFeaturesData.CoastStart.Length - 1;
            if (box == null)
            {
                box = new double[rings * 4];
                for (int r = 0; r < rings; r++)
                {
                    double x0 = double.MaxValue, x1 = double.MinValue, y0 = double.MaxValue, y1 = double.MinValue;
                    for (int k = IceFeaturesData.CoastStart[r]; k < IceFeaturesData.CoastStart[r + 1]; k++)
                    {
                        double x = pts[2 * k] / CentiDeg, y = pts[2 * k + 1] / CentiDeg;
                        x0 = Math.Min(x0, x); x1 = Math.Max(x1, x); y0 = Math.Min(y0, y); y1 = Math.Max(y1, y);
                    }
                    box[4 * r] = x0; box[4 * r + 1] = x1; box[4 * r + 2] = y0; box[4 * r + 3] = y1;
                }
                coastBox = box;
            }
            for (int r = 0; r < rings; r++)
                if (box[4 * r + 2] <= lat && lat <= box[4 * r + 3] && box[4 * r] <= lon && lon <= box[4 * r + 1] &&
                    IceFeatureGeo.RingContains(pts, IceFeaturesData.CoastStart[r], IceFeaturesData.CoastStart[r + 1], CentiDeg, lat, lon))
                    return true;
            return false;
        }

        // icebergs._blocked: land, or an Antarctic ice shelf.
        internal static bool Blocked(double lat, double lon) => Land(lat, lon) || (lat < -60 && IceShelves.ShelfAt(lat, lon) >= 0);

        private static int Poisson(double lam, PyRandom rng)
        {
            if (lam <= 0) return 0;
            if (lam > 50) return Math.Max(0, (int)Math.Round(rng.Gauss(lam, Math.Sqrt(lam)), MidpointRounding.ToEven));
            int k = 0;
            double p = 1.0, limit = Math.Exp(-lam);
            while (true)
            {
                p *= rng.Random();
                if (p <= limit) return k;
                k++;
            }
        }

        internal static uint Fnv(string s)
        {
            uint h = 2166136261u;
            foreach (char c in s) { h ^= c; h = unchecked(h * 16777619u); }
            return h;
        }

        // icebergs.generate: bergs inside [lat0, lat1] x [lon0, lon1] (lon0 > lon1 crosses 180) for a
        // date, drawn per global cell (cellDeg) from the stream "mno-icebergs|seed|date|j|i", so a
        // cell always holds the same bergs whatever the box. Never on land or a shelf (blocked).
        // sstC NaN: no life computed. Throws when more than maxBergs would be made.
        internal static List<Berg> Generate(double lat0, double lat1, double lon0, double lon1, DateTime when, string seed,
            Func<double, double, bool> blocked = null, double sstC = double.NaN, double cellDeg = 0.5, int maxBergs = 20000, bool[] categories = null)
        {
            if (lat0 > lat1) throw new ArgumentException("bbox lat_min > lat_max");
            if (blocked == null) blocked = Blocked;
            double span = IceFeatureGeo.PyMod(lon1 - lon0, 360.0);
            if (span == 0) span = lon1 != lon0 ? 360.0 : 0.0;
            double month = FractionalMonth(when);
            string dateKey = when.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
            var o = new List<Berg>();
            long j0 = (long)Math.Floor(lat0 / cellDeg), j1 = (long)Math.Floor(lat1 / cellDeg);
            long iStart = (long)Math.Floor(lon0 / cellDeg);
            long iCount = (long)Math.Ceiling(span / cellDeg) + 1;
            var seen = new HashSet<long>();
            for (long j = j0; j <= j1; j++)
            {
                double clat0 = j * cellDeg, clatC = clat0 + cellDeg / 2;
                for (long di = 0; di < iCount; di++)
                {
                    long iRaw = iStart + di;
                    double clon0 = IceFeatureGeo.WrapLon(iRaw * cellDeg);
                    long i = (long)Math.Floor(clon0 / cellDeg + 1e-9);
                    if (!seen.Add(j * 1000003L + i)) continue;
                    int r = RegionAt(clatC, clon0 + cellDeg / 2);
                    if (r < 0) continue;
                    double area = Math.Pow(EarthRadiusKm * IceFeatureGeo.Radians(cellDeg), 2) * Math.Cos(IceFeatureGeo.Radians(clatC));
                    var dens = Density(clatC, clon0 + cellDeg / 2, month);
                    var rng = new PyRandom("mno-icebergs|" + seed + "|" + dateKey + "|" + j.ToString(CultureInfo.InvariantCulture) + "|" + i.ToString(CultureInfo.InvariantCulture));
                    for (int cat = 0; cat < Count; cat++) // fixed order keeps the stream stable
                    {
                        int n = Poisson(dens[cat] * area / 1e4, rng);
                        for (int k = 0; k < n; k++)
                        {
                            double plat = double.NaN, plon = double.NaN;
                            for (int t = 0; t < 8; t++) // a few tries to land in water
                            {
                                double la = clat0 + rng.Random() * cellDeg;
                                double lo = IceFeatureGeo.WrapLon(clon0 + rng.Random() * cellDeg);
                                if (!blocked(la, lo)) { plat = la; plon = lo; break; }
                            }
                            Dims(cat, rng, out double length, out double width, out double height, out double draft, out double mass);
                            if (double.IsNaN(plat) || (categories != null && !categories[cat])) continue;
                            if (!(lat0 <= plat && plat <= lat1 && IceFeatureGeo.PyMod(plon - lon0, 360.0) <= span)) continue;
                            if (RegionAt(plat, plon) < 0) continue;
                            string id = "gen-" + dateKey + "-" + j.ToString(CultureInfo.InvariantCulture) + "-" + i.ToString(CultureInfo.InvariantCulture) + "-" + IceFeaturesData.Categories[cat] + "-" + k.ToString(CultureInfo.InvariantCulture);
                            var b = new Berg
                            {
                                Id = id, Category = (BergCategory)cat, Region = IceFeaturesData.RegionId[r],
                                Lat = plat, Lon = plon, Lat0 = plat, Lon0 = plon,
                                LengthM = length, WidthM = width, HeightM = height, DraftM = draft, MassT = mass,
                                U = IceFeaturesData.RegionCurrent[2 * r] + IceFeaturesData.WindFactor[cat] * 0.0,
                                V = IceFeaturesData.RegionCurrent[2 * r + 1] + IceFeaturesData.WindFactor[cat] * 0.0,
                                Shape = Fnv(id),
                            };
                            if (!double.IsNaN(sstC))
                            {
                                b.LifeDays = RemainingLifeDays(length, width, height, draft, sstC, double.NaN, 0.0, 0.0, out bool capped);
                                b.LifeCapped = capped;
                            }
                            o.Add(b);
                            if (o.Count > maxBergs) throw new InvalidOperationException("more than " + maxBergs + " bergs: use a smaller box");
                        }
                    }
                }
            }
            return o;
        }

        // ---- sensors ----------------------------------------------------------------------------

        // sensors.radar_horizon_km: radio horizon over a smooth sea, effective Earth radius factor k.
        internal static double RadarHorizonKm(double radarM, double targetM, double k = 4.0 / 3.0)
        {
            double re = 6371.0 * k;
            return Math.Sqrt(2 * re * radarM / 1000) + Math.Sqrt(2 * re * targetM / 1000);
        }

        // icebergs.radar_range_factor: 0..1 on the calm-sea range; 0 = lost in sea clutter (ESTIMATE).
        internal static double RadarFactor(int cat, int seaState) =>
            IceFeaturesData.RadarSeaStateFactor[10 * cat + Math.Max(0, Math.Min(9, seaState))];

        internal static double MidHeight(int cat) => (IceFeaturesData.CategoryDims[4 * cat + 2] + IceFeaturesData.CategoryDims[4 * cat + 3]) / 2;

        // icebergs.radar_detection_nm: calm-sea range times the sea-state factor, capped by the radar
        // horizon to the berg top (4/3 Earth). heightM NaN: the middle of the class.
        internal static double RadarDetectionNm(int cat, int seaState, double antennaM = 20.0, double heightM = double.NaN, bool enhanced = false)
        {
            double b = (enhanced ? IceFeaturesData.RadarCalmEnhancedNm : IceFeaturesData.RadarCalmNm)[cat];
            if (double.IsNaN(heightM)) heightM = MidHeight(cat);
            double horizon = RadarHorizonKm(antennaM, Math.Max(0.1, heightM)) / IceFeatureGeo.KmPerNm;
            return PyRound(Math.Min(b * RadarFactor(cat, seaState), horizon), 2);
        }

        // icebergs.visual_detection_nm: least of visibility, geographic range (Bowditch) and the
        // small-ice cap; a moonless night scales it (estimate).
        internal static double VisualDetectionNm(int cat, double visibilityKm, double eyeM = 15.0, double heightM = double.NaN, bool night = false)
        {
            if (double.IsNaN(heightM)) heightM = MidHeight(cat);
            double geoNm = IceFeaturesData.GeographicRangeCoefficient * (Math.Sqrt(eyeM) + Math.Sqrt(Math.Max(0.0, heightM)));
            double cap = IceFeaturesData.VisualDayCapNm[cat];
            double r = Math.Min(Math.Min(Math.Max(0.0, visibilityKm) / IceFeatureGeo.KmPerNm, geoNm), double.IsNaN(cap) ? geoNm : cap);
            if (night) r *= IceFeaturesData.VisualNightFactor;
            return PyRound(r, 2);
        }

        // icebergs.sonar_false_contact_index: 0..1 DESIGN INDEX, not a probability. A keel that does
        // not reach within 50 m (estimate) of the sonar depth halves it. NaN: not given.
        internal static double SonarFalseContactIndex(int cat, double draftM = double.NaN, double sonarDepthM = double.NaN)
        {
            double b = IceFeaturesData.SonarFalseContactIndex[cat];
            if (!double.IsNaN(draftM) && !double.IsNaN(sonarDepthM) && draftM + 50.0 < sonarDepthM) b *= 0.5;
            return PyRound(b, 3);
        }

        // The sonar false-contact flag: the index at or above a design threshold (0.5 default:
        // medium bergs and larger with a keel near the sonar). A game rule, not a measured rate.
        internal const double DefaultFalseContactThreshold = 0.5;
        internal static bool FalseContact(int cat, double draftM, double sonarDepthM, double threshold = DefaultFalseContactThreshold) =>
            SonarFalseContactIndex(cat, draftM, sonarDepthM) >= threshold;
    }

    // A low-poly berg sized by its class dimensions (waterline length and width, height above the
    // waterline, draft below it), in metres, x east, y up, z north, centred on the waterline.
    // Shape (a visual choice, not data): an irregular ring of corners around an ellipse of the
    // waterline length and width, jittered from the berg's id so every berg differs but is the
    // same each time. Non-tabular bergs narrow toward a dome top and widen a little below the
    // waterline, then taper to the keel at the draft; tabular bergs are flat-topped slabs with
    // near-vertical sides. The waterline ring sits at y = 0, so the draft is below the waterline.
    internal static class BergMesher
    {
        private static double Jitter(ref uint s)
        {
            s ^= s << 13; s ^= s >> 17; s ^= s << 5;
            return (s & 0xFFFFFF) / (double)0x1000000;
        }

        internal static IceMeshData Build(Berg b) => Build(b.Category, b.LengthM, b.WidthM, b.HeightM, b.DraftM, b.Shape);

        internal static IceMeshData Build(BergCategory cat, double lengthM, double widthM, double heightM, double draftM, uint shape)
        {
            uint s = shape == 0 ? 0x9E3779B9u : shape;
            bool tabular = cat == BergCategory.Tabular;
            int corners = tabular ? 10 : (cat <= BergCategory.BergyBit ? 6 : 8);
            double a = Math.Max(0.5, lengthM) / 2, c = Math.Max(0.5, widthM) / 2;
            double h = Math.Max(0.05, heightM), d = Math.Max(0.1, draftM);
            double rot = Jitter(ref s) * Math.PI * 2;
            var ring = new double[corners * 2];
            for (int k = 0; k < corners; k++)
            {
                double t = (k + 0.3 * (Jitter(ref s) - 0.5)) / corners * Math.PI * 2;
                double r = tabular ? 0.92 + 0.08 * Jitter(ref s) : 0.75 + 0.25 * Jitter(ref s);
                double x = a * Math.Cos(t) * r, z = c * Math.Sin(t) * r;
                ring[2 * k] = x * Math.Cos(rot) - z * Math.Sin(rot);
                ring[2 * k + 1] = x * Math.Sin(rot) + z * Math.Cos(rot);
            }
            // levels: (y, scale of the waterline ring)
            double[] ys, sc;
            if (tabular) { ys = new[] { -d, -0.05 * d, 0.0, h }; sc = new[] { 0.95, 1.0, 1.0, 0.97 }; }
            else { ys = new[] { -d, -0.45 * d, 0.0, 0.5 * h, 0.85 * h }; sc = new[] { 0.3, 1.1, 1.0, 0.8, 0.45 }; }
            var m = new IceMeshData();
            for (int lv = 0; lv + 1 < ys.Length; lv++)
                for (int k = 0; k < corners; k++)
                {
                    int k2 = (k + 1) % corners;
                    var p0 = IceMeshData.P(ring[2 * k] * sc[lv], ys[lv], ring[2 * k + 1] * sc[lv]);
                    var p1 = IceMeshData.P(ring[2 * k2] * sc[lv], ys[lv], ring[2 * k2 + 1] * sc[lv]);
                    var p2 = IceMeshData.P(ring[2 * k2] * sc[lv + 1], ys[lv + 1], ring[2 * k2 + 1] * sc[lv + 1]);
                    var p3 = IceMeshData.P(ring[2 * k] * sc[lv + 1], ys[lv + 1], ring[2 * k + 1] * sc[lv + 1]);
                    double ox = (p0[0] + p1[0] + p2[0] + p3[0]) / 4, oz = (p0[2] + p1[2] + p2[2] + p3[2]) / 4;
                    double dy = (sc[lv] - sc[lv + 1]) * Math.Sqrt(ox * ox + oz * oz) / Math.Max(1e-6, ys[lv + 1] - ys[lv]); // outward tilt
                    m.Quad(p0, p1, p2, p3, ox, dy, oz);
                }
            // caps: a flat top (tabular) or a dome point at the full height, and the keel point at the draft
            var top = IceMeshData.P(0, h, 0);
            var keel = IceMeshData.P(0, -d, 0);
            int last = ys.Length - 1;
            for (int k = 0; k < corners; k++)
            {
                int k2 = (k + 1) % corners;
                var t0 = IceMeshData.P(ring[2 * k] * sc[last], ys[last], ring[2 * k + 1] * sc[last]);
                var t1 = IceMeshData.P(ring[2 * k2] * sc[last], ys[last], ring[2 * k2 + 1] * sc[last]);
                m.Tri(top, t0, t1, 0, 1, 0);
                var b0 = IceMeshData.P(ring[2 * k] * sc[0], ys[0], ring[2 * k + 1] * sc[0]);
                var b1 = IceMeshData.P(ring[2 * k2] * sc[0], ys[0], ring[2 * k2 + 1] * sc[0]);
                m.Tri(keel, b0, b1, 0, -1, 0);
            }
            return m;
        }
    }
}
