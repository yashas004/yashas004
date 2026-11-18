#!/usr/bin/env python3
import json
import math
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path('.')
CFG = json.loads((ROOT / 'scripts' / 'config.json').read_text())
FONTS_DIR = ROOT / 'scripts' / '.fonts'
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

PALETTE = CFG['palette']
C1, C2, C3 = PALETTE['accent1'], PALETTE['accent2'], PALETTE['accent3']

FONT_MAP = {
    'bold': str(FONTS_DIR / 'SpaceGrotesk-Bold.woff'),
    'med': str(FONTS_DIR / 'SpaceGrotesk-Medium.woff'),
    'jb': str(FONTS_DIR / 'JetBrainsMono-Regular.woff'),
    'jbmed': str(FONTS_DIR / 'JetBrainsMono-Medium.woff'),
    'inter': str(FONTS_DIR / 'Inter-Regular.woff'),
    'intermed': str(FONTS_DIR / 'Inter-Medium.woff'),
}

ttfonts = {k: TTFont(v) for k, v in FONT_MAP.items()}


def text_to_paths(text, font_key, font_size, x=0, y=0, fill=PALETTE['text']):
    ttfont = ttfonts[font_key]
    cmap = ttfont.getBestCmap()
    hmtx = ttfont['hmtx']
    glyphset = ttfont.getGlyphSet()
    paths = []
    cur_x = x
    for ch in text:
        if ch == ' ':
            cur_x += font_size * 0.25
            continue
        gid = cmap.get(ord(ch))
        if gid is None:
            cur_x += font_size * 0.3
            continue
        try:
            pen = SVGPathPen(glyphset)
            glyphset[gid].draw(pen)
            d = pen.getCommands()
            if d and d.strip():
                paths.append(
                    f'<path d="{d}" fill="{fill}" '
                    f'transform="matrix({font_size/1000.0},0,0,-{font_size/1000.0},{cur_x:.1f},{y:.1f})"/>'
                )
        except Exception:
            pass
        cur_x += hmtx.metrics[gid][0] * font_size / 1000.0 if gid in hmtx.metrics else font_size * 0.5
    return '\n'.join(paths), cur_x


def wrap_text(text, font_key, font_size, max_width):
    lines = []
    current = ''
    for word in text.split():
        candidate = f'{current} {word}'.strip()
        if text_to_paths(candidate, font_key, font_size)[1] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def starfield(seed, count, w, h):
    rng = random.Random(seed)
    dots = []
    for _ in range(count):
        x = rng.uniform(45, w - 45)
        y = rng.uniform(45, h - 45)
        r = rng.choice((0.8, 1.0, 1.4))
        dur = rng.uniform(2.5, 6.5)
        begin = rng.uniform(0, 4)
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{PALETTE["text"]}" opacity="0.15">'
            f'<animate attributeName="opacity" values="0.06;0.55;0.06" '
            f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            '</circle>'
        )
    return '\n'.join(dots)


