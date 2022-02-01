import argparse
from datetime import datetime
import logging
import os
from subprocess import call
import time
from typing import Any, List, Union

from colors import color
import humanize
import pandas as pd

from dfk.apps.apiv6 import *
from dfk.apps.kwps import HeroData, valuate_profession


TABLE_FMT = '{:<6} {:<6} {:<12} {:<10} {:<10} {:<3} {:<4} {:<8} {:<16} {:<5} {:<8} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<9}'
LOG = logging.getLogger(__name__)


def clear() -> None:
    """
    Clear screen for specific operating system
    """
    _ = call('clear' if os.name =='posix' else 'cls', shell=True)


# aka presets
def build_recommended_profession_matcher(df: pd.DataFrame) -> 'pd.Series[bool]':
    foraging_class, foraging_stats = PROFESSIONS_MAP['foraging']['class'], PROFESSIONS_MAP['foraging']['stats']
    fishing_class, fishing_stats = PROFESSIONS_MAP['fishing']['class'], PROFESSIONS_MAP['fishing']['stats']
    gardening_class, gardening_stats = PROFESSIONS_MAP['gardening']['class'], PROFESSIONS_MAP['gardening']['stats']
    mining_class, mining_stats = PROFESSIONS_MAP['mining']['class'], PROFESSIONS_MAP['mining']['stats']

    foraging_match = ((df[PROFESSION_KEY] == 'foraging') & (df[MAINCLASS_KEY].isin(foraging_class)) & (df[STATBOOST1_KEY].isin(foraging_stats) | df[STATBOOST2_KEY].isin(foraging_stats)))
    fishing_match = ((df[PROFESSION_KEY] == 'fishing') & (df[MAINCLASS_KEY].isin(fishing_class)) & (df[STATBOOST1_KEY].isin(fishing_stats) | df[STATBOOST2_KEY].isin(fishing_stats)))
    gardening_match = ((df[PROFESSION_KEY] == 'gardening') & (df[MAINCLASS_KEY].isin(gardening_class)) & (df[STATBOOST1_KEY].isin(gardening_stats) | df[STATBOOST2_KEY].isin(gardening_stats)))
    mining_match = ((df[PROFESSION_KEY] == 'mining') & (df[MAINCLASS_KEY].isin(mining_class)) & (df[STATBOOST1_KEY].isin(mining_stats) | df[STATBOOST2_KEY].isin(mining_stats)))

    return foraging_match | fishing_match | gardening_match | mining_match


def run_matching(df: pd.DataFrame, professions: List[str] = PROFESSIONS, classes: List[str] = CLASSES,
                 statboost1s: List[str] = STAT_TO_CODE.values(), statboost2s: List[str] = STAT_TO_CODE.values(),
                 matcher: Union[bool, 'pd.Series[bool]'] = True) -> pd.DataFrame:
    """
    """
    # TODO: generalize:
    # - take in lists of PROFESSION, MAINCLASS, SUBCLASS, STAT BOOSTS, GENERATION, RARITY, LEVEL, SUMMONS...
    # - provide a 'toggle' that subselects from above lists according to PROFESSION > TOTAL BASE STATS + STAT BOOSTS
    #     (in this profession, you'll see total base stats > N with these main classes; optionally care about aligned stat boosts)
    #     (how much should we take subclass into account?)
    # - what is growth/growthp/growths?
    professions_matcher = df[PROFESSION_KEY].isin(professions)
    classes_matcher = df[MAINCLASS_KEY].isin(classes)
    statboost1s_matcher = df[STATBOOST1_KEY].isin(statboost1s)
    statboost2s_matcher = df[STATBOOST2_KEY].isin(statboost2s)

    # n.b., copy to intentionally create a new dataframe of matches
    return df.loc[professions_matcher & classes_matcher & (statboost1s_matcher | statboost2s_matcher) & matcher].copy()


