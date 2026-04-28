"""
compute_icons.py  —  Computes bg3.wiki CDN icon URLs for every spell using
MediaWiki's MD5-based path formula.  No HTTP requests needed.

Formula:
  filename = SpellName_Icon.webp  (spaces → underscores)
  md5_hex  = md5(filename)        ← exact case, no lowercasing
  url      = https://bg3.wiki/w/images/<md5[0]>/<md5[:2]>/<filename>

Injects  var wikiIconMap={...};  into index.html, then updates
siUrl() and siFallback() to use the map.

Run once (pure Python, no network):
    python compute_icons.py
"""

import json, hashlib, re
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).resolve().parent.parent   # project root
HTML_FILE    = str(ROOT / 'index.html')
SPELLS_FILE  = str(ROOT / 'data' / 'current_spells.json')
BASE         = 'https://bg3.wiki/w/images'

# ── CDN URL formula ───────────────────────────────────────────────
def cdn_url(filename):
    """Given an exact-case wiki filename, return full CDN URL."""
    h = hashlib.md5(filename.encode('utf-8')).hexdigest()
    return f'{BASE}/{h[0]}/{h[:2]}/{filename}'

def spell_filename(name, variant='Icon.webp'):
    """Convert spell name + variant to wiki filename (spaces → underscores)."""
    return name.strip().replace(' ', '_').replace("'", "%27") + f'_{variant}'

# ── build map ────────────────────────────────────────────────────
spells   = json.load(open(SPELLS_FILE, encoding='utf-8'))

# Load any existing maps from the HTML so manually-corrected entries are preserved
html = open(HTML_FILE, encoding='utf-8').read()
OLD_VARS_RE = re.compile(
    r'var wikiIconMap=(\{[^;]+\});\s*var wikiIconFb=(\{[^;]+\});', re.DOTALL)
existing_map_match = OLD_VARS_RE.search(html)
existing_icon_map = {}
existing_icon_fb  = {}
if existing_map_match:
    try:
        existing_icon_map = json.loads(existing_map_match.group(1))
        existing_icon_fb  = json.loads(existing_map_match.group(2))
    except Exception:
        pass

icon_map = {}          # name → primary URL  (_Icon.webp)
icon_fb  = {}          # name → fallback URL (_Unfaded_Icon.webp)

for sp in spells:
    n = sp['name']
    # Preserve manually-corrected entries; only compute for new/missing ones
    icon_map[n] = existing_icon_map.get(n) or cdn_url(spell_filename(n, 'Icon.webp'))
    icon_fb[n]  = existing_icon_fb.get(n)  or cdn_url(spell_filename(n, 'Unfaded_Icon.webp'))

computed = sum(1 for n in icon_map if n not in existing_icon_map)
print(f'Computed {computed} new icon URLs ({len(icon_map)} total)')

# ── inject into HTML ─────────────────────────────────────────────
# (html already loaded above)

# Serialise as compact JS object literals
map_json = json.dumps(icon_map, ensure_ascii=False, separators=(',', ':'))
fb_json  = json.dumps(icon_fb,  ensure_ascii=False, separators=(',', ':'))

new_vars = (
    f'var wikiIconMap={map_json};\n'
    f'var wikiIconFb={fb_json};'
)

# Replace existing declarations if present, otherwise insert before siUrl
if OLD_VARS_RE.search(html):
    html = OLD_VARS_RE.sub(new_vars, html)
    print('Replaced existing wikiIconMap/wikiIconFb declarations')
else:
    html = html.replace('function siUrl(', new_vars + '\nfunction siUrl(', 1)
    print('Inserted wikiIconMap/wikiIconFb before siUrl()')

# ── update siUrl() ────────────────────────────────────────────────
# Replace the entire siUrl function with a map-lookup version
OLD_SIURL_RE = re.compile(
    r'function siUrl\(n\)\{.*?\}(?=\s*\nfunction|\s*\nvar|\s*\n/)'
    , re.DOTALL)
NEW_SIURL = (
    'function siUrl(n){'
    'return wikiIconMap[n]||'
    '(function(s){var h=wikiIconMap[n]||"";'
    'return "https://bg3.wiki/w/images/"+s+"_Icon.webp";})'
    '(n.trim().replace(/ /g,"_").replace(/\'/g,"%27"));'
    '}'
)
# Simpler version: just look up the map, fall back to a guessed URL
NEW_SIURL_SIMPLE = (
    "function siUrl(n){"
    "if(wikiIconMap[n])return wikiIconMap[n];"
    "var s=n.trim().replace(/ /g,'_').replace(/'/g,'%27');"
    "return 'https://bg3.wiki/w/images/0/00/'+s+'_Icon.webp';"  # dummy — map covers all spells
    "}"
)

if OLD_SIURL_RE.search(html):
    html = OLD_SIURL_RE.sub(NEW_SIURL_SIMPLE, html, count=1)
    print('Updated siUrl()')
else:
    print('WARNING: siUrl() not found — not updated')

# ── update siFallback() ───────────────────────────────────────────
OLD_FB_RE = re.compile(
    r'function siFallback\(img,n\)\{.*?\}(?=\s*\nfunction|\s*\nvar|\s*\n/)'
    , re.DOTALL)
NEW_FB = (
    "function siFallback(img,n){"
    "var fb=wikiIconFb[n];"
    "img.onerror=function(){this.onerror=null;this.outerHTML='<span style=\"font-size:28px\">\u2728</span>';};"
    "img.src=fb||'https://bg3.wiki/w/images/0/00/'+n.trim().replace(/ /g,'_').replace(/'/g,'%27')+'_Unfaded_Icon.webp';"
    "}"
)
if OLD_FB_RE.search(html):
    html = OLD_FB_RE.sub(NEW_FB, html, count=1)
    print('Updated siFallback()')
else:
    print('WARNING: siFallback() not found — not updated')

open(HTML_FILE, 'w', encoding='utf-8').write(html)
print(f'\nDone — reload index.html in your browser.')
