from dataclasses import dataclass
from enum import auto, Enum
from typing import Dict

JEWEL_MULTIPLIER = 1000000000000000000

PROFESSIONS = {'fishing', 'foraging', 'gardening', 'mining'}

PROFESSIONS_MAP = {
    'fishing': {
        'class': {'Ninja', 'Thief', 'Sage', 'DreadKnight', 'Dragoon', 'Pirate'},
        'stats': {'LCK', 'AGI'},
    },
    'foraging': {
        'class': {'DreadKnight', 'Sage', 'Summoner', 'DarkKnight', 'Ninja', 'Archer', 'Dragoon', 'Wizard'}, #, 'Priest'},
        'stats': {'DEX', 'INT'},
    },
    'gardening': {
        'class': {'DreadKnight', 'Sage', 'Paladin', 'Summoner', 'Priest', 'Wizard', 'Dragoon'}, #'DarkKnight', 'Monk', 'Knight'},
        'stats': {'WIS', 'VIT'}
    },
    'mining': {
        'class': {'DreadKnight', 'Paladin', 'Dragoon', 'DarkKnight', 'Knight', 'Warrior', 'Pirate'}, #'Archer', 'Monk', 'Thief'},
        'stats': {'STR', 'END'},
    }
}

CLASSES_MAP = {
    'Warrior': {
        'stat_growth': {
            'STR': 75,
            'INT': 20,
            'WIS': 20,
            'LCK': 35,
            'AGI': 50,
            'VIT': 65,
            'END': 65,
            'DEX': 70
        }
    },
    'Knight': {
        'stat_growth': {
            'STR': 70,
            'INT': 20,
            'WIS': 25,
            'LCK': 35,
            'AGI': 45,
            'VIT': 75,
            'END': 75,
            'DEX': 55
        }
    },
    'Thief': {
        'stat_growth': {
            'STR': 55,
            'INT': 25,
            'WIS': 35,
            'LCK': 65,
            'AGI': 70,
            'VIT': 50,
            'END': 40,
            'DEX': 55
        }
    },
    'Archer': {
        'stat_growth': {
            'STR': 55,
            'INT': 40,
            'WIS': 25,
            'LCK': 40,
            'AGI': 50,
            'VIT': 50,
            'END': 60,
            'DEX': 80
        }
    },
    'Priest': {
        'stat_growth': {
            'STR': 30,
            'INT': 70,
            'WIS': 80,
            'LCK': 40,
            'AGI': 40,
            'VIT': 50,
            'END': 60,
            'DEX': 30
        }
    },
    'Wizard': {
        'stat_growth': {
            'STR': 30,
            'INT': 80,
            'WIS': 80,
            'LCK': 40,
            'AGI': 40,
            'VIT': 50,
            'END': 50,
            'DEX': 30
        }
    },
    'Monk': {
        'stat_growth': {
            'STR': 60,
            'INT': 25,
            'WIS': 50,
            'LCK': 30,
            'AGI': 60,
            'VIT': 60,
            'END': 55,
            'DEX': 60
        }
    },
    'Pirate': {
        'stat_growth': {
            'STR': 70,
            'INT': 20,
            'WIS': 20,
            'LCK': 55,
            'AGI': 50,
            'VIT': 60,
            'END': 55,
            'DEX': 70
        }
    },
    'Paladin': {
        'stat_growth': {
            'STR': 80,
            'INT': 30,
            'WIS': 65,
            'LCK': 40,
            'AGI': 35,
            'VIT': 80,
            'END': 80,
            'DEX': 40
        }
    },
    'DarkKnight': {
        'stat_growth': {
            'STR': 85,
            'INT': 70,
            'WIS': 35,
            'LCK': 35,
            'AGI': 35,
            'VIT': 75,
            'END': 60,
            'DEX': 55
        }
    },
    'Summoner': {
        'stat_growth': {
            'STR': 45,
            'INT': 85,
            'WIS': 85,
            'LCK': 40,
            'AGI': 50,
            'VIT': 50,
            'END': 50,
            'DEX': 45
        }
    },
    'Ninja': {
        'stat_growth': {
            'STR': 50,
            'INT': 50,
            'WIS': 40,
            'LCK': 60,
            'AGI': 85,
            'VIT': 50,
            'END': 40,
            'DEX': 75
        }
    },
    'Dragoon': {
        'stat_growth': {
            'STR': 80,
            'INT': 50,
            'WIS': 60,
            'LCK': 50,
            'AGI': 65,
            'VIT': 60,
            'END': 70,
            'DEX': 65
        }
    },
    'Sage': {
        'stat_growth': {
            'STR': 40,
            'INT': 90,
            'WIS': 90,
            'LCK': 55,
            'AGI': 75,
            'VIT': 60,
            'END': 50,
            'DEX': 40
        }
    },
    'DreadKnight': {
        'stat_growth': {
            'STR': 85,
            'INT': 65,
            'WIS': 65,
            'LCK': 60,
            'AGI': 60,
            'VIT': 65,
            'END': 75,
            'DEX': 75
        }
    }
}

CLASSES = CLASSES_MAP.keys()

RARITY_TO_COLOR = [
    'white',    # common
    'green',    # uncommon
    'blue',     # rare
    'orange',   # legendary
    'purple',   # mythic
]

STAT_TO_CODE = {
    'strength': 'STR',
    'agility': 'AGI',
    'endurance': 'END',
    'wisdom': 'WIS',
    'dexterity': 'DEX',
    'vitality': 'VIT',
    'intelligence': 'INT',
    'luck': 'LCK'
}
CODE_TO_STAT = { v: k for k,v in STAT_TO_CODE.items() }

PROFESSIONSCORE_KEY = 'ps'
PROFESSIONSCOREPERJEWEL_KEY = 'psJewel'

COMBATSCOREAVG_KEY = 'csAvg'
COMBATSCOREAVGPERJEWEL_KEY = 'csAvgJewel'

# Petrify's roles - https://medium.com/@Petrify/defikingdoms-combat-stats-speculation-eabd90368a4f
COMBATPHYSICALDAMAGE_KEY = 'phyDmg'
COMBATMAGICALDAMAGE_KEY = 'magDmg'
COMBATPHYSICALTANK_KEY = 'phyTank'
COMBATMAGICALTANK_KEY = 'magTank'

class EndpointType(Enum):
    APIV5 = auto()
    APIV6 = auto()


@dataclass
class HeroData:
    level: int
    main_class: str
    profession: str
    rarity: int
    stats: Dict[str, int]
    sub_class: str
    blue_gene: str
