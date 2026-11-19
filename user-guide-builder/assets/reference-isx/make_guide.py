"""The task-card user guide (Vietnamese), in the current guide's own page shell.

Content: proto/body-vi.html (hand-written task cards). Shell, styles and scripts: src/vi.html, src/guide.css,
src/guide.js, assets/marks.js. Blocks marked <!--FIG:name--> are copied from src/vi.html so text and diagrams stay
the same as the current guide. Writes proto/khung-vi.html and copies every image it uses under proto/assets/.
Touches neither src/ nor dist/."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'proto'
SRC = (ROOT / 'src/vi.html').read_text('utf8')
BODY = (OUT / 'body-vi.html').read_text('utf8')
BODY = BODY[BODY.index('<section'):]  # drop the authoring note at the top


def block(start, tag, after=None):
    """The element that begins with `start` (after the text `after`, if given), with its nested children."""
    i = SRC.index(start, SRC.index(after) if after else 0)
    depth = 0
    for m in re.finditer(rf'<{tag}[\s>]|</{tag}>', SRC[i:]):
        depth += -1 if m.group(0).startswith('</') else 1
        if depth == 0:
            return SRC[i:i + m.end()]
    raise ValueError(start)


def between(a, b):
    i = SRC.index(a) + len(a)
    return SRC[i:SRC.index(b, i)]


TOOLS_HP = ';'.join(f'{n}:@{n}:r' for n in range(1, 10))
files_start = SRC.index('<div class="tbl"><table>', SRC.index('<h3>Định dạng và nơi xuất</h3>'))
FIGS = {
    'zones': block('<figure class="diagram zones">', 'figure'),
    'check': '<div class="prereq solo"><div>' + block('<ul class="check">', 'ul').replace(' bên dưới.', '.') + '</div></div>',
    'compare-real': block('<div class="compare real">', 'div'),
    'status': block('<figure class="diagram fdg">', 'figure', '<h3>Trạng thái bản quét</h3>'),
    'ifc-flow': block('<figure class="diagram fdg ifc-flow">', 'figure'),
    'issue-status': block('<figure class="diagram fdg">', 'figure', '<h3>Các trạng thái</h3>'),
    'dashboard': block('<figure class="shot" data-shot="dashboard"', 'figure'),
    'data-org': block('<figure class="diagram fdg">', 'figure', '<h3>Cách dữ liệu được sắp xếp</h3>'),
    'viewer': block('<figure class="shot" data-shot="viewer">', 'figure'),
    'modes-table': block('<div class="tbl wide">', 'div', '<h3>Chế độ xem</h3>').replace('class="tbl wide"', 'class="tbl wide stack"', 1)
        .replace('<tr><td>BIM</td>', '<tr data-flow="ks"><td>BIM</td>').replace('<tr><td>Mặt bằng 2D</td>', '<tr data-flow="ks"><td>Mặt bằng 2D</td>')
        .replace('<td>Hình dung không gian như đang đứng tại chỗ</td></tr>', '<td>Hình dung không gian như đang đứng tại chỗ</td></tr>'
                 '<tr><td>Street View</td><td>Đi trong mô hình ở tầm mắt người: bấm xuống sàn để đi tới chỗ đó, kéo để xoay</td>'
                 '<td>Xem không gian như đang đi trong công trình</td></tr>', 1),
    'viewer-tools': block('<figure class="shot" data-shot="viewer-tools">', 'figure').replace(
        'data-shot="viewer-tools"', f'data-ref="viewer-tools" data-hp="{TOOLS_HP}"'),
    'join': between('<h3>Ghép khu vực hoạt động thế nào</h3>', '<h3>In marker</h3>'),
    'files': SRC[files_start:SRC.index('<h3>Mở file IFC', files_start)],
    'glossary': block('<div class="tbl wide">', 'div', '<h3>Từ ngữ hay gặp</h3>').replace('<tr><td>RoomPlan</td>', '<tr data-flow="ks"><td>RoomPlan</td>', 1),
    'security': block('<ol class="layers">', 'ol'),
    'devices': '<div class="prereq solo"><div>' + SRC[SRC.index('<h4>Thiết bị</h4>'):SRC.index('</ul>', SRC.index('Lý do yêu cầu thiết bị')) + 5] + '</div></div>',
}
body = re.sub(r'<!--FIG:([\w-]+)-->', lambda m: FIGS[m.group(1)], BODY)

# links into the old chapters point at the matching task or reference section
LINKS = {
    'chuan-bi': 'dan-marker', 'chuan-bi-in-marker': 'in-marker', 'chuan-bi-chia-khu-vuc-va-dan-marker': 'dan-marker',
    'chuan-bi-dieu-kien-truoc-khi-ra-cong-trinh': 'tc-thiet-bi', 'quet-cach-cam-may-va-di-chuyen': 'quet-khu-vuc',
    'quet-sau-khi-quet': 'xem-truoc', 'mep': 'trich-xuat-mep', 'xuat': 'tc-file', 'tai-len': 'tai-len-may-tinh',
    'tai-len-gop-nhieu-ban-quet-thanh-mot': 'gop-ban-quet', 'xuat-mo-file-ifc-trong-rebro-va-revit': 'xuat-ifc-mep',
    'to-chuc': 'quan-tri', 'to-chuc-vai-tro-truy-cap-va-han-muc': 'vai-tro-han-muc', 'tai-khoan': 'dang-ky',
    'tai-khoan-ho-so-va-bao-mat': 'bao-mat-tai-khoan', 'xem-3d-thanh-cong-cu': 'tc-cong-cu', 'du-an': 'tao-du-an',
    'chuc-nang': 'tao-du-an', 'quy-trinh': 'bat-dau',
}
TITLES = dict(re.findall(r'<h3 id="([\w-]+)">([^<]+)</h3>', body))


def relink(m):
    """A link into an old chapter goes to the matching new section and takes that section's name."""
    old, text = m.group(1), m.group(2)
    new = LINKS.get(old, old)
    if old in LINKS and new in TITLES and '<' not in text:
        text = TITLES[new]
    return f'<a href="#{new}">{text}</a>'


body = re.sub(r'<a href="#([\w-]+)">(.*?)</a>', relink, body)
# as in the release build: no internal notes, unconfirmed facts shipped as plain text
body = re.sub(r'\s*<div class="todo"[^>]*>.*?</div>', '', body, flags=re.S)
body = re.sub(r'\s*<span class="verify">.*?</span>', '', body, flags=re.S)  # unconfirmed claims stay out
body = re.sub(r'href="#([\w-]+)"', lambda m: 'href="#' + LINKS.get(m.group(1), m.group(1)) + '"', body)
# a FAQ item or table row that points into one flow only is shown in that flow only
ONLY = {'mep': ('trich-xuat-mep', 'xem-mep', 'chinh-sua', 'ra-soat', 'sua-ong', 'kiem-tra-luu', 'xuat-ifc-mep'),
        'ks': ('xem-bim', 'xuat-bim')}


def tag_flow(m):
    for flow, ids in ONLY.items():
        if any(f'href="#{i}"' in m.group(0) for i in ids):
            return f'<{m.group(1)} data-flow="{flow}">' + m.group(0)[len(m.group(1)) + 2:]
    return m.group(0)


body = re.sub(r'<(details|tr)>(?:(?!</\1>).)*?</\1>', tag_flow, body, flags=re.S)

# ---- shell: head, top bar, cover from src/vi.html; the cover's "Bắt đầu từ đâu" becomes the flow choice ----
shell = SRC[:SRC.index('<aside class="toc">')]
shell = re.sub(r'\s*<div class="start">.*?</ul>\s*</div>', '', shell, count=1, flags=re.S)
# the two flow cards on the cover are the choice: question on top, each card clickable with its own button
fig_at = shell.index('<figure class="flows"')
fig_end = shell.index('</figure>', fig_at)
fig = shell[fig_at:fig_end]
for key in ('mep', 'ks'):
    fig = fig.replace('<div class="fw">', f'<div class="fw pickable" data-pick="{key}" role="button" tabindex="0" aria-pressed="false">', 1)
