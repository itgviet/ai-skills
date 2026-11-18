// Layout check for a draw.io diagram rendered by viewer-static at scale 1 (page from preview_page.py).
// Run in the browser console / javascript tool:  __check()  ->  { ll: [...], el: [...], nl, ns }
//   ll: pairs of labels whose boxes overlap                      -> must be empty
//   el: edge segments that cross a label ("<path start> x <label>") -> every entry must be the edge's OWN label
//       (draw.io puts an edge label on the edge itself, so it always shows up once; anything else is a real crossing)
// __go(x, y) scrolls the page so diagram point (x, y) is at the top-left, for screenshots area by area.
window.__check = function () {
  const svg = document.querySelector('.mxgraph svg');
  const labs = [...svg.querySelectorAll('foreignObject')].map(fo => {
    const d = fo.querySelector('div div div') || fo.querySelector('div'); const r = d.getBoundingClientRect();
    return { t: d.innerText.replace(/\s+/g, ' ').slice(0, 40), x1: r.left, y1: r.top, x2: r.right, y2: r.bottom };
  }).filter(l => l.t.trim() && l.x2 - l.x1 > 1);
  const segs = [];
  [...svg.querySelectorAll('path')].forEach(p => {
    if (p.getAttribute('fill') !== 'none' || p.getAttribute('visibility') === 'hidden') return;
    const d = p.getAttribute('d') || ''; if (/[CQAZ]/i.test(d.replace(/^M/, ''))) return;
    const n = d.match(/-?[\d.]+/g); if (!n || n.length < 4) return; const m = p.getScreenCTM(); const pts = [];
    for (let k = 0; k + 1 < n.length; k += 2) { const pt = svg.createSVGPoint(); pt.x = +n[k]; pt.y = +n[k + 1]; const q = pt.matrixTransform(m); pts.push([q.x, q.y]); }
    for (let k = 0; k + 1 < pts.length; k++) segs.push({ a: pts[k], b: pts[k + 1], d: d.slice(0, 26) });
  });
  const inter = (a, b) => !(a.x2 <= b.x1 + 1 || b.x2 <= a.x1 + 1 || a.y2 <= b.y1 + 1 || b.y2 <= a.y1 + 1);
  const out = { ll: [], el: [] };
  for (let i = 0; i < labs.length; i++) for (let j = i + 1; j < labs.length; j++) if (inter(labs[i], labs[j])) out.ll.push(labs[i].t + ' <> ' + labs[j].t);
  segs.forEach(s => labs.forEach(l => { const [x1, y1] = s.a, [x2, y2] = s.b;
    if (Math.max(x1, x2) < l.x1 + 1 || Math.min(x1, x2) > l.x2 - 1 || Math.max(y1, y2) < l.y1 + 1 || Math.min(y1, y2) > l.y2 - 1) return;
    out.el.push(s.d + ' x ' + l.t); }));
  out.el = [...new Set(out.el)]; out.nl = labs.length; out.ns = segs.length; return out;
};
window.__go = (x, y) => { window.scrollTo(x, y); return [scrollX, scrollY]; };
