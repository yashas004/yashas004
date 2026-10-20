#!/usr/bin/env python3
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
CFG = json.loads((Path(__file__).parent / "config.json").read_text())

def svg_open(w=1200, h=200, idp=""):
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title{ idp } desc{ idp }">
<title id="title{ idp }">{CFG["name"]}</title>
<desc id="desc{ idp }">Animated profile graphic</desc>
<defs>
<style><![CDATA[
:root{{}}
@media (prefers-color-scheme: light){{
  .bg{{fill:{CFG["colors"]["light"]["bg"]};}}
  .surface{{fill:{CFG["colors"]["light"]["surface"]};stroke:{CFG["colors"]["light"]["border"]};}}
  .text{{fill:{CFG["colors"]["light"]["text"]};}}
  .text2{{fill:{CFG["colors"]["light"]["text2"]};}}
  .accent1{{fill:{CFG["colors"]["light"]["accent1"]};}}
  .accent2{{fill:{CFG["colors"]["light"]["accent2"]};}}
  .accent3{{fill:{CFG["colors"]["light"]["accent3"]};}}
  .grid{{stroke:{CFG["colors"]["light"]["grid"]};}}
  .wave{{stroke:{CFG["colors"]["light"]["accent1"]};}}
}}
@media (prefers-color-scheme: dark){{
  .bg{{fill:{CFG["colors"]["dark"]["bg"]};}}
  .surface{{fill:{CFG["colors"]["dark"]["surface"]};stroke:{CFG["colors"]["dark"]["border"]};}}
  .text{{fill:{CFG["colors"]["dark"]["text"]};}}
  .text2{{fill:{CFG["colors"]["dark"]["text2"]};}}
  .accent1{{fill:{CFG["colors"]["dark"]["accent1"]};}}
  .accent2{{fill:{CFG["colors"]["dark"]["accent2"]};}}
  .accent3{{fill:{CFG["colors"]["dark"]["accent3"]};}}
  .grid{{stroke:{CFG["colors"]["dark"]["grid"]};}}
  .wave{{stroke:{CFG["colors"]["dark"]["accent1"]};}}
}}
@media (prefers-reduced-motion: reduce){{
  .anim, .marquee, .fadein, .typing {{ animation: none !important; }}
  animate, animateTransform, animateMotion {{ display: none !important; }}
}}
]]></style>
</defs>
<rect width="100%" height="100%" class="bg"/>
'''

def svg_close():
    return "</svg>\n"

# Header banner
def gen_header():
    w,h = 1200, 220
    roles = CFG["roles"]
    svg = svg_open(w,h,"header")
    # animated grid
    svg += '''<g class="grid" opacity="0.5">
<line x1="0" y1="40" x2="1200" y2="40"><animate attributeName="opacity" values="0.3;0.6;0.3" dur="6s" repeatCount="indefinite"/></line>
<line x1="0" y1="90" x2="1200" y2="90"><animate attributeName="opacity" values="0.3;0.5;0.3" dur="7s" repeatCount="indefinite"/></line>
<line x1="0" y1="140" x2="1200" y2="140"><animate attributeName="opacity" values="0.3;0.6;0.3" dur="8s" repeatCount="indefinite"/></line>
</g>
'''
    # gradient blobs
    svg += '''<g opacity="0.15">
<ellipse cx="200" cy="60" rx="120" ry="40" class="accent2"><animate attributeName="cx" values="200;250;200" dur="10s" repeatCount="indefinite"/></ellipse>
<ellipse cx="900" cy="40" rx="100" ry="30" class="accent3"><animate attributeName="cx" values="900;850;900" dur="12s" repeatCount="indefinite"/></ellipse>
<ellipse cx="600" cy="160" rx="140" ry="35" class="accent1"><animate attributeName="cy" values="160;140;160" dur="9s" repeatCount="indefinite"/></ellipse>
</g>
'''
    # name
    svg += f'''<text x="60" y="90" font-size="42" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text" font-weight="600">{CFG["name"]}</text>
'''
    # typing effect - show roles in sequence
    y = 140
    svg += f'''<text x="60" y="{y}" font-size="20" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2" opacity="0">{roles[0]}
<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.28;0.33" dur="12s" begin="0s" repeatCount="indefinite"/>
</text>
<text x="60" y="{y}" font-size="20" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2" opacity="0">{roles[1]}
<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.33;0.61;0.66" dur="12s" begin="0s" repeatCount="indefinite"/>
</text>
<text x="60" y="{y}" font-size="20" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2" opacity="0">{roles[2]}
<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.66;0.95;1.0" dur="12s" begin="0s" repeatCount="indefinite"/>
</text>
'''
    svg += svg_close()
    return svg

# Focus cards
def gen_focus():
    w,h = 1200, 240
    svg = svg_open(w,h,"focus")
    cards = CFG["focus"]
    positions = [(60,40),(420,40),(780,40)]
    for i,(card,(x,y)) in enumerate(zip(cards, positions)):
        delay = i * 0.25
        svg += f'''<g opacity="0">
