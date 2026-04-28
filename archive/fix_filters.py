import re

html = open('bg3-spellbook.html', encoding='utf-8').read()
results = []

# ══════════════════════════════════════════════════════════════════
# 1. Remove Cast Time <div> block from HTML (duplicates Action filter)
# ══════════════════════════════════════════════════════════════════
cast_block = (
    '      <!-- Casting Time -->\n'
    '      <div class="fg">\n'
    '        <label>Cast Time</label>\n'
    '        <select id="cast" onchange="doFilter()" style="width:110px">\n'
    '          <option value="">Any Time</option>\n'
    '          <option value="action">Action</option>\n'
    '          <option value="bonus">Bonus Action</option>\n'
    '          <option value="reaction">Reaction</option>\n'
    '          <option value="long">1+ Minutes</option>\n'
    '        </select>\n'
    '      </div>\n'
)
if cast_block in html:
    html = html.replace(cast_block, '')
    results.append('[HTML] Cast Time filter removed')
else:
    results.append('[HTML] WARNING: Cast Time block not found (check whitespace)')

# ══════════════════════════════════════════════════════════════════
# 2. Convert Damage, Condition, Tag selects to multi-select
# ══════════════════════════════════════════════════════════════════

# --- Damage ---
old_dmg = '<select id="dmg" onchange="doFilter()" style="width:110px">'
new_dmg = '<select id="dmg" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">'
if old_dmg in html:
    html = html.replace(old_dmg, new_dmg)
    # Also remove the "Any Damage" placeholder option (meaningless in multi-select)
    html = html.replace(
        '<select id="dmg" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">\n'
        '          <option value="">Any Damage</option>\n',
        '<select id="dmg" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">\n'
    )
    results.append('[HTML] Damage → multi-select')
else:
    results.append('[HTML] WARNING: Damage select not found')

# --- Condition ---
old_cond = '<select id="cond" onchange="doFilter()" style="width:110px">'
new_cond = '<select id="cond" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">'
if old_cond in html:
    html = html.replace(old_cond, new_cond)
    html = html.replace(
        '<select id="cond" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">\n'
        '          <option value="">Any Condition</option>\n',
        '<select id="cond" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">\n'
    )
    results.append('[HTML] Condition → multi-select')
else:
    results.append('[HTML] WARNING: Condition select not found')

# --- Tag ---
old_tag = '<select id="tag" onchange="doFilter()" style="width:110px">'
new_tag = '<select id="tag" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">'
if old_tag in html:
    html = html.replace(old_tag, new_tag)
    html = html.replace(
        '<select id="tag" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">\n'
        '          <option value="">Any Tag</option>\n',
        '<select id="tag" multiple size="5" onchange="doFilter()" style="width:110px" title="Ctrl+click to select multiple">\n'
    )
    results.append('[HTML] Tag → multi-select')
else:
    results.append('[HTML] WARNING: Tag select not found')

# ══════════════════════════════════════════════════════════════════
# 3. Add multi-select CSS — style for consistent look
# ══════════════════════════════════════════════════════════════════
multi_css = (
    '\n/* Multi-select filters */\n'
    'select[multiple] { height: auto; padding: 2px; cursor: pointer; }\n'
    'select[multiple] option { padding: 3px 7px; border-radius: 2px; }\n'
    'select[multiple] option:checked { background: linear-gradient(var(--gold), var(--gold)); color: var(--bg); font-weight: 600; }\n'
)
# Insert before closing </style>
if multi_css.strip() not in html:
    html = html.replace('</style>', multi_css + '</style>', 1)
    results.append('[CSS] multi-select styles added')
else:
    results.append('[CSS] multi-select styles already present')

# ══════════════════════════════════════════════════════════════════
# 4. JS: add getMultiVal() helper before doFilter
# ══════════════════════════════════════════════════════════════════
helper_fn = (
    'function getMultiVal(id){'
    'var el=document.getElementById(id);if(!el)return[];'
    'return Array.from(el.options).filter(function(o){return o.selected&&o.value;}).map(function(o){return o.value;});'
    '}\n'
)
marker = 'function doFilter(){'
if marker in html and 'function getMultiVal(' not in html:
    html = html.replace(marker, helper_fn + marker)
    results.append('[JS] getMultiVal() helper added')
else:
    results.append('[JS] getMultiVal() already present or marker missing')

# ══════════════════════════════════════════════════════════════════
# 5. JS: update doFilter — remove cast var, replace dmg/cond/tag with multi-select reads
# ══════════════════════════════════════════════════════════════════

