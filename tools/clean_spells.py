"""
clean_spells.py  —  Two-phase cleanup of dead wiki pages.

Phase 1 (default): checks every spell page, writes checked_spells.json
Phase 2 (--apply):  reads checked_spells.json and removes dead entries
                    from current_spells.json and wiki_data.json

Run:
  C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python312\\python.exe clean_spells.py
  C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python312\\python.exe clean_spells.py --apply
"""

import json, sys, time, os, urllib.request, urllib.error
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).resolve().parent.parent   # project root
DATA         = ROOT / 'data'
SPELLS_FILE  = str(DATA / 'current_spells.json')
DATA_FILE    = str(DATA / 'wiki_data.json')
REMOVED_FILE = str(DATA / 'removed_spells.json')
CHECKED_FILE = str(DATA / 'checked_spells.json')

try:
    import ssl
    _CTX = ssl.create_default_context()
    _CTX.check_hostname = False
    _CTX.verify_mode    = ssl.CERT_NONE
except Exception:
    _CTX = None
RATE         = 0.3
TIMEOUT      = 12
UA           = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

NO_CONTENT_PHRASES = [
    'There is currently no text in this page',
    'noarticletext',
]

def fetch_page(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    kw  = {'timeout': TIMEOUT}
    if _CTX:
        kw['context'] = _CTX
    try:
        with urllib.request.urlopen(req, **kw) as r:
            return r.read().decode('utf-8', errors='replace'), r.status
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception:
        return None, 0

def page_exists(html, status):
    if status == 404:
        return False
    if html is None:
        return None   # network error
    for phrase in NO_CONTENT_PHRASES:
        if phrase in html:
            return False
    return True

def spell_url(sp):
    if sp.get('url'):
        return sp['url']
    import urllib.parse
    slug = sp['name'].replace(' ', '_')
    slug = urllib.parse.quote(slug, safe='/:')
    return 'https://bg3.wiki/wiki/' + slug

# ─────────────────────────────────────────────────────────────────
# PHASE 2: apply removals
# ─────────────────────────────────────────────────────────────────
if '--apply' in sys.argv:
    if not os.path.exists(CHECKED_FILE):
        print('ERROR: checked_spells.json not found. Run phase 1 first.')
        sys.exit(1)

    checked = json.load(open(CHECKED_FILE, encoding='utf-8'))
    spells  = json.load(open(SPELLS_FILE,  encoding='utf-8'))
    wiki    = json.load(open(DATA_FILE,    encoding='utf-8')) if os.path.exists(DATA_FILE) else {}

    dead = [name for name, exists in checked.items() if not exists]
    print(f'Dead pages to remove ({len(dead)}):')
    for n in dead:
        print(f'  - {n}')

    if not dead:
        print('Nothing to remove.')
        sys.exit(0)

    dead_set = set(dead)

    # Save removed spells for reference
    removed_entries = [sp for sp in spells if sp['name'] in dead_set]
    prev_removed    = json.load(open(REMOVED_FILE, encoding='utf-8')) if os.path.exists(REMOVED_FILE) else []
    json.dump(prev_removed + removed_entries,
              open(REMOVED_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    # Remove from current_spells.json
    cleaned = [sp for sp in spells if sp['name'] not in dead_set]
    json.dump(cleaned, open(SPELLS_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    # Remove from wiki_data.json
    for n in dead:
        wiki.pop(n, None)
    json.dump(wiki, open(DATA_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    print(f'\nRemoved {len(dead)} spells from current_spells.json and wiki_data.json.')
    print(f'Backup of removed entries saved to {REMOVED_FILE}.')
    print(f'\nNext step: python fetch_wiki.py  (then inject_wiki.py)')
    sys.exit(0)

# ─────────────────────────────────────────────────────────────────
# PHASE 1: check all pages
# ─────────────────────────────────────────────────────────────────
spells  = json.load(open(SPELLS_FILE, encoding='utf-8'))
checked = json.load(open(CHECKED_FILE, encoding='utf-8')) if os.path.exists(CHECKED_FILE) else {}

to_check = [sp for sp in spells if sp['name'] not in checked]
print(f'Total spells   : {len(spells)}')
print(f'Already checked: {len(checked)}')
print(f'To check now   : {len(to_check)}\n')

if not to_check:
    dead = [n for n, e in checked.items() if not e]
    print(f'All done! Dead pages: {len(dead)}')
    print('Run with --apply to remove them.')
    sys.exit(0)

for i, sp in enumerate(to_check):
    name = sp['name']
    url  = spell_url(sp)
    print(f'[{i+1:3}/{len(to_check)}] {name[:50]:50}', end=' ', flush=True)

    html, status = fetch_page(url)
    exists       = page_exists(html, status)

    if exists is None:
        print(f'NETWORK ERR (status={status}) — will retry next run')
        time.sleep(1.5)
        continue

    checked[name] = exists
    print('ok' if exists else f'DEAD (HTTP {status})')

    json.dump(checked, open(CHECKED_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    time.sleep(RATE)

dead = [n for n, e in checked.items() if not e]
print(f'\n{"="*60}')
print(f'Checked {len(checked)} / {len(spells)} spells')
print(f'Dead pages : {len(dead)}')
if dead:
    for n in dead:
        print(f'  - {n}')
    print(f'\nRun with --apply to remove them from the database.')
else:
    print('All pages exist — nothing to remove.')
