"""Build the single-file rank page: site/index.html with data/ratings.json inlined.

Standard library only; this script does not import nba_stabilization.  The JSON is
the interface between the two (see README.md).

    python site/build.py                                  # -> site/dist/rank.html
    python site/build.py --data other.json --out page.html
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLACEHOLDER = "/*__DATA__*/null"


def build(template: str, data: dict) -> str:
    """``template`` with ``data`` in place of the placeholder.  Raises ValueError if the
    page and the data have different schema versions."""
    m = re.search(r"const SCHEMA = (\d+);", template)
    if not m or template.count(PLACEHOLDER) != 1:
        raise ValueError("template has no SCHEMA constant or not exactly one data placeholder")
    if data.get("schema_version") != int(m.group(1)):
        raise ValueError(f"data schema {data.get('schema_version')} != page schema {m.group(1)}")
    # "</" would end the <script> element early; "<\/" is the same string in JavaScript
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return template.replace(PLACEHOLDER, text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, default=HERE / "data" / "ratings.json", help="output of `nba-stab export`")
    ap.add_argument("--template", type=Path, default=HERE / "index.html")
    ap.add_argument("--out", type=Path, default=HERE / "dist" / "rank.html")
    args = ap.parse_args(argv)
    if not args.data.exists():
        print(f"error: {args.data} not found. Run `nba-stab export --out {args.data}` first.", file=sys.stderr)
        return 1
    try:
        page = build(args.template.read_text(encoding="utf-8"), json.loads(args.data.read_text(encoding="utf-8")))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"{args.out}  ({args.out.stat().st_size / 1e3:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
