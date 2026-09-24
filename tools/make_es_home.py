#!/usr/bin/env python3
"""Generate src/pages/es/index.html from the English home page + tools/translations_home_es.py.

Run after editing the English home page, then add/adjust pairs for any new text:
    python3 tools/make_es_home.py && python3 tools/build.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from translations_home_es import PAIRS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "src/pages/index.html").read_text()
src = re.sub(r'"path": "/"(, "alt": "/es/")?', '"path": "/es/", "alt": "/"', src, count=1)
missing = []
for en, es in PAIRS:
    if en not in src:
        missing.append(en[:80])
        continue
    src = src.replace(en, es)
if missing:
    sys.exit("English strings not found (update translations_home_es.py):\n  " + "\n  ".join(missing))
# point the English home page at its Spanish counterpart
en_path = ROOT / "src/pages/index.html"
en = en_path.read_text()
if '"alt": "/es/"' not in en:
    en_path.write_text(en.replace('<!--META {"path": "/",', '<!--META {"path": "/", "alt": "/es/",', 1))
src = re.sub(r"\n{3,}", "\n\n", src)
(ROOT / "src/pages/es").mkdir(exist_ok=True)
(ROOT / "src/pages/es/index.html").write_text(src)
print("wrote src/pages/es/index.html")
