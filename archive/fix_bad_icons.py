"""
fix_bad_icons.py  —  Removes known-bad icon URLs from chip_icons.json cache
so fetch_chip_icons.py will re-fetch them with the improved SKIP filter.
Then re-injects cleaned maps into HTML.
"""
import json, re

CACHE_FILE = 'chip_icons.json'
HTML_FILE  = 'bg3-spellbook.html'
NAMES_FILE = 'chip_names.json'

# Patterns that indicate a wrong/UI icon snuck through the SKIP filter
BAD_PATTERNS = [
    'Shattered_Condition_Icon',
    'Stunned_Condition_Icon',
    'Armour_class_icon_frame',
    'D6_Physical',
]

# ── Load and clean cache ──────────────────────────────────────────
cache = json.load(open(CACHE_FILE, encoding='utf-8'))

to_delete = []
for name, url in cache.items():
    if url and any(bad in url for bad in BAD_PATTERNS):
        print(f'  Removing bad icon for "{name}": ...{url[30:]}')
        to_delete.append(name)

for name in to_delete:
    del cache[name]

print(f'\nRemoved {len(to_delete)} bad entries from cache (will re-fetch)')
json.dump(cache, open(CACHE_FILE, 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('Saved chip_icons.json — run fetch_chip_icons.py to re-fetch them')
