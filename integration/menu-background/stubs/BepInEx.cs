// Compile-time stand-in for BepInEx 5's BepInEx.dll: only the two types the
// SEST plugin names, with BepInEx 5.4's own signatures. It is never shipped.
// At run time the game's real BepInEx.dll (5.4.23.2 in the 3 Oct 2026
// snapshot) answers these references by name; BepInEx is not strong-named,
// so the binding does not depend on this file's version.
using System;
using System.Reflection;
using UnityEngine;

[assembly: AssemblyVersion("5.4.23.2")]

namespace BepInEx
{
    [AttributeUsage(AttributeTargets.Class, AllowMultiple = false)]
    public class BepInPlugin : Attribute
    {
        public BepInPlugin(string GUID, string Name, string Version) { }
    }

    public abstract class BaseUnityPlugin : MonoBehaviour
    {
        protected BaseUnityPlugin() { }
    }
}
