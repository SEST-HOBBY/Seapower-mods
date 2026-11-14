// Beta-only assembly preparation. Author Workshop files are never rewritten.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string IdentifyHash = "9f0ec630e9d7659082bdce61743a87895de14f1903a44c68395f8f158af8afd7";
    private static readonly Dictionary<string, string> originalPaths = new(StringComparer.OrdinalIgnoreCase);
    private static readonly Dictionary<string, ModuleDefinition> nativeModules = new(StringComparer.OrdinalIgnoreCase);
    private static readonly Dictionary<ModuleDefinition, Dictionary<string, TypeDefinition>> nativeTypes = new();
    private static readonly object pathLock = new();

    // Calls from an adapted Identify image use this accessor, preserving its
    // Workshop assets/config provenance while the image lives in a private cache.
    public static string OriginalLocation(Assembly assembly)
    {
        string location = assembly.Location;
        lock (pathLock) return originalPaths.TryGetValue(Path.GetFullPath(location), out string source) ? source : location;
    }

    internal static string Hash(string path)
    {
        using var stream = File.OpenRead(path);
        using var sha = SHA256.Create();
        return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }

    private static IEnumerable<TypeDefinition> Types(IEnumerable<TypeDefinition> roots)
    {
        foreach (var type in roots) {
            yield return type;
            foreach (var child in Types(type.NestedTypes)) yield return child;
        }
    }

    internal static List<string> InvalidNativeFields(ModuleDefinition module, ModuleDefinition native)
    {
        if (!nativeTypes.TryGetValue(native, out var definitions)) {
            definitions = Types(native.Types).ToDictionary(t => t.FullName);
            nativeTypes[native] = definitions;
        }
        var errors = new List<string>();
        foreach (var type in Types(module.Types)) foreach (var field in type.Fields)
            Check(field.FieldType, type.FullName + "." + field.Name, definitions, errors);
        return errors;
    }

    private static void Check(TypeReference type, string field, Dictionary<string, TypeDefinition> definitions, List<string> errors)
    {
        if (type is GenericInstanceType generic) {
            foreach (var argument in generic.GenericArguments) Check(argument, field, definitions, errors);
            Check(generic.ElementType, field, definitions, errors);
            return;
        }
        if (type is TypeSpecification specification) { Check(specification.ElementType, field, definitions, errors); return; }
        if (type.Scope is AssemblyNameReference scope && scope.Name == "Seapower-Scripts" &&
            definitions.TryGetValue(type.FullName, out var actual) && type.IsValueType != actual.IsValueType)
            errors.Add(field + ": " + type.FullName + " encoded as " + (type.IsValueType ? "value" : "reference")
                + "; native definition is " + (actual.IsValueType ? "value" : "reference"));
    }

    public static string Prepare(string source, string nativePath, string cacheRoot, Action<string> log)
    {
        string hash = Hash(source);
        if (HoldRejectedStartup(hash, source, log)) return null;
        if (IsNativePeLibrary(source)) {
            log("SKIPPED native library before CLR metadata scan: " + Path.GetFileName(source) + "; original file retained.");
            return null;
        }
        // A pinned adapter rewrites one exact author image. Any other image
        // loads unadapted, but only if every game member it names exists.
        var adapter = AdapterFor(hash);
        var native = NativeModule(nativePath);
        using var resolver = new DefaultAssemblyResolver();
        foreach (var resolverDirectory in new[] { Path.GetDirectoryName(source), Path.GetDirectoryName(nativePath),
            Path.GetDirectoryName(typeof(HarmonyLib.Harmony).Assembly.Location),
            Path.GetDirectoryName(typeof(BetaAssemblyPolicy).Assembly.Location) })
            if (!String.IsNullOrEmpty(resolverDirectory)) resolver.AddSearchDirectory(resolverDirectory);
        using var module = ModuleDefinition.ReadModule(source, new ReaderParameters {
            InMemory = true, ReadingMode = ReadingMode.Deferred, AssemblyResolver = resolver });
        // Preserve the owner's ExtendedGuidance-off profile before CLR load.
        if (module.Assembly.Name.Name == "ExtendedGuidance") {
            log("SKIPPED before CLR load: ExtendedGuidance; disabled by the SEST profile. Data files retained.");
            return null;
        }
        // R14: a plugin whose own library in the same folder is held cannot
        // run either (Osprey deck code needs Osprey Mechanics).
        string dependency = HeldDependency(module, source, native, new HashSet<string>(StringComparer.OrdinalIgnoreCase));
        if (dependency != null) {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; depends on " + dependency + ". Data retained.");
            return null;
        }
        bool plugin = Types(module.Types).Any(t => t.CustomAttributes.Any(a => a.AttributeType.FullName == "AnchorChain.ACPlugin"));
        // Libraries are not loaded here; the CLR resolves them for their
        // dependants, which the rule above holds when the library would fail.
        if (!plugin) return null;
        var bad = InvalidNativeFields(module, native);
        if (adapter != null) bad.RemoveAll(finding => adapter.AcceptedNativeFields.Contains(finding));
        if (bad.Count != 0) {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; " + String.Join("; ", bad.Take(4)));
            return null;
        }
        string audit = AdaptCapturedImage(module, native, hash);
        // R14: check the image that would load, after any rewrite. A game
        // member this build no longer has fails the whole method when Mono
        // compiles it, so a partial plugin is held instead of half-running.
        var missing = UnresolvedNativeMembers(module, native);
        if (missing.Count != 0) {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; names " + missing.Count +
                " game member(s) this build does not have: " + String.Join("; ", missing.Take(4)) + ". Awaiting an author port; data retained.");
            return null;
        }
        if (audit == null) return source;
        string directory = Path.Combine(cacheRoot, "beta-api-r14-261113", hash);
        Directory.CreateDirectory(directory);
        string target = Path.Combine(directory, module.Assembly.Name.Name + ".dll");
        string temporary = target + ".tmp";
        module.Write(temporary);
        using (var check = ModuleDefinition.ReadModule(temporary)) {
            if (InvalidNativeFields(check, native).Count != 0) throw new InvalidDataException("Adapted native field layout failed validation");
        }
        if (File.Exists(target)) File.Delete(target);
        File.Move(temporary, target);
        lock (pathLock) originalPaths[Path.GetFullPath(target)] = Path.GetFullPath(source);
        log("ADAPTED " + module.Assembly.Name.Name + " in private cache: " + audit + "; original Workshop DLL and asset paths preserved.");
        return target;
    }

    private static ModuleDefinition NativeModule(string nativePath)
    {
        nativePath = Path.GetFullPath(nativePath);
        lock (pathLock) {
            if (nativeModules.TryGetValue(nativePath, out var cached)) return cached;
            if (Hash(nativePath) != "3f56861f09e867f315b194c81a7a2450154ccc6bb5afb769b4956dfd4a00503a")
                throw new InvalidDataException("Assembly adapters require the inspected 0.9.2-261113 (3f56861f).");
            var native = ModuleDefinition.ReadModule(nativePath, new ReaderParameters { InMemory = true });
            nativeModules[nativePath] = native;
            return native;
        }
    }

    // The reason a referenced library beside this image would be held, or
    // null. Only libraries in the same folder are judged; anything else is
    // left to the CLR as before.
    private static string HeldDependency(ModuleDefinition module, string source, ModuleDefinition native, HashSet<string> visited)
    {
        if (!visited.Add(Path.GetFullPath(source))) return null;
        foreach (var reference in module.AssemblyReferences) {
            string sibling = Path.Combine(Path.GetDirectoryName(source), reference.Name + ".dll");
            if (!File.Exists(sibling) || visited.Contains(Path.GetFullPath(sibling)) || IsNativePeLibrary(sibling)) continue;
            string hash = Hash(sibling);
            if (StartupHolds.ContainsKey(hash)) return reference.Name + ", which is held";
            // A pinned adapter vouches for its image; its own load reports any failure.
            if (AdapterFor(hash) != null) continue;
            using var library = ModuleDefinition.ReadModule(sibling, new ReaderParameters { ReadingMode = ReadingMode.Deferred });
            if (library.Assembly.Name.Name == "ExtendedGuidance") return reference.Name + ", which the SEST profile disables";
            var missing = UnresolvedNativeMembers(library, native);
            if (missing.Count != 0) return reference.Name + ", which names game members this build does not have (" + missing[0] + ")";
            string deeper = HeldDependency(library, sibling, native, visited);
            if (deeper != null) return reference.Name + ", which depends on " + deeper;
        }
        return null;
    }

    // Every game type, method and field the module's code and signatures
    // name, checked against the native image itself (not by loading it).
    internal static List<string> UnresolvedNativeMembers(ModuleDefinition module, ModuleDefinition native)
    {
        var resolver = new MetadataResolver(new NativeOnlyResolver(native.Assembly));
        var missing = new List<string>();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        bool Native(TypeReference type)
        {
            while (type is TypeSpecification specification) type = specification.ElementType;
            while (type?.DeclaringType != null && type.Scope == null) type = type.DeclaringType;
            return type != null && type.Scope is AssemblyNameReference scope && scope.Name == native.Assembly.Name.Name;
        }
        void Type(TypeReference type)
        {
            if (type == null || type.IsGenericParameter) return;
            if (type is GenericInstanceType generic) { foreach (var argument in generic.GenericArguments) Type(argument); Type(generic.ElementType); return; }
            if (type is TypeSpecification specification) { Type(specification.ElementType); return; }
            if (!Native(type) || !seen.Add("T " + type.FullName)) return;
            TypeDefinition resolved = null;
            try { resolved = resolver.Resolve(type); } catch (Exception) { }
            if (resolved == null) missing.Add("type " + type.FullName);
        }
        void Member(MemberReference member)
        {
            if (member is TypeReference type) { Type(type); return; }
            if (member is GenericInstanceMethod instance) { foreach (var argument in instance.GenericArguments) Type(argument); Member(instance.ElementMethod); return; }
            if (member?.DeclaringType == null) return;
            Type(member.DeclaringType);
            if (!Native(member.DeclaringType) || !seen.Add("M " + member.FullName)) return;
            object resolved = null;
            try { resolved = member is MethodReference method ? resolver.Resolve(method) : member is FieldReference field ? resolver.Resolve(field) : (object)member; }
            catch (Exception) { }
            if (resolved == null) missing.Add(member.FullName);
        }
        foreach (var type in Types(module.Types)) {
            Type(type.BaseType);
            foreach (var face in type.Interfaces) Type(face.InterfaceType);
            foreach (var field in type.Fields) Type(field.FieldType);
            foreach (var property in type.Properties) Type(property.PropertyType);
            foreach (var method in type.Methods) {
                Type(method.ReturnType);
                foreach (var parameter in method.Parameters) Type(parameter.ParameterType);
                if (!method.HasBody) continue;
                foreach (var variable in method.Body.Variables) Type(variable.VariableType);
                foreach (var handler in method.Body.ExceptionHandlers) Type(handler.CatchType);
                foreach (var instruction in method.Body.Instructions)
                    if (instruction.Operand is MemberReference member) Member(member);
            }
        }
        return missing;
    }

    private sealed class NativeOnlyResolver : IAssemblyResolver
    {
        private readonly AssemblyDefinition native;
        internal NativeOnlyResolver(AssemblyDefinition native) { this.native = native; }
        public AssemblyDefinition Resolve(AssemblyNameReference name) => name.Name == native.Name.Name ? native : null;
        public AssemblyDefinition Resolve(AssemblyNameReference name, ReaderParameters parameters) => Resolve(name);
        public void Dispose() { }
    }

}
