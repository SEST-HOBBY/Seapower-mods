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

The campaign combat costs (CampaignCosts.cs, 24 Oct 2026, checked on 0.8.7
only) add the debrief's Load target, its snapshot, row-parser and
weapon-report members, the summary-row constructor, the weapon-report
totals, IniHandler's Data, doesKeyExist and string readValue, the two Utils
INI openers, the snapshot row's fields and the enum names the plugin
requires; INSPECTED holds members it only relies on, whose bodies are read:
the section names, Clear before the summary rows, the blank "fired nothing"
report, ignored fuel tanks, CIWS bursts counted as projectiles and the
case-insensitive weapon totals.
"""
import hashlib
from pathlib import Path
import sys
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes

EXPECTED = "eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd"
OBJ, WPN, AP = "SeaPower.ObjectBase", "SeaPower.WeaponBase", "SeaPower.AmmunitionParameters"
TER, INI, MISSION = "SeaPower.TerrainUtils", "SeaPower.IniHandler", "SeaPower.LinearCampaignMission"
VM = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel"
SAVE = "SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager"
SNAP = "SeapowerUI.ViewModels.LinearCampaignTaskForceSnapshot"
ROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefUnitRow"
ROSTER = "SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem"
ROWS = "class System.Collections.Generic.IEnumerable`1<class %s>" % ROW
CTOR = "instance void(%s, bool, bool, valuetype SeaPower.ObjectBase+CrewSkill, int)" % ", ".join(["string"] * 6)
SUMROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefSummaryRow"
SNAPROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterSnapshotRow"
RULES = "SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules"
TWR, AMMO, UTILS = "SeaPower.TaskforceWeaponReport", "SeaPower.WeaponReportAmmoData", "SeaPower.Utils"
EXT = "SeaPower.TaskforceWeaponReportExtensions"
DATA = "class System.Collections.Generic.Dictionary`2<string, class System.Collections.Generic.Dictionary`2<string, string>>"
SUMROWS = "class System.Collections.ObjectModel.ObservableCollection`1<class %s>" % SUMROW
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
    # Campaign combat costs (CampaignCosts.cs), added 24 Oct 2026, checked on 0.8.7 only.
    (VM, "Load"): "instance void(class %s)" % MISSION,
    (VM, "get_SummaryRows"): "instance %s()" % SUMROWS,
    (VM, "HasDebriefSnapshot"): "static bool(class %s, int)" % INI,
    (VM, "GetDebriefSectionName"): "static string(int)",
    (VM, "TryParseRegisterRows"): "static bool(string, ref class System.Collections.Generic.List`1<valuetype %s>)" % SNAPROW,
    (VM, "TryReadWeaponReports"): "static bool(class %s, int, %s)" % (INI, ", ".join(["ref class " + TWR] * 3)),
    (SUMROW, ".ctor"): "instance void(string, string, bool, bool)",
    (RULES, "OpenCampaignStateIni"): "static class %s()" % INI,
    (TWR, "BuildTaskforceTotals"): "instance class System.Collections.Generic.Dictionary`2<string, class %s>()" % AMMO,
    (AMMO, "get_AmmoRef"): "instance string()",
    (AMMO, "get_AmmoType"): "instance valuetype SeaPower.Ammunition+Type()",
    (AMMO, "get_Launched"): "instance int()",
    (AMMO, "get_ProjectileFired"): "instance int()",
    (INI, "get_Data"): "instance %s()" % DATA,
    (INI, "doesKeyExist"): "instance bool(string, string)",
    (UTILS, "openVirtualIniFile"): "static class %s(string, string, string, bool)" % INI,
    (UTILS, "openIniFile"): "static class %s(string, string, bool, bool)" % INI,
}
# METHODS is keyed by (type, name): a second overload of a bound name is checked here the same way.
OVERLOADS = [(INI, "readValue", "instance string(string, string, string, bool)", "sectionName key defaultValue performLogging")]
# Not bound, but CampaignCosts.cs relies on what their bodies do (checked below): exact signatures.
INSPECTED = {
    (VM, "Clear"): "instance void()",
    (VM, "ReadRegisterRows"): "instance void(class %s, int, string, class System.Collections.ObjectModel."
                              "ObservableCollection`1<class SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterRow>)" % INI,
    (VM, "WriteRegisterRows"): "static void(class %s, int, string, class System.Collections.Generic.IEnumerable`1<class "
                               "SeaPower.UnitRegister>)" % INI,
    (VM, "SaveDebriefSnapshot"): "static void(class %s, class SeapowerUI.ViewModels.MissionDebriefViewModel)" % MISSION,
    (VM, "WriteWeaponReport"): "static void(class %s, int, string, class %s)" % (INI, TWR),
    (VM, "ReadWeaponReport"): "static class %s(class %s, string, string)" % (TWR, INI),
    (EXT, "IsIgnoredAmmo"): "static bool(valuetype SeaPower.Ammunition+Type, valuetype SeaPower.Ammunition+Type)",
    (EXT, "RecordCiwsRoundsFired"): "static void(class SeaPower.Taskforce, class SeaPower.WeaponSystemCIWS, int)",
}
# Instance members read through GetField/GetProperty (exact name) or, for the names in
# IGNORE_CASE, Expression.PropertyOrField: each must be the only member of that name.
FIELDS = {(AP, "_ammunitionFileName"): "string", (AP, "_terrainFollowFlight"): "bool",
          (WPN, "_ap"): "class " + AP, (MISSION, "_index"): "int",
          (SNAPROW, "IniRef"): "string", (SNAPROW, "Folder"): "string", (SNAPROW, "ObjectType"): "string",
          (SNAPROW, "Count"): "int", (SNAPROW, "IsDestroyed"): "bool"}
PROPERTIES = {(OBJ, "_geoPosition"): "valuetype SeaPower.GeoPosition",
              (WPN, "_flightStage"): "valuetype SeaPower.WeaponBase+FlightStage",
              (SNAP, "Items"): METHODS[SNAP, "get_Items"][len("instance "):-2],
              (VM, "UnitRows"): METHODS[VM, "get_UnitRows"][len("instance "):-2],
              (ROSTER, "CrewSkill"): "valuetype SeaPower.ObjectBase+CrewSkill", (ROW, "InstanceId"): "string"}
PROPERTIES.update({(ROSTER, n): "string" for n in ("InstanceId", "UnitType", "UnitFolder", "Category", "VariantReference")})
PROPERTIES.update({(VM, "SummaryRows"): SUMROWS, (AMMO, "AmmoRef"): "string",
                   (AMMO, "AmmoType"): "valuetype SeaPower.Ammunition+Type", (AMMO, "Launched"): "int",
                   (AMMO, "ProjectileFired"): "int"})
IGNORE_CASE = {"_ammunitionFileName", "_terrainFollowFlight", "_ap", "_geoPosition", "_flightStage"}
# Harmony's __N and the row constructor's arguments are positional: same-typed neighbours must not swap.
PARAMETERS = {
    (TER, "GetSafeAltitudeOverSurface"): "objBase targetAltitude minAltOverSea cantStayAtAltitude isWeapon",
    (TER, "CrudeGetHighestTerrainHeightAhead"): "geoPosition heading distanceLimit isCalledFromJob",
    (INI, "readValue"): "sectionName key defaultValue performLogging",
    (ROW, ".ctor"): "instanceId iniRef iniFolder category variantReference damageState isDestroyed isFlagship crewSkill quantity",
    (VM, "HasDebriefSnapshot"): "campaignStateIni missionIndex",
    (VM, "TryReadWeaponReports"): "campaignStateIni missionIndex playerReport enemyReport neutralReport",
    (SUMROW, ".ctor"): "label value isPositive isNegative",
    (INI, "doesKeyExist"): "sectionName key",
    (UTILS, "openVirtualIniFile"): "basePath fileName folderName checkCached",
    (UTILS, "openIniFile"): "rootPath name logErrors useCaching",
}
STAGES = ("ToBearing", "MaintainHeight", "MoveToLoftAlt", "MaintainLoftAlt", "MoveToSeaSkimming",
          "MaintainSeaSkimming", "MoveToFinalFlightAlt", "MaintainFinalFlightAlt", "AlignSensorToTarget", "TerminalApproach")
LOOKAHEAD_NM = 1.10  # Policy.LookAheadNm
# CostPolicy.CountedTypes and PricedObjects: Bind throws unless the game defines them.
AMMO_TYPES = ("Missile", "ASROC", "RBU", "AirDepthCharge", "Torpedo", "Bomb", "Projectile", "AerialRocket", "MLRS")
OBJECT_TYPES = ("Vessel", "Submarine", "Aircraft", "Helicopter")
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

    def member(self, token):
        """'Owner::Name' for a MethodDef, Field, MemberRef or MethodSpec token (call, ldftn, ldsfld operands)."""
        table, rid = token >> 24, token & 0xFFFFFF
        if not hasattr(self, "owners"):
            self.owners = {}
            for i in range(1, len(self.tables.TypeDef) + 1):
                td = self.tables.TypeDef[i - 1]
                self.owners.update({("MethodDef", m.row_index): i for m in td.MethodList})
                self.owners.update({("Field", f.row_index): i for f in td.FieldList})
        if table in (0x06, 0x04):
            kind = "MethodDef" if table == 0x06 else "Field"
            return self.names[self.owners[kind, rid]] + "::" + str(getattr(self.tables, kind)[rid - 1].Name)
        if table == 0x0A:
            row = self.tables.MemberRef[rid - 1]
            parent = row.Class
            owner = self.token(parent.table.name, parent.row_index) if parent.table.name in ("TypeDef", "TypeRef", "TypeSpec") \
                else parent.table.name
            return owner + "::" + str(row.Name)
        if table == 0x2B:
            method = self.tables.MethodSpec[rid - 1].Method
            return self.member((0x06 if method.table.name == "MethodDef" else 0x0A) << 24 | method.row_index)
        return "token %08x" % token

    def enum(self, name):
        """{member: value} of an enum's literal fields."""
        values = {}
        for c in self.tables.Constant or []:
            if c.Parent.table is not None and c.Parent.table.name == "Field":
                values[c.Parent.row_index] = int.from_bytes(c.Value.value, "little", signed=True)
        return {str(f.row.Name): values.get(f.row_index) for f in self.typedef(name).FieldList if f.row.Flags.fdStatic}

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
    path = Path(sys.argv[1])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED, "uninspected native build"
    game = Assembly(path)
    bound = {}
    for (owner, name), expected in METHODS.items():
        rows = [m.row for m in game.typedef(owner).MethodList if str(m.row.Name) == name]
        params = expected[expected.index("(") + 1:-1].split(", ") if not expected.endswith("()") else []
        exact = [row for row in rows if game.method(row)[1] == params]
        assert len(exact) == 1 and game.method(exact[0])[0] == expected, (owner, name, [game.method(r)[0] for r in rows])
        bound[owner, name] = exact[0]
    for owner, name, expected, names in OVERLOADS:
        rows = [m.row for m in game.typedef(owner).MethodList if str(m.row.Name) == name]
        exact = [row for row in rows if game.method(row)[0] == expected]
        assert len(exact) == 1, (owner, name, expected)
        got = " ".join(str(p.row.Name) for p in exact[0].ParamList if p.row.Sequence > 0)
        assert got == names, (owner, name, got)
    inspected = {}
    for (owner, name), expected in INSPECTED.items():
        rows = [m.row for m in game.typedef(owner).MethodList if str(m.row.Name) == name]
        assert len(rows) == 1 and game.method(rows[0])[0] == expected, (owner, name, [game.method(r)[0] for r in rows])
        inspected[owner, name] = rows[0]
    assert bound[ROW, ".ctor"].Flags.mdPublic, "row constructor must be public (GetConstructor)"
    assert bound[SUMROW, ".ctor"].Flags.mdPublic, "summary-row constructor must be public (GetConstructor)"
    assert game.token(game.typedef(SNAPROW).Extends.table.name, game.typedef(SNAPROW).Extends.row_index) == "System.ValueType", \
        "the snapshot row is a struct (List<row> by ref)"
    for (owner, name), names in PARAMETERS.items():
        got = " ".join(str(p.row.Name) for p in bound[owner, name].ParamList if p.row.Sequence > 0)
        assert got == names, (owner, name, got)
    for kind, table in (("field", FIELDS), ("property", PROPERTIES)):
        for (owner, name), expected in table.items():
            found = game.members(owner, name, name in IGNORE_CASE)
            assert found == [(kind, owner, name, expected)], (owner, name, found)
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

    # Campaign combat costs: what CampaignCosts.cs relies on in these bodies.
    for type_name, names in (("SeaPower.Ammunition+Type", AMMO_TYPES), ("SeaPower.ObjectBase+ObjectType", OBJECT_TYPES)):
        enum = game.typedef(type_name)
        assert game.token(enum.Extends.table.name, enum.Extends.row_index) == "System.Enum", type_name
        values = game.enum(type_name)
        for name in names:
            assert name in values, (type_name, name)
    assert game.enum("SeaPower.Ammunition+Type")["Fueltank"] == 16, "Fueltank is 16 (IsIgnoredAmmo)"

    def code(key):
        row = bound[key] if key in bound else inspected[key]
        assert row.Rva and row.ImplFlags.miIL, (key, "no IL body")
        out = []
        for i in CilMethodBody(CilMethodBodyReaderBytes(game.pe.get_data(row.Rva))).instructions:
            op, operand = str(i.opcode), i.operand
            if op == "ldstr":
                operand = game.pe.net.user_strings.get(operand.value & 0xFFFFFF).value
            elif op in ("call", "callvirt", "newobj", "ldftn", "ldsfld", "ldfld", "stfld"):
                operand = game.member(operand.value)
            out.append((op, operand))
        return out

    def strings(key):
        return [operand for op, operand in code(key) if op == "ldstr"]

    def calls(key):
        return [operand for op, operand in code(key) if op in ("call", "callvirt", "newobj", "ldftn")]

    for key, wanted in (((VM, "GetDebriefSectionName"), ("Mission_", "_TaskForceDebrief")),
                        ((VM, "ReadRegisterRows"), ("Rows",)), ((VM, "WriteRegisterRows"), ("Rows",)),
                        ((VM, "Load"), ("Kill", "Loss")), ((VM, "SaveDebriefSnapshot"), ("Kill", "Loss")),
                        ((VM, "TryReadWeaponReports"), ("PlayerWeaponReport", "EnemyWeaponReport"))):
        for text in wanted:
            assert text in strings(key), (key, text)
    load = calls((VM, "Load"))
    first_rows = next(i for i, c in enumerate(load) if c == VM + "::get_SummaryRows")
    assert VM + "::Clear" in load[:first_rows], "Load clears the summary rows before adding any"
    assert load.count(SUMROW + "::.ctor") == 4, "Load adds the 4 native summary rows"
    clear = calls((VM, "Clear"))
    at = clear.index(VM + "::get_SummaryRows")
    assert clear[at + 1] == "class System.Collections.ObjectModel.Collection`1<class %s>::Clear" % SUMROW, clear[at + 1]
    assert VM + "::TryParseRegisterRows" in calls((VM, "ReadRegisterRows")), "ReadRegisterRows parses through TryParseRegisterRows"
    assert VM + "::WriteWeaponReports" in calls((VM, "SaveDebriefSnapshot")), "the snapshot saves the weapon reports"
    write = code((VM, "WriteWeaponReport"))
    blank = [i for i, (op, operand) in enumerate(write) if op == "ldsfld" and operand == "System.String::Empty"]
    assert len(blank) == 1 and write[blank[0] + 1] == ("call", VM + "::WriteDebriefSectionValue"), \
        "a side with no report rows is saved blank"
    assert VM + "::HasWeaponReportRows" in calls((VM, "WriteWeaponReport"))
    assert "System.String::IsNullOrWhiteSpace" in calls((VM, "ReadWeaponReport")), "ReadWeaponReport: blank gives null"
    ignored = [operand for op, operand in code((EXT, "IsIgnoredAmmo")) if op.startswith("ldc.i4.s") or op == "ldc.i4"]
    assert ignored and set(ignored) == {16}, ("IsIgnoredAmmo compares with Fueltank only", ignored)
    lambdas = [c for c in calls((EXT, "RecordCiwsRoundsFired")) if "<RecordCiwsRoundsFired>" in c]
    owner_rows = {game.names[game.owners["MethodDef", m.row_index]] + "::" + str(m.row.Name): m.row
                  for i in game.types.get(EXT + "+<>c__DisplayClass13_0", []) for m in game.tables.TypeDef[i - 1].MethodList}
    ciws = [name for name in lambdas if name in owner_rows]
    assert ciws, ("CIWS lambda not found", lambdas)
    bodies = []
    for name in ciws:
        bound[name] = owner_rows[name]
        bodies += calls(name)
    assert AMMO + "::set_CiwsRoundsFired" in bodies and AMMO + "::set_ProjectileFired" in bodies, \
        "CIWS bursts are counted in ProjectileFired, so count = Launched + ProjectileFired"
    assert "System.StringComparer::get_OrdinalIgnoreCase" in calls((TWR, "BuildTaskforceTotals")), \
        "weapon totals are keyed by AmmoRef ignoring case"

    print("Native 0.8.7 ABI verified: captured hash, %d method signatures and %d overload with %d parameter orders, "
          "%d inspected bodies, %d fields, %d properties, 10 cruise/terminal enum names, %d ammunition and %d object "
          "type names, inheritance, native lookahead and sampler reach (%.2f nm), and the campaign-cost behaviour checks"
          % (len(METHODS), len(OVERLOADS), len(PARAMETERS) + len(OVERLOADS), len(INSPECTED), len(FIELDS),
             len(PROPERTIES), len(AMMO_TYPES), len(OBJECT_TYPES), reach))
    print("No game code executed. Unity gameplay and Harmony installation still require the PC acceptance test.")


if __name__ == "__main__":
    main()
