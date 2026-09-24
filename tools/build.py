#!/usr/bin/env python3
"""Build the static site from src/ into the repository root.

    python3 tools/build.py

- src/partials/*   shared markup (head, header, footer, CTA blocks, hero scene)
- src/pages/*.html page bodies. The first line is a <!--META {json} --> block.

Business details (name, address, phone, hours) live in BUSINESS below and are
injected everywhere so NAP stays identical on every page and in structured data.
Set SITE_URL to the production domain before launch, then rebuild.
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

# ---------------------------------------------------------------------------
# CONFIGURE BEFORE LAUNCH
SITE_URL = "https://www.example.com"  # production domain, no trailing slash
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
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
              "opens": "08:00", "closes": "18:00"},
    "same_as": [
        "https://www.yelp.com/biz/hugo-s-alignment-and-tire-shop-phoenix-5",
        "https://www.facebook.com/100090052066585/",
    ],
    "services": ["Tires", "Wheel Alignment", "Auto Repair", "Transmission Repair"],
}

FULL_ADDRESS = f"{BUSINESS['street']}, {BUSINESS['city']}, {BUSINESS['region']} {BUSINESS['zip']}"
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&destination=" + quote_plus(FULL_ADDRESS)
TEL = "tel:" + BUSINESS["phone_e164"]

META_RE = re.compile(r"^<!--META\s+(\{.*?\})\s*-->\s*", re.S)
INCLUDE_RE = re.compile(r"\{\{include:([\w.\-]+)\}\}")


def asset_version():
    h = hashlib.sha1()
    for p in sorted((ROOT / "assets" / "css").glob("*.css")) + sorted((ROOT / "assets" / "js").glob("*.js")):
        h.update(p.read_bytes())
    return h.hexdigest()[:8]


def expand_includes(text, depth=0):
    if depth > 5:
        raise RuntimeError("include nesting too deep")
    return INCLUDE_RE.sub(lambda m: expand_includes((PARTIALS / m.group(1)).read_text(), depth + 1), text)


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def business_schema():
    b = BUSINESS
    return {
        "@context": "https://schema.org",
        "@type": "AutoRepair",
        "@id": f"{SITE_URL}/#business",
        "name": b["name"],
        "url": f"{SITE_URL}/",
        "telephone": b["phone_e164"],
        "image": f"{SITE_URL}/assets/img/og-image.png",
        "logo": f"{SITE_URL}/assets/img/apple-touch-icon.png",
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
    if "business" in kinds:
        blocks.append(business_schema())
    if "website" in kinds:
        blocks.append({"@context": "https://schema.org", "@type": "WebSite", "name": BUSINESS["name"],
                       "url": f"{SITE_URL}/"})
    if "service" in kinds:
        blocks.append({
            "@context": "https://schema.org", "@type": "Service",
            "name": f"{meta['service_name']} in Phoenix, AZ",
            "serviceType": meta["service_name"],
            "provider": {"@id": f"{SITE_URL}/#business"},
            "areaServed": {"@type": "City", "name": "Phoenix"},
            "url": url,
        })
    if "breadcrumb" in kinds:
        blocks.append({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": meta["breadcrumb"], "item": url},
            ],
        })
    return "\n".join(ld(b) for b in blocks)


def out_path(path):
    if path.endswith(".html"):
        return ROOT / path.lstrip("/")
    return ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"


def root_prefix(meta):
    if meta.get("absolute_root"):
        return "/"
    depth = len([p for p in meta["path"].split("/") if p and not p.endswith(".html")])
    return "../" * depth if depth else "./"


def render(page_file, version):
    raw = page_file.read_text()
    m = META_RE.match(raw)
    if not m:
        raise SystemExit(f"{page_file}: missing META block")
    meta = json.loads(m.group(1))
    body = raw[m.end():]

    html = "\n".join([
        (PARTIALS / "head.html").read_text(),
        '<body>',
        (PARTIALS / "header.html").read_text(),
        '<main id="main" tabindex="-1">',
        body,
        "</main>",
        (PARTIALS / "footer.html").read_text(),
        "</body>\n</html>\n",
    ])
    html = expand_includes(html)

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
    for m in sorted(metas, key=lambda m: -float(m.get("priority", 0.5))):
        if m.get("noindex"):
            continue
        urls.append(
            f"  <url><loc>{SITE_URL}{m['path']}</loc><lastmod>{today}</lastmod>"
            f"<changefreq>{m.get('changefreq', 'monthly')}</changefreq><priority>{m.get('priority', '0.5')}</priority></url>"
        )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")


def main():
    version = asset_version()
    metas = [render(p, version) for p in sorted(PAGES.glob("*.html"))]
    write_sitemap(metas)
    print(f"built {len(metas)} pages (assets v{version})")


if __name__ == "__main__":
    main()
