using System;
using Sest.UiFixes;
static class FormationModeTests
{
    static int checks;
    static void Check(bool condition, string text) { checks++; if (!condition) throw new Exception(text); }
    static void Main()
    {
        var mode = new FormationModeState();
        Check(!mode.Stock && !mode.Pending.HasValue, "Default must preserve enhanced UI");
        mode.Toggle();
        Check(!mode.Stock && mode.Pending == true, "Routed click must not rebuild the active UI immediately");
        Check(mode.Commit() && mode.Stock && !mode.Pending.HasValue, "Next controller update must select stock");
        Check(!mode.Commit(), "Repeating an update must not detach/rebuild again");
        mode.Toggle();
        Check(mode.Stock && mode.Pending == false, "Stock UI must offer a way back without changing it inside the click");
        Check(mode.Commit() && !mode.Stock, "Return to enhanced UI");
        mode.Toggle(); mode.Toggle();
        Check(!mode.Commit() && !mode.Stock, "Two queued clicks cancel without two detach/rebuild operations");
        mode.Restore("stock\r\n");
        Check(mode.Stock && !mode.Pending.HasValue && mode.Encode() == "stock", "Stock preference round trip");
        mode.Toggle(); mode.Restore("enhanced\n");
        Check(!mode.Stock && !mode.Pending.HasValue, "Restore clears an uncommitted click");
        mode.Restore("unknown version");
        Check(!mode.Stock, "Unrecognized preference preserves original enhanced behavior");
        mode.Restore(null);
        Check(!mode.Stock, "Missing preference preserves original enhanced behavior");
        for (int i = 0; i < 100; i++)
        {
            bool prior = mode.Stock;
            mode.Toggle(); Check(mode.Commit() && mode.Stock != prior, "Repeated round trip");
        }
        Check(!mode.Stock, "Repeated switches must return to initial mode");
        Console.WriteLine(checks + " formation mode regression checks passed");
    }
}
