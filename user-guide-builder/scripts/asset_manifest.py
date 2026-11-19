# /// script
# requires-python = ">=3.10"
# ///
"""List every local file a guide page references, and compare it with what is published.

Why: publishing an Artifact sends only the HTML. Images added or edited later stay missing or stale online
while local screenshots look fine. Run this before calling a version done.

Usage:
  python scripts/asset_manifest.py <page.html>                       # JSON list: path, bytes, sha256
  python scripts/asset_manifest.py <page.html> --published list.txt  # compare with a published file listing
  python scripts/asset_manifest.py <page.html> --published list.txt --files-arg
                                                                     # also print the `files` map to re-publish

list.txt: paste of the Artifact "files" listing; any line holding `"<path>" ... <N> bytes` is read.
Exit codes: 0 all in sync, 1 missing/stale files found, 2 usage error.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REF = re.compile(r'''(?:src|href|data-src|poster)\s*=\s*["']([^"'#?]+)["']|url\(\s*["']?([^"')#?]+)["']?\s*\)''', re.I)


def referenced(page: Path) -> list[str]:
    html = page.read_text(encoding="utf-8")
    out = set()
    for m in REF.finditer(html):
        ref = m.group(1) or m.group(2)
        if re.match(r"^(?:[a-z]+:|//|data:)", ref, re.I) or ref.endswith(".html"):
            continue
        out.add(ref.lstrip("./"))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", type=Path)
    ap.add_argument("--published", type=Path, help="text file with the published files listing")
    ap.add_argument("--files-arg", action="store_true", help="print the files map for the out-of-sync paths")
    a = ap.parse_args()
    if not a.page.is_file():
        print(f"page not found: {a.page}", file=sys.stderr)
        return 2
    root = a.page.parent
    rows = []
    for ref in referenced(a.page):
        f = root / ref
        if f.is_file():
            data = f.read_bytes()
            rows.append({"path": ref, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()[:16]})
        else:
            rows.append({"path": ref, "bytes": None, "note": "missing locally"})
    if not a.published:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 1 if any(r["bytes"] is None for r in rows) else 0

    pub = {}
    for line in a.published.read_text(encoding="utf-8").splitlines():
        m = re.search(r'"([^"]+)"\s.*?(\d+)\s+bytes', line)
        if m:
            pub[m.group(1)] = int(m.group(2))
    diff = []
    for r in rows:
        if r["bytes"] is None:
            diff.append({**r, "state": "missing locally"})
        elif r["path"] not in pub:
            diff.append({**r, "state": "not published"})
        elif pub[r["path"]] != r["bytes"]:
            diff.append({**r, "state": f"stale online ({pub[r['path']]} bytes)"})
    json.dump({"referenced": len(rows), "published": len(pub), "out_of_sync": diff}, sys.stdout, ensure_ascii=False, indent=1)
    print()
    if a.files_arg and diff:
        files = {d["path"]: str((root / d["path"]).resolve()) for d in diff if d["bytes"] is not None}
        print(json.dumps(files, ensure_ascii=False))
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main())
