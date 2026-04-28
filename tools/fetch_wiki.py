"""
fetch_wiki.py  —  Scrapes bg3.wiki for each spell:
  description, range, area of effect, duration, recharge, icon URL.

If you get an SSL DLL error, run with the non-Anaconda Python:
  C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python312\\python.exe fetch_wiki.py

Output : wiki_data.json
Resume : safe to re-run — already-fetched spells are skipped.
         Entries where ALL fields are empty (previous FAILED fetches)
         are automatically re-fetched.
"""

import json, re, time, os, urllib.request
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent   # project root
DATA        = ROOT / 'data'
DATA_FILE   = str(DATA / 'wiki_data.json')
SPELLS_FILE = str(DATA / 'current_spells.json')

# ── SSL: graceful fallback if Anaconda's _ssl DLL is broken ──────
try:
    import ssl
    _CTX = ssl.create_default_context()
    _CTX.check_hostname = False
    _CTX.verify_mode    = ssl.CERT_NONE
except Exception:
    _CTX = None
RATE        = 1.0
RETRIES     = 3
UA          = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# ── fetch with retry ─────────────────────────────────────────────
def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for attempt in range(RETRIES):
        try:
            kw = {'timeout': 18}
            if _CTX:
                kw['context'] = _CTX
            with urllib.request.urlopen(req, **kw) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt < RETRIES - 1:
                time.sleep(1.5)
    return None

# ── check if a cached entry is a previous failed fetch ───────────
def is_empty(entry):
    """True if ALL data fields are blank, OR if the entry was fetched with
    an older version of the script that didn't extract 'recharge'."""
    all_blank = not any([
        entry.get('description'),
        entry.get('range'),
        entry.get('area'),
        entry.get('duration'),
        entry.get('recharge'),
        entry.get('icon'),
    ])
    missing_recharge_key = 'recharge' not in entry
    return all_blank or missing_recharge_key

# ── parse one wiki page ──────────────────────────────────────────
def parse_page(html, name):
    result = {
        'description': '',
        'range':       '',
        'area':        '',
        'duration':    '',
        'recharge':    '',
        'icon':        '',
    }

    # ── Description ─────────────────────────────────────────────
    # Primary: <meta name="description"> — always clean on bg3.wiki
    m = re.search(r'<meta name="description" content="([^"]{20,})"', html)
    if m:
        result['description'] = re.sub(r'\s{2,}', ' ', m.group(1)).strip()

    # Fallback: first <p> inside mw-parser-output that has real text
    if not result['description']:
        p_m = re.search(
            r'class="mw-parser-output"[^>]*>.*?<p>(.*?)</p>',
            html, re.DOTALL)
        if p_m:
            text = re.sub(r'<[^>]+>', '', p_m.group(1))
            text = re.sub(r'\s{2,}', ' ', text).strip()
            if len(text) > 20:
                result['description'] = text

    # ── Icon ─────────────────────────────────────────────────────
    # Look for full-size image: src="/w/images/<h>/<hh>/SpellName_Icon.webp"
    import urllib.parse
    slug_re = re.escape(urllib.parse.quote(name.replace(' ', '_'), safe='/:'))
    icon_m = re.search(
        r'src="(/w/images/[a-f0-9]/[a-f0-9]{2}/'
        + slug_re
        + r'_(?:Unfaded_)?Icon\.(?:png|webp))(?:\?[^"]*)?"',
        html, re.IGNORECASE)
    if icon_m:
        result['icon'] = 'https://bg3.wiki' + icon_m.group(1)

    # ── Properties from alt="Key: Value" ────────────────────────
    for pat, key in [
        (r'alt="Range:\s*([^"]{2,80})"',          'range'),
        (r'alt="AoE:\s*([^"]{2,80})"',             'area'),
        (r'alt="Area of Effect:\s*([^"]{2,80})"',  'area'),
        (r'alt="Duration:\s*([^"]{2,80})"',        'duration'),
        (r'alt="Recharge:\s*([^"]{2,80})"',        'recharge'),
    ]:
        am = re.search(pat, html, re.IGNORECASE)
        if am and not result[key]:
            result[key] = am.group(1).strip()

    return result

# ── main ─────────────────────────────────────────────────────────
def main():
    spells  = json.load(open(SPELLS_FILE, encoding='utf-8'))
    import urllib.parse
    def to_url(sp):
        if sp.get('url'):
            return sp['url']
        slug = sp['name'].replace(' ', '_')
        return 'https://bg3.wiki/wiki/' + urllib.parse.quote(slug, safe='/:')
    url_map = {sp['name']: to_url(sp) for sp in spells}

    cache = {}
    if os.path.exists(DATA_FILE):
        cache = json.load(open(DATA_FILE, encoding='utf-8'))

    # Re-fetch spells not cached OR previously failed (all fields empty)
    todo = [
        sp['name'] for sp in spells
        if sp['name'] not in cache or is_empty(cache[sp['name']])
    ]

    cached_ok = len(spells) - len(todo)
    print(f'Total: {len(spells)}  |  Cached OK: {cached_ok}  |  To fetch: {len(todo)}\n')

    if not todo:
        print('Nothing to fetch — run inject_wiki.py')
        return

    failed = []
    for i, name in enumerate(todo):
        print(f'[{i+1:3}/{len(todo)}] {name[:44]:44}', end=' ', flush=True)
        html = fetch(url_map[name])
        if not html:
            print('FAILED')
            failed.append(name)
            # Keep blank entry so we know it was attempted
            cache[name] = {
                'description': '', 'range': '', 'area': '',
                'duration': '', 'recharge': '', 'icon': '',
            }
        else:
            data = parse_page(html, name)
            cache[name] = data
            tags = []
            if data['description']:  tags.append('desc')
            if data['range']:        tags.append(f"r={data['range'][:12]}")
            if data['area']:         tags.append(f"aoe={data['area'][:12]}")
            if data['recharge']:     tags.append(f"rc={data['recharge'][:12]}")
            if data['icon']:         tags.append('icon✓')
            print('ok' + (f'  [{", ".join(tags)}]' if tags else '  [no data]'))

        # Save after every spell — safe to Ctrl+C and resume
        json.dump(cache, open(DATA_FILE, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        time.sleep(RATE)

    print(f'\n{"="*60}')
    print(f'Done. {len(cache)} spells in {DATA_FILE}')
    if failed:
        print(f'Failed ({len(failed)}): ' + ', '.join(failed[:12])
              + ('…' if len(failed) > 12 else ''))
    print('Next step:  python inject_wiki.py')

if __name__ == '__main__':
    main()
