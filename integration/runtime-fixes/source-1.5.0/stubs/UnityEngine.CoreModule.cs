// Compile-time stand-in ONLY (never shipped).
using System.Reflection;
[assembly: AssemblyVersion("0.0.0.0")]
namespace UnityEngine
{
    public class Object
    {
        public static bool operator ==(Object a, Object b) { return ReferenceEquals(a, b); }
        public static bool operator !=(Object a, Object b) { return !ReferenceEquals(a, b); }
        public override bool Equals(object o) { return ReferenceEquals(this, o); }
        public override int GetHashCode() { return 0; }
    }
    public class Component : Object { }
    public class Behaviour : Component { }
    public class MonoBehaviour : Behaviour { }
}
