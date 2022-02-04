import logging
from typing import Dict

from dfk.apps.apibase import CODE_TO_STAT, COMBATMAGICALDAMAGE_KEY, COMBATMAGICALTANK_KEY, COMBATPHYSICALDAMAGE_KEY, COMBATPHYSICALTANK_KEY, HeroData
from dfk.apps.kwps import calculate_stat_growth

LOG = logging.getLogger(__name__)


def valuate_combat_petrify(heroData: HeroData) -> Dict[str, int]:
    """
    source (article): https://medium.com/@Petrify/defikingdoms-combat-stats-speculation-eabd90368a4f
    "DefiKingdoms Combat Stats — Speculation" -- Dec 14, 2021
    """

    # how many levels left before 100
    levels_left = 100 - heroData.level

    # current stats + expected growth
    expected_stats = {
        stat_code: heroData.stats[stat_code] * 1 + calculate_stat_growth(heroData, stat_code, levels_left)
        for stat_code in CODE_TO_STAT.keys()
    }

    # use Petrify's rating formalas
    scores = {
        COMBATPHYSICALDAMAGE_KEY: int(round(expected_stats['STR'] + (0.5 * expected_stats['DEX']) + (0.2 * expected_stats['LCK']) + (0.2 * expected_stats['AGI']))),
        COMBATMAGICALDAMAGE_KEY: int(round(expected_stats['INT'] + expected_stats['WIS'] + (0.2 * expected_stats['LCK']) + (0.2 * expected_stats['AGI']))),
        COMBATPHYSICALTANK_KEY: int(round(expected_stats['END'] + expected_stats['VIT'] + (0.2 * expected_stats['DEX']) + (0.2 * expected_stats['AGI']) + (0.1 * expected_stats['LCK']))),
        COMBATMAGICALTANK_KEY: int(round(expected_stats['END'] + expected_stats['VIT'] + (0.5 * expected_stats['INT']) + (0.5 * expected_stats['WIS'])))
    }

    LOG.debug(scores)

    return scores
