import re

html = open('bg3-spellbook.html', encoding='utf-8').read()
results = []

# ══════════════════════════════════════════════════════════════════
# 1. Update CC — add Wizard schools and other missing subclass colors
# ══════════════════════════════════════════════════════════════════
old_cc = "var CC={Barbarian:'#FF5722',Bard:'#9C27B0',Cleric:'#FFC107',Druid:'#4CAF50',Fighter:'#F44336',Monk:'#FF9800',Paladin:'#2196F3',Ranger:'#8BC34A',Rogue:'#607D8B',Sorcerer:'#E91E63',Warlock:'#673AB7',Wizard:'#3F51B5','Arcane Trickster':'#90A4AE',Thief:'#78909C',Assassin:'#546E7A','Eldritch Knight':'#EF9A9A','Battle Master':'#EF5350',Berserker:'#FF8A65',Wildheart:'#FFAB91','College of Lore':'#CE93D8','College of Valour':'#BA68C8','College of Swords':'#AB47BC','College of Glamour':'#8E24AA','Life Domain':'#F9A825','Light Domain':'#FFD54F','Nature Domain':'#C0CA33','Tempest Domain':'#29B6F6','Trickery Domain':'#FFB300','War Domain':'#FF8F00','Knowledge Domain':'#FFF176','Death Domain':'#6D4C41','Twilight Domain':'#7E57C2','Peace Domain':'#EC407A','Spores Domain':'#66BB6A','Arcane Domain':'#7986CB','Circle of the Land':'#43A047','Circle of the Moon':'#26A69A','Circle of Spores':'#8D6E63','Oath of Devotion':'#42A5F5','Oath of Ancients':'#26C6DA','Oath of Vengeance':'#5C6BC0','Oath of the Crown':'#1976D2','Oath of Glory':'#039BE5','Gloom Stalker':'#78909C',Hunter:'#AED581','Beast Master':'#BCAAA4','Storm Sorcery':'#80DEEA','Draconic Bloodline':'#F48FB1','Wild Magic':'#FF80AB','The Fiend':'#CE93D8','The Great Old One':'#9575CD','The Archfey':'#F06292','The Hexblade':'#7B1FA2','Way of Shadow':'#455A64','Way of the Open Hand':'#FF7043','Way of the Four Elements':'#FFA726'};"
new_cc = "var CC={Barbarian:'#FF5722',Bard:'#9C27B0',Cleric:'#FFC107',Druid:'#4CAF50',Fighter:'#F44336',Monk:'#FF9800',Paladin:'#2196F3',Ranger:'#8BC34A',Rogue:'#607D8B',Sorcerer:'#E91E63',Warlock:'#673AB7',Wizard:'#3F51B5','Arcane Trickster':'#90A4AE',Thief:'#78909C',Assassin:'#546E7A','Swashbuckler':'#B0BEC5','Eldritch Knight':'#EF9A9A','Battle Master':'#EF5350',Champion:'#E53935','Arcane Archer':'#EF9A9A','Psi Warrior':'#CE93D8',Berserker:'#FF8A65',Wildheart:'#FFAB91',Giant:'#FF8A65','College of Lore':'#CE93D8','College of Valour':'#BA68C8','College of Swords':'#AB47BC','College of Glamour':'#8E24AA','Life Domain':'#F9A825','Light Domain':'#FFD54F','Nature Domain':'#C0CA33','Tempest Domain':'#29B6F6','Trickery Domain':'#FFB300','War Domain':'#FF8F00','Knowledge Domain':'#FFF176','Death Domain':'#6D4C41','Twilight Domain':'#7E57C2','Peace Domain':'#EC407A','Spores Domain':'#66BB6A','Arcane Domain':'#7986CB','Circle of the Land':'#43A047','Circle of the Moon':'#26A69A','Circle of Spores':'#8D6E63','Circle of the Spores':'#8D6E63','Circle of Stars':'#5C6BC0','Circle of the Stars':'#5C6BC0','Oath of Devotion':'#42A5F5','Oath of Ancients':'#26C6DA','Oath of the Ancients':'#26C6DA','Oath of Vengeance':'#5C6BC0','Oath of the Crown':'#1976D2','Oath of Glory':'#039BE5','Oathbreaker':'#37474F','Gloom Stalker':'#78909C',Hunter:'#AED581','Beast Master':'#BCAAA4',Swarmkeeper:'#66BB6A','Storm Sorcery':'#80DEEA','Draconic Bloodline':'#F48FB1','Wild Magic':'#FF80AB','Shadow Magic':'#673AB7','Aberrant Mind':'#9C27B0','The Fiend':'#CE93D8','The Great Old One':'#9575CD','The Archfey':'#F06292','The Hexblade':'#7B1FA2','Way of Shadow':'#455A64','Way of the Open Hand':'#FF7043','Way of the Four Elements':'#FFA726','Way of Mercy':'#EF9A9A','Way of the Astral Self':'#7986CB','Necromancer':'#6D4C41','Abjuration School':'#4CAF50','Conjuration School':'#2196F3','Divination School':'#9C27B0','Enchantment School':'#FF9800','Evocation School':'#F44336','Illusion School':'#00BCD4','Transmutation School':'#8BC34A'};"
if old_cc in html:
    html = html.replace(old_cc, new_cc)
    results.append('[JS] CC updated with all subclass colors')
