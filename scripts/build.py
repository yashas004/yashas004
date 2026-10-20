#!/usr/bin/env python3
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path('.')
CFG = json.loads((ROOT / 'scripts' / 'config.json').read_text())
FONTS_DIR = ROOT / 'scripts' / '.fonts'
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

PALETTE = CFG['palette']

FONT_MAP = {
    'bold': str(FONTS_DIR / 'SpaceGrotesk-Bold.woff'),
    'med': str(FONTS_DIR / 'SpaceGrotesk-Medium.woff'),
    'jb': str(FONTS_DIR / 'JetBrainsMono-Regular.woff'),
    'jbmed': str(FONTS_DIR / 'JetBrainsMono-Medium.woff'),
    'inter': str(FONTS_DIR / 'Inter-Regular.woff'),
    'intermed': str(FONTS_DIR / 'Inter-Medium.woff'),
}

ttfonts = {k: TTFont(v) for k,v in FONT_MAP.items()}

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
        if ord(ch) not in cmap:
            cur_x += font_size * 0.3
            continue
        gid = cmap[ord(ch)]
        try:
            pen = SVGPathPen(glyphset)
            glyphset[gid].draw(pen)
            d = pen.getCommands()
            if d and d.strip():
                # Scale and translate - font units to pixel units
                paths.append(f'<path d="{d}" fill="{fill}" transform="matrix({font_size/1000.0},0,0,-{font_size/1000.0},{cur_x:.1f},{y:.1f})"/>')
            gname = gid
            try:
                w = hmtx[gname][0]
                cur_x += w * font_size / 1000.0
            except Exception:
                cur_x += font_size * 0.5
        except Exception:
            cur_x += font_size * 0.3
            continue
    return '\n'.join(paths), cur_x

