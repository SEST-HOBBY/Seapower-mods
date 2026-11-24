using System;
using System.Collections.Generic;

// TEST ONLY. Stub UnityEngine and SeaPower types with the members the drop-in uses, so
// IceFeaturesBattle.cs compiles and runs under Mono without the game. The SeaPower names and
// shapes follow how r16's SeaIceBattle.cs / SeaIceSheet.cs use them (they compile against Sea
// Power 0.9.3 Build 261123); the stubs do not prove the real members exist. That needs the PC.
namespace UnityEngine
{
    public class Object
    {
        private static int ids;
        private readonly int id = ++ids;
        public string name = "";
        internal bool destroyed;
        public static readonly List<Object> Destroyed = new List<Object>();
        public int GetInstanceID() => id;
        public static void Destroy(Object o) { if (o != null) { o.destroyed = true; Destroyed.Add(o); } }
        public static void DontDestroyOnLoad(Object o) { }
        public static bool operator ==(Object a, Object b)
        {
            bool an = ReferenceEquals(a, null) || a.destroyed, bn = ReferenceEquals(b, null) || b.destroyed;
            if (an || bn) return an && bn;
            return ReferenceEquals(a, b);
        }
        public static bool operator !=(Object a, Object b) => !(a == b);
        public override bool Equals(object o) => ReferenceEquals(this, o);
        public override int GetHashCode() => id;
    }

    public struct Vector2
    {
        public float x, y;
        public Vector2(float x, float y) { this.x = x; this.y = y; }
        public static bool operator ==(Vector2 a, Vector2 b) => a.x == b.x && a.y == b.y;
        public static bool operator !=(Vector2 a, Vector2 b) => !(a == b);
        public override bool Equals(object o) => o is Vector2 v && v == this;
        public override int GetHashCode() => x.GetHashCode() ^ y.GetHashCode();
    }

    public struct Vector3
    {
        public float x, y, z;
        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
        public static Vector3 zero => new Vector3(0, 0, 0);
        public float magnitude => (float)Math.Sqrt(x * x + y * y + z * z);
        public static Vector3 operator -(Vector3 a, Vector3 b) => new Vector3(a.x - b.x, a.y - b.y, a.z - b.z);
        public static Vector3 operator +(Vector3 a, Vector3 b) => new Vector3(a.x + b.x, a.y + b.y, a.z + b.z);
        public static Vector3 operator /(Vector3 a, float d) => new Vector3(a.x / d, a.y / d, a.z / d);
        public static Vector3 operator *(Vector3 a, float d) => new Vector3(a.x * d, a.y * d, a.z * d);
    }

    public struct Quaternion
    {
        public float yaw;
        public static Quaternion Euler(float x, float y, float z) => new Quaternion { yaw = y };
    }

    public struct Color
    {
        public float r, g, b, a;
        public Color(float r, float g, float b, float a) { this.r = r; this.g = g; this.b = b; this.a = a; }
    }

    public static class Mathf
    {
        public const float Rad2Deg = 57.29578f;
        public static float Atan2(float y, float x) => (float)Math.Atan2(y, x);
    }

    public static class Time
    {
        public static float time, deltaTime, realtimeSinceStartup;
    }

    public static class Debug { public static void Log(object m) { Console.WriteLine(m); } }

    public class Transform
    {
        public Vector3 position, localScale, eulerAngles;
        public Quaternion rotation;
        public Transform parent;
        public void SetParent(Transform p, bool worldPositionStays) { parent = p; }
    }

    public class Component : Object
    {
        internal GameObject owner;
        private Transform own;
        public Transform transform => owner != null ? owner.transform : (own ?? (own = new Transform()));
        public GameObject gameObject => owner;
    }

    public class Behaviour : Component { public bool enabled = true; }
    public class MonoBehaviour : Behaviour { }

    public sealed class GameObject : Object
    {
        public readonly Transform transform = new Transform();
        public readonly List<Component> Components = new List<Component>();
        public GameObject(string name) { this.name = name; }
        public T AddComponent<T>() where T : Component, new() { var c = new T(); c.owner = this; Components.Add(c); return c; }
        public T GetComponent<T>() where T : Component { foreach (var c in Components) if (c is T t) return t; return null; }
    }

