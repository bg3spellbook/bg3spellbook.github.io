import json, re

html = open('bg3-spellbook.html', encoding='utf-8').read()
results = []

# ══════════════════════════════════════════════════════════════════
# FIX 1-3: DATA — normalize cost/save/classes in spell array
# ══════════════════════════════════════════════════════════════════
m = re.search(r'(var spells\s*=\s*)(\[.*?\]);', html, re.DOTALL)
prefix, sp_json = m.group(1), m.group(2)
spells = json.loads(re.sub(r',(\s*,)+', ',', sp_json))

fc = fs = fcls = 0
for sp in spells:
    if sp.get('cost') == 'Bonus':
        sp['cost'] = 'Bonus Action'; fc += 1
    if sp.get('save') == 'Dexterity':
        sp['save'] = 'DEX'; fs += 1
    cls = sp.get('classes', '')
    if cls and ',' in cls and ', ' not in cls:
        sp['classes'] = ', '.join(x.strip() for x in cls.split(','))
        fcls += 1

html = html[:m.start()] + prefix + json.dumps(spells, ensure_ascii=False) + ';' + html[m.end():]
results.append(f'[DATA] cost: {fc} fixed | save: {fs} fixed | classes spacing: {fcls} fixed')

# ══════════════════════════════════════════════════════════════════
# FIX 4: flags() — read from spell object fields too
# ══════════════════════════════════════════════════════════════════
old = "function flags(sp){return{conc:!!CONC[sp.name],ritual:!!RITUAL[sp.name],react:!!REACT[sp.name],bonus:!!BONUS[sp.name],saves:SAVE_MAP[sp.name]||[]};}"
new = "function flags(sp){return{conc:!!(CONC[sp.name]||sp.concentration),ritual:!!(RITUAL[sp.name]||sp.ritual),react:!!(REACT[sp.name]||sp.cost==='Reaction'),bonus:!!(BONUS[sp.name]||sp.cost==='Bonus Action'),saves:SAVE_MAP[sp.name]?[SAVE_MAP[sp.name]]:(sp.save?[sp.save]:[])};}"
if old in html:
    html = html.replace(old, new); results.append('[JS] flags() fixed')
else:
    results.append('[JS] WARNING: flags() not found')

# ══════════════════════════════════════════════════════════════════
# FIX 5: Add isVariant() helper + patch all 3 sp.parent usages
# ══════════════════════════════════════════════════════════════════
iv_fn = (
    'function isVariant(sp){'
    'return /^(Recast |Activate |Move |Psionic Suggestion: |Sethan: )/.test(sp.name)||'
    '/\\s*\\((Dryad|Tactician|Illithid Arcanist|Assistant)\\)\\s*$/.test(sp.name)||'
    '!!sp.parent;'
    '}\n'
)
marker = 'function toggleVariants(){'
if marker in html and 'function isVariant(' not in html:
    html = html.replace(marker, iv_fn + marker)
    results.append('[JS] isVariant() added')
else:
    results.append('[JS] isVariant() already present or marker missing')

for old_s, new_s, label in [
    ('return !sp.parent;',                                   'return !isVariant(sp);',          'doFilter baseSpells'),
    ("var variantCount=all.filter(function(s){return !!s.parent;}).length;", "var variantCount=all.filter(isVariant).length;", 'variantCount'),
    ("+(sp.parent?' sp-variant':'')",                        "+(isVariant(sp)?' sp-variant':'')", 'section row class'),
]:
    if old_s in html:
        html = html.replace(old_s, new_s); results.append(f'[JS] isVariant patch: {label}')
    else:
        results.append(f'[JS] WARNING: patch not found: {label}')

