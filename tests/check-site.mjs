// End-to-end checks for the built site.
//   npm run build && npm run serve   (in one terminal)
//   npm test                         (in another)
// BASE_URL defaults to http://localhost:8080
import { chromium, devices } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const BASE = (process.env.BASE_URL || 'http://localhost:8080').replace(/\/$/, '');
const TEL = 'tel:+16022420442';
const PAGES_EN = ['/', '/tires/', '/wheel-alignment/', '/auto-repair/', '/transmission-repair/', '/privacy/', '/terms/'];
const PAGES_ES = ['/es/', '/es/llantas/', '/es/alineacion/', '/es/reparacion-automotriz/', '/es/reparacion-de-transmision/', '/es/privacidad/', '/es/terminos/'];
const PAGES = [...PAGES_EN, ...PAGES_ES];
const VIEWPORTS = {
  desktop: { viewport: { width: 1440, height: 900 } },
  tablet: devices['iPad (gen 7)'],
  iphone: devices['iPhone 13'],
  android: devices['Pixel 7'],
};

let failures = 0;
const ok = (cond, msg) => { if (cond) console.log('  ✓', msg); else { failures++; console.log('  ✗', msg); } };

const browser = await chromium.launch();

// ---------------------------------------------------------------- per page / per device
for (const [name, opts] of Object.entries(VIEWPORTS)) {
  console.log(`\n=== ${name} ===`);
  const ctx = await browser.newContext({ ...opts, serviceWorkers: 'block' });
  // third-party map embed is irrelevant to these checks and may be offline
  await ctx.route(/google\.com\/maps\?q=/, r => r.fulfill({ status: 200, contentType: 'text/html', body: '<html></html>' }));
  for (const path of PAGES) {
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    const res = await page.goto(BASE + path, { waitUntil: 'load' });
    ok(res.status() === 200, `${path} → 200`);

    const tels = await page.$$eval('a[href^="tel:"]', as => as.map(a => a.getAttribute('href')));
    ok(tels.length > 0 && tels.every(h => h === TEL), `${path}: ${tels.length} phone links all dial ${TEL}`);

    const dirs = await page.$$eval('[data-directions]', as => as.map(a => a.href));
    const isApple = /iPhone|iPad/.test(opts.userAgent || '');
    const dirOk = dirs.every(h => isApple
      ? h.startsWith('https://maps.apple.com/') && h.includes('6040%20N%20Black%20Canyon%20Hwy')
      : h.startsWith('https://www.google.com/maps/dir/') && h.includes('6040+N+Black+Canyon+Hwy%2C+Phoenix%2C+AZ+85017'));
    ok(dirs.length > 0 && dirOk, `${path}: ${dirs.length} directions links → ${isApple ? 'Apple' : 'Google'} Maps with full address`);

    const h1 = await page.$$eval('h1', els => els.length);
    ok(h1 === 1, `${path}: exactly one <h1>`);

    const noHScroll = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1);
    ok(noHScroll, `${path}: no horizontal scroll`);

    if (name !== 'desktop') {
      // touch targets: every visible link/button at least 44px tall (inline text links excepted)
      const small = await page.$$eval('a, button, input, select, textarea', els => els.filter(el => {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return false;
        const cs = getComputedStyle(el);
        if (cs.visibility === 'hidden' || el.closest('[hidden], .hp, .visually-hidden, .skip-link')) return false;
        if (el.tagName === 'A' && cs.display === 'inline') return false; // links inside sentences
        return r.height < 44;
      }).map(el => (el.textContent || el.name || el.tagName).trim().slice(0, 40)));
      ok(small.length === 0, `${path}: touch targets ≥ 44px ${small.length ? JSON.stringify(small) : ''}`);
    }

    const bar = await page.$eval('.action-bar', el => getComputedStyle(el).display !== 'none');
    ok(name === 'desktop' || name === 'tablet' ? true : bar, `${path}: mobile action bar ${bar ? 'shown' : 'hidden'}`);

    if (name === 'desktop' || name === 'iphone') {
      await page.waitForTimeout(1500); // let entrance animations finish before measuring contrast
      const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).exclude('iframe').analyze();
      const v = axe.violations.map(x => `${x.id} (${x.nodes.length})`);
      ok(v.length === 0, `${path}: axe WCAG A/AA ${v.length ? JSON.stringify(v) : 'no violations'}`);
    }
    ok(errors.length === 0, `${path}: no console errors ${errors.length ? JSON.stringify(errors) : ''}`);
    await page.close();
  }
  await ctx.close();
}

