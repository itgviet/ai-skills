# /// script
# requires-python = ">=3.10"
# ///
"""Build a one-page task-card user guide from guide.config.json + a content file.

Usage:
  python scripts/build_guide.py --config <project>/guide.config.json        # writes the page named in "output"
  python scripts/build_guide.py --config <cfg> --check                       # structure checks only, no output
  python scripts/build_guide.py --init <folder>                              # start a project from the template

Structure checks (errors stop the build, exit 1): duplicate or missing ids on cards, data-flow values not in
"flows", images that do not exist, pin numbers in data-hp that match no step number in the same card, bad
data-hp / data-crop syntax. Warnings (printed, build goes on): cards without a figure, steps not starting
with an action word list ("Để ", "Nếu ") .
Output: a complete HTML document (doctype, charset) with CSS/JS inlined; every image it uses is copied next to it.
"""
import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL / 'assets' / 'template'
DEFAULT_LABELS = {
    'vi': {'next': 'Tiếp theo', 'noResult': 'Không tìm thấy', 'search': 'Tìm trong hướng dẫn (/)', 'toc': 'Mục lục',
           'pickFlow': 'Bạn đang làm việc nào?', 'top': 'Lên đầu trang', 'all': 'Tất cả'},
    'en': {'next': 'Next', 'noResult': 'No result', 'search': 'Search the guide (/)', 'toc': 'Contents',
           'pickFlow': 'What are you working on?', 'top': 'Back to top', 'all': 'All'},
}
ACTION_SMELLS = ('Để ', 'Nếu ', 'Bạn có thể ')


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def init(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    for name in ('guide.config.example.json', 'content.example.html'):
        dst = folder / name.replace('.example', '')
        if dst.exists():
            fail(f'{dst} already exists; not overwriting')
        shutil.copy(TEMPLATE / name, dst)
    (folder / 'img').mkdir(exist_ok=True)
    shutil.copy(TEMPLATE / 'example-screen.png', folder / 'img' / 'example-screen.png')  # the example content points at it
    print(json.dumps({'created': [str(folder / 'guide.config.json'), str(folder / 'content.html'), str(folder / 'img')]}, ensure_ascii=False))


def cards_of(body: str):
    """(card_html, h3_id, flow) for every task card, in order."""
    out = []
    for m in re.finditer(r'<div class="card"([^>]*)>(.*?)</div><!--/card-->', body, re.S):
        attrs, inner = m.group(1), m.group(2)
        h = re.search(r'<h3 id="([^"]*)"', inner)
        f = re.search(r'data-flow="([^"]+)"', attrs)
        out.append((inner, h.group(1) if h else None, f.group(1) if f else None, m.start()))
    return out


def step_numbers(card: str) -> set[int]:
    nums = set()
    for m in re.finditer(r'<ol class="proc"([^>]*)>(.*?)</ol>', card, re.S):
        start = re.search(r'counter-reset:\s*s\s+(\d+)', m.group(1))
        k = int(start.group(1)) if start else 0
        for _ in re.finditer(r'<li\b', m.group(2)):
            k += 1
            nums.add(k)
    return nums


def image_size(path: Path):
    """(width, height) from the file header for png / jpeg / gif / webp, without Pillow; None if unknown."""
    b = path.read_bytes()[:256 * 1024]
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        return int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big')
    if b[:6] in (b'GIF87a', b'GIF89a'):
        return int.from_bytes(b[6:8], 'little'), int.from_bytes(b[8:10], 'little')
    if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
        k = b[12:16]
        if k == b'VP8 ':
            return int.from_bytes(b[26:28], 'little') & 0x3fff, int.from_bytes(b[28:30], 'little') & 0x3fff
        if k == b'VP8L':
            v = int.from_bytes(b[21:25], 'little')
            return (v & 0x3fff) + 1, ((v >> 14) & 0x3fff) + 1
        if k == b'VP8X':
            return int.from_bytes(b[24:27], 'little') + 1, int.from_bytes(b[27:30], 'little') + 1
    if b[:2] == b'\xff\xd8':
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return int.from_bytes(b[i + 7:i + 9], 'big'), int.from_bytes(b[i + 5:i + 7], 'big')
            i += 2 + int.from_bytes(b[i + 2:i + 4], 'big')
    return None


def fix_sizes(body: str, root: Path):
    """width/height on every <img> set from the real file: crops, phone frames and the layout all depend on them."""
    notes = []

    def one(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        f = root / src
        if re.match(r'^(?:[a-z]+:|//|data:)', src) or not f.is_file():
            return tag
        size = image_size(f)
        if not size:
            return tag
        w, h = re.search(r'\swidth="(\d+)"', tag), re.search(r'\sheight="(\d+)"', tag)
        if w and h and (int(w.group(1)), int(h.group(1))) == size:
            return tag
        notes.append(f'{src}: width/height set to the real {size[0]}x{size[1]}' + (f' (was {w.group(1)}x{h.group(1)})' if w and h else ''))
        tag = re.sub(r'\s(?:width|height)="\d*"', '', tag)
        return tag.replace('<img', f'<img width="{size[0]}" height="{size[1]}"', 1)
    return re.sub(r'<img\b[^>]*>', one, body), notes


def check(body: str, root: Path, flows: list[str], lang: str = 'vi'):
    errors, warnings = [], []
    # layout comes from the template's classes; inline styles were how a past guide hid a missing pattern
    for m in re.finditer(r'<(\w+)[^>]*\sstyle="([^"]*)"', body):
        if not re.fullmatch(r'\s*counter-reset:\s*s\s+\d+;?\s*', m.group(2)):
            errors.append(f'inline style on <{m.group(1)} style="{m.group(2)[:40]}">: use a template class (figure.photo, .phones, .dialog...) instead')
    ids = re.findall(r'\sid="([^"]+)"', body)
    for i in sorted({x for x in ids if ids.count(x) > 1}):
        errors.append(f'duplicate id "{i}"')
    for f in sorted(set(re.findall(r'data-flow="([^"]+)"', body)) - set(flows) - {'all'}):
        errors.append(f'data-flow="{f}" is not one of the flows in guide.config.json ({", ".join(flows) or "none"})')
    for src in sorted(set(re.findall(r'<img[^>]+src="([^"]+)"', body))):
        if not re.match(r'^(?:[a-z]+:|//|data:)', src) and not (root / src).is_file():
            errors.append(f'image not found: {src}')
    for card, hid, _, _ in cards_of(body):
        name = hid or '(card without h3 id)'
        if not hid:
            errors.append('a card has no <h3 id="...">')
        steps = step_numbers(card)
        for fig in re.finditer(r'<figure\b([^>]*)>(.*?)</figure>', card, re.S):
            tag, inner = fig.group(0)[:fig.group(0).index('>') + 1], fig.group(2)
            m_cls = re.search(r'class="([^"]*)"', tag)
            cls = m_cls.group(1).split() if m_cls else []
            hp = re.search(r'data-hp="([^"]*)"', tag)
            crop = re.search(r'data-crop="([^"]*)"', tag)
            img = re.search(r'<img\b[^>]*>', inner)
            img_tag = img.group(0) if img else ''
            m_alt, m_src = re.search(r'alt="([^"]*)"', img_tag), re.search(r'src="([^"]*)"', img_tag)
            alt, src = (m_alt.group(1) if m_alt else ''), (m_src.group(1) if m_src else '')
            m_cap = re.search(r'<figcaption>(.*?)</figcaption>', inner, re.S)
            cap = re.sub(r'<[^>]+>', '', m_cap.group(1)) if m_cap else ''
            kind = 'photo' if 'photo' in cls else 'diagram' if 'diagram' in cls else 'shot'
            # a screenshot beside numbered steps must show where each step happens
            if kind == 'shot' and img and len(steps) >= 2 and not hp and 'annotated' not in cls:
                errors.append(f'#{name}: screenshot {src} has no pins for steps {min(steps)}–{max(steps)}: add data-hp, or class "annotated" '
                              f'if the image already carries numbers that match the steps, or "photo" for an illustration')
            if 'annotated' in cls:
                warnings.append(f'#{name}: annotated image: check every number drawn in it equals the step it marks, and that its marks look like the '
                                f'guide\'s pins; a clean source image + data-hp is better')
            if kind == 'photo' and lang == 'vi' and not cap.strip().startswith('Ảnh minh họa'):
                warnings.append(f'#{name}: illustration photo without a caption starting "Ảnh minh họa"')
            if alt and cap and re.sub(r'\W+', '', alt.lower()) == re.sub(r'\W+', '', cap.lower()):
                warnings.append(f'#{name}: caption repeats the alt text "{cap[:40]}": say what the reader should see, or drop the caption')
            # only beside the steps (inside .grid-2) is a full screen squeezed; under them it gets the card's full width
            seg = card[:fig.start()]
            g = seg.rfind('<div class="grid-2">')
            beside = g >= 0 and seg[g:].count('<div') > seg[g:].count('</div>')
            if kind == 'shot' and img and beside and not crop and not ({'phone', 'dialog'} & set(cls)):
                w = re.search(r'\swidth="(\d+)"', img.group(0))
                if w and int(w.group(1)) >= 1200:
                    warnings.append(f'#{name}: full {w.group(1)} px screen without data-crop: beside the steps it shows at ~1/3 size and its text cannot be read; '
                                    f'crop to the area the steps use')
            if crop:
                v = crop.group(1).split(',')
                if len(v) != 4 or not all(re.fullmatch(r'-?\d+(\.\d+)?', x.strip()) for x in v) or float(v[0]) >= float(v[2]) or float(v[1]) >= float(v[3]):
                    errors.append(f'#{name}: bad data-crop "{crop.group(1)}" (x0,y0,x1,y1 in %, x0<x1, y0<y1)')
            if not hp:
                continue
            for item in filter(None, hp.group(1).split(';')):
                parts = item.split(':')
                if len(parts) < 2 or not parts[0].isdigit():
                    errors.append(f'#{name}: bad data-hp item "{item}"')
                    continue
                spec = parts[1]
                if not (spec.startswith('@') or re.fullmatch(r'-?[\d.]+(,-?[\d.]+){1}|-?[\d.]+(,-?[\d.]+){3}', spec)):
                    errors.append(f'#{name}: bad data-hp box "{item}"')
                if steps and int(parts[0]) not in steps:
                    errors.append(f'#{name}: pin {parts[0]} has no step {parts[0]} in this card (steps {min(steps)}–{max(steps)})')
        for b in re.findall(r'<li><div><b>(.*?)</b>', card):
            text = re.sub(r'<[^>]+>', '', b)
            if text.startswith(ACTION_SMELLS):
                warnings.append(f'#{name}: step starts with a condition, not an action: "{text[:60]}"')
        if 'class="proc"' in card and '<figure' not in card and 'FIG:' not in card:
            warnings.append(f'#{name}: steps without a picture')
    return errors, warnings


def build(cfg_path: Path, only_check: bool):
    cfg = json.loads(cfg_path.read_text('utf8'))
    root = cfg_path.parent
    lang = cfg.get('lang', 'vi')
    labels = {**DEFAULT_LABELS.get(lang, DEFAULT_LABELS['en']), **cfg.get('labels', {})}
    flows = cfg.get('flows', [])
    flow_ids = [f['id'] for f in flows]
    src = (root / cfg['content']).read_text('utf8')
    src = re.sub(r'^\s*<!--.*?-->', '', src, count=1, flags=re.S)  # the authoring note at the top quotes markup
    body = src[src.index('<section'):] if '<section' in src else src
    body, size_notes = fix_sizes(body, root)
    errors, warnings = check(body, root, flow_ids, lang)
    report = {'errors': errors, 'warnings': warnings, 'fixed': size_notes}
    if errors or only_check:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 1 if errors else 0

    # contents: chapters and their cards, flow-tagged so the same CSS hides them
    toc = []
    for ch in re.finditer(r'<section class="chapter" id="([^"]+)"([^>]*)>\s*<div class="ch-head"><h2>(.*?)</h2>', body, re.S):
        cid, attrs, title = ch.group(1), ch.group(2), ch.group(3)
        f = re.search(r'data-flow="([^"]+)"', attrs)
        end = body.find('<section class="chapter"', ch.end())
        part = body[ch.end(): end if end > 0 else len(body)]
        items = ''.join(
            f'<li{f" data-flow={chr(34)}{cf}{chr(34)}" if cf else ""}><a href="#{hid}"><span class="num"></span>{html.escape(re.sub("<[^>]+>", "", re.search(r"<h3[^>]*>(.*?)</h3>", c, re.S).group(1)))}</a></li>'
            for c, hid, cf, _ in cards_of(part) if hid)
        toc.append(f'<li{f" data-flow={chr(34)}{f.group(1)}{chr(34)}" if f else ""}><a href="#{cid}"><span class="num"></span>{title}</a><ol>{items}</ol></li>')

    # one rule per pair of flows; before a flow is picked, inline wording shows only the first flow's variant
    flow_css = ''.join(f'html[data-flow="{a}"] [data-flow="{b}"] {{ display: none !important; }}\n'
                       for a in flow_ids for b in flow_ids if a != b)
    if flow_ids:
        flow_css += f'html:not([data-flow]) .fl[data-flow]:not([data-flow="{flow_ids[0]}"]) {{ display: none !important; }}\n'
    brand = cfg.get('brand', {})
    tokens = ''.join(f'--{k}: {v}; ' for k, v in {'brand': brand.get('primary'), 'brand-soft': brand.get('soft'),
                                                    'brand-ink': brand.get('ink', brand.get('primary')), 'tip-bg': brand.get('soft')}.items() if v)
    css = (TEMPLATE / 'guide.css').read_text('utf8') + (f':root {{ {tokens}}}\n' if tokens else '') + flow_css + cfg.get('extraCss', '')
    marks = json.loads((root / cfg['marks']).read_text('utf8')) if cfg.get('marks') else {}
    runtime = {'flows': [{'id': f['id'], 'label': f['label']} for f in flows], 'labels': labels, 'marks': marks,
               'storageKey': cfg.get('storageKey', re.sub(r'\W+', '-', cfg.get('product', 'guide').lower()) + '-flow')}

    switch = ''.join(f'<button type="button" data-pick="{f["id"]}" aria-pressed="false">{html.escape(f["label"])}</button>' for f in flows)
    tiles = ''.join(
        f'<button type="button" class="fw" data-pick="{f["id"]}" aria-pressed="false"><span class="ic">{html.escape(f.get("icon", f["label"][:1]))}</span>'
        f'<span><b>{html.escape(f["label"])}</b><small>{html.escape(f.get("desc", ""))}</small></span><span class="go"></span></button>' for f in flows)
    t = html.escape(cfg['title'])
    page = f'''<!doctype html>
<html lang="{lang}" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{t}</title>
<style>
{css}</style>
</head>
<body>
<header class="topbar"><div class="in">
  <a class="brand" href="#top">{t}</a>
  <div class="search"><input type="search" placeholder="{html.escape(labels['search'])}" aria-label="{html.escape(labels['search'])}"><div class="results" role="listbox"></div></div>
  {f'<div class="flow-switch" role="group">{switch}</div>' if flows else ''}
</div></header>
<section class="cover" id="top"><div class="in">
  <h1>{t}</h1>
  {f'<p class="lede">{cfg["lede"]}</p>' if cfg.get('lede') else ''}
  {f'<p class="pick-q"><b>{html.escape(labels["pickFlow"])}</b></p><div class="flows">{tiles}</div>' if flows else ''}
</div></section>
<div class="shell">
<aside class="toc"><details open><summary>{html.escape(labels['toc'])}</summary><ol>{''.join(toc)}</ol></details></aside>
<main>
{body}
<footer class="foot">{cfg.get('footer', t)}</footer>
</main>
</div>
<button class="to-top" type="button" aria-label="{html.escape(labels['top'])}">↑</button>
<script>window.GUIDE = {json.dumps(runtime, ensure_ascii=False)};</script>
<script>
{(TEMPLATE / 'guide.js').read_text('utf8')}</script>
</body>
</html>
'''
    out = (root / cfg.get('output', 'dist/guide.html')).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, 'utf8')
    copied = 0
    if out.parent != root.resolve():
        for s in sorted(set(re.findall(r'<img[^>]+src="([^"]+)"', body))):
            if re.match(r'^(?:[a-z]+:|//|data:)', s):
                continue
            dst = out.parent / s
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / s, dst)
            copied += 1
    report.update({'output': str(out), 'bytes': out.stat().st_size, 'images_copied': copied, 'cards': len(cards_of(body))})
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', type=Path)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--init', type=Path, metavar='FOLDER')
    a = ap.parse_args()
    if a.init:
        init(a.init)
        return 0
    if not a.config or not a.config.is_file():
        fail('need --config <guide.config.json> (or --init <folder> to start one)')
    return build(a.config, a.check)


if __name__ == '__main__':
    sys.exit(main())