# Remove: var cast=... and var tag=... (old single-value reads)
old_vars = (
    '  var dmg=document.getElementById(\'dmg\').value;\n'
    '  var cond=document.getElementById(\'cond\').value;\n'
    '  var cast=document.getElementById(\'cast\').value;\n'
)
new_vars = (
    '  var dmgVals=getMultiVal(\'dmg\');\n'
    '  var condVals=getMultiVal(\'cond\');\n'
)
if old_vars in html:
    html = html.replace(old_vars, new_vars)
    results.append('[JS] doFilter dmg/cond/cast vars updated')
else:
    results.append('[JS] WARNING: doFilter dmg/cond/cast var block not found')

# Remove old tag single-value read
old_tag_var = "  var tag=(document.getElementById('tag')||{value:''}).value;\n"
new_tag_var = "  var tagVals=getMultiVal('tag');\n"
if old_tag_var in html:
    html = html.replace(old_tag_var, new_tag_var)
    results.append('[JS] doFilter tag var updated')
else:
    results.append('[JS] WARNING: doFilter tag var not found')

# Replace cast filter logic (entire cast block)
old_cast_logic = (
    "    if(cast){var spCost=sp.cost||'Action';"
    "if(cast==='action'&&spCost!=='Action')return false;"
    "if(cast==='bonus'&&spCost!=='Bonus Action')return false;"
    "if(cast==='reaction'&&spCost!=='Reaction')return false;"
    "if(cast==='long'&&!(RITUAL[sp.name]||sp.ritual))return false;"
    "}"
)
if old_cast_logic in html:
    html = html.replace(old_cast_logic, '')
    results.append('[JS] cast filter logic removed from doFilter')
else:
    results.append('[JS] WARNING: cast filter logic not found')

# Replace single dmg filter with multi-value OR logic
old_dmg_logic = "    if(dmg){var spDmg=sp.damage_types||[];if(spDmg.indexOf(dmg)<0)return false;}"
new_dmg_logic = "    if(dmgVals.length){var spDmg=sp.damage_types||[];if(!dmgVals.some(function(d){return spDmg.indexOf(d)>=0;}))return false;}"
if old_dmg_logic in html:
    html = html.replace(old_dmg_logic, new_dmg_logic)
    results.append('[JS] dmg filter → multi OR logic')
else:
    results.append('[JS] WARNING: dmg filter logic not found')

# Replace single cond filter with multi-value OR logic
old_cond_logic = "    if(cond){var spConds=sp.conditions||[];if(spConds.indexOf(cond)<0)return false;}"
new_cond_logic = "    if(condVals.length){var spConds=sp.conditions||[];if(!condVals.some(function(c){return spConds.indexOf(c)>=0;}))return false;}"
if old_cond_logic in html:
    html = html.replace(old_cond_logic, new_cond_logic)
    results.append('[JS] cond filter → multi OR logic')
else:
    results.append('[JS] WARNING: cond filter logic not found')

# Replace single tag filter with multi-value OR logic
old_tag_logic = "    if(tag){var spTags=sp.tags||[];if(spTags.indexOf(tag)<0)return false;}"
new_tag_logic = "    if(tagVals.length){var spTags=sp.tags||[];if(!tagVals.some(function(t){return spTags.indexOf(t)>=0;}))return false;}"
if old_tag_logic in html:
    html = html.replace(old_tag_logic, new_tag_logic)
    results.append('[JS] tag filter → multi OR logic')
else:
    results.append('[JS] WARNING: tag filter logic not found')

# ══════════════════════════════════════════════════════════════════
# 6. JS: update clearAll — handle multi-selects properly, remove cast
# ══════════════════════════════════════════════════════════════════
old_clear = (
    "  ['q','lvl','usg','act','sav','flg','src','cls','race','dmg','cond','cast','comp','tag']"
    ".forEach(function(id){var el=document.getElementById(id);if(el)el.value='';});"
)
new_clear = (
    "  ['q','lvl','usg','act','sav','flg','src','cls','race','comp'].forEach(function(id){var el=document.getElementById(id);if(el)el.value='';});\n"
    "  ['dmg','cond','tag'].forEach(function(id){var el=document.getElementById(id);if(el)Array.from(el.options).forEach(function(o){o.selected=false;});});"
)
if old_clear in html:
    html = html.replace(old_clear, new_clear)
    results.append('[JS] clearAll updated for multi-selects + removed cast')
else:
    results.append('[JS] WARNING: clearAll not found')

# ══════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════
open('bg3-spellbook.html', 'w', encoding='utf-8').write(html)
print('\n'.join(results))
print('\nDone.')
