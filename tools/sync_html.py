"""
sync_html.py  —  Adds spells from current_spells.json that are missing
from the HTML's var spells=[...] array, merging wiki_data.json info.
Does NOT remove any spells already in the HTML.

Run:
    python sync_html.py
"""
import json, re, os
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent   # project root
HTML_FILE   = str(ROOT / 'bg3-spellbook.html')
SPELLS_FILE = str(ROOT / 'data' / 'current_spells.json')
DATA_FILE   = str(ROOT / 'data' / 'wiki_data.json')

html   = open(HTML_FILE,   encoding='utf-8').read()
spells = json.load(open(SPELLS_FILE, encoding='utf-8'))
wiki   = json.load(open(DATA_FILE,   encoding='utf-8')) if os.path.exists(DATA_FILE) else {}

# ── 1. Parse the existing spell array from HTML ───────────────────
BLOCK_RE = re.compile(r'(var spells\s*=\s*\[)(.*?)(\];)', re.DOTALL)
m = BLOCK_RE.search(html)
if not m:
    print('ERROR: var spells=[...] not found'); exit(1)

prefix, body, suffix = m.group(1), m.group(2), m.group(3)

raw_json = '[' + body.strip().rstrip(',') + ']'
try:
    existing = json.loads(raw_json)
except Exception as e:
    print(f'ERROR parsing spell array: {e}'); exit(1)

existing_names = {sp['name'] for sp in existing}
print(f'HTML currently has {len(existing)} spells')

# ── 2. Find spells missing from HTML ─────────────────────────────
to_add = [sp for sp in spells if sp['name'] not in existing_names]
print(f'Adding {len(to_add)} new spells from current_spells.json')

# ── 3. Merge wiki data into new spells ────────────────────────────
for sp in to_add:
    name = sp.get('name', '')
    if name in wiki:
        w = wiki[name]
        if w.get('description') and not sp.get('description'):
            sp['description'] = w['description']
        if w.get('range')    and not sp.get('range'):    sp['range']    = w['range']
        if w.get('area')     and not sp.get('area'):     sp['area']     = w['area']
        if w.get('duration') and not sp.get('duration'): sp['duration'] = w['duration']
        if w.get('recharge') and not sp.get('recharge'): sp['recharge'] = w['recharge']
        if w.get('icon')     and not sp.get('wiki_icon'): sp['wiki_icon'] = w['icon']

# ── 4. Combine and re-serialise ───────────────────────────────────
combined = existing + to_add
new_body = ',\n'.join(
    json.dumps(sp, ensure_ascii=False, separators=(',', ':'))
    for sp in combined
)
new_block = prefix + '\n' + new_body + '\n' + suffix
html = html[:m.start()] + new_block + html[m.end():]

open(HTML_FILE, 'w', encoding='utf-8').write(html)
print(f'Done — HTML now has {len(combined)} spells')
