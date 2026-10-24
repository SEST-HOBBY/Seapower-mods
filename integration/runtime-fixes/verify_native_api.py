#!/usr/bin/env python3
"""Read-only ABI check against a player-exported Seapower-Scripts.dll.

Optional development check: python verify_native_api.py /path/to/assembly
Requires dnfile and dncil. Neither the assembly nor its decompiled code is
copied into the pack, and nothing in it is executed. The exact captured hash
is also checked at runtime (SestRuntimeFixes.cs, `inspected`).

Signatures are compared as decoded type names, not raw blobs: a blob embeds
TypeDef row numbers, which move whenever the game adds a type. Sea Power
0.8.7 inserted three, so ten 0.8.6 blobs changed while the API did not.

What was checked on which build. On 0.8.6 (c913e31f..., 20 Oct 2026): the
first 12 entries of METHODS, the three AmmunitionParameters/WeaponBase
fields, the 10 FlightStage names and the 0.405 lookahead, as raw blobs. On
0.8.7 (23 Oct 2026) each of those 12 has the same element types in the same
order as before and differs only in TypeDef indexes, consistent with three
inserted types (+1, +2, +3); what each 0.8.6 row named could not be checked
without the 0.8.6 DLL. Everything else here - the members only
TaskForceDebrief binds (IniHandler, the mission's _index, the roster item's
and row's properties, UnitRows), inheritance, parameter order, constructor
visibility, unique overloads, the property/field lookups, the sampler's
reach and the Harmony targets' bodies - was added on 23 Oct 2026 and checked
on 0.8.7 only, because the 0.8.6 DLL was not to hand.
"""
import argparse
import hashlib
from pathlib import Path
import sys
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes

