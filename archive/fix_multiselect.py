import re

html = open('bg3-spellbook.html', encoding='utf-8').read()
results = []

# ══════════════════════════════════════════════════════════════════
# 1. Replace <select multiple> blocks with pill containers in HTML
# ══════════════════════════════════════════════════════════════════

def replace_select_with_pills(h, select_id, label, pill_id, container_cls='filter-pills'):
    pattern = (
        r'      <!-- ' + re.escape(label) + r' -->\n'
        r'      <div class="fg">\n'
        r'        <label>' + re.escape(label) + r'</label>\n'
        r'        <select id="' + re.escape(select_id) + r'".*?</select>\n'
        r'      </div>\n'
    )
    replacement = (
        '      <!-- ' + label + ' -->\n'
        '      <div class="fg">\n'
        '        <label>' + label + '</label>\n'
        '        <div class="' + container_cls + '" id="' + pill_id + '"></div>\n'
        '      </div>\n'
    )
    new_h, n = re.subn(pattern, replacement, h, count=1, flags=re.DOTALL)
    return new_h, n > 0

html, ok = replace_select_with_pills(html, 'dmg',  'Damage',    'dmgPills')
results.append('[HTML] Damage → pill container' if ok else '[HTML] WARNING: Damage select not found')

html, ok = replace_select_with_pills(html, 'cond', 'Condition', 'condPills')
results.append('[HTML] Condition → pill container' if ok else '[HTML] WARNING: Condition select not found')

html, ok = replace_select_with_pills(html, 'tag',  'Tag',       'tagPills',  'filter-pills tag-pills')
results.append('[HTML] Tag → pill container' if ok else '[HTML] WARNING: Tag select not found')

# ══════════════════════════════════════════════════════════════════
# 2. Add CSS for pill containers
# ══════════════════════════════════════════════════════════════════
new_css = """
/* Filter pill containers (Damage, Condition, Tag) */
.filter-pills { display: flex; flex-wrap: wrap; gap: 3px; align-items: flex-start; max-width: 300px; }
.tag-pills { max-height: 72px; overflow-y: auto; max-width: 400px; }
"""
# Replace the old multi-select CSS we added earlier
old_ms_css = (
    '\n/* Multi-select filters */\n'
    'select[multiple] { height: auto; padding: 2px; cursor: pointer; }\n'
    'select[multiple] option { padding: 3px 7px; border-radius: 2px; }\n'
    "select[multiple] option:checked { background: linear-gradient(var(--gold), var(--gold)); color: var(--bg); font-weight: 600; }\n"
)
if old_ms_css in html:
    html = html.replace(old_ms_css, new_css)
    results.append('[CSS] multi-select CSS replaced with pill container CSS')
elif new_css.strip() not in html:
    html = html.replace('</style>', new_css + '</style>', 1)
    results.append('[CSS] pill container CSS added')
else:
    results.append('[CSS] pill container CSS already present')

# ══════════════════════════════════════════════════════════════════
# 3. Add aDmg, aCond, aTag Sets to global state
# ══════════════════════════════════════════════════════════════════
old_state = 'var activeMode={}, aSchools=new Set(), collCols=new Set(), collChars=new Set();'
new_state = 'var activeMode={}, aSchools=new Set(), aDmg=new Set(), aCond=new Set(), aTag=new Set(), collCols=new Set(), collChars=new Set();'
if old_state in html:
    html = html.replace(old_state, new_state)
    results.append('[JS] aDmg/aCond/aTag Sets added to global state')
else:
    results.append('[JS] WARNING: global state line not found')

# ══════════════════════════════════════════════════════════════════
# 4. Add toggleFPill() function + pill init IIFE
#    Insert before the existing initSchoolPills IIFE
# ══════════════════════════════════════════════════════════════════
pill_js = r"""function toggleFPill(s,el){var v=el.dataset.v;if(s.has(v)){s.delete(v);el.classList.remove('on');}else{s.add(v);el.classList.add('on');}doFilter();}

(function initFilterPills(){
  var DMG_COLORS={
    Acid:'#8BC34A',Bludgeoning:'#78909C',Cold:'#4FC3F7',Fire:'#FF5722',
    Force:'#9C27B0',Lightning:'#FDD835',Necrotic:'#546E7A',Piercing:'#B0BEC5',
    Poison:'#558B2F',Psychic:'#E91E63',Radiant:'#FFE082',Slashing:'#EF5350',Thunder:'#29B6F6'
  };
  var COND_LIST=['Blinded','Charmed','Deafened','Frightened','Grappled','Incapacitated',
    'Invisible','Paralyzed','Petrified','Poisoned','Prone','Restrained','Stunned','Unconscious'];
  var TAG_LIST=['AoE','Banishment','Buff','Concentration','Control','Damage','Debuff','Defensive',
    'Divination','Enchantment','Environment','Exploration','Fear','Healing','Illumination',
    'Illusion','Melee','Movement','Necromancy','Ranger','Reaction','Self','Smite','Social',
    'Special','Stealth','Summoning','Support','Teleportation','Transmutation','Trap','Utility'];
  function makePills(containerId, list, colorFn, set){
    var p=document.getElementById(containerId); if(!p)return;
    p.innerHTML=list.map(function(v){
      var bg=colorFn(v);
      return '<span class="spill" data-v="'+v+'" style="background:'+bg+';color:'+(il(bg)?'#1a1a1a':'#fff')+'" onclick="toggleFPill('+set+',this)">'+v+'</span>';
    }).join('');
  }
  makePills('dmgPills', Object.keys(DMG_COLORS), function(v){return DMG_COLORS[v];}, 'aDmg');
  makePills('condPills', COND_LIST, hc, 'aCond');
  makePills('tagPills',  TAG_LIST,  hc, 'aTag');
})();

"""
marker = '(function initSchoolPills(){'
if marker in html and 'function toggleFPill(' not in html:
    html = html.replace(marker, pill_js + marker)
    results.append('[JS] toggleFPill() + initFilterPills() added')
