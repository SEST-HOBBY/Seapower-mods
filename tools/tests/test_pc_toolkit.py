"""The PC toolkit builder and the launchers it ships agree with each other.

tools/build_pc_toolkit.py extracts the beta package as R14/ and refuses a
package for another beta or game build, a branch Prepare-PC.ps1 would refuse,
and writes the toolkit ZIP the same way every time. Repair-PC.cmd, Upload-PC.ps1,
Prepare-PC.ps1 and the data installer must name the same folder and branches;
the R12-to-R13 move had to change five files by hand and nothing checked that
they agreed. Nothing is built here and no git command runs. Prepare-PC.ps1's
beta step by journal phase is run by tools/tests/test_prepare_pc.ps1.

    python3 -m unittest tools/tests/test_pc_toolkit.py
"""
import hashlib
import importlib.util
import json
import os
import re
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / 'docs' / 'releases' / '20261107'


def load_builder():
    spec = importlib.util.spec_from_file_location('build_pc_toolkit', ROOT / 'tools' / 'build_pc_toolkit.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load_builder()
R14 = {'revision': 'R14-20261114-sea-power-092-3f56861f',
       'target_game_sha256': '3f56861f09e867f315b194c81a7a2450154ccc6bb5afb769b4956dfd4a00503a'}
R13 = {'revision': 'R13-20261110-mission-awards-499675cd',
       'target_game_sha256': '499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9'}


def text(path):
    return Path(path).read_text(encoding='utf-8')


class Builder(unittest.TestCase):
    def test_beta_folder_and_game(self):
        self.assertEqual(B.BETA_DIRECTORY, 'R14')
        self.assertEqual(B.TARGET_GAME_SHA256, R14['target_game_sha256'])

    def test_bundle_name_drops_the_game_hash(self):
        self.assertEqual(B.bundle_name(R14), 'SEST-Workshop-R14-20261114-sea-power-092.bundle')
        self.assertEqual(B.bundle_name(R13), 'SEST-Workshop-R13-20261110-mission-awards.bundle')

    def test_r14_package_for_092_is_accepted(self):
        B.check_support(R14)

    def test_other_packages_are_refused_by_name(self):
        cases = [(R13, 'R13-20261110-mission-awards-499675cd'),
                 ({**R14, 'revision': 'R140-x-3f56861f'}, 'R140-x'),
                 ({**R14, 'target_game_sha256': R13['target_game_sha256']}, '0.9.2'),
                 ({}, 'unnamed')]
        for support, said in cases:
            with self.subTest(support=support), self.assertRaises(SystemExit) as stop:
                B.check_support(support)
            self.assertIn(said, str(stop.exception.code))

    def test_branches_prepare_pc_accepts(self):
        for branch in ('beta', 'dev', 'sest-dev/exciting-fermi-kb5bs9', 'release/r14-092-20261114',
                       'feature/x', 'fix/y.z', 'chore/a/b'):
            with self.subTest(branch=branch):
                B.check_branch(branch)
        for branch in ('main', 'claude/x', 'sest-dev/', 'beta2', 'release/a b', 'devx', 'x/beta'):
            with self.subTest(branch=branch), self.assertRaises(SystemExit) as stop:
                B.check_branch(branch)
            self.assertIn(branch, str(stop.exception.code))

    def test_branch_pattern_is_prepare_pcs(self):
        found = re.search(r"\$branch -notmatch '\^\((.+?)\)\$'", text(RELEASE / 'Prepare-PC.ps1'))
        self.assertIsNotNone(found, 'Prepare-PC.ps1 no longer checks the branch with -notmatch')
        self.assertEqual(found.group(1), B.BRANCH_PATTERN)

    def test_zip_date_time(self):
        self.assertEqual(B.zip_date_time(0), (1980, 1, 1, 0, 0, 0))
        self.assertEqual(B.zip_date_time('1794614400'), (2026, 11, 14, 0, 0, 0))

    def test_zip_is_rooted_sorted_and_repeatable(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'toolkit'
            for name, data in (('SOURCE-RECEIPT.json', b'{}\n'), ('R14/payload/SEST.RuntimeFixes.dll', b'MZ'),
                               ('Prepare-PC.cmd', b'@echo off\n'), ('R14/Install-SEST-Beta.ps1', b'param()\r\n'),
                               ('README-FIRST.txt', b'read me\n')):
                path = folder / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            stamp = (2026, 11, 14, 12, 0, 0)
            first = B.write_zip(folder, Path(temp) / 'a.zip', stamp)
            for path in folder.rglob('*'):
                os.utime(path, (1, 1))
            second = B.write_zip(folder, Path(temp) / 'b.zip', stamp)
            self.assertEqual(first, second)
            self.assertEqual(first, hashlib.sha256((Path(temp) / 'a.zip').read_bytes()).hexdigest())
            with zipfile.ZipFile(Path(temp) / 'a.zip') as z:
                self.assertEqual(z.namelist(), ['Prepare-PC.cmd', 'R14/Install-SEST-Beta.ps1',
                                                'R14/payload/SEST.RuntimeFixes.dll', 'README-FIRST.txt',
                                                'SOURCE-RECEIPT.json'])
                self.assertTrue(all(i.date_time == stamp and not i.is_dir() for i in z.infolist()))
                self.assertEqual(z.read('R14/Install-SEST-Beta.ps1'), b'param()\r\n')

    def test_shipped_package_is_this_toolkits_beta(self):
        support = json.loads(text(B.SUPPORT / 'manifest.json'))
        try:
            B.check_support(support)
        except SystemExit as stop:
            self.fail(f'{B.SUPPORT / "manifest.json"}: {stop.code}')


class Launchers(unittest.TestCase):
    def test_repair_pc_runs_the_beta_folder(self):
        data = (RELEASE / 'Repair-PC.cmd').read_bytes()
        self.assertIn(b'"%~dp0' + B.BETA_DIRECTORY.encode() + b'\\Repair-SEST-Beta-Startup.ps1" -Action Repair', data)

    def test_cmd_launchers_stay_lf(self):
        # Copied byte for byte into the toolkit; the index and checkout are LF.
        for path in sorted(RELEASE.glob('*.cmd')):
            with self.subTest(path=path.name):
                self.assertNotIn(b'\r', path.read_bytes())

    def test_upload_pc_wants_this_toolkit(self):
        source = text(RELEASE / 'Upload-PC.ps1')
        self.assertEqual(re.findall(r"beta_directory -ne '(R\d+)'", source), [B.BETA_DIRECTORY])
        self.assertIn(f'use the complete {B.BETA_DIRECTORY} toolkit', source)
        self.assertIn(f"beta_directory='{B.BETA_DIRECTORY}'", text(ROOT / 'tools' / 'tests' / 'test_publisher_pc.ps1'))

    def test_data_installer_accepts_this_beta(self):
        found = re.search(r"candidate_revision -notmatch '([^']+)'", text(ROOT / 'tools' / 'install-workshop-release-data.ps1'))
        self.assertIsNotNone(found)
        accepts = re.compile(found.group(1), re.IGNORECASE)
        for revision in ('R7-x', 'R13-x', B.BETA_DIRECTORY + '-x'):
            self.assertTrue(accepts.search(revision), revision)
        for revision in ('R6-x', 'R15-x', 'R140-x'):
            self.assertFalse(accepts.search(revision), revision)

    def test_prepare_pc_reads_the_beta_scripts_journal(self):
        source = text(RELEASE / 'Prepare-PC.ps1')
        self.assertIn("[string]$AppDataRoot=''", source)
        self.assertIn("GetFolderPath('LocalApplicationData')) 'SEST'", source)
        self.assertIn("J $AppDataRoot 'BetaCompatibility' 'current.json'", source)
        for step in ("'Repair-SEST-Beta-Startup.ps1') @options -Action Repair",
                     "'Install-SEST-Beta.ps1') @options -Action Stage -Quiet",
                     "'Install-SEST-Beta.ps1') @options -Action Enable"):
            self.assertIn(step, source)


if __name__ == '__main__':
    unittest.main()
