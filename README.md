# Hugo's Alignment, Tires & Auto Repair: website

A fast, mobile-first static website for **Hugo's Alignment, Tires & Auto Repair**,
6040 N Black Canyon Hwy, Phoenix, AZ 85017 · (602) 242-0442 · Mon–Sat 8:00 AM–6:00 PM.

Plain HTML, CSS and JavaScript. It needs no framework and has no runtime dependencies, so it works on any static host
(Netlify, Cloudflare Pages, GitHub Pages, Vercel, S3, or ordinary shared hosting).

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

Every phone button dials `tel:+16022420442`. Every directions button opens Google Maps with the
full address (Apple Maps on iPhone, iPad and Mac). A persistent **Call Now | Directions** bar sits at
the bottom of the screen on phones.

## Before launch: checklist

1. **Set the domain.** In `tools/build.py` set `SITE_URL` (currently `https://www.example.com`), then run
   `python3 tools/build.py`. This updates canonical URLs, Open Graph tags, structured data, `sitemap.xml`
   and `robots.txt`.
2. **Connect the service request form.** In `assets/js/site-config.js` set `formEndpoint` to a form
   service URL (e.g. [Formspree](https://formspree.io), Basin, Getform, or your own endpoint). Until this is
   set, the form **does not** claim success. It tells the visitor the request wasn't sent and asks them to call.
   The success message "Thanks. Hugo's received your request." appears only after the endpoint returns a 2xx response.
3. **Confirm the hours.** The site uses **Mon–Sat 8:00 AM–6:00 PM**, as provided. Some public listings (e.g. Yelp)
   show 7:00 PM. Make sure every listing matches.
4. **Confirm the business name on listings.** Yelp lists the shop as "Hugo's Alignment & Tire Shop". For local SEO,
   keep the name, address and phone identical everywhere (Google Business Profile, Yelp, Facebook, Apple Maps).
5. **More photos and video.** Four real photos of the shop's work (from the owner's Yelp posts) are in the gallery and service pages. Add more, plus a hero video if the owner has one (see below).
6. **Add genuine reviews** (see below), or leave the section as-is: it links out to Yelp.
7. **Logo file.** The logo in `assets/img/logo-*.png` was cut out of a phone screenshot of the owner's
   artwork (`src/logo-source.png`, 576px). It holds up at header and hero sizes. If the owner has the original
   high-res file (PNG with transparency, SVG, or the designer's source), replace `src/logo-source.png` and re-export
   `logo-200.png`, `logo-400.png` and `logo-576.png` at those widths. The logo reads "Hugo's Alignment and Tire Shop LLC".
   The site keeps "Hugo's Alignment, Tires & Auto Repair" as the business name, as requested. Pick one name to use on every listing.
8. Have the owner review `/privacy/` and `/terms/` (ideally with an attorney).
9. After launch, submit `sitemap.xml` in Google Search Console and link the site from the Google Business Profile.

## Brand

Everything visual is taken from the shop's logo:

| | Value | From the logo |
| --- | --- | --- |
| Yellow | `#F9D10E` (gradient `#FFEC7A → #F9D10E → #E9B50C`) | "HUGO'S" lettering, stars, shield stripe |
| Chrome | `#F6F7F9 → #9C9EA4 → #74777E` gradient | shield, pistons, car |
| Black | `#0A0A0E` + perforated-metal texture (pure CSS) | the logo's background plate |
| Headings | **Saira ExtraBold Italic** (self-hosted) | heavy slanted "HUGO'S" lettering |
| Labels & body | **Arimo** Regular/Bold (self-hosted, Arial-metric) | "ALIGNMENT AND TIRE SHOP LLC" line |

The colour tokens live at the top of `assets/css/styles.css`. The illustration accent is `YELLOW` in `tools/generate_art.py`.

## Editing content

- **Owner settings (no build needed):** `assets/js/site-config.js`. This file holds the form endpoint, hero video, reviews and the reviews link.
- **Page text:** `src/pages/*.html`. **Shared header/footer/CTAs:** `src/partials/`.
  After editing anything in `src/`, run:

```bash
python3 tools/build.py      # writes index.html, tires/index.html, … sitemap.xml, robots.txt
```

Name, address, phone and hours are defined once in `BUSINESS` in `tools/build.py` and injected everywhere,
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
npm run serve        # http://localhost:8080
npm test             # in a second terminal
```

`tests/check-site.mjs` loads every page on desktop, iPad, iPhone and Android viewports and checks:

- every phone link dials (602) 242-0442 and every directions link goes to the full address
- all internal links and anchors resolve, with no console errors and no horizontal scrolling
- one `<h1>` per page, touch targets ≥ 44px, and the mobile action bar
- axe-core WCAG 2.1 A/AA
- mobile menu, symptom picker, alignment toggle, reduced-motion behaviour
- form validation, the honest "not sent" state with no endpoint, a success message on a 2xx response only, and an error on a 5xx response

Lighthouse (local, uncompressed server): Performance 95–100, Accessibility 100, Best Practices 100, SEO 100
on mobile and desktop. Production hosts that serve gzip/brotli will do slightly better.
