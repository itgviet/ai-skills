#!/usr/bin/env node
// Automated checks for a one-page user guide built with this skill.
// Usage: node scripts/check_guide.cjs <command> --page <guide.html> [options]
//   marks    boxes overlapping, pins outside the frame, pins sitting on a box        (widths 1440, 390)
//   flows    elements of another flow still visible after picking a flow             (widths 1280, 390)
//   contrast text below WCAG AA (4.5:1, 3:1 for large text)                          (1440, light + dark)
//   cover    cover block fits the first screen at 12 common sizes                    (writes PNGs with --out)
//   shots    screenshot figures/cards one by one: --width 390 --flow mep --out dir/prefix --dpr 3 <css selectors...>
// Options: --flows a,b (default: read from .flow-switch [data-pick]); --channel msedge|chrome (default msedge)
// Output: one JSON object per line on stdout; exit 0 = clean, 1 = findings, 2 = usage / runtime error.
// Playwright: resolved from PLAYWRIGHT_MODULE, then require('playwright'), then require('@playwright/test').
'use strict';
const path = require('path');
const fs = require('fs');

function loadPlaywright() {
  const tries = [process.env.PLAYWRIGHT_MODULE, 'playwright', '@playwright/test'].filter(Boolean);
  for (const t of tries) { try { return require(t); } catch (e) { /* try next */ } }
  console.error('Playwright not found. Set PLAYWRIGHT_MODULE to a node_modules/playwright folder, or run `npm i -D playwright` in the project.');
  process.exit(2);
}

function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k.startsWith('--')) { const v = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true; a[k.slice(2)] = v; }
    else a._.push(k);
  }
  return a;
}

const args = parseArgs(process.argv.slice(2));
const cmd = args._.shift();
if (!cmd || args.help || !args.page) {
  console.error(fs.readFileSync(__filename, 'utf8').split('\n').filter((l) => l.startsWith('//')).map((l) => l.slice(3)).join('\n'));
  process.exit(cmd && args.page ? 0 : 2);
}
const pageUrl = 'file:///' + path.resolve(args.page).replace(/\\/g, '/');
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
  const f = await p.evaluate(() => [...document.querySelectorAll('.flow-switch [data-pick]')].map((e) => e.dataset.pick));
  await p.close();
  return f.length ? f : [null];
}

