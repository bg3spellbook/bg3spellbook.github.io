"""
inject_wiki.py  —  Takes wiki_data.json (from fetch_wiki.py) and:
  1. Adds description / range / area / duration / icon fields to every
     spell object inside the embedded `var spells=[...]` JS array in the HTML.
  2. Replaces the siUrl() function with a lookup from the injected icon map.

Run AFTER fetch_wiki.py:
    python inject_wiki.py
"""

import json, re, os
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent   # project root
HTML_FILE  = str(ROOT / 'index.html')
DATA_FILE  = str(ROOT / 'data' / 'wiki_data.json')

# ── load ──────────────────────────────────────────────────
if not os.path.exists(DATA_FILE):
    print(f'ERROR: {DATA_FILE} not found. Run fetch_wiki.py first.')
    exit(1)

wiki = json.load(open(DATA_FILE, encoding='utf-8'))
html = open(HTML_FILE, encoding='utf-8').read()
results = []

# ── 1. Patch the embedded spell array ─────────────────────
# The spells are stored as: var spells=[{...},{...},...];
# We'll locate each spell object by name and inject the new fields.

SPELL_BLOCK_RE = re.compile(r'(var spells\s*=\s*\[)(.*?)(\];)', re.DOTALL)
m = SPELL_BLOCK_RE.search(html)
if not m:
    print('ERROR: could not find var spells=[...] in HTML')
    exit(1)

prefix, body, suffix = m.group(1), m.group(2), m.group(3)

# Parse each spell JSON object — they're separated by "},{"
# Use Python json to safely decode the full array
try:
    raw_json = '[' + body.strip().rstrip(',') + ']'
    spells = json.loads(raw_json)
except Exception as e:
    print(f'ERROR parsing spell array: {e}')
    exit(1)

patched = 0
for sp in spells:
    name = sp.get('name','')
    if name in wiki:
        w = wiki[name]
        if w.get('description'):
            sp['description'] = w['description']
        if w.get('range'):
            sp['range'] = w['range']
        if w.get('area'):
            sp['area'] = w['area']
        if w.get('duration'):
            sp['duration'] = w['duration']
        if w.get('recharge'):
            sp['recharge'] = w['recharge']
        if w.get('icon'):
            sp['wiki_icon'] = w['icon']
        # Component flags: inject as booleans only when the wiki page had data.
        # verbal=False is meaningful (castable while Silenced), so we use explicit
        # None-check rather than falsy-check.
        if w.get('verbal') is not None:
            sp['verbal']   = w['verbal']
        if w.get('somatic') is not None:
            sp['somatic']  = w['somatic']
        if w.get('material') is not None:
            sp['material'] = w['material']
        patched += 1

results.append(f'[spells] Patched {patched} / {len(spells)} spells with wiki data')

# Serialize back — compact per-spell, one per line
new_body = ',\n'.join(json.dumps(sp, ensure_ascii=False, separators=(',',':')) for sp in spells)
new_block = prefix + '\n' + new_body + '\n' + suffix
html = html[:m.start()] + new_block + html[m.end():]

# siUrl() in the HTML already uses wikiIconMap + wiki_icon via spIcoUrl().
# No replacement needed here.

# ── write ──────────────────────────────────────────────────
open(HTML_FILE, 'w', encoding='utf-8').write(html)
print('\n'.join(results))
print('\nDone — reload index.html in your browser.')
