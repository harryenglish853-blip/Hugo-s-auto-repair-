#!/usr/bin/env python3
"""Build the static site from src/ into dist/ (the folder that gets published).

    python3 tools/build.py

- src/partials/*   shared markup (head, header, footer, CTA blocks, hero scene)
- src/pages/*.html page bodies. The first line is a <!--META {json} --> block.

Business details (name, address, phone, hours) live in BUSINESS below and are
injected everywhere so NAP stays identical on every page and in structured data.
To change the address, hours, or domain, edit the CONFIGURE block below and rebuild.
"""
import hashlib
import json
import os
import shutil
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

# ---------------------------------------------------------------------------
# CONFIGURE
# Custom domain, e.g. "www.hugosautophx.com". Leave "" to use the GitHub Pages address.
# When set, the build also writes the CNAME file GitHub Pages needs.
CUSTOM_DOMAIN = ""
GITHUB_PAGES_URL = "https://harryenglish853-blip.github.io/Hugo-s-auto-repair-"
SITE_URL = os.environ.get("SITE_URL") or (f"https://{CUSTOM_DOMAIN}" if CUSTOM_DOMAIN else GITHUB_PAGES_URL)

# Opening hours (24-hour clock). Used in page text, the open/closed badge and Google's structured data.
OPENS, CLOSES = "08:00", "18:00"
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SRC = ROOT / "src"
PARTIALS = SRC / "partials"
PAGES = SRC / "pages"

BUSINESS = {
    "name": "Hugo's Alignment, Tires & Auto Repair",
    "street": "6040 N Black Canyon Hwy",
    "city": "Phoenix",
    "region": "AZ",
    "zip": "85017",
    "phone_display": "(602) 242-0442",
    "phone_e164": "+16022420442",
    "hours": {"days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
              "opens": OPENS, "closes": CLOSES},
    "same_as": [
        "https://www.yelp.com/biz/hugo-s-alignment-and-tire-shop-phoenix-5",
        "https://www.facebook.com/100090052066585/",
        "https://www.instagram.com/hugosalignment_/",
    ],
    "services": ["Tires", "Wheel Alignment", "Auto Repair", "Transmission Repair", "Custom Wheels & Tires",
                 "Lift, Leveling & Drop Kits", "Suspension", "Brakes & Rotors", "Oil Changes & Maintenance",
                 "Engine Repair & Diagnostics", "Electrical Repair", "A/C Repair", "Steering", "Welding & Fabrication"],
}

def clock(hhmm, short=False):
    """'18:00' -> '6:00 PM' (or '6PM' when short)."""
    h, m = map(int, hhmm.split(":"))
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    if short:
        return f"{h12}{'' if m == 0 else f':{m:02d}'}{suffix}"
    return f"{h12}:{m:02d} {suffix}"


FULL_ADDRESS = f"{BUSINESS['street']}, {BUSINESS['city']}, {BUSINESS['region']} {BUSINESS['zip']}"
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&destination=" + quote_plus(FULL_ADDRESS)
TEL = "tel:" + BUSINESS["phone_e164"]

# Shop photos in assets/img/shop/<name>-{480,800,1180}.{jpg,webp}: intrinsic size of the largest file
PHOTOS = {
    "control-arms-accord": (1191, 890),
    "level-kit-silverado": (1191, 1538),
    "level-kit-tires-silverado": (1191, 890),
    "alignment-4runner": (1177, 890),
    "engine-jeep": (1191, 1586),
}
# {{photo:name|alt text|sizes}} or {{photo:name|alt text|sizes|eager}}
PHOTO_RE = re.compile(r"\{\{photo:([\w-]+)\|([^|}]*)\|([^|}]*)(?:\|(eager))?\}\}")


def photo(m):
    name, alt, sizes, eager = m.groups()
    w, h = PHOTOS[name]
    ss = lambda ext: ", ".join(f"{{{{ROOT}}}}assets/img/shop/{name}-{x}.{ext} {x}w" for x in (480, 800, 1180))
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/webp" srcset="{ss("webp")}" sizes="{sizes}">'
            f'<img src="{{{{ROOT}}}}assets/img/shop/{name}-800.jpg" srcset="{ss("jpg")}" sizes="{sizes}" '
            f'alt="{alt}" width="{w}" height="{h}" {load} decoding="async"></picture>')


META_RE = re.compile(r"^<!--META\s+(\{.*?\})\s*-->\s*", re.S)
INCLUDE_RE = re.compile(r"\{\{include:([\w.\-]+)\}\}")


