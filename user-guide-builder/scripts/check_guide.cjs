#!/usr/bin/env node
// Automated checks for a one-page user guide built with this skill.
// Usage: node scripts/check_guide.cjs <command> --page <guide.html> [--accept guide.accept.json] [options]
//   all      marks + flows + contrast + pictures + cover, then one PASS/FAIL summary (the gate of the fix loop)
//   marks    boxes overlapping, pins outside the frame, pins sitting on a box        (widths 1440, 390)
//   flows    elements of another flow still visible after picking a flow             (widths 1280, 390)
//   contrast text below WCAG AA (4.5:1, 3:1 for large text)                          (1440, every flow)
//   pictures screenshots shown below 45% of real size (unreadable) or without numbers beside 2+ steps (1280)
//   cover    cover block fits the first screen and nothing scrolls sideways at 12 sizes (PNGs with --out)
//   shots    screenshot each picture: --width 390 --flow <id> --dpr 2 --out dir/prefix [--sheet sheet.png] [css selectors...]
//            (no selector = every visible figure; --sheet joins them into one labelled image to look at)
// --accept: JSON list of findings already judged fine, each a substring of the finding text or {"match": "...", "why": "..."}.
//   Accepted findings are reported as "accepted", not as failures, so the next round only sees new problems.
// Options: --flows a,b (default: read from .flow-switch [data-pick]); --channel msedge|chrome (default msedge)
// Output: JSON lines on stdout; exit 0 = no new findings, 1 = new findings, 2 = usage / runtime error.
// Playwright: resolved from PLAYWRIGHT_MODULE, then require('playwright'), then require('@playwright/test').
'use strict';
const path = require('path');
const fs = require('fs');

function loadPlaywright() {
  for (const t of [process.env.PLAYWRIGHT_MODULE, 'playwright', '@playwright/test'].filter(Boolean)) { try { return require(t); } catch (e) { /* next */ } }
  console.error('Playwright not found. Set PLAYWRIGHT_MODULE to a node_modules/playwright folder, or run `npm i -D playwright` in the project.');
  process.exit(2);
}
function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k.startsWith('--')) { const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true; a[k.slice(2)] = v; } else a._.push(k);
  }
  return a;
}
const args = parseArgs(process.argv.slice(2));
const cmd = args._.shift();
if (!cmd || args.help || !args.page) {
  console.error(fs.readFileSync(__filename, 'utf8').split('\n').filter((l) => l.startsWith('//')).map((l) => l.slice(3)).join('\n'));
  process.exit(cmd && args.page ? 0 : 2);
}
if (!fs.existsSync(args.page)) { console.error('page not found: ' + args.page); process.exit(2); }
const pageUrl = 'file:///' + path.resolve(args.page).split(path.sep).join('/');
let accepted = [];
if (args.accept) {
  if (!fs.existsSync(args.accept)) { console.error('accept file not found: ' + args.accept); process.exit(2); }
  accepted = JSON.parse(fs.readFileSync(args.accept, 'utf8')).map((x) => (typeof x === 'string' ? { match: x } : x));
}
const isAccepted = (f) => accepted.find((a) => f.includes(a.match));
const { chromium } = loadPlaywright();

async function open(b, w, h, flow, extra = {}) {
  const p = await b.newPage({ viewport: { width: w, height: h || 900 }, ...extra });
  p.on('pageerror', (e) => console.error('pageerror', e.message));
  await p.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 90000 });
  if (flow) await p.click(`.flow-switch [data-pick="${flow}"]`);
  await p.evaluate(() => document.querySelectorAll('img').forEach((i) => { i.loading = 'eager'; }));
  await p.waitForTimeout(2500);
  return p;
}
async function flowsOf(b) {
  if (args.flows) return String(args.flows).split(',');
  const p = await open(b, 1280);
  const f = await p.evaluate(() => [...new Set([...document.querySelectorAll('.flow-switch [data-pick]')].map((e) => e.dataset.pick))]);
  await p.close();
  return f.length ? f : [null];
}

