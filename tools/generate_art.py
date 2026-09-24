#!/usr/bin/env python3
"""Generate the site's technical line-art SVGs.

These illustrations stand in until the shop's own photography and video are
added. They are deliberately drawn as clean technical art (no logos, no text on
equipment, mechanically plausible geometry) rather than fake "photos".

Usage:  python3 tools/generate_art.py
Writes: assets/img/*.svg and src/partials/hero-scene.svg
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
PARTIALS = ROOT / "src" / "partials"

STEEL = "#8e969f"
STEEL_LT = "#c9ced4"
AMBER = "#f0a431"
INK = "#0d0e10"


def f(n):
    return f"{n:.2f}".rstrip("0").rstrip(".")


def polar(r, deg, cx=0.0, cy=0.0):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def gear_path(teeth, r_pitch, depth, cx=0.0, cy=0.0, internal=False, phase=0.0):
    """Trapezoid-tooth gear outline. internal=True points teeth inward (ring gear)."""
    step = 360.0 / teeth
    r_out = r_pitch - depth if internal else r_pitch + depth
    r_in = r_pitch + depth if internal else r_pitch - depth
    pts = []
    for i in range(teeth):
        c = phase + i * step
        # root -> flank -> tip -> flank
        pts.append(polar(r_in, c - step * 0.5, cx, cy))
        pts.append(polar(r_in, c - step * 0.28, cx, cy))
        pts.append(polar(r_out, c - step * 0.14, cx, cy))
        pts.append(polar(r_out, c + step * 0.14, cx, cy))
        pts.append(polar(r_in, c + step * 0.28, cx, cy))
    d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + " Z"
    return d


def svg(view, body, label, extra_style=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" role="img" '
        f'aria-label="{label}">\n'
        f"<style>{extra_style}</style>\n{body}\n</svg>\n"
    )


REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


# ---------------------------------------------------------------- wheel parts
def wheel_group(r_tire=262, r_rim=172, spokes=5, lugs=5, tread_blocks=64, cid="w"):
    """Side view of a tyre + 5-spoke wheel. Returns (rotating_svg, static_svg)."""
    rot = []
    # tyre body
    rot.append(f'<circle r="{r_tire}" fill="#121315"/>')
    # tread blocks on the circumference
    step = 360 / tread_blocks
    for i in range(tread_blocks):
        a = i * step
        x1, y1 = polar(r_tire - 14, a - step * 0.3)
        x2, y2 = polar(r_tire + 2, a - step * 0.26)
        x3, y3 = polar(r_tire + 2, a + step * 0.26)
        x4, y4 = polar(r_tire - 14, a + step * 0.3)
        rot.append(
            f'<path d="M{f(x1)} {f(y1)} L{f(x2)} {f(y2)} L{f(x3)} {f(y3)} L{f(x4)} {f(y4)} Z" fill="#1b1d20"/>'
        )
    # sidewall
    rot.append(
        f'<circle r="{r_tire - 22}" fill="url(#{cid}-side)"/>'
        f'<circle r="{r_tire - 22}" fill="none" stroke="#26292d" stroke-width="2"/>'
        f'<circle r="{(r_tire + r_rim) / 2 - 6}" fill="none" stroke="#1f2124" stroke-width="1.5"/>'
    )
    # rim lip + barrel
    rot.append(
        f'<circle r="{r_rim}" fill="#0a0b0c"/>'
        f'<circle r="{r_rim}" fill="none" stroke="url(#{cid}-lip)" stroke-width="9"/>'
        f'<circle r="{r_rim - 12}" fill="none" stroke="#2c3035" stroke-width="2"/>'
    )
    # brake rotor visible through the spokes
    rot.append(
        f'<circle r="{r_rim * 0.78}" fill="#3a3d41"/>'
        f'<circle r="{r_rim * 0.78}" fill="none" stroke="#4a4e53" stroke-width="3"/>'
        f'<circle r="{r_rim * 0.46}" fill="#2a2d31"/>'
    )
    # tapered spokes
    for i in range(spokes):
        a = i * 360 / spokes - 90
        xa, ya = polar(40, a - 13)
        xb, yb = polar(r_rim - 12, a - 5)
        xc, yc = polar(r_rim - 12, a + 5)
        xd, yd = polar(40, a + 13)
        rot.append(
            f'<path d="M{f(xa)} {f(ya)} L{f(xb)} {f(yb)} L{f(xc)} {f(yc)} L{f(xd)} {f(yd)} Z" '
            f'fill="url(#{cid}-spoke)" stroke="#6d747c" stroke-width="1"/>'
        )
    # hub, lug nuts, centre cap (plain - no logo)
    rot.append(f'<circle r="58" fill="url(#{cid}-hub)" stroke="#6d747c" stroke-width="1.5"/>')
    for i in range(lugs):
        x, y = polar(40, i * 360 / lugs - 90)
        rot.append(
            f'<circle cx="{f(x)}" cy="{f(y)}" r="7.5" fill="#1c1e21" stroke="{STEEL_LT}" stroke-width="2"/>'
        )
    rot.append(f'<circle r="20" fill="#24272b" stroke="#5b6168" stroke-width="1.5"/>')
    defs = (
        f'<radialGradient id="{cid}-side" r="0.5"><stop offset="0.62" stop-color="#16171a"/>'
        f'<stop offset="0.9" stop-color="#1e2023"/><stop offset="1" stop-color="#141517"/></radialGradient>'
        f'<linearGradient id="{cid}-lip" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dfe3e7"/>'
        f'<stop offset="0.5" stop-color="#6b7178"/><stop offset="1" stop-color="#b9bfc5"/></linearGradient>'
        f'<linearGradient id="{cid}-spoke" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#c5cad0"/>'
        f'<stop offset="1" stop-color="#5d636a"/></linearGradient>'
        f'<radialGradient id="{cid}-hub"><stop offset="0" stop-color="#7f868e"/>'
        f'<stop offset="1" stop-color="#3b3f44"/></radialGradient>'
    )
    return defs, "\n".join(rot)


def caliper(r_rim=172, angle=-150):
    """Brake caliper - fixed to the knuckle, so it never rotates with the wheel."""
    a0, a1 = angle - 22, angle + 22
    ro, ri = r_rim * 0.8, r_rim * 0.56
    p = [polar(ro, a0), polar(ro, a1), polar(ri, a1 - 3), polar(ri, a0 + 3)]
    d = (
        f"M{f(p[0][0])} {f(p[0][1])} A{f(ro)} {f(ro)} 0 0 1 {f(p[1][0])} {f(p[1][1])} "
        f"L{f(p[2][0])} {f(p[2][1])} A{f(ri)} {f(ri)} 0 0 0 {f(p[3][0])} {f(p[3][1])} Z"
    )
    return f'<path d="{d}" fill="#2b2e32" stroke="#777e86" stroke-width="2"/>'


# ---------------------------------------------------------------- hero scene
def hero_scene():
    W, H = 1600, 900
    cx, cy, rt = 1180, 610, 262
    defs, wheel = wheel_group(cid="hw")
    # alignment-rack runway in perspective (vanishing point far left)
    body = f"""