def svg_start(w, h, svgid):
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title{svgid} desc{svgid}">
<title id="title{svgid}">{svgid}</title>
<desc id="desc{svgid}">{svgid}</desc>
<defs>
<style><![CDATA[
.bg{{fill:{PALETTE['bg']};}}
.surface{{fill:{PALETTE['surface']};stroke:{PALETTE['border']};stroke-width:1;}}
.text{{fill:{PALETTE['text']};}}
.muted{{fill:{PALETTE['muted']};}}
.accent1{{fill:{C1};}}
.accent2{{fill:{C2};}}
.accent3{{fill:{C3};}}
.border{{stroke:{PALETTE['border']};stroke-width:1;fill:none;}}
@keyframes float{{0%,100%{{transform:translateY(0px);}}50%{{transform:translateY(-7px);}}}}
@keyframes glow{{0%,100%{{opacity:0.35;}}50%{{opacity:0.95;}}}}
@keyframes scan{{0%{{transform:translateY(-120px);}}100%{{transform:translateY(220px);}}}}
@keyframes blink{{0%,49%{{opacity:1;}}50%,100%{{opacity:0;}}}}
@keyframes dash{{to{{stroke-dashoffset:0;}}}}
@keyframes pulse{{0%,100%{{opacity:0.25;transform:scale(0.96);}}50%{{opacity:0.9;transform:scale(1.05);}}}}
@keyframes drift{{0%,100%{{transform:translateX(0);}}50%{{transform:translateX(12px);}}}}
@keyframes breathe{{0%,100%{{opacity:0.2;}}50%{{opacity:0.75;}}}}
@media (prefers-reduced-motion: reduce){{
  .anim,.float,.glow,.scan,.blink,.dash,.pulse,.drift,.breathe{{animation:none !important;}}
  animate,animateTransform,animateMotion{{display:none !important;}}
}}
]]></style>
<clipPath id="clip{svgid}"><rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" ry="18"/></clipPath>
<linearGradient id="g{svgid}" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{C1}"><animate attributeName="stop-color" values="{C1};{C2};{C1}" dur="7s" repeatCount="indefinite"/></stop>
<stop offset="50%" stop-color="{C2}"><animate attributeName="stop-color" values="{C2};{C3};{C2}" dur="9s" repeatCount="indefinite"/></stop>
<stop offset="100%" stop-color="{C3}"><animate attributeName="stop-color" values="{C3};{C1};{C3}" dur="7s" repeatCount="indefinite"/></stop>
</linearGradient>
<radialGradient id="rad{svgid}">
<stop offset="0%" stop-color="{C2}" stop-opacity="0.35"><animate attributeName="stop-opacity" values="0.15;0.45;0.15" dur="6s" repeatCount="indefinite"/></stop>
<stop offset="100%" stop-color="{C2}" stop-opacity="0"/>
</radialGradient>
<filter id="blur{svgid}"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="glow{svgid}" x="-60%" y="-60%" width="220%" height="220%">
<feGaussianBlur stdDeviation="4" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
</defs>
<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>
<rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" ry="18" class="surface"/>
<rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" ry="18" class="border" fill="none"/>
<g clip-path="url(#clip{svgid})">
'''


def svg_end():
    return '</g>\n</svg>\n'


def scan_beam(w, h, svgid, dur='8s'):
    return (
        f'<rect x="24" y="24" width="{w-48}" height="2" fill="url(#g{svgid})" '
        f'opacity="0.3" filter="url(#glow{svgid})">'
        f'<animate attributeName="y" values="24;{h-26};24" dur="{dur}" repeatCount="indefinite"/>'
        '</rect>'
    )


def dash_border(w, h, svgid):
    return (
        f'<rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" fill="none" '
        f'stroke="url(#g{svgid})" stroke-width="1.5" stroke-dasharray="14 10" opacity="0.45">'
        '<animate attributeName="stroke-dashoffset" values="0;-48" dur="4s" repeatCount="indefinite"/>'
        '</rect>'
    )


def sweep(w, h, svgid, dur='6s'):
    return (
        f'<rect x="-240" y="24" width="240" height="{h-48}" fill="url(#g{svgid})" opacity="0.07">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0,0;{w+280},0" dur="{dur}" repeatCount="indefinite"/>'
        '</rect>'
    )


def gen_typing_header():
    w, h = 1000, 92
    svg = svg_start(w, h, 'typing-header')
    svg += starfield(11, 18, w, h)
    svg += sweep(w, h, 'typing-header', '7s')
    svg += scan_beam(w, h, 'typing-header', '10s')
    svg += f'<ellipse cx="180" cy="46" rx="220" ry="55" fill="url(#radtyping-header)"/>'
    svg += text_to_paths('> ', 'jb', 22, 38, 48, C3)[0]
    svg += (
        f'<circle cx="30" cy="41" r="3" fill="{C1}" filter="url(#glowtyping-header)">'
        '<animate attributeName="r" values="2;4;2" dur="2.2s" repeatCount="indefinite"/>'
        '</circle>'
    )
    phrases = ['Full Stack + AI/ML Engineer', 'Building Intelligent Systems', 'Shipping Scalable AI Solutions']
    for i, phrase in enumerate(phrases):
        svg += (
            '<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
            'keyTimes="0;0.02;0.06;0.28;0.33;1" dur="9s" '
            f'begin="{i*3}s" repeatCount="indefinite"/>'
            + text_to_paths(phrase, 'jb', 22, 68, 48, PALETTE['text'])[0] + '</g>'
        )
    svg += (
        f'<rect x="66" y="62" height="2" width="0" fill="url(#gtyping-header)" '
        f'filter="url(#glowtyping-header)" opacity="0.8">'
        '<animate attributeName="width" values="0;380;380;0;0" '
        'keyTimes="0;0.08;0.28;0.34;1" dur="9s" repeatCount="indefinite"/>'
        '</rect>'
    )
    svg += (
        f'<rect x="740" y="33" width="9" height="20" fill="{C3}" filter="url(#glowtyping-header)">'
        '<animate attributeName="opacity" values="1;0;1" dur="0.9s" repeatCount="indefinite"/>'
        '</rect>'
    )
    svg += dash_border(w, h, 'typing-header')
    return svg + svg_end()


def gen_hero():
    w, h = 1000, 380
    svg = svg_start(w, h, 'hero')
    svg += starfield(23, 30, w, h)
    svg += sweep(w, h, 'hero', '8s')
    svg += scan_beam(w, h, 'hero', '11s')
    svg += f'<ellipse cx="800" cy="100" rx="220" ry="70" fill="{C1}" opacity="0.1" filter="url(#blurhero)"><animate attributeName="cx" values="800;690;800" dur="12s" repeatCount="indefinite"/></ellipse>'
    svg += f'<ellipse cx="220" cy="300" rx="200" ry="60" fill="{C2}" opacity="0.09" filter="url(#blurhero)"><animate attributeName="cx" values="220;330;220" dur="14s" repeatCount="indefinite"/></ellipse>'
    svg += f'<ellipse cx="520" cy="160" rx="260" ry="80" fill="url(#radhero)"/>'
    svg += f'<g opacity="0.5"><ellipse cx="250" cy="160" rx="210" ry="72" fill="none" stroke="url(#ghero)" stroke-width="1" stroke-dasharray="5 9"><animateTransform attributeName="transform" type="rotate" from="0 250 160" to="360 250 160" dur="24s" repeatCount="indefinite"/></ellipse></g>'
    svg += f'<circle cx="250" cy="88" r="4" fill="{C2}" filter="url(#glowhero)"><animateMotion dur="24s" repeatCount="indefinite" path="M 250 88 A 210 72 0 1 1 249.9 88"/></circle>'
    svg += text_to_paths(CFG['name'], 'bold', 72, 60, 150, PALETTE['text'])[0]
    svg += f'<rect x="60" y="100" width="200" height="80" fill="url(#ghero)" opacity="0.18"><animateTransform attributeName="transform" type="translate" values="-300,0;1200,0" dur="10s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="60" y="200" width="880" height="120" rx="12" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<circle cx="82" cy="218" r="4" fill="{PALETTE["muted"]}"/><circle cx="98" cy="218" r="4" fill="{PALETTE["muted"]}"/><circle cx="114" cy="218" r="4" fill="{PALETTE["muted"]}"/>'
    svg += text_to_paths('> ', 'jb', 16, 82, 268, C3)[0]
    for i, line in enumerate(CFG['hero']['terminal_lines']):
        start = 0.02 + i * 0.33
        svg += (
            '<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{start:.3f};{start+0.02:.3f};{start+0.28:.3f};{start+0.31:.3f};1" '
            'dur="12s" repeatCount="indefinite"/>'
            + text_to_paths(line, 'jb', 16, 102, 268, PALETTE['text'])[0] + '</g>'
        )
    svg += f'<rect x="360" y="254" width="10" height="18" fill="{C3}" filter="url(#glowhero)"><animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="60" y="292" width="0" height="2" fill="url(#ghero)" opacity="0.8"><animate attributeName="width" values="0;880;880;0" keyTimes="0;0.06;0.94;1" dur="12s" repeatCount="indefinite"/></rect>'
    svg += dash_border(w, h, 'hero')
    return svg + svg_end()


def gen_about():
    w, h = 1000, 300
    svg = svg_start(w, h, 'about-terminal')
    svg += starfield(37, 24, w, h)
    svg += sweep(w, h, 'about-terminal', '9s')
    svg += scan_beam(w, h, 'about-terminal', '7s')
    svg += f'<rect x="60" y="60" width="880" height="180" rx="12" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<circle cx="82" cy="78" r="4" fill="{PALETTE["muted"]}"/><circle cx="98" cy="78" r="4" fill="{PALETTE["muted"]}"/><circle cx="114" cy="78" r="4" fill="{PALETTE["muted"]}"/>'
    svg += text_to_paths('~/about', 'jb', 11, 500, 82, PALETTE['muted'])[0]
    for i in range(9):
        x = 90 + i * 96
        svg += (
            f'<line x1="{x}" y1="90" x2="{x}" y2="228" stroke="{C1}" stroke-width="1" '
            'stroke-dasharray="2 14" opacity="0.12">'
            '<animate attributeName="stroke-dashoffset" values="0;-64" dur="4s" repeatCount="indefinite"/>'
            '</line>'
        )
    y = 120
    for i, line in enumerate(CFG['about_terminal']['lines']):
        start = 0.02 + i * 0.06
        svg += (
            '<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{start:.3f};{start+0.015:.3f};0.93;0.96;1" '
            'dur="16s" repeatCount="indefinite"/>'
            + text_to_paths(line, 'jb', 13, 82, y, C3 if line.startswith('$') else PALETTE['text'])[0] + '</g>'
        )
        y += 20
    svg += f'<rect x="82" y="224" width="0" height="3" rx="1" fill="url(#gabout-terminal)" filter="url(#glowabout-terminal)"><animate attributeName="width" values="0;836;836;0" keyTimes="0;0.2;0.85;1" dur="16s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="908" y="122" width="7" height="14" fill="{C3}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>'
    svg += dash_border(w, h, 'about-terminal')
    return svg + svg_end()


def gen_focus():
    w, h = 1000, 320
    svg = svg_start(w, h, 'focus')
    svg += starfield(41, 26, w, h)
    svg += sweep(w, h, 'focus', '10s')
    svg += scan_beam(w, h, 'focus', '9s')
    focus = CFG['focus']
    for cx, cy, tint in ((200, 190, C1), (500, 190, C2), (800, 190, C3)):
        svg += (
            f'<ellipse cx="{cx}" cy="{cy}" rx="80" ry="34" fill="{tint}" opacity="0.09" '
            f'filter="url(#blurfocus)"><animate attributeName="rx" values="70;95;70" dur="6s" repeatCount="indefinite"/>'
            '</ellipse>'
        )
    svg += f'<rect x="60" y="70" width="280" height="200" rx="14" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(focus[0]['title'], 'med', 18, 82, 105, PALETTE['text'])[0]
    svg += text_to_paths(focus[0]['caption'], 'inter', 11, 82, 125, PALETTE['muted'])[0]
    svg += f'<circle cx="200" cy="190" r="12" stroke="{C1}" fill="none"><animate attributeName="r" values="10;15;10" dur="3s" repeatCount="indefinite"/></circle>'
    for ang, rad in ((0, 36), (120, 36), (240, 36)):
        x = 200 + rad * math.cos(ang * math.pi / 180)
        y = 190 + rad * math.sin(ang * math.pi / 180)
        svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" stroke="{C2}" fill="none"><animate attributeName="opacity" values="0.3;1;0.3" dur="3s" repeatCount="indefinite"/></circle>'
    svg += f'<circle cx="200" cy="190" r="38" stroke="{PALETTE["border"]}" fill="none" stroke-dasharray="4 6"><animateTransform attributeName="transform" type="rotate" from="0 200 190" to="360 200 190" dur="18s" repeatCount="indefinite"/></circle>'
    svg += f'<circle cx="200" cy="152" r="3" fill="{C1}" filter="url(#glowfocus)"><animateMotion dur="10s" repeatCount="indefinite" path="M 200 152 A 38 38 0 1 1 199.9 152"/></circle>'
    svg += f'<rect x="360" y="70" width="280" height="200" rx="14" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(focus[1]['title'], 'med', 18, 382, 105, PALETTE['text'])[0]
    svg += text_to_paths(focus[1]['caption'], 'inter', 11, 382, 125, PALETTE['muted'])[0]
    svg += f'<rect x="382" y="150" width="236" height="90" rx="6" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<rect x="394" y="162" width="32" height="18" rx="3" stroke="{C2}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;70,0;-20,0" dur="8s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="440" y="182" width="38" height="20" rx="3" stroke="{C1}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;-40,0;30,0" dur="9s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="410" y="210" width="28" height="16" rx="3" stroke="{C3}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;50,0;-10,0" dur="7s" repeatCount="indefinite"/></rect>'
    svg += f'<line x1="382" y1="195" x2="618" y2="195" stroke="{C3}" stroke-width="1" opacity="0.5"><animate attributeName="y1" values="195;185;205;195" dur="4s" repeatCount="indefinite"/><animate attributeName="y2" values="195;185;205;195" dur="4s" repeatCount="indefinite"/></line>'
    svg += f'<circle cx="382" cy="195" r="3" fill="{C3}" filter="url(#glowfocus)"><animateMotion dur="5s" repeatCount="indefinite" path="M 382 195 L 618 195"/></circle>'
    svg += f'<rect x="660" y="70" width="280" height="200" rx="14" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(focus[2]['title'], 'med', 18, 682, 105, PALETTE['text'])[0]
    svg += text_to_paths(focus[2]['caption'], 'inter', 11, 682, 125, PALETTE['muted'])[0]
    svg += f'<path d="M 682 190 L 730 190 L 750 175 L 790 175 L 810 190 L 920 190" stroke="{C1}" stroke-width="2" fill="none" stroke-dasharray="400 0"><animate attributeName="stroke-dasharray" values="0,400;400,0" dur="4s" repeatCount="indefinite"/></path>'
    svg += f'<circle cx="682" cy="190" r="4" fill="{C1}" filter="url(#glowfocus)"><animateMotion dur="4s" repeatCount="indefinite" path="M 682 190 L 730 190 L 750 175 L 790 175 L 810 190 L 920 190"/></circle>'
    svg += f'<rect x="850" y="170" width="70" height="36" rx="8" stroke="{PALETTE["border"]}" fill="none"/>'
    for i in range(6):
        svg += f'<rect x="{860+i*8}" y="{180+(i%2)*4}" width="4" height="16" rx="2" fill="{C2}"><animate attributeName="height" values="6;18;6" dur="1.2s" begin="{i*0.08}s" repeatCount="indefinite"/></rect>'
    svg += dash_border(w, h, 'focus')
    return svg + svg_end()


def gen_stack():
    w, h = 1000, 280
    svg = svg_start(w, h, 'stack')
    svg += starfield(53, 20, w, h)
    svg += sweep(w, h, 'stack', '7s')
    rows = CFG['stack']['rows']
    y = 90
    for r, row in enumerate(rows):
        svg += f'<g><animateTransform attributeName="transform" type="translate" values="0,0;-14,0;0,0" dur="{8+r*2}s" repeatCount="indefinite"/>'
        svg += f'<rect x="48" y="{y-16}" width="904" height="32" rx="16" fill="url(#radstack)" opacity="0.25"/>'
        cx = 60
        for item in row:
            item_w = len(item) * 7 + 36
            tint = C1 if r == 0 else C2 if r == 1 else C3
            svg += f'<rect x="{cx}" y="{y-12}" width="{item_w}" height="24" rx="12" stroke="{PALETTE["border"]}" fill="none"/>'
            svg += f'<circle cx="{cx+14}" cy="{y}" r="3" fill="{tint}"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.4s" repeatCount="indefinite"/></circle>'
            svg += text_to_paths(item, 'jb', 11, cx + 26, y + 4, PALETTE['text'])[0]
            cx += item_w + 14
        svg += f'<rect x="48" y="{y-16}" width="120" height="32" rx="16" fill="url(#gstack)" opacity="0.14"><animateTransform attributeName="transform" type="translate" values="0,0;840,0;0,0" dur="{6+r}s" repeatCount="indefinite"/></rect>'
        svg += '</g>'
        y += 60
    svg += dash_border(w, h, 'stack')
    return svg + svg_end()


def gen_project(fname, proj):
    svgid = fname.replace('.svg', '')
    w, h = 1000, 260
    svg = svg_start(w, h, svgid)
    svg += starfield(sum(fname.encode()), 20, w, h)
    svg += sweep(w, h, svgid, '8s')
    svg += scan_beam(w, h, svgid, '9s')
    svg += '<g><animateTransform attributeName="transform" type="translate" values="0,0;0,-4;0,0" dur="6s" repeatCount="indefinite"/>'
    svg += f'<rect x="60" y="40" width="880" height="180" rx="16" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<ellipse cx="880" cy="120" rx="160" ry="60" fill="url(#rad{svgid})"/>'
    svg += text_to_paths(proj['name'], 'bold', 30, 90, 90, PALETTE['text'])[0]
    if proj.get('chip'):
        chip_w = len(proj['chip']) * 6 + 22
        chip_x = 90 + len(proj['name']) * 15 + 24
        svg += f'<rect x="{chip_x}" y="74" width="{chip_w}" height="20" rx="10" stroke="{C3}" fill="none"><animate attributeName="opacity" values="0.45;1;0.45" dur="2.6s" repeatCount="indefinite"/></rect>'
        svg += text_to_paths(proj['chip'], 'jb', 9, chip_x + 10, 86, C3)[0]
    for i, line in enumerate(wrap_text(proj['desc'], 'inter', 13, 670)):
        svg += text_to_paths(line, 'inter', 13, 90, 120 + i * 18, PALETTE['text'])[0]
    cx = 90
    for tag in proj['tags']:
        tag_w = len(tag) * 6 + 20
        svg += f'<rect x="{cx}" y="185" width="{tag_w}" height="22" rx="11" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += text_to_paths(tag, 'jb', 10, cx + 12, 199, PALETTE['muted'])[0]
        cx += tag_w + 10
    if proj['name'] == 'Persona.AI':
        for i in range(6):
            svg += f'<rect x="{800+i*10}" y="{110+(3-i%4)*3}" width="6" height="{12+i*2}" rx="3" fill="{C1}"><animate attributeName="height" values="{8+i};{18+i};{8+i}" dur="1.4s" begin="{i*0.08}s" repeatCount="indefinite"/></rect>'
    elif proj['name'] == 'PriorAuth':
        svg += f'<rect x="800" y="90" width="42" height="52" rx="6" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += f'<circle cx="870" cy="98" r="9" stroke="{C1}" fill="none"/><circle cx="910" cy="116" r="9" stroke="{C2}" fill="none"/><circle cx="870" cy="134" r="9" stroke="{C3}" fill="none"/>'
        svg += f'<polyline points="865,134 870,139 879,130" stroke="{C3}" fill="none" stroke-width="1.5"><animate attributeName="stroke-dasharray" values="0,16;16,0" dur="2s" repeatCount="indefinite"/></polyline>'
    elif proj['name'] == 'bq-cost-guard':
        svg += f'<path d="M 812 82 L 840 92 L 840 118 Q 840 140 812 152 Q 784 140 784 118 L 784 92 Z" stroke="{C1}" fill="none" stroke-width="1.5"/>'
        svg += f'<path d="M 802 118 L 810 128 L 826 106" stroke="{C3}" fill="none" stroke-width="2"><animate attributeName="stroke-dasharray" values="0,40;40,0" dur="2.4s" repeatCount="indefinite"/></path>'
        svg += f'<rect x="858" y="104" width="72" height="6" rx="3" fill="{PALETTE["border"]}"/>'
        svg += f'<rect x="858" y="104" width="0" height="6" rx="3" fill="url(#g{svgid})"><animate attributeName="width" values="0;72;72;0" keyTimes="0;0.3;0.8;1" dur="5s" repeatCount="indefinite"/></rect>'
        for i in range(4):
            svg += f'<rect x="{858+i*18}" y="122" width="10" height="{8+i*3}" rx="2" fill="{C2}" opacity="0.6"><animate attributeName="height" values="{4+i};{12+i*3};{4+i}" dur="{1.4+i*0.2:.1f}s" repeatCount="indefinite"/></rect>'
    elif proj['name'] == 'schema-drift-watch':
        for col_x, tint in ((780, C1), (872, C2)):
            for j, bar_w in enumerate((52, 34, 60, 44)):
                svg += f'<rect x="{col_x}" y="{94+j*16}" width="{bar_w}" height="6" rx="3" fill="{tint}" opacity="0.5"><animate attributeName="opacity" values="0.2;0.85;0.2" dur="{2+j*0.3:.1f}s" repeatCount="indefinite"/></rect>'
        svg += f'<path d="M 846 122 L 864 122" stroke="{C3}" stroke-width="2" fill="none"><animate attributeName="stroke-dasharray" values="0,20;20,0" dur="2s" repeatCount="indefinite"/></path>'
        svg += f'<circle cx="855" cy="122" r="3" fill="{C3}" filter="url(#glow{svgid})"><animate attributeName="r" values="2;5;2" dur="2s" repeatCount="indefinite"/></circle>'
    svg += '</g>'
    svg += dash_border(w, h, svgid)
    return svg + svg_end()


def gen_build():
    w, h = 1000, 220
    svg = svg_start(w, h, 'build-loop')
    svg += starfield(67, 22, w, h)
    svg += sweep(w, h, 'build-loop', '8s')
    svg += text_to_paths('build loop', 'med', 16, 60, 80, PALETTE['muted'])[0]
    nodes = [('Idea', 170), ('Prototype', 380), ('Test', 590), ('Ship', 800)]
    for name, x in nodes:
        svg += f'<circle cx="{x}" cy="130" r="42" fill="url(#radbuild-loop)" opacity="0.4"><animate attributeName="r" values="36;46;36" dur="5s" repeatCount="indefinite"/></circle>'
        svg += f'<circle cx="{x}" cy="130" r="30" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += f'<circle cx="{x}" cy="130" r="30" stroke="url(#gbuild-loop)" fill="none" stroke-dasharray="8 12" opacity="0.6"><animateTransform attributeName="transform" type="rotate" from="0 {x} 130" to="360 {x} 130" dur="12s" repeatCount="indefinite"/></circle>'
        svg += text_to_paths(name, 'jb', 11, x - len(name) * 3, 135, PALETTE['text'])[0]
    trail = 'M0,0 L210,0 L420,0 L630,0 L630,-70 L-630,-70 L-630,0 Z'
    svg += f'<circle cx="170" cy="130" r="14" fill="{C3}" opacity="0.18" filter="url(#glowbuild-loop)"><animateMotion dur="7s" repeatCount="indefinite" path="{trail}"/></circle>'
    svg += f'<circle cx="170" cy="130" r="6" fill="{C3}" filter="url(#glowbuild-loop)"><animateMotion dur="7s" repeatCount="indefinite" path="{trail}"/></circle>'
    svg += dash_border(w, h, 'build-loop')
    return svg + svg_end()


def gen_contact(label):
    svgid = f'contact-{label.lower()}'
    w, h = 320, 90
    svg = svg_start(w, h, svgid)
    svg += starfield(71 + len(label), 10, w, h)
    svg += sweep(w, h, svgid, '6s')
    svg += f'<rect x="30" y="20" width="260" height="50" rx="25" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<rect x="30" y="20" width="260" height="50" rx="25" stroke="url(#g{svgid})" fill="none" stroke-dasharray="20 12" opacity="0.5"><animate attributeName="stroke-dashoffset" values="0;-64" dur="5s" repeatCount="indefinite"/></rect>'
    svg += text_to_paths(label, 'jb', 13, 52, 48, PALETTE['text'])[0]
    svg += f'<g><animateTransform attributeName="transform" type="translate" values="0,0;6,0;0,0" dur="2s" repeatCount="indefinite"/>'
    svg += text_to_paths('->', 'jb', 16, 252, 50, C1)[0]
    svg += '</g>'
    svg += dash_border(w, h, svgid)
    return svg + svg_end()


def gen_footer():
    w, h = 1000, 110
    svg = svg_start(w, h, 'footer')
    svg += starfield(83, 24, w, h)
    svg += sweep(w, h, 'footer', '6s')
    svg += f'<ellipse cx="500" cy="58" rx="380" ry="40" fill="url(#radfooter)"/>'
    svg += (
        '<path d="M 50 60 Q 250 40 450 60 T 850 60 T 950 60" '
        'stroke="url(#gfooter)" stroke-width="2.5" fill="none" opacity="0.9" filter="url(#glowfooter)">'
        '<animate attributeName="d" values="M 50 60 Q 250 40 450 60 T 850 60 T 950 60;'
        'M 50 60 Q 250 78 450 60 T 850 60 T 950 60;'
        'M 50 60 Q 250 40 450 60 T 850 60 T 950 60" dur="8s" repeatCount="indefinite"/>'
        '<animate attributeName="stroke-dasharray" values="4 8;18 4;4 8" dur="5s" repeatCount="indefinite"/>'
        '</path>'
    )
    svg += f'<circle cx="50" cy="60" r="4" fill="{C1}" filter="url(#glowfooter)"><animateMotion dur="6s" repeatCount="indefinite" path="M 50 60 Q 250 40 450 60 T 850 60 T 950 60"/></circle>'
    for x, tint in ((200, C1), (500, C2), (800, C3)):
        svg += f'<circle cx="{x}" cy="60" r="6" fill="none" stroke="{tint}" opacity="0.5"><animate attributeName="r" values="3;14;3" dur="4s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0;0.6" dur="4s" repeatCount="indefinite"/></circle>'
    svg += dash_border(w, h, 'footer')
    return svg + svg_end()


def gen_footer_glow():
    w, h = 1000, 120
    svg = svg_start(w, h, 'footer-glow')
    svg += starfield(97, 26, w, h)
    svg += sweep(w, h, 'footer-glow', '6s')
    svg += scan_beam(w, h, 'footer-glow', '8s')
    svg += f'<ellipse cx="500" cy="60" rx="420" ry="50" fill="url(#radfooter-glow)"/>'
    wave = 'M 40 62 Q 240 32 440 62 T 840 62 T 960 62'
    svg += (
        f'<path d="{wave}" stroke="url(#gfooter-glow)" stroke-width="3" fill="none" '
        f'filter="url(#glowfooter-glow)" opacity="0.9">'
        '<animate attributeName="stroke-dasharray" values="6 12;30 6;6 12" dur="6s" repeatCount="indefinite"/>'
        '</path>'
    )
    svg += f'<circle cx="40" cy="62" r="5" fill="{C3}" filter="url(#glowfooter-glow)"><animateMotion dur="7s" repeatCount="indefinite" path="{wave}"/></circle>'
    for i in range(14):
        x = 70 + i * 65
        svg += (
            f'<line x1="{x}" y1="42" x2="{x}" y2="84" stroke="{C1 if i%2 else C2}" '
            'stroke-width="2" stroke-linecap="round" opacity="0.5">'
            f'<animate attributeName="opacity" values="0.1;0.8;0.1" dur="{1.2+i*0.07:.2f}s" '
            f'begin="{i*0.11:.2f}s" repeatCount="indefinite"/>'
            '</line>'
        )
    svg += dash_border(w, h, 'footer-glow')
    return svg + svg_end()


def main():
    (ASSETS / 'typing-header.svg').write_text(gen_typing_header())
    (ASSETS / 'hero.svg').write_text(gen_hero())
    (ASSETS / 'about-terminal.svg').write_text(gen_about())
    (ASSETS / 'focus.svg').write_text(gen_focus())
    (ASSETS / 'stack.svg').write_text(gen_stack())
    for proj in CFG['projects']:
        (ASSETS / proj['file']).write_text(gen_project(proj['file'], proj))
    (ASSETS / 'build-loop.svg').write_text(gen_build())
    if CFG['contacts']['email']['enabled']:
        (ASSETS / 'contact-email.svg').write_text(gen_contact('Email'))
    if CFG['contacts']['youtube']['enabled']:
        (ASSETS / 'contact-youtube.svg').write_text(gen_contact('YouTube'))
    (ASSETS / 'footer.svg').write_text(gen_footer())
    (ASSETS / 'footer-glow.svg').write_text(gen_footer_glow())
    print('done')


if __name__ == '__main__':
    main()
