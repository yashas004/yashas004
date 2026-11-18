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
                paths.append(f'<path d="{d}" fill="{fill}" transform="matrix({font_size/1000.0},0,0,-{font_size/1000.0},{cur_x:.1f},{y:.1f})"/>')
            try:
                w = hmtx[gid][0] if gid in hmtx else 500
                cur_x += w * font_size / 1000.0
            except:
                cur_x += font_size * 0.5
        except:
            cur_x += font_size * 0.3
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
@keyframes float{{0%,100%{{transform:translateY(0px);}}50%{{transform:translateY(-6px);}}}}
@keyframes glow{{0%,100%{{opacity:0.4;}}50%{{opacity:0.9;}}}}
@keyframes scan{{0%{{transform:translateY(-120px);}}100%{{transform:translateY(200px);}}}}
@keyframes blink{{0%,49%{{opacity:1;}}50%,100%{{opacity:0;}}}}
@keyframes dash{{to{{stroke-dashoffset:0;}}}}
@keyframes pulse{{0%,100%{{opacity:0.3;}}50%{{opacity:1;}}}}
@media (prefers-reduced-motion: reduce){{
  .anim,.float,.glow,.scan,.blink,.dash,.pulse{{animation:none !important;}}
  animate,animateTransform,animateMotion{{display:none !important;}}
}}
]]></style>
<clipPath id="clip{svgid}"><rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" ry="18"/></clipPath>
<linearGradient id="g{svgid}" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="{PALETTE['accent1']}"><animate attributeName="stop-color" values="{PALETTE['accent1']};{PALETTE['accent2']};{PALETTE['accent1']}" dur="8s" repeatCount="indefinite"/></stop>
<stop offset="100%" stop-color="{PALETTE['accent2']}"><animate attributeName="stop-color" values="{PALETTE['accent2']};{PALETTE['accent1']};{PALETTE['accent2']}" dur="8s" repeatCount="indefinite"/></stop>
</linearGradient>
<filter id="blur{svgid}"><feGaussianBlur stdDeviation="12"/></filter>
</defs>
<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>
<rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" ry="18" class="surface"/>
<rect x="24" y="24" width="{w-48}" height="{h-48}" rx="18" ry="18" class="border" fill="none"/>
<g clip-path="url(#clip{svgid})">
'''

def svg_end():
    return '</g>\n</svg>\n'

def gen_hero():
    w,h = 1000, 380
    svg = svg_start(w,h,'hero')
    # bg glow
    svg += f'<ellipse cx="800" cy="100" rx="200" ry="60" fill="{PALETTE["accent1"]}" opacity="0.08" filter="url(#blurhero)"><animate attributeName="cx" values="800;700;800" dur="12s" repeatCount="indefinite"/></ellipse>'
    svg += f'<ellipse cx="200" cy="300" rx="180" ry="50" fill="{PALETTE["accent2"]}" opacity="0.06" filter="url(#blurhero)"><animate attributeName="cx" values="200;300;200" dur="14s" repeatCount="indefinite"/></ellipse>'
    # name
    svg += text_to_paths(CFG['name'], 'bold', 72, 60, 150, PALETTE['text'])[0]
    # shimmer line
    svg += f'<rect x="60" y="100" width="200" height="80" fill="url(#ghero)" opacity="0.15"><animateTransform attributeName="transform" type="translate" values="-300,0;1200,0" dur="10s" repeatCount="indefinite"/></rect>'
    # terminal
    svg += f'<rect x="60" y="200" width="880" height="120" rx="12" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<circle cx="82" cy="218" r="4" fill="{PALETTE["muted"]}"/><circle cx="98" cy="218" r="4" fill="{PALETTE["muted"]}"/><circle cx="114" cy="218" r="4" fill="{PALETTE["muted"]}"/>'
    svg += text_to_paths('> ', 'jb', 16, 82, 268, PALETTE['accent3'])[0]
    lines = CFG['hero']['terminal_lines']
    for i,l in enumerate(lines):
        svg += f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{0.02+i*0.33:.3f};{0.31+i*0.33:.3f};{0.33+i*0.33:.3f}" dur="12s" repeatCount="indefinite"/>' + text_to_paths(l, 'jb', 16, 102, 268, PALETTE['text'])[0] + '</g>'
    svg += f'<rect x="360" y="254" width="10" height="18" fill="{PALETTE["accent3"]}"><animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/></rect>'
    svg += svg_end()
    return svg

def gen_about():
    w,h = 1000, 300
    svg = svg_start(w,h,'about-terminal')
    svg += f'<rect x="60" y="60" width="880" height="180" rx="12" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<circle cx="82" cy="78" r="4" fill="{PALETTE["muted"]}"/><circle cx="98" cy="78" r="4" fill="{PALETTE["muted"]}"/><circle cx="114" cy="78" r="4" fill="{PALETTE["muted"]}"/>'
    svg += text_to_paths('~/about', 'jb', 11, 500, 82, PALETTE['muted'])[0]
    lines = CFG['about_terminal']['lines']
    y = 120
    for i,l in enumerate(lines):
        svg += f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;{0.015+i*0.11:.3f};{0.86-i*0.005:.3f};0.94" dur="16s" repeatCount="indefinite"/>' + text_to_paths(l, 'jb', 13, 82, y, PALETTE['accent3'] if l.startswith('$') else PALETTE['text'])[0] + '</g>'
        y += 20
    svg += svg_end()
    return svg

def gen_focus():
    w,h = 1000, 320
    svg = svg_start(w,h,'focus')
    focus = CFG['focus']
    # col1
    svg += f'<rect x="60" y="70" width="280" height="200" rx="14" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(focus[0]['title'], 'med', 18, 82, 105, PALETTE['text'])[0]
    svg += text_to_paths(focus[0]['caption'], 'inter', 11, 82, 125, PALETTE['muted'])[0]
    svg += f'<circle cx="200" cy="190" r="12" stroke="{PALETTE["accent1"]}" fill="none"><animate attributeName="r" values="12;14;12" dur="3s" repeatCount="indefinite"/></circle>'
    for ang,rad in [(0,36),(120,36),(240,36)]:
        svg += f'<circle cx="{200+rad*__import__("math").cos(ang*__import__("math").pi/180):.1f}" cy="{190+rad*__import__("math").sin(ang*__import__("math").pi/180):.1f}" r="5" stroke="{PALETTE["accent2"]}" fill="none"/>'
    svg += f'<circle cx="200" cy="190" r="38" stroke="{PALETTE["border"]}" fill="none" stroke-dasharray="4 6"><animateTransform attributeName="transform" type="rotate" from="0 200 190" to="360 200 190" dur="18s" repeatCount="indefinite"/></circle>'
    # col2
    svg += f'<rect x="360" y="70" width="280" height="200" rx="14" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(focus[1]['title'], 'med', 18, 382, 105, PALETTE['text'])[0]
    svg += text_to_paths(focus[1]['caption'], 'inter', 11, 382, 125, PALETTE['muted'])[0]
    svg += f'<rect x="382" y="150" width="236" height="90" rx="6" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += f'<rect x="394" y="162" width="32" height="18" rx="3" stroke="{PALETTE["accent2"]}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;70,0;-20,0" dur="8s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="440" y="182" width="38" height="20" rx="3" stroke="{PALETTE["accent1"]}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;-40,0;30,0" dur="9s" repeatCount="indefinite"/></rect>'
    svg += f'<rect x="410" y="210" width="28" height="16" rx="3" stroke="{PALETTE["accent3"]}" fill="none"><animateTransform attributeName="transform" type="translate" values="0,0;50,0;-10,0" dur="7s" repeatCount="indefinite"/></rect>'
    svg += f'<line x1="382" y1="195" x2="618" y2="195" stroke="{PALETTE["accent3"]}" stroke-width="1" opacity="0.5"><animate attributeName="y1" values="195;185;205;195" dur="4s" repeatCount="indefinite"/><animate attributeName="y2" values="195;185;205;195" dur="4s" repeatCount="indefinite"/></line>'
    # col3
    svg += f'<rect x="660" y="70" width="280" height="200" rx="14" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(focus[2]['title'], 'med', 18, 682, 105, PALETTE['text'])[0]
    svg += text_to_paths(focus[2]['caption'], 'inter', 11, 682, 125, PALETTE['muted'])[0]
    svg += f'<path d="M 682 190 L 730 190 L 750 175 L 790 175 L 810 190 L 920 190" stroke="{PALETTE["accent1"]}" stroke-width="2" fill="none"><animate attributeName="stroke-dasharray" values="0,400;400,0" dur="4s" repeatCount="indefinite"/></path>'
    svg += f'<rect x="850" y="170" width="70" height="36" rx="8" stroke="{PALETTE["border"]}" fill="none"/>'
    for i in range(6):
        svg += f'<rect x="{860+i*8}" y="{180 + (i%2)*4}" width="4" height="16" rx="2" fill="{PALETTE["accent2"]}"><animate attributeName="height" values="6;16;6" dur="1.2s" begin="{i*0.08}s" repeatCount="indefinite"/></rect>'
    svg += svg_end()
    return svg

def gen_stack():
    w,h = 1000, 280
    svg = svg_start(w,h,'stack')
    rows = CFG['stack']['rows']
    y = 90
    for r,row in enumerate(rows):
        cx = 60
        for item in row:
            witem = len(item)*7 + 36
            svg += f'<rect x="{cx}" y="{y-12}" width="{witem}" height="24" rx="12" stroke="{PALETTE["border"]}" fill="none"/>'
            svg += f'<circle cx="{cx+14}" cy="{y}" r="3" fill="{PALETTE["accent1"] if r==0 else PALETTE["accent2"] if r==1 else PALETTE["accent3"]}"/>'
            svg += text_to_paths(item, 'jb', 11, cx+26, y+4, PALETTE['text'])[0]
            cx += witem + 14
        y += 60
    svg += svg_end()
    return svg

def gen_project(fname, proj):
    w,h = 1000, 240
    svg = svg_start(w,h,fname.replace('.svg',''))
    svg += f'<rect x="60" y="40" width="880" height="160" rx="16" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(proj['name'], 'bold', 30, 90, 90, PALETTE['text'])[0]
    if proj.get('chip'):
        cw = len(proj['chip'])*6 + 22
        svg += f'<rect x="{90 + len(proj["name"])*15 + 24}" y="74" width="{cw}" height="20" rx="10" stroke="{PALETTE["accent3"]}" fill="none"/>'
        svg += text_to_paths(proj['chip'], 'jb', 9, 90 + len(proj["name"])*15 + 34, 86, PALETTE['accent3'])[0]
    svg += text_to_paths(proj['desc'], 'inter', 13, 90, 120, PALETTE['text'])[0]
    cx = 90; cy = 165
    for tag in proj['tags']:
        tw = len(tag)*6 + 20
        svg += f'<rect x="{cx}" y="{cy-10}" width="{tw}" height="22" rx="11" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += text_to_paths(tag, 'jb', 10, cx+12, cy+4, PALETTE['muted'])[0]
        cx += tw + 10
    if proj['name'] == 'Persona.AI':
        for i in range(6):
            svg += f'<rect x="{800+i*10}" y="{110 + (3-i%4)*3}" width="6" height="{12+i*2}" rx="3" fill="{PALETTE["accent1"]}"><animate attributeName="height" values="{8+i};{18+i};{8+i}" dur="1.4s" begin="{i*0.08}s" repeatCount="indefinite"/></rect>'
    elif proj['name'] == 'PriorAuth':
        svg += f'<rect x="800" y="90" width="42" height="52" rx="6" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += f'<circle cx="870" cy="98" r="9" stroke="{PALETTE["accent1"]}" fill="none"/><circle cx="910" cy="116" r="9" stroke="{PALETTE["accent2"]}" fill="none"/><circle cx="870" cy="134" r="9" stroke="{PALETTE["accent3"]}" fill="none"/>'
        svg += f'<polyline points="865,134 870,139 879,130" stroke="{PALETTE["accent3"]}" fill="none" stroke-width="1.5"><animate attributeName="stroke-dasharray" values="0,16;16,0" dur="2s" repeatCount="indefinite"/></polyline>'
    elif proj['name'] == 'SecureWays':
        svg += f'<rect x="780" y="100" width="150" height="70" rx="6" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += f'<rect x="790" y="110" width="26" height="16" rx="3" stroke="{PALETTE["accent1"]}"><animateTransform attributeName="transform" type="translate" values="0,0;80,0;-10,0" dur="8s" repeatCount="indefinite"/></rect>'
        svg += f'<rect x="840" y="130" width="32" height="18" rx="3" stroke="{PALETTE["accent2"]}"><animateTransform attributeName="transform" type="translate" values="0,0;-40,0;40,0" dur="9s" repeatCount="indefinite"/></rect>'
        svg += f'<rect x="810" y="125" width="30" height="17" rx="3" stroke="{PALETTE["accent3"]}" opacity="0.7"><animate attributeName="opacity" values="0.2;0.9;0.2" dur="3s" repeatCount="indefinite"/></rect>'
    elif proj['name'] == 'Finways':
        svg += f'<circle cx="800" cy="120" r="7" stroke="{PALETTE["accent1"]}" fill="none"/><circle cx="860" cy="100" r="7" stroke="{PALETTE["accent2"]}" fill="none"/><circle cx="920" cy="120" r="7" stroke="{PALETTE["accent3"]}" fill="none"/><circle cx="860" cy="140" r="7" stroke="{PALETTE["muted"]}" fill="none"/>'
        svg += f'<line x1="807" y1="118" x2="853" y2="102" stroke="{PALETTE["accent1"]}" stroke-width="1.5"><animate attributeName="stroke-dasharray" values="0,70;70,0" dur="3s" repeatCount="indefinite"/></line>'
        svg += f'<line x1="867" y1="102" x2="913" y2="118" stroke="{PALETTE["accent2"]}" stroke-width="1.5"><animate attributeName="stroke-dasharray" values="0,70;70,0" dur="3.2s" repeatCount="indefinite"/></line>'
    svg += svg_end()
    return svg

def gen_build():
    w,h = 1000, 220
    svg = svg_start(w,h,'build-loop')
    svg += text_to_paths('build loop', 'med', 16, 60, 80, PALETTE['muted'])[0]
    nodes = [('Idea',170),('Prototype',380),('Test',590),('Ship',800)]
    for n,x in nodes:
        svg += f'<circle cx="{x}" cy="130" r="30" stroke="{PALETTE["border"]}" fill="none"/>'
        svg += text_to_paths(n, 'jb', 11, x-len(n)*3, 135, PALETTE['text'])[0]
    svg += f'<circle cx="170" cy="130" r="6" fill="{PALETTE["accent3"]}"><animateMotion dur="7s" repeatCount="indefinite" path="M0,0 L210,0 L420,0 L630,0 L630,-70 L-630,-70 L-630,0 Z"/></circle>'
    svg += svg_end()
    return svg

def gen_contact(label):
    w,h = 320, 90
    svg = svg_start(w,h,f'contact-{label.lower()}')
    svg += f'<rect x="30" y="20" width="260" height="50" rx="25" stroke="{PALETTE["border"]}" fill="none"/>'
    svg += text_to_paths(label, 'jb', 13, 52, 48, PALETTE['text'])[0]
    svg += text_to_paths('\u2192', 'jb', 16, 258, 50, PALETTE['accent1'])[0]
    svg += svg_end()
    return svg

def gen_footer():
    w,h = 1000, 110
    svg = svg_start(w,h,'footer')
    svg += f'<path d="M 50 60 Q 250 40 450 60 T 850 60 T 950 60" stroke="url(#gfooter)" stroke-width="2" fill="none" opacity="0.8"><animate attributeName="d" values="M 50 60 Q 250 40 450 60 T 850 60 T 950 60;M 50 60 Q 250 75 450 60 T 850 60 T 950 60;M 50 60 Q 250 40 450 60 T 850 60 T 950 60" dur="8s" repeatCount="indefinite"/></path>'
    svg += svg_end()
    return svg

def main():
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
    print('done')

if __name__ == '__main__':
    main()
