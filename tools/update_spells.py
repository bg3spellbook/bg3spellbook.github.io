#!/usr/bin/env python3
"""
Phase 2 spell database update:
  - Remove 4 Level 9 spells with broken/missing wiki pages
  - Remove duplicate Pass without Trace (keep capital W version)
  - Remove duplicate Dispel Evil And Good (keep lowercase 'and' version)
  - Add ~50 spells missing from the wiki categories
  - Bump version v603 → v604
"""

import json, re, copy
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).resolve().parent.parent   # project root
INFILE = str(ROOT / 'bg3-spellbook.html')

def extract_balanced(text, marker, open_ch):
    close_ch = '}' if open_ch == '{' else ']'
    pos = text.index(marker) + len(marker)
    depth, start = 0, pos
    for i in range(pos, len(text)):
        if text[i] == open_ch: depth += 1
        elif text[i] == close_ch:
            depth -= 1
            if depth == 0: return text[start:i+1], start, i+1
    raise ValueError(f"no close for {marker!r}")

with open(INFILE, 'r', encoding='utf-8') as f:
    html = f.read()

sp_json, sp_s, sp_e = extract_balanced(html, 'var spells = ', '[')
sp_json_clean = re.sub(r',(\s*,)+', ',', sp_json)
spells = json.loads(sp_json_clean)
print(f"Loaded {len(spells)} spells")

# ── 1. Remove broken/invalid spells ──────────────────────────────────────────

REMOVE = {
    'Foresight',          # 404 on wiki
    'Mass Heal',          # 404 on wiki
    'True Resurrection',  # 404 on wiki
    'Wish',               # Disambiguation page, no spell content
}
before = len(spells)
spells = [s for s in spells if s['name'] not in REMOVE]
print(f"Removed {before - len(spells)} invalid spells: {REMOVE}")

# ── 2. Remove duplicates ──────────────────────────────────────────────────────

# Keep "Pass Without Trace" (capital W), remove "Pass without Trace" (lowercase w)
before = len(spells)
spells = [s for s in spells if s['name'] != 'Pass without Trace']
print(f"Removed {before - len(spells)} duplicate: 'Pass without Trace'")

# Keep "Dispel Evil and Good" (lowercase), remove "Dispel Evil And Good" (uppercase A)
before = len(spells)
spells = [s for s in spells if s['name'] != 'Dispel Evil And Good']
print(f"Removed {before - len(spells)} duplicate: 'Dispel Evil And Good'")

# ── 3. Add missing spells ─────────────────────────────────────────────────────

def sp(name, url_name, school, level, **kwargs):
    """Build a spell object with defaults."""
    url_name = url_name or name.replace(' ', '_').replace("'", '%27').replace(':', ':')
    obj = {
        'name': name,
        'url': f'https://bg3.wiki/wiki/{url_name}',
        'school': school,
        'level': level,
        'used': 0,
        'cost': kwargs.pop('cost', 'Action'),
        'damage_types': kwargs.pop('damage_types', []),
        'save': kwargs.pop('save', ''),
        'attack_roll': kwargs.pop('attack_roll', False),
        'concentration': kwargs.pop('concentration', False),
        'ritual': kwargs.pop('ritual', False),
        'conditions': kwargs.pop('conditions', []),
        'tags': kwargs.pop('tags', []),
    }
    for k in ('classes', 'races', 'features', 'items', 'scrolls'):
        v = kwargs.pop(k, '')
        if v: obj[k] = v
    obj.update(kwargs)
    return obj

