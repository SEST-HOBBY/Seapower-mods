"""Check the runtime hash compiled into both companion plugins before shipping them."""
import hashlib
import sys
from pathlib import Path

import dnfile


COMPANIONS = {
    "SEST.ContactsFix.dll": "Sest.UiFixes",
    "SEST.IdentifyDataPaths.dll": "Sest.IdentifyDataPaths",
}


def require_runtime_pairing(read_file):
    expected = hashlib.sha256(read_file("SEST.RuntimeFixes.dll")).hexdigest()
    for name, namespace in COMPANIONS.items():
        with dnfile.dnPE(data=read_file(name)) as pe:
            tables = pe.net.mdtables
            fields = [field.row for t in tables.TypeDef
                      if str(t.TypeNamespace) == namespace and str(t.TypeName) == "BuildPins"
                      for field in t.FieldList if str(field.row.Name) == "RuntimeSha256"]
            values = [constant.Value.value.decode("utf-16le") for constant in tables.Constant
                      if constant.Type == 0x0e and constant.Parent.table is tables.Field
                      and constant.Parent.row in fields]
        if values != [expected]:
            raise ValueError(f"{name} expects runtime {values}, packaged runtime is {expected}")
    return expected


if __name__ == "__main__":
    payload = Path(sys.argv[1])
    print("Contacts and Identify both require the packaged runtime", require_runtime_pairing(
        lambda name: (payload / name).read_bytes()))