EXPECTED = "eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd"
COMPARISON_086 = "c913e31f2d73e526f2d28043f522f2be26f12534fd0421eedee3cd70eab9cdd8"
OBJ, WPN, AP = "SeaPower.ObjectBase", "SeaPower.WeaponBase", "SeaPower.AmmunitionParameters"
TER, INI, MISSION = "SeaPower.TerrainUtils", "SeaPower.IniHandler", "SeaPower.LinearCampaignMission"
VM = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel"
SAVE = "SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager"
SNAP = "SeapowerUI.ViewModels.LinearCampaignTaskForceSnapshot"
ROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefUnitRow"
ROSTER = "SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem"
ROWS = "class System.Collections.Generic.IEnumerable`1<class %s>" % ROW
CTOR = "instance void(%s, bool, bool, valuetype SeaPower.ObjectBase+CrewSkill, int)" % ", ".join(["string"] * 6)
# (type, method) -> decoded signature; each must exist exactly once with these parameter types.
METHODS = {
    (OBJ, "get__geoPosition"): "instance valuetype SeaPower.GeoPosition()",
    (WPN, "get__flightStage"): "instance valuetype SeaPower.WeaponBase+FlightStage()",
    (TER, "GetSafeAltitudeOverSurface"): "static float(class %s, float, float, bool, bool)" % OBJ,
    (TER, "CrudeGetHighestTerrainHeightAhead"): "static float(valuetype SeaPower.GeoPosition, float, float, bool)",
    ("SeaPower.Utils", "heightInFeetToUnity"): "static float(float)",
    (SAVE, "ReadSnapshot"): "static class %s(class %s, string, string)" % (SNAP, INI),
    (SAVE, "MissionLaunchSection"): "static string(int)",
    (SAVE, "MissionLaunchUnitPrefix"): "static string(int)",
    (VM, "ReadUnitRows"): "instance void(class %s, class %s)" % (INI, MISSION),
    (VM, "SortDebriefUnitRows"): "static %s(%s)" % (ROWS, ROWS),
    (SNAP, "get_Items"): "instance class System.Collections.ObjectModel.ReadOnlyCollection`1<class %s>()" % ROSTER,
    (ROW, ".ctor"): CTOR,
    # Added 23 Oct 2026, checked on 0.8.7 only.
    (INI, "doesSectionExist"): "instance bool(string)",
    (INI, "readValue"): "instance bool(string, string, bool, bool)",
    (ROSTER, "get_InstanceId"): "instance string()",
    (ROSTER, "get_UnitType"): "instance string()",
    (ROSTER, "get_UnitFolder"): "instance string()",
    (ROSTER, "get_Category"): "instance string()",
    (ROSTER, "get_VariantReference"): "instance string()",
    (ROSTER, "get_CrewSkill"): "instance valuetype SeaPower.ObjectBase+CrewSkill()",
    (ROW, "get_InstanceId"): "instance string()",
    (VM, "get_UnitRows"): "instance class System.Collections.ObjectModel.ObservableCollection`1<class %s>()" % ROW,
}
# Added 24 October. Campaign debrief bindings also match the repository's
# 0.8.7 review. New inventory/F11 bindings are compared against the available
# 0.8.6 capture; a fresh 0.8.7 run and PC acceptance remain required. Comparison
# mode never changes the DLL's runtime hash allowlist.
SUMROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefSummaryRow"
SNAPROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterSnapshotRow"
RULES = "SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules"
REPORT, AMMO = "SeaPower.TaskforceWeaponReport", "SeaPower.WeaponReportAmmoData"
TF, REG, OBP, DECK = "SeaPower.Taskforce", "SeaPower.UnitRegister", "SeaPower.ObjectBaseParameters", "SeaPower.FlightDeck"
METHODS.update({
    (VM,"Load"): "instance void(class SeaPower.LinearCampaignMission)",
    (VM,"HasDebriefSnapshot"): "static bool(class SeaPower.IniHandler, int)",
    (VM,"GetDebriefSectionName"): "static string(int)",
    (VM,"TryParseRegisterRows"): "static bool(string, ref class System.Collections.Generic.List`1<valuetype %s>)" % SNAPROW,
    (VM,"TryReadWeaponReports"): "static bool(class SeaPower.IniHandler, int, ref class %s, ref class %s, ref class %s)" % (REPORT,REPORT,REPORT),
    (VM,"SaveDebriefSnapshot"): "static void(class SeaPower.LinearCampaignMission, class SeapowerUI.ViewModels.MissionDebriefViewModel)",
    (VM,"get_SummaryRows"): "instance class System.Collections.ObjectModel.ObservableCollection`1<class %s>()" % SUMROW,
    (SUMROW,".ctor"): "instance void(string, string, bool, bool)",
    (RULES,"OpenCampaignStateIni"): "static class SeaPower.IniHandler()",
    (INI,"get_Data"): "instance class System.Collections.Generic.Dictionary`2<string, class System.Collections.Generic.Dictionary`2<string, string>>()",
    (INI,"writeValue"): "instance void(string, string, string)",
    (INI,"saveFile"): "instance void(bool)",
    (REPORT,"BuildTaskforceTotals"): "instance class System.Collections.Generic.Dictionary`2<string, class %s>()" % AMMO,
    (AMMO,"get_AmmoRef"): "instance string()",
    (AMMO,"get_AmmoType"): "instance valuetype SeaPower.Ammunition+Type()",
    (AMMO,"get_Launched"): "instance int()",
    (AMMO,"get_ProjectileFired"): "instance int()",
    ("SeaPower.Utils","openVirtualIniFile"): "static class SeaPower.IniHandler(string, string, string, bool)",
    ("SeaPower.Utils","openIniFile"): "static class SeaPower.IniHandler(string, string, bool, bool)",
    (TF,"RegisterUnitStatus"): "instance void(bool, class SeaPower.ObjectBase, bool, bool)",
    ("SeaPower.SaveLoadManager","WriteTaskforceAarData"): "static void(class SeaPower.IniHandler, class SeaPower.Taskforce, string)",
    ("SeaPower.SaveLoadManager","LoadTaskforceAarData"): "static void(class SeaPower.IniHandler, class SeaPower.Taskforce, string)",
    (OBJ,"get_AmmunitionAmountDictionary"): "instance class UniRx.ReactiveDictionary`2<string, int>()",
    (REG,"get_IniRef"): "instance string()", (REG,"get_IniFolder"): "instance string()",
    (REG,"get_ObjectType"): "instance valuetype SeaPower.ObjectBase+ObjectType()",
    (REG,"get_Count"): "instance int()", (REG,"get_IsDestroyed"): "instance bool()",
    (INI,"getFilePath"): "instance string()",
    (RULES,"OpenCampaignIni"): "static class SeaPower.IniHandler()",
    (RULES,"IsTaskForceModeEnabled"): "static bool(class SeaPower.IniHandler)",
    ("SeaPower.GameMain","OnDestroy"): "instance void()",
    ("SeaPower.GameMain","Update"): "instance void()",
    # Added 24 Oct 2026, checked on 0.8.7: copying the debrief section into the .sav
    # again once SEST's keys are in it, and naming the campaign by its .sav.
    (VM,"PersistDebriefSectionsToCurrentCampaignSave"): "static void(class SeaPower.IniHandler, int)",
    ("SeaPower.SaveLoadManager","GetGlobalCampaignSaveFilePath"): "static string()",
})
OVERLOADS = [(INI,"readValue","instance string(string, string, string, bool)")]
# Instance members read through GetField/GetProperty (exact name) or, for the names in
# IGNORE_CASE, Expression.PropertyOrField: each must be the only member of that name.
FIELDS = {(AP, "_ammunitionFileName"): "string", (AP, "_terrainFollowFlight"): "bool",
          (WPN, "_ap"): "class " + AP, (MISSION, "_index"): "int"}
