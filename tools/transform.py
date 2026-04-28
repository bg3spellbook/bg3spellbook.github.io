#!/usr/bin/env python3
"""
bg3-spellbook data transformation:
  - Merge SPELL_DB into each spell object (single source of truth)
  - Add Lolth-Sworn Drow / Seldarine Drow to their racial spells
  - Add Dragonborn breath-weapon spell entries
  - Fix duplicate <select id="tag"> (remove smaller first copy)
  - Fix Cast Time <div class="fg"> missing </div>
  - Remove disabled class-filter options that have no spells in BG3
  - Enable Drow subraces & Dragonborn in race filter; remove no-spell races
  - Fix JS: duplicate `var tag` and `var sdb` declarations
  - Redirect sdb.* references in doFilter() to sp.*
  - Bump version v602 → v603
"""

import json, re
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).resolve().parent.parent   # project root
INFILE = str(ROOT / 'index.html')

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def extract_balanced(text, marker, open_ch):
    """Return (json_str, abs_start, abs_end) for the balanced structure after marker."""
    close_ch = '}' if open_ch == '{' else ']'
    pos = text.index(marker) + len(marker)
    depth, start = 0, pos
    for i in range(pos, len(text)):
        if text[i] == open_ch:
            depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i+1], start, i+1
    raise ValueError(f"No balanced close for marker: {marker!r}")


# ─────────────────────────────────────────────────────────────────────────────
# Load file
# ─────────────────────────────────────────────────────────────────────────────

with open(INFILE, 'r', encoding='utf-8') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1.  Extract SPELL_DB and spells array
# ─────────────────────────────────────────────────────────────────────────────

sdb_json, sdb_s, sdb_e = extract_balanced(html, 'var SPELL_DB=', '{')
spell_db = json.loads(sdb_json)

sp_json, sp_s, sp_e = extract_balanced(html, 'var spells = ', '[')
# JS allows sparse arrays (`, , ,` between items); strip them before JSON-parsing
sp_json_clean = re.sub(r',(\s*,)+', ',', sp_json)
spells = json.loads(sp_json_clean)

print(f"Loaded {len(spell_db)} SPELL_DB entries, {len(spells)} spells")

# ─────────────────────────────────────────────────────────────────────────────
# 2.  Merge SPELL_DB fields into every spell object
# ─────────────────────────────────────────────────────────────────────────────

DB_KEYS    = ['cost','damage_types','save','attack_roll','concentration','ritual','conditions','tags']
DB_DEFAULT = {'cost':'Action','damage_types':[],'save':'','attack_roll':False,
               'concentration':False,'ritual':False,'conditions':[],'tags':[]}

merged_count = 0
for sp in spells:
    db = spell_db.get(sp['name'], {})
    for k in DB_KEYS:
        if k not in sp:
            import copy
            sp[k] = copy.deepcopy(db.get(k, DB_DEFAULT[k]))
    if db:
        merged_count += 1

print(f"Merged SPELL_DB data into {merged_count} spells")

# ─────────────────────────────────────────────────────────────────────────────
# 3.  Add Drow subrace names to their racial spells
# ─────────────────────────────────────────────────────────────────────────────

DROW_SPELLS = {'Dancing Lights', 'Faerie Fire', 'Darkness'}
DROW_SUBS   = ['Lolth-Sworn Drow', 'Seldarine Drow']

for sp in spells:
    if sp['name'] in DROW_SPELLS:
        races = sp.get('races', '')
        to_add = [r for r in DROW_SUBS if r not in races]
        if to_add:
            sp['races'] = (races + ', ' + ', '.join(to_add)).strip(', ') if races else ', '.join(to_add)
            print(f"  Added {to_add} to {sp['name']}")

# ─────────────────────────────────────────────────────────────────────────────
# 4.  Add Dragonborn breath-weapon entries
# ─────────────────────────────────────────────────────────────────────────────