<defs>
  {defs}
  <linearGradient id="hs-bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#16181b"/><stop offset="0.62" stop-color="#0f1012"/><stop offset="1" stop-color="#08090a"/>
  </linearGradient>
  <linearGradient id="hs-floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1a1c1f"/><stop offset="1" stop-color="#0b0c0d"/>
  </linearGradient>
  <linearGradient id="hs-light" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f4efe6" stop-opacity=".9"/><stop offset="1" stop-color="#f4efe6" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="hs-pool" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#f4efe6" stop-opacity=".10"/><stop offset="1" stop-color="#f4efe6" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="hs-laser" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{AMBER}" stop-opacity="0"/><stop offset=".5" stop-color="{AMBER}" stop-opacity=".9"/>
    <stop offset="1" stop-color="{AMBER}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="hs-shade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{INK}" stop-opacity=".96"/><stop offset=".48" stop-color="{INK}" stop-opacity=".7"/>
    <stop offset="1" stop-color="{INK}" stop-opacity="0"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#hs-bg)"/>
<!-- rear wall: roll-up bay door slats -->
<g opacity=".55">
  <rect x="520" y="120" width="560" height="470" fill="#131518" stroke="#23262a" stroke-width="3"/>
  {''.join(f'<line x1="522" y1="{140 + i * 22}" x2="1078" y2="{140 + i * 22}" stroke="#1d2024" stroke-width="2"/>' for i in range(20))}
</g>
<!-- overhead shop lights -->
<g class="hs-lights">
  <rect x="340" y="40" width="300" height="10" rx="3" fill="#e9e4da"/>
  <rect x="960" y="40" width="300" height="10" rx="3" fill="#e9e4da"/>
  <path d="M340 50 L640 50 L760 420 L220 420 Z" fill="url(#hs-light)" opacity=".07"/>
  <path d="M960 50 L1260 50 L1380 420 L840 420 Z" fill="url(#hs-light)" opacity=".07"/>