// ---------------------------------------------------------------- links
console.log('\n=== internal links ===');
{
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const seen = new Set();
  for (const path of PAGES) {
    await page.goto(BASE + path);
    const links = await page.$$eval('a[href]', as => as.map(a => a.href));
    for (const l of links) {
      const u = new URL(l);
      if (u.origin !== new URL(BASE).origin) continue;
      const key = u.pathname;
      if (!seen.has(key)) {
        seen.add(key);
        const r = await ctx.request.get(BASE + key);
        ok(r.status() === 200, `${key} → ${r.status()}`);
      }
      if (u.hash && u.hash.length > 1) {
        const target = await ctx.request.get(BASE + u.pathname).then(r => r.text());
        ok(target.includes(`id="${u.hash.slice(1)}"`), `${key}${u.hash} anchor exists`);
      }
    }
  }
  const r404 = await ctx.request.get(BASE + '/404.html');
  ok(r404.status() === 200, '/404.html exists');
  for (const f of ['/sitemap.xml', '/robots.txt', '/site.webmanifest', '/assets/img/og-image.png']) {
    ok((await ctx.request.get(BASE + f)).status() === 200, `${f} served`);
  }
  await ctx.close();
}

// ---------------------------------------------------------------- interactions
console.log('\n=== interactions (iPhone) ===');
{
  const ctx = await browser.newContext({ ...devices['iPhone 13'] });
  const page = await ctx.newPage();
  await page.goto(BASE + '/');

  // mobile menu
  await page.click('[data-menu-toggle]');
  ok(await page.isVisible('#site-nav'), 'menu opens');
  ok(await page.getAttribute('[data-menu-toggle]', 'aria-expanded') === 'true', 'menu toggle aria-expanded=true');
  await page.keyboard.press('Escape');
  ok(!(await page.isVisible('#site-nav')), 'Escape closes menu');
  await page.click('[data-menu-toggle]');
  await page.click('#site-nav a[href$="#reviews"]');
  ok(!(await page.isVisible('#site-nav')), 'nav link click closes menu');

  // symptom picker
  ok(await page.isHidden('[data-problem-answer]'), 'symptom answer hidden initially');
  await page.click('.problem[data-problem="Uneven tire wear"]');
  ok(await page.isVisible('[data-problem-answer]'), 'symptom answer revealed');
  ok((await page.textContent('[data-problem-answer]')).includes("Let's take a look."), 'shows "Let\'s take a look."');
  ok(await page.getAttribute('.problem[data-problem="Uneven tire wear"]', 'aria-pressed') === 'true', 'selected card aria-pressed');
  ok(await page.$eval('[data-problem-answer] a[href^="tel:"]', a => a.getAttribute('href')) === TEL, 'symptom CTA calls shop');
  await page.click('[data-problem-request]');
  ok((await page.inputValue('#f-message')).includes('Uneven tire wear'), 'symptom pre-fills request message');

  // alignment toggle
  await page.click('[data-align-set="1"]');
  ok(await page.$eval('[data-align-viz]', el => el.classList.contains('is-aligned')), 'alignment toggle → aligned');
  await page.click('[data-align-set="0"]');
  ok(await page.$eval('[data-align-viz]', el => !el.classList.contains('is-aligned')), 'alignment toggle → misaligned');

  // form: validation
  await page.fill('#f-message', '');
  await page.selectOption('#f-service', '');
  await page.click('.request-form button[type="submit"]');
  const invalid = await page.$$eval('[aria-invalid="true"]', els => els.map(e => e.name));
  ok(['name', 'phone', 'service'].every(n => invalid.includes(n)), `empty submit flags required fields ${JSON.stringify(invalid)}`);
  ok(await page.isHidden('[data-form-status]'), 'no status message on invalid submit');

  const fill = async () => {
    await page.fill('#f-name', 'Test Driver');
    await page.fill('#f-phone', '(602) 555-0100');
    await page.fill('#f-year', '2014');
    await page.selectOption('#f-service', 'Alignment');
  };
  // form: no endpoint configured → must NOT claim success
  await fill();
  await page.click('.request-form button[type="submit"]');
  const noEndpoint = await page.textContent('[data-form-status]');
  ok(!noEndpoint.includes('received your request') && noEndpoint.includes('not sent'), 'no endpoint → honest "not sent" message');
  await ctx.close();
}

