namespace Sest.UiFixes
{
    internal static class DiagnosticModules
    {
        // Hashes from the 27 October 11:13 Brisbane capture. Timing hooks only.
        // Each entry is { assembly name, inspected hash, ... }.
        internal static readonly string[][] Known = {
            new[] { "CombatCosts", "8f7195ff1540d1901446b3783789c84e1f76bebe943da7606afd85f9dd3d78bc" },
            new[] { "ContactLog", "a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e" },
            new[] { "EnhancedUIMod", "37b9301de2f6d19cd5bd7e16f5042aca6eb80979313b3c84a3a26be106ec6f95" },
            new[] { "IdentifyExpanded", "215af03b37653e0b785e8fad3f977f9883646e846f2c3b6648bc831149e552f1" },
            new[] { "SEST.MenuBackground", "9dfd561db256aaa2455ff0039783b46cfbaf113b641c97f0815121d3a4502515" },
            new[] { "SEST.RuntimeFixes", BuildPins.RuntimeSha256 },
            // The R.A.T.S. host update now lives in Rigging. Pop-Out keeps its own late update.
            new[] { "SeaPowerRigging", "2e2b0bc9c419219753a2dd41866c0819c94234e4a8ac2ba98aa837d60cee5f72" },
            new[] { "SeaPowerPopOut", ContactsSurfaceFix.PopOut14Hash },
            new[] { "SeaPowerSquadPanel", "eff3fa12904a0c61e8fa9f1d10d94e9fa67b0aa76b27c5399808e7ecdd961f4c" },
            new[] { "SeaPowerTopo", "50be459b47b78653a5d4709a83153ac11398512869be1d803646989aca77a6ea" },
            new[] { "UiWorkerProbe", "b87d7a1b2b97b2f717be8303ebf4c9fca29d730715bb6283ecbe4a2df594b7b7" },
        };
    }
}