// every check returns finding strings: "<check> <width|scheme> <flow>: <what> #<card id>"
const checks = {
  async marks(b, flows) {
    const out = [];
    for (const w of [1440, 390]) for (const flow of flows) {
      const p = await open(b, w, 900, flow);
      const r = await p.evaluate(() => {
        const f = [];
        document.querySelectorAll('.frame').forEach((fr) => {
          const R = fr.getBoundingClientRect(); if (!R.width || fr.offsetParent === null || fr.closest('.lightbox')) return;
          const h = fr.closest('.card')?.querySelector('h3')?.id || '?';
          fr.querySelectorAll('.pin').forEach((q) => { const r = q.getBoundingClientRect();
            if (r.left < R.left || r.right > R.right || r.top < R.top || r.bottom > R.bottom) f.push(`pin ${q.textContent} outside frame #${h}`); });
          const els = [...fr.querySelectorAll('.box')], bx = els.map((x) => x.getBoundingClientRect());
          bx.forEach((a, i) => bx.slice(i + 1).forEach((c) => {
            if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) f.push(`boxes overlap #${h}`); }));
          // a number on its own box is a choice (crowded shot); on another step's box it hides what that step points at
          fr.querySelectorAll('.pin').forEach((q) => { const r = q.getBoundingClientRect(); bx.forEach((a, k) => {
            if (q.dataset.n && els[k].dataset.n === q.dataset.n) return;
            const ix = Math.min(r.right, a.right) - Math.max(r.left, a.left), iy = Math.min(r.bottom, a.bottom) - Math.max(r.top, a.top);
            if (ix > r.width * .6 && iy > r.height * .6) f.push(`pin ${q.textContent} on box ${els[k].dataset.n || '?'} #${h}`); }); });
        });
        return f;
      });
      r.forEach((x) => out.push(`marks ${w} ${flow || '-'}: ${x}`)); await p.close();
    }
    return out;
  },
  async flows(b, flows) {
    const out = []; if (flows[0] === null) return out;
    for (const w of [1280, 390]) for (const flow of flows) {
      const p = await open(b, w, 900, flow);
      const r = await p.evaluate((f) => [...document.querySelectorAll('[data-flow]')]
        .filter((e) => e !== document.documentElement && !e.closest('.flow-switch') && !['all', f].includes(e.dataset.flow) && e.getClientRects().length && getComputedStyle(e).display !== 'none')
        .map((e) => e.tagName + ' "' + (e.textContent || '').trim().slice(0, 50) + '"'), flow);
      r.forEach((x) => out.push(`flows ${w} ${flow}: other flow visible ${x}`)); await p.close();
    }
    return out;
  },
  async contrast(b, flows) {
    const out = [];
    for (const flow of flows) {
      const p = await open(b, 1440, 900, flow);
      const r = await p.evaluate(() => {
        const rgb = (s) => { const m = s.match(/[\d.]+/g); return m ? m.map(Number) : null; };
        const lum = (c) => { const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
        const bg = (el) => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c && (c.length < 4 || c[3] > .5)) return c; } return [255, 255, 255]; };
        const low = new Set();
        document.querySelectorAll('body *').forEach((el) => {
          if (!el.offsetParent || el.closest('svg, .frame, figure.shot')) return;
          if (![...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim().length > 1)) return;
          const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity < .5) return;
          const fg = rgb(cs.color), B = bg(el), a = fg.length > 3 ? fg[3] : 1;
          const f2 = fg.slice(0, 3).map((v, i) => v * a + B[i] * (1 - a));
          const L1 = lum(f2), L2 = lum(B), cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
          const big = parseFloat(cs.fontSize) >= 18.5 || (parseFloat(cs.fontSize) >= 14 && +cs.fontWeight >= 700);
          if (cr < (big ? 3 : 4.5)) low.add(cr.toFixed(2) + ':1 ' + el.tagName + ' "' + el.textContent.trim().slice(0, 40) + '"');
        });
        return [...low];
      });
      r.forEach((x) => out.push(`contrast 1440 ${flow || '-'}: low ${x}`)); await p.close();
    }
    return out;
  },
  async pictures(b, flows) {
    // what a reader actually sees at 1280: screen text big enough to read, and steps tied to the picture by numbers
    const out = [];
    for (const flow of flows) {
      const p = await open(b, 1280, 900, flow);
      const r = await p.evaluate(() => {
        const f = [];
        // photos, scenes and e-mails are not app screens: no pins expected, no screen-text size to keep
        const notUi = (fig) => ['photo', 'scene', 'mail'].some((c) => fig.classList.contains(c));
        document.querySelectorAll('main .card').forEach((card) => {
          if (card.offsetParent === null) return;
          const steps = card.querySelectorAll('ol.proc > li').length;
          const figs = [...card.querySelectorAll('figure.shot')].filter((x) => x.offsetParent !== null && !notUi(x));
          // numbers may sit on any picture of the card (a row of phone screens shares the steps)
          if (steps >= 2 && figs.length && !card.querySelector('figure.shot .pin') && !figs.some((x) => x.classList.contains('annotated')))
            f.push(`${figs.length} screenshot(s) but no numbers for the ${steps} steps #${card.querySelector('h3')?.id || '?'}`);
        });
        document.querySelectorAll('main figure.shot').forEach((fig) => {
          const fr = fig.querySelector('.frame'), img = fig.querySelector('img');
          if (!fr || !img || fr.offsetParent === null || !img.naturalWidth || notUi(fig)) return;
          const h = fig.closest('.card')?.querySelector('h3')?.id || '?', name = (img.getAttribute('src') || '').split('/').pop();
          const crop = (fig.getAttribute('data-crop') || '0,0,100,100').split(',').map(Number);
          const shown = fr.getBoundingClientRect().width;
          // phone screenshots are taken at 2-3x: compare with the phone's own width in CSS px (~390)
          const real = fig.classList.contains('phone') ? 390 * (crop[2] - crop[0]) / 100 : img.naturalWidth * (crop[2] - crop[0]) / 100;
          const scale = shown / real;
          if (scale < 0.45) f.push(`${name} shows its screen at ${Math.round(scale * 100)}% of real size: text unreadable; crop to the area the steps use #${h}`);
        });
        return f;
      });
      r.forEach((x) => out.push(`pictures 1280 ${flow || '-'}: ${x}`)); await p.close();
    }
    return out;
  },
  async cover(b) {
    const out = [];
    const sizes = [[2560, 1440], [1920, 1080], [1536, 864], [1440, 900], [1366, 768], [1280, 720], [1024, 768], [768, 1024], [414, 896], [390, 844], [375, 667], [360, 640]];
    for (const [w, h] of sizes) {
      const p = await open(b, w, h);
      const r = await p.evaluate(() => {
        const c = document.querySelector('.cover');
        const bottoms = c ? [...c.querySelectorAll('*')].filter((e) => e.offsetParent).map((e) => e.getBoundingClientRect().bottom) : [0];
        return { contentBottom: Math.round(Math.max(...bottoms)), vh: innerHeight, scrollWidth: document.documentElement.scrollWidth, hasCover: !!c };
      });
      if (r.hasCover && r.contentBottom > r.vh) out.push(`cover ${w}x${h}: cover content ends ${r.contentBottom - r.vh}px below the first screen`);
      if (r.scrollWidth > w) out.push(`cover ${w}x${h}: page scrolls sideways (${r.scrollWidth}px wide)`);
      if (args.out) await p.screenshot({ path: `${args.out}-${w}x${h}.png` });
      await p.close();
    }
    return out;
  },
  async shots(b) {
    // no selector = every visible picture of the flow (figure.shot and diagrams), named after its card
    if (!args.out) { console.error('shots needs --out <dir/prefix> [css selectors...]; --sheet <file.png> also joins them into one image'); process.exit(2); }
    const p = await open(b, +(args.width || 390), 900, args.flow || null, { deviceScaleFactor: +(args.dpr || 2) });
    // the sticky top bar and the back-to-top button would otherwise sit on top of figures in element screenshots
    await p.addStyleTag({ content: '.topbar{position:static!important} .to-top{display:none!important}' });
    fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true });
    let targets;
    if (args._.length) targets = args._.map((s) => ({ loc: p.locator(s).first(), label: s }));
    else {
      const all = p.locator('main figure.shot, main figure.diagram'); const n = await all.count(); targets = [];
      for (let k = 0; k < n; k++) {
        const loc = all.nth(k); if (!(await loc.isVisible())) continue;
        const id = await loc.evaluate((e) => e.closest('.card')?.querySelector('h3')?.id || 'page');
        targets.push({ loc, label: id });
      }
    }
    const saved = []; let i = 0;
    for (const t of targets) {
      if (!(await t.loc.count()) || !(await t.loc.isVisible())) { console.log(JSON.stringify({ check: 'shots', target: t.label, saved: null, note: 'not found or hidden in this flow' })); i++; continue; }
      // a phone picture in a sideways-scrolling row is cut unless the row is scrolled to it first
      await t.loc.evaluate((e) => e.scrollIntoView({ block: 'center', inline: 'center' })); await p.waitForTimeout(300);
      const file = `${args.out}-${String(i++).padStart(2, '0')}-${t.label.replace(/[^\w-]+/g, '_').slice(0, 40)}.png`;
      await t.loc.screenshot({ path: file }); saved.push({ file, label: t.label });
      console.log(JSON.stringify({ check: 'shots', target: t.label, saved: file }));
    }
    await p.close();
    if (args.sheet && saved.length) {
      // one labelled contact sheet, so a person or an agent can look at every picture in one image
      const q = await b.newPage({ viewport: { width: 1400, height: 900 } });
      // inline the pictures: a page made with setContent is about:blank and may not load file:// images
      const url = (f) => 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');
      await q.setContent(`<body style="margin:0;background:#cfd3da;font:13px sans-serif"><div style="display:flex;flex-wrap:wrap;gap:14px;padding:14px;align-items:flex-start">${
        saved.map((s) => `<figure style="margin:0;background:#fff;padding:6px"><figcaption style="color:#b00;margin-bottom:4px">${s.label}</figcaption><img src="${url(s.file)}" style="display:block;max-width:${args.width >= 1000 ? 660 : 330}px"></figure>`).join('')}</div></body>`);
      await q.waitForTimeout(500); await q.screenshot({ path: args.sheet, fullPage: true }); await q.close();
      console.log(JSON.stringify({ check: 'shots', sheet: args.sheet, pictures: saved.length }));
    }
    return [];
  },
};