def asset_version():
    h = hashlib.sha1()
    for p in sorted((ROOT / "assets" / "css").glob("*.css")) + sorted((ROOT / "assets" / "js").glob("*.js")):
        h.update(p.read_bytes())
    return h.hexdigest()[:8]


def partial(name, lang):
    """Language-specific partial (src/partials/<lang>/name) if present, else the shared one."""
    localized = PARTIALS / lang / name
    return (localized if localized.exists() else PARTIALS / name).read_text()


def expand_includes(text, lang, depth=0):
    if depth > 5:
        raise RuntimeError("include nesting too deep")
    return INCLUDE_RE.sub(lambda m: expand_includes(partial(m.group(1), lang), lang, depth + 1), text)


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


DESCRIPTION = {
    "en": ("In business 10+ years. Our goal is to provide quality service for our clients' vehicles so everyone stays safe. "
           "We specialize in automotive services and give every client professional, customized service."),
    "es": ("Más de 10 años en el negocio. Nuestra meta es brindar servicios de calidad para los vehículos de nuestros clientes "
           "para que todos estén seguros. Nos especializamos en servicios automotrices y damos un servicio profesional y "
           "personalizado a cada cliente."),
}


def business_schema(lang="en"):
    b = BUSINESS
    return {
        "@context": "https://schema.org",
        "@type": "AutoRepair",
        "@id": f"{SITE_URL}/#business",
        "name": b["name"],
        "description": DESCRIPTION[lang],
        "url": f"{SITE_URL}/",
        "telephone": b["phone_e164"],
        "image": f"{SITE_URL}/assets/img/og-image.png",
        "logo": f"{SITE_URL}/assets/img/logo-full.png",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": b["street"],
            "addressLocality": b["city"],
            "addressRegion": b["region"],
            "postalCode": b["zip"],
            "addressCountry": "US",
        },
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": b["hours"]["days"],
            "opens": b["hours"]["opens"],
            "closes": b["hours"]["closes"],
        }],
        "areaServed": {"@type": "City", "name": "Phoenix", "containedInPlace": {"@type": "State", "name": "Arizona"}},
        "hasMap": "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f"{b['name']} {FULL_ADDRESS}"),
        "sameAs": b["same_as"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Automotive services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}} for s in b["services"]
            ],
        },
    }


def page_schema(meta):
    blocks = []
    kinds = meta.get("schema", [])
    url = SITE_URL + meta["path"]
    es = meta.get("lang") == "es"
    if "business" in kinds:
        blocks.append(business_schema(meta.get("lang", "en")))
    if "website" in kinds:
        blocks.append({"@context": "https://schema.org", "@type": "WebSite", "name": BUSINESS["name"],
                       "url": f"{SITE_URL}/"})
    if "service" in kinds:
        blocks.append({
            "@context": "https://schema.org", "@type": "Service",
            "name": f"{meta['service_name']} {'en' if es else 'in'} Phoenix, AZ",
            "serviceType": meta["service_name"],
            "provider": {"@id": f"{SITE_URL}/#business"},
            "areaServed": {"@type": "City", "name": "Phoenix"},
            "url": url,
            "inLanguage": meta.get("lang", "en"),
        })
    if "breadcrumb" in kinds:
        blocks.append({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Inicio" if es else "Home",
                 "item": f"{SITE_URL}/es/" if es else f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": meta["breadcrumb"], "item": url},
            ],
        })
    return "\n".join(ld(b) for b in blocks)


def out_path(path):
    if path.endswith(".html"):
        return DIST / path.lstrip("/")
    return DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html"


def root_prefix(meta):
    if meta.get("absolute_root"):
        # e.g. the 404 page, which can be served from any URL depth
        return SITE_URL + "/"
    depth = len([p for p in meta["path"].split("/") if p and not p.endswith(".html")])
    return "../" * depth if depth else "./"


def read_page(page_file, lang):
    raw = page_file.read_text()
    m = META_RE.match(raw)
    if not m:
        raise SystemExit(f"{page_file}: missing META block")
    meta = json.loads(m.group(1))
    meta.setdefault("lang", lang)
    return meta, raw[m.end():]


def rel(from_path, to_path, meta):
    """Relative link from one page URL to another (keeps the site working under a sub-path)."""
    return root_prefix(meta) + to_path.lstrip("/")


def hreflang_links(meta):
    alt = meta.get("alt")
    if not alt or meta.get("noindex"):
        return ""
    en, es = (meta["path"], alt) if meta["lang"] == "en" else (alt, meta["path"])
    return "\n".join([
        f'<link rel="alternate" hreflang="en" href="{SITE_URL}{en}">',
        f'<link rel="alternate" hreflang="es" href="{SITE_URL}{es}">',
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{en}">',
    ])