fig = fig.replace('<div class="fw pickable"', '<p class="fw-q">Bạn đang làm dự án loại nào?</p><div class="fw pickable"', 1)
shell = shell[:fig_at] + fig + shell[fig_end:]
shell = shell.replace('href="#quy-trinh"', 'href="#bat-dau"')
shell = re.sub(r'\s*<a href="ja.html">日本語</a>\s*<a href="en.html">EN</a>', '', shell)
shell = shell.replace('<nav class="lang"', '''<div class="flow-switch" role="group" aria-label="Loại dự án">
      <button type="button" data-pick="mep">MEP</button><button type="button" data-pick="ks">Khảo sát</button>
    </div>
    <nav class="lang"''', 1)
# the shell's own pictures (logo, QR, cover photo) travel with the page
for src in []:
    dst = OUT / src
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / src, dst)


EXTRA = '''
/* task cards inside the guide */
.card-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; margin-top: -14px; font-size: var(--step--1); color: var(--muted); }
.pill.mep { background: #e3e8fb; color: #132b88; } .pill.ks { background: var(--tip-bg); color: var(--tip-ink); }
.chapter .note ul { padding-left: 1.2em; gap: 2px; }
.branch { display: grid; gap: 14px; max-width: 64rem; align-items: start; }
@media (min-width: 900px) { .branch { grid-template-columns: 1fr 1fr; } }
.arm { border: 1px solid var(--line); border-radius: var(--radius); background: var(--paper); padding: 14px 16px; display: grid; gap: 14px; align-content: start; }
.arm-h { font: 600 var(--step-0) var(--f-display); color: var(--brand-ink); }
.arm .phones { margin: 0; }
.ends { display: grid; gap: 10px; }
.note { align-content: start; }
.nw { white-space: nowrap; }
.flows .il-flange { fill: #a8236e; stroke: #fff; stroke-width: 1; }
/* zones plan: the "> 1 m" label sits on the dashed zone border; a halo keeps it readable */
.zones .zn-gap-t { paint-order: stroke; stroke: #fff; stroke-width: 4px; stroke-linejoin: round; }
/* IFC flow: Rebro and Revit are alternatives, so no arrow from one to the other, only the word "hoặc" */
.ifc-flow .fd-link { border-left: 0 !important; }
.ifc-flow .fd-link::before { display: none !important; }
/* the zone plan keeps a readable size on phones: it scrolls sideways instead of shrinking its labels to 5 px */
@media (max-width: 640px) {
  .chapter .card figure.diagram.zones { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .chapter .card .zones > svg { min-width: 600px !important; width: 600px !important; height: auto !important; display: block; }
}
/* stacked (narrow) layout: the alternative target lines up with the first one, "hoặc" centred between them */
@media (max-width: 640px) {
  .ifc-flow .fd-br { margin-left: 0 !important; padding-left: 0 !important; }
  .ifc-flow .fd-br > .fd-n { margin-left: 0 !important; width: auto !important; }
  .ifc-flow .fd-link { display: block; text-align: center; margin: 0 !important; padding: 6px 0 !important; }
}
/* before a flow is picked both flows' cards show, but a sentence holds only one of its two wordings (the MEP one),
   or "phòng bơm" and "một sàn văn phòng" would run together */
html:not([data-flow]) main .card [data-flow="ks"][data-flow][data-flow][data-flow] { display: none !important; }
i.fl { font-style: normal; }  /* inline flow-specific words inside a step hint (a span there would become a block) */
/* phones: the top bar wraps to three rows, so a jump leaves room for it above the heading */
@media (max-width: 700px) { html { scroll-padding-top: calc(var(--topbar-h, 132px) + 12px) !important; } }
/* print: Chrome sometimes drops a zoomed crop at a page break, so paper shows the whole screenshot; the pins are
   placed in % of the full image, so they stay on their elements */
@media print {
  .frame.cropped { aspect-ratio: auto !important; height: auto !important; }
  .frame.cropped > .zoom { position: relative !important; left: 0 !important; top: 0 !important; width: 100% !important; height: auto !important; }
  .frame.cropped > .zoom > img { position: static !important; width: 100% !important; height: auto !important; }
}
@media print { .card > .next { display: none !important; } details::details-content { content-visibility: visible !important; display: block !important; } .faq details > div { display: block !important; } }
.chapter .card .zones > svg { min-width: 0; width: 100%; height: auto; }  /* the whole plan fits on a phone instead of scrolling */
@media (min-width: 900px) { .ends { grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); max-width: 64rem; } }
.more a, .next a { font-weight: 600; }
.next:empty { display: none; }
.next { padding-bottom: 10px; border-bottom: 1px dashed var(--line); }
.frame.photo img { aspect-ratio: auto; }
.todo.review { margin: 24px 0 0; }
/* flow choice */
.flow-switch { display: inline-flex; border: 1px solid var(--line); border-radius: 999px; overflow: hidden; flex: none; }
.flow-switch button { font: 600 var(--step--1) var(--f-body); color: var(--muted); background: transparent; border: 0; padding: 5px 10px; cursor: pointer; }
.flow-switch button[aria-pressed="true"] { background: var(--brand); color: #fff; }
.phones .frame .pin { width: 16px; height: 16px; font-size: 9px; border-width: 1.5px; }
/* repeated attribute: must outrank the card layout rules that force display: grid */
html[data-flow="mep"] [data-flow="ks"][data-flow][data-flow][data-flow][data-flow], html[data-flow="ks"] [data-flow="mep"][data-flow][data-flow][data-flow][data-flow] { display: none !important; }
/* cover: the two flow cards are the choice */
.cover > .flows { align-content: center; grid-template-rows: auto auto auto !important; }
.fw-q { font: 700 var(--step-2) var(--f-display); color: var(--ink); }
.fw.pickable { cursor: pointer; background: var(--paper); border: 2px solid var(--line); border-radius: calc(var(--radius) + 4px);
  padding: 16px 18px 18px; transition: border-color .15s, box-shadow .15s, opacity .15s, transform .15s; }
.fw.pickable:hover, .fw.pickable:focus-visible { border-color: var(--brand); outline: none; transform: translateY(-2px); box-shadow: var(--shadow); }
.fw.pickable[aria-pressed="true"] { border-color: var(--brand); box-shadow: 0 0 0 4px var(--brand-soft), var(--shadow); }
/* phones: the two cards sit side by side, each flow reads top to bottom, so both choices are on one screen */
@media (max-width: 700px) {
  .cover > .flows { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); grid-template-rows: auto auto !important; gap: 10px; }
  .fw-q { grid-column: 1 / -1; font-size: var(--step-1); }
  .fw.pickable { padding: 10px 10px 12px; gap: 8px; align-content: start; }
  .fw-t { display: grid; gap: 2px; font-size: var(--step--2); }
  .fw-t .pill { justify-self: start; }
  .fw-steps { grid-template-columns: minmax(0, 1fr); gap: 16px; }
  .fw-steps li:not(:last-child)::after { content: "↓"; right: auto; left: 50%; top: auto; bottom: -18px; transform: translateX(-50%); width: 16px; height: 16px; font-size: 10px; }
  .fw-img { aspect-ratio: 16 / 9; }
  .fw-steps b { font-size: var(--step--1); margin-top: 2px; }
  .fw-steps small { font-size: var(--step--2); }
}
/* phones: the choice comes right after the intro, not below a full empty screen */
@media (max-width: 1079px) { .cover-text { min-height: 0 !important; } .cover .scroll-cue { display: none; } .cover > .flows { margin-top: 8px; } }
@media (max-width: 640px) { .flow-switch button { padding: 4px 8px; } }
'''


