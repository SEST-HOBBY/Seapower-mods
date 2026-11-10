"""Build the owner's PC toolkit for the R12 Workshop release from this checkout.

The toolkit is what Prepare-PC.cmd, Repair-PC.cmd, Upload-PC.cmd and
Finish-Upload.cmd run against on the gaming PC: the release docs and
launchers from docs/releases/20261107, RIBBONS.txt, the reviewed beta package
extracted as R12/, a git bundle of the release branch and SOURCE-RECEIPT.json,
which Prepare-PC.ps1 and Upload-PC.ps1 read. Nothing here touches a game,
Steam or a remote.

  python tools/build_pc_toolkit.py --out <dir> [--package <SEST-Beta-*.zip>]
      [--prerequisite <commit the PC already has>] [--github-pushed]

The checkout must be clean, so the receipt's commit is exactly what is built.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'docs' / 'releases' / '20261107'
BETA_DIRECTORY = 'R12'
SUPPORT = ROOT / 'integration' / 'dist' / 'SEST_Integration' / 'beta-support'
LAUNCHERS = ('Prepare-PC.cmd', 'Prepare-PC.ps1', 'Repair-PC.cmd', 'Upload-PC.cmd',
             'Upload-PC.ps1', 'Finish-Upload.cmd')


def git(*args):
    run = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    if run.returncode != 0:
        sys.exit('git ' + ' '.join(args) + ' failed: ' + run.stderr.strip())
    return run.stdout.strip()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--package', type=Path, default=SUPPORT / 'SEST-Beta-Features.zip',
                        help='the reviewed beta package zip (default: the one the upload carries)')
    parser.add_argument('--out', required=True, type=Path, help='a new, empty toolkit folder')
    parser.add_argument('--prerequisite', default='72129cb45d3ec49d145ab323f16111089d868edb',
                        help='a commit the PC repository already has (bundle base)')
    parser.add_argument('--github-pushed', action='store_true', help='record that the branch is on GitHub')
    args = parser.parse_args()

    if git('status', '--porcelain'):
        sys.exit('The checkout has uncommitted changes; commit them first.')
    branch = git('symbolic-ref', '--short', 'HEAD')
    commit = git('rev-parse', 'HEAD')
    git('merge-base', '--is-ancestor', args.prerequisite, commit)
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        sys.exit(f'{out} is not empty.')
    out.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((RELEASE / 'upload-manifest.json').read_text(encoding='utf-8'))
    support = json.loads((SUPPORT / 'manifest.json').read_text(encoding='utf-8'))
    if sha256(args.package) != support['archive_sha256']:
        sys.exit('The package is not the beta-support archive the upload carries.')

    copies = sorted(p.name for p in RELEASE.iterdir() if p.is_file() and (
        p.name in LAUNCHERS or p.name == 'README-FIRST.txt' or p.name.startswith(('R12-', 'STEAM-'))))
    for name in copies:
        (out / name).write_bytes((RELEASE / name).read_bytes())
    (out / 'RIBBONS.txt').write_bytes((ROOT / 'integration/campaign/setup/RIBBONS.txt').read_bytes())
    (out / 'VALIDATION.json').write_bytes((RELEASE / 'validation.json').read_bytes())

    beta = out / BETA_DIRECTORY
    with zipfile.ZipFile(args.package) as z:
        for info in z.infolist():
            name = PurePosixPath(info.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in info.filename:
                sys.exit('Unsafe path in package: ' + info.filename)
            if info.is_dir():
                continue
            target = beta.joinpath(*name.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(info))
    beta_files = {p.name: sha256(p) for p in sorted((beta / 'payload').glob('*.dll'))}

    bundle_name = f'SEST-Workshop-{support["revision"].split("-499675cd")[0]}.bundle'
    bundle = out / bundle_name
    git('bundle', 'create', str(bundle), f'^{args.prerequisite}', f'refs/heads/{branch}')
    git('bundle', 'verify', str(bundle))

    receipt = {
        'format': 1,
        'release_commit': commit,
        'release_branch': branch,
        'beta_directory': BETA_DIRECTORY,
        'workshop_bundle': {'file': bundle_name, 'sha256': sha256(bundle), 'prerequisite': args.prerequisite},
        'beta_revision': support['revision'],
        'beta_package_sha256': support['archive_sha256'],
        'target_game_sha256': support['target_game_sha256'],
        'target_game_label': support.get('target_game_label', ''),
        'runtime_version': manifest.get('beta_runtime_version'),
        'ui_version': manifest.get('beta_ui_version'),
        'status': 'prepared-for-pc-acceptance',
        'canonical_files': manifest['file_count'],
        'beta_files': beta_files,
        'steam_published': False,
        'github_pushed': bool(args.github_pushed),
        'save_files_modified': False,
        'guide': 'README-FIRST.txt',
    }
    (out / 'SOURCE-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')

    files = sorted((p for p in out.rglob('*') if p.is_file()), key=lambda p: p.relative_to(out).parts)
    integrity = {'release_commit': commit, 'file_count': len(files),
                 'files': [{'path': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha256(p)}
                           for p in files]}
    (out / 'TOOLKIT-INTEGRITY.json').write_text(json.dumps(integrity, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'toolkit {out}: {len(files) + 1} files, {branch} at {commit[:12]}, bundle {receipt["workshop_bundle"]["sha256"][:12]}')


if __name__ == '__main__':
    main()
