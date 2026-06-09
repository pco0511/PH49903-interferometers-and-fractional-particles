const { chromium } = require('playwright-core');
const path = require('path');
(async () => {
  const deck = process.argv[2];
  const B = process.argv[3] || '1';
  const Vg = process.argv[4] || '0.7';
  const out = process.argv[5] || '_live.png';
  const url = 'file:///' + deck.split(path.sep).join('/') + '#6';
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push('PAGEERROR ' + e.message));
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.evaluate(({B,Vg})=>{
    const sB=document.getElementById('s6_B'), sV=document.getElementById('s6_Vg');
    sB.value=B; sV.value=Vg;
    sB.dispatchEvent(new Event('input',{bubbles:true}));
    sV.dispatchEvent(new Event('input',{bubbles:true}));
  }, {B,Vg});
  await page.waitForTimeout(900);
  const el = await page.$('#stage');
  await el.screenshot({ path: out });
  console.log('errors:', JSON.stringify(errors));
  await browser.close();
})();