PROPERTIES = {(OBJ, "_geoPosition"): "valuetype SeaPower.GeoPosition",
              (WPN, "_flightStage"): "valuetype SeaPower.WeaponBase+FlightStage",
              (SNAP, "Items"): METHODS[SNAP, "get_Items"][len("instance "):-2],
              (VM, "UnitRows"): METHODS[VM, "get_UnitRows"][len("instance "):-2],
              (ROSTER, "CrewSkill"): "valuetype SeaPower.ObjectBase+CrewSkill", (ROW, "InstanceId"): "string"}
PROPERTIES.update({(ROSTER, n): "string" for n in ("InstanceId", "UnitType", "UnitFolder", "Category", "VariantReference")})
FIELDS.update({
    (OBJ,"_type"): "valuetype SeaPower.ObjectBase+ObjectType", (OBJ,"_obp"): "class " + OBP,
    (OBP,"_objectIniName"): "string", (OBP,"_flightDeck"): "class " + DECK,
    (DECK,"_currentAmmo"): "float", (DECK,"_accountableAmmunition"): "class System.Collections.Generic.Dictionary`2<string, int>",
    (TF,"_unitStatusRegister"): "class System.Collections.Generic.List`1<class SeaPower.UnitRegister>",
    (TF,"_weaponsSpent"): "class System.Collections.Generic.Dictionary`2<string, class SeaPower.WeaponsSpent>",
    ("SeaPower.WeaponsSpent","_number"): "int",
    **{(SNAPROW,n): t for n,t in (("IniRef","string"),("Folder","string"),("ObjectType","string"),("Count","int"),("IsDestroyed","bool"))},
})
STATIC_FIELDS = {("SeaPower.Globals",n): "class " + TF for n in ("_playerTaskforce","_enemyTaskforce","_neutralTaskforce")}
STATIC_FIELDS["SeaPower.Globals","currentMissionFilePath"] = "string"
PROPERTIES.update({
    (VM,"SummaryRows"): METHODS[VM,"get_SummaryRows"][len("instance "):-2],
    (INI,"Data"): METHODS[INI,"get_Data"][len("instance "):-2],
    (OBJ,"AmmunitionAmountDictionary"): "class UniRx.ReactiveDictionary`2<string, int>",
    (REG,"IniRef"): "string",(REG,"IniFolder"): "string",(REG,"Count"): "int",(REG,"IsDestroyed"): "bool",
    (REG,"ObjectType"): "valuetype SeaPower.ObjectBase+ObjectType",
    (AMMO,"AmmoRef"): "string",(AMMO,"AmmoType"): "valuetype SeaPower.Ammunition+Type",
    (AMMO,"Launched"): "int",(AMMO,"ProjectileFired"): "int",
})
IGNORE_CASE = {"_ammunitionFileName", "_terrainFollowFlight", "_ap", "_geoPosition", "_flightStage"}
# Harmony's __N and the row constructor's arguments are positional: same-typed neighbours must not swap.
PARAMETERS = {
    (TER, "GetSafeAltitudeOverSurface"): "objBase targetAltitude minAltOverSea cantStayAtAltitude isWeapon",
    (TER, "CrudeGetHighestTerrainHeightAhead"): "geoPosition heading distanceLimit isCalledFromJob",
    (INI, "readValue"): "sectionName key defaultValue performLogging",
    (ROW, ".ctor"): "instanceId iniRef iniFolder category variantReference damageState isDestroyed isFlagship crewSkill quantity",
}
PARAMETERS.update({
    (VM,"TryReadWeaponReports"): "campaignStateIni missionIndex playerReport enemyReport neutralReport",
    (VM,"TryParseRegisterRows"): "rawValue rows", (VM,"SaveDebriefSnapshot"): "mission debrief",
    (SUMROW,".ctor"): "label value isPositive isNegative",
    (INI,"writeValue"): "sectionName key value", (INI,"saveFile"): "overwrite",
    ("SeaPower.Utils","openVirtualIniFile"): "basePath fileName folderName checkCached",
    ("SeaPower.Utils","openIniFile"): "rootPath name logErrors useCaching",
    (TF,"RegisterUnitStatus"): "useTmpList tfObject destroyed damaged",
    ("SeaPower.SaveLoadManager","WriteTaskforceAarData"): "ini taskforce sectionName",
    ("SeaPower.SaveLoadManager","LoadTaskforceAarData"): "missionIni taskforce sectionName",
})
STAGES = ("ToBearing", "MaintainHeight", "MoveToLoftAlt", "MaintainLoftAlt", "MoveToSeaSkimming",
          "MaintainSeaSkimming", "MoveToFinalFlightAlt", "MaintainFinalFlightAlt", "AlignSensorToTarget", "TerminalApproach")