def calculate_profession_scores(row: pd.Series) -> Dict[str, int | float]:
    """
    """
    stat_to_points = {
        'STR': row[STRENGTH_KEY], 'AGI': row[AGILITY_KEY], 'END': row[ENDURANCE_KEY], 'WIS': row[WISDOM_KEY],
        'DEX': row[DEXTERITY_KEY], 'VIT': row[VITALITY_KEY], 'INT': row[INTELLIGENCE_KEY], 'LCK': row[LUCK_KEY]
    }

    hero_data = HeroData(
        level=row[LEVEL_KEY],
        main_class=row[MAINCLASS_KEY],
        profession=row[PROFESSION_KEY],
        rarity=row[RARITY_KEY],
        stats={s: stat_to_points[s] for s in PROFESSIONS_MAP[row[PROFESSION_KEY]]['stats']},
        sub_class=row[SUBCLASS_KEY]
    )
    kwps = valuate_profession(hero_data, row[PROFESSION_KEY])
    kwps_per_jewel = round(kwps / row[STARTINGPRICE_KEY], 4)

    return {
        PROFESSIONSCORE_KEY: kwps,
        PROFESSIONSCOREPERJEWEL_KEY: kwps_per_jewel
    }


def normalize_table(row: pd.Series) -> Dict[str, Any]:
    """
    """
    mainclass = APIV6_NUM_TO_CLASS[int(row[MAINCLASS_KEY])] if ARGS.endpoint is EndpointType.APIV6 else row[MAINCLASS_KEY]
    subclass = APIV6_NUM_TO_CLASS[int(row[SUBCLASS_KEY])] if ARGS.endpoint is EndpointType.APIV6 else row[SUBCLASS_KEY]

    # TODO: in api v6, summons field seems inverted...
    summons = row[MAXSUMMONS_KEY] - row[SUMMONS_KEY] if ARGS.endpoint is EndpointType.APIV6 else row[SUMMONS_KEY]

    startingprice = int(row[STARTINGPRICE_KEY])/1e18

    return {
        SALEID_KEY: row[SALEID_KEY],
        MAINCLASS_KEY: mainclass,
        SUBCLASS_KEY: subclass,
        SUMMONS_KEY: summons,
        STARTINGPRICE_KEY: startingprice
    }