FLOW_JS = '''
(function () {
  var bar = document.querySelector('.topbar');
  window.addEventListener('beforeprint', function () { document.querySelectorAll('main details:not([open])').forEach(function (d) { d.setAttribute('open', ''); d.dataset.printOpened = '1'; }); });
  window.addEventListener('afterprint', function () { document.querySelectorAll('main details[data-print-opened]').forEach(function (d) { d.removeAttribute('open'); delete d.dataset.printOpened; }); });
  function barH() { if (bar) document.documentElement.style.setProperty('--topbar-h', bar.offsetHeight + 'px'); }
  barH(); window.addEventListener('resize', barH);
  var KEY = 'isx-flow-2', html = document.documentElement;
  function nextLinks() {
    var cards = [].slice.call(document.querySelectorAll('main section.chapter > .card > h3.task')).filter(function (h) { return h.offsetParent !== null; });
    cards.forEach(function (h, i) {
      var p = h.parentNode.querySelector(':scope > .next');
      if (!p) return;
      var n = cards[i + 1];
      p.innerHTML = n ? '<a href="#' + n.id + '">Tiếp theo: ' + n.firstChild.textContent + ' →</a>' : '';
    });
  }
  function setFlow(f) {
    html.dataset.flow = f;
    document.querySelectorAll('[data-pick]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.pick === f)); });
    nextLinks();
  }
  document.querySelectorAll('[data-pick]').forEach(function (b) {
    var go = function () {
      setFlow(b.dataset.pick);
      if (b.classList.contains('pickable')) document.getElementById('bat-dau').scrollIntoView({ behavior: 'smooth' });
    };
    b.addEventListener('click', go);
    b.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
  });
  // no type is chosen until the reader picks one; earlier saved choices are cleared
  try { localStorage.removeItem(KEY); localStorage.removeItem('isx-flow'); } catch (e) {}
  nextLinks();
})();
'''


CH = re.findall(r'<section class="chapter" id="([\w-]+)"(?: data-flow="(\w+)")?>\s*<div class="ch-head"><h2>([^<]+)</h2>', body)
toc = ''.join('<li' + (f' data-flow="{f}"' if f else '') + f'><a href="#{sid}">{name}</a></li>' for sid, f, name in CH)
TOC = f'<aside class="toc">\n  <details>\n    <summary>Mục lục</summary>\n    <ol>{toc}</ol>\n  </details>\n</aside>\n'

