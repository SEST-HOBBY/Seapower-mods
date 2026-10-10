// Compile-time stand-in for Anchor Chain 1.1.0's AnchorChain.dll: only the two
// types the SEST plugin names, with the signatures of
// github.com/SeaPower-Modders/AnchorChain AnchorChain/Main.cs (28d225b). It is
// never shipped. At run time the AnchorChain.dll the game has loaded answers
// these references by assembly name.
using System;
using System.Reflection;

[assembly: AssemblyVersion("1.1.0.0")]

namespace AnchorChain
{
    [AttributeUsage(AttributeTargets.Class, AllowMultiple = false)]
    public class ACPlugin : Attribute
    {
        public ACPlugin(string guid, string name, string version, string[] before = null, string[] after = null) { }
    }

    public interface IAnchorChainMod
    {
        void TriggerEntryPoint();
    }
}
