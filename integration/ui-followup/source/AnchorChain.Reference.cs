// Compile-time reference only. Never install this assembly in the game.
// Signatures are taken from the captured Runtime 1.5.0 assembly metadata.
using System;
using System.Reflection;
[assembly: AssemblyVersion("1.1.0.0")]
namespace AnchorChain
{
    public interface IAnchorChainMod { void TriggerEntryPoint(); }
    public sealed class ACPlugin : Attribute
    {
        public ACPlugin(string guid, string name, string version, string[] dependencies, string[] incompatible) { }
    }
}
