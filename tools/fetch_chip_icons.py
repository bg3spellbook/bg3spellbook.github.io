"""
fetch_chip_icons.py  —  Fetches icon URLs for scrolls, items, and features
from bg3.wiki, then injects them into index.html as JS maps.

Run:
    python fetch_chip_icons.py

Output: chip_icons.json  (cache — safe to re-run, skips already-fetched)
        Also injects var scrollIconMap={...}; var itemIconMap={...};
        var featIconMap={...}; into the HTML before the CHIP RENDERERS section.
"""

import json, re, time, os, urllib.request, urllib.parse
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent   # project root
DATA        = ROOT / 'data'
HTML_FILE   = str(ROOT / 'index.html')
NAMES_FILE  = str(DATA / 'chip_names.json')
CACHE_FILE  = str(DATA / 'chip_icons.json')
RATE        = 0.4
UA          = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

try:
    import ssl
    _CTX = ssl.create_default_context()
    _CTX.check_hostname = False
    _CTX.verify_mode    = ssl.CERT_NONE
except Exception:
    _CTX = None

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    kw  = {'timeout': 15}
    if _CTX: kw['context'] = _CTX
    try:
        with urllib.request.urlopen(req, **kw) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception:
        return None

def wiki_url(name):
    slug = urllib.parse.quote(name.replace(' ', '_'), safe='/:')
    return 'https://bg3.wiki/wiki/' + slug

def extract_icon(html, name):
    """
    Extract the item/feature icon from a wiki page.
    Strategy: find the LARGEST thumbnail (by pixel size) that is not a UI/chrome
    icon. The main infobox icon is rendered at ~300px; property/ability icons are
    20-40px, so taking the largest reliably picks the right one.
    Returns the full https URL or '' if not found.
    """
    SKIP = re.compile(
        r'Description_Icon|Rarity_Icon|Scrolls_Icon|Consumables_Icon|'
        r'Weight_Icon|Gold_Icon|Action_Icon|Bonus_Action_Icon|Reaction_Icon|'
        r'Passive_Icon|Toggle_Icon|Equipment_Icon|Weapons_Icon|Armour_Icon|'
        r'Class_\w+_Badge|(?<![A-Za-z])Race_|Up_Arrow|Down_Arrow|No_Icon|'
        r'Condition_Icon|Armour_class_icon_frame|D\d+_Physical|Ico_stats|'
        r'_Difficulty|SEO\.webp|_frame\.|'
        r'_Damage_Icon|Proficiency_Icon|Options_Icon|Recharge_Icons|'
        r'Repair_Icon|Misc_Coin_Icon|Tutorial_Icon|Alert_Icon|'
        r'_Model\.|_Front_Model|_Back_Model|Portrait_|'
        r'Dyes\.|poweredby',
        re.IGNORECASE
    )
    # Find all thumbnail src attributes with their pixel sizes
    # Format: /w/images/thumb/H/HH/Filename.ext/NNpx-Filename.ext(.webp)
    thumbs = re.findall(
        r'/w/images/thumb/([a-f0-9]/[a-f0-9]{2}/([^/]+\.(png|webp)))/(\d+)px-',
        html, re.IGNORECASE
    )

    # Collect candidates: deduplicate by filename, keep max pixel size
    best = {}  # filename -> (px, path)
    for path, filename, ext, px in thumbs:
        if SKIP.search(filename):
            continue
        px = int(px)
        if filename not in best or px > best[filename][0]:
            best[filename] = (px, path)

    if not best:
        return ''

    # Return the URL of the largest thumbnail
    _, path = max(best.values(), key=lambda x: x[0])
    return 'https://bg3.wiki/w/images/' + path

# ── load names and cache ──────────────────────────────────────────
names_data = json.load(open(NAMES_FILE, encoding='utf-8-sig'))
scrolls  = names_data.get('scrolls', [])
items    = names_data.get('items', [])
features = names_data.get('features', [])

cache = {}
if os.path.exists(CACHE_FILE):
    cache = json.load(open(CACHE_FILE, encoding='utf-8'))

all_names = [('scroll', n) for n in scrolls] + \
            [('item',   n) for n in items]   + \
            [('feat',   n) for n in features]

todo = [(t, n) for t, n in all_names if n not in cache]
print(f'Total: {len(all_names)}  Cached: {len(all_names)-len(todo)}  To fetch: {len(todo)}')

for i, (typ, name) in enumerate(todo):
    print(f'[{i+1:3}/{len(todo)}] {name[:50]:50}', end=' ', flush=True)
    html = fetch(wiki_url(name))
    if not html:
        print('FAILED')
        cache[name] = ''
    else:
        icon = extract_icon(html, name)
        cache[name] = icon
        print('ok' + (f'  {icon[30:70]}' if icon else '  [no icon]'))
    json.dump(cache, open(CACHE_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    time.sleep(RATE)

# ── build maps ────────────────────────────────────────────────────
scroll_map = {n: cache[n] for n in scrolls  if cache.get(n)}
item_map   = {n: cache[n] for n in items    if cache.get(n)}
feat_map   = {n: cache[n] for n in features if cache.get(n)}

print(f'\nScrolls with icons : {len(scroll_map)} / {len(scrolls)}')
print(f'Items with icons   : {len(item_map)} / {len(items)}')
print(f'Features with icons: {len(feat_map)} / {len(features)}')

# ── inject into HTML ─────────────────────────────────────────────
html = open(HTML_FILE, encoding='utf-8').read()

new_maps = (
    'var scrollIconMap=' + json.dumps(scroll_map, ensure_ascii=False, separators=(',',':')) + ';\n'
    'var itemIconMap='   + json.dumps(item_map,   ensure_ascii=False, separators=(',',':')) + ';\n'
    'var featIconMap='   + json.dumps(feat_map,   ensure_ascii=False, separators=(',',':')) + ';'
)

# Replace existing declarations or insert before CHIP RENDERERS
OLD_MAPS_RE = re.compile(
    r'var scrollIconMap=\{[^;]*\};\s*var itemIconMap=\{[^;]*\};\s*var featIconMap=\{[^;]*\};',
    re.DOTALL)
if OLD_MAPS_RE.search(html):
    html = OLD_MAPS_RE.sub(new_maps, html)
    print('Replaced existing icon maps')
else:
    html = html.replace(
        '// ═══════════════════════════════════\n// CHIP RENDERERS',
        new_maps + '\n// ═══════════════════════════════════\n// CHIP RENDERERS',
        1)
    print('Inserted icon maps before CHIP RENDERERS')

open(HTML_FILE, 'w', encoding='utf-8').write(html)
print('Done — reload index.html')