BREATH_WEAPONS = [
    {"name":"Acid Breath",      "url":"https://bg3.wiki/wiki/Acid_Breath",
     "school":"Evocation",  "level":"Cantrip",
     "races":"Black Dragonborn, Copper Dragonborn", "used":0,
     "cost":"Action","damage_types":["Acid"],"save":"DEX","attack_roll":False,
     "concentration":False,"ritual":False,"conditions":[],"tags":["Damage","AoE"]},

    {"name":"Lightning Breath", "url":"https://bg3.wiki/wiki/Lightning_Breath",
     "school":"Evocation",  "level":"Cantrip",
     "races":"Blue Dragonborn, Bronze Dragonborn", "used":0,
     "cost":"Action","damage_types":["Lightning"],"save":"DEX","attack_roll":False,
     "concentration":False,"ritual":False,"conditions":[],"tags":["Damage","AoE"]},

    {"name":"Fire Breath",      "url":"https://bg3.wiki/wiki/Fire_Breath",
     "school":"Evocation",  "level":"Cantrip",
     "races":"Brass Dragonborn, Gold Dragonborn, Red Dragonborn", "used":0,
     "cost":"Action","damage_types":["Fire"],"save":"DEX","attack_roll":False,
     "concentration":False,"ritual":False,"conditions":[],"tags":["Damage","AoE"]},

    {"name":"Poison Breath",    "url":"https://bg3.wiki/wiki/Poison_Breath",
     "school":"Conjuration","level":"Cantrip",
     "races":"Green Dragonborn", "used":0,
     "cost":"Action","damage_types":["Poison"],"save":"CON","attack_roll":False,
     "concentration":False,"ritual":False,"conditions":["Poisoned"],"tags":["Damage","AoE","Debuff"]},

    {"name":"Frost Breath",     "url":"https://bg3.wiki/wiki/Frost_Breath",
     "school":"Evocation",  "level":"Cantrip",
     "races":"Silver Dragonborn, White Dragonborn", "used":0,
     "cost":"Action","damage_types":["Cold"],"save":"CON","attack_roll":False,
     "concentration":False,"ritual":False,"conditions":[],"tags":["Damage","AoE"]},
]

existing = {sp['name'] for sp in spells}
added = 0
for bw in BREATH_WEAPONS:
    if bw['name'] not in existing:
        spells.append(bw)
        added += 1

print(f"Added {added} Dragonborn breath-weapon entries")

# ─────────────────────────────────────────────────────────────────────────────
# 5.  Rebuild HTML with new spells JSON; remove SPELL_DB variable
# ─────────────────────────────────────────────────────────────────────────────

new_sp_json = json.dumps(spells, separators=(',', ':'), ensure_ascii=False)

# Find 'var SPELL_DB=' statement start (walk back to find 'var ')
sdb_var_start = html.rindex('var SPELL_DB=', 0, sdb_s + 1)
sdb_stmt_end  = html.index(';', sdb_e)          # semicolon after the closing brace

# Step A: remove SPELL_DB declaration
html = html[:sdb_var_start] + '// (SPELL_DB merged into spell objects)' + html[sdb_stmt_end + 1:]

# Step B: re-locate and replace spells array (indices shifted after A)
sp2_json, sp2_s, sp2_e = extract_balanced(html, 'var spells = ', '[')
html = html[:sp2_s] + new_sp_json + html[sp2_e:]

print("Replaced SPELL_DB + spells array in HTML")

# ─────────────────────────────────────────────────────────────────────────────
# 6.  Fix doFilter() – remove duplicate sdb lines, redirect sdb.* → sp.*
# ─────────────────────────────────────────────────────────────────────────────

# Remove both duplicate sdb declarations (and the surrounding comments)
html = html.replace(
    '    // Use SPELL_DB for rich filtering\n'
    '    var sdb=SPELL_DB[sp.name]||{};\n'
    '    // All new filters use SPELL_DB\n'
    '    var sdb=SPELL_DB[sp.name]||{};\n',
    ''
)

# Redirect sdb.* → sp.* in the filter body
SDB_RENAMES = [
    ('sdb.damage_types', 'sp.damage_types'),
    ('sdb.conditions',   'sp.conditions'),
    ("sdb.cost",         "sp.cost"),
    ('sdb.concentration','sp.concentration'),
    ('sdb.ritual',       'sp.ritual'),
    ('sdb.attack_roll',  'sp.attack_roll'),
    ('sdb.save',         'sp.save'),
    ('sdb.tags',         'sp.tags'),
]
for old, new in SDB_RENAMES:
    html = html.replace(old, new)

print("Updated doFilter() – removed SPELL_DB lookups")

# ─────────────────────────────────────────────────────────────────────────────
# 7.  Fix duplicate `var tag` declaration in doFilter()
# ─────────────────────────────────────────────────────────────────────────────