<rect x="{x}" y="{y}" width="340" height="160" rx="12" class="surface" stroke-width="1"/>
<text x="{x+24}" y="{y+40}" font-size="18" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text" font-weight="600">{card["title"]}</text>
<text x="{x+24}" y="{y+72}" font-size="14" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2">{card["desc"][:60]}</text>
<animate attributeName="opacity" values="0;1" dur="0.6s" begin="{delay}s" fill="freeze"/>
<animateTransform attributeName="transform" type="translate" values="0,10;0,0" dur="0.6s" begin="{delay}s" fill="freeze"/>
</g>
'''
    svg += svg_close()
    return svg

# Tech marquee
def gen_tech():
    w,h = 1200, 120
    svg = svg_open(w,h,"tech")
    tech = CFG["tech"]
    text = "  •  ".join(tech)
    # duplicated for seamless loop
    full = text + "  •  " + text
    svg += f'''<g class="marquee">
<text x="0" y="70" font-size="16" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2" letter-spacing="0.5">{full}
<animateTransform attributeName="transform" type="translate" values="0,0;-2000,0" dur="40s" repeatCount="indefinite"/>
</text>
</g>
'''
    svg += svg_close()
    return svg

# Projects cards
def gen_projects():
    w,h = 1200, 520
    svg = svg_open(w,h,"projects")
    projs = CFG["projects"]
    positions = [(60,40),(620,40),(60,280),(620,280)]
    for i,(proj,(x,y)) in enumerate(zip(projs, positions)):
        delay = i * 0.15
        tags = " • ".join(proj["tags"])
        # clickable card represented by group; actual links in README wrap
        svg += f'''<g opacity="0">
<rect x="{x}" y="{y}" width="520" height="200" rx="12" class="surface" stroke-width="1"/>
<text x="{x+24}" y="{y+40}" font-size="18" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text" font-weight="600">{proj["name"]}</text>
<text x="{x+24}" y="{y+72}" font-size="13" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2">{proj["desc"][:90]}</text>
<text x="{x+24}" y="{y+140}" font-size="12" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="accent1">{tags}</text>
<text x="{x+24}" y="{y+170}" font-size="11" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2">View repository</text>
<animate attributeName="opacity" values="0;1" dur="0.5s" begin="{delay}s" fill="freeze"/>
<animateTransform attributeName="transform" type="translate" values="0,8;0,0" dur="0.5s" begin="{delay}s" fill="freeze"/>
</g>
'''
    svg += svg_close()
    return svg

# Footer wave
def gen_footer():
    w,h = 1200, 140
    svg = svg_open(w,h,"footer")
    svg += '''<path d="M0 80 Q 150 40 300 80 T 600 80 T 900 80 T 1200 80 L 1200 140 L 0 140 Z" class="wave" fill="none" stroke-width="2" opacity="0.7">
<animate attributeName="d" 
  values="M0 80 Q 150 40 300 80 T 600 80 T 900 80 T 1200 80 L 1200 140 L 0 140 Z;
          M0 80 Q 150 60 300 80 T 600 80 T 900 80 T 1200 80 L 1200 140 L 0 140 Z;
          M0 80 Q 150 40 300 80 T 600 80 T 900 80 T 1200 80 L 1200 140 L 0 140 Z" 
  dur="8s" repeatCount="indefinite"/>
</path>
<text x="60" y="110" font-size="12" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" class="text2">Built with locally generated SVGs</text>
'''
    svg += svg_close()
    return svg

def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "header-banner-light.svg").write_text(gen_header())
    (assets / "header-banner-dark.svg").write_text(gen_header())
    (assets / "focus-cards-light.svg").write_text(gen_focus())
    (assets / "focus-cards-dark.svg").write_text(gen_focus())
    (assets / "tech-marquee-light.svg").write_text(gen_tech())
    (assets / "tech-marquee-dark.svg").write_text(gen_tech())
    (assets / "projects-cards-light.svg").write_text(gen_projects())
    (assets / "projects-cards-dark.svg").write_text(gen_projects())
    (assets / "footer-wave-light.svg").write_text(gen_footer())
    (assets / "footer-wave-dark.svg").write_text(gen_footer())
    print("Generated SVGs")

if __name__ == "__main__":
    main()