def svg_start(w,h,svgid):
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title{svgid} desc{svgid}">
<title id="title{svgid}">{svgid}</title>
<desc id="desc{svgid}">{svgid}</desc>
<defs>
<style><![CDATA[
.bg{{fill:{PALETTE['bg']};}}
.surface{{fill:{PALETTE['surface']};stroke:{PALETTE['border']};stroke-width:1;}}
.text{{fill:{PALETTE['text']};}}
.muted{{fill:{PALETTE['muted']};}}
.accent1{{fill:{PALETTE['accent1']};}}
.accent2{{fill:{PALETTE['accent2']};}}
.accent3{{fill:{PALETTE['accent3']};}}
.border{{stroke:{PALETTE['border']};stroke-width:1;fill:none;}}
@keyframes shimmer{{0%{{transform:translateX(-200px);}}100%{{transform:translateX(1400px);}}}}
@keyframes pulse{{0%,100%{{opacity:0.4;}}50%{{opacity:1;}}}}
@keyframes blink{{0%,49%{{opacity:1;}}50%,100%{{opacity:0;}}}}
@keyframes sweep{{0%{{transform:translateX(-400px);}}100%{{transform:translateX(1500px);}}}}
@keyframes rotate{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}
@media (prefers-reduced-motion: reduce){{
  .anim,.shimmer,.pulse,.blink,.sweep,.rotate{{animation:none !important;}}
  animate,animateTransform,animateMotion{{display:none !important;}}
}}
]]></style>
<clipPath id="clip{svgid}"><rect x="16" y="16" width="{w-32}" height="{h-32}" rx="16" ry="16"/></clipPath>
<linearGradient id="grad{svgid}" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{PALETTE['accent1']}"/>
<stop offset="50%" stop-color="{PALETTE['accent2']}"/>
<stop offset="100%" stop-color="{PALETTE['accent1']}"/>
</linearGradient>
</defs>
<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>
<rect x="16" y="16" width="{w-32}" height="{h-32}" rx="16" ry="16" class="surface"/>
<rect x="16" y="16" width="{w-32}" height="{h-32}" rx="16" ry="16" class="border" fill="none"/>
<g clip-path="url(#clip{svgid})">
'''

def svg_end():
    return '</g>\n</svg>\n'

def gen_label(name, text):
    w,h = 260, 60
    svg = svg_start(w,h,name)
    svg += f'<line x1="32" y1="40" x2="228" y2="40" stroke="{PALETTE["accent1"]}" stroke-width="1.5" stroke-dasharray="200" stroke-dashoffset="200"><animate attributeName="stroke-dashoffset" from="200" to="0" dur="1.2s" fill="freeze" calcMode="spline" keySplines=".22 1 .36 1"/></line>'
    svg += text_to_paths(text, 'jb', 12, 32, 32, PALETTE['muted'])[0]
    svg += svg_end()
    return svg

def gen_divider():
    w,h = 1000, 40
    svg = svg_start(w,h,'divider')
    svg += f'<line x1="32" y1="20" x2="968" y2="20" stroke="url(#graddivider)" stroke-width="1"><animate attributeName="opacity" values="0.3;0.8;0.3" dur="6s" repeatCount="indefinite"/></line>'
    svg += svg_end()
    return svg

def gen_hero():
    w,h = 1000, 400
    svg = svg_start(w,h,'hero')
    # grid
    svg += f'<g opacity="0.08"><line x1="32" y1="80" x2="968" y2="80" stroke="{PALETTE["muted"]}"/><line x1="32" y1="120" x2="968" y2="120" stroke="{PALETTE["muted"]}"/></g>'
    svg += f'<g opacity="0.05"><animateTransform attributeName="transform" type="translate" values="0,0;0,-4;0,0" dur="12s" repeatCount="indefinite"/><line x1="60" y1="60" x2="940" y2="60" stroke="{PALETTE["muted"]}"/></g>'
    svg += text_to_paths(CFG['name'], 'bold', 64, 60, 140, PALETTE['text'])[0]
    svg += f'<rect x="60" y="90" width="120" height="70" fill="url(#gradhero)" opacity="0.25"><animateTransform attributeName="transform" type="translate" values="-200,0;1400,0" dur="8s" repeatCount="indefinite"/></rect>'
    svg += text_to_paths('> ', 'jb', 16, 60, 190, PALETTE['accent3'])[0]
    lines = CFG['hero']['terminal_lines']
    for i,l in enumerate(lines):
        svg += f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{0.01+i*0.33:.3f};{0.32+i*0.33:.3f};{0.33+i*0.33:.3f}" dur="12s" repeatCount="indefinite"/>' + text_to_paths(l, 'jb', 16, 80, 190, PALETTE['text'])[0] + '</g>'
    svg += f'<rect x="320" y="176" width="10" height="18" fill="{PALETTE["accent3"]}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>'
    # signal
    svg += f'<ellipse cx="120" cy="300" rx="8" ry="8" class="accent1"><animate attributeName="opacity" values="0.5;1;0.5" dur="3s" repeatCount="indefinite"/></ellipse>'
    svg += text_to_paths('audio', 'jb', 10, 100, 330, PALETTE['muted'])[0]
    svg += f'<ellipse cx="120" cy="320" rx="8" ry="8" class="accent2"><animate attributeName="opacity" values="0.5;1;0.5" dur="3.2s" repeatCount="indefinite"/></ellipse>'
    svg += text_to_paths('video', 'jb', 10, 100, 350, PALETTE['muted'])[0]
    svg += f'<ellipse cx="120" cy="340" rx="8" ry="8" class="accent3"><animate attributeName="opacity" values="0.5;1;0.5" dur="3.4s" repeatCount="indefinite"/></ellipse>'
    svg += text_to_paths('text', 'jb', 10, 100, 370, PALETTE['muted'])[0]
    svg += f'<path d="M 128 300 Q 200 300 260 320" stroke="{PALETTE["accent1"]}" stroke-width="1" fill="none" opacity="0.6"><animate attributeName="stroke-dasharray" values="0,200;200,0" dur="4s" repeatCount="indefinite"/></path>'
    svg += f'<path d="M 128 320 Q 200 310 260 320" stroke="{PALETTE["accent2"]}" stroke-width="1" fill="none" opacity="0.6"><animate attributeName="stroke-dasharray" values="0,200;200,0" dur="4.2s" repeatCount="indefinite"/></path>'
    svg += f'<path d="M 128 340 Q 200 330 260 320" stroke="{PALETTE["accent3"]}" stroke-width="1" fill="none" opacity="0.6"><animate attributeName="stroke-dasharray" values="0,200;200,0" dur="4.4s" repeatCount="indefinite"/></path>'
    svg += f'<polygon points="500,290 530,305 530,335 500,350 470,335 470,305" stroke="{PALETTE["accent1"]}" fill="none" stroke-width="1.5"><animateTransform attributeName="transform" type="rotate" from="0 500 320" to="360 500 320" dur="20s" repeatCount="indefinite"/></polygon>'
    svg += text_to_paths('model', 'jb', 10, 488, 325, PALETTE['text'])[0]
    svg += f'<path d="M 530 320 Q 650 320 720 320" stroke="{PALETTE["accent2"]}" stroke-width="1" fill="none" opacity="0.6"><animate attributeName="stroke-dasharray" values="0,220;220,0" dur="5s" repeatCount="indefinite"/></path>'
    svg += f'<rect x="720" y="290" width="200" height="80" rx="6" class="border" fill="none"/>'
    svg += text_to_paths('app', 'jb', 10, 735, 310, PALETTE['muted'])[0]
    svg += f'<rect x="735" y="320" width="170" height="6" rx="3" fill="{PALETTE["border"]}"><animate attributeName="width" values="20;170;170" dur="3s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="735" y="335" width="120" height="6" rx="3" fill="{PALETTE["border"]}"><animate attributeName="width" values="0;120;120" dur="3.3s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="735" y="350" width="90" height="6" rx="3" fill="{PALETTE["border"]}"><animate attributeName="width" values="0;90;90" dur="3.6s" repeatCount="indefinite"/></rect>'
    svg += svg_end()
    return svg

def gen_about():
    w,h = 1000, 330
    svg = svg_start(w,h,'about-terminal')
    svg += f'<rect x="32" y="40" width="936" height="250" rx="8" class="border" fill="none"/>'
    svg += f'<circle cx="52" cy="56" r="4" fill="{PALETTE["muted"]}"/><circle cx="66" cy="56" r="4" fill="{PALETTE["muted"]}"/><circle cx="80" cy="56" r="4" fill="{PALETTE["muted"]}"/>'
    svg += text_to_paths('yashas ~ about', 'jb', 11, 500, 60, PALETTE['muted'])[0]
    lines = CFG['about_terminal']['lines']
    y = 90
    for i,l in enumerate(lines):
        svg += f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{0.02+i*0.11:.3f};{0.88-i*0.01:.3f};0.95" dur="16s" repeatCount="indefinite"/>' + text_to_paths(l, 'jb', 13, 52, y, PALETTE['accent3'] if l.startswith('$') else PALETTE['text'])[0] + '</g>'
        y += 22
    svg += svg_end()
    return svg

def gen_focus():
    w,h = 1000, 300
    svg = svg_start(w,h,'focus')
    focus = CFG['focus']
    svg += f'<rect x="60" y="60" width="280" height="200" rx="10" class="border" fill="none"/>'
    svg += text_to_paths(focus[0]['title'], 'med', 16, 80, 90, PALETTE['text'])[0]
    svg += text_to_paths(focus[0]['caption'], 'inter', 11, 80, 110, PALETTE['muted'])[0]
    svg += f'<circle cx="200" cy="170" r="10" stroke="{PALETTE["accent1"]}" fill="none"><animate attributeName="r" values="10;12;10" dur="3s" repeatCount="indefinite"/></circle>'
    svg += f'<circle cx="140" cy="150" r="6" stroke="{PALETTE["accent2"]}" fill="none"/><circle cx="260" cy="150" r="6" stroke="{PALETTE["accent2"]}" fill="none"/><circle cx="200" cy="210" r="6" stroke="{PALETTE["accent2"]}" fill="none"/>'
    svg += f'<path d="M200 170 L140 150" stroke="{PALETTE["accent1"]}" opacity="0.6"><animate attributeName="stroke-dasharray" values="0,80;80,0" dur="4s" repeatCount="indefinite"/></path>'
    svg += f'<path d="M200 170 L260 150" stroke="{PALETTE["accent1"]}" opacity="0.6"><animate attributeName="stroke-dasharray" values="0,80;80,0" dur="4.2s" repeatCount="indefinite"/></path>'
    svg += f'<path d="M200 170 L200 210" stroke="{PALETTE["accent1"]}" opacity="0.6"><animate attributeName="stroke-dasharray" values="0,80;80,0" dur="4.4s" repeatCount="indefinite"/></path>'
    svg += f'<ellipse cx="200" cy="170" rx="30" ry="14" stroke="{PALETTE["border"]}" fill="none"><animateTransform attributeName="transform" type="rotate" from="0 200 170" to="360 200 170" dur="12s" repeatCount="indefinite"/></ellipse>'
    svg += f'<rect x="360" y="60" width="280" height="200" rx="10" class="border" fill="none"/>'
    svg += text_to_paths(focus[1]['title'], 'med', 16, 380, 90, PALETTE['text'])[0]
    svg += text_to_paths(focus[1]['caption'], 'inter', 11, 380, 110, PALETTE['muted'])[0]
    svg += f'<rect x="380" y="130" width="240" height="80" rx="4" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<rect x="390" y="140" width="30" height="18" rx="2" stroke="{PALETTE["accent2"]}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;40,0;0,0" dur="6s" repeatCount="indefinite"/></rect>'
    svg += text_to_paths('vehicle', 'jb', 8, 393, 151, PALETTE['muted'])[0]
    svg += f'<rect x="450" y="160" width="35" height="20" rx="2" stroke="{PALETTE["accent1"]}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;-30,0;0,0" dur="7s" repeatCount="indefinite"/></rect>'
    svg += text_to_paths('vehicle', 'jb', 8, 453, 172, PALETTE['muted'])[0]
    svg += f'<line x1="380" y1="170" x2="620" y2="170" stroke="{PALETTE["accent3"]}" stroke-width="1" opacity="0.5"><animate attributeName="x1" values="380;620;380" dur="4s" repeatCount="indefinite"/><animate attributeName="x2" values="420;660;420" dur="4s" repeatCount="indefinite"/></line>'
    svg += f'<rect x="660" y="60" width="280" height="200" rx="10" class="border" fill="none"/>'
    svg += text_to_paths(focus[2]['title'], 'med', 16, 680, 90, PALETTE['text'])[0]
    svg += text_to_paths(focus[2]['caption'], 'inter', 11, 680, 110, PALETTE['muted'])[0]
    svg += f'<path d="M 680 170 L 720 170 L 740 155 L 780 155 L 800 170 L 920 170" stroke="{PALETTE["accent1"]}" fill="none" stroke-width="1.5"><animate attributeName="stroke-dasharray" values="0,300;300,0" dur="4s" repeatCount="indefinite"/></path>'
    svg += f'<rect x="820" y="150" width="80" height="40" rx="6" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<rect x="830" y="160" width="40" height="4" rx="2" fill="{PALETTE["accent2"]}"><animate attributeName="width" values="10;40;10" dur="3s" repeatCount="indefinite"/></rect>'
    svg += f'<circle cx="900" cy="170" r="4" fill="{PALETTE["accent3"]}"><animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/></circle>'
    svg += svg_end()
    return svg

def gen_stack():
    w,h = 1000, 300
    svg = svg_start(w,h,'stack')
    rows = CFG['stack']['rows']
    y = 80
    for r,row in enumerate(rows):
        cx = 32
        for item in row:
            witem = len(item)*7 + 30
            svg += f'<rect x="{cx}" y="{y-10}" width="{witem}" height="22" rx="11" stroke="{PALETTE["border"]}" fill="none"/>'
            svg += f'<circle cx="{cx+12}" cy="{y+1}" r="3" fill="{PALETTE["accent1"] if r==0 else PALETTE["accent2"] if r==1 else PALETTE["accent3"]}"/>'
            svg += text_to_paths(item, 'jb', 11, cx+22, y+4, PALETTE['text'])[0]
            cx += witem + 12
        y += 60
    # marquee groups
    svg += f'<g><animateTransform attributeName="transform" type="translate" values="0,0;-300,0;0,0" dur="18s" repeatCount="indefinite"/></g>'
    svg += svg_end()
    return svg

def gen_project(fname, proj):
    w,h = 1000, 260
    svg = svg_start(w,h,fname.replace('.svg',''))
    svg += f'<rect x="32" y="32" width="936" height="196" rx="12" class="border" fill="none"/>'
    svg += text_to_paths(proj['name'], 'bold', 28, 60, 80, PALETTE['text'])[0]
    if proj.get('chip'):
        cw = len(proj['chip'])*6 + 20
        svg += f'<rect x="{60 + len(proj["name"])*14 + 20}" y="64" width="{cw}" height="18" rx="9" stroke="{PALETTE["accent3"]}" fill="none"/>'
        svg += text_to_paths(proj['chip'], 'jb', 9, 60 + len(proj["name"])*14 + 30, 75, PALETTE['accent3'])[0]
    svg += text_to_paths(proj['desc'], 'inter', 13, 60, 110, PALETTE['text'])[0]
    cx = 60; cy = 150
    for tag in proj['tags']:
        tw = len(tag)*6 + 18
        svg += f'<rect x="{cx}" y="{cy-10}" width="{tw}" height="20" rx="10" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += text_to_paths(tag, 'jb', 10, cx+10, cy+3, PALETTE['muted'])[0]
        cx += tw + 8
    if proj['name'] == 'Persona.AI':
        for i in range(5):
            svg += f'<rect x="{780+i*12}" y="{120 + (2-i%3)*4}" width="6" height="{14+i*2}" rx="2" fill="{PALETTE["accent1"]}"><animate attributeName="height" values="{8+i};{18+i};{8+i}" dur="1.6s" begin="{i*0.1}s" repeatCount="indefinite"/></rect>'
    elif proj['name'] == 'PriorAuth':
        svg += f'<rect x="760" y="80" width="40" height="50" rx="4" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += f'<circle cx="820" cy="90" r="8" stroke="{PALETTE["accent1"]}" fill="none"/><circle cx="860" cy="105" r="8" stroke="{PALETTE["accent2"]}" fill="none"/><circle cx="820" cy="120" r="8" stroke="{PALETTE["accent3"]}" fill="none"/>'
        svg += f'<polyline points="816,120 820,124 828,116" stroke="{PALETTE["accent3"]}" fill="none"><animate attributeName="stroke-dasharray" values="0,20;20,0" dur="2.4s" repeatCount="indefinite"/></polyline>'
    elif proj['name'] == 'SecureWays':
        svg += f'<rect x="740" y="90" width="160" height="80" rx="4" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += f'<rect x="750" y="100" width="25" height="15" rx="2" stroke="{PALETTE["accent1"]}"><animateTransform attributeName="transform" type="translate" values="0,0;60,0;0,0" dur="6s" repeatCount="indefinite"/></rect>'
        svg += f'<rect x="820" y="110" width="30" height="18" rx="2" stroke="{PALETTE["accent2"]}"><animateTransform attributeName="transform" type="translate" values="0,0;-40,0;0,0" dur="7s" repeatCount="indefinite"/></rect>'
    elif proj['name'] == 'Finways':
        svg += f'<circle cx="760" cy="110" r="6" stroke="{PALETTE["accent1"]}" fill="none"/><circle cx="820" cy="90" r="6" stroke="{PALETTE["accent2"]}" fill="none"/><circle cx="880" cy="110" r="6" stroke="{PALETTE["accent3"]}" fill="none"/><circle cx="820" cy="130" r="6" stroke="{PALETTE["muted"]}" fill="none"/>'
        svg += f'<line x1="766" y1="108" x2="814" y2="92" stroke="{PALETTE["accent1"]}"><animate attributeName="stroke-dasharray" values="0,80;80,0" dur="3s" repeatCount="indefinite"/></line>'
    svg += svg_end()
    return svg

def gen_build_loop():
    w,h = 1000, 240
    svg = svg_start(w,h,'build-loop')
    svg += text_to_paths('How I build', 'med', 16, 60, 80, PALETTE['text'])[0]
    nodes = [('Idea',140),('Prototype',340),('Test',540),('Ship',740)]
    for n,x in nodes:
        svg += f'<circle cx="{x}" cy="140" r="28" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += text_to_paths(n, 'jb', 11, x-len(n)*3, 145, PALETTE['text'])[0]
    svg += f'<circle cx="140" cy="140" r="6" fill="{PALETTE["accent3"]}"><animateMotion dur="6s" repeatCount="indefinite" path="M0,0 L200,0 L400,0 L600,0 L600,-100 L-600,-100 L-600,0 Z"/></circle>'
    svg += svg_end()
    return svg

def gen_contact(label):
    w,h = 300, 90
    svg = svg_start(w,h,f'contact-{label.lower()}')
    svg += f'<rect x="20" y="20" width="260" height="50" rx="25" class="border" fill="none"/>'
    svg += text_to_paths(label, 'jb', 13, 40, 48, PALETTE['text'])[0]
    svg += text_to_paths('\u2192', 'jb', 16, 230, 50, PALETTE['accent1'])[0]
    svg += svg_end()
    return svg

def gen_footer():
    w,h = 1000, 120
    svg = svg_start(w,h,'footer')
    svg += f'<path d="M 40 60 Q 200 40 360 60 T 680 60 T 960 60" stroke="{PALETTE["accent1"]}" fill="none" stroke-width="1.5" opacity="0.7"><animate attributeName="d" values="M 40 60 Q 200 40 360 60 T 680 60 T 960 60;M 40 60 Q 200 80 360 60 T 680 60 T 960 60;M 40 60 Q 200 40 360 60 T 680 60 T 960 60" dur="6s" repeatCount="indefinite"/></path>'
    svg += svg_end()
    return svg

def main():
    (ASSETS / 'label-about.svg').write_text(gen_label('label-about', 'ABOUT'))
    (ASSETS / 'label-focus.svg').write_text(gen_label('label-focus', 'FOCUS'))
    (ASSETS / 'label-stack.svg').write_text(gen_label('label-stack', 'TECH STACK'))
    (ASSETS / 'label-projects.svg').write_text(gen_label('label-projects', 'PROJECTS'))
    (ASSETS / 'label-build.svg').write_text(gen_label('label-build', 'BUILD'))
    (ASSETS / 'label-activity.svg').write_text(gen_label('label-activity', 'ACTIVITY'))
    (ASSETS / 'label-contact.svg').write_text(gen_label('label-contact', 'CONTACT'))
    (ASSETS / 'divider.svg').write_text(gen_divider())
    (ASSETS / 'hero.svg').write_text(gen_hero())
    (ASSETS / 'about-terminal.svg').write_text(gen_about())
    (ASSETS / 'focus.svg').write_text(gen_focus())
    (ASSETS / 'stack.svg').write_text(gen_stack())
    for proj in CFG['projects']:
        (ASSETS / proj['file']).write_text(gen_project(proj['file'], proj))
    (ASSETS / 'build-loop.svg').write_text(gen_build_loop())
    if CFG['contacts']['email']['enabled']:
        (ASSETS / 'contact-email.svg').write_text(gen_contact('Email'))
    if CFG['contacts']['youtube']['enabled']:
        (ASSETS / 'contact-youtube.svg').write_text(gen_contact('YouTube'))
    (ASSETS / 'footer.svg').write_text(gen_footer())
    print('done')

if __name__ == '__main__':
    main()