EXTRA += '''
/* steps beside a row of phone screens */
@media (min-width: 900px) {
  .grid-2.phone-pair { grid-template-columns: minmax(0, 1fr) auto; align-items: start; gap: 12px 28px; }
  .phone-pair > .phones { grid-auto-flow: column; grid-template-columns: none; grid-auto-columns: 150px; margin: 0; }
}
.prereq.solo { grid-template-columns: minmax(0, 1fr); }
figure.shot.mail .frame { max-width: 360px; }
.grid-2 > .note { align-self: start; }
/* cover: title and app box on one row, the two project types side by side under the question */
.fw-steps li .fw-img { animation: none !important; }
@media (min-width: 1080px) {
  .cover { min-height: 0 !important; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important; grid-template-rows: auto auto !important;
    align-items: start !important; padding-block: 40px 32px !important; row-gap: 40px !important; }
  .cover > .cover-text { grid-column: 1 / -1; grid-row: 1 !important; min-height: 0 !important; display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); column-gap: 48px; row-gap: 14px; align-items: center; align-content: start; }
  .cover-text > h1, .cover-text > .lede { grid-column: 1; }
  .cover-text > h1 { align-self: end; } .cover-text > .lede { align-self: start; }
  .cover-text > .get-app { grid-column: 2; grid-row: 1 / span 2; }
  .cover > .flows { grid-column: 1 / -1; grid-row: 2 !important; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); grid-template-rows: auto auto !important;
    gap: 14px 24px; align-self: start; margin: 0; }
  .fw-q { grid-column: 1 / -1; }
  .cover > .scroll-cue { display: none !important; }
}
@media (min-width: 701px) and (max-width: 1079px) {
  .cover > .flows { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); grid-template-rows: auto auto !important; gap: 12px 16px; }
  .fw-q { grid-column: 1 / -1; }
}
/* one card per task, the same everywhere: white panel, title, steps, then a large picture */
.chapter > .card { max-width: 64rem; background: var(--paper); border: 1px solid var(--line); border-radius: 14px;
  padding: clamp(16px, 2.4vw, 30px); display: grid; gap: 18px; box-shadow: 0 1px 2px rgba(10, 21, 66, .05); min-width: 0; }
.chapter > .card + .card { margin-top: 4px; }
.chapter > .card > * { max-width: none !important; min-width: 0; }
.chapter > .card > h3 { counter-increment: sub; font-size: var(--step-2); padding-top: 0; }
.chapter > .card > h3::before { content: counter(sec) "." counter(sub); display: inline-block; min-width: 2.6em; margin-right: .4em; color: var(--muted); font-weight: 600; }
.chapter > .card > .card-meta { margin-top: -12px; }
.chapter > .card > .next { padding: 12px 0 0; border-top: 1px solid var(--line); border-bottom: 0; }
.chapter > .card > .next:empty { display: none; }
/* steps above, picture below at full card width, so screen text stays readable */
.chapter .card .grid-2 { display: grid !important; grid-template-columns: minmax(0, 1fr) !important; gap: 16px !important; align-items: start; }
.chapter .card .grid-2 > figure.shot { display: grid !important; order: 0 !important; }
.chapter .card .grid-2 > * { grid-column: auto !important; grid-row: auto !important; }
/* the same round step numbers everywhere (the guide draws them square beside pictures) */
.chapter .card ol.proc { gap: 12px; font-size: var(--step-0); line-height: 1.6; }
.chapter .card ol.proc > li { grid-template-columns: 2rem minmax(0, 1fr) !important; gap: 12px !important; }
.chapter .card ol.proc > li::before { width: 2rem !important; height: 2rem !important; border-radius: 50% !important; margin-top: 0 !important; }
.chapter .card ol.proc > li > div { padding-top: 3px !important; }
.chapter .card .grid-2 > figure.shot > .frame, .chapter .card .grid-2 > figure.shot > figcaption { grid-column: auto !important; grid-row: auto !important; }
.chapter .card figure.shot { margin: 0; gap: 8px; }
/* reference pictures with a numbered legend: picture full width, legend below in two columns */
.chapter .card figure.shot:has(> ol.legend) { display: grid !important; grid-template-columns: minmax(0, 1fr) !important; gap: 14px !important; }
.chapter .card figure.shot:has(> ol.legend) > * { grid-column: auto !important; grid-row: auto !important; }
.chapter .card figure.shot > ol.legend { grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr)) !important; }
.chapter .card figure.shot:not(.phone) { width: 100%; justify-self: stretch; }
.chapter .card figure.shot:not(.phone) > .frame { width: 100%; }
/* sizes by kind: full screens use the card width, dialogs and photos a calmer width, centred like the screens */
.chapter .card figure.shot.mail > .frame { max-width: 320px; }
.chapter .card figure.shot.scene > .frame { max-width: 640px; }
.chapter .card figure.shot.scene.narrow > .frame { max-width: 460px; }
.chapter .card figure.shot.dialog, .chapter .card figure.shot.mail, .chapter .card figure.shot.scene { justify-items: start; }
/* every web screen at one zoom: a crop takes its share of the card width, like the full screen it came from */
.chapter .card figure.shot > .frame.cropped[style*="--crop-w"] { width: var(--crop-w) !important; max-width: none !important; }
@media (max-width: 640px) { .chapter .card figure.shot > .frame.cropped[style*="--crop-w"] { width: 100% !important; } }
@media print { .chapter .card figure.shot > .frame.cropped[style*="--crop-w"] { width: 100% !important; } .chapter .card .grid-2 { grid-template-columns: minmax(0, 1fr) !important; } }
/* print: phone rows wrap instead of scrolling, and no picture, row or note is split by a page break */
@media print {
  .chapter .card .phones, .phone-pair > .phones { display: block !important; overflow: visible !important; }
  .chapter .card .phones > figure.phone { display: inline-block !important; vertical-align: top; margin: 0 4mm 4mm 0 !important; }
  .chapter .card .phones figure.phone, .chapter .card .phones .frame { width: 46mm !important; max-width: 46mm !important; }
  figure:not(.phone), .phones, .note, tr, .compare .row, ol.proc > li { break-inside: avoid; page-break-inside: avoid; }
  .chapter .card .phones { display: flow-root !important; }
  h3 { break-after: avoid; page-break-after: avoid; }
  /* a grid row cannot split across pages, so on paper the two-column blocks flow as normal blocks */
  section.chapter, .chapter .card, .chapter .card .grid-2 { display: block !important; }
  section.chapter > * + *, .chapter .card > * + * { margin-top: 4mm !important; }
  .chapter .card .grid-2 > * + * { margin-top: 4mm !important; }
}
/* boxes sit a little outside the control, the same gap all round; pins move out with them */
.frame .box { box-sizing: content-box; padding: 5px; margin: -5px 0 0 -5px; border-radius: 7px; }
/* a box over the app's black control bar: white line with a navy halo stays visible on dark and light parts */
.on-dark .frame .box { border-color: #fff !important; box-shadow: 0 0 0 1.5px var(--brand) !important; }
.frame .pin:not(.c):not(.r):not(.t):not(.b) { transform: translate(calc(-100% - 10px), -50%) !important; }
.frame .pin.r { transform: translate(10px, -50%) !important; }
.frame .pin.t { transform: translate(-50%, calc(-100% - 10px)) !important; }
.frame .pin.b { transform: translate(-50%, 10px) !important; }
.frame .pin.tl { margin: -5px 0 0 -5px; }
/* a number placed on a corner or a set point is the same size as the others (it used the container width) */
.frame .pin.c { width: clamp(18px, 2.2vw, 28px) !important; height: clamp(18px, 2.2vw, 28px) !important; font-size: clamp(10px, 1.2vw, 14px) !important; }
.phones .frame .pin.c { width: 16px !important; height: 16px !important; font-size: 9px !important; }  /* phone shots keep their small numbers */
/* narrow screens: a web screenshot is only ~340 px wide, so boxes lose their padding (the edge would cut the text
   next to them) and phone-shot numbers get smaller than web-shot ones */
@media (max-width: 640px) {
  .chapter .card figure.shot:not(.phone):not(.form) .frame .box { padding: 1px !important; margin: -1px 0 0 -1px !important; }
  .phones .frame .pin, .phones .frame .pin.c { width: 13px !important; height: 13px !important; font-size: 8px !important; border-width: 1.2px !important; }
}
.frame .box.tight { padding: 1px; margin: -1px 0 0 -1px; }
/* the 3-column troubleshooting table becomes one block per problem on a phone, each cell under its column name */
@media (max-width: 640px) {
  .tbl.stack { overflow: visible; }
  .tbl.stack thead { display: none; }
  .tbl.stack table, .tbl.stack tbody, .tbl.stack tr, .tbl.stack td { display: block; width: auto; }
  .tbl.stack tr { padding: 10px 12px; border-bottom: 1px solid var(--line); }
  .tbl.stack tr:last-child { border-bottom: 0; }
  .tbl.stack td { padding: 2px 0; border: 0; }
  .tbl.stack td:first-child { font-weight: 700; padding-bottom: 4px; }
  .tbl.stack td:not(:first-child)::before { content: attr(data-label) ": "; color: var(--muted); font-weight: 600; }
}
/* contrast to WCAG AA: table heads, the OK label and the footer */
main th, .foot span { color: hsl(220 12% 38%); }
.compare .card.ok figcaption b { color: #1b7443; }
/* on a phone the screen is only ~340px wide: smaller numbers and a smaller gap keep them off each other */
@media (max-width: 640px) {
  .frame .pin:not(.c) { width: 15px; height: 15px; font-size: 9px; border-width: 1.5px; }
  .frame .pin.c { width: 15px !important; height: 15px !important; font-size: 9px !important; }
  .frame .box:not(.tight) { padding: 3px; margin: -3px 0 0 -3px; }
  .frame .pin:not(.c):not(.r):not(.t):not(.b) { transform: translate(calc(-100% - 6px), -50%) !important; }
  .frame .pin.r { transform: translate(6px, -50%) !important; }
  .frame .pin.t { transform: translate(-50%, calc(-100% - 6px)) !important; }
  .frame .pin.b { transform: translate(-50%, 6px) !important; }
  .frame .pin.tl { margin: -3px 0 0 -3px; }
}
/* one column everywhere: steps, then pictures, then branches one under the other */
.chapter .card .branch { grid-template-columns: minmax(0, 1fr) !important; }
/* notes in the app's colours: navy for what to prepare and the result, warm only for problems */
.chapter .card .note { background: var(--bg); color: var(--ink); border-left: 3px solid var(--line); border-radius: 0 var(--radius) var(--radius) 0; }
.chapter .card .note b.t { color: var(--brand-ink); }
.chapter .card .note.tip { background: var(--brand-soft); border-left-color: var(--brand); color: var(--ink); }
.chapter .card .note.tip b.t::before { content: "✓ "; }
.chapter .card .note.warn { background: var(--warn-bg); border-left-color: #d98b2b; color: var(--ink); }
.chapter .card .note.warn b.t { color: var(--warn-ink); }
.pill.ks { background: var(--brand-soft); color: var(--brand-ink); }
/* phone screens: steps on the left, phones on the right, every phone the same size */
.chapter .card .phones { display: grid; grid-template-columns: repeat(auto-fill, 210px); gap: 16px; margin: 0; justify-content: start; }
.chapter .card .phones figure.phone { width: 210px; }
.chapter .card .phones .frame { max-width: 210px; width: 210px; border-radius: 18px; }
.chapter .card .phones figcaption { max-width: 210px; }
.chapter .card .grid-2.phone-pair > .tbl { order: 0; }
@media (max-width: 640px) {
  .chapter .card .phones { grid-auto-flow: column; grid-template-columns: none; grid-auto-columns: 62%; overflow-x: auto; padding-bottom: 6px; }
  .chapter .card .phones figure.phone, .chapter .card .phones .frame, .chapter .card .phones figcaption { width: 100%; max-width: none; }
  .chapter .card .grid-2:has(> figure.shot ~ figure.shot) { grid-template-columns: minmax(0, 1fr) !important; }
}
.chapter .card .branch { max-width: none; }
.chapter .card .arm { background: var(--bg); border-color: var(--line); }
.chapter .card .arm .phones { grid-template-columns: repeat(auto-fill, 210px); }
.chapter .card .prereq.solo { padding: 0; border: 0; background: none; }
.chapter .card .ends { max-width: none; }
/* the cover always fills exactly one screen: picture heights, gaps and type follow the window height */
.cover { min-height: calc(100svh - var(--topbar-h)) !important; box-sizing: border-box; align-content: center !important;
  padding-block: clamp(10px, 3vh, 40px) !important; row-gap: clamp(10px, 3.2vh, 40px) !important; }
.cover-text { min-height: 0 !important; gap: clamp(8px, 1.6vh, 16px) !important; }
.cover h1 { font-size: clamp(1.5rem, min(5.2vh, 4.4vw), 3.2rem) !important; }
.cover .lede { font-size: clamp(.8rem, 1.75vh, 1.05rem); color: var(--ink-2, #3d4556); }  /* --muted on the cover tint is 4.4:1, below AA */
.cover .get-app { padding: clamp(8px, 1.4vh, 14px) clamp(10px, 1.6vh, 18px); row-gap: clamp(6px, 1vh, 12px); }
.cover .ga-qr { width: clamp(64px, 10vh, 112px); height: clamp(64px, 10vh, 112px); }
.cover .flows { gap: clamp(8px, 1.6vh, 14px) clamp(12px, 1.8vw, 24px) !important; }
.fw-q { font-size: clamp(.95rem, 2.2vh, 1.25rem) !important; }
.fw.pickable { padding: clamp(8px, 1.6vh, 18px) clamp(10px, 1.4vw, 18px) !important; gap: clamp(6px, 1.2vh, 10px) !important; }
.fw-steps { gap: clamp(10px, 1.8vw, 28px); }
.fw-img { aspect-ratio: auto !important; height: clamp(54px, 17vh, 200px); }
.fw-img svg { height: 92%; width: auto; max-width: 92%; }
.fw-steps b { font-size: clamp(.72rem, 1.5vh, .875rem); margin-top: 2px; }
.fw-steps small { font-size: clamp(.66rem, 1.3vh, .75rem); }
.cover .scroll-cue { display: none !important; }
@media (max-height: 700px) { .cover .ga-dev { display: none; } }
@media (max-width: 700px) and (max-height: 760px) { .cover .lede { display: none; } }
@media (max-width: 1079px) {
  .cover { grid-template-columns: minmax(0, 1fr) !important; grid-template-rows: auto auto !important; }
  .cover > .cover-text, .cover > .flows { grid-row: auto !important; align-self: start !important; }
  .cover .ga-dev { display: none; }
  .cover .ga-s { display: none; }
}
@media (max-width: 700px) {
  .cover h1 { font-size: clamp(1.15rem, 3.1vh, 1.75rem) !important; }
  .cover { row-gap: clamp(8px, 1.6vh, 16px) !important; padding-block: 8px 8px !important; }
  .fw.pickable { padding: 8px 8px 10px !important; }
  .fw-steps { gap: 12px !important; }
  .cover .fw-t { padding-bottom: 4px; }
  .cover .lede { font-size: clamp(.75rem, 1.6vh, .9rem); }
  .fw-steps { gap: clamp(10px, 1.6vh, 16px); }
  .cover .fw-steps .fw-img { height: clamp(30px, 6.2vh, 100px) !important; aspect-ratio: auto !important; }
  .fw-steps small { display: none; }
  .cover .fw-t { font-size: .68rem; }
  .cover .get-app { grid-template-columns: 1fr; }
  .cover .ga-qr { display: none; }
  .fw-steps li:not(:last-child)::after { bottom: calc(-1 * clamp(10px, 1.6vh, 16px)); width: 14px; height: 14px; }
}
/* the subtitle beside the logo stays on one line, or steps aside when the bar is too tight */
.topbar .brand small { white-space: nowrap; }
@media (max-width: 760px) { .topbar .brand small { display: none; } }
/* wide cover cards: the gap between pictures shrinks with the screen, so the arrow is centred in whatever gap there
   is and drawn above the pictures (at 768 px the gap is narrower than the arrow) */
@media (min-width: 701px) {
  .cover .fw-steps { --g: clamp(18px, 2.2vw, 28px); gap: var(--g) !important; }
  .cover .fw-steps li:not(:last-child)::after { right: calc(var(--g) / -2 - 9px); width: 18px; height: 18px; z-index: 1; }
}
/* data diagram on phones: the side branch (Vị trí has many Vấn đề) sits beside Vị trí, so the main down arrow goes
   from Vị trí to Bản quét and is not read as "an issue has many scans" */
@media (max-width: 640px) {
  .fdg:not(.ifc-flow) .fd-col:has(> .fd-br) { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); column-gap: 6px; align-items: stretch; }
  .fdg:not(.ifc-flow) .fd-col:has(> .fd-br) > .fd-br { margin: 0 !important; grid-template-rows: auto 1fr; gap: 4px; }
  .fdg:not(.ifc-flow) .fd-col:has(> .fd-br) .fd-link { border-left: 0; margin-left: 0; padding-left: 0; height: auto; }
  .fdg:not(.ifc-flow) .fd-col:has(> .fd-br) .fd-link::before { content: "→"; position: static; width: auto; height: auto; border: 0; margin: 0; font-size: 14px; line-height: 1; }
}
/* every picture in a task card starts at the left edge of its column, like the text above it (the login dialog
   alone was centred) */
.chapter .card figure.shot { justify-items: start !important; }
.chapter .card figure.shot > .frame { margin-left: 0 !important; margin-right: auto !important; justify-self: start !important; }
.chapter .card figure.shot > figcaption { justify-self: start; text-align: left; }
/* narrow cards: each step is one row, picture left and its name right; the arrow sits under the picture's
   centre and fills the gap down to the next picture */
@media (max-width: 700px) {
  .cover .fw-steps { gap: 14px !important; }
  .cover .fw-steps li { grid-template-columns: 56px minmax(0, 1fr); column-gap: 10px; align-items: center; }
  .cover .fw-steps .fw-img { width: 56px; height: 44px !important; grid-row: 1 / span 2; }
  .cover .fw-steps .fw-img svg { height: 90%; max-width: 90%; }
  /* the steps run top to bottom here: the arrow nudges downwards, the way it points, and stays centred under the picture */
  .fw-steps li:not(:last-child)::after { animation-name: nudge-down !important; }
  @keyframes nudge-down { 0%, 100% { transform: translateX(-50%) translateY(0); } 50% { transform: translateX(-50%) translateY(3px); } }
  .cover .fw-steps b { grid-column: 2; grid-row: 1 / span 2; margin: 0; line-height: 1.25; }
  .cover .fw-t .pill { white-space: normal; }
  .cover .fw-steps li:not(:last-child)::after { left: 28px; right: auto; top: auto; bottom: -14px; transform: translateX(-50%);
    width: 14px; height: 14px; display: grid; place-items: center; line-height: 1; }
}
'''