else:
    results.append('[JS] WARNING: CC not found for replacement')

# ══════════════════════════════════════════════════════════════════
# 2. Update S2C — add all missing subclass→class mappings
# ══════════════════════════════════════════════════════════════════
old_s2c_wizard = "  // Wizard\n  'Necromancer':'Wizard','Conjuration School':'Wizard','Illusion School':'Wizard'"
new_s2c_wizard = (
    "  // Wizard\n"
    "  'Necromancer':'Wizard','Abjuration School':'Wizard','Conjuration School':'Wizard',\n"
    "  'Divination School':'Wizard','Enchantment School':'Wizard','Evocation School':'Wizard',\n"
    "  'Illusion School':'Wizard','Transmutation School':'Wizard'"
)
if old_s2c_wizard in html:
    html = html.replace(old_s2c_wizard, new_s2c_wizard)
    results.append('[JS] S2C Wizard schools expanded')
else:
    results.append('[JS] WARNING: S2C Wizard entry not found')

old_s2c_fighter = "  // Fighter\n  'Battle Master':'Fighter','Eldritch Knight':'Fighter','Arcane Archer':'Fighter',"
new_s2c_fighter = "  // Fighter\n  'Battle Master':'Fighter','Champion':'Fighter','Eldritch Knight':'Fighter','Arcane Archer':'Fighter','Psi Warrior':'Fighter',"
if old_s2c_fighter in html:
    html = html.replace(old_s2c_fighter, new_s2c_fighter)
    results.append('[JS] S2C Fighter updated')
else:
    results.append('[JS] WARNING: S2C Fighter not found')

old_s2c_monk = "  // Monk\n  'Way of the Open Hand':'Monk','Way of Shadow':'Monk','Way of the Four Elements':'Monk','Shadow Magic':'Monk',"
new_s2c_monk = "  // Monk\n  'Way of the Open Hand':'Monk','Way of Shadow':'Monk','Way of the Four Elements':'Monk','Way of Mercy':'Monk','Way of the Astral Self':'Monk','Shadow Magic':'Monk',"
if old_s2c_monk in html:
    html = html.replace(old_s2c_monk, new_s2c_monk)
    results.append('[JS] S2C Monk updated')
else:
    results.append('[JS] WARNING: S2C Monk not found')

old_s2c_sorc = "  // Sorcerer\n  'Draconic Bloodline':'Sorcerer','Storm Sorcery':'Sorcerer','Wild Magic':'Sorcerer',"
new_s2c_sorc = "  // Sorcerer\n  'Draconic Bloodline':'Sorcerer','Storm Sorcery':'Sorcerer','Wild Magic':'Sorcerer','Shadow Magic':'Sorcerer','Aberrant Mind':'Sorcerer',"
# Shadow Magic appears under Monk in the original - add it to Sorcerer too (it appears in both per BG3)
if old_s2c_sorc in html:
    html = html.replace(old_s2c_sorc, new_s2c_sorc)
    results.append('[JS] S2C Sorcerer updated')
else:
    results.append('[JS] WARNING: S2C Sorcerer not found')

old_s2c_rogue = "  // Rogue\n  'Thief':'Rogue','Arcane Trickster':'Rogue','Assassin':'Rogue','Swashbuckler':'Rogue',"
if old_s2c_rogue not in html:
    # might already be there, check
    results.append('[JS] S2C Rogue already complete or not found')
