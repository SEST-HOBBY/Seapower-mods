"""For Claude's cloud workspace: verify and extract the complete SEST pack."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import argparse, hashlib, json, subprocess, sys

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--destination',required=True,help='New or empty scratch directory')
    args=parser.parse_args()
    here=Path(__file__).resolve().parent
    info=json.loads((here/'SEST_BROWSER_PARTS.json').read_text(encoding='utf-8'))
    dest=Path(args.destination).resolve()
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir())):
        raise SystemExit('Destination must be a new or empty directory; existing files were not touched.')
    seen=set()
    for part in info['parts']:
        path=here/part['file']
        if not path.is_file():raise SystemExit('Missing ZIP part: '+part['file'])
        if path.stat().st_size!=part['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=part['sha256']:
            raise SystemExit('Part checksum or size mismatch: '+part['file'])
        with ZipFile(path) as z:
            for item in z.infolist():
                p=PurePosixPath(item.filename)
                if p.is_absolute() or '..' in p.parts or '\\' in item.filename or ':' in item.filename or not p.parts or p.parts[0]!=info['root_folder']:
                    raise SystemExit('Unsafe archive member: '+item.filename)
                if item.filename in seen:raise SystemExit('Duplicate archive member: '+item.filename)
                seen.add(item.filename)
            bad=z.testzip()
            if bad:raise SystemExit('ZIP CRC failure: '+bad)
    if len(seen)!=info['file_count']:raise SystemExit('Incomplete combined inventory')
    dest.mkdir(parents=True,exist_ok=True)
    for part in info['parts']:
        with ZipFile(here/part['file']) as z:z.extractall(dest)
    root=dest/info['root_folder']
    for script in ['validate_pack.py','validate_quality_review.py']:
        subprocess.run([sys.executable,str(root/'tools'/script)],check=True)
    print('Complete gallery extracted to: '+str(root))
    print('Read CLAUDE_START_HERE.txt and both integration handoffs before changes.')
if __name__=='__main__':main()
