#!/usr/bin/env python3
"""Read-only ABI check against a player-exported Seapower-Scripts.dll.

Optional development check: python verify_native_api.py /path/to/assembly
Requires dnfile and dncil. Neither the assembly nor its decompiled code is
copied into the pack. The exact captured hash is also checked at runtime.
"""
import hashlib
from pathlib import Path
import sys
import dnfile
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes

EXPECTED = "c913e31f2d73e526f2d28043f522f2be26f12534fd0421eedee3cd70eab9cdd8"
SIGNATURES = {
    ("SeaPower.ObjectBase", "get__geoPosition"): "200011ac48",
    ("SeaPower.WeaponBase", "get__flightStage"): "200011c00044bc",
    ("SeaPower.TerrainUtils", "GetSafeAltitudeOverSurface"): "00050c12adac0c0c0202",
    ("SeaPower.TerrainUtils", "CrudeGetHighestTerrainHeightAhead"): "00040c11ac480c0c02",
    ("SeaPower.Utils", "heightInFeetToUnity"): "00010c0c",
    ("SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager", "ReadSnapshot"): "0003129a4c12c00040b00e0e",
    ("SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager", "MissionLaunchSection"): "00010e08",
    ("SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager", "MissionLaunchUnitPrefix"): "00010e08",
    ("SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel", "ReadUnitRows"): "20020112c00040b012bf04",
    ("SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel", "SortDebriefUnitRows"): "00011512819d011298fc1512819d011298fc",
    ("SeapowerUI.ViewModels.LinearCampaignTaskForceSnapshot", "get_Items"): "2000151288390112983c",
    ("SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefUnitRow", ".ctor"): "200a010e0e0e0e0e0e020211adc808",
}


def main():
    path = Path(sys.argv[1])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED, "uninspected native build"
    pe = dnfile.dnPE(str(path))
    methods, fields = {}, {}
    for type_row in pe.net.mdtables.TypeDef:
        owner = str(type_row.TypeNamespace) + "." + str(type_row.TypeName)
        for method in type_row.MethodList:
            methods.setdefault((owner, str(method.row.Name)), []).append(method.row)
        for field in type_row.FieldList:
            fields[(owner, str(field.row.Name))] = field.row.Signature.value.hex()
    for key, signature in SIGNATURES.items():
        matches = [row for row in methods[key] if row.Signature.value.hex() == signature]
        assert len(matches) == 1, key
    assert fields["SeaPower.AmmunitionParameters", "_ammunitionFileName"] == "060e"
    assert fields["SeaPower.AmmunitionParameters", "_terrainFollowFlight"] == "0602"
    assert fields["SeaPower.WeaponBase", "_ap"] == "0612c0004294"
    enums = {str(row.Name) for t in pe.net.mdtables.TypeDef if str(t.TypeName) == "FlightStage" for row in [f.row for f in t.FieldList]}
    for name in ("ToBearing", "MaintainHeight", "MoveToLoftAlt", "MaintainLoftAlt", "MoveToSeaSkimming",
                 "MaintainSeaSkimming", "MoveToFinalFlightAlt", "MaintainFinalFlightAlt", "AlignSensorToTarget", "TerminalApproach"):
        assert name in enums, name
    safe = methods["SeaPower.TerrainUtils", "GetSafeAltitudeOverSurface"][0]
    body = CilMethodBody(CilMethodBodyReaderBytes(pe.get_data(safe.Rva)))
    numbers = [instruction.operand for instruction in body.instructions if str(instruction.opcode) == "ldc.r4"]
    assert any(abs(n - .405) < .00001 for n in numbers), "native weapon lookahead assumption changed"
    print("Native 0.8.6 ABI verified: captured hash, 12 method signatures, 3 fields, 10 cruise/terminal enum names and native lookahead")
    print("No game code executed. Unity gameplay and Harmony installation still require the PC acceptance test.")


if __name__ == "__main__":
    main()
