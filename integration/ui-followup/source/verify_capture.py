"""Audit captured target contracts and preservation of the PC-confirmed hooks.

Requires dnfile and dncil. This is a metadata/IL audit; it does not run the game.
"""
import argparse
from pathlib import Path
import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes

p = argparse.ArgumentParser()
p.add_argument('--capture', required=True)
p.add_argument('--previous', required=True, help='PC-confirmed Contacts Fix 1.0.0 DLL')
p.add_argument('--new', required=True)
a = p.parse_args()
capture = Path(a.capture)

def fullname(t):
    return str(t.TypeNamespace) + '.' + str(t.TypeName)

def definition(pe, type_name):
    return next(t for t in pe.net.mdtables.TypeDef if fullname(t) == type_name)

def method(pe, type_name, name):
    return next(m.row for m in definition(pe, type_name).MethodList if str(m.row.Name) == name)

def signature(pe, data):
    pos = 0
    def integer():
        nonlocal pos
        b = data[pos]; pos += 1
        if b & 0x80 == 0: return b
        if b & 0xc0 == 0x80:
            value = ((b & 0x3f) << 8) | data[pos]; pos += 1; return value
        value = ((b & 0x1f) << 24) | int.from_bytes(data[pos:pos+3], 'big'); pos += 3; return value
    def named(code):
        tag, index = code & 3, code >> 2
        table = [pe.net.mdtables.TypeDef, pe.net.mdtables.TypeRef, pe.net.mdtables.TypeSpec][tag]
        row = table.rows[index - 1]
        return fullname(row) if tag != 2 else signature(pe, b'\x06' + row.Signature.value)
    def kind():
        nonlocal pos
        value = data[pos]; pos += 1
        if value in [0x11, 0x12]: return named(integer())
        if value == 0x1d: return kind() + '[]'
        if value in [0x10, 0x0f]: return ('ref ' if value == 0x10 else 'ptr ') + kind()
        if value in [0x13, 0x1e]: return ('!' if value == 0x13 else '!!') + str(integer())
        if value == 0x15:
            owner = kind(); count = integer(); return owner + '<' + ','.join(kind() for _ in range(count)) + '>'
        return hex(value)
    convention = data[pos]; pos += 1
    if convention == 0x06: return kind()
    generic = integer() if convention & 0x10 else 0
    count = integer(); returns = kind()
    return str(convention) + '/' + str(generic) + ':' + returns + '(' + ','.join(kind() for _ in range(count)) + ')'

def member_name(pe, row):
    owner = row.Class.row
    return str(getattr(owner, 'TypeNamespace', '')) + '.' + str(getattr(owner, 'TypeName', '')) + '.' + str(row.Name) + ':' + signature(pe, row.Signature.value)

def normalized(pe, type_name, name):
    tokens = {}
    for t in pe.net.mdtables.TypeDef:
        for m in t.MethodList: tokens[0x06000000 + m.row_index] = fullname(t) + '.' + str(m.row.Name) + ':' + signature(pe, m.row.Signature.value)
        for f in t.FieldList: tokens[0x04000000 + f.row_index] = fullname(t) + '.' + str(f.row.Name)
    for i, m in enumerate(pe.net.mdtables.MemberRef, 1): tokens[0x0a000000 + i] = member_name(pe, m)
    for i, t in enumerate(pe.net.mdtables.TypeRef, 1): tokens[0x01000000 + i] = fullname(t)
    result = []
    for x in read_method_body_from_bytes(pe.get_data(method(pe, type_name, name).Rva)).instructions:
        value = x.operand
        if hasattr(value, 'value'):
            raw = value.value
            if raw >> 24 == 0x70: value = pe.net.user_strings.get(raw & 0xffffff).value
            else: value = tokens.get(raw, str(value))
        elif value is not None: value = str(value)
        result.append((str(x.opcode), value))
    return result

old = dnfile.dnPE(a.previous)
new = dnfile.dnPE(a.new)
for type_name, name in [('Sest.UiFixes.ContactsFix', 'BeforeMatches'), ('Sest.UiFixes.ContactsFix', 'UiParent'), ('Sest.UiFixes.InputPolicy', 'MayMatch')]:
    assert normalized(old, type_name, name) == normalized(new, type_name, name), name + ' changed from the PC-confirmed build'
    print('PC-confirmed hook preserved:', name)

def captured(old_path, current_path):
    p = capture / current_path
    return p if p.exists() else capture / old_path

