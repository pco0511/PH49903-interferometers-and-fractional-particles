// Headless smoke-test for all viz pages using system Edge (no browser download).
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const VIZ = path.join(__dirname, 'viz');
const OUT = path.join(__dirname, 'figures', 'viz-tests');
fs.mkdirSync(OUT, { recursive: true });

const PAGES = [
  'index.html',
  'concepts/a1-braiding.html',
  'concepts/a2-phase-decomposition.html',
  'concepts/a3-dos-regimes.html',
  'concepts/a4-energy-occupation.html',
  'device/b1-device-edge.html',
  'device/b2-layer-stack.html',
  'measurements/c2-linecut.html',
  'measurements/c3-lever-arm.html',
  'measurements/c4-temperature.html',
  'measurements/c5-velocity-checkerboard.html',
  'measurements/c6-nu1-control.html',
  'simulation/d1-heatmap.html',
  'simulation/d3-width-calculator.html',
  'prototypes/index.html',
  'prototypes/p-slice-crosshair.html',
  'prototypes/p-slice-measured.html',
  'prototypes/p-compare-sidebyside.html',
  'prototypes/p-compare-overlay.html',
  'prototypes/p-derivation-phasor.html',
  'prototypes/p-derivation-twopath.html',
];

(async () => {
  const browser = await chromium.launch({ executablePath: EDGE, headless: true });
  const results = [];
  for (const rel of PAGES) {
    const ctx = await browser.newContext({ viewport: { width: 1180, height: 820 } });
    const page = await ctx.newPage();
    const errs = [];
    page.on('console', m => { if (m.type() === 'error') errs.push('console.error: ' + m.text()); });
    page.on('pageerror', e => errs.push('pageerror: ' + e.message));
    const url = 'file:///' + path.join(VIZ, rel).replace(/\\/g, '/');
    try {
      await page.goto(url, { waitUntil: 'load', timeout: 15000 });
      // interact: nudge each range slider once to exercise handlers
      const sliders = await page.$$('input[type=range]');
      for (const s of sliders.slice(0, 8)) {
        try { await s.evaluate(el => { el.value = el.value; el.dispatchEvent(new Event('input', { bubbles: true })); }); } catch (e) {}
      }
      await page.waitForTimeout(400);
      const shot = path.join(OUT, rel.replace(/[\/]/g, '__').replace('.html', '.png'));
      await page.screenshot({ path: shot });
      results.push({ rel, ok: errs.length === 0, errs });
    } catch (e) {
      results.push({ rel, ok: false, errs: ['NAV: ' + e.message] });
    }
    await ctx.close();
  }
  await browser.close();
  let bad = 0;
  for (const r of results) {
    if (r.ok) { console.log('PASS  ' + r.rel); }
    else { bad++; console.log('FAIL  ' + r.rel); r.errs.forEach(e => console.log('        ' + e)); }
  }
  console.log('\n' + (results.length - bad) + '/' + results.length + ' pages clean. screenshots -> figures/viz-tests/');
  process.exit(bad ? 1 : 0);
})();