for (const [status, expectSuccess] of [[200, true], [500, false]]) {
  const ctx = await browser.newContext({ ...devices['Pixel 7'] });
  await ctx.addInitScript(() => {
    Object.defineProperty(window, 'HUGOS_CONFIG', {
      configurable: true,
      set(v) { v.formEndpoint = 'https://forms.test/submit'; Object.defineProperty(window, 'HUGOS_CONFIG', { value: v, writable: true }); },
      get() { return undefined; },
    });
  });
  let posted = null;
  await ctx.route('https://forms.test/submit', r => { posted = r.request().postData(); r.fulfill({ status, body: '{}' }); });
  const page = await ctx.newPage();
  await page.goto(BASE + '/#request');
  await page.fill('#f-name', 'Test Driver');
  await page.fill('#f-phone', '602-555-0100');
  await page.selectOption('#f-service', 'Tires');
  await page.click('.request-form button[type="submit"]');
  await page.waitForSelector('[data-form-status]:not([hidden])');
  const txt = await page.textContent('[data-form-status]');
  ok(posted && posted.includes('Test Driver'), `endpoint ${status}: form data posted`);
  ok(expectSuccess ? txt.includes("Thanks. Hugo's received your request.") : !txt.includes('received your request'),
    `endpoint ${status}: ${expectSuccess ? 'success shown' : 'success NOT shown'}`);
  await ctx.close();
}

// ---------------------------------------------------------------- Spanish
console.log('\n=== español ===');
{
  const ctx = await browser.newContext({ ...devices['Pixel 7'] });
  const page = await ctx.newPage();
  for (let i = 0; i < PAGES_EN.length; i++) {
    await page.goto(BASE + PAGES_EN[i]);
    ok(await page.getAttribute('html', 'lang') === 'en', `${PAGES_EN[i]}: lang="en"`);
    await page.click('[data-lang-switch]');
    await page.waitForLoadState('load');
    ok(new URL(page.url()).pathname === PAGES_ES[i], `${PAGES_EN[i]} → switch → ${PAGES_ES[i]}`);
    ok(await page.getAttribute('html', 'lang') === 'es', `${PAGES_ES[i]}: lang="es"`);
    const hre = await page.$$eval('link[rel=alternate][hreflang]', ls => ls.map(l => l.hreflang).sort().join(','));
    ok(hre === 'en,es,x-default', `${PAGES_ES[i]}: hreflang alternates`);
    await page.click('[data-lang-switch]');
    await page.waitForLoadState('load');
    ok(new URL(page.url()).pathname === PAGES_EN[i], `${PAGES_ES[i]} → switch → ${PAGES_EN[i]}`);
  }
  await page.goto(BASE + '/es/');
  await page.click('.problem[data-problem="Ruido extraño"]');
  ok((await page.textContent('[data-problem-answer]')).includes('Vamos a revisarlo.'), 'es: "Vamos a revisarlo."');
  await page.click('[data-problem-request]');
  ok((await page.inputValue('#f-message')).includes('Lo que estoy notando: Ruido extraño'), 'es: symptom pre-fills message in Spanish');
  await page.fill('#f-message', '');
  await page.selectOption('#f-service', '');
  await page.click('.request-form button[type="submit"]');
  ok((await page.textContent('#f-name-error')) === 'Por favor escribe tu nombre.', 'es: validation messages in Spanish');
  await page.fill('#f-name', 'Prueba');
  await page.fill('#f-phone', '602-555-0100');
  await page.selectOption('#f-service', 'Tires');
  await page.click('.request-form button[type="submit"]');
  const st = await page.textContent('[data-form-status]');
  ok(st.includes('no se envió') && !st.includes('recibió'), 'es: no endpoint → honest "no se envió" message');
  await ctx.close();
}

// ---------------------------------------------------------------- reduced motion
{
  const ctx = await browser.newContext({ reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  await page.goto(BASE + '/');
  ok(await page.$eval('[data-align-viz]', el => el.classList.contains('is-aligned')), 'reduced motion: alignment shows static aligned state');
  const reveal = await page.$eval('.services .reveal', el => getComputedStyle(el).opacity);
  ok(reveal === '1', 'reduced motion: content visible without scroll animation');
  await ctx.close();
}

await browser.close();
console.log(failures ? `\n${failures} check(s) FAILED` : '\nAll checks passed');
process.exit(failures ? 1 : 0);
