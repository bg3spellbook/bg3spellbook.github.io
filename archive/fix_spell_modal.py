"""
Replace inline dpanel row-expand with openSpellModal() popup for both
desktop table rows and mobile card clicks.
"""
import re

html = open('bg3-spellbook.html', encoding='utf-8').read()
results = []

# ─────────────────────────────────────────────────────────
# 1. Table row onclick: toggleDetail → openSpellModal
# ─────────────────────────────────────────────────────────
OLD_TR = """h+='<tr class="dr'+(ex?' dx':'')+(isPinned?' pinned':'')+(i%2===0?'':' alt')+(isVariant(sp)?' sp-variant':'')+'\" onclick="toggleDetail(\\''+k+'\\')">\';\n"""
NEW_TR = """h+='<tr class="dr'+(isPinned?' pinned':'')+(i%2===0?'':' alt')+(isVariant(sp)?' sp-variant':'')+'\" onclick="openSpellModal(allSpellsMap[\\x27'+esc(sp.name)+'\\x27])">\';\n"""
if OLD_TR in html:
    html = html.replace(OLD_TR, NEW_TR)
    results.append('[JS] table row onclick → openSpellModal')
else:
    results.append('[JS] WARNING: table row onclick not found')

# ─────────────────────────────────────────────────────────
# 2. Upcast badge onclick: toggleDetail → openSpellModal
# ─────────────────────────────────────────────────────────
OLD_UP = """if(hasUpcast)bgs+='<span class="sf sf-up" data-tip="Upcast tracked" onclick="event.stopPropagation();toggleDetail(\\''+k+'\\')">⬆️</span>';"""
NEW_UP = """if(hasUpcast)bgs+='<span class="sf sf-up" data-tip="Upcast tracked" onclick="event.stopPropagation();openSpellModal(allSpellsMap[\\x27'+esc(sp.name)+'\\x27])">⬆️</span>';"""
if OLD_UP in html:
    html = html.replace(OLD_UP, NEW_UP)
    results.append('[JS] upcast badge onclick → openSpellModal')
else:
    results.append('[JS] WARNING: upcast badge onclick not found')

# ─────────────────────────────────────────────────────────
# 3. Remove: var k=type+i; var ex=expKey===k;
# ─────────────────────────────────────────────────────────
OLD_KE = "    var k=type+i; var ex=expKey===k;\n"
if OLD_KE in html:
    html = html.replace(OLD_KE, "")
    results.append('[JS] var k / var ex removed from section()')
else:
    results.append('[JS] WARNING: var k/ex line not found')

# ─────────────────────────────────────────────────────────
# 4. Remove the entire if(ex){ dpanel } block
# ─────────────────────────────────────────────────────────
DPANEL_PATTERN = r"\n    if\(ex\)\{[\s\S]*?h\+='</div></td></tr>';\n    \}"
m = re.search(DPANEL_PATTERN, html)
if m:
    html = html[:m.start()] + html[m.end():]
    results.append('[JS] dpanel if(ex) block removed')
else:
    results.append('[JS] WARNING: dpanel if(ex) block not found')

# ─────────────────────────────────────────────────────────
# 5. toggleDetail → no-op stub (safety)
# ─────────────────────────────────────────────────────────
OLD_TD = "function toggleDetail(k){expKey=expKey===k?null:k;render();}"
NEW_TD = "function toggleDetail(k){ /* replaced by spell modal */ }"
if OLD_TD in html:
    html = html.replace(OLD_TD, NEW_TD)
    results.append('[JS] toggleDetail → no-op stub')
else:
    results.append('[JS] WARNING: toggleDetail not found')

open('bg3-spellbook.html', 'w', encoding='utf-8').write(html)
print('\n'.join(results))
print('\nDone.')