const checks = {
  async marks(b, flows) {
    let bad = 0;
    for (const w of [1440, 390]) for (const flow of flows) {
      const p = await open(b, w, 900, flow);
      const r = await p.evaluate(() => {
        const out = []; let pins = 0;
        document.querySelectorAll('.frame').forEach((fr) => {
          const R = fr.getBoundingClientRect(); if (!R.width || fr.offsetParent === null) return;
          const h = fr.closest('.card')?.querySelector('h3')?.id || '?';
          fr.querySelectorAll('.pin').forEach((q) => { pins++; const r = q.getBoundingClientRect();
            if (r.left < R.left || r.right > R.right || r.top < R.top || r.bottom > R.bottom) out.push(`pin ${q.textContent} outside frame #${h}`); });
          const bx = [...fr.querySelectorAll('.box')].map((x) => x.getBoundingClientRect());
          bx.forEach((a, i) => bx.slice(i + 1).forEach((c) => {
            if (a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) out.push(`boxes overlap #${h}`); }));
          fr.querySelectorAll('.pin').forEach((q) => { const r = q.getBoundingClientRect(); bx.forEach((a) => {
            const ix = Math.min(r.right, a.right) - Math.max(r.left, a.left), iy = Math.min(r.bottom, a.bottom) - Math.max(r.top, a.top);
            if (ix > r.width * .6 && iy > r.height * .6) out.push(`pin ${q.textContent} on a box #${h}`); }); });
        });
        return { pins, findings: out };
      });
      bad += r.findings.length; console.log(JSON.stringify({ check: 'marks', width: w, flow, ...r })); await p.close();
    }
    return bad;
  },
  async flows(b, flows) {
    let bad = 0; if (flows[0] === null) { console.log(JSON.stringify({ check: 'flows', note: 'page has no flow switch' })); return 0; }
    for (const w of [1280, 390]) for (const flow of flows) {
      const p = await open(b, w, 900, flow);
      const r = await p.evaluate((f) => [...document.querySelectorAll('[data-flow]')]
        .filter((e) => e !== document.documentElement && !['all', f].includes(e.dataset.flow) && e.getClientRects().length && getComputedStyle(e).display !== 'none')
        .map((e) => e.tagName + ': ' + (e.textContent || '').trim().slice(0, 60)), flow);
      bad += r.length; console.log(JSON.stringify({ check: 'flows', width: w, flow, wrongFlowVisible: r.slice(0, 20), count: r.length })); await p.close();
    }
    return bad;
  },
  async contrast(b, flows) {
    let bad = 0;
    for (const scheme of ['light', 'dark']) for (const flow of flows) {
      const p = await open(b, 1440, 900, flow, { colorScheme: scheme });
      const r = await p.evaluate(() => {
        const rgb = (s) => { const m = s.match(/[\d.]+/g); return m ? m.map(Number) : null; };
        const lum = (c) => { const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); };
        const bg = (el) => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c && (c.length < 4 || c[3] > .5)) return c; } return [255, 255, 255]; };
        const low = []; let n = 0;
        document.querySelectorAll('body *').forEach((el) => {
          if (!el.offsetParent || el.closest('svg, .frame, figure.shot')) return;
          if (![...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim().length > 1)) return;
          const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || +cs.opacity < .5) return;
          n++; const fg = rgb(cs.color), B = bg(el), a = fg.length > 3 ? fg[3] : 1;
          const f2 = fg.slice(0, 3).map((v, i) => v * a + B[i] * (1 - a));
          const L1 = lum(f2), L2 = lum(B), cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
          const big = parseFloat(cs.fontSize) >= 18.5 || (parseFloat(cs.fontSize) >= 14 && +cs.fontWeight >= 700);
          if (cr < (big ? 3 : 4.5)) low.push(cr.toFixed(2) + ' ' + el.tagName + ' "' + el.textContent.trim().slice(0, 40) + '"');
        });
        return { texts: n, low: [...new Set(low)] };
      });
      bad += r.low.length; console.log(JSON.stringify({ check: 'contrast', scheme, flow, texts: r.texts, low: r.low.slice(0, 25), count: r.low.length })); await p.close();
    }
    return bad;
  },
  async cover(b) {
    let bad = 0;
    const sizes = [[2560, 1440], [1920, 1080], [1536, 864], [1440, 900], [1366, 768], [1280, 720], [1024, 768], [768, 1024], [414, 896], [390, 844], [375, 667], [360, 640]];
    for (const [w, h] of sizes) {
      const p = await open(b, w, h);
      const r = await p.evaluate(() => {
        const c = document.querySelector('.cover'); if (!c) return null;
        const bottoms = [...c.querySelectorAll('*')].filter((e) => e.offsetParent).map((e) => e.getBoundingClientRect().bottom);
        return { contentBottom: Math.round(Math.max(...bottoms)), vh: innerHeight, scrollWidth: document.documentElement.scrollWidth };
      });
      if (!r) { console.log(JSON.stringify({ check: 'cover', note: 'no .cover block' })); await p.close(); return 0; }
      const ok = r.contentBottom <= r.vh && r.scrollWidth <= w; if (!ok) bad++;
      console.log(JSON.stringify({ check: 'cover', size: `${w}x${h}`, ...r, fits: ok }));
      if (args.out) await p.screenshot({ path: `${args.out}-${w}x${h}.png` });
      await p.close();
    }
    return bad;
  },
  async shots(b) {
    const sels = args._; if (!args.out || !sels.length) { console.error('shots needs --out <dir/prefix> and at least one CSS selector'); process.exit(2); }
    const p = await open(b, +(args.width || 390), 900, args.flow || null, { deviceScaleFactor: +(args.dpr || 2) });
    // the sticky top bar and the back-to-top button would otherwise sit on top of figures in element screenshots
    await p.addStyleTag({ content: '.topbar{position:static!important} .to-top,[class*="totop"],[class*="back-top"]{display:none!important}' });
    fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true });
    let i = 0;
    for (const s of sels) {
      const f = p.locator(s).first();
      if (!(await f.count()) || !(await f.isVisible())) { console.log(JSON.stringify({ check: 'shots', selector: s, saved: null, note: 'not found or hidden in this flow' })); i++; continue; }
      await f.scrollIntoViewIfNeeded(); await p.waitForTimeout(300);
      const file = `${args.out}-${i++}.png`; await f.screenshot({ path: file });
      console.log(JSON.stringify({ check: 'shots', selector: s, saved: file }));
    }
    await p.close(); return 0;
  },
};

(async () => {
  if (!checks[cmd]) { console.error(`unknown command "${cmd}"; use marks | flows | contrast | cover | shots`); process.exit(2); }
  const b = await chromium.launch({ channel: args.channel || 'msedge' });
  try {
    const flows = ['marks', 'flows', 'contrast'].includes(cmd) ? await flowsOf(b) : [];
    const bad = await checks[cmd](b, flows);
    process.exitCode = bad ? 1 : 0;
  } catch (e) { console.error(e.message); process.exitCode = 2; }
  finally { await b.close(); }
})();
