# Original world-population research

These three files are the original supplied reports, now available directly on
`feature/world-campaign-draft`. A sandbox link or separate attachment is no longer
needed to read them from the repository.

| ID | Repository file | Original attachment | Bytes | Lines |
|---|---|---|---:|---:|
| R01 | `R01.md` | `Pasted markdown(1).md` | 11698 | 70 |
| R02 | `R02.md` | `Pasted markdown (2).md` | 11083 | 79 |
| R03 | `R03.md` | `Pasted markdown (3).md` | 36684 | 172 |

The copies preserve the original wording, tables, whitespace and lack of a final
newline. Existing R01-R03 line locators remain applicable. The SHA-256 values in
`../source-manifest.json` are unchanged from the original manifest; repository
paths and matching Git blob IDs have been added. The local `.gitattributes`
disables line-ending conversion for these three source files.

Byte identity proves faithful transfer, not factual accuracy. The reports remain
`supplied_unverified`. Keep proposed game mechanics, source-described real-world
roles, independently checked facts and authored scenario choices distinct.
Do not silently edit or correct these originals; record checks, disagreements and
corrections separately with their evidence.

## Continue the build

Read all three reports alongside `../WORLD_POPULATION_PLAN.md`, then complete
the source-linked world-population register using the collection mappings already
under way. Preserve full geographic coverage, including unresolved nodes and
unsupported assets. The reports remove the missing-source blocker; they do not
prove engine limits, working services or a complete current order of battle.

Keep the existing inventory work. A session on a different working branch can
fetch the draft ref and read these paths from it without resetting that branch,
merging unrelated work or repeating finished inventories.

## Verify exact copies

Run from the repository root on a checkout containing these files:

```bash
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

manifest = json.loads(Path('docs/world-sandbox/source-manifest.json').read_text(encoding='utf-8'))
failed = False
for report in manifest['reports']:
    path = Path(report['repository_path'])
    try:
        data = path.read_bytes()
    except OSError as exc:
        print(f"FAIL {report['id']}: {exc}")
        failed = True
        continue
    observed = {
        'bytes': len(data),
        'lines': len(data.splitlines()),
        'sha256': hashlib.sha256(data).hexdigest(),
        'git_blob_sha': hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest(),
    }
    mismatches = [key for key, value in observed.items() if value != report[key]]
    if mismatches:
        print(f"FAIL {report['id']}: mismatched {', '.join(mismatches)}")
        failed = True
    else:
        print(f"PASS {report['id']}: bytes, lines, SHA-256 and Git blob match")
raise SystemExit(1 if failed else 0)
PY
```

This checks source integrity only. It is not a campaign build, gameplay test or
independent verification of the reports' claims.
