import re

html = open('bg3-spellbook.html', encoding='utf-8').read()
results = []

# ══════════════════════════════════════════════════════════════════
# 1. Replace pill containers back to custom multi-select wrappers
# ══════════════════════════════════════════════════════════════════
def replace_pills_with_ms(h, comment, label, wrap_id, default_lbl):
    pattern = (
        r'      <!-- ' + re.escape(comment) + r' -->\n'
        r'      <div class="fg">\n'
        r'        <label>' + re.escape(label) + r'</label>\n'
        r'        <div class="filter-pills[^"]*" id="[^"]+"></div>\n'
        r'      </div>\n'
    )
    replacement = (
        '      <!-- ' + comment + ' -->\n'
        '      <div class="fg">\n'
        '        <label>' + label + '</label>\n'
        '        <div class="ms-wrap" id="' + wrap_id + '" data-default="' + default_lbl + '"></div>\n'
        '      </div>\n'
    )
    new_h, n = re.subn(pattern, replacement, h, count=1, flags=re.DOTALL)
    return new_h, n > 0

html, ok = replace_pills_with_ms(html, 'Damage Type', 'Damage',    'dmgWrap',  'Any Damage')
results.append('[HTML] Damage → ms-wrap' if ok else '[HTML] WARNING: Damage pills not found')

html, ok = replace_pills_with_ms(html, 'Condition',   'Condition', 'condWrap', 'Any Condition')
results.append('[HTML] Condition → ms-wrap' if ok else '[HTML] WARNING: Condition pills not found')

html, ok = replace_pills_with_ms(html, 'Spell Tags',  'Tag',       'tagWrap',  'Any Tag')
results.append('[HTML] Tag → ms-wrap' if ok else '[HTML] WARNING: Tag pills not found')

# ══════════════════════════════════════════════════════════════════
# 2. Replace pill CSS with custom multi-select CSS
# ══════════════════════════════════════════════════════════════════
old_pill_css = """
/* Filter pill containers (Damage, Condition, Tag) */
.filter-pills { display: flex; flex-wrap: wrap; gap: 3px; align-items: flex-start; max-width: 300px; }
.tag-pills { max-height: 72px; overflow-y: auto; max-width: 400px; }
"""
new_ms_css = """
/* Custom multi-select dropdowns */
.ms-wrap { position: relative; width: 110px; }
.ms-btn {
  width: 100%; padding: 5px 26px 5px 8px; text-align: left;
  background: var(--bg3); border: 1px solid var(--border);
  color: var(--text); border-radius: 3px; font-size: 12px;
  font-family: 'Crimson Pro', serif; cursor: pointer;
  transition: border-color .15s; position: relative; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}
.ms-btn:focus, .ms-btn.open { border-color: var(--gold); outline: none; }
.ms-btn::after { content: '▾'; position: absolute; right: 7px; top: 50%; transform: translateY(-50%); color: var(--text3); font-size: 10px; pointer-events: none; }
.ms-btn.active { border-color: var(--gold); color: var(--gold2); }
.ms-drop {
  display: none; position: absolute; top: calc(100% + 2px); left: 0;
  min-width: 130px; max-height: 220px; overflow-y: auto;
  background: var(--bg3); border: 1px solid var(--border2);
  border-radius: 3px; z-index: 200;
  box-shadow: 0 6px 20px rgba(0,0,0,.4);
}
.ms-drop.open { display: block; }
.ms-item {
  display: flex; align-items: center; gap: 7px;
  padding: 5px 10px; cursor: pointer; font-size: 12px;
  font-family: 'Crimson Pro', serif; color: var(--text2);
  transition: background .1s; white-space: nowrap; user-select: none;
}
.ms-item:hover { background: var(--rune); color: var(--text); }
.ms-item input[type=checkbox] { accent-color: var(--gold); cursor: pointer; width: 12px; height: 12px; flex-shrink: 0; }
.ms-item.checked { color: var(--gold2); }
"""
if old_pill_css in html:
    html = html.replace(old_pill_css, new_ms_css)
    results.append('[CSS] pill CSS replaced with ms-dropdown CSS')
else:
    html = html.replace('</style>', new_ms_css + '</style>', 1)
    results.append('[CSS] ms-dropdown CSS added')

