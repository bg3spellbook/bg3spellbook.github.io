html = open('bg3-spellbook.html', encoding='utf-8').read()
results = []

# ══════════════════════════════════════════════════════════════════
# 1. Expand Flags select to include Attack Roll + Saving Throw
# ══════════════════════════════════════════════════════════════════
old_flg = (
    '      <!-- Flags -->\n'
    '      <div class="fg">\n'
    '        <label>Flags</label>\n'
    '        <select id="flg" onchange="doFilter()" style="width:110px">\n'
    '          <option value="">All</option>\n'
    '          <option value="conc">Concentration</option>\n'
    '          <option value="ritual">Ritual</option>\n'
    '          <option value="overlap">Overlap (2+)</option>\n'
    '          <option value="pinned">Pinned \u2605</option>\n'
    '          <option value="noted">Has Notes</option>\n'
    '          <option value="upcasted">Upcasted</option>\n'
    '        </select>\n'
    '      </div>\n'
)
new_flg = (
    '      <!-- Flags -->\n'
    '      <div class="fg">\n'
    '        <label>Flags</label>\n'
    '        <select id="flg" onchange="doFilter()" style="width:120px">\n'
    '          <option value="">All</option>\n'
    '          <option value="conc">Concentration</option>\n'
    '          <option value="ritual">Ritual</option>\n'
    '          <option value="atk">Attack Roll</option>\n'
    '          <option value="save">Saving Throw</option>\n'
    '          <option value="overlap">Overlap (2+)</option>\n'
    '          <option value="pinned">Pinned \u2605</option>\n'
    '          <option value="noted">Has Notes</option>\n'
    '          <option value="upcasted">Upcasted</option>\n'
    '        </select>\n'
    '      </div>\n'
)
if old_flg in html:
    html = html.replace(old_flg, new_flg)
    results.append('[HTML] Flags expanded with Attack Roll + Saving Throw')
else:
    results.append('[HTML] WARNING: Flags block not found')

# ══════════════════════════════════════════════════════════════════
# 2. Remove Components <div> block entirely
# ══════════════════════════════════════════════════════════════════
comp_block = (
    '      <!-- Components -->\n'
    '      <div class="fg">\n'
    '        <label>Components</label>\n'
    '        <select id="comp" onchange="doFilter()" style="width:110px">\n'
    '          <option value="">Any</option>\n'
    '          <option value="conc">Concentration</option>\n'
    '          <option value="ritual">Ritual</option>\n'
    '          <option value="atk">Attack Roll</option>\n'
    '          <option value="save">Saving Throw</option>\n'
    '        </select>\n'
    '      </div>\n'
)
if comp_block in html:
    html = html.replace(comp_block, '')
    results.append('[HTML] Components filter removed')
else:
    results.append('[HTML] WARNING: Components block not found')

# ══════════════════════════════════════════════════════════════════
# 3. JS doFilter — add atk/save cases to fl handler, remove comp var + logic
# ══════════════════════════════════════════════════════════════════

# Add atk/save to the fl=== block (after upcasted line)
old_fl_block = (
    "    if(fl==='conc'&&!fg.conc)return false;\n"
    "    if(fl==='ritual'&&!fg.ritual)return false;\n"
    "    if(fl==='overlap'){var cnt=CHARS.filter(function(c){return sp[c]==='\u2705';}).length;if(cnt<2)return false;}\n"
    "    if(fl==='pinned'&&!pinned.has(sp.name))return false;\n"
    "    if(fl==='noted'&&!notes[sp.name])return false;\n"
    "    if(fl==='upcasted'&&!upcasts[sp.name])return false;"
)
new_fl_block = (
    "    if(fl==='conc'&&!(sp.concentration||fg.conc))return false;\n"
    "    if(fl==='ritual'&&!(sp.ritual||fg.ritual))return false;\n"
    "    if(fl==='atk'&&!sp.attack_roll)return false;\n"
    "    if(fl==='save'&&!sp.save)return false;\n"
    "    if(fl==='overlap'){var cnt=CHARS.filter(function(c){return sp[c]==='\u2705';}).length;if(cnt<2)return false;}\n"
    "    if(fl==='pinned'&&!pinned.has(sp.name))return false;\n"
    "    if(fl==='noted'&&!notes[sp.name])return false;\n"
    "    if(fl==='upcasted'&&!upcasts[sp.name])return false;"
)
if old_fl_block in html:
    html = html.replace(old_fl_block, new_fl_block)
    results.append('[JS] Flags filter expanded with atk/save, conc/ritual now use sp fields')
else:
    results.append('[JS] WARNING: Flags filter block not found')

# Remove var comp= read
old_comp_var = "  var comp=document.getElementById('comp').value;\n"
if old_comp_var in html:
    html = html.replace(old_comp_var, '')
    results.append('[JS] var comp removed from doFilter')
else:
    results.append('[JS] WARNING: var comp not found')

# Remove comp filter logic
old_comp_logic = (
    "    if(comp==='conc'&&!(sp.concentration||fg.conc))return false;\n"
    "    if(comp==='ritual'&&!(sp.ritual||fg.ritual))return false;\n"
    "    if(comp==='atk'&&!sp.attack_roll)return false;\n"
    "    if(comp==='save'&&!sp.save)return false;\n"
)
if old_comp_logic in html:
    html = html.replace(old_comp_logic, '')
    results.append('[JS] comp filter logic removed from doFilter')
else:
    results.append('[JS] WARNING: comp filter logic not found')

# ══════════════════════════════════════════════════════════════════
# 4. Remove 'comp' from clearAll
# ══════════════════════════════════════════════════════════════════
old_clear = "  ['q','lvl','usg','act','sav','flg','src','cls','race','comp'].forEach"
new_clear = "  ['q','lvl','usg','act','sav','flg','src','cls','race'].forEach"
if old_clear in html:
    html = html.replace(old_clear, new_clear)
    results.append('[JS] comp removed from clearAll')
else:
    results.append('[JS] WARNING: clearAll array not found')

# ══════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════
open('bg3-spellbook.html', 'w', encoding='utf-8').write(html)
print('\n'.join(results))
print('\nDone.')