# ══════════════════════════════════════════════════════════════════
# FIX 6: charCanHave — remove incorrect subclass-gating of base class
# ══════════════════════════════════════════════════════════════════
old_block = (
    '    if(spCls.has(cls)){\n'
    '      var spSubsForCls=[];\n'
    '      spCls.forEach(function(t){if(S2C[t]===cls)spSubsForCls.push(t);});\n'
    '      if(spSubsForCls.length){\n'
    '        // Subclass-gated \u2014 char must have the matching subclass at the right level\n'
    '        if(sub&&spSubsForCls.indexOf(sub)>-1&&charLvl>=spellMinLvl(sp.classes,sub))return true;\n'
    '      } else {\n'
    '        if(charLvl>=spellMinLvl(sp.classes,cls))return true;\n'
    '      }\n'
    '    }'
)
new_block = (
    '    if(spCls.has(cls)){\n'
    '      // Base class listed \u2014 available to all members at the class\'s listed level\n'
    '      if(charLvl>=spellMinLvl(sp.classes,cls))return true;\n'
    '    }'
)
if old_block in html:
    html = html.replace(old_block, new_block)
    results.append('[JS] charCanHave subclass-gating fixed')
else:
    results.append('[JS] WARNING: charCanHave block not found (check whitespace)')

# ══════════════════════════════════════════════════════════════════
# FIX 7: doFilter — fix `at` filter to use sp.cost
# ══════════════════════════════════════════════════════════════════
old_at = (
    "    if(at==='reaction'&&!fg.react)return false;\n"
    "    if(at==='bonus'&&!fg.bonus)return false;\n"
    "    if(at==='action'&&(fg.react||fg.bonus))return false;"
)
new_at = (
    "    if(at==='reaction'&&sp.cost!=='Reaction')return false;\n"
    "    if(at==='bonus'&&sp.cost!=='Bonus Action')return false;\n"
    "    if(at==='action'&&(sp.cost==='Reaction'||sp.cost==='Bonus Action'))return false;"
)
if old_at in html:
    html = html.replace(old_at, new_at); results.append('[JS] at filter uses sp.cost')
else:
    results.append('[JS] WARNING: at filter block not found')

# ══════════════════════════════════════════════════════════════════
# FIX 8: doFilter — add cast='long' handler
# ══════════════════════════════════════════════════════════════════
old_cast = (
    "if(cast==='action'&&spCost!=='Action')return false;"
    "if(cast==='bonus'&&spCost!=='Bonus Action')return false;"
    "if(cast==='reaction'&&spCost!=='Reaction')return false;"
    "}"
)
new_cast = (
    "if(cast==='action'&&spCost!=='Action')return false;"
    "if(cast==='bonus'&&spCost!=='Bonus Action')return false;"
    "if(cast==='reaction'&&spCost!=='Reaction')return false;"
    "if(cast==='long'&&!(RITUAL[sp.name]||sp.ritual))return false;"
    "}"
)
if old_cast in html:
    html = html.replace(old_cast, new_cast); results.append("[JS] cast='long' handler added")
else:
    results.append('[JS] WARNING: cast block not found')

# ══════════════════════════════════════════════════════════════════
# FIX 9: Remove dead sr==='party' code
# ══════════════════════════════════════════════════════════════════
for candidate in [
    "    if(sr==='party'&&sp.used<1)return false;\n",
    "    if(sr==='party'&&sp.used<1)return false;",
]:
    if candidate in html:
        html = html.replace(candidate, '')
        results.append("[JS] dead sr==='party' removed")
        break
else:
    results.append("[JS] WARNING: sr==='party' not found")

# ══════════════════════════════════════════════════════════════════
# FIX 10: Fix stats bar initial message text
# ══════════════════════════════════════════════════════════════════
old_msg = 'No spell data loaded \u2014 click \u2b06 Import Data to get started'
new_msg = 'No spell data loaded \u2014 click \u2b06 Load Custom Data to get started'
if old_msg in html:
    html = html.replace(old_msg, new_msg); results.append('[HTML] stats bar text fixed')
else:
    results.append('[HTML] stats bar text already correct or not found')

# ══════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════
open('bg3-spellbook.html', 'w', encoding='utf-8').write(html)

print('\n'.join(results))
print('\nDone.')
