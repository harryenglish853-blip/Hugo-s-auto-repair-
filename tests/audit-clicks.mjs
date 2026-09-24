// Clicks every link and button on every page (EN + ES, desktop + phone) and checks where each one goes.
//   npm run build && npm run serve   (then)   node tests/audit-clicks.mjs
// BASE_URL may include a sub-path, e.g. http://localhost:8081/Hugo-s-auto-repair-  (mirrors GitHub Pages)
import { chromium, devices } from 'playwright';

const BASE = (process.env.BASE_URL || 'http://localhost:8080').replace(/\/$/, '');
const ORIGIN = new URL(BASE).origin;
const TEL = 'tel:+16022420442';
const ADDRESS_GOOGLE = 'destination=6040+N+Black+Canyon+Hwy%2C+Phoenix%2C+AZ+85017';
const ADDRESS_APPLE = 'daddr=6040%20N%20Black%20Canyon%20Hwy%2C%20Phoenix%2C%20AZ%2085017';
const PAGES = ['/', '/tires/', '/wheel-alignment/', '/auto-repair/', '/transmission-repair/', '/privacy/', '/terms/',
  '/es/', '/es/llantas/', '/es/alineacion/', '/es/reparacion-automotriz/', '/es/reparacion-de-transmision/', '/es/privacidad/', '/es/terminos/'];