def print_table(df: pd.DataFrame, order_by: str, ascending_order: bool = False) -> pd.DataFrame:
    """
    """
    normalize_df = df.apply(normalize_table, axis='columns', result_type='expand')
    df.update(normalize_df)

    df[PROFESSIONSCORE_KEY], df[PROFESSIONSCOREPERJEWEL_KEY] = -1, -1.0
    scores_df = df.apply(calculate_profession_scores, axis='columns', result_type='expand')
    df.update(scores_df)

    df = df.sort_values(by=order_by, ascending=ascending_order) #[:50]

    print(color(TABLE_FMT.format(
        'saleId',
        'heroId',
        'time',
        'class',
        'sub',
        'gen',
        'rare',
        'price',
        'prof',
        'level',
        'summons',
        'str',
        'agi',
        'end',
        'wis',
        'dex',
        'vit',
        'int',
        'lck',
        'ps',
        'ps/jewel'
    ), style='underline'))
    for _, row in df[[SALEID_KEY, HEROID_KEY, STARTEDAT_KEY, MAINCLASS_KEY, SUBCLASS_KEY, GENERATION_KEY, RARITY_KEY, STARTINGPRICE_KEY, PROFESSION_KEY, FISHING_KEY, FORAGING_KEY, GARDENING_KEY, MINING_KEY, LEVEL_KEY, SUMMONS_KEY, MAXSUMMONS_KEY, STRENGTH_KEY, AGILITY_KEY, ENDURANCE_KEY, WISDOM_KEY, DEXTERITY_KEY, VITALITY_KEY, INTELLIGENCE_KEY, LUCK_KEY, STATBOOST1_KEY, STATBOOST2_KEY, PROFESSIONSCORE_KEY, PROFESSIONSCOREPERJEWEL_KEY]].iterrows():
        id, token_id, start_time, main_class, sub_class, generation, rarity, starting_price, profession, fishing, foraging, gardening, mining, level, summons, max_summons, strength, agility, endurance, wisdom, dexterity, vitality, intelligence, luck, boost1, boost2, kwps, kwps_per_jewel = row

        profession_to_points = {'fishing': fishing, 'foraging': foraging, 'gardening': gardening, 'mining': mining}

        if profession_to_points[profession] < 10:
            continue

        time_diff = humanize.naturaltime(datetime.now() - datetime.fromtimestamp(int(start_time))).replace('minutes', 'min').replace('seconds', 'sec')

        stat_boost = {stat: '' for stat in STAT_TO_CODE.keys()}
        stat_boost[CODE_TO_STAT[boost1]] += '+'
        stat_boost[CODE_TO_STAT[boost2]] += '%'

        print(color(TABLE_FMT.format(
            id,
            token_id,
            time_diff,
            main_class,
            sub_class,
            generation,
            rarity,
            starting_price,
            f'{profession} ({profession_to_points[profession]/10})',
            level,
            f'{summons}/{max_summons}',
            f'{strength}{stat_boost["strength"]}',
            f'{agility}{stat_boost["agility"]}',
            f'{endurance}{stat_boost["endurance"]}',
            f'{wisdom}{stat_boost["wisdom"]}',
            f'{dexterity}{stat_boost["dexterity"]}',
            f'{vitality}{stat_boost["vitality"]}',
            f'{intelligence}{stat_boost["intelligence"]}',
            f'{luck}{stat_boost["luck"]}',
            kwps,
            kwps_per_jewel,
        ), RARITY_TO_COLOR[int(rarity)]))

    time.sleep(ARGS.refresh)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Watch open hero sales')
    PARSER.add_argument('-e', '--endpoint', help='API endpoint for querying DFK data',
                        choices=list(EndpointType), default=EndpointType.APIV6,
                        type=lambda x: EndpointType[x.upper()] if x else EndpointType.APIV6)
    PARSER.add_argument('--min-price', help='Minimum sales price to watch for (in JEWEL)',
                        default=1, type=int)
    PARSER.add_argument('--max-price', help='Maximum sales price to watch for (in JEWEL)',
                        default=80, type=int)
    PARSER.add_argument('--order-by', help='Order results by column name',
                        default=None, type=str)
    PARSER.add_argument('--limit', help='Maximum number of sales to query for',
                        default=500, type=int)
    PARSER.add_argument('--refresh', help='Interval (in seconds) for refreshing the data',
                        default=30, type=int)

    # TODO: it would be cool/extra if this could merely highlight rows, not filter others totally out
    PARSER.add_argument('-p', '--professions', action='extend', nargs='+', help='Professions to watch for',
                        choices=PROFESSIONS, type=lambda x: x.lower())

    ARGS = PARSER.parse_args()

    if ARGS.endpoint == EndpointType.APIV5:
        from dfk.apps.apiv5 import *

    if not ARGS.order_by:
        ARGS.order_by = STARTEDAT_KEY

    if not ARGS.professions:
        ARGS.professions = PROFESSIONS

    LOG.debug('Watching open hero sales...')

    while True:
        try:
            clear()
            LOG.info(f'refresh interval: {ARGS.refresh}s')

            auctions = get_open_auctions(min_price=ARGS.min_price*JEWEL_MULTIPLIER, max_price=ARGS.max_price*JEWEL_MULTIPLIER, limit=ARGS.limit)
            auctions_df = pd.json_normalize(auctions)

            LOG.debug(f'Available data ({len(auctions_df.columns)}): ' + ', '.join(list(auctions_df.columns)))

            reco_profession_matcher = build_recommended_profession_matcher(auctions_df)

            # TODO: add cmd line arg for matcher=reco_profession_matcher
            match_df = run_matching(auctions_df, professions=ARGS.professions, matcher=reco_profession_matcher)
            print_table(match_df, ARGS.order_by)
        except KeyboardInterrupt:
            print()
            LOG.info('CTRL-C Caught, shutting down')
            exit()

# TODO: improvements
# - webapp with filters and real-time updates
# - notifications on new entries to your filter settings
# - twitter bot notifications on undervalued floor heros (by profession, combat when that comes online, questing gains, etc.)
# - incorporate more advanced community knowledge
#     - 'hero value score' + 'profession score'
#     - https://medium.com/@Samichpunch/breaking-down-a-defi-kingdoms-hero-card-and-what-to-consider-when-purchasing-efd5e5222f97
#     - allow class filtering by numerical score (total base stats from albus) for profession
#     - account for genetics
#     - account for other ROI dimensions beyond questing...
#         - pvp combat archetypes (tank, weapon dps, caster)
#         - summoning (e.g., lower generations; summons remaining; compare with hero owned by user)
#         - pve
#         - 'leveling and reselling' (idea from nous#1009 in #hero-advice)
#         - 'collectability' (idea from nous#1009 in #hero-advice)
# - ML for recognizing patterns in earnings (think: https://www.dfkearn.com/hero/62569), summonings, eventually combat

# I think this has long-term potential as heros become more important down the road (h/t jewelcast)
