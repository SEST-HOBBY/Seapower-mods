"""The PowerShell tests in this folder, run through pwsh so one command covers both suites.

Each tools/tests/test_*.ps1 is a script that exits 1 on any failed check and
prints "all checks passed" otherwise (tools/tests/test_scan_ui_assets.ps1 is
the pattern). This runs every one of them with pwsh and fails the case on a
non-zero exit, with the script's output in the message. Skipped when pwsh is
not installed, so the Python suite still runs on a machine without it; on
the gaming PC, Windows PowerShell runs the scripts directly:

    python3 -m unittest tools/tests/test_powershell_scripts.py
    pwsh -File tools/tests/test_set_mod_order.ps1
"""
import os
import shutil
import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PWSH = shutil.which("pwsh") or shutil.which("powershell")


def run(script):
    return subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(script)],
                          capture_output=True, text=True, cwd=str(HERE.parents[1]),
                          env={**os.environ, "SEST_TESTING": "1"}, timeout=600)


class PowerShellTests(unittest.TestCase):
    pass


def _case(script):
    def test(self):
        if not PWSH:
            self.skipTest("pwsh is not installed")
        r = run(script)
        self.assertEqual(r.returncode, 0, f"{script.name} exit {r.returncode}\n{r.stdout}\n{r.stderr}")
        self.assertIn("all checks passed", r.stdout, f"{script.name} did not report success\n{r.stdout}")
    return test


for _script in sorted(HERE.glob("test_*.ps1")):
    setattr(PowerShellTests, "test_" + _script.stem[len("test_"):], _case(_script))


if __name__ == "__main__":
    unittest.main()
