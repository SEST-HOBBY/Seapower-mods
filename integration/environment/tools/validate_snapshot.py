"""Conformance check for mno.environment.snapshot.v1 files (.json or .json.gz). BUILD-TESTED.

    python3 integration/environment/tools/validate_snapshot.py FILE [FILE ...]

Exit 0 when every file conforms; 1 otherwise. Prints one line per problem.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mno_env import snapshot  # noqa: E402


def main(argv=None):
    paths = argv if argv is not None else sys.argv[1:]
    if not paths:
        print(__doc__)
        return 2
    bad = 0
    for p in paths:
        try:
            errors = snapshot.validate(snapshot.read(Path(p)))
        except snapshot.SnapshotError as exc:
            errors = [str(exc)]
        for e in errors:
            print(f"{p}: {e}")
        if errors:
            bad += 1
        else:
            print(f"{p}: OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
