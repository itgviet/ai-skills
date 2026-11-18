"""Write a full-size preview page for one .drawio file, with the layout checker (layout_check.js) built in.

    python scripts/preview_page.py <out.html> <diagram.drawio>

One diagram per page: __check() measures the first diagram on the page only.

The diagram is drawn at scale 1 (resize off, no toolbar), so label boxes measured by __check() are real sizes.
Serve the folder over http (e.g. a preview server running `python -m http.server <port> --directory <folder>`):
the Browser pane cannot screenshot or script file:// pages. Do not check on viewer.diagrams.net lightbox or on a
page with resize on: the diagram is scaled there and group labels measure wrong.
"""
import html
import json
import sys
from pathlib import Path

VIEWER = "https://viewer.diagrams.net/js/viewer-static.min.js"


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    out, files = Path(argv[0]), argv[1:]
    check = (Path(__file__).parent / "layout_check.js").read_text(encoding="utf-8")
    parts = []
    for f in files:
        xml = Path(f).read_text(encoding="utf-8")
        cfg = {"highlight": "#0000ff", "nav": False, "resize": False, "toolbar": "", "xml": xml}
        parts.append(f'<div class="mxgraph" data-mxgraph="{html.escape(json.dumps(cfg, ensure_ascii=False), quote=True)}"></div>')
    out.write_text('<!doctype html><meta charset="utf-8"><body style="margin:0;background:#fff">' + "".join(parts)
                   + f'<script src="{VIEWER}"></script><script>{check}</script>', encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main(sys.argv[1:])
