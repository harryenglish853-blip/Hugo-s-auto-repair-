# Hugo's Alignment, Tires & Auto Repair: website

A fast, mobile-first static website for **Hugo's Alignment, Tires & Auto Repair**,
6040 N Black Canyon Hwy, Phoenix, AZ 85017 · (602) 242-0442 · Mon–Sat 8:00 AM–6:00 PM.

Plain HTML, CSS and JavaScript with no framework and no runtime dependencies. It's hosted on **GitHub Pages**
(see *Going live*), and the built `dist/` folder works on any static host.

## Pages

| URL | Purpose |
| --- | --- |
| `/` | Home: hero, trust strip, services, "What is your car doing?", alignment feature, tires, shop gallery, reviews, location + map, service request form, final CTA |
| `/tires/` | Tire Shop, Phoenix AZ |
| `/wheel-alignment/` | Wheel Alignment, Phoenix AZ |
| `/auto-repair/` | Auto Repair, Phoenix AZ |
| `/transmission-repair/` | Transmission Repair, Phoenix AZ |
| `/privacy/`, `/terms/` | Legal starting points |
| `/404.html` | Not-found page |

**Spanish (español):** every page has a Spanish version with an **EN/ES switch** in the header:
`/es/`, `/es/llantas/`, `/es/alineacion/`, `/es/reparacion-automotriz/`, `/es/reparacion-de-transmision/`,
`/es/privacidad/`, `/es/terminos/`. Each pair is linked with `hreflang` tags and sitemap alternates so
Google shows Spanish speakers the Spanish page. Form messages, open/closed status and other script text are
translated too. Form submissions include a `language` field, so the shop knows which language to reply in.

Every phone button dials `tel:+16022420442`. Every directions button opens Google Maps with the
full address (Apple Maps on iPhone, iPad and Mac). A persistent **Call Now | Directions** bar sits at
the bottom of the screen on phones.

## Going live (GitHub Pages)

The site is built by `tools/build.py` into `dist/` and published by `.github/workflows/deploy.yml`
every time `main` changes. Only `dist/` is published, never the source files.

**One-time setup (about 2 minutes):**
1. Merge this branch into `main`.
2. In the GitHub repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Open the **Actions** tab. "Deploy site" runs automatically (or click **Run workflow**). When it finishes, the site is live at
   **https://harryenglish853-blip.github.io/Hugo-s-auto-repair-/**

Every later change to `main` redeploys automatically. "Site checks" runs the full test suite on every push and pull request.

### Settings you can change later (each is one edit, then commit to `main`)

| What | Where | Notes |
| --- | --- | --- |
| **Hours** | `OPENS` / `CLOSES` in `tools/build.py` (24-hour clock, e.g. `"19:00"`) | Updates every page in both languages, the open/closed badge and Google's structured data. The site currently says **8:00 AM – 6:00 PM**. Yelp says 7:00 PM, so confirm with the shop. |
| **Request form** | `formEndpoint` in `assets/js/site-config.js` | Until it's set, visitors see a "Call or stop by" panel instead of the form. Paste a form service URL (e.g. a free [Formspree](https://formspree.io) form that emails the shop) and the form appears. It only says "received" after a successful send. |
| **Domain** | `CUSTOM_DOMAIN` in `tools/build.py` (e.g. `"www.hugosautophx.com"`) | The build writes the `CNAME` file and updates canonical URLs, sitemap and social previews. At the domain registrar, add a `CNAME` record for `www` → `harryenglish853-blip.github.io`. Then in Settings → Pages, enter the domain and tick **Enforce HTTPS**. |

## Before or after launch: checklist

1. **Keep the business listings consistent.** The Yelp listing, the flyer and the site all use "Hugo's Alignment, Tires & Auto Repair".
   Make sure Google Business Profile, Facebook and Apple Maps use the same name, address and phone.
2. **Confirm financing providers** (Snap Finance, Koalafi, EasyPay Finance) are still current.
3. **Have a native speaker skim the Spanish pages.**
4. **Owner review of `/privacy/` and `/terms/`** (ideally with an attorney).
5. **After launch:** add the site to Google Search Console, submit `sitemap.xml`, and put the website link on the Google Business Profile, Yelp and Facebook.
6. **Nice to have:** the original high-res logo file (see *Logo* below), more photos (shop front, alignment rack, the team) and genuine reviews.

### Logo