runtime = dnfile.dnPE(str(captured('installed-pack/workshop/plugins/SEST.RuntimeFixes.dll', 'assemblies/workshop/3812461539/plugins/SEST.RuntimeFixes.dll')))
calls = normalized(runtime, 'Sest.RuntimeFixes.ContactWindowBridge', 'Move')
assert sum('PopOutBridge.get_Root:' in str(v) for _, v in calls) == 1
assert sum('VisualTreeHelper.GetParent:' in str(v) for _, v in calls) == 2
calls = normalized(runtime, 'Sest.RuntimeFixes.ContactWindowBridge', 'AfterTick')
assert sum('VisualTreeHelper.GetParent:' in str(v) for _, v in calls) == 3
print('Captured move audit passed: one pop-out root lookup, two move parent lookups, three button parent lookups')

pop = dnfile.dnPE(str(captured('mod-reference/3826396311/SeaPowerPopOut.dll', 'assemblies/workshop/3826396311/SeaPowerPopOut.dll')))
screen = definition(pop, 'SeaPowerPopOut.PopOutScreen')
for name in ['UpdateScreen', 'FindButtonsPanel', 'Decorate', 'get_Instance']:
    assert method(pop, 'SeaPowerPopOut.PopOutScreen', name).Rva
for name in ['root', 'items', 'windows', 'hint']:
    assert any(str(f.row.Name) == name for f in screen.FieldList)

# Decode the root's compressed TypeDefOrRef index: the original failed cast is
# confirmed against the real field type, not inferred from a screenshot.
root_sig = next(f.row.Signature.value for f in screen.FieldList if str(f.row.Name) == 'root')
assert root_sig[:2] == b'\x06\x12'
code = root_sig[2]
if code & 0xc0 == 0x80: code = ((code & 0x3f) << 8) | root_sig[3]
assert code & 3 == 1
root_type = fullname(pop.net.mdtables.TypeRef.rows[(code >> 2) - 1])
assert root_type == 'SeapowerUI.ScalableUserControl', root_type
print('Confirmed pop-out root is ScalableUserControl; corrected code selects the inner Items parent panel')

formation = dnfile.dnPE(str(captured('mod-reference/3818251045/SeaPowerSquadPanel.dll', 'assemblies/workshop/3818251045/SeaPowerSquadPanel.dll')))
contracts = {
    'SeaPowerSquadPanel.Plugin': (['_squads', '_enabled'], ['LateUpdate']),
    'SeaPowerSquadPanel.SquadManagerController': (['_bar', '_state', '_main'], ['Tick', 'Detach']),
    'SeaPowerSquadPanel.SquadBarController': (['_window'], []),
    'SeaPowerSquadPanel.SquadBarTools': (['_tools'], ['RefreshAppearance']),
    'SeaPowerSquadPanel.SquadWindowState': ([], ['SetVisible']),
}
for type_name, (fields, methods) in contracts.items():
    t = definition(formation, type_name)
    for name in fields: assert any(str(f.row.Name) == name for f in t.FieldList), type_name + '.' + name
    for name in methods: assert method(formation, type_name, name).Rva, type_name + '.' + name
print('All Formation Manager reflection contracts present in captured 0.2.17')

def anchor_ctor(pe):
    return next(m.Signature.value for m in pe.net.mdtables.MemberRef if str(getattr(m.Class.row, 'TypeName', '')) == 'ACPlugin')
assert anchor_ctor(runtime) == anchor_ctor(new)
print('Anchor Chain attribute constructor contract matches the captured runtime')

cv = dnfile.dnPE(str(capture / 'assemblies/workshop/3774859959/CV16.dll'))
calls = normalized(cv, 'meltemi.CV16.plugin.ForwardRunwayClearancePatch', 'IsClear')
assert sum('System.Reflection.FieldInfo.GetValue:' in str(v) for _, v in calls) == 1
assert any('ReleasedAt' in str(v) for _, v in calls)
assert any('AircraftInFlightField' in str(v) for _, v in calls)
assert any(op == 'ldc.r4' and float(v) == 30 for op, v in calls)
game = dnfile.dnPE(str(capture / 'game-reference/Seapower-Scripts.dll'))
for t in ['SeaPower.Aircraft', 'SeaPower.Helicopter']:
    assert any(str(f.row.Name) == '_isInFlight' and f.row.Signature.value == b'\x06\x02' for f in definition(game, t).FieldList)
for f in ['_initialized', '_closing']:
    assert any(str(x.row.Name) == f and x.row.Signature.value == b'\x06\x02' for x in definition(game, 'SeaPower.GameMain').FieldList)
for name in ['Update', 'OnDestroy', 'PerformFixedUpdate']:
    assert method(game, 'SeaPower.GameMain', name).Rva
