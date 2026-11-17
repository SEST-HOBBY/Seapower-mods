"""Build an auditable file integrity manifest for the ZIP handoff."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=[]
for p in sorted(root.rglob('*')):
    if not p.is_file() or p.name in {'MANIFEST.json'} or '__pycache__' in p.parts or p.suffix=='.pyc':continue
    raw=p.read_bytes()
    files.append({'path':p.relative_to(root).as_posix(),'size_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
manifest={'project':'Modern Naval Operations / Global Command Operations','artifact':'Environmental Operations Prototype','version':'0.1.0-draft','created_brisbane':'2026-11-18','game_integration_status':'NOT GAME TESTED','data_status':'synthetic demo; real API adapter not executed in container','files':files}
(root/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Manifest:',len(files),'files')