CARD_JS = r"""
(function () {
  var M = (window.SHOT_MARKS && window.SHOT_MARKS.vi) || {};
  var TAG = { mep: '<span class="pill mep">MEP</span>', ks: '<span class="pill ks">Khảo sát</span>' };
  // a card's children become chapter children, so the guide's numbering, anchors and search see them
  // each task stays in its own card; the card gets its flow tag and a "Tiếp theo" line
  document.querySelectorAll('div.card').forEach(function (c) {
    var f = c.getAttribute('data-flow'), meta = c.querySelector(':scope > .card-meta'), h = c.querySelector(':scope > h3');
    if (!meta || !h) return;
    h.classList.add('task');
    if (f) meta.insertAdjacentHTML('beforeend', ' ' + TAG[f]);
    var n = document.createElement('p'); n.className = 'next'; c.appendChild(n);
  });
  // step-numbered pins: "n:@m[:side]" uses box m measured on the live page, "n:x,y,w,h[:side]" a box, "n:x,y" a point
  // a crop also applies to a shot without numbers (the dashboard is cropped by its own marks script)
  document.querySelectorAll('figure[data-hp], figure.shot[data-crop]:not([data-shot])').forEach(function (fig) {
    var frame = fig.querySelector('.frame'), layer = frame, crop = fig.getAttribute('data-crop');
    if (crop) {
      var c = crop.split(',').map(Number), cw = c[2] - c[0], ch = c[3] - c[1];
      layer = document.createElement('div'); layer.className = 'zoom';
      layer.style.cssText = 'left:' + (-c[0] / cw * 100) + '%;top:' + (-c[1] / ch * 100) + '%;width:' + (100 / cw * 100) + '%;height:' + (100 / ch * 100) + '%';
      frame.classList.add('cropped'); frame.style.aspectRatio = (cw * 16) + ' / ' + (ch * 10);
      // a cropped screen is shown at the same zoom as a full screen: its width is its share of the full image
      if (!fig.classList.contains('phone')) frame.style.setProperty('--crop-w', cw + '%');
      layer.appendChild(frame.querySelector('img')); frame.appendChild(layer);
    }
    var marks = M[fig.getAttribute('data-ref')] || [];
    (fig.getAttribute('data-hp') || '').split(';').filter(Boolean).forEach(function (item) {
      var p = item.split(':'), n = p[0], spec = p[1], side = p[2], b = null, at = null;
      // "n:box:@x,y" boxes an element but puts its number at x,y: for crowded shots where every side covers text
      var pinAt = side && side.charAt(0) === '@' ? side.slice(1).split(',').map(Number) : null;
      if (pinAt) side = null;
      if (spec.charAt(0) === '@') {
        var m = marks.filter(function (k) { return k.n === +spec.slice(1); })[0];
        if (!m) { console.warn('no mark', spec); return; }
        b = [m.x, m.y, m.w, m.h];
        if (!side && m.px != null) at = [m.px, m.py];
      } else {
        var v = spec.split(',').map(Number);
        if (v.length === 2) at = v; else b = v;
      }
      if (pinAt) at = pinAt;
      if (b) {
        var bx = document.createElement('span'); bx.className = 'box';
        bx.style.cssText = 'left:' + b[0] + '%;top:' + b[1] + '%;width:' + b[2] + '%;height:' + b[3] + '%';
        layer.appendChild(bx);
      }
      var pin = document.createElement('span'); pin.textContent = n;
      if (at) { pin.className = 'pin c'; pin.style.cssText = 'left:' + at[0] + '%;top:' + at[1] + '%'; }
      else {
        side = side || (b[0] < 5 ? 'r' : 'l');
        var x = side === 'r' ? b[0] + b[2] : (side === 't' || side === 'b') ? b[0] + b[2] / 2 : b[0];
        var y = side === 't' || side === 'tl' ? b[1] : side === 'b' ? b[1] + b[3] : side === 'lb' ? b[1] + b[3] - Math.min(b[3], 8) / 2 : b[1] + Math.min(b[3], 8) / 2;
        pin.className = 'pin ' + (side === 'tl' ? 'c tl' : side);
        pin.style.cssText = 'left:' + x + '%;top:' + y + '%';
      }
      layer.appendChild(pin);
    });
  });
  // after layout: boxes closer than their padding lose it so they never overlap,
  // and a number that would fall outside the picture is moved back inside it
  function fitMarks() {
    document.querySelectorAll('.frame').forEach(function (fr) {
      var r = fr.getBoundingClientRect();
      if (!r.width) return;
      var boxes = Array.prototype.slice.call(fr.querySelectorAll('.box'));
      boxes.forEach(function (b) { b.classList.remove('tight'); });
      boxes.forEach(function (a, i) {
        var ra = a.getBoundingClientRect();
        boxes.slice(i + 1).forEach(function (b) {
          var rb = b.getBoundingClientRect();
          if (ra.left < rb.right + 2 && rb.left < ra.right + 2 && ra.top < rb.bottom + 2 && rb.top < ra.bottom + 2) {
            a.classList.add('tight'); b.classList.add('tight');
          }
        });
      });
      fr.querySelectorAll('.pin').forEach(function (p) {
        p.style.translate = '';
        var q = p.getBoundingClientRect(), dx = 0, dy = 0;
        if (q.left < r.left + 2) dx = r.left + 2 - q.left; else if (q.right > r.right - 2) dx = r.right - 2 - q.right;
        if (q.top < r.top + 2) dy = r.top + 2 - q.top; else if (q.bottom > r.bottom - 2) dy = r.bottom - 2 - q.bottom;
        if (dx || dy) p.style.translate = dx + 'px ' + dy + 'px';
      });
    });
  }
  var queued = false;
  function queueFit() { if (queued) return; queued = true; requestAnimationFrame(function () { queued = false; fitMarks(); }); }
  document.querySelectorAll('.tbl.stack table').forEach(function (t) {
    var names = [].map.call(t.querySelectorAll('thead th'), function (th) { return th.textContent.trim(); });
    t.querySelectorAll('tbody tr').forEach(function (tr) { [].forEach.call(tr.children, function (td, i) { if (names[i]) td.setAttribute('data-label', names[i]); }); });
  });
  window.fitMarks = fitMarks;
  window.addEventListener('load', queueFit);
  window.addEventListener('resize', queueFit);
  document.addEventListener('load', function (e) { if (e.target.tagName === 'IMG') queueFit(); }, true);
  new MutationObserver(queueFit).observe(document.documentElement, { attributes: true, attributeFilter: ['data-flow'] });
})();
"""

