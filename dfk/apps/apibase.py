from enum import auto, Enum

JEWEL_MULTIPLIER = 1000000000000000000

PROFESSIONS_MAP = {
    'foraging': {
        'class': {'Sage', 'Summoner', 'DarkKnight', 'Ninja', 'Archer', 'Dragoon', 'Wizard', 'Priest'},
        'stats': {'DEX', 'INT'},
    },
    'fishing': {
        'class': {'Ninja', 'Thief', 'Sage', 'Dragoon', 'Pirate'},
        'stats': {'LCK', 'AGI'},
    },
    'gardening': {
        'class': {'Sage', 'Paladin', 'Summoner', 'Priest', 'Wizard', 'Dragoon'}, #'DarkKnight', 'Monk', 'Knight'},
        'stats': {'WIS', 'VIT'}
    },
    'mining': {
        'class': {'Paladin', 'Dragoon', 'DarkKnight', 'Knight', 'Warrior', 'Pirate'}, #'Archer', 'Monk', 'Thief'},
        'stats': {'STR', 'END'},
    }
}

RARITY_TO_COLOR = [
    'white',    # common
    'green',    # uncommon
    'blue',     # rare
    'orange',   # legendary
    'purple',   # mythic
]

STAT_TO_ABBREV = {
    'strength': 'STR',
    'agility': 'AGI',
    'endurance': 'END',
    'wisdom': 'WIS',
    'dexterity': 'DEX',
    'vitality': 'VIT',
    'intelligence': 'INT',
    'luck': 'LCK'
}
ABBREV_TO_STAT = { v: k for k,v in STAT_TO_ABBREV.items() }

class EndpointType(Enum):
    APIV5 = auto()
    APIV6 = auto()
