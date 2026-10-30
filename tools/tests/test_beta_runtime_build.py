"""Synthetic verification of build-ID and fail-closed DLL checks."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_beta_runtime_build as b


class BetaRuntimeBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.p = Path(self.temp.name)

    def file(self, name, text):
        path = self.p / name
        path.write_text(text)
        return path

    def test_same_semver_mismatched_build(self):
        ch = self.file('changelog.txt', '21-Oct-2026: 0.8.7 Build 261021 Public Release\n')
        runtime = self.file('Runtime.cs', 'const string inspected = "' + 'a' * 64 + '";')
        ui = self.file('UI.cs', 'NativeHashes = {"' + 'a'*64 + '","' + 'b'*64 + '"};\nconst string RuntimeHash = "' + 'c'*64 + '";')
        problems, notes = b.inspect('0.8.7', '261026', ch, runtime, ui)
        self.assertTrue(any('STALE' in p for p in problems))

    def test_beta_build_regex_and_missing(self):
        self.assertEqual(b.parse_build('26-Oct-2026: 0.8.7 Build 261026 Public Beta'), ('0.8.7', '261026'))
        self.assertIsNone(b.parse_build('unknown'))

    def test_disagreeing_pins(self):
        ch = self.file('changelog.txt', '26-Oct-2026: 0.8.7 Build 261026\n')
        runtime = self.file('Runtime.cs', 'const string inspected = "' + 'a' * 64 + '";')
        ui = self.file('UI.cs', 'NativeHashes = {"' + 'f'*64 + '","' + 'b'*64 + '"};\nconst string RuntimeHash = "' + 'c'*64 + '";')
        problems, notes = b.inspect('0.8.7', '261026', ch, runtime, ui)
        self.assertTrue(any('disagree' in p for p in problems))

    def test_hash_match_full_gate(self):
        ch = self.file('changelog.txt', '26-Oct-2026: 0.8.7 Build 261026\n')
        game = self.file('Game.dll', 'game bytes')
        noesis = self.file('Noesis.dll', 'noesis bytes')
        sest = self.file('Sest.dll', 'sest bytes')
        game_hash, noesis_hash, sest_hash = (b.digest(x) for x in (game,noesis,sest))
        runtime = self.file('Runtime.cs', 'const string inspected = "' + game_hash + '";')
        ui = self.file('UI.cs', 'NativeHashes = {"' + game_hash + '","' + noesis_hash + '"};\nconst string RuntimeHash = "' + sest_hash + '";')
        problems, notes = b.inspect('0.8.7', '261026', ch, runtime, ui, game, noesis, sest)
        self.assertFalse(problems, problems)
        self.assertEqual(len(notes), 4)


if __name__ == '__main__':
    unittest.main()