guide_js = (ROOT / 'src/guide.js').read_text('utf8')
guide_js = guide_js.replace('var match = function (r)',
    "idx.forEach(function (r) { if (r.kind === 't') { r.text = (r.el.innerText || r.el.textContent).replace(/\s+/g, ' ').trim(); r.f = fold(r.text); } }); var match = function (r)")
assert 'r.f = fold(r.text); } });' in guide_js
guide_js = guide_js.replace('var res = idx.filter(match);',
                            'var res = idx.filter(match).filter(function (r) { return r.el.offsetParent !== null; });')
assert 'offsetParent !== null; });' in guide_js
# a section whose text matched shows once, as title + snippet, not again as a bare title above it
guide_js = guide_js.replace('var per = {}; res = res.filter(',
    'var withText = {}; res.forEach(function (r) { if (r.kind === "t") withText[r.num] = 1; }); '
    'res = res.filter(function (r) { return r.kind !== "h" || !withText[r.num]; }); var per = {}; res = res.filter(')
assert 'withText[r.num] = 1' in guide_js
# lightbox: the copy keeps the picture's shape and fits the screen height too, so tall shots are not cut off
guide_js = guide_js.replace("      document.body.appendChild(lb);\n",
    "      document.body.appendChild(lb);\n"
    "      var ratio = frame.offsetWidth / Math.max(1, frame.offsetHeight);\n"
    "      copy.style.width = 'min(1600px, 100%, ' + Math.floor((window.innerHeight - 72) * ratio) + 'px)';\n", 1)
assert 'var ratio = frame.offsetWidth' in guide_js
guide_js = guide_js.replace("r.el.scrollIntoView({ behavior: 'smooth', block: 'center' }); flash(r.el);",
    "var to = r.el.matches('section') ? (r.el.querySelector('.ch-head') || r.el) : r.el; "
    "to.scrollIntoView({ behavior: 'smooth', block: r.el.matches('section, h3') ? 'start' : 'center' }); flash(to);")
assert "r.el.matches('section, h3') ? 'start'" in guide_js
# section numbers come from CSS counters, which skip the other flow's hidden cards: a result shows the number
# the reader sees now, counted over the visible chapters and cards
guide_js = guide_js.replace("a.firstChild.textContent = (r.num ? r.num + '  ' : '') + r.title;",
    "var ln = liveNum(r.el); a.firstChild.textContent = (ln ? ln + '  ' : '') + r.title;")
assert 'liveNum(r.el)' in guide_js
guide_js = guide_js.replace('  // ---- Search: headings first, then text; tone marks ignored ----',
    """  function liveNum(el) {
    var vis = function (e) { return e.offsetParent !== null; };
    var sec = el.closest('section.chapter'); if (!sec) return '';
    var si = Array.prototype.filter.call(document.querySelectorAll('main section.chapter'), vis).indexOf(sec) + 1;
    var task = el.closest('section.chapter > .card'), card = el.matches('h3') ? el : (task && task.querySelector(':scope > h3'));
    if (!card) return String(si);
    var hs = Array.prototype.filter.call(sec.querySelectorAll(':scope > h3, :scope > .card > h3'), vis);
    return si + '.' + (hs.indexOf(card) + 1);
  }
  // ---- Search: headings first, then text; tone marks ignored ----""")
assert 'function liveNum' in guide_js
# tasks live in .card wrappers: anchors, numbering and search look inside them too
for a, b in [("sec.querySelectorAll(':scope > h3')", "sec.querySelectorAll(':scope > h3, :scope > .card > h3')"),
             ("'main section.chapter > *, main section.chapter li", "'main section.chapter > *, main section.chapter > .card > *, main section.chapter li"),
             ("el.closest('section.chapter > *')", "el.closest('section.chapter > *, section.chapter > .card > *')"),
             ("if (el.matches('.ch-head, ol, ul,", "if (el.matches('.branch, .card, .ch-head, ol, ul,")]:
    assert a in guide_js, a
    guide_js = guide_js.replace(a, b)
css = (ROOT / 'src/guide.css').read_text('utf8').replace('/*CMS-TOKENS*/', (ROOT / 'src/cms-tokens.css').read_text('utf8')) + EXTRA
LIGHT = ('<meta name="color-scheme" content="light">\n<script>(function () { var r = document.documentElement;'
         ' function pin() { if (r.getAttribute("data-theme") !== "light") r.setAttribute("data-theme", "light"); }'
         ' pin(); new MutationObserver(pin).observe(r, { attributes: true, attributeFilter: ["data-theme"] }); })();</script>\n')