html = html.replace(
    "  var tag=document.getElementById('tag')?document.getElementById('tag').value:'';\n"
    "  var tag=(document.getElementById('tag')||{value:''}).value;\n",
    "  var tag=(document.getElementById('tag')||{value:''}).value;\n"
)
print("Fixed duplicate var tag")

# ─────────────────────────────────────────────────────────────────────────────
# 8.  Fix HTML – Cast Time div + remove duplicate #tag select
#
#  Before: <select id="cast">…</select>
#          (no closing </div> for the fg wrapper)
#          <!-- Spell Tag -->
#          <div class="fg"><label>Tag</label><select id="tag">…</select></div></div>
#
#  After:  <select id="cast">…</select>
#          </div>           ← close Cast Time fg
#          (first tag select block removed entirely)
# ─────────────────────────────────────────────────────────────────────────────

OLD_CAST_TAIL = (
    '        </select>\n'
    '      \n'
    '      <!-- Spell Tag -->\n'
    '      <div class="fg">\n'
    '        <label>Tag</label>\n'
    '        <select id="tag" onchange="doFilter()" style="width:110px">\n'
    '          <option value="">Any Tag</option>\n'
    '          <option value="AoE">AoE</option>\n'
    '          <option value="Buff">Buff</option>\n'
    '          <option value="Control">Control</option>\n'
    '          <option value="Damage">Damage</option>\n'
    '          <option value="Debuff">Debuff</option>\n'
    '          <option value="Defensive">Defensive</option>\n'
    '          <option value="Enchantment">Enchantment</option>\n'
    '          <option value="Fear">Fear</option>\n'
    '          <option value="Healing">Healing</option>\n'
    '          <option value="Illusion">Illusion</option>\n'
    '          <option value="Melee">Melee</option>\n'
    '          <option value="Movement">Movement</option>\n'
    '          <option value="Necromancy">Necromancy</option>\n'
    '          <option value="Reaction">Reaction</option>\n'
    '          <option value="Smite">Smite</option>\n'
    '          <option value="Summoning">Summoning</option>\n'
    '          <option value="Support">Support</option>\n'
    '          <option value="Teleportation">Teleportation</option>\n'
    '          <option value="Utility">Utility</option>\n'
    '        </select>\n'
    '      </div></div>\n'
)
NEW_CAST_TAIL = '        </select>\n      </div>\n'

count = html.count(OLD_CAST_TAIL)
html  = html.replace(OLD_CAST_TAIL, NEW_CAST_TAIL, 1)
print(f"Fixed Cast Time div + removed duplicate tag select ({count} occurrence{'s' if count!=1 else ''})")

# ─────────────────────────────────────────────────────────────────────────────
# 9.  Class dropdown – remove disabled options that have no spells in BG3
# ─────────────────────────────────────────────────────────────────────────────

REMOVE_CLASS_OPTIONS = [
    '          <option value="Berserker" disabled>└ Berserker</option>\n',
    '          <option value="College of Valour" disabled>└ College of Valour</option>\n',
    '          <option value="College of Swords" disabled>└ College of Swords</option>\n',
    '          <option value="College of Glamour" disabled>└ College of Glamour</option>\n',
    '          <option value="Arcane Domain" disabled>└ Arcane Domain</option>\n',
    '          <option value="Twilight Domain" disabled>└ Twilight Domain</option>\n',
    '          <option value="Peace Domain" disabled>└ Peace Domain</option>\n',
    '          <option value="Spores Domain" disabled>└ Spores Domain</option>\n',
    '          <option value="Circle of the Moon" disabled>└ Circle of the Moon</option>\n',
    '          <option value="Battle Master" disabled>└ Battle Master</option>\n',
    '          <option value="Way of the Open Hand" disabled>└ Way of the Open Hand</option>\n',
    '          <option value="Way of the Four Elements" disabled>└ Way of the Four Elements</option>\n',
    '          <option value="Oath of Glory" disabled>└ Oath of Glory</option>\n',
    '          <option value="Hunter" disabled>└ Hunter</option>\n',
    '          <option value="Beast Master" disabled>└ Beast Master</option>\n',
    '          <option value="Thief" disabled>└ Thief</option>\n',
    '          <option value="Assassin" disabled>└ Assassin</option>\n',
    '          <option value="Wild Magic" disabled>└ Wild Magic</option>\n',
]

removed_cls = 0
for opt in REMOVE_CLASS_OPTIONS:
    if opt in html:
        html = html.replace(opt, '', 1)
        removed_cls += 1

