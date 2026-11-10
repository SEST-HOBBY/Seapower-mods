"""Check preservation of Runtime 1.5.0's declared API in the reconstruction.

Requires dnfile. Compiler-generated closures/state machines are excluded; the
intentional F11 field-to-property binding and beta entrypoint retain their API.
This is a metadata/source-coverage check, not a gameplay assertion.
"""
import argparse
import ast
from pathlib import Path
import dnfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('captured')
p.add_argument('candidate')
a = p.parse_args()
root = Path(__file__).resolve().parents[3]
tree = ast.parse((root / 'integration/ui-followup/source/verify_capture.py').read_text())
ns = {}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                             and n.name in ['fullname', 'signature']], type_ignores=[]), 'signature', 'exec'), ns)


def inventory(path):
    pe = dnfile.dnPE(path)
    nested = {x.NestedClass.row_index: x.EnclosingClass.row_index for x in pe.net.mdtables.NestedClass}
    def name(index):
        t = pe.net.mdtables.TypeDef.rows[index - 1]
        return name(nested[index]) + '+' + str(t.TypeName) if index in nested else ns['fullname'](t)
    result = {}
    for index, t in enumerate(pe.net.mdtables.TypeDef, 1):
        full = name(index)
        if not full.startswith('Sest.RuntimeFixes.') or '<' in full:
            continue
        result[full] = {str(m.row.Name) + ':' + ns['signature'](pe, m.row.Signature.value)
                        for m in t.MethodList if '<' not in str(m.row.Name)}
    return result


old, new = inventory(a.captured), inventory(a.candidate)
checks = 0
for name, methods in old.items():
    assert name in new, 'Missing Runtime type: ' + name
    checks += 1
    assert methods <= new[name], 'Missing methods in ' + name + ': ' + str(methods - new[name])
    checks += len(methods)
print(f'Runtime API preservation passed: {checks} type/method contracts across {len(old)} types; no gameplay claim.')