    public sealed class Mesh : Object
    {
        public Vector3[] vertices = new Vector3[0];
        public int[] triangles = new int[0];
        public bool normalsDone, boundsDone;
        public void RecalculateNormals() { normalsDone = true; }
        public void RecalculateBounds() { boundsDone = true; }
    }

    public sealed class MeshFilter : Component { public Mesh sharedMesh; }

    public class Renderer : Component
    {
        public Material sharedMaterial;
        public Rendering.ShadowCastingMode shadowCastingMode;
        public bool receiveShadows;
        public Rendering.ReflectionProbeUsage reflectionProbeUsage;
    }

    public sealed class MeshRenderer : Renderer { }

    public sealed class Shader : Object
    {
        public static readonly HashSet<string> Available = new HashSet<string> { "Legacy Shaders/Diffuse" };
        public bool isSupported = true;
        public static Shader Find(string name) => Available.Contains(name) ? new Shader { name = name } : null;
    }

    public sealed class Material : Object
    {
        public readonly Shader shader;
        public Color color;
        public Material(Shader s) { shader = s; }
        public bool HasProperty(string n) => false;
        public void SetFloat(string n, float v) { }
    }

    public sealed class Camera : Behaviour
    {
        public static Camera main;
        public static Camera[] allCameras => main != null ? new[] { main } : new Camera[0];
    }
}

namespace UnityEngine.Rendering
{
    public enum ShadowCastingMode { Off = 0, On = 1 }
    public enum ReflectionProbeUsage { Off = 0, BlendProbes = 1 }
}

namespace SeaPower
{
    using UnityEngine;

    public class Singleton<T> { private static T _instance; internal static void Set(T v) { _instance = v; } }

    public sealed class Environment : MonoBehaviour
    {
        private DateTime date;
        public bool BrokenDate; // test: the date getter throws
        public DateTime DateTime { get { if (BrokenDate) throw new InvalidOperationException("stub: no date"); return date; } set { date = value; } }
        public int SeaState { get; set; }
    }

    public struct GeoPosition { public double _latitude, _longitude; public float _height; }

    public static class GameTime
    {
        public static double Mission;
        public static double missionElapsedTime => Mission;
    }

    // A simple local frame: 1 Unity unit = 67.2 m (220.472656 ft), equirectangular about the tile,
    // so the drop-in's placement and the test's own geometry agree.
    public static class Utils
    {
        private const double M = 0.3048 * 220.472656;
        public static double OriginLat = -78;
        public static Vector3 longLatToLocalV3(GeoPosition g, Vector2 tile)
        {
            double k = Math.Cos(OriginLat * Math.PI / 180);
            return new Vector3((float)((g._longitude - tile.x) * 111320 * k / M), (float)(g._height / M), (float)((g._latitude - tile.y) * 111320 / M));
        }
        public static GeoPosition worldPositionFromUnityToLongLat(Vector3 p, Vector2 tile)
        {
            double k = Math.Cos(OriginLat * Math.PI / 180);
            return new GeoPosition { _latitude = tile.y + p.z * M / 111320, _longitude = tile.x + p.x * M / (111320 * k) };
        }
        public static float UnityYawToTrueHeading(float yaw, GeoPosition g) => yaw;
    }

    public static class Globals { public static Vector2 _currentCenterTile; }

    public class ObjectBase : MonoBehaviour
    {
        public GeoPosition _geoPosition;
        public bool IsPlayerObject { get; set; }
    }

    public sealed class Submarine : ObjectBase
    {
        public bool Submerged = true;
        public bool isSubmerged() => Submerged;
    }

    public sealed class Compartments
    {
        public ObjectBase _baseObject;
        public bool _isSinking, _immobile;
        private float[] _telegraphVelocities = { -10, 0, 5, 10, 20, 30 };
        private float[] _telegraphVelocitiesSubmerged = { -8, 0, 5, 10, 20, 25 };
        private Submarine _submarine;
        public float WantedVelocityInKnots { get; private set; }
        public float Ordered;
        public Compartments(ObjectBase ob) { _baseObject = ob; _submarine = ob as Submarine; }
        public void UpdateWantedVelocityInKnots() { WantedVelocityInKnots = Ordered; }
    }
}