else:
    results.append('[JS] S2C Rogue already complete')

# ══════════════════════════════════════════════════════════════════
# 3. Update PARTY_CLASSES — add all missing subclasses
# ══════════════════════════════════════════════════════════════════
old_pc = """var PARTY_CLASSES = {
  Barbarian: ['Berserker','Wildheart','Giant'],
  Bard:      ['College of Lore','College of Valour','College of Swords','College of Glamour'],
  Cleric:    ['Life Domain','Light Domain','Nature Domain','Tempest Domain','Trickery Domain','War Domain','Knowledge Domain','Death Domain','Arcane Domain','Twilight Domain','Peace Domain','Spores Domain'],
  Druid:     ['Circle of the Land','Circle of the Moon','Circle of the Spores','Circle of Stars'],
  Fighter:   ['Battle Master','Eldritch Knight','Arcane Archer'],
  Monk:      ['Way of the Open Hand','Way of Shadow','Way of the Four Elements','Shadow Magic'],
  Paladin:   ['Oath of Devotion','Oath of the Ancients','Oath of Vengeance','Oath of the Crown','Oath of Glory','Oathbreaker'],
  Ranger:    ['Hunter','Gloom Stalker','Beast Master','Swarmkeeper'],
  Rogue:     ['Thief','Arcane Trickster','Assassin','Swashbuckler'],
  Sorcerer:  ['Draconic Bloodline','Storm Sorcery','Wild Magic'],
  Warlock:   ['The Fiend','The Great Old One','The Archfey','The Hexblade'],
  Wizard:    ['Necromancer','Conjuration School','Illusion School']
};"""
new_pc = """var PARTY_CLASSES = {
  Barbarian: ['Berserker','Wildheart','Giant'],
  Bard:      ['College of Lore','College of Valour','College of Swords','College of Glamour'],
  Cleric:    ['Life Domain','Light Domain','Nature Domain','Tempest Domain','Trickery Domain','War Domain','Knowledge Domain','Death Domain','Arcane Domain','Twilight Domain','Peace Domain','Spores Domain'],
  Druid:     ['Circle of the Land','Circle of the Moon','Circle of the Spores','Circle of Stars'],
  Fighter:   ['Battle Master','Champion','Eldritch Knight','Arcane Archer','Psi Warrior'],
  Monk:      ['Way of the Open Hand','Way of Shadow','Way of the Four Elements','Way of Mercy','Way of the Astral Self'],
  Paladin:   ['Oath of Devotion','Oath of the Ancients','Oath of Vengeance','Oath of the Crown','Oath of Glory','Oathbreaker'],
  Ranger:    ['Hunter','Gloom Stalker','Beast Master','Swarmkeeper'],
  Rogue:     ['Thief','Arcane Trickster','Assassin','Swashbuckler'],
  Sorcerer:  ['Draconic Bloodline','Storm Sorcery','Wild Magic','Shadow Magic','Aberrant Mind'],
  Warlock:   ['The Fiend','The Great Old One','The Archfey','The Hexblade'],
  Wizard:    ['Abjuration School','Conjuration School','Divination School','Enchantment School','Evocation School','Illusion School','Necromancer','Transmutation School']
};"""
if old_pc in html:
    html = html.replace(old_pc, new_pc)
    results.append('[JS] PARTY_CLASSES updated')
else:
    results.append('[JS] WARNING: PARTY_CLASSES not found')