NEW_SPELLS = [

    # ── CANTRIPS ───────────────────────────────────────────────────────────────
    sp('Cosmic Omen: Ability Check', 'Cosmic_Omen:_Ability_Check',
       'Divination', 'Cantrip',
       classes='Circle of Stars (Lv 6)',
       concentration=True,
       tags=['Buff', 'Support']),

    sp('Debilitating Infusion', 'Debilitating_Infusion',
       'Enchantment', 'Cantrip',
       cost='Bonus Action',
       conditions=['Disadvantage on Saving Throws'],
       tags=['Debuff']),

    sp('Enlarge (Duergar)', 'Enlarge_(Duergar)',
       'Transmutation', 'Cantrip',
       races='Duergar',
       tags=['Buff', 'Self']),

    sp('Ensnaring Shock', 'Ensnaring_Shock',
       'Evocation', 'Cantrip',
       cost='Bonus Action',
       items='A Sparking Promise',
       damage_types=['Lightning'],
       save='DEX',
       attack_roll=True,
       conditions=['Charged Lightning'],
       tags=['Damage', 'Debuff']),

    sp('Entangle (Dryad)', 'Entangle_(Dryad)',
       'Conjuration', 'Cantrip',
       save='STR',
       concentration=True,
       conditions=['Entangled'],
       tags=['Control', 'AoE']),

    sp('Githyanki Psionics: Mage Hand', 'Githyanki_Psionics:_Mage_Hand',
       'Conjuration', 'Cantrip',
       races='Githyanki',
       tags=['Utility']),

    sp('Hellflame Cleave', 'Hellflame_Cleave',
       'Evocation', 'Cantrip',
       items='Hellfire Greataxe',
       damage_types=['Slashing', 'Fire'],
       save='DEX',
       conditions=['Burning'],
       tags=['Damage', 'AoE', 'Melee']),

    sp('Howl of the Dead', 'Howl_of_the_Dead',
       'Necromancy', 'Cantrip',
       cost='Bonus Action',
       items="Reaper's Embrace",
       save='WIS',
       conditions=['Numbed'],
       tags=['Debuff', 'AoE']),

    sp('Invisibility (Duergar)', 'Invisibility_(Duergar)',
       'Illusion', 'Cantrip',
       races='Duergar',
       concentration=True,
       conditions=['Invisible'],
       tags=['Stealth', 'Self']),

    sp('Pulling Web', 'Pulling_Web',
       'Transmutation', 'Cantrip',
       items='Pale Widow Gloves',
       damage_types=['Piercing'],
       attack_roll=True,
       tags=['Damage', 'Movement']),

    sp('Stand Like Stone', 'Stand_Like_Stone',
       'Abjuration', 'Cantrip',
       cost='Bonus Action',
       items='Tenacious Boots',
       tags=['Defensive', 'Self']),

    # ── LEVEL 1 ────────────────────────────────────────────────────────────────
    sp('Arcane Critical', 'Arcane_Critical',
       'Divination', 'Level 1',
       cost='Bonus Action',
       items='Deadly Channeller Gloves',
       tags=['Buff', 'Self']),

    sp('Detect Evil and Good', 'Detect_Evil_and_Good',
       'Divination', 'Level 1',
       concentration=True,
       tags=['Divination', 'Utility']),

    sp('Find Familiar: Boo', 'Find_Familiar:_Boo',
       'Conjuration', 'Level 1',
       tags=['Summoning']),

    sp('Find Familiar: Cheeky Quasit', 'Find_Familiar:_Cheeky_Quasit',
       'Conjuration', 'Level 1',
       scrolls='Scroll of Summon Quasit',
       ritual=True,
       conditions=['Frightened'],
       tags=['Summoning']),

    sp('Githyanki Psionics: Jump', 'Githyanki_Psionics:_Jump',
       'Transmutation', 'Level 1',
       races='Githyanki',
       tags=['Movement', 'Buff']),

    sp('Grave Repulsion', 'Grave_Repulsion',
       'Evocation', 'Level 1',
       damage_types=['Necrotic'],
       save='CON',
       tags=['Damage', 'AoE']),

    sp('Hellfire Curse', 'Hellfire_Curse',
       'Enchantment', 'Level 1',
       cost='Bonus Action',
       save='WIS',
       conditions=['Hellfire Curse'],
       tags=['Debuff', 'AoE']),

    sp('Incongruent Splash', 'Incongruent_Splash',
       'Evocation', 'Level 1',
       items='Cup of Endless Water',
       damage_types=['Fire'],
       save='DEX',
       conditions=['Wet'],
       tags=['Damage']),

    sp('Magic Missile (Illithid Arcanist)', 'Magic_Missile_(Illithid_Arcanist)',
       'Evocation', 'Level 1',
       damage_types=['Force'],
       tags=['Damage']),

    sp('Sanctuary of Loss', 'Sanctuary_of_Loss',
       'Abjuration', 'Level 1',
       cost='Reaction',
       features='Legendary Action (Honour Mode)',
       tags=['Defensive', 'Special']),

    sp("Shar's Aegis", "Shar%27s_Aegis",
       'Abjuration', 'Level 1',
       cost='Bonus Action',
       items="Dark Justiciar Half-Plate",
       concentration=True,
       tags=['Defensive', 'Buff', 'Self']),

    # ── LEVEL 2 ────────────────────────────────────────────────────────────────
    sp('Dismiss Arcane Lock', 'Dismiss_Arcane_Lock',
       'Abjuration', 'Level 2',
       tags=['Utility']),

    sp("Ethel's Ray of Sickness", "Ethel%27s_Ray_of_Sickness",
       'Necromancy', 'Level 2',
       damage_types=['Poison'],
       save='CON',
       attack_roll=True,
       conditions=['Poisoned'],
       tags=['Damage', 'Debuff']),

    sp("Lump's Command", "Lump%27s_Command",
       'Enchantment', 'Level 2',
       cost='Bonus Action',
       tags=['Debuff']),

    sp('Reduce (Duergar)', 'Reduce_(Duergar)',
       'Transmutation', 'Level 2',
       races='Duergar',
       conditions=['Reduced'],
       tags=['Debuff']),

    sp("Umberlee's Praise", "Umberlee%27s_Praise",
       'Enchantment', 'Level 2',
       items="The Bitch Queen's Blessing",
       save='WIS',
       conditions=['Charmed'],
       tags=['Enchantment', 'Control']),

    # ── LEVEL 3 ────────────────────────────────────────────────────────────────
    sp('Animate Dead', 'Animate_Dead',
       'Necromancy', 'Level 3',
       classes='Cleric (Lv 5), Wizard (Lv 5), Circle of the Spores (Lv 5), '
               'Warlock (Lv 5), Death Domain (Lv 5), College of Lore (Lv 6), '
               'Necromancer (Lv 6), Oathbreaker (Lv 9), Bard (Lv 10)',
       items='Circle of Bones',
       scrolls='Scroll of Animate Dead',
       tags=['Necromancy', 'Summoning']),

    sp('Fanatic Retaliation', 'Fanatic_Retaliation',
       'Evocation', 'Level 3',
       cost='Reaction',
       features='Legendary Action (Honour Mode)',
       damage_types=['Psychic'],
       save='INT',
       conditions=['Silenced'],
       tags=['Damage', 'Special']),

    sp('Tightening Orbit', 'Tightening_Orbit',
       'Evocation', 'Level 3',
       items='Tightening Orbit Helm',
       damage_types=['Force'],
       tags=['Damage', 'AoE', 'Movement']),

    sp('Umbral Ally', 'Umbral_Ally',
       'Necromancy', 'Level 3',
       cost='Bonus Action',
       damage_types=['Necrotic'],
       tags=['Summoning', 'Necromancy']),

    # ── LEVEL 4 ────────────────────────────────────────────────────────────────
    sp("Bane's Wrath", "Bane%27s_Wrath",
       'Enchantment', 'Level 4',
       damage_types=['Psychic'],
       save='WIS',
       attack_roll=True,
       concentration=True,
       conditions=['Frightened'],
       tags=['Damage', 'Fear', 'Melee']),

    sp('Dark Celebration', 'Dark_Celebration',
       'Necromancy', 'Level 4',
       cost='Bonus Action',
       damage_types=['Necrotic'],
       tags=['Buff', 'Debuff']),

    sp("Gargoyle's Countenance", "Gargoyle%27s_Countenance",
       'Abjuration', 'Level 4',
       items='Gargoyle Boots',
       tags=['Defensive', 'Buff', 'Self']),

    sp('Rays of Fire (Mol)', 'Rays_of_Fire_(Mol)',
       'Evocation', 'Level 4',
       features="Gathering Mol's support",
       damage_types=['Fire'],
       attack_roll=True,
       tags=['Damage']),

    sp("Rolan's Fireball", "Rolan%27s_Fireball",
       'Evocation', 'Level 4',
       damage_types=['Fire'],
       save='DEX',
       conditions=['Heat Metal'],
       tags=['Damage', 'AoE']),

    sp('Wail of Loss (Assistant)', 'Wail_of_Loss_(Assistant)',
       'Enchantment', 'Level 4',
       cost='Reaction',
       damage_types=['Psychic'],
       save='WIS',
       conditions=['Confused'],
       tags=['Damage', 'Control', 'AoE', 'Special']),

    # ── LEVEL 5 ────────────────────────────────────────────────────────────────
    sp('Disconcerting Visage', 'Disconcerting_Visage',
       'Illusion', 'Level 5',
       save='WIS',
       conditions=['Confused'],
       tags=['Control', 'AoE']),

    sp('Disconcerting Visage (Tactician)', 'Disconcerting_Visage_(Tactician)',
       'Illusion', 'Level 5',
       damage_types=['Necrotic'],
       save='WIS',
       conditions=['Confused'],
       tags=['Damage', 'Control', 'AoE']),

    sp("Keeper's Fee", "Keeper%27s_Fee",
       'Enchantment', 'Level 5',
       cost='Bonus Action',
       save='DEX',
       concentration=True,
       conditions=['Disarmed'],
       tags=['Debuff', 'Control']),

    sp('Perturbing Visage', 'Perturbing_Visage',
       'Illusion', 'Level 5',
       save='WIS',
       conditions=['Unnerved'],
       tags=['Control', 'AoE']),

    sp('Sacrifice Soul', 'Sacrifice_Soul',
       'Necromancy', 'Level 5',
       cost='Reaction',
       features='Legendary Action (Honour Mode)',
       tags=['Necromancy', 'Buff', 'Special']),

    sp('Terrifying Visage', 'Terrifying_Visage',
       'Illusion', 'Level 5',
       save='WIS',
       conditions=['Frightened'],
       tags=['Control', 'Fear', 'AoE']),

    sp('Terrifying Visage (Tactician)', 'Terrifying_Visage_(Tactician)',
       'Illusion', 'Level 5',
       damage_types=['Necrotic'],
       save='WIS',
       conditions=['Frightened'],
       tags=['Damage', 'Control', 'Fear', 'AoE']),

    # ── LEVEL 6 ────────────────────────────────────────────────────────────────
    sp('Punish Divinity', 'Punish_Divinity',
       'Abjuration', 'Level 6',
       cost='Reaction',
       save='DEX',
       concentration=True,
       conditions=['Infernal Stun'],
       tags=['Control', 'Special']),

    sp('Sethan: Spiritual Greataxe', 'Sethan:_Spiritual_Greataxe',
       'Evocation', 'Level 6',
       cost='Bonus Action',
       items='Sethan',
       damage_types=['Force'],
       attack_roll=True,
       conditions=['Bleeding'],
       tags=['Summoning', 'Melee']),

    sp('Sights of the Seelie: Summon Deva', 'Sights_of_the_Seelie:_Summon_Deva',
       'Conjuration', 'Level 6',
       scrolls='Scroll of Bestial Communion',
       conditions=['Frightened'],
       tags=['Summoning']),

    sp('Soul Drain', 'Soul_Drain',
       'Necromancy', 'Level 6',
       cost='Free Action',
       damage_types=['Necrotic'],
       attack_roll=True,
       tags=['Damage', 'Necromancy', 'Melee']),

    sp('Summon Eternal Debtor', 'Summon_Eternal_Debtor',
       'Conjuration', 'Level 6',
       cost='Bonus Action',
       tags=['Summoning']),

    # ── LEVEL 9 ────────────────────────────────────────────────────────────────
    sp('Aegis of the Absolute', 'Aegis_of_the_Absolute',
       'Evocation', 'Level 9',
       features='Netherbrain (Honour Mode)',
       tags=['Defensive', 'Special']),
]