page = (LIGHT + shell.replace('<!--CSS-->', f'<style>\n{css}</style>') + TOC + '<main>\n' + body
        + '<footer class="foot">\n  <span>InsightScanX · Hướng dẫn sử dụng · Tiếng Việt · 11/2026</span>\n</footer>\n\n</main>\n</div>\n</div>\n'
        + '<script>' + (ROOT / 'assets/marks.js').read_text('utf8').replace(  # pin 1 on the company box, not by the collapse button
            '"dashboard": [{"n": 1, "x": 0.78, "y": 7, "w": 15.55, "h": 5, "px": 14.83, "py": 3.16}, {"n": 2, "x": 0.55, "y": 12.88, "w": 16.02, "h": 26.13, "px": 14.17, "py": 35.17}, {"n": 3, "x": 72.84, "y": 0.94, "w": 12.41, "h": 4, "px": 70.44, "py": 2.94}, {"n": 4, "x": 85.56, "y": 0.94, "w": 2.5, "h": 4, "px": 86.81, "py": 8.78}',
            '"dashboard": [{"n": 1, "x": 0.78, "y": 7.2, "w": 15.55, "h": 4.4, "px": 12.2, "py": 9.4}, {"n": 2, "x": 0.55, "y": 13.6, "w": 16.02, "h": 25.4, "px": 14.17, "py": 35.17}, {"n": 3, "x": 72.84, "y": 0.94, "w": 12.0, "h": 4, "px": 70.44, "py": 2.94}, {"n": 4, "x": 85.75, "y": 0.94, "w": 2.2, "h": 4, "px": 86.85, "py": 8.78}', 1).replace('{"n": 6, "x": 10, "y": 8.25, "w": 9.64,', '{"n": 6, "x": 10, "y": 8.25, "w": 8.6,', 1) + '</script>\n'
        + '<script>\n' + CARD_JS + guide_js + FLOW_JS + '</script>\n')
# every image the page uses travels with it
# the 9-tool legend: show the toolbar and the model next to it, not the whole screen, so on a phone the numbers
# are not packed onto 20px icons
_tools = '<figure class="shot" data-ref="viewer-tools" data-hp="1:@1:r;2:@2:r;3:@3:r;'
assert page.count(_tools) == 1
page = page.replace(_tools, _tools.replace('data-hp=', 'data-crop="5.3,25.2,50,86" data-hp='))
# wording fix in the block copied from the main manual (the main manual itself is left as it is)
assert page.count('mỗi lần đăng nhập nhập thêm mã') == 1
page = page.replace('mỗi lần đăng nhập nhập thêm mã', 'mỗi lần đăng nhập, bạn nhập thêm mã')
FIXES = {  # wording in blocks copied from src/vi.html, fixed for this page only
    'Chúng tôi muốn giảm thiểu các rủi ro liên quan đến hiệu năng, như app bị crash, chạy không ổn định và các vấn đề hiệu năng khác.':
        'Chúng tôi muốn giảm rủi ro app bị thoát đột ngột, chạy chậm hoặc không ổn định.',
    'mở tình trạng xử lý trên máy chủ': 'mở bảng tình trạng xử lý trên máy chủ',
    '<td>Bản vẽ có kích thước</td>': '<td>Bản vẽ có trục, cao độ và tên phòng</td>',
    ' Thời gian xử lý tuỳ dung lượng file. Xong hoặc lỗi, người tạo bản quét nhận thông báo ở biểu tượng chuông và qua email (“Dựng 3D hoàn tất”).</figcaption>': '</figcaption>',
    'Chèn cùng đám mây điểm .E57/.PLY theo gốc tọa độ (origin to origin) là khớp nhau.': 'Khi chèn cùng đám mây điểm .E57/.PLY theo gốc tọa độ (origin to origin), hai file sẽ khớp nhau.',
    'Quét cả buổi thì sạc đầy và mang sạc dự phòng.': 'Quét cả buổi thì mang thêm sạc dự phòng.',
    # the data diagram follows the picked flow, like the rest of the examples
    '<small>Bệnh viện</small>': '<small><i class="fl" data-flow="mep">Bệnh viện</i><i class="fl" data-flow="ks">Văn phòng</i></small>',
    '<small>Tầng hầm B1, phòng bơm</small>': '<small><i class="fl" data-flow="mep">Tầng hầm B1, phòng bơm</i><i class="fl" data-flow="ks">Tầng 5, khu làm việc</i></small>',
    '<small>Rò nước dưới ống cấp, gắn vào điểm 3D</small>': '<small><i class="fl" data-flow="mep">Rò nước dưới ống cấp</i><i class="fl" data-flow="ks">Vết nứt tường phòng họp</i>, gắn vào điểm 3D</small>',
    '<li><div>Pin đầy, còn nhiều bộ nhớ trống<span>': '<li><div>Sạc đầy pin trước buổi quét, còn nhiều bộ nhớ trống<span>',
    'Mỗi lần quét đi hết khu vực của nó rồi lấn qua cửa sang khu vực tiếp theo 1–2&nbsp;m. Hai marker ở cửa':
        'Hai marker ở cửa',
    ' Mỗi bản quét gồm một hoặc nhiều khu vực nối nhau bằng marker (xem <a href="#dan-marker">Chia khu vực và dán marker</a>). Vấn đề thuộc vị trí và có thể gắn vào một điểm trên bản quét.': '',
    'ở đây còn có Mesh và IFC của BIM.': 'ở đây còn có Lưới 3D (Mesh)<span data-flow="ks"> và IFC của BIM</span>.',
    '<tr><td>IFC, DXF</td><td>File mô hình BIM (IFC) và bản vẽ CAD (DXF) để mở bằng phần mềm thiết kế.</td></tr>':
        '<tr data-flow="ks"><td>IFC, DXF</td><td>File mô hình BIM (IFC) và bản vẽ CAD (DXF) để mở bằng phần mềm thiết kế.</td></tr>'
        '<tr data-flow="mep"><td>IFC</td><td>File mô hình đường ống để mở bằng Rebro, Revit hoặc phần mềm BIM khác.</td></tr>',
    'Thiết bị đã kiểm chứng: iPhone 15 Pro, iPad Pro chip M3 trở lên.': 'Thiết bị đã kiểm chứng: iPhone 15 Pro trở lên, iPad Pro chip M3 trở lên.',
    ': .PLY, .E57, và .IFC (MEP Model) ở dự án MEP (': ': .PLY, .E57<span data-flow="mep"> và .IFC (MEP Model) ở dự án MEP</span> (',
    'Quản trị tổ chức giới hạn dải IP': 'Quản trị tổ chức có thể giới hạn dải IP',
    'Quản trị tổ chức tạo thêm vai trò riêng': 'Quản trị tổ chức có thể tạo thêm vai trò riêng',
    'như “Nhà thầu phụ”, và bật tắt từng quyền Xem, Thêm, Sửa, Xóa, Xuất.': 'như “Giám sát viên”, và bật tắt từng quyền Xem, Thêm, Sửa, Xóa, Xuất báo cáo.',
    'bạn nên tránh để phần chồng chỉ là một dãy ống giống nhau.': 'bạn nên tránh để phần chồng chỉ là <span data-flow="mep">một dãy ống giống nhau</span><span data-flow="ks">một mảng tường trơn</span>.',
    'hoặc marker dán sai số.': 'hoặc marker dán sai số thứ tự hoặc trùng số.',
    'cạnh Đám mây điểm và MEP mở bảng': 'cạnh Đám mây điểm<span data-flow="mep"> và MEP</span> mở bảng',
    'Trước khi quét, máy nên còn trên 20% pin và':
        'Trước khi quét, máy nên còn trên 50% pin (app cảnh báo khi dưới 20%) và',
    'Bật hết đèn phòng máy, góc tối thì mang đèn phụ. Tránh đèn chiếu xiên tạo bóng đổ phía sau ống: bóng thay đổi khi bạn đi làm máy dễ mất định vị.':
        'Bật hết đèn trong phòng, góc tối thì mang đèn phụ. Tránh đèn chiếu xiên tạo bóng đổ phía sau ống hoặc đồ vật: bóng thay đổi khi bạn di chuyển khiến máy dễ mất định vị.',
    'Thu hồi</span> để chặn ngay (<a href="#vai-tro-han-muc">Vai trò, quyền và hạn mức</a>)':
        'Thu hồi</span> để chặn ngay (<a href="#duyet-thiet-bi">Duyệt thiết bị và giới hạn truy cập</a>)',
    'Cắt (Crop): chỉ giữ một vùng để nhìn vào bên trong.':
        'Cắt (Crop): chỉ giữ một vùng để nhìn vào bên trong. Khi đang cắt, nút mũi tên xoay ngay bên dưới dùng để bỏ vùng cắt.',
}
for a, b in FIXES.items():
    assert page.count(a) == 1, a
    page = page.replace(a, b)