menu = dnfile.dnPE(str(capture / 'assemblies/workshop/3812461539/plugins/SEST.MenuBackground.dll'))
for t, methods in {'Sest.MenuBackground.PictureLog':['Tick','Schedule'],
                   'Sest.MenuBackground.PictureSwap':['Tick','Watch'],
                   'Sest.MenuBackground.MenuFilmSwapper':['Scan']}.items():
    for m in methods: assert method(menu, t, m).Rva
print('Performance/CV16 contracts passed: exact one flag read, original timeout, both typed flags, lifecycle and picture discovery hooks')

# 1.3.0: remove only the unconditional discovery invalidation. Preserve the
# resize/content event paths that decide when a fitting search is actually needed.
discover = normalized(formation, 'SeaPowerSquadPanel.SquadBarController', 'DiscoverTrees')
assert sum('SquadBarResize.InvalidateContent:' in str(v) for _, v in discover) == 1
assert any('SquadBarResize.DiscoverHandles:' in str(v) for _, v in discover)
assert any('SquadBarTree.DiscoverLayout:' in str(v) for _, v in discover)
for name in ['.ctor', 'UseState', 'EndContentSizes']:
    code = normalized(formation, 'SeaPowerSquadPanel.SquadBarResize', name)
    assert any(op == 'stfld' and '._contentDirty' in str(v) for op, v in code), name
refresh = normalized(formation, 'SeaPowerSquadPanel.SquadBarResize', 'Refresh')
assert any(op == 'ldfld' and '._contentDirty' in str(v) for op, v in refresh)
for name in ['OnDelta', 'Refresh']:
    assert any('SquadBarResize.PickScale:' in str(v) for _, v in normalized(formation, 'SeaPowerSquadPanel.SquadBarResize', name))
for t, names in {
    'SeaPowerSquadPanel.SquadRowLayout': ['Apply', 'FullScale'],
    'SeaPowerSquadPanel.SquadBarTools': ['RefreshAppearance'],
}.items():
    for name in names: assert method(formation, t, name).Rva
assert signature(runtime, method(runtime, 'Sest.RuntimeFixes.PopOutBridge', 'AfterFormation').Signature.value).endswith('(0x1c)')
assert method(runtime, 'Sest.RuntimeFixes.PopOutBridge', 'Contains').Rva
print('Formation 1.3 audit passed: exactly one idle invalidation, actual content/size/drag refits retained, chrome/profiling contracts present')

noesis = dnfile.dnPE(str(capture / 'game-reference/Noesis.NoesisGUI.dll'))
for name in ['CreateView', 'LateUpdate', 'set_EnableKeyboard', 'set_EnableMouse', 'set_EnableTouch', 'set_EnableActions']:
    assert method(noesis, '.NoesisView', name).Rva, 'NoesisView.' + name
assert signature(noesis, method(noesis, '.NoesisView', 'CreateView').Signature.value).endswith('(Noesis.FrameworkElement)')
for t, names in {
    'SeaPower.RichMissionMessages': ['ParseMissionPopupText'],
    'SeaPower.InputHandler': ['LoadKeybindings'],
    'SeaPower.KeyBinding': ['get_KeyAction', 'set_DisplayString'],
    'SeapowerUI.ViewModels.MainGameViewModel': ['get_BearingTapeTransform', 'get_WorldViewMonitor', 'get_WorldViewDetached', 'get_ShowPip3D'],
}.items():
    for name in names: assert method(game, t, name).Rva, t + '.' + name
assert method(pop, 'SeaPowerPopOut.PopOutScreen', 'Flatten').Rva
binding = normalized(game, 'SeaPower.InputHandler', 'LoadKeybindings')
assert ('ldstr', 'F9') in binding
key_patch = normalized(new, 'Sest.UiFixes.UiRefinements', 'AfterBindings')
assert ('ldstr', 'LeftControl+F9') in key_patch
assert any('SeaPower.KeyBinding.set_DisplayString:' in str(v) for _, v in key_patch)
assert any(op == 'ldc.i4' and v == '290' for op, v in key_patch), 'F9 key code'
assert any(op == 'ldc.i4' and v == '306' for op, v in key_patch), 'LeftControl key code'
for name in ['BearingTapeTransform', 'CameraCompassHost', 'CompassScale']:
    assert any(name in str(v) for method_name in ['HeadingBinding', 'ScreenHost']
               for _, v in normalized(new, 'Sest.UiFixes.CameraCompass', method_name)), name
print('Preparation/F9/compass 1.3 contracts passed against captured native game and Noesis APIs')