</g>
<!-- floor -->
<rect y="585" width="{W}" height="{H - 585}" fill="url(#hs-floor)"/>
<line x1="0" y1="585" x2="{W}" y2="585" stroke="#2a2d31" stroke-width="2"/>
<ellipse cx="1000" cy="700" rx="700" ry="120" fill="url(#hs-pool)"/>
<!-- alignment rack runway + turn plate -->
<path d="M180 640 L1600 800 L1600 836 L180 652 Z" fill="#202327" stroke="#33373c" stroke-width="1.5"/>
<path d="M180 652 L1600 836 L1600 852 L180 658 Z" fill="#141619"/>
<ellipse cx="{cx}" cy="{cy + rt - 6}" rx="210" ry="22" fill="#2a2e33" stroke="#4a4f55" stroke-width="2"/>
<ellipse cx="{cx}" cy="{cy + rt - 6}" rx="150" ry="14" fill="none" stroke="#3a3e43" stroke-width="1.5"/>
<!-- measurement laser sweeping the floor -->
<rect class="hs-laser" x="200" y="{cy + rt - 8}" width="520" height="2" fill="url(#hs-laser)"/>
<!-- wheel reflection -->
<g transform="translate({cx} {cy + 2 * rt - 4}) scale(1 -0.18)" opacity=".18">
  <circle r="{rt}" fill="#2a2d31"/>
</g>
<!-- the wheel: rolls in, stops -->
<g class="hs-wheel-move">
  <g transform="translate({cx} {cy})">
    <g class="hs-wheel-spin">{wheel}</g>
    {caliper()}
    <!-- wheel clamp + alignment sensor head: attached after the wheel stops -->
    <g class="hs-clamp">
      {''.join(f'<line x1="0" y1="0" x2="{f(polar(166, a)[0])}" y2="{f(polar(166, a)[1])}" stroke="{STEEL_LT}" stroke-width="7" stroke-linecap="round"/><circle cx="{f(polar(166, a)[0])}" cy="{f(polar(166, a)[1])}" r="8" fill="#2b2e32" stroke="{STEEL_LT}" stroke-width="3"/>' for a in (-90, 30, 150))}
      <circle r="24" fill="#2b2e32" stroke="{STEEL_LT}" stroke-width="4"/>
      <rect x="24" y="-16" width="276" height="16" rx="3" fill="#3b3f44" stroke="#8e969f" stroke-width="1.5"/>
      <rect x="268" y="-54" width="92" height="74" rx="8" fill="#1f2226" stroke="{STEEL_LT}" stroke-width="3"/>
      <circle class="hs-sensor-led" cx="340" cy="-34" r="5" fill="{AMBER}"/>
      <rect x="290" y="-10" width="48" height="16" rx="3" fill="#0b0c0d" stroke="#555b62"/>
    </g>
  </g>
</g>
<!-- legibility shade behind headline -->
<rect width="{W}" height="{H}" fill="url(#hs-shade)"/>
"""
    style = f"""