(async () => {
  const names = cmd === 'all' ? ['marks', 'flows', 'contrast', 'pictures', 'cover'] : [cmd];
  if (!names.every((n) => checks[n])) { console.error(`unknown command "${cmd}"; use all | marks | flows | contrast | pictures | cover | shots`); process.exit(2); }
  const b = await chromium.launch({ channel: args.channel || 'msedge' });
  try {
    const flows = names.some((n) => ['marks', 'flows', 'contrast', 'pictures'].includes(n)) ? await flowsOf(b) : [];
    const fresh = [], ok = [];
    for (const n of names) {
      const found = await checks[n](b, flows);
      for (const f of found) { const a = isAccepted(f); (a ? ok : fresh).push(a ? { finding: f, why: a.why || a.match } : f); }
      if (n !== 'shots') console.log(JSON.stringify({ check: n, new: found.filter((f) => !isAccepted(f)), accepted: found.filter(isAccepted).length }));
    }
    const unused = accepted.filter((a) => !ok.some((o) => o.finding.includes(a.match))).map((a) => a.match);
    if (cmd !== 'shots') console.log(JSON.stringify({ summary: fresh.length ? 'FAIL' : 'PASS', new: fresh.length, accepted: ok.length, flows, unusedAccepts: unused }));
    process.exitCode = fresh.length ? 1 : 0;
  } catch (e) { console.error(e.message); process.exitCode = 2; } finally { await b.close(); }
})();