# ══════════════════════════════════════════════════════════════════
# 3. Replace pill JS with custom multi-select JS
# ══════════════════════════════════════════════════════════════════
old_pill_js = r"""function toggleFPill(s,el){var v=el.dataset.v;if(s.has(v)){s.delete(v);el.classList.remove('on');}else{s.add(v);el.classList.add('on');}doFilter();}

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
new_ms_js = r"""function msOpen(wrapId){
  var wrap=document.getElementById(wrapId);
  var drop=wrap.querySelector('.ms-drop');
  var btn=wrap.querySelector('.ms-btn');
  var isOpen=drop.classList.contains('open');
  // close all
  document.querySelectorAll('.ms-drop.open').forEach(function(d){d.classList.remove('open');});
  document.querySelectorAll('.ms-btn.open').forEach(function(b){b.classList.remove('open');});
  if(!isOpen){drop.classList.add('open');btn.classList.add('open');}
}
function msTick(wrapId,set,cb){
  var v=cb.value;
  var item=cb.parentElement;
  if(cb.checked){set.add(v);item.classList.add('checked');}else{set.delete(v);item.classList.remove('checked');}
  msUpdateLabel(wrapId,set);
  doFilter();
}
function msUpdateLabel(wrapId,set){
  var wrap=document.getElementById(wrapId);
  var btn=wrap.querySelector('.ms-btn');
  var def=wrap.dataset.default||'Any';
  if(set.size===0){btn.textContent=def;btn.classList.remove('active');}
  else if(set.size===1){btn.textContent=[...set][0];btn.classList.add('active');}
  else{btn.textContent=set.size+' selected';btn.classList.add('active');}
}
function msClear(wrapId,set){
  set.clear();
  var wrap=document.getElementById(wrapId);
  wrap.querySelectorAll('input[type=checkbox]').forEach(function(cb){cb.checked=false;});
  wrap.querySelectorAll('.ms-item').forEach(function(i){i.classList.remove('checked');});
  msUpdateLabel(wrapId,set);
}
document.addEventListener('click',function(e){
  if(!e.target.closest('.ms-wrap')){
    document.querySelectorAll('.ms-drop.open').forEach(function(d){d.classList.remove('open');});
    document.querySelectorAll('.ms-btn.open').forEach(function(b){b.classList.remove('open');});
  }
});
(function initMultiSelects(){
  var MS=[
    {id:'dmgWrap', set:'aDmg', items:['Acid','Bludgeoning','Cold','Fire','Force','Lightning','Necrotic','Piercing','Poison','Psychic','Radiant','Slashing','Thunder']},
    {id:'condWrap',set:'aCond',items:['Blinded','Charmed','Deafened','Frightened','Grappled','Incapacitated','Invisible','Paralyzed','Petrified','Poisoned','Prone','Restrained','Stunned','Unconscious']},
    {id:'tagWrap', set:'aTag', items:['AoE','Banishment','Buff','Concentration','Control','Damage','Debuff','Defensive','Divination','Enchantment','Environment','Exploration','Fear','Healing','Illumination','Illusion','Melee','Movement','Necromancy','Ranger','Reaction','Self','Smite','Social','Special','Stealth','Summoning','Support','Teleportation','Transmutation','Trap','Utility']}
  ];
  MS.forEach(function(ms){
    var wrap=document.getElementById(ms.id); if(!wrap)return;
    var btn='<button class="ms-btn" type="button" onclick="msOpen(\''+ms.id+'\')" >'+wrap.dataset.default+'</button>';
    var items=ms.items.map(function(v){
      return '<label class="ms-item"><input type="checkbox" value="'+v+'" onchange="msTick(\''+ms.id+'\','+ms.set+',this)">'+v+'</label>';
    }).join('');
    wrap.innerHTML=btn+'<div class="ms-drop">'+items+'</div>';
  });
})();

"""
if old_pill_js in html:
    html = html.replace(old_pill_js, new_ms_js)
    results.append('[JS] pill JS replaced with ms-dropdown JS')
else:
    results.append('[JS] WARNING: pill JS not found — may need manual check')

# ══════════════════════════════════════════════════════════════════
# 4. Update clearAll to use msClear
# ══════════════════════════════════════════════════════════════════
old_clear = (
    "  aDmg.clear();aCond.clear();aTag.clear();\n"
    "  document.querySelectorAll('#dmgPills .spill,#condPills .spill,#tagPills .spill').forEach(function(el){el.classList.remove('on');});"
)
new_clear = (
    "  msClear('dmgWrap',aDmg);msClear('condWrap',aCond);msClear('tagWrap',aTag);"
)
if old_clear in html:
    html = html.replace(old_clear, new_clear)
    results.append('[JS] clearAll updated for ms-dropdown')
else:
    results.append('[JS] WARNING: clearAll pill block not found')

open('bg3-spellbook.html', 'w', encoding='utf-8').write(html)
print('\n'.join(results))
print('\nDone.')