LOOKAHEAD_NM = 1.10  # Policy.LookAheadNm
PRIMITIVES = {0x01: "void", 0x02: "bool", 0x03: "char", 0x04: "sbyte", 0x05: "byte", 0x06: "short", 0x07: "ushort",
              0x08: "int", 0x09: "uint", 0x0a: "long", 0x0b: "ulong", 0x0c: "float", 0x0d: "double", 0x0e: "string",
              0x16: "TypedReference", 0x18: "IntPtr", 0x19: "UIntPtr", 0x1c: "object"}


def unsigned(blob, i):
    b = blob[i]
    if b & 0x80 == 0:
        return b, i + 1
    if b & 0xc0 == 0x80:
        return (b & 0x3f) << 8 | blob[i + 1], i + 2
    return (b & 0x1f) << 24 | blob[i + 1] << 16 | blob[i + 2] << 8 | blob[i + 3], i + 4


class Assembly:
    def __init__(self, path):
        self.pe = dnfile.dnPE(str(path))
        t = self.tables = self.pe.net.mdtables
        enclosing = {r.NestedClass.row_index: r.EnclosingClass.row_index for r in (t.NestedClass or [])}

        def name(i):
            row = t.TypeDef[i - 1]
            if i in enclosing:
                return name(enclosing[i]) + "+" + str(row.TypeName)
            return ".".join(n for n in (str(row.TypeNamespace or ""), str(row.TypeName)) if n)
        self.names = {i: name(i) for i in range(1, len(t.TypeDef) + 1)}
        self.types = {}
        for i, n in self.names.items():
            self.types.setdefault(n, []).append(i)
        self.properties = {}
        for pm in (t.PropertyMap or []):
            self.properties.setdefault(pm.Parent.row_index, []).extend(p.row for p in pm.PropertyList)

    def typedef(self, name):
        found = self.types.get(name, [])
        assert len(found) == 1, ("type defined %d times" % len(found), name)
        return self.tables.TypeDef[found[0] - 1]

    def token(self, table, row):
        if table == "TypeDef":
            return self.names[row]
        if table == "TypeRef":
            ref = self.tables.TypeRef[row - 1]
            scope = ref.ResolutionScope
            if scope.table is not None and scope.table.name == "TypeRef":
                return self.token("TypeRef", scope.row_index) + "+" + str(ref.TypeName)
            return ".".join(n for n in (str(ref.TypeNamespace or ""), str(ref.TypeName)) if n)
        return self.type(self.tables.TypeSpec[row - 1].Signature.value, 0)[0]

    def coded(self, blob, i):
        value, i = unsigned(blob, i)
        return self.token(("TypeDef", "TypeRef", "TypeSpec")[value & 3], value >> 2), i

    def type(self, blob, i):
        e = blob[i]
        i += 1
        if e in PRIMITIVES:
            return PRIMITIVES[e], i
        if e in (0x11, 0x12):
            name, i = self.coded(blob, i)
            return ("valuetype " if e == 0x11 else "class ") + name, i
        if e in (0x0f, 0x10, 0x1d, 0x45):
            inner, i = self.type(blob, i)
            return {0x0f: inner + "*", 0x10: "ref " + inner, 0x1d: inner + "[]", 0x45: "pinned " + inner}[e], i
        if e in (0x13, 0x1e):
            n, i = unsigned(blob, i)
            return ("!" if e == 0x13 else "!!") + str(n), i
        if e in (0x1f, 0x20):
            _, i = self.coded(blob, i)
            return self.type(blob, i)
        if e == 0x15:
            kind = blob[i]
            name, i = self.coded(blob, i + 1)
            count, i = unsigned(blob, i)
            args = []
            for _ in range(count):
                arg, i = self.type(blob, i)
                args.append(arg)
            return ("valuetype " if kind == 0x11 else "class ") + name + "<" + ", ".join(args) + ">", i
        raise ValueError("unsupported element type 0x%02x" % e)

    def method(self, row):
        """'static|instance return(param, ...)' and the parameter list."""
        blob = row.Signature.value
        i = 1
        if blob[0] & 0x10:
            _, i = unsigned(blob, i)
        count, i = unsigned(blob, i)
        returns, i = self.type(blob, i)
        params = []
        for _ in range(count):
            p, i = self.type(blob, i)
            params.append(p)
        generic = "<generic> " if blob[0] & 0x10 else ""
        return generic + ("instance " if blob[0] & 0x20 else "static ") + returns + "(" + ", ".join(params) + ")", params

    def chain(self, name):
        names = [name]
        while len(self.types.get(names[-1], [])) == 1:
            base = self.typedef(names[-1]).Extends
            if base is None or base.table is None or base.row_index == 0:
                break
            names.append(self.token(base.table.name, base.row_index).split("<")[0])
        return names

    def members(self, name, member, ignore_case=True):
        """Instance properties and fields named `member` in the game-assembly hierarchy of `name`."""
        same = (lambda n: n.lower() == member.lower()) if ignore_case else (lambda n: n == member)
        found = []
        for owner in self.chain(name):
            if len(self.types.get(owner, [])) != 1:
                break
            index = self.types[owner][0]
            for prop in self.properties.get(index, []):
                if same(str(prop.Name)):
                    blob = prop.Type.value
                    found.append(("property", owner, str(prop.Name), self.type(blob, unsigned(blob, 1)[1])[0]))
            for field in self.tables.TypeDef[index - 1].FieldList:
                if same(str(field.row.Name)) and not field.row.Flags.fdStatic:
                    found.append(("field", owner, str(field.row.Name), self.type(field.row.Signature.value, 1)[0]))
        return found


