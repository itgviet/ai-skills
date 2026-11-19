/* Page runtime for task-card guides: pins/boxes/crops from data-hp and data-crop, flow picker.
   Extracted from the InsightScanX guide generator (make_guide.py: CARD_JS + FLOW_JS). Expects a global M = {shotRef: [marks]} (may be {}). */

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