.hs-wheel-move{{animation:hs-roll 2.8s cubic-bezier(.16,.84,.3,1) both}}
.hs-wheel-spin{{animation:hs-spin 2.8s cubic-bezier(.16,.84,.3,1) both}}
.hs-clamp{{opacity:0;animation:hs-clamp .7s ease-out 2.9s forwards}}
.hs-laser{{opacity:0;animation:hs-sweep 5s ease-in-out 3.6s infinite}}
.hs-sensor-led{{animation:hs-led 2.4s ease-in-out 3.6s infinite}}
@keyframes hs-roll{{from{{transform:translateX(620px)}}to{{transform:none}}}}
@keyframes hs-spin{{from{{transform:rotate(360deg)}}to{{transform:rotate(0)}}}}
@keyframes hs-clamp{{from{{opacity:0;transform:translateX(18px)}}to{{opacity:1;transform:none}}}}
@keyframes hs-sweep{{0%{{opacity:0;transform:translateX(0)}}15%{{opacity:1}}70%{{opacity:1}}100%{{opacity:0;transform:translateX(620px)}}}}
@keyframes hs-led{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}
@media (prefers-reduced-motion: reduce){{.hs-wheel-move,.hs-wheel-spin{{animation:none}}.hs-clamp{{animation:none;opacity:1}}.hs-laser{{animation:none;opacity:.7}}.hs-sensor-led{{animation:none}}}}
"""
    return (
        f'<svg class="hero__scene" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" '
        f'aria-hidden="true" focusable="false">\n<style>{style}</style>{body}</svg>\n'
    )


# ---------------------------------------------------------------- service art
def tire_tread():
    """Macro, top-down view of a tyre's contact patch: four ribs, shoulder blocks, sipes."""
    W, H = 800, 520
    parts = [f'<rect width="{W}" height="{H}" fill="#101113"/>']
    parts.append(
        '<defs><linearGradient id="tt-l" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#000" stop-opacity=".75"/><stop offset=".25" stop-color="#000" stop-opacity="0"/>'
        '<stop offset=".75" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></linearGradient>'
        '<linearGradient id="tt-b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2d31"/>'
        '<stop offset="1" stop-color="#1b1d20"/></linearGradient></defs>'
    )
    parts.append('<g class="tt-roll">')
    ribs = [(110, 210), (230, 390), (410, 570), (590, 690)]  # x ranges; grooves between
    pitch = 64
    for row in range(-2, H // pitch + 3):
        y = row * pitch
        # shoulders: angled blocks
        for x0, x1, s in ((20, 100, 1), (700, 780, -1)):
            parts.append(
                f'<path d="M{x0} {y + 6} L{x1} {y + 6 + 10 * s} L{x1} {y + pitch - 8 + 10 * s} L{x0} {y + pitch - 8} Z" fill="url(#tt-b)" stroke="#34383d"/>'
            )
        for x0, x1 in ribs:
            parts.append(
                f'<path d="M{x0} {y + 4} L{x1} {y + 18} L{x1} {y + pitch - 2} L{x0} {y + pitch - 16} Z" fill="url(#tt-b)" stroke="#34383d"/>'
            )
            # sipes
            for k in (0.33, 0.66):
                sx = x0 + (x1 - x0) * k
                parts.append(
                    f'<path d="M{f(sx)} {y + 12} l6 10 l-6 10 l6 10 l-6 10" fill="none" stroke="#0e0f11" stroke-width="2.5"/>'
                )
    parts.append("</g>")
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#tt-l)"/>')
    style = (
        f".tt-roll{{animation:tt 9s linear infinite}}@keyframes tt{{to{{transform:translateY({pitch * 2}px)}}}}"
        + REDUCED
    )
    return svg(f"0 0 {W} {H}", "\n".join(parts), "Close-up illustration of tire tread", style)


def alignment_card():
    """Top-down front axle on turn plates with thrust/centre lines."""
    W, H = 800, 520
    cx = 400
    parts = [
        f'<rect width="{W}" height="{H}" fill="#101113"/>',
        # grid
        "".join(
            f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#16181b"/>' for x in range(0, W, 40)
        ),
        "".join(
            f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#16181b"/>' for y in range(0, H, 40)
        ),
        # body outline (front half of a car, top view)
        f'<path d="M250 500 L250 170 Q250 70 400 60 Q550 70 550 170 L550 500" fill="#17191c" stroke="#3c4146" stroke-width="3"/>',
        f'<path d="M285 330 Q400 300 515 330 L505 420 Q400 400 295 420 Z" fill="#0d0e10" stroke="#3c4146" stroke-width="2"/>',
        # axle
        f'<line x1="232" y1="230" x2="568" y2="230" stroke="{STEEL}" stroke-width="6"/>',
        f'<line x1="{cx}" y1="20" x2="{cx}" y2="500" stroke="#565c63" stroke-width="2" stroke-dasharray="10 8"/>',
    ]
    for side, x in (("l", 205), ("r", 595)):
        parts.append(
            f'<circle cx="{x}" cy="230" r="82" fill="none" stroke="#2c3035" stroke-width="3"/>'
            f'<g class="ac-wheel ac-{side}"><rect x="{x - 26}" y="160" width="52" height="140" rx="12" fill="#1c1e21" stroke="{STEEL_LT}" stroke-width="3"/>'
            f'<line x1="{x}" y1="40" x2="{x}" y2="420" stroke="{AMBER}" stroke-width="2.5" class="ac-beam"/></g>'
        )
    style = (
        ".ac-wheel{transform-box:fill-box;transform-origin:center}"
        ".ac-beam{stroke-dasharray:380;stroke-dashoffset:380;animation:ac-draw 4s ease-in-out infinite}"
        "@keyframes ac-draw{0%{stroke-dashoffset:380}40%,80%{stroke-dashoffset:0}100%{stroke-dashoffset:-380}}"
        + REDUCED
        + "@media (prefers-reduced-motion: reduce){.ac-beam{stroke-dashoffset:0}}"
    )
    return svg(f"0 0 {W} {H}", "\n".join(parts), "Illustration of a front axle with wheel alignment reference lines", style)


def repair_card():
    """Brake assembly (rotor + caliper) with a click-type torque wrench."""
    W, H = 800, 520
    rx, ry = 320, 270
    parts = [f'<rect width="{W}" height="{H}" fill="#101113"/>']
    # rotor: friction ring, vent ring, hat, lug holes
    parts.append(
        f'<circle cx="{rx}" cy="{ry}" r="190" fill="#34373b" stroke="#6b7178" stroke-width="3"/>'
        f'<circle cx="{rx}" cy="{ry}" r="182" fill="none" stroke="#2a2d31" stroke-width="2"/>'
        f'<circle cx="{rx}" cy="{ry}" r="104" fill="#26292d" stroke="#6b7178" stroke-width="3"/>'
        f'<circle cx="{rx}" cy="{ry}" r="36" fill="#101113" stroke="#6b7178" stroke-width="2"/>'
    )
    for i in range(5):
        x, y = polar(66, i * 72 - 90, rx, ry)
        parts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="9" fill="#101113" stroke="#8e969f" stroke-width="2"/>')
    # machining marks on the friction face
    for r in range(116, 180, 9):
        parts.append(f'<circle cx="{rx}" cy="{ry}" r="{r}" fill="none" stroke="#3d4145" stroke-width="1"/>')
    # caliper at 3 o'clock
    parts.append(
        f'<path d="M{rx + 150} {ry - 110} Q{rx + 240} {ry} {rx + 150} {ry + 110} L{rx + 120} {ry + 96} Q{rx + 196} {ry} {rx + 120} {ry - 96} Z" fill="#2b2e32" stroke="{STEEL_LT}" stroke-width="3"/>'
        f'<circle cx="{rx + 196}" cy="{ry - 52}" r="8" fill="#101113" stroke="{STEEL}" stroke-width="2"/>'
        f'<circle cx="{rx + 196}" cy="{ry + 52}" r="8" fill="#101113" stroke="{STEEL}" stroke-width="2"/>'
    )
    # torque wrench across the frame, socket on a lug
    lx, ly = rx + 196, ry - 52
    parts.append(
        '<g class="rc-wrench">'
        f'<rect x="{f(lx - 14)}" y="{f(ly - 14)}" width="28" height="28" rx="4" fill="#4b5056" stroke="{STEEL_LT}" stroke-width="2"/>'
        f'<circle cx="{f(lx)}" cy="{f(ly)}" r="22" fill="#5a6067" stroke="{STEEL_LT}" stroke-width="2"/>'
        f'<rect x="{f(lx)}" y="{f(ly - 11)}" width="250" height="22" rx="11" fill="#8a9199" stroke="{STEEL_LT}" stroke-width="2"/>'
        f'<rect x="{f(lx + 170)}" y="{f(ly - 15)}" width="100" height="30" rx="15" fill="#1c1e21" stroke="#5d636a" stroke-width="2"/>'
        f'<line x1="{f(lx + 120)}" y1="{f(ly - 11)}" x2="{f(lx + 120)}" y2="{f(ly + 11)}" stroke="{AMBER}" stroke-width="3"/>'
        "</g>"
    )
    style = (
        f".rc-wrench{{transform-origin:{f(lx)}px {f(ly)}px;animation:rc 5s ease-in-out infinite}}"
        "@keyframes rc{0%,100%{transform:rotate(0)}45%,60%{transform:rotate(-9deg)}}" + REDUCED
    )
    return svg(f"0 0 {W} {H}", "\n".join(parts), "Illustration of a brake rotor, caliper and torque wrench", style)


def transmission_card():
    """Planetary gear set with a fixed ring gear. Tooth counts and speeds are consistent:
    ring 60T, sun 24T, planets 18T. Sun 24s/rev -> carrier 84s/rev,
    planets 25.2s/rev (reverse) relative to the carrier."""
    W, H = 800, 520
    m = 5.6
    zs, zp, zr = 24, 18, 60
    rs, rp, rr = m * zs / 2, m * zp / 2, m * zr / 2
    dep = m * 0.95
    cx, cy = W / 2, H / 2
    parts = [f'<rect width="{W}" height="{H}" fill="#101113"/>']
    parts.append(f'<g transform="translate({f(cx)} {f(cy)})">')
    # ring gear housing
    parts.append(f'<circle r="{f(rr + 34)}" fill="#1a1c1f" stroke="#4a4f55" stroke-width="3"/>')
    parts.append(f'<path d="{gear_path(zr, rr, dep, internal=True)}" fill="#101113" stroke="{STEEL}" stroke-width="2"/>')
    # carrier with planets
    parts.append('<g class="tc-carrier">')
    parts.append(f'<circle r="{f(rr + 40)}" fill="none" stroke="none"/>')  # symmetric bbox
    orbit = rs + rp
    parts.append(
        '<path d="' + " ".join(
            f"M0 0 L{f(polar(orbit, a)[0])} {f(polar(orbit, a)[1])}" for a in (0, 120, 240)
        ) + f'" stroke="#3b3f44" stroke-width="16" stroke-linecap="round"/>'
    )
    for a in (0, 120, 240):
        px, py = polar(orbit, a)
        parts.append(
            f'<g transform="translate({f(px)} {f(py)})"><g class="tc-planet">'
            f'<path d="{gear_path(zp, rp, dep, phase=10)}" fill="#2b2e32" stroke="{STEEL_LT}" stroke-width="2"/>'
            f'<circle r="9" fill="#101113" stroke="{STEEL}" stroke-width="2"/>'
            f'<line x1="0" y1="-{f(rp * 0.6)}" x2="0" y2="-{f(rp * 0.3)}" stroke="#5d636a" stroke-width="3"/>'
            "</g></g>"
        )
    parts.append("</g>")
    # sun gear
    parts.append(
        '<g class="tc-sun">'
        f'<path d="{gear_path(zs, rs, dep)}" fill="#3a3e43" stroke="{STEEL_LT}" stroke-width="2"/>'
        f'<circle r="16" fill="#101113" stroke="{AMBER}" stroke-width="3"/>'
        "</g>"
    )
    parts.append("</g>")
    style = (
        ".tc-carrier,.tc-planet,.tc-sun{transform-box:fill-box;transform-origin:center}"
        ".tc-sun{animation:tc 24s linear infinite}"
        ".tc-carrier{animation:tc 84s linear infinite}"
        ".tc-planet{animation:tc 25.2s linear infinite reverse}"
        "@keyframes tc{to{transform:rotate(360deg)}}" + REDUCED
    )
    return svg(f"0 0 {W} {H}", "\n".join(parts), "Illustration of a planetary gear set used in automatic transmissions", style)


# ---------------------------------------------------------------- tire sequence frames
def frame(body, label, style=""):
    return svg("0 0 600 400", f'<rect width="600" height="400" fill="#101113"/>{body}', label, style + REDUCED)


def seq_sidewall():
    parts = []
    parts.append('<circle cx="300" cy="620" r="560" fill="#141517"/>')
    for r, c, w in ((548, "#1d1f22", 24), (470, "#202326", 90), (412, "#2a2d31", 6), (380, "#2e3236", 2)):
        parts.append(f'<circle cx="300" cy="620" r="{r}" fill="none" stroke="{c}" stroke-width="{w}"/>')
    parts.append('<circle cx="300" cy="620" r="352" fill="#0b0c0d"/>')
    parts.append('<circle cx="300" cy="620" r="352" fill="none" stroke="url(#sw-lip)" stroke-width="10"/>')
    parts.append('<circle cx="300" cy="620" r="336" fill="none" stroke="#3b3f44" stroke-width="2"/>')
    # raised ribs/serrations near the bead
    for i in range(-40, 41):
        a = -90 + i * 1.6
        x1, y1 = polar(400, a, 300, 620)
        x2, y2 = polar(424, a, 300, 620)
        parts.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="#2b2e32" stroke-width="2"/>')
    defs = ('<defs><linearGradient id="sw-lip" x1="0" x2="1"><stop offset="0" stop-color="#6b7178"/>'
            '<stop offset=".5" stop-color="#dfe3e7"/><stop offset="1" stop-color="#6b7178"/></linearGradient></defs>')
    return frame(defs + "".join(parts), "Illustration of a tire sidewall meeting the wheel rim")


def seq_wheel():
    defs, wheel = wheel_group(cid="sq")
    body = f"<defs>{defs}</defs><g transform=\"translate(300 200) scale(.68)\"><g class=\"sq-spin\">{wheel}</g>{caliper()}</g>"
    style = ".sq-spin{animation:sq 30s linear infinite}@keyframes sq{to{transform:rotate(360deg)}}"
    return frame(body, "Illustration of a wheel and tire", style)


def seq_lugs():
    """Five-lug hub with the standard star tightening sequence."""
    parts = [f'<circle cx="300" cy="200" r="150" fill="#1b1d20" stroke="#4a4f55" stroke-width="3"/>',
             f'<circle cx="300" cy="200" r="44" fill="#26292d" stroke="{STEEL}" stroke-width="2"/>']
    pts = [polar(100, i * 72 - 90, 300, 200) for i in range(5)]
    order = [0, 2, 4, 1, 3]  # star pattern
    d = "M" + " L".join(f"{f(pts[i][0])} {f(pts[i][1])}" for i in order) + " Z"
    parts.append(f'<path class="lg-star" d="{d}" fill="none" stroke="{AMBER}" stroke-width="2" stroke-dasharray="6 6"/>')
    for n, i in enumerate(order, 1):
        x, y = pts[i]
        parts.append(
            f'<g><polygon points="{" ".join(f"{f(polar(24, k * 60, x, y)[0])},{f(polar(24, k * 60, x, y)[1])}" for k in range(6))}" '
            f'fill="#2b2e32" stroke="{STEEL_LT}" stroke-width="2.5"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="9" fill="#101113"/>'
            f'<text x="{f(x + (34 if x >= 300 else -34))}" y="{f(y + 6)}" fill="{STEEL_LT}" font-family="Barlow Condensed, sans-serif" '
            f'font-size="20" font-weight="700" text-anchor="middle">{n}</text></g>'
        )
    style = ".lg-star{animation:lg 3s linear infinite}@keyframes lg{to{stroke-dashoffset:-48}}"
    return frame("".join(parts), "Illustration of five lug nuts with a star-pattern tightening sequence", style)


def seq_balance():
    """Wheel mounted on a balancer spindle with cone and wing nut."""
    parts = [
        '<rect x="0" y="330" width="600" height="70" fill="#17191c"/>',
        '<rect x="40" y="250" width="160" height="150" rx="6" fill="#1f2226" stroke="#4a4f55" stroke-width="2"/>',
        f'<rect x="200" y="186" width="330" height="28" rx="4" fill="#5a6067" stroke="{STEEL_LT}" stroke-width="2"/>',
        # wheel edge-on (section view)
        f'<rect x="300" y="40" width="110" height="320" rx="36" fill="#141517" stroke="#2c3035" stroke-width="3"/>',
        f'<rect x="312" y="104" width="86" height="192" rx="6" fill="#2b2e32" stroke="{STEEL}" stroke-width="2"/>',
        # cone and wing nut
        f'<path d="M410 170 L450 186 L450 214 L410 230 Z" fill="#4b5056" stroke="{STEEL_LT}" stroke-width="2"/>',
        f'<rect x="450" y="176" width="40" height="48" rx="6" fill="#2b2e32" stroke="{STEEL_LT}" stroke-width="2"/>',
        f'<rect x="462" y="150" width="16" height="100" rx="6" fill="#3b3f44" stroke="{STEEL}" stroke-width="2"/>',
        # clip-on weight on rim flange
        f'<rect class="bl-wt" x="398" y="104" width="10" height="26" rx="2" fill="{AMBER}"/>',
    ]
    style = ".bl-wt{animation:bl 2.6s ease-in-out infinite}@keyframes bl{0%,100%{opacity:1}50%{opacity:.35}}"
    return frame("".join(parts), "Illustration of a wheel mounted on a tire balancing machine", style)


def seq_tread_depth():
    parts = []
    for i in range(6):
        x = 40 + i * 90
        parts.append(f'<rect x="{x}" y="120" width="70" height="200" rx="4" fill="#26292d" stroke="#34383d" stroke-width="2"/>')
    # tread depth gauge in a groove
    parts.append(
        f'<rect x="283" y="40" width="34" height="150" rx="4" fill="#3b3f44" stroke="{STEEL_LT}" stroke-width="2"/>'
        f'<rect class="td-pin" x="296" y="190" width="8" height="120" fill="{STEEL_LT}"/>'
        f'<line x1="283" y1="120" x2="317" y2="120" stroke="{AMBER}" stroke-width="3"/>'
    )
    for k in range(6):
        parts.append(f'<line x1="283" y1="{60 + k * 20}" x2="295" y2="{60 + k * 20}" stroke="#101113" stroke-width="2"/>')
    style = ".td-pin{animation:td 3.2s ease-in-out infinite}@keyframes td{0%,100%{transform:translateY(-40px)}50%{transform:none}}"
    return frame("".join(parts), "Illustration of a tread depth gauge measuring a tire groove", style)


def final_night():
    """Shop at dusk: open bays glowing, desert mountains, saguaros. No signage text."""
    W, H = 1600, 800
    parts = [
        '<defs><linearGradient id="fn-sky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#0b0d14"/><stop offset=".55" stop-color="#1b1824"/>'
        '<stop offset=".8" stop-color="#4a2a22"/><stop offset="1" stop-color="#8a4a26"/></linearGradient>'
        '<linearGradient id="fn-bay" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7e3bd"/>'
        '<stop offset="1" stop-color="#d99a4a"/></linearGradient>'
        '<linearGradient id="fn-spill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0b46a" stop-opacity=".45"/>'
        '<stop offset="1" stop-color="#f0b46a" stop-opacity="0"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" fill="url(#fn-sky)"/>',
        # distant mountains
        '<path d="M0 470 L120 430 L220 450 L360 380 L430 400 L520 350 L610 395 L760 420 L900 372 L980 330 L1060 360 '
        'L1180 400 L1320 380 L1460 420 L1600 400 L1600 520 L0 520 Z" fill="#191620"/>',
        '<path d="M0 500 L200 470 L380 490 L600 455 L820 480 L1040 460 L1300 485 L1600 470 L1600 540 L0 540 Z" fill="#131118"/>',
        # lot
        f'<rect y="560" width="{W}" height="{H - 560}" fill="#0c0c0e"/>',
        # building
        '<rect x="360" y="330" width="1000" height="232" fill="#17181b" stroke="#26282c" stroke-width="3"/>',
        '<rect x="340" y="312" width="1040" height="22" fill="#1f2124"/>',
    ]
    for i, x in enumerate((420, 660, 900)):
        parts.append(
            f'<path d="M{x} 560 L{x + 200} 560 L{x + 330} 800 L{x - 130} 800 Z" fill="url(#fn-spill)"/>'
            f'<rect x="{x}" y="382" width="200" height="178" fill="url(#fn-bay)"/>'
            f'<rect x="{x}" y="382" width="200" height="30" fill="#2a2b2e"/>'
            + "".join(f'<line x1="{x}" y1="{386 + k * 7}" x2="{x + 200}" y2="{386 + k * 7}" stroke="#1c1d20"/>' for k in range(4))
            + f'<rect x="{x + 40}" y="498" width="120" height="44" rx="10" fill="#6b4a2a" opacity=".55"/>'
            + f'<rect x="{x - 4}" y="560" width="208" height="6" fill="#2a2b2e"/>'
        )
    # office door + window
    parts.append('<rect x="1160" y="420" width="70" height="140" fill="#2a2b2e"/><rect x="1250" y="400" width="80" height="80" fill="#d99a4a" opacity=".7"/>')
    # wall lights
    for x in (520, 760, 1000):
        parts.append(f'<rect x="{x - 12}" y="350" width="24" height="8" rx="2" fill="#f7e3bd"/>')
    # saguaros
    def saguaro(x, h, s=1):
        y = 560
        return (
            f'<g fill="#0a0a0c"><rect x="{x}" y="{y - h}" width="{18 * s}" height="{h}" rx="{9 * s}"/>'
            f'<path d="M{x} {y - h * 0.45} h-{30 * s} v-{h * 0.28} a{8 * s} {8 * s} 0 0 1 {16 * s} 0 v{h * 0.16} h{14 * s} Z"/>'
            f'<path d="M{x + 18 * s} {y - h * 0.58} h{28 * s} v-{h * 0.22} a{8 * s} {8 * s} 0 0 0 -{16 * s} 0 v{h * 0.1} h-{12 * s} Z"/></g>'
        )
    parts.append(saguaro(170, 240) + saguaro(1480, 200, 0.9) + saguaro(260, 120, 0.6))
    return svg(f"0 0 {W} {H}", "\n".join(parts), "Illustration of an auto shop at dusk with lit service bays and desert mountains")


def main():
    IMG.mkdir(parents=True, exist_ok=True)
    files = {
        "art-tires.svg": tire_tread(),
        "art-alignment.svg": alignment_card(),
        "art-repair.svg": repair_card(),
        "art-transmission.svg": transmission_card(),
        "seq-tread.svg": seq_tread_depth(),
        "seq-sidewall.svg": seq_sidewall(),
        "seq-wheel.svg": seq_wheel(),
        "seq-lugs.svg": seq_lugs(),
        "seq-balance.svg": seq_balance(),
        "final-night.svg": final_night(),
    }
    for name, content in files.items():
        (IMG / name).write_text(content)
    (PARTIALS / "hero-scene.svg").write_text(hero_scene())
    print("wrote", len(files) + 1, "files")


if __name__ == "__main__":
    main()