const EXTERNAL_OK = [/^https:\/\/www\.google\.com\/maps\//, /^https:\/\/maps\.apple\.com\//, /^https:\/\/www\.yelp\.com\/biz\//, /^https:\/\/www\.facebook\.com\//, /^https:\/\/www\.instagram\.com\/hugosalignment_\/$/];
const VIEWPORTS = { desktop: { viewport: { width: 1440, height: 900 } }, iphone: devices['iPhone 13'], android: devices['Pixel 7'] };

let failures = 0, checks = 0;
const fail = (msg) => { failures++; console.log('  ✗', msg); };
const pass = () => { checks++; };
const externals = new Set();
const pageCache = new Map();

const browser = await chromium.launch();

async function fetchHtml(ctx, url) {
  const key = url.split('#')[0];
  if (!pageCache.has(key)) {
    const r = await ctx.request.get(key);
    pageCache.set(key, { status: r.status(), html: r.status() === 200 ? await r.text() : '' });
  }
  return pageCache.get(key);
}

for (const [vname, vopts] of Object.entries(VIEWPORTS)) {
  const ctx = await browser.newContext({ ...vopts });
  await ctx.route(/google\.com\/maps\?q=/, r => r.fulfill({ status: 200, contentType: 'text/html', body: '<html></html>' }));
  const isApple = /iPhone|iPad/.test(vopts.userAgent || '');
  let perViewport = 0;
  for (const path of PAGES) {
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const res = await page.goto(BASE + path, { waitUntil: 'load' });
    if (res.status() !== 200) { fail(`[${vname}] ${path} returned ${res.status()}`); await page.close(); continue; }

    // ---- every <a>
    const links = await page.$$eval('a', as => as.map((a, i) => ({
      i, href: a.getAttribute('href'), abs: a.href, text: (a.textContent || a.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 40),
      target: a.target, rel: a.rel, visible: !!(a.offsetWidth || a.offsetHeight || a.getClientRects().length) && getComputedStyle(a).visibility !== 'hidden',
      directions: a.hasAttribute('data-directions'), hidden: !!a.closest('[hidden]'),
    })));
    for (const l of links) {
      const where = `[${vname}] ${path} "${l.text}"`;
      if (!l.href || l.href === '#') { fail(`${where}: empty href`); continue; }
      if (l.href.startsWith('tel:')) { l.abs === TEL ? pass() : fail(`${where}: dials ${l.href}`); continue; }
      if (l.href.startsWith('mailto:')) { fail(`${where}: unexpected mailto`); continue; }
      if (l.directions) {
        const ok = isApple ? l.abs.includes(ADDRESS_APPLE) : l.abs.includes(ADDRESS_GOOGLE);
        ok ? pass() : fail(`${where}: directions → ${l.abs}`);
        (l.target === '_blank' && l.rel.includes('noopener')) ? pass() : fail(`${where}: directions should open in a new tab safely`);
        continue;
      }
      const u = new URL(l.abs);
      if (u.origin !== ORIGIN) {
        EXTERNAL_OK.some(re => re.test(l.abs)) ? pass() : fail(`${where}: unexpected external link ${l.abs}`);
        externals.add(l.abs);
        (l.target === '_blank' && l.rel.includes('noopener')) ? pass() : fail(`${where}: external link should open in a new tab safely`);
        continue;
      }
      // internal: target page must exist, and the #anchor must exist on it
      if (!u.pathname.startsWith(new URL(BASE + '/').pathname)) { fail(`${where}: escapes the site path → ${u.pathname}`); continue; }
      const t = await fetchHtml(ctx, l.abs);
      t.status === 200 ? pass() : fail(`${where}: → ${u.pathname} returned ${t.status}`);
      if (u.hash && u.hash.length > 1) {
        t.html.includes(`id="${decodeURIComponent(u.hash.slice(1))}"`) ? pass() : fail(`${where}: anchor ${u.hash} missing on ${u.pathname}`);
      }
      perViewport++;
    }

    // ---- actually click every visible internal link and confirm where it lands
    const internal = links.filter(l => l.visible && !l.hidden && !l.directions && l.href && !l.href.startsWith('tel:') && new URL(l.abs).origin === ORIGIN);
    const seen = new Set();
    for (const l of internal) {
      if (seen.has(l.abs)) continue;
      seen.add(l.abs);
      const p2 = await ctx.newPage();
      await p2.goto(BASE + path, { waitUntil: 'load' });
      await p2.evaluate(() => document.documentElement.style.scrollBehavior = 'auto');
      const a = p2.locator('a').nth(l.i);
      // links inside the closed mobile menu: open it first
      if (!(await a.isVisible())) {
        const toggle = p2.locator('[data-menu-toggle]');
        if (await toggle.isVisible()) await toggle.click();
      }
      if (!(await a.isVisible())) { await p2.close(); continue; }
      const expected = new URL(l.abs);
      try {
        await a.click({ timeout: 5000 });
      } catch {
        // keyboard-only links (e.g. "Skip to content" appears on focus): use them the way a keyboard user would
        await a.focus(); await p2.keyboard.press('Enter');
      }
      await p2.waitForLoadState('load');
      await p2.waitForTimeout(150);
      const landed = new URL(p2.url());
      const samePath = landed.pathname === expected.pathname && landed.hash === expected.hash;
      samePath ? pass() : fail(`[${vname}] ${path} click "${l.text}" landed on ${landed.pathname}${landed.hash}, expected ${expected.pathname}${expected.hash}`);
      if (expected.hash.length > 1) {
        const inView = await p2.evaluate(h => { const el = document.getElementById(h); if (!el) return false; const r = el.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; }, decodeURIComponent(expected.hash.slice(1)));
        inView ? pass() : fail(`[${vname}] ${path} click "${l.text}": ${expected.hash} not scrolled into view`);
      }
      await p2.close();
    }

    // ---- every <button>: visible ones must do something when clicked
    const buttons = await page.$$eval('button', bs => bs.map((b, i) => ({
      i, text: (b.textContent || b.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 40),
      visible: !!(b.offsetWidth || b.offsetHeight) && !b.closest('[hidden]'), type: b.type, inForm: !!b.form,
    })));
    for (const b of buttons) {
      if (!b.visible) continue;
      const where = `[${vname}] ${path} button "${b.text}"`;
      const btn = page.locator('button').nth(b.i);
      const before = await page.evaluate(() => document.body.innerHTML.length + '|' + [...document.querySelectorAll('[aria-pressed],[aria-expanded],[hidden],.is-aligned')].map(e => e.getAttribute('aria-pressed') + e.getAttribute('aria-expanded') + e.hidden + e.className).join());
      await btn.click();
      await page.waitForTimeout(120);
      const after = await page.evaluate(() => document.body.innerHTML.length + '|' + [...document.querySelectorAll('[aria-pressed],[aria-expanded],[hidden],.is-aligned')].map(e => e.getAttribute('aria-pressed') + e.getAttribute('aria-expanded') + e.hidden + e.className).join());
      before !== after ? pass() : fail(`${where}: clicking it changed nothing`);
      // close the menu again if it was the menu toggle
      if (await page.locator('[data-menu-toggle][aria-expanded="true"]').count()) await page.keyboard.press('Escape');
    }
    errors.length ? fail(`[${vname}] ${path}: script errors ${JSON.stringify(errors)}`) : pass();
    await page.close();
  }
  console.log(`${vname}: checked ${perViewport} internal link targets`);
  await ctx.close();
}

// ---- external links respond (network permitting)
console.log('\nexternal links:');
for (const url of externals) console.log('  ', url);

await browser.close();
console.log(failures ? `\n${failures} problem(s) found (${checks} checks passed)` : `\nAll ${checks} link/button checks passed`);
process.exit(failures ? 1 : 0);