# ══════════════════════════════════════════════════════════════════
# 4. Add buildFilterDropdowns() function + call from loadData()
# ══════════════════════════════════════════════════════════════════
build_fn = r"""function buildFilterDropdowns(){
  // Count spells per class/race token (direct)
  var clsDirect={},raceDirect={};
  all.forEach(function(sp){
    (sp.classes||'').split(',').forEach(function(t){
      var b=t.trim().replace(/\s*\([^)]+\)/g,'').trim();
      if(b)clsDirect[b]=(clsDirect[b]||0)+1;
    });
    (sp.races||'').split(',').forEach(function(t){
      var b=t.trim().replace(/\s*\([^)]+\)/g,'').trim();
      if(b)raceDirect[b]=(raceDirect[b]||0)+1;
    });
  });
  function baseClsCount(cls){
    var n=clsDirect[cls]||0;
    Object.keys(S2C).forEach(function(s){if(S2C[s]===cls)n+=clsDirect[s]||0;});
    return n;
  }
  function baseRaceCount(race){
    var n=raceDirect[race]||0;
    Object.keys(S2R).forEach(function(s){if(S2R[s]===race)n+=raceDirect[s]||0;});
    return n;
  }
  var clsSel=document.getElementById('cls');
  if(clsSel){
    var cv=clsSel.value;
    var baseClasses=Object.keys(CC).filter(function(k){return !S2C[k];}).sort();
    var h='<option value="">All Classes</option>';
    baseClasses.forEach(function(cls){
      var subs=Object.keys(S2C).filter(function(k){return S2C[k]===cls;}).sort();
      var cnt=baseClsCount(cls);
      h+='<optgroup label="'+cls+'">';
      h+='<option value="'+cls+'"'+(cnt===0?' disabled':'')+'>'+cls+'</option>';
      subs.forEach(function(sub){
        var sc=clsDirect[sub]||0;
        h+='<option value="'+sub+'"'+(sc===0?' disabled':'')+'>└ '+sub+'</option>';
      });
      h+='</optgroup>';
    });
    clsSel.innerHTML=h;
    clsSel.value=cv;
  }
  var raceSel=document.getElementById('race');
  if(raceSel){
    var rv=raceSel.value;
    var baseRaces=Object.keys(RC).filter(function(k){return !S2R[k];}).sort();
    var rh='<option value="">All Races</option>';
    baseRaces.forEach(function(race){
      var subs=Object.keys(S2R).filter(function(k){return S2R[k]===race;}).sort();
      var cnt=baseRaceCount(race);
      rh+='<optgroup label="'+race+'">';
      rh+='<option value="'+race+'"'+(cnt===0?' disabled':'')+'>'+race+'</option>';
      subs.forEach(function(sub){
        var sc=raceDirect[sub]||0;
        rh+='<option value="'+sub+'"'+(sc===0?' disabled':'')+'>└ '+sub+'</option>';
      });
      rh+='</optgroup>';
    });
    raceSel.innerHTML=rh;
    raceSel.value=rv;
  }
}
"""

marker = 'function isVariant('
if marker in html and 'function buildFilterDropdowns(' not in html:
    html = html.replace(marker, build_fn + marker)
    results.append('[JS] buildFilterDropdowns() added')
else:
    results.append('[JS] WARNING: buildFilterDropdowns insertion point not found or already exists')

# Call buildFilterDropdowns() at end of loadData(), before doFilter()
old_loaddone = '  doFilter();\n  notify'
new_loaddone = '  buildFilterDropdowns();\n  doFilter();\n  notify'
if old_loaddone in html:
    html = html.replace(old_loaddone, new_loaddone, 1)
    results.append('[JS] buildFilterDropdowns() called from loadData()')
else:
    results.append('[JS] WARNING: loadData doFilter call not found')

# ══════════════════════════════════════════════════════════════════
# 5. Replace static cls/race select content with minimal placeholders
#    (JS will populate them dynamically)
# ══════════════════════════════════════════════════════════════════
# Class select — strip all static optgroup content
cls_pattern = r'(<select id="cls"[^>]*>).*?(</select>)'
cls_replace = r'\1\n          <option value="">All Classes</option>\n        \2'
new_html, n = re.subn(cls_pattern, cls_replace, html, count=1, flags=re.DOTALL)
if n:
    html = new_html
    results.append('[HTML] cls select replaced with placeholder')
else:
    results.append('[HTML] WARNING: cls select not found')

# Race select
race_pattern = r'(<select id="race"[^>]*>).*?(</select>)'
race_replace = r'\1\n          <option value="">All Races</option>\n        \2'
new_html, n = re.subn(race_pattern, race_replace, html, count=1, flags=re.DOTALL)
if n:
    html = new_html
    results.append('[HTML] race select replaced with placeholder')
else:
    results.append('[HTML] WARNING: race select not found')

# ══════════════════════════════════════════════════════════════════
# WRITE
# ══════════════════════════════════════════════════════════════════
open('bg3-spellbook.html', 'w', encoding='utf-8').write(html)
print('\n'.join(results))
print('\nDone.')
