import os
import re
import sys
from pathlib import Path

ROOT = Path('.')
forbidden_file = ROOT / 'scripts' / 'forbidden.txt'
forbidden = []
if forbidden_file.exists():
    for l in forbidden_file.read_text().splitlines():
        l = l.strip()
        if l:
            forbidden.append(re.compile(re.escape(l), re.IGNORECASE))

def check_forbidden(text, path):
    for pat in forbidden:
        if pat.search(text):
            raise SystemExit(f"forbidden word found in {path}: {pat.pattern}")

def check_xml(path):
    try:
        import xml.etree.ElementTree as ET
        ET.parse(path)
    except Exception as e:
        raise SystemExit(f"XML malformed in {path}: {e}")

def check_svg(path):
    t = path.read_text(errors='ignore')
    check_forbidden(t, path)
    if 'font-family' in t:
        raise SystemExit(f"font-family found in {path}")
    if '<script' in t:
        raise SystemExit(f"script in {path}")
    if 'foreignObject' in t:
        raise SystemExit(f"foreignObject in {path}")
    if '—' in t or '–' in t:
        raise SystemExit(f"em dash in {path}")
    if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]', t):
        raise SystemExit(f"emoji in {path}")
    # check reduced motion
    if '@media (prefers-reduced-motion: reduce)' not in t:
        raise SystemExit(f"missing reduced motion in {path}")
    sz = path.stat().st_size
    if sz > 150*1024:
        raise SystemExit(f"too large {path} {sz}")

def check_text(path):
    t = path.read_text(errors='ignore')
    check_forbidden(t, path)
    if '—' in t or '–' in t:
        raise SystemExit(f"em dash in {path}")
    if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]', t):
        raise SystemExit(f"emoji in {path}")

# check files
for p in ROOT.rglob('*.svg'):
    if str(p).startswith('scripts/venv/'): continue
    if str(p).startswith('node_modules/'): continue
    check_xml(p)
    check_svg(p)

for ext in ['*.md','*.json','*.yml','*.yaml']:
    for p in ROOT.rglob(ext):
        if str(p).startswith('scripts/venv/'): continue
        if str(p).startswith('node_modules/'): continue
        if p.name == 'forbidden.txt': continue
        check_text(p)

print('ok')
