using System;
using System.Reflection;

namespace Sest.UiFixes
{
    static class PerformancePolicyTests
    {
        sealed class Plane { public bool Flying; }
        sealed class Helo { public bool Flying; }
        static int checks;
        static void Check(bool value, string message) { checks++; if (!value) throw new Exception(message); }
        static void Main()
        {
            var aircraftField = typeof(Plane).GetField("Flying");
            var helicopterField = typeof(Helo).GetField("Flying");
            bool reproduced = false;
            try { aircraftField.GetValue(new Helo()); } catch (ArgumentException) { reproduced = true; }
            Check(reproduced, "Original CV16 reflection failure must reproduce");
            Check(!(bool)FlightFlagReader.Read(aircraftField, helicopterField, new Plane { Flying = false }), "Fixed-wing deck hold");
            Check((bool)FlightFlagReader.Read(aircraftField, helicopterField, new Plane { Flying = true }), "Fixed-wing departure");
            Check(!(bool)FlightFlagReader.Read(aircraftField, helicopterField, new Helo { Flying = false }), "Helicopter deck hold");
            Check((bool)FlightFlagReader.Read(aircraftField, helicopterField, new Helo { Flying = true }), "Helicopter departure");
            Check(!(bool)FlightFlagReader.Read(aircraftField, helicopterField, new object()), "Unknown type must hold");
            Check((bool)FlightFlagReader.Read(aircraftField, helicopterField, null), "Missing aircraft must release");

            var cache = new LookupCache<object>();
            object context = new object(), host = new object(), window = new object();
            int scans = 0;
            for (int i = 0; i < 3750; i++) // Five minutes at the author's 12.5 Hz cadence.
                Check(ReferenceEquals(window, cache.Resolve(context, host, i * 0.08f, null,
                    w => ReferenceEquals(w, window), () => { scans++; return window; })), "Stock window lookup");
            Check(scans == 1, "An attached stock window must not trigger repeated HUD searches");
            object previous = window;
            context = new object(); window = new object();
            bool oldValidated = false;
            var result = cache.Resolve(context, host, 301, null,
                w => { if (ReferenceEquals(w, previous)) oldValidated = true; return true; }, () => { scans++; return window; });
            Check(!oldValidated && ReferenceEquals(result, window), "Mission change must discard old native view before validation");
            previous = window; host = new object(); window = new object(); oldValidated = false;
            result = cache.Resolve(context, host, 302, null,
                w => { if (ReferenceEquals(w, previous)) oldValidated = true; return true; }, () => { scans++; return window; });
            Check(!oldValidated && ReferenceEquals(result, window), "Screen change must invalidate the old host");

            var absent = new LookupCache<object>(); scans = 0;
            for (int i = 0; i < 125; i++)
                absent.Resolve(context, host, i * 0.08f, null, w => false, () => { scans++; return null; });
            Check(scans <= 20, "An absent window must limit full discovery to at most twice a second");
            scans = 0;
            for (int i = 0; i < 125; i++)
                absent.Resolve(context, host, 20 + i * 0.08f, window, w => true, () => { scans++; return null; });
            Check(scans == 0, "Author-supplied enhanced window must bypass discovery");
            int invalidCalls = 0;
            absent.Resolve(null, null, 99, null, w => { invalidCalls++; return false; }, () => { invalidCalls++; return null; });
            Check(invalidCalls == 0, "Teardown with no context must not touch native UI");
            var refresh = new UiRefreshGate(); int updates = 0;
            for (int i = 0; i < 3600; i++) if (refresh.Due(window, true, i / 60f)) updates++;
            Check(updates <= 301, "Contacts chrome must not refresh at frame rate");
            Check(refresh.Due(window, false, 60.001f), "Closing must refresh immediately");
            Check(refresh.Due(window, true, 60.002f), "Opening must refresh immediately");
            Check(refresh.Due(new object(), true, 60.003f), "Recreated window must refresh immediately");
            Check(!refresh.Due(null, false, 60.004f), "Missing window needs no chrome update");
            Console.WriteLine("Performance/type-safety checks passed: " + checks);
        }
    }
}