def render(page_file, meta, body, version):
    lang = meta["lang"]
    html = "\n".join([
        partial("head.html", lang),
        '<body>',
        partial("header.html", lang),
        '<main id="main" tabindex="-1">',
        body,
        "</main>",
        partial("footer.html", lang),
        "</body>\n</html>\n",
    ])
    html = expand_includes(html, lang)
    html = PHOTO_RE.sub(photo, html)

    nav = meta.get("nav", "")
    for key in ("services", "tires", "alignment", "repair", "transmission"):
        cur = ' aria-current="page"' if key == nav else ""
        html = html.replace("{{NAV_%s}}" % key, cur).replace("{{REL_%s}}" % key, cur)

    replacements = {
        "{{TITLE}}": escape_attr(meta["title"]),
        "{{DESCRIPTION}}": escape_attr(meta["description"]),
        "{{CANONICAL}}": SITE_URL + meta["path"],
        "{{ROBOTS}}": "noindex, follow" if meta.get("noindex") else "index, follow, max-image-preview:large",
        "{{SITE_URL}}": SITE_URL,
        "{{SCHEMA}}": page_schema(meta),
        "{{ROOT}}": root_prefix(meta),
        "{{VERSION}}": version,
        "{{PHONE}}": BUSINESS["phone_display"],
        "{{TEL}}": TEL,
        "{{DIRECTIONS}}": DIRECTIONS.replace("&", "&amp;"),
        "{{LANG}}": lang,
        "{{OG_LOCALE}}": "es_US" if lang == "es" else "en_US",
        "{{HREFLANG}}": hreflang_links(meta),
        "{{OPEN}}": clock(OPENS),
        "{{CLOSE}}": clock(CLOSES),
        "{{OPEN_S}}": clock(OPENS, short=True),
        "{{CLOSE_S}}": clock(CLOSES, short=True),
        "{{OPEN_24}}": OPENS,
        "{{CLOSE_24}}": CLOSES,
        "{{ALT_HREF}}": rel(meta["path"], meta.get("alt") or ("/" if lang == "es" else "/es/"), meta),
    }
    for k, v in replacements.items():
        html = html.replace(k, v)
    leftover = re.findall(r"\{\{[^}]+\}\}", html)
    if leftover:
        raise SystemExit(f"{page_file}: unreplaced tokens {sorted(set(leftover))}")

    dest = out_path(meta["path"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    return meta


def escape_attr(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


def write_sitemap(metas):
    today = date.today().isoformat()
    urls = []
    for m in sorted(metas, key=lambda m: (m["lang"] != "en", -float(m.get("priority", 0.5)))):
        if m.get("noindex"):
            continue
        alts = ""
        if m.get("alt"):
            en, es = (m["path"], m["alt"]) if m["lang"] == "en" else (m["alt"], m["path"])
            alts = (f'<xhtml:link rel="alternate" hreflang="en" href="{SITE_URL}{en}"/>'
                    f'<xhtml:link rel="alternate" hreflang="es" href="{SITE_URL}{es}"/>')
        urls.append(
            f"  <url><loc>{SITE_URL}{m['path']}</loc>{alts}<lastmod>{today}</lastmod>"
            f"<changefreq>{m.get('changefreq', 'monthly')}</changefreq><priority>{m.get('priority', '0.5')}</priority></url>"
        )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n"
    )
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


def prepare_dist():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copy2(ROOT / "site.webmanifest", DIST / "site.webmanifest")
    (DIST / ".nojekyll").write_text("")  # serve files as-is on GitHub Pages
    if CUSTOM_DOMAIN:
        (DIST / "CNAME").write_text(CUSTOM_DOMAIN + "\n")


def main():
    prepare_dist()
    version = asset_version()
    pages = [(p, *read_page(p, "en")) for p in sorted(PAGES.glob("*.html"))]
    pages += [(p, *read_page(p, "es")) for p in sorted((PAGES / "es").glob("*.html"))]
    paths = {m["path"] for _, m, _ in pages}
    for p, m, _ in pages:
        if m.get("alt") and m["alt"] not in paths:
            raise SystemExit(f"{p}: alt page {m['alt']} does not exist")
    metas = [render(p, m, body, version) for p, m, body in pages]
    write_sitemap(metas)
    print(f"built {len(metas)} pages into dist/ for {SITE_URL} (assets v{version})")


if __name__ == "__main__":
    main()
