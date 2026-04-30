"""
patch_components.py — Manually assigns verbal/somatic/material component data
for the ~55 spells whose wiki pages didn't expose component flags.

Rules applied:
  - Continuation/sub-actions (Activate X, Move X, Reapply, Launch, Hurl, Dismiss): no components
  - Natural creature abilities (breath weapons, psionics, howls): no components
  - Physical strikes (Pierce/Slash/Bludgeon the Weak, etc.): somatic-only
  - Counterspell: somatic-only (5e RAW — castable while Silenced)
  - Known D&D 5e spells: follow 5e component list (BG3 matches closely)
  - Variants inherit parent's component profile
  - Vocal/prayer invocations: verbal-only
  - Everything else (general spells/abilities): VS, no material
"""

import json
from pathlib import Path

ROOT      = Path(__file__).resolve().parent.parent
DATA_FILE = str(ROOT / 'data' / 'wiki_data.json')

wiki = json.load(open(DATA_FILE, encoding='utf-8'))

T, F = True, False

MANUAL = {
    # ── Continuation / sub-actions (not new casts, no components) ────────
    'Activate Witch Bolt':                  {'verbal':F,'somatic':F,'material':F},
    'Move Moonbeam':                        {'verbal':F,'somatic':F,'material':F},
    'Heat Metal: Reapply Damage':           {'verbal':F,'somatic':F,'material':F},
    "Otiluke's Freezing Sphere (Launch)":   {'verbal':F,'somatic':F,'material':F},
    'Produce Flame: Hurl':                  {'verbal':F,'somatic':F,'material':F},
    'Cosmic Omen: Ability Check':           {'verbal':F,'somatic':F,'material':F},
    'Dismiss Arcane Lock':                  {'verbal':F,'somatic':F,'material':F},
    'Arcane Critical':                      {'verbal':F,'somatic':F,'material':F},

    # ── Natural creature abilities ────────────────────────────────────────
    'Acid Breath':                          {'verbal':F,'somatic':F,'material':F},
    'Frost Breath':                         {'verbal':F,'somatic':F,'material':F},
    'Howl of the Dead':                     {'verbal':F,'somatic':F,'material':F},

    # ── Psionic abilities (no components by nature) ───────────────────────
    'Githyanki Psionics: Mage Hand':        {'verbal':F,'somatic':F,'material':F},
    'Githyanki Psionics: Jump':             {'verbal':F,'somatic':F,'material':F},

    # ── Physical strikes (somatic only) ──────────────────────────────────
    'Pierce the Weak':                      {'verbal':F,'somatic':T,'material':F},
    'Slash the Weak':                       {'verbal':F,'somatic':T,'material':F},
    'Bludgeon the Weak':                    {'verbal':F,'somatic':T,'material':F},
    'Hellflame Cleave':                     {'verbal':F,'somatic':T,'material':F},
    'Fanatic Retaliation':                  {'verbal':F,'somatic':T,'material':F},

    # ── Counterspell: S-only reaction (5e RAW, castable while Silenced!) ──
    'Counterspell':                         {'verbal':F,'somatic':T,'material':F},

    # ── Known D&D 5e spells ───────────────────────────────────────────────
    'Booming Blade':                        {'verbal':T,'somatic':F,'material':F},  # V,M in 5e; BG3 drops M
    'Banishing Smite':                      {'verbal':T,'somatic':F,'material':F},  # V only bonus action
    'Fly':                                  {'verbal':T,'somatic':T,'material':F},
    "Otiluke's Freezing Sphere":            {'verbal':T,'somatic':T,'material':F},
    'Enlarge (Duergar)':                    {'verbal':T,'somatic':T,'material':F},
    'Invisibility (Duergar)':               {'verbal':T,'somatic':T,'material':F},
    'Entangle (Dryad)':                     {'verbal':T,'somatic':T,'material':F},

    # ── Variants inheriting parent components ─────────────────────────────
    'Animate Dead: Zombie Batallion':       {'verbal':T,'somatic':T,'material':F},  # Animate Dead = VS
    'Eyes of the Dark: Darkness':           {'verbal':T,'somatic':T,'material':F},  # Darkness = VS
    'Magic Missile (Illithid Arcanist)':    {'verbal':T,'somatic':T,'material':F},  # Magic Missile = VS
    'Rays of Fire (Mol)':                   {'verbal':T,'somatic':T,'material':F},  # Fire Bolt-like = VS
    'Rays of Fire (Cantrip)':               {'verbal':T,'somatic':T,'material':F},
    'Find Familiar: Cheeky Quasit':         {'verbal':T,'somatic':T,'material':F},  # Find Familiar = VS

    # ── Vocal/prayer invocations (verbal only) ────────────────────────────
    "Umberlee's Praise":                    {'verbal':T,'somatic':F,'material':F},
    'Wail of Loss (Assistant)':             {'verbal':T,'somatic':F,'material':F},

    # ── General spells/special abilities (VS, no material) ───────────────
    'Ghoulish Touch':                       {'verbal':T,'somatic':T,'material':F},
    "Karsus' Compulsion":                   {'verbal':T,'somatic':T,'material':F},
    'Beckoning Darkness':                   {'verbal':T,'somatic':T,'material':F},
    'Brand the Weak':                       {'verbal':T,'somatic':T,'material':F},
    'Disrobing Blinkstep':                  {'verbal':T,'somatic':T,'material':F},
    'Luminous Arrow':                       {'verbal':T,'somatic':T,'material':F},
    'Heartwrench':                          {'verbal':T,'somatic':T,'material':F},
    "Selune's Dream":                       {'verbal':T,'somatic':T,'material':F},
    'Ensnaring Shock':                      {'verbal':T,'somatic':T,'material':F},
    'Pulling Web':                          {'verbal':T,'somatic':T,'material':F},
    'Stand Like Stone':                     {'verbal':T,'somatic':T,'material':F},
    'Incongruent Splash':                   {'verbal':T,'somatic':T,'material':F},
    'Sanctuary of Loss':                    {'verbal':T,'somatic':T,'material':F},
    'Tightening Orbit':                     {'verbal':T,'somatic':T,'material':F},
    "Gargoyle's Countenance":               {'verbal':T,'somatic':T,'material':F},
    'Disconcerting Visage (Tactician)':     {'verbal':T,'somatic':T,'material':F},
    'Sacrifice Soul':                       {'verbal':T,'somatic':T,'material':F},
    'Terrifying Visage (Tactician)':        {'verbal':T,'somatic':T,'material':F},
    'Aegis of the Absolute':               {'verbal':T,'somatic':T,'material':F},
    "Bane's Wrath":                         {'verbal':T,'somatic':T,'material':F},
    'Restore Vitality':                     {'verbal':T,'somatic':T,'material':F},
}

patched = 0
for name, components in MANUAL.items():
    if name not in wiki:
        wiki[name] = {'description':'','range':'','area':'','duration':'','recharge':'','icon':''}
    wiki[name].update(components)
    patched += 1

json.dump(wiki, open(DATA_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

non_verbal = [n for n, v in MANUAL.items() if not v['verbal']]
print(f'Patched {patched} spells')
print(f'Non-verbal in manual set ({len(non_verbal)}): {", ".join(non_verbal)}')
