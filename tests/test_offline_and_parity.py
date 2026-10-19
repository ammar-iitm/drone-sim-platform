"""Offline rule (nothing fetched at run time) and browser/server roll parity."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from app import rng

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
URL = re.compile(r"https?://", re.I)


def own_files():
    for path in list((APP / "templates").rglob("*.html")) + list((APP / "static").rglob("*")):
        if path.is_file() and "vendor" not in path.parts and path.suffix in {".html", ".js", ".css", ".svg"}:
            yield path


def test_no_external_urls_in_pages_scripts_or_styles():
    offenders = []
    for path in own_files():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            # The SVG namespace is an identifier, not a fetch.
            if URL.search(line.replace("http://www.w3.org/2000/svg", "")):
                offenders.append(f"{path.relative_to(ROOT)}:{n}")
    assert offenders == []


def test_vendored_libraries_present_and_local():
    vendor = APP / "static" / "vendor"
    for name in ("three.module.js", "three.core.js", "chart.umd.min.js"):
        assert (vendor / name).stat().st_size > 100_000
    imports = re.findall(r"from\s+'([^']+)'", (vendor / "three.module.js").read_text(encoding="utf-8"))
    assert imports and all(i.startswith("./") for i in imports)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_js_and_python_rolls_match():
    cases = [(1, "C1", 0), (48213, "C7", 2), (2**31 - 1, "C12", 5), (606, "C3", 0), (0, "C1", 9)]
    script = (
        "import('" + (APP / "static/js/sim/rng.js").as_uri() + "').then(m => {"
        f"const cases = {json.dumps(cases)};"
        "console.log(JSON.stringify(cases.map(([s, id, k]) => m.rollFor(s, id, k))));});"
    )
    out = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, check=True)
    js = json.loads(out.stdout)
    py = [rng.roll(*c) for c in cases]
    assert js == py