# the web's own Vietnamese labels for the export formats
# cover drawings: the lower pipe turned down and stopped in mid-wall, which read as a hole in the wall;
# it now drops to the floor line like a riser (right wall floor edge at x 95.6 is y 63.8)
assert page.count('L95.6 47.8 L95.6 57.8"') == 2
page = page.replace('L95.6 47.8 L95.6 57.8"', 'L95.6 47.8 L95.6 63.2"')
# MEP drawing: the riser ends in a floor flange (a flat ellipse in the fitting colour), so it reads as going into
# the floor rather than stopping in mid-air
_fit = '<circle cx="95.6" cy="47.8" r="3"/></g>'
assert page.count(_fit) == 1
page = page.replace(_fit, _fit + '<ellipse class="il-flange" cx="95.6" cy="63.6" rx="4.6" ry="2.1"/>')
# cover drawings: the scan area was drawn phone -> top-left -> top-right -> bottom-right -> bottom-left, so its first
# edge cut across the area and left the lower-left part unfilled (a missing corner). Drawn phone -> bottom-left ->
# top-left -> top-right -> bottom-right, it covers the whole scanned patch plus the small beam from the phone.
page, _n = re.subn(r'(<path class="sc-beam" d="M[\d.]+ [\d.]+) (L[\d.]+ [\d.]+) (L[\d.]+ [\d.]+) (L[\d.]+ [\d.]+) (L[\d.]+ [\d.]+) Z"',
                   lambda m: f'{m.group(1)} {m.group(5)} {m.group(2)} {m.group(3)} {m.group(4)} Z"', page)
assert _n == 2, _n

# --- cover drawings, second pass (review of every drawing at 4x) ---
# BIM: the door lay across its partition (sloping down-right while the wall slopes up-right); now it lies on the wall face
assert page.count('<path class="bdoor" d="M97.9 76.6 L112.2 84.9 L112.2 62.9 L97.9 54.6 Z"/>') == 1
page = page.replace('<path class="bdoor" d="M97.9 76.6 L112.2 84.9 L112.2 62.9 L97.9 54.6 Z"/>',
                    '<path class="bdoor" d="M100.5 75.1 L109.3 70.0 L109.3 52.0 L100.5 57.1 Z"/>')
# 2D plan: the 7,300 and 6,200 dimensions were drawn the same length; the bottom one now spans the whole room
assert page.count('M34 102 H96 M34 99 V105 M96 99 V105') == 1
page = page.replace('M34 102 H96 M34 99 V105 M96 99 V105', 'M34 102 H130 M34 99 V105 M130 99 V105')
page = page.replace('<text class="pl-d" x="65" y="110">7,300</text>', '<text class="pl-d" x="82" y="110">9,600</text>')
# survey scan: the scanned patch hung flat across the room corner, on neither wall; it is moved onto the left wall
# (old patch is a parallelogram TL 41,35.5 / +62.4,-7.8 / +0,38; new one TL 36,38 / +38,-19 / +0,32)
def _onwall(m):
    x, y = float(m.group(1)), float(m.group(2))
    u = (x - 41.0) / 62.4
    v = (y - 35.5 + 7.8 * u) / 38.0
    return f'{36 + 38 * u:.1f} {38 - 19 * u + 32 * v:.1f}'
_i = page.index('<svg viewBox="0 0 160 120" role="img" aria-label="iPhone trong văn phòng')
_j = page.index('</svg>', _i) + 6
_svg = page[_i:_j]
_svg = re.sub(r'(<path class="sc-mesh" d=")([^"]+)"', lambda m: m.group(1) + re.sub(r'([\d.]+) ([\d.]+)', _onwall, m.group(2)) + '"', _svg)
_svg = _svg.replace('<path class="sc-beam" d="M72.2 70 L41.0 73.5 L41.0 35.5 L103.4 27.7 L103.4 65.7 Z"',
                    '<path class="sc-beam" d="M36.0 70.0 L36.0 38.0 L74.0 19.0 L74.0 51.0 Z"')
def _hit(m):
    xy = _onwall(re.match(r'([\d.]+) ([\d.]+)', m.group(1) + ' ' + m.group(2))).split()
    return f'<circle class="sc-hit" cx="{xy[0]}" cy="{xy[1]}"'
_svg = re.sub(r'<circle class="sc-hit" cx="([\d.]+)" cy="([\d.]+)"', _hit, _svg)
def _dot(m):
    xy = _onwall(re.match(r'([\d.]+) ([\d.]+)', m.group(1) + ' ' + m.group(2))).split()
    return f'<circle class="pd pscan" cx="{xy[0]}" cy="{xy[1]}"'
_svg, _nd = re.subn(r'<circle class="pd pscan" cx="([\d.]+)" cy="([\d.]+)"', _dot, _svg)
assert 'M36.0 70.0 L36.0 38.0 L74.0 19.0 L74.0 51.0 Z' in _svg and _nd > 100, _nd
page = page[:_i] + _svg + page[_j:]
page = page.replace('(MEP Model)', '(Mô hình MEP)').replace('(3D Layout Model)', '(Mô hình bố trí 3D)')
# the ownership sentence is held back until confirmed, so the item is about AI only
page, _n = re.subn(r'<b>Quyền sở hữu dữ liệu và AI</b><p>\s*', '<b>Tính năng AI</b><p>', page)
assert _n == 1
# one spelling style for the whole page (the old style, used by most of the text): xóa, tùy, tọa, hòa
_W = 'A-Za-zÀ-ỹ'
for old, new in (('oá', 'óa'), ('uỳ', 'ùy'), ('oạ', 'ọa'), ('oà', 'òa')):
    page = re.sub(rf'(?<=[{_W}])(?<![{_W}][{_W}][{_W}]){old}(?![{_W}])', new, page)
# old-manual ids are remapped only when this page has no section of that id (the TOC links to its own chapters)
page_ids = set(re.findall(r'id="([\w-]+)"', page))
page = re.sub(r'href="#([\w-]+)"', lambda m: 'href="#' + (m.group(1) if m.group(1) in page_ids else LINKS.get(m.group(1), m.group(1))) + '"', page)
# phone and photo frames drop the width/height ratio (aspect-ratio: auto), so they collapsed until the image loaded
# and every TOC jump landed short; give each image its own ratio so the page height is final from the start
page = re.sub(r'(<div class="frame (?:tall|photo)[^"]*"><img )([^>]*?width="(\d+)" height="(\d+)")',
              lambda m: m.group(1) + f'style="aspect-ratio:{m.group(3)}/{m.group(4)}" ' + m.group(2), page)
used = sorted(set(re.findall(r'(?:src|href)="(assets/[^"]+)"', page)))
for s in used:
    src = ROOT / s if (ROOT / s).exists() else ROOT / 'dist' / s
    if not src.exists():   # made for this page only (e.g. zoomed comparison photos), already under proto/
        assert (OUT / s).exists(), s
        continue
    (OUT / s).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, OUT / s)
(OUT / 'khung-vi.html').write_text(page, 'utf8')
(OUT / 'khung-vi.files.json').write_text(json.dumps({s: f'D:/Projects/NCISSX/user-guide/proto/{s}' for s in used}, ensure_ascii=False), 'utf8')
print('ok', len(page) // 1024, 'KB,', len(used), 'images')