terrain = normalized(game, 'SeaPower.LayeredTerrainTextureData', 'CreateTextureArray')
indices = [i for i, (op, v) in enumerate(terrain) if op == 'call' and 'UnityEngine.Resources.UnloadUnusedAssets:' in str(v)]
assert len(indices) == 1
assert terrain[indices[0] + 1] == ('pop', None)
assert terrain[-1] == ('ret', None)
assert sum('Texture2DArrayUtil.Build:' in str(v) for _, v in terrain) == 1
assert sum('UpdateCompactTextureAssetArray:' in str(v) for _, v in terrain) == 1
assert ('ldstr', 'Request') in normalized(new, 'Sest.UiFixes.TerrainCleanup', 'BatchCall')
request = normalized(new, 'Sest.UiFixes.TerrainCleanup', 'Request')
assert any('PerformanceReview.get_Live:' in str(v) for _, v in request)
assert sum('Resources.UnloadUnusedAssets:' in str(v) for _, v in request) == 1
tick = normalized(new, 'Sest.UiFixes.TerrainCleanup', 'Tick')
assert sum('Resources.UnloadUnusedAssets:' in str(v) for _, v in tick) == 1
assert any('AsyncOperation.get_isDone:' in str(v) for _, v in tick)
print('Terrain 1.4 audit passed: exactly one discarded unload, original texture build retained, native outside-mission fallback and in-flight guard present')

# 1.4.1 is an observation build. Timing hooks must not gate original methods or
# replace their exception. All existing cleanup and UI logic remains identical.
assert signature(new, method(new, 'Sest.UiFixes.StutterDiagnostics', 'Begin').Signature.value).split(':', 1)[1].startswith('0x1(')
finish = normalized(new, 'Sest.UiFixes.StutterDiagnostics', 'Finish')
assert finish[-2:] == [('ldarg.2', None), ('ret', None)]
assert not any(op.startswith('starg') for op, _ in finish)
for name in ['Start', 'Tick', 'Report', 'Reset', 'End', 'Begin', 'Finish', 'Install']:
    code = normalized(new, 'Sest.UiFixes.StutterDiagnostics', name)
    assert not any('System.GC.Collect:' in str(v) or 'GC.WaitForPendingFinalizers:' in str(v) for _, v in code)
    assert not any(any(s in str(v) for s in ['set_vSyncCount:', 'set_targetFrameRate:', 'set_GCMode:', 'Profiler.set_enabled:']) for _, v in code)
assert any('ProfilerRecorderHandle.GetAvailable:' in str(v) for _, v in normalized(new, 'Sest.UiFixes.StutterDiagnostics', 'Start'))
assert any('ProfilerRecorder.Dispose:' in str(v) for _, v in normalized(new, 'Sest.UiFixes.StutterDiagnostics', 'End'))
assert any('StutterDiagnostics.Tick:' in str(v) for _, v in normalized(new, 'Sest.UiFixes.FramePacing', 'Tick'))
assert any('StutterDiagnostics.End:' in str(v) for _, v in normalized(new, 'Sest.UiFixes.PerformanceReview', 'EndGame'))
print('Stutter observation audit passed: void prefix, original exception returned, no forced GC or settings mutation, native counter disposal and lifecycle hooks present')

factory = method(runtime, 'Sest.RuntimeFixes.CampaignCosts', 'Prices')
factory_body = read_method_body_from_bytes(runtime.get_data(factory.Rva))
assert len(factory_body.exception_handlers) == 0
assert sum(str(i.opcode) == 'ret' for i in factory_body.instructions) == 2
assert sum('CombatPrices..ctor:' in str(v) for _, v in normalized(runtime, 'Sest.RuntimeFixes.CampaignCosts', 'Prices')) == 1
assert method(runtime, 'Sest.RuntimeFixes.CampaignCosts', 'LiveView').Rva
assert any('CostCatalogueCache.Clear:' in str(v) for _, v in normalized(new, 'Sest.UiFixes.PerformanceReview', 'BeforeGame'))
assert any('CostCatalogueCache.Clear:' in str(v) for _, v in normalized(new, 'Sest.UiFixes.PerformanceReview', 'EndGame'))
assert any('PerformanceReview.get_MissionContext:' in str(v) for _, v in normalized(new, 'Sest.UiFixes.CostCatalogueCache', 'Get'))
assert ('ldstr', 'LoadConfig') in normalized(new, 'Sest.UiFixes.CostCatalogueCache', 'Install')
assert ('ldstr', 'Prices') in normalized(new, 'Sest.UiFixes.CostCatalogueCache', 'Install')
for name in ['Get', 'Remember', 'Clear']:
    code = normalized(new, 'Sest.UiFixes.CostCatalogueCache', name)
    assert not any('System.IO.File.' in str(v) or 'System.GC.Collect:' in str(v) for _, v in code)
print('Cost cache audit passed: exact two-return factory, original constructor, live mission scope, tracker reload and mission teardown invalidation; no cost capture/history method replaced')
