const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const file = process.argv[2];
  const out = process.argv[3] || '_shot.png';
  const url = 'file:///' + file.split(path.sep).join('/');
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1060, height: 560 }, deviceScaleFactor: 2 });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);   // let the animation sweep a bit
  const el = await page.$('#cv');
  if (el) await el.screenshot({ path: out });
  else await page.screenshot({ path: out });
  console.log('errors:', JSON.stringify(errors));
  await browser.close();
})();
