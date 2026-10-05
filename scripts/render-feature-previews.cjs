// Screenshot the HTML layout exported by preview-familiarfaces-ui.py.
// Requires Playwright and an installed Chromium browser; no browser download.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');
(async () => {
  const candidates = [process.env.FAMILIARFACES_PREVIEW_BROWSER,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].filter(Boolean);
  const executablePath = candidates.find(candidate => fs.existsSync(candidate));
  if (!executablePath) throw new Error('Set FAMILIARFACES_PREVIEW_BROWSER to an installed Chromium executable.');
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const page = await browser.newPage({ viewport: { width: 1160, height: 900 }, deviceScaleFactor: 1 });
    for (const state of ['adventures', 'companions', 'forgetting', 'reunion']) {
      const source = path.resolve(__dirname, '../assets/curseforge/familiar-faces-' + state + '.html');
      await page.goto(pathToFileURL(source).href);
      await page.evaluate(() => Promise.all([...document.images].map(img => img.decode())));
      await page.screenshot({ path: source.replace('.html', '.png'), fullPage: true });
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exit(1); });