else:
    results.append('[JS] WARNING: initSchoolPills marker not found or toggleFPill already exists')

# ══════════════════════════════════════════════════════════════════
# 5. Update doFilter — replace getMultiVal() reads with Set checks
# ══════════════════════════════════════════════════════════════════

# Remove getMultiVal reads for dmg/cond and tag
old_dmg_cond_read = (
    "  var dmgVals=getMultiVal('dmg');\n"
    "  var condVals=getMultiVal('cond');\n"
)
if old_dmg_cond_read in html:
    html = html.replace(old_dmg_cond_read, '')
    results.append('[JS] dmgVals/condVals reads removed from doFilter')
else:
    results.append('[JS] WARNING: dmgVals/condVals reads not found')

old_tag_read = "  var tagVals=getMultiVal('tag');\n"
if old_tag_read in html:
    html = html.replace(old_tag_read, '')
    results.append('[JS] tagVals read removed from doFilter')
else:
    results.append('[JS] WARNING: tagVals read not found')

# Replace filter logic to use Sets
old_dmg_logic = "    if(dmgVals.length){var spDmg=sp.damage_types||[];if(!dmgVals.some(function(d){return spDmg.indexOf(d)>=0;}))return false;}"
new_dmg_logic = "    if(aDmg.size){var spDmg=sp.damage_types||[];if(![...aDmg].some(function(d){return spDmg.indexOf(d)>=0;}))return false;}"
if old_dmg_logic in html:
    html = html.replace(old_dmg_logic, new_dmg_logic)
    results.append('[JS] dmg filter uses aDmg Set')
else:
    results.append('[JS] WARNING: dmg filter logic not found')

old_cond_logic = "    if(condVals.length){var spConds=sp.conditions||[];if(!condVals.some(function(c){return spConds.indexOf(c)>=0;}))return false;}"
new_cond_logic = "    if(aCond.size){var spConds=sp.conditions||[];if(![...aCond].some(function(c){return spConds.indexOf(c)>=0;}))return false;}"
if old_cond_logic in html:
    html = html.replace(old_cond_logic, new_cond_logic)
    results.append('[JS] cond filter uses aCond Set')
else:
    results.append('[JS] WARNING: cond filter logic not found')

old_tag_logic = "    if(tagVals.length){var spTags=sp.tags||[];if(!tagVals.some(function(t){return spTags.indexOf(t)>=0;}))return false;}"
new_tag_logic = "    if(aTag.size){var spTags=sp.tags||[];if(![...aTag].some(function(t){return spTags.indexOf(t)>=0;}))return false;}"
if old_tag_logic in html:
    html = html.replace(old_tag_logic, new_tag_logic)
    results.append('[JS] tag filter uses aTag Set')
else:
    results.append('[JS] WARNING: tag filter logic not found')

# ══════════════════════════════════════════════════════════════════
# 6. Remove getMultiVal() — no longer needed
# ══════════════════════════════════════════════════════════════════
old_helper = (
    'function getMultiVal(id){'
    'var el=document.getElementById(id);if(!el)return[];'
    'return Array.from(el.options).filter(function(o){return o.selected&&o.value;}).map(function(o){return o.value;});'
    '}\n'
)
if old_helper in html:
    html = html.replace(old_helper, '')
    results.append('[JS] getMultiVal() removed (no longer needed)')
else:
    results.append('[JS] getMultiVal() not found (may already be gone)')

# ══════════════════════════════════════════════════════════════════
# 7. Update clearAll — clear Sets + deselect pills, remove multi-select reset
# ══════════════════════════════════════════════════════════════════
old_clear_multi = (
    "  ['q','lvl','usg','act','sav','flg','src','cls','race'].forEach(function(id){var el=document.getElementById(id);if(el)el.value='';});\n"
    "  ['dmg','cond','tag'].forEach(function(id){var el=document.getElementById(id);if(el)Array.from(el.options).forEach(function(o){o.selected=false;});});"
)
new_clear_multi = (
    "  ['q','lvl','usg','act','sav','flg','src','cls','race'].forEach(function(id){var el=document.getElementById(id);if(el)el.value='';});\n"
    "  aDmg.clear();aCond.clear();aTag.clear();\n"
    "  document.querySelectorAll('#dmgPills .spill,#condPills .spill,#tagPills .spill').forEach(function(el){el.classList.remove('on');});"
)
if old_clear_multi in html:
    html = html.replace(old_clear_multi, new_clear_multi)
    results.append('[JS] clearAll updated for pill Sets')
else:
    results.append('[JS] WARNING: clearAll multi-select block not found')

# ══════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════
open('bg3-spellbook.html', 'w', encoding='utf-8').write(html)
print('\n'.join(results))
print('\nDone.')
