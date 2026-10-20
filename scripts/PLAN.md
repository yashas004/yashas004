STAGE 0 PLAN

Palette
- background: #0A0E1A
- surface: #111827
- border: #1F2937
- text: #E5E7EB
- muted: #94A3B8
- accents: #38BDF8, #A78BFA, #34D399

Font roles
- Space Grotesk Bold: name and big headings
- Space Grotesk Medium: card titles
- JetBrains Mono: terminal text, tags, labels, code-like
- Inter: descriptive sentences

Page order (ASCII wireframe)
┌─────────────────────────────────────────────────────────────┐
│ HERO (assets/hero.svg)                                        │
├─────────────────────────────────────────────────────────────┤
│ ABOUT TERMINAL (assets/about-terminal.svg)                   │
├─────────────────────────────────────────────────────────────┤
│ FOCUS (assets/focus.svg)                                      │
├─────────────────────────────────────────────────────────────┤
│ TECH STACK (assets/stack.svg)                                  │
├─────────────────────────────────────────────────────────────┤
│ PROJECTS (assets/projects/*.svg or stacked cards)            │
│  - Persona.AI                                                │
│  - PriorAuth                                                 │
│  - SecureWays                                                │
│  - Finways                                                   │
├─────────────────────────────────────────────────────────────┤
│ BUILD LOOP (assets/build-loop.svg)                           │
├─────────────────────────────────────────────────────────────┤
│ ACTIVITY (snake via picture element)                         │
├─────────────────────────────────────────────────────────────┤
│ CONTACT (assets/contact-*.svg pills) + FOOTER (assets/footer.svg)
└─────────────────────────────────────────────────────────────┘

File list
- scripts/forbidden.txt (git-ignored)
- scripts/FONTS.md
- scripts/build.py (driven by scripts/config.json)
- scripts/validate.py
- scripts/PLAN.md (git-ignored)
- scripts/venv/ (git-ignored)
- scripts/.fonts/ (git-ignored)
- assets/hero.svg
- assets/label-*.svg (section labels)
- assets/divider.svg
- assets/about-terminal.svg
- assets/focus.svg
- assets/stack.svg
- assets/project-persona.svg
- assets/project-priorauth.svg
- assets/project-secureways.svg
- assets/project-finways.svg
- assets/build-loop.svg
- assets/contact-email.svg
- assets/contact-youtube.svg
- assets/footer.svg
- .github/workflows/snake.yml (updated)
- README.md
- preview/index.html

Storyboard (timings)
- Hero: name shimmer ~8s loop; terminal typing/cycle 12s loop 2.5s hold; packet motion subtle 6-10s; hexagon rotate slow; bars light up sequence
- About terminal: type lines sequentially, hold ~16s total loop
- Focus: hub pulse 2-3s, ring rotate slow; road vehicles move 6-8s, boxes snap, scan line sweep 4-6s; waveform+bubble 4-6s
- Stack: three rows marquee alternating dirs different speeds 12-18s seamless
- Projects: per card unique subtle motion 6-10s
- Build loop: dot travels loop 6-8s, nodes highlight in order
- Contact pills: arrow nudge idle 3-4s
- Footer: waveform glide 6-8s
All use cubic-bezier(.22,1,.36,1), staggers 80-150ms, prefers-reduced-motion disables animation.

Rules enforced: text outlined (paths), no font-family, no external URLs except xmlns, no script/foreignObject, fit checks, <150KB each.
