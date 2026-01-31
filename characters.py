# Character Definitions
from settings import *

# Vivid Color Palette
VIVID_CRIMSON = (220, 20, 60)
VIVID_GOLD = (255, 223, 0)
VIVID_ORANGE = (255, 100, 20)
VIVID_BROWN = (160, 85, 45)
VIVID_PURPLE = (180, 60, 220)
VIVID_BLUE = (0, 191, 255)
VIVID_GREEN = (50, 255, 50)
VIVID_DARK = (40, 40, 45)
VIVID_WHITE = (255, 255, 255)
VIVID_PINK = (255, 105, 180)
VIVID_RED = (255, 40, 40)

class CharacterData:
    """Data class holding character stats and properties."""

    def __init__(self, name, speed, health, damage, special_name, special_desc,
                 color, secondary_color, attack_type='melee', can_fly=False, heals=False):
        self.name = name
        self.speed = speed
        self.health = health
        self.max_health = health
        self.damage = damage
        self.special_name = special_name
        self.special_desc = special_desc
        self.color = color
        self.secondary_color = secondary_color
        self.attack_type = attack_type  # 'melee' or 'ranged'
        self.can_fly = can_fly
        self.heals = heals


# Character definitions
CHARACTERS = {
    # RANGED characters: Lower damage but safe, uses MANA (limited shots)
    'Harry': CharacterData(
        name='Harry',
        speed=5,
        health=100,
        damage=12,  # Reduced: ranged = safe but weaker
        special_name='Patronus Charm',
        special_desc='Summons a stag to charge forward',
        color=VIVID_CRIMSON,
        secondary_color=VIVID_GOLD,
        attack_type='ranged'
    ),
    # MELEE characters: Higher damage, unlimited attacks, must get close (risky)
    'Ron': CharacterData(
        name='Ron',
        speed=4,
        health=120,
        damage=35,  # Increased: melee = risky but powerful
        special_name='Howler Shout',
        special_desc='Stuns and damages nearby enemies',
        color=VIVID_ORANGE,
        secondary_color=VIVID_BROWN,
        attack_type='melee'
    ),
    'Hermione': CharacterData(
        name='Hermione',
        speed=6,
        health=85,
        damage=12,  # Reduced: ranged = safe but weaker
        special_name='Spell Barrage',
        special_desc='Rapid fire homing magical orbs',
        color=VIVID_PURPLE,
        secondary_color=VIVID_BLUE,
        attack_type='ranged'
    ),
    'Voldemort': CharacterData(
        name='Voldemort',
        speed=5,
        health=85,
        damage=18,  # Reduced but still "powerful caster"
        special_name='Avada Kedavra',
        special_desc='Devastating green beam of doom',
        color=VIVID_DARK,
        secondary_color=VIVID_GREEN,
        attack_type='ranged'
    ),
    'Hagrid': CharacterData(
        name='Hagrid',
        speed=4,
        health=150,
        damage=45,  # Increased: slow tank hits HARD
        special_name='Earthquake',
        special_desc='Smashes ground to clear the screen',
        color=VIVID_BROWN,
        secondary_color=VIVID_DARK,
        attack_type='melee'
    ),
    'Unicorn': CharacterData(
        name='Unicorn',
        speed=7,
        health=90,
        damage=28,  # Increased: fast melee fighter
        special_name='Mystic Heal',
        special_desc='Heals allies and burns darkness',
        color=VIVID_WHITE,
        secondary_color=VIVID_PINK,
        attack_type='melee',
        heals=True
    ),
    'Dragon': CharacterData(
        name='Dragon',
        speed=4,
        health=110,
        damage=15,  # Reduced: ranged + flight = needs tradeoff
        special_name='Inferno Breath',
        special_desc='Unleashes a wall of rising fire',
        color=VIVID_RED,
        secondary_color=VIVID_ORANGE,
        attack_type='ranged',
        can_fly=True
    )
}

# Character selection order
CHARACTER_ORDER = ['Harry', 'Ron', 'Hermione', 'Voldemort', 'Hagrid', 'Unicorn', 'Dragon']


def get_character(name):
    """Get a fresh copy of character data."""
    original = CHARACTERS[name]
    return CharacterData(
        name=original.name,
        speed=original.speed,
        health=original.health,
        damage=original.damage,
        special_name=original.special_name,
        special_desc=original.special_desc,
        color=original.color,
        secondary_color=original.secondary_color,
        attack_type=original.attack_type,
        can_fly=original.can_fly,
        heals=original.heals
    )
