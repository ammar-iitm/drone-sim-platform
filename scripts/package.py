"""Build a clean zip of the project for submission or for copying to another machine.

    python scripts/package.py                  # dist/drone-threat-trainer-<date>.zip
    python scripts/package.py --with-archive   # also include archive/ (the earlier prototype)

Includes every file git tracks or would track (so no .venv, node_modules or caches), without the demo
database, test screenshots or archive by default. Run start.sh --demo (or start.bat --demo)
after unzipping to rebuild a demo cohort.
"""

import argparse
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_ALWAYS = ("data/", "test-results/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-archive", action="store_true")
    parser.add_argument("--out", default=str(ROOT / "dist"))
    args = parser.parse_args()
    # Tracked files plus new files that are not ignored, so uncommitted work is not silently left out.
    files = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split()
    files = sorted(f for f in set(files) if (ROOT / f).is_file())
    skip = SKIP_ALWAYS + (() if args.with_archive else ("archive/",))
    files = [f for f in files if not f.startswith(skip)]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"drone-threat-trainer-{date.today().isoformat()}"
    target = out_dir / f"{name}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            info = zipfile.ZipInfo.from_file(ROOT / f, f"{name}/{f}")
            if f in ("start.sh",):
                info.external_attr = 0o755 << 16
            with open(ROOT / f, "rb") as fh:
                zf.writestr(info, fh.read(), zipfile.ZIP_DEFLATED)
    size = target.stat().st_size / 1e6
    print(f"{target} ({len(files)} files, {size:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
