"""
clear_party.py  —  Strips party-member columns and resets 'used' counts from
the embedded spell array in index.html, so the app ships with a clean slate.

Standard spell fields (everything else is a character column):
  name url school level classes races features items scrolls
  used cost save attack_roll concentration ritual conditions tags
  description range area duration recharge wiki_icon damage_types
"""

import json, re
from pathlib import Path

ROOT      = Path(__file__).resolve().parent.parent
HTML_FILE = str(ROOT / 'index.html')

STANDARD_FIELDS = {
    'name','url','school','level','classes','races','features','items','scrolls',
    'used','cost','save','attack_roll','concentration','ritual','conditions','tags',
    'description','range','area','duration','recharge','wiki_icon','damage_types',
    'parent',  # variant parent reference
}

html = open(HTML_FILE, encoding='utf-8').read()

# Locate the var spells=[...] block
BLOCK_RE = re.compile(r'(var spells\s*=\s*\[)(.*?)(\];)', re.DOTALL)
m = BLOCK_RE.search(html)
if not m:
    print('ERROR: var spells=[...] not found'); exit(1)

prefix, body, suffix = m.group(1), m.group(2), m.group(3)
raw_json = '[' + body.strip().rstrip(',') + ']'
spells = json.loads(raw_json)
print(f'Loaded {len(spells)} spells')

removed_keys = set()
for sp in spells:
    # Reset usage counter
    sp['used'] = 0
    # Remove all character-column keys
    for k in list(sp.keys()):
        if k not in STANDARD_FIELDS:
            removed_keys.add(k)
            del sp[k]

print(f'Removed character columns: {sorted(removed_keys)}')
print(f'Reset "used" to 0 on all spells')

# Re-serialize
new_body = ',\n'.join(
    json.dumps(sp, ensure_ascii=False, separators=(',', ':'))
    for sp in spells
)
new_block = prefix + '\n' + new_body + '\n' + suffix
html = html[:m.start()] + new_block + html[m.end():]

open(HTML_FILE, 'w', encoding='utf-8').write(html)
print(f'Done — index.html updated ({len(spells)} spells, no party data)')
