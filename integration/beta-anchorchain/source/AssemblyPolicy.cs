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
    internal const string ExtendedHash = "63b02be22041bd505882f65254c7ea0a7d7ff995960121566fd79f52b4fdc599";
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
        // Both captured files declare the same plugin/assembly identity. Pick
        // the Workshop-named image before either duplicate enters the CLR.
        if (hash == SubAmmoDuplicateHash) {
            string canonical = Path.Combine(Path.GetDirectoryName(source), "SubAmmunitionMod.dll");
            if (File.Exists(canonical) && Hash(canonical) == SubAmmoHash) {
                log("SKIPPED duplicate before CLR load: SubAmmunitionMod.fixed.dll; canonical SubAmmunitionMod.dll is present and will receive the beta API adapter.");
                return null;
            }
        }
        // The crash capture proves this image blocks Unity ECS before a mission
        // can initialize. Do this BEFORE Assembly.LoadFile/GetExportedTypes.
        if (hash == ExtendedHash) {
            log("SKIPPED before CLR load: ExtendedGuidance 0.9.7; SensorDistanceData field layout blocks beta ECS initialization. Data files retained.");
            return null;
        }
        if (hash == "bcd193256a8078652bacb4a0055d713fc0e7b0c1fe0d76d5152acf733b937361" ||
            hash == "2349def7bf71a7df1f87b387645e4e146f66ba9bc6869a3e5001187a0a7ae98b") {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; captured beta patch failure with partial initialization. Awaiting a port.");
            return null;
        }
        using var resolver = new DefaultAssemblyResolver();
        foreach (var resolverDirectory in new[] { Path.GetDirectoryName(source), Path.GetDirectoryName(nativePath),
            Path.GetDirectoryName(typeof(HarmonyLib.Harmony).Assembly.Location),
            Path.GetDirectoryName(typeof(BetaAssemblyPolicy).Assembly.Location) })
            if (!String.IsNullOrEmpty(resolverDirectory)) resolver.AddSearchDirectory(resolverDirectory);
        using var module = ModuleDefinition.ReadModule(source, new ReaderParameters {
            InMemory = true, ReadingMode = ReadingMode.Deferred, AssemblyResolver = resolver });
        if (module.AssemblyReferences.Any(a => a.Name == "OspreyMechanics")) {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; depends on the captured, incompatible OspreyMechanics assembly.");
            return null;
        }
        // Libraries and native DLLs are not plugins. Let dependencies resolve in
        // their normal context instead of loading duplicate Harmony/Cecil copies.
        if (!Types(module.Types).Any(t => t.CustomAttributes.Any(a => a.AttributeType.FullName == "AnchorChain.ACPlugin"))) return null;
        nativePath = Path.GetFullPath(nativePath);
        if (!nativeModules.TryGetValue(nativePath, out var native)) {
            if (Hash(nativePath) != "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62")
                throw new InvalidDataException("Assembly adapters require the inspected beta Build 261026.");
            native = ModuleDefinition.ReadModule(nativePath, new ReaderParameters { InMemory = true });
            nativeModules[nativePath] = native;
        }
        var bad = InvalidNativeFields(module, native);
        if (bad.Count != 0) {
            log("SKIPPED before CLR load: " + Path.GetFileName(source) + "; " + String.Join("; ", bad.Take(4)));
            return null;
        }
        string audit = AdaptCapturedImage(module, native, hash);
        if (audit == null) return source;
        string directory = Path.Combine(cacheRoot, "beta-api-r3", hash);
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

}
