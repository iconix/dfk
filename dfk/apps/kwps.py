"""
source (javascript): https://kingdom.watch/about/heroranking

The Kingdom.Watch Profession Score (KWPS) is a modified version the great algorithm Discord user @GokMachar published in the [Analysis on profession](https://www.reddit.com/r/DefiKingdoms/comments/qpotgf/analysis_on_profession/) Reddit post.

In short, the score is the expected value of the sum of the two relevant skills for the profession, assuming perfect/focused leveling. The profession gene adds a 10% bonus to this value for now, but as we get more information about the actual impact of the main profession this will be adjusted.

The most visible difference from @GokMachar's algorithm is that the KWPS is not normalized and not discounted. Once the scoring algorithm is stable a hero's score will not change significantly after each level.

TODO: appreciate kingdom.watch for doing this... look for opportunities to share & be transparent like this as well
    - public API
    - public algos
"""

from dfk.apps.apibase import CLASSES_MAP, HeroData, PROFESSIONS_MAP


VERSION = 'v0.5.1'

RARITY_MULTIPLIER_PCT = [
    0,         # common
    25 / 5,    # uncommon
    50 / 5,    # rare
    87.5 / 5,  # legendary
    125 / 5    # mythic
]


def valuate_profession(heroData: HeroData, profession: str) -> int:
    """
    valuate one profession
    """
    stat1name, stat2name = PROFESSIONS_MAP[profession]['stats']

    # how many levels left before 100
    levels_left = 100 - heroData.level

    # current stat + expected growth
    stat1val = heroData.stats[stat1name] * 1 + calculate_stat_growth(heroData, stat1name, levels_left)
    stat2val = heroData.stats[stat2name] * 1 + calculate_stat_growth(heroData, stat2name, levels_left)

    # combine them
    stat_sum = stat1val + stat2val

    # if this is the main profession of the hero, add 10%
    if heroData.profession == profession:
        stat_sum *= 1.1

    return int(round(stat_sum))


def calculate_stat_growth(heroData: HeroData, stat: str, levels: int) -> float:
    """
    per stat
    """
    growth = 0.0

    # stat growth
    growth += CLASSES_MAP[heroData.main_class]['stat_growth'][stat] / 100
    growth += CLASSES_MAP[heroData.sub_class]['stat_growth'][stat] / 100 * 0.25

    # blue gene will give + 2% to the primary stat growth and + 4% to the secondary
    # since this function works per stat we just add the two bonuses to the growth
    if heroData.blue_gene == stat:
        growth += 0.02  # primary
        growth += 0.04  # secondary

    # rarity bonus
    growth += RARITY_MULTIPLIER_PCT[heroData.rarity] / 100

    # half of +1 stat choice every level
    growth += 0.5

    # half of Gaia's blessing 50% chance of +1 for the other gene
    growth += 0.25

    return  growth * levels
