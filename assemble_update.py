#!/usr/bin/env python3
"""Claude cloud helper: verify and assemble the normal ZIP parts into a new directory."""
import argparse,hashlib,json,stat,zipfile
from pathlib import Path,PurePosixPath

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--destination',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parent;dest=a.destination.resolve()
 if dest.exists():raise ValueError('Destination already exists; use a new staging directory.')
 parts=json.loads((root/'PARTS.json').read_text())['parts'];seen=set();total=0
 for p in parts:
  f=root/p['file']
  if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=p['sha256']:raise ValueError('Missing or changed part: '+p['file'])
  with zipfile.ZipFile(f) as z:
   for i in z.infolist():
    q=PurePosixPath(i.filename);total+=i.file_size
    if q.is_absolute() or '..' in q.parts or '\\' in i.filename or q.parts[0]!='SEST_Gallery_Update_190':raise ValueError('Unexpected archive path')
    if i.filename in seen or stat.S_ISLNK(i.external_attr>>16):raise ValueError('Duplicate path or symlink in archive')
    seen.add(i.filename)
 if total>400*1024*1024:raise ValueError('Unexpected expanded size')
 dest.mkdir(parents=True)
 for p in parts:
  with zipfile.ZipFile(root/p['file']) as z:z.extractall(dest)
 print('Assembled '+str(dest/'SEST_Gallery_Update_190'))

if __name__=='__main__':main()
