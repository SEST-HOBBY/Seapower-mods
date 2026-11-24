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
    // The previous Identify build needs the API adapter. Version 3.420.6967 uses the native API.
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
        // Sensor View's EG add-on finds EG only by type name, so the
        // dependency rule cannot see it; it shares this switch and lifts with it.
        if (module.Assembly.Name.Name == "ExtendedGuidance") {
            log("SKIPPED before CLR load: ExtendedGuidance; disabled by the SEST profile. Data files retained.");
            return null;
        }
        if (module.Assembly.Name.Name == "SensorView.ExtendedGuidance") {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; Sensor View's add-on for ExtendedGuidance, which the SEST profile disables. "
                + "Sensor View and its other add-ons load. Data retained.");
            return null;
        }
        // Another mod loader's own image, at any hash (the reviewed hashes
        // are StartupHolds above): SEST never starts a second loader.
        if (ForeignLoaderAssemblies.Contains(module.Assembly.Name.Name)) {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + " (" + hash.Substring(0, 8) + "); R.A.T.S. Keel's own loader image, "
                + "which SEST does not start. Data retained.");
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
        // R16: a hash-pinned BepInEx-only Workshop plugin is started by SEST's
        // loader (WorkshopBepInRunner) once its own metadata matches the pin.
        var bepin = plugin ? null : WorkshopBepInFor(hash);
        // Libraries are not loaded here; the CLR resolves them for their
        // dependants, which the rule above holds when the library would fail.
        if (!plugin && bepin == null) return null;
        if (bepin != null) {
            string refusal = WorkshopBepInRefusal(module, source, bepin);
            if (refusal != null) {
                log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; " + refusal + ". Data retained.");
                return null;
            }
        }
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
        // R16: a pinned nested loader admits only with every companion checked
        // (AssemblyPolicy.Companions.cs); adapted companions preload first.
        if (NestedLoaderCompanions.TryGetValue(hash, out var companions)) {
            var preloads = new List<string>();
            string refusal = PrepareCompanions(source, companions, native, nativePath, cacheRoot, log, preloads);
            if (refusal != null) {
                log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; companion " + refusal + ". Data retained.");
                return null;
            }
            lock (pathLock) companionPreloads[Path.GetFullPath(source)] = preloads;
        }
        if (audit == null) return source;
        string directory = Path.Combine(cacheRoot, "beta-api-r16-261123", hash);
        // Rigging checks the last directory name of its client assembly against
        // the Workshop ID in usersettings.ini. Preserve that name for Topo.
        if (hash == Topography181Hash)
            directory = Path.Combine(directory, new FileInfo(source).Directory.Name);
        string target = WritePrivateImage(module, native, source, directory);
        log("ADAPTED " + module.Assembly.Name.Name + " in private cache: " + audit + "; original Workshop DLL and asset paths preserved.");
        return target;
    }

    // Writes an adapted image to its private cache folder, re-checks its
    // native field layout and records its Workshop provenance.
    private static string WritePrivateImage(ModuleDefinition module, ModuleDefinition native, string source, string directory)
    {
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
        return target;
    }

    private static ModuleDefinition NativeModule(string nativePath)
    {
        nativePath = Path.GetFullPath(nativePath);
        lock (pathLock) {
            if (nativeModules.TryGetValue(nativePath, out var cached)) return cached;
            if (Hash(nativePath) != "ea653e49632dbaaad16d33b9c51d79b3eec420e7c41954dbcd09d19157beb65a")
                throw new InvalidDataException("Assembly adapters require the inspected 0.9.3-261123 (ea653e49).");
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
            // Get, Set, Address and .ctor of a multi-dimensional array are
            // supplied by the runtime; its element type is checked above.
            if (member.DeclaringType is ArrayType) return;
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
