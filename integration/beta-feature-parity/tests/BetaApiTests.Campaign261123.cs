using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AnchorChain;
using Mono.Cecil;
using Mono.Cecil.Cil;

static partial class BetaApiTests
{
    // Dynamic Campaign Mod 1.0.2 (18a2416e) on 0.9.3-261123: the private
    // image names none of the six members 261123 removed, every bridge sits
    // at its inspected site, and the image loads.
    static void R6_Campaign261123(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3813157776", "DynamicCampaignMod.dll");
        byte[] original = File.ReadAllBytes(source);
        string hash; using (var sha = System.Security.Cryptography.SHA256.Create()) hash = BitConverter.ToString(sha.ComputeHash(original)).Replace("-", "").ToLowerInvariant();
        Check(hash == "18a2416e6dd51bd574a5012405b088442b4ef84f54028c73cd7b396429be9929", "Campaign fixture is the inspected Dynamic Campaign Mod 1.0.2 image");
        var messages = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        Check(prepared != null && prepared != source && File.Exists(prepared), "Dynamic Campaign Mod 1.0.2 is admitted through its 261123 adapter");
        Check(original.SequenceEqual(File.ReadAllBytes(source)), "Original campaign DLL retained byte for byte");
        var adapted = messages.Where(m => m.Contains("ADAPTED DynamicCampaignMod")).ToList();
        Check(adapted.Count == 1 && adapted[0].Contains((string)typeof(BetaAssemblyPolicy).GetField("Campaign261123Audit", BindingFlags.NonPublic | BindingFlags.Static).GetValue(null)), "Campaign audit is the inspected 261123 audit: " + string.Join(" | ", messages));
        if (prepared == null || prepared == source) return;
        string[] gone = { "SeaPower.CampaignMain::GetVisualPostureAndColour", "SeapowerUI.ViewModels.GroupOfUnits::set_UnitColorBrush",
            "SeapowerUI.ViewModels.GroupOfUnits::get_UnitColorBrush", "SeapowerUI.ViewModels.MapDrawingLayer::.ctor()",
            "MapControl.MapTileLayer", "Seapower.SceneEditor.Scheduler",
            "MapControl.MapTerrainBackground::.ctor(SeaPower.LiveMap.MapPalette,SeaPower.LiveMap.MapTerrainEdits)" };
        var sites = new Dictionary<string, int>();
        using (var after = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var names = new List<string>();
            names.AddRange(after.GetTypeReferences().Select(t => t.FullName));
            names.AddRange(after.GetMemberReferences().Select(m => m.FullName));
            foreach (var t in Types(after.Types)) foreach (var m in t.Methods.Where(x => x.HasBody)) {
                names.AddRange(m.Body.Variables.Select(v => v.VariableType.FullName));
                foreach (var i in m.Body.Instructions) {
                    if (i.Operand is MemberReference r) names.Add(r.FullName);
                    if (i.Operand is MethodReference c && c.DeclaringType.FullName == "AnchorChain.BetaCompatibilityCalls")
                        sites[c.Name] = sites.TryGetValue(c.Name, out int n) ? n + 1 : 1;
                }
            }
            foreach (var g in gone)
                Check(!names.Any(n => n.Replace(" ", "").Contains(g.Replace(" ", ""))), "The 261123 image no longer names " + g);
        }
        int Site(string name) => sites.TryGetValue(name, out int n) ? n : 0;
        Check(Site("CampaignSideLook") == 8, "Side colour bridged at its 8 inspected sites");
        Check(Site("CampaignGroupBrush") == 2, "Group brush bridged at its 2 inspected sites");
        Check(Site("NewCampaignDrawingLayer") == 1, "Drawing layer bridged at its one site");
        Check(Site("CampaignFlatTileLayer") == 2, "Flat-tile lookup bridged at its 2 sites");
        Check(Site("CampaignGlobeToDispose") == 1, "Globe failure guard at its one site");
        var assembly = Assembly.LoadFile(prepared);
        Check(assembly.GetTypes().Length > 100, "Adapted Dynamic Campaign Mod completes CLR type discovery on 261123");
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "Campaign original asset provenance retained");
    }
}