# Only add spells not already in DB
existing_names = {s['name'] for s in spells}
added = 0
for new_sp in NEW_SPELLS:
    if new_sp['name'] not in existing_names:
        spells.append(new_sp)
        added += 1
    else:
        print(f"  SKIP (already exists): {new_sp['name']}")

print(f"Added {added} new spells")

# ── 4. Serialize and write back ───────────────────────────────────────────────

new_sp_json = json.dumps(spells, separators=(',', ':'), ensure_ascii=False)

sp2_json, sp2_s, sp2_e = extract_balanced(html, 'var spells = ', '[')
html = html[:sp2_s] + new_sp_json + html[sp2_e:]

# Update version and comment
html = html.replace('BG3 Spellbook v603', 'BG3 Spellbook v604')
html = html.replace('// EMBEDDED SPELL DATA (607 spells)', '// EMBEDDED SPELL DATA (see version for count)')
html = html.replace('607 spells embedded', f'{len(spells)} spells embedded')

with open(INFILE, 'w', encoding='utf-8') as f:
    f.write(html)

# ── 5. Final stats ────────────────────────────────────────────────────────────

by_level = {}
for s in spells:
    l = s.get('level', '?')
    by_level[l] = by_level.get(l, 0) + 1

print(f"\nDone — v604, {len(spells)} total spells")
for lvl in ['Cantrip','Level 1','Level 2','Level 3','Level 4','Level 5','Level 6','Level 7','Level 9']:
    print(f"  {lvl}: {by_level.get(lvl, 0)}")
