/* Task-card user guide: page runtime. build_guide.py puts window.GUIDE before this script:
   { flows: [{id, label}], storageKey, labels: {next, noResult}, marks: {shotRef: [{n,x,y,w,h,px,py}]} } */
(function () {
  var G = window.GUIDE || {}, FLOWS = G.flows || [], L = G.labels || {}, M = G.marks || {};
  var html = document.documentElement;
  var vis = function (e) { return e.offsetParent !== null; };
  var arr = function (x) { return Array.prototype.slice.call(x); };

  // ---- task cards: flow tag in the meta line, an empty "next" line filled per flow ----
  arr(document.querySelectorAll('main .card')).forEach(function (c) {
    var f = c.getAttribute('data-flow'), meta = c.querySelector(':scope > .card-meta'), h = c.querySelector(':scope > h3');
    if (!h) return;
    h.classList.add('task');
    var fl = FLOWS.filter(function (x) { return x.id === f; })[0];
    if (fl && meta) meta.insertAdjacentHTML('beforeend', ' <span class="pill">' + fl.label + '</span>');
    var n = document.createElement('p'); n.className = 'next'; c.appendChild(n);
  });

  // ---- pins and boxes from data-hp, crops from data-crop (coordinates in % of the full image) ----
  //   "n:x,y,w,h[:side]" box, number beside it; "n:x,y,w,h:@px,py" box, number at a point;
  //   "n:@m[:side]" box measured on the live app (marks); "n:x,y" number only
  arr(document.querySelectorAll('figure[data-hp], figure.shot[data-crop]')).forEach(function (fig) {
    var frame = fig.querySelector('.frame'), layer = frame, crop = fig.getAttribute('data-crop');
    if (!frame) return;
    var img = frame.querySelector('img');
    if (crop && img) {
      var c = crop.split(',').map(Number), cw = c[2] - c[0], ch = c[3] - c[1];
      var iw = +img.getAttribute('width') || 16, ih = +img.getAttribute('height') || 10;
      layer = document.createElement('div'); layer.className = 'zoom';
      layer.style.cssText = 'left:' + (-c[0] / cw * 100) + '%;top:' + (-c[1] / ch * 100) + '%;width:' + (100 / cw * 100) + '%;height:' + (100 / ch * 100) + '%';
      frame.classList.add('cropped'); frame.style.aspectRatio = (cw * iw) + ' / ' + (ch * ih);
      // a crop fills its frame, i.e. it zooms in: that is what makes screen text readable beside the steps
      layer.appendChild(img); frame.appendChild(layer);
    }
    var marks = M[fig.getAttribute('data-ref')] || [];
    (fig.getAttribute('data-hp') || '').split(';').filter(Boolean).forEach(function (item) {
      var p = item.split(':'), n = p[0], spec = p[1], side = p[2], b = null, at = null;
      var pinAt = side && side.charAt(0) === '@' ? side.slice(1).split(',').map(Number) : null;
      if (pinAt) side = null;
      if (spec.charAt(0) === '@') {
        var m = marks.filter(function (k) { return k.n === +spec.slice(1); })[0];
        if (!m) { console.warn('guide: no mark', spec, fig.getAttribute('data-ref')); return; }
        b = [m.x, m.y, m.w, m.h];
        if (!side && m.px != null) at = [m.px, m.py];
      } else {
        var v = spec.split(',').map(Number);
        if (v.length === 2) at = v; else b = v;
      }
      if (pinAt) at = pinAt;
      if (b) {
        var bx = document.createElement('span'); bx.className = 'box'; bx.dataset.n = n;
        bx.style.cssText = 'left:' + b[0] + '%;top:' + b[1] + '%;width:' + b[2] + '%;height:' + b[3] + '%';
        layer.appendChild(bx);
      }
      var pin = document.createElement('span'); pin.textContent = n; pin.dataset.n = n;
      if (at) { pin.className = 'pin c'; pin.style.cssText = 'left:' + at[0] + '%;top:' + at[1] + '%'; }
      else {
        side = side || (b[0] < 5 ? 'r' : 'l');
        var x = side === 'r' ? b[0] + b[2] : (side === 't' || side === 'b') ? b[0] + b[2] / 2 : b[0];
        var y = side === 't' || side === 'tl' ? b[1] : side === 'b' ? b[1] + b[3] : side === 'lb' ? b[1] + b[3] - Math.min(b[3], 8) / 2 : b[1] + Math.min(b[3], 8) / 2;
        pin.className = 'pin ' + (side === 'tl' ? 'c tl' : side === 'lb' ? 'l' : side);
        pin.style.cssText = 'left:' + x + '%;top:' + y + '%';
      }
      layer.appendChild(pin);
    });
  });

  // after layout: boxes closer than their padding lose it, numbers falling outside the picture move back inside
  function fitMarks() {
    arr(document.querySelectorAll('.frame')).forEach(function (fr) {
      var r = fr.getBoundingClientRect(); if (!r.width) return;
      var boxes = arr(fr.querySelectorAll('.box'));
      boxes.forEach(function (b) { b.classList.remove('tight'); });
      boxes.forEach(function (a, i) {
        var ra = a.getBoundingClientRect();
        boxes.slice(i + 1).forEach(function (b) {
          var rb = b.getBoundingClientRect();
          if (ra.left < rb.right + 2 && rb.left < ra.right + 2 && ra.top < rb.bottom + 2 && rb.top < ra.bottom + 2) { a.classList.add('tight'); b.classList.add('tight'); }
        });
      });
      arr(fr.querySelectorAll('.pin')).forEach(function (p) {
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
  window.addEventListener('load', queueFit);
  window.addEventListener('resize', queueFit);
  document.addEventListener('load', function (e) { if (e.target.tagName === 'IMG') queueFit(); }, true);

  // ---- numbering over what the reader sees (chapters and cards of the picked flow) ----
  function renumber() {
    var chapters = arr(document.querySelectorAll('main section.chapter')).filter(vis);
    chapters.forEach(function (sec, i) {
      var h2 = sec.querySelector('.ch-head h2'); setNum(h2, String(i + 1));
      arr(sec.querySelectorAll(':scope > .card > h3')).filter(vis).forEach(function (h, j) { setNum(h, (i + 1) + '.' + (j + 1)); });
    });
    arr(document.querySelectorAll('.toc a[href^="#"]')).forEach(function (a) {
      var t = document.getElementById(a.getAttribute('href').slice(1)); var s = a.querySelector('.num');
      if (t && s) { var tn = t.querySelector('.num'); s.textContent = tn ? tn.textContent : ''; }
    });
  }
  function setNum(h, n) {
    if (!h) return; var s = h.querySelector(':scope > .num');
    if (!s) { s = document.createElement('span'); s.className = 'num'; h.insertBefore(s, h.firstChild); }
    s.textContent = n;
  }
  function titleOf(h) { var c = h.cloneNode(true), n = c.querySelector('.num'); if (n) n.remove(); return c.textContent.trim(); }

  // ---- "next" line: the following visible card ----
  function nextLinks() {
    var cards = arr(document.querySelectorAll('main section.chapter > .card > h3.task')).filter(vis);
    cards.forEach(function (h, i) {
      var p = h.parentNode.querySelector(':scope > .next'); if (!p) return;
      var n = cards[i + 1];
      p.innerHTML = n ? '<a href="#' + n.id + '">' + (L.next || 'Next') + ': ' + titleOf(n) + ' →</a>' : '';
    });
  }

  // ---- flows: nothing is picked until the reader picks; the choice is kept for the visit ----
  function setFlow(f) {
    if (f) html.dataset.flow = f; else delete html.dataset.flow;
    arr(document.querySelectorAll('[data-pick]')).forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.pick === f)); });
    try { if (f) sessionStorage.setItem(G.storageKey || 'guide-flow', f); } catch (e) {}
    renumber(); nextLinks(); queueFit();
  }
  arr(document.querySelectorAll('[data-pick]')).forEach(function (b) {
    b.addEventListener('click', function () {
      setFlow(b.dataset.pick);
      if (b.classList.contains('fw')) { var s = document.querySelector('main section.chapter'); if (s) s.scrollIntoView({ behavior: 'smooth' }); }
    });
  });
  var saved = null; try { saved = sessionStorage.getItem(G.storageKey || 'guide-flow'); } catch (e) {}
  setFlow(FLOWS.some(function (f) { return f.id === saved; }) ? saved : null);

  // ---- contents: open beside the text on wide screens, folded above it on phones ----
  var tocBox = document.querySelector('.toc details'); if (tocBox && innerWidth < 1100) tocBox.removeAttribute('open');
  // ---- contents: highlight the section being read ----
  var tocLinks = arr(document.querySelectorAll('.toc a[href^="#"]'));
  if ('IntersectionObserver' in window && tocLinks.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        tocLinks.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    tocLinks.forEach(function (a) { var t = document.getElementById(a.getAttribute('href').slice(1)); if (t) io.observe(t); });
  }

  // ---- search: headings first, then step text; tone marks ignored ----
  var fold = function (s) { return s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase(); };
  var input = document.querySelector('.search input'), box = document.querySelector('.search .results');
  if (input && box) {
    input.addEventListener('input', function () {
      var q = fold(input.value.trim()); box.innerHTML = '';
      if (q.length < 2) { box.classList.remove('open'); return; }
      var hits = [];
      arr(document.querySelectorAll('main section.chapter > .card > h3')).filter(vis).forEach(function (h) {
        var card = h.parentNode, num = (h.querySelector('.num') || {}).textContent || '';
        if (fold(titleOf(h)).indexOf(q) >= 0) hits.push({ rank: 0, id: h.id, num: num, title: titleOf(h), snip: '' });
        else {
          var t = card.textContent, i = fold(t).indexOf(q);
          if (i >= 0) hits.push({ rank: 1, id: h.id, num: num, title: titleOf(h), snip: t.slice(Math.max(0, i - 30), i + 60).replace(/\s+/g, ' ').trim() });
        }
      });
      hits.sort(function (a, b) { return a.rank - b.rank; });
      box.innerHTML = hits.slice(0, 12).map(function (h) {
        return '<a href="#' + h.id + '">' + h.num + ' ' + h.title + (h.snip ? '<small>…' + h.snip.replace(/</g, '&lt;') + '…</small>' : '') + '</a>';
      }).join('') || '<a>' + (L.noResult || 'No result') + '</a>';
      box.classList.add('open');
    });
    box.addEventListener('click', function () { box.classList.remove('open'); input.value = ''; });
    document.addEventListener('keydown', function (e) {
      if (e.key === '/' && document.activeElement !== input) { e.preventDefault(); input.focus(); }
      if (e.key === 'Escape') box.classList.remove('open');
    });
  }

  // ---- picture zoom, back to top, print opens every collapsed block ----
  document.addEventListener('click', function (e) {
    var fr = e.target.closest('main .frame'); if (!fr || e.target.closest('a')) return;
    var lb = document.createElement('div'); lb.className = 'lightbox';
    var copy = fr.cloneNode(true), ratio = fr.offsetWidth / fr.offsetHeight;
    copy.style.width = 'min(1600px, 100%, ' + Math.round((innerHeight - 72) * ratio) + 'px)';
    lb.appendChild(copy); document.body.appendChild(lb); requestAnimationFrame(fitMarks);
    lb.addEventListener('click', function () { lb.remove(); });
  });
  var top = document.querySelector('.to-top');
  if (top) {
    window.addEventListener('scroll', function () { top.classList.toggle('show', scrollY > 800); }, { passive: true });
    top.addEventListener('click', function () { scrollTo({ top: 0, behavior: 'smooth' }); });
  }
  var bar = document.querySelector('.topbar');
  function barH() { if (bar) html.style.setProperty('--topbar-h', bar.offsetHeight + 'px'); }
  barH(); window.addEventListener('resize', barH);
  window.addEventListener('beforeprint', function () { arr(document.querySelectorAll('main details:not([open])')).forEach(function (d) { d.setAttribute('open', ''); d.dataset.po = '1'; }); });
  window.addEventListener('afterprint', function () { arr(document.querySelectorAll('main details[data-po]')).forEach(function (d) { d.removeAttribute('open'); delete d.dataset.po; }); });
  window.fitMarks = fitMarks;
})();