The site uses the owner's current logo, "HUGO'S · Alignment, Tires & Auto Repair", which matches the business name
on the site, the Yelp listing and the flyer. It was cut out of the owner's flyer (`src/logo-source.png`, 438px),
which holds up at header and hero sizes. The older "Alignment and Tire Shop LLC" version is kept for reference in
`src/logo-source-llc-version.png` (it also still appears inside one of the owner's own photo posts in the gallery).
If the owner has the original high-res logo file, replace `src/logo-source.png` and re-export
`logo-200.png`, `logo-400.png` and `logo-full.png`, plus the icons `favicon-48.png`, `apple-touch-icon.png` and `icon-512.png`.

## Brand

Everything visual is taken from the shop's logo:

| | Value | From the logo |
| --- | --- | --- |
| Yellow | `#F9D10E` (gradient `#FFEC7A → #F9D10E → #E9B50C`) | "HUGO'S" lettering, stars, shield stripe |
| Chrome | `#F6F7F9 → #9C9EA4 → #74777E` gradient | shield, pistons, car |
| Black | `#0A0A0E` + perforated-metal texture (pure CSS) | the logo's background plate |
| Headings | **Saira ExtraBold Italic** (self-hosted) | heavy slanted "HUGO'S" lettering |
| Labels & body | **Arimo** Regular/Bold (self-hosted, Arial-metric) | the logo's small uppercase lettering |

The colour tokens live at the top of `assets/css/styles.css`. The illustration accent is `YELLOW` in `tools/generate_art.py`.

## Content sources

Everything factual comes from the owner's own material:
- **Yelp listing + "Specialties"**: 10+ years in business and the owner's statement (the quote in "The shop", the footer line
  on every page, and the business description in the structured data)
- **Owner's Spanish flyer**: full service list, values ("Trabajo de calidad · Precios honestos · Manteniendo tu camino"),
  the Spanish tagline "Tu taller de confianza para todo tu vehículo", and financing through Snap Finance, Koalafi and EasyPay Finance
- **Owner's Yelp photo posts**: the five work photos and their captions

Financing providers are named in text only (no third-party logos). Confirm they're still current before launch.

## Editing content

- **Owner settings:** `assets/js/site-config.js`. This file holds the form endpoint, hero video, reviews and the reviews link.
- **Page text:** `src/pages/*.html`. **Shared header/footer/CTAs:** `src/partials/`.
  After editing anything in `src/`, run:

```bash
npm run build      # regenerates the Spanish home page, then writes everything into dist/
```

**Spanish pages:** the Spanish home page is generated from the English one:
`python3 tools/make_es_home.py` applies the string pairs in `tools/translations_home_es.py`.
If you change English text on the home page, add or adjust the matching pair. The script stops and lists any
English string it can't find, so nothing slips through untranslated. Other Spanish pages live in `src/pages/es/`,
and the Spanish header, footer and CTA blocks are in `src/partials/es/`.

Name, address, phone and hours are defined once in `tools/build.py` and injected everywhere,
including the `AutoRepair` structured data.

### Adding real shop photos

The **Local shop. Real people. Real work.** gallery (in `src/pages/index.html`) shows four photos the owner posted
to Yelp, captioned with the owner's own post titles. They're stored in `assets/img/shop/` at 480/800/1180px as
JPEG + WebP. The Tires, Wheel Alignment and Auto Repair pages each lead with the matching photo. To add more, export the same
sizes and copy a `<figure>` in the gallery. Good next shots: the shop exterior, the alignment rack, and the team.
Use only authentic photos of Hugo's.

Export tip: 1600px and 800px wide versions, AVIF quality ~50 and WebP quality ~75
(e.g. `npx @squoosh/cli` or `sharp`).

### Adding hero video

Set `heroVideo` in `assets/js/site-config.js` (WebM + MP4 + poster). The video only loads for visitors
who haven't enabled reduced motion or data-saver, and the illustrated scene stays as the fallback.
Keep clips short (6–12 s), muted, ~1280px wide, under ~3 MB.

### Adding reviews

Add entries to `reviews` in `assets/js/site-config.js`. **Genuine, verbatim reviews only**, with the rating
exactly as on the source and only reviews the business is allowed to display. Never write, edit or
"improve" reviews.

## Illustrations

The technical line-art (tire tread, alignment, brake/torque wrench, planetary gear set, tire detail sequence,
shop at dusk, animated hero wheel on an alignment rack) is generated by `tools/generate_art.py`.
The drawings avoid logos and text on equipment, and the mechanics are plausible: the gear set uses consistent tooth counts and speeds,
the caliper doesn't rotate with the wheel, and lug nuts show the star tightening pattern. Regenerate with
`python3 tools/generate_art.py && python3 tools/build.py`.

## Testing

```bash
npm install
npm run build
npm run serve        # serves dist/ at http://localhost:8080
npm test             # in a second terminal
```

`tests/check-site.mjs` loads every page on desktop, iPad, iPhone and Android viewports and checks:

- every phone link dials (602) 242-0442 and every directions link goes to the full address
- all internal links and anchors resolve, with no console errors and no horizontal scrolling
- one `<h1>` per page, touch targets ≥ 44px, and the mobile action bar
- axe-core WCAG 2.1 A/AA
- mobile menu, symptom picker, alignment toggle, reduced-motion behaviour
- both languages: the EN/ES switch on every page, `hreflang` tags, and Spanish form messages
- the "Call or stop by" panel while no form endpoint is set; with an endpoint set: validation, a success message on a 2xx response only, and an error on a 5xx response

Lighthouse (local, uncompressed server): Performance 95–100, Accessibility 100, Best Practices 100, SEO 100
on mobile and desktop. Production hosts that serve gzip/brotli will do slightly better.
