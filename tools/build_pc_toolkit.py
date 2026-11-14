"""Build the owner's PC toolkit for the R12 Workshop release (beta R14, Sea Power 0.9.2 Build 261113) from this checkout.

The toolkit is what Prepare-PC.cmd, Repair-PC.cmd, Upload-PC.cmd and
Finish-Upload.cmd run against on the gaming PC: the release docs and
launchers from docs/releases/20261107, RIBBONS.txt, the reviewed beta package
extracted as R14/, a git bundle of the release branch and SOURCE-RECEIPT.json,
which Prepare-PC.ps1 and Upload-PC.ps1 read. Nothing here touches a game,
Steam or a remote.

  python tools/build_pc_toolkit.py --out <dir> [--package <SEST-Beta-*.zip>]
      [--prerequisite <commit the PC already has>] [--github-pushed]
      [--zip <toolkit.zip>]

The checkout must be clean, so the receipt's commit is exactly what is built,
and on a branch Prepare-PC.ps1 accepts. The beta-support package must be the
R14 one for Sea Power 0.9.2 (integration/dist/SEST_Integration/beta-support);
an older package is refused before anything is written. --zip also writes the
toolkit as one ZIP with every file at its root, entries sorted and dated at
the commit time, so the same commit gives the same bytes, and prints its
SHA-256.
"""
import argparse
import hashlib
import io
import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'docs' / 'releases' / '20261107'
BETA_DIRECTORY = 'R14'
# Seapower-Scripts.dll of Sea Power 0.9.2 Build 261113, the game the R14
# package was built and reviewed against.
TARGET_GAME_SHA256 = '3f56861f09e867f315b194c81a7a2450154ccc6bb5afb769b4956dfd4a00503a'
SUPPORT = ROOT / 'integration' / 'dist' / 'SEST_Integration' / 'beta-support'
LAUNCHERS = ('Prepare-PC.cmd', 'Prepare-PC.ps1', 'Repair-PC.cmd', 'Upload-PC.cmd',
             'Upload-PC.ps1', 'Finish-Upload.cmd')
# The release branches Prepare-PC.ps1 imports (its own pattern, unanchored):
# beta, dev, or a release/, feature/, fix/, chore/ or sest-dev/ branch.
BRANCH_PATTERN = r'(release|feature|fix|chore|sest-dev)/[A-Za-z0-9._/-]+|beta|dev'


def git(*args):
    run = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    if run.returncode != 0:
        sys.exit('git ' + ' '.join(args) + ' failed: ' + run.stderr.strip())
    return run.stdout.strip()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_branch(branch):
    """Stop here on a branch the PC would refuse ('Unrecognised release receipt.')."""
    if not re.fullmatch(BRANCH_PATTERN, branch):
        sys.exit(f'Prepare-PC.ps1 refuses the branch {branch}; build from beta, dev or a '
                 'release/, feature/, fix/, chore/ or sest-dev/ branch.')


def check_support(support):
    """Stop unless the beta-support manifest describes this toolkit's beta for 0.9.2."""
    revision = str(support.get('revision', ''))
    if not revision.startswith(BETA_DIRECTORY + '-'):
        sys.exit(f'The beta-support package is {revision or "unnamed"}, not {BETA_DIRECTORY}: '
                 'rebuild integration/dist/SEST_Integration/beta-support from the '
                 f'{BETA_DIRECTORY} package before building the toolkit.')
    target = str(support.get('target_game_sha256', ''))
    if target != TARGET_GAME_SHA256:
        sys.exit(f'The beta-support package targets game {target[:12] or "(none)"}, not '
                 f'Sea Power 0.9.2 ({TARGET_GAME_SHA256[:12]}).')


def bundle_name(support):
    """SEST-Workshop-<revision without its game-hash suffix>.bundle."""
    revision = support['revision'].removesuffix('-' + support['target_game_sha256'][:8])
    return f'SEST-Workshop-{revision}.bundle'


def zip_date_time(epoch):
    """A ZIP timestamp (UTC) for epoch seconds; ZIP cannot hold dates before 1980."""
    return max(time.gmtime(int(epoch))[:6], (1980, 1, 1, 0, 0, 0))


def write_zip(folder, destination, date_time):
    """Write every file under folder to destination, at the ZIP root, sorted and
    with one fixed timestamp and mode, so the bytes depend on the files alone.
    Returns the ZIP's SHA-256."""
    folder = Path(folder)
    files = sorted((p for p in folder.rglob('*') if p.is_file()), key=lambda p: p.relative_to(folder).parts)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(folder).as_posix(), date_time=date_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, path.read_bytes(), compresslevel=9)
    data = buffer.getvalue()
    Path(destination).write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--package', type=Path, default=SUPPORT / 'SEST-Beta-Features.zip',
                        help='the reviewed beta package zip (default: the one the upload carries)')
    parser.add_argument('--out', required=True, type=Path, help='a new, empty toolkit folder')
    parser.add_argument('--prerequisite', default='72129cb45d3ec49d145ab323f16111089d868edb',
                        help='a commit the PC repository already has (bundle base)')
    parser.add_argument('--github-pushed', action='store_true', help='record that the branch is on GitHub')
    parser.add_argument('--zip', type=Path, help='also write the toolkit as this ZIP (a new file outside --out)')
    args = parser.parse_args()

    if git('status', '--porcelain'):
        sys.exit('The checkout has uncommitted changes; commit them first.')
    branch = git('symbolic-ref', '--short', 'HEAD')
    check_branch(branch)
    commit = git('rev-parse', 'HEAD')
    git('merge-base', '--is-ancestor', args.prerequisite, commit)
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        sys.exit(f'{out} is not empty.')
    archive = args.zip.resolve() if args.zip else None
    if archive and (archive.exists() or archive.is_relative_to(out)):
        sys.exit(f'{archive} exists or is inside the toolkit folder; name a new ZIP outside it.')

    manifest = json.loads((RELEASE / 'upload-manifest.json').read_text(encoding='utf-8'))
    support = json.loads((SUPPORT / 'manifest.json').read_text(encoding='utf-8'))
    check_support(support)
    if sha256(args.package) != support['archive_sha256']:
        sys.exit('The package is not the beta-support archive the upload carries.')
    out.mkdir(parents=True, exist_ok=True)

    copies = sorted(p.name for p in RELEASE.iterdir() if p.is_file() and (
        p.name in LAUNCHERS or p.name == 'README-FIRST.txt'
        or p.name.startswith(('R12-', BETA_DIRECTORY + '-', 'STEAM-'))))
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

    name = bundle_name(support)
    bundle = out / name
    git('bundle', 'create', str(bundle), f'^{args.prerequisite}', f'refs/heads/{branch}')
    git('bundle', 'verify', str(bundle))

    receipt = {
        'format': 1,
        'release_commit': commit,
        'release_branch': branch,
        'beta_directory': BETA_DIRECTORY,
        'workshop_bundle': {'file': name, 'sha256': sha256(bundle), 'prerequisite': args.prerequisite},
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
    if archive:
        archive.parent.mkdir(parents=True, exist_ok=True)
        digest = write_zip(out, archive, zip_date_time(git('show', '-s', '--format=%ct', commit)))
        print(f'zip {archive}: {len(files) + 1} files at the root, sha256 {digest}')


if __name__ == '__main__':
    main()