def main():
    if sys.flags.optimize:
        sys.exit("verify_native_api.py checks with assert: run it without -O or PYTHONOPTIMIZE")
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assembly",type=Path)
    parser.add_argument("--comparison-086",action="store_true",help="structural comparison only on the known 0.8.6 capture; does not authorize runtime loading")
    args=parser.parse_args()
    path=args.assembly
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == (COMPARISON_086 if args.comparison_086 else EXPECTED), "uninspected native build"
    game = Assembly(path)
    bound = {}
    for owner,name,expected in [(o,n,s) for (o,n),s in METHODS.items()] + OVERLOADS:
        rows = [m.row for m in game.typedef(owner).MethodList if str(m.row.Name) == name]
        params = expected[expected.index("(") + 1:-1].split(", ") if not expected.endswith("()") else []
        exact = [row for row in rows if game.method(row)[1] == params]
        assert len(exact) == 1 and game.method(exact[0])[0] == expected, (owner, name, [game.method(r)[0] for r in rows])
        bound[owner, name] = exact[0]
    assert bound[ROW, ".ctor"].Flags.mdPublic, "row constructor must be public (GetConstructor)"
    assert bound[SUMROW,".ctor"].Flags.mdPublic, "GetConstructor requires a public summary constructor"
    for (owner, name), names in PARAMETERS.items():
        got = " ".join(str(p.row.Name) for p in bound[owner, name].ParamList if p.row.Sequence > 0)
        assert got == names, (owner, name, got)
    for kind, table in (("field", FIELDS), ("property", PROPERTIES)):
        for (owner, name), expected in table.items():
            found = game.members(owner, name, name in IGNORE_CASE)
            assert found == [(kind, owner, name, expected)], (owner, name, found)
    for (owner,name),expected in STATIC_FIELDS.items():
        rows=[f.row for f in game.typedef(owner).FieldList if str(f.row.Name)==name]
        assert len(rows)==1 and rows[0].Flags.fdStatic and game.type(rows[0].Signature.value,1)[0]==expected,(owner,name)
    for owner,names in {"SeaPower.Ammunition+Type": "Missile ASROC RBU AirDepthCharge Torpedo Bomb Projectile AerialRocket MLRS", "SeaPower.ObjectBase+ObjectType": "Vessel Submarine Aircraft Helicopter LandUnit"}.items():
        actual={str(f.row.Name) for f in game.typedef(owner).FieldList if f.row.Flags.fdStatic}
        assert set(names.split()) <= actual,(owner,actual)
    assert WPN in game.chain("SeaPower.Missile") and OBJ in game.chain(WPN), "Missile : WeaponBase : ObjectBase"
    assert "UnityEngine.MonoBehaviour" in game.chain(OBJ) and not game.members(OBJ, "transform"), "ObjectBase.transform"
    stage = game.typedef("SeaPower.WeaponBase+FlightStage")
    assert game.token(stage.Extends.table.name, stage.Extends.row_index) == "System.Enum", "FlightStage is an enum"
    enums = {str(f.row.Name) for f in stage.FieldList if f.row.Flags.fdStatic}
    for name in STAGES:
        assert name in enums, name

    def literals(key):
        row = bound[key]
        assert row.Rva and row.ImplFlags.miIL, (key, "no IL body")
        body = CilMethodBody(CilMethodBodyReaderBytes(game.pe.get_data(row.Rva)))
        return [i.operand for i in body.instructions if str(i.opcode) == "ldc.r4"]
    assert any(abs(n - .405) < .00001 for n in literals((TER, "GetSafeAltitudeOverSurface"))), \
        "native weapon lookahead assumption changed"
    reach = max(literals((TER, "CrudeGetHighestTerrainHeightAhead")))
    assert 1.0 < reach <= LOOKAHEAD_NM, ("native sampler reach no longer inside Policy.LookAheadNm", reach)
    literals((VM, "ReadUnitRows"))
    label="0.8.6 structural comparison only" if args.comparison_086 else "0.8.7 ABI"
    print("Native %s verified: captured hash, %d method signatures with %d parameter orders, %d fields, "
          "%d properties, 10 cruise/terminal enum names, inheritance, native lookahead and sampler reach (%.2f nm)"
          % (label,len(METHODS)+len(OVERLOADS), len(PARAMETERS), len(FIELDS)+len(STATIC_FIELDS), len(PROPERTIES), reach))
    print("No game code executed. External Unity members and Harmony installation still require PC acceptance.")
    if args.comparison_086: print("This is NOT a 0.8.7 verification. The plugin remains restricted to the previously reviewed 0.8.7 hash.")


if __name__ == "__main__":
    main()