print(f"Removed {removed_cls} no-spell disabled class options")

# ─────────────────────────────────────────────────────────────────────────────
# 10. Race dropdown – enable Drow subraces + Dragonborn; remove no-spell races
# ─────────────────────────────────────────────────────────────────────────────

# Enable Drow subraces
for subrace in ['Lolth-Sworn Drow', 'Seldarine Drow']:
    html = html.replace(
        f'          <option value="{subrace}" disabled>',
        f'          <option value="{subrace}">'
    )

# Remove base "Dragonborn" option (no spells reference just "Dragonborn")
html = html.replace(
    '          <option value="Dragonborn" disabled>Dragonborn</option>\n',
    ''
)

# Enable the 10 specific Dragonborn variants
for variant in [
    'Black Dragonborn','Blue Dragonborn','Brass Dragonborn','Bronze Dragonborn',
    'Copper Dragonborn','Gold Dragonborn','Green Dragonborn','Red Dragonborn',
    'Silver Dragonborn','White Dragonborn'
]:
    html = html.replace(
        f'          <option value="{variant}" disabled>',
        f'          <option value="{variant}">'
    )

# Remove races/subraces with no spells
REMOVE_RACE_OPTIONS = [
    '          <option value="Gold Dwarf" disabled>└ Gold Dwarf</option>\n',
    '          <option value="Shield Dwarf" disabled>└ Shield Dwarf</option>\n',
    '          <option value="Wood Elf" disabled>└ Wood Elf</option>\n',
    '          <option value="Deep Gnome" disabled>└ Deep Gnome</option>\n',
    '          <option value="Rock Gnome" disabled>└ Rock Gnome</option>\n',
    '          <option value="Wood Half-Elf" disabled>└ Wood Half-Elf</option>\n',
    '          <option value="Half-Orc" disabled>Half-Orc</option>\n',
    '          <option value="Halfling" disabled>Halfling</option>\n',
    '          <option value="Lightfoot Halfling" disabled>└ Lightfoot Halfling</option>\n',
    '          <option value="Strongheart Halfling" disabled>└ Strongheart Halfling</option>\n',
    '          <option value="Human" disabled>Human</option>\n',
]

removed_race = 0
for opt in REMOVE_RACE_OPTIONS:
    if opt in html:
        html = html.replace(opt, '', 1)
        removed_race += 1

print(f"Enabled Drow subraces + 10 Dragonborn variants; removed {removed_race} no-spell race options")

# Remove now-empty optgroups (Half-Orc, Halfling, Human)
html = re.sub(
    r'[ \t]*<optgroup label="(?:Half-Orc|Halfling|Human)">\s*</optgroup>\n?',
    '',
    html
)

# ─────────────────────────────────────────────────────────────────────────────
# 11. Update version number
# ─────────────────────────────────────────────────────────────────────────────

html = html.replace('BG3 Spellbook v602', 'BG3 Spellbook v603')
html = html.replace('<title>BG3 Spellbook v602</title>', '<title>BG3 Spellbook v603</title>')

# ─────────────────────────────────────────────────────────────────────────────
# Verify no remaining SPELL_DB / sdb references
# ─────────────────────────────────────────────────────────────────────────────

sdb_remaining = [i for i, line in enumerate(html.split('\n'), 1)
                 if 'SPELL_DB' in line or ('sdb.' in line and 'sdb_' not in line)]
if sdb_remaining:
    print(f"WARNING – remaining SPELL_DB/sdb refs on lines: {sdb_remaining[:10]}")
else:
    print("✓ No remaining SPELL_DB / sdb references")

# ─────────────────────────────────────────────────────────────────────────────
# Write output
# ─────────────────────────────────────────────────────────────────────────────

with open(INFILE, 'w', encoding='utf-8') as f:
    f.write(html)

# Final counts
final_sp_json, _, _ = extract_balanced(html, 'var spells = ', '[')
final_spells = json.loads(final_sp_json)
level_counts = {}
for s in final_spells:
    l = s.get('level','?')
    level_counts[l] = level_counts.get(l, 0) + 1

print(f"\nDone! Written to {INFILE}")
print(f"Total spells: {len(final_spells)}")
for lvl in ['Cantrip','Level 1','Level 2','Level 3','Level 4','Level 5','Level 6','Level 7','Level 8','Level 9']:
    if lvl in level_counts:
        print(f"  {lvl}: {level_counts[lvl]}")
