import argparse
from datetime import datetime
from enum import auto, Enum
import logging
import os
from subprocess import call
import time

from colors import color
import humanize
import pandas as pd


class EndpointType(Enum):
  APIV5 = auto()
  APIV6 = auto()

RARITY_TO_COLOR = [
  'white',  # common
  'green',  # uncommon
  'blue',   # rare
  'orange', # legendary
  'purple', # mythic
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

ARGS = PARSER.parse_args()

TABLE_FMT = '{:<6} {:<6} {:<12} {:<10} {:<10} {:<3} {:<4} {:<8} {:<16} {:<5} {:<8} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4}'

if ARGS.endpoint == EndpointType.APIV5:
  from dfk.apps.apiv5 import *
elif ARGS.endpoint == EndpointType.APIV6:
  from dfk.apps.apiv6 import *

if not ARGS.order_by:
  ARGS.order_by = STARTEDAT_KEY

LOG = logging.getLogger(__name__)


def clear() -> None:
  """
  Clear screen for specific operating system
  """
  _ = call('clear' if os.name =='posix' else 'cls', shell=True)


def run_matching(df: pd.DataFrame) -> pd.DataFrame:
  """
  """
  # TODO: unit tests
  # TODO: generalize

  # TODO: growth/growthp/growths?

  # TODO: should subclass be included here?
  # foraging_match = ((df[PROFESSION_KEY] == 'foraging') & (df[MAINCLASS_KEY].isin(FORAGING_PROFS) | df[SUBCLASS_KEY].isin(FORAGING_PROFS)) & (df[STATBOOST1_KEY].isin(FORAGING_STATS) | df[STATBOOST2_KEY].isin(FORAGING_STATS)))
  # fishing_match = ((df[PROFESSION_KEY] == 'fishing') & (df[MAINCLASS_KEY].isin(FISHING_PROFS) | df[SUBCLASS_KEY].isin(FISHING_PROFS)) & (df[STATBOOST1_KEY].isin(FISHING_STATS) | df[STATBOOST2_KEY].isin(FISHING_STATS)))
  # gardening_match = ((df[PROFESSION_KEY] == 'gardening') & (df[MAINCLASS_KEY].isin(GARDENING_PROFS) | df[SUBCLASS_KEY].isin(GARDENING_PROFS)) & (df[STATBOOST1_KEY].isin(GARDENING_STATS) | df[STATBOOST2_KEY].isin(GARDENING_STATS)))
  # mining_match = ((df[PROFESSION_KEY] == 'mining') & (df[MAINCLASS_KEY].isin(MINING_PROFS) | df[SUBCLASS_KEY].isin(MINING_PROFS)) & (df[STATBOOST1_KEY].isin(MINING_STATS) | df[STATBOOST2_KEY].isin(MINING_STATS)))

  foraging_match = ((df[PROFESSION_KEY] == 'foraging') & (df[MAINCLASS_KEY].isin(FORAGING_PROFS)) & (df[STATBOOST1_KEY].isin(FORAGING_STATS) | df[STATBOOST2_KEY].isin(FORAGING_STATS)))
  fishing_match = ((df[PROFESSION_KEY] == 'fishing') & (df[MAINCLASS_KEY].isin(FISHING_PROFS)) & (df[STATBOOST1_KEY].isin(FISHING_STATS) | df[STATBOOST2_KEY].isin(FISHING_STATS)))
  gardening_match = ((df[PROFESSION_KEY] == 'gardening') & (df[MAINCLASS_KEY].isin(GARDENING_PROFS)) & (df[STATBOOST1_KEY].isin(GARDENING_STATS) | df[STATBOOST2_KEY].isin(GARDENING_STATS)))
  mining_match = ((df[PROFESSION_KEY] == 'mining') & (df[MAINCLASS_KEY].isin(MINING_PROFS)) & (df[STATBOOST1_KEY].isin(MINING_STATS) | df[STATBOOST2_KEY].isin(MINING_STATS)))

  return df.loc[foraging_match | fishing_match | gardening_match | mining_match].sort_values(by=ARGS.order_by, ascending=False) #.sort_values(STARTINGPRICE_KEY)


def print_table(df: pd.DataFrame) -> pd.DataFrame:
  """
  """
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
    'lck'
  ), style='underline'))
  for _, row in df[[SALEID_KEY, HEROID_KEY, STARTEDAT_KEY, MAINCLASS_KEY, SUBCLASS_KEY, GENERATION_KEY, RARITY_KEY, STARTINGPRICE_KEY, PROFESSION_KEY, FISHING_KEY, FORAGING_KEY, GARDENING_KEY, MINING_KEY, LEVEL_KEY, SUMMONS_KEY, MAXSUMMONS_KEY, STRENGTH_KEY, AGILITY_KEY, ENDURANCE_KEY, WISDOM_KEY, DEXTERITY_KEY, VITALITY_KEY, INTELLIGENCE_KEY, LUCK_KEY, STATBOOST1_KEY, STATBOOST2_KEY]].iterrows():
    id, token_id, start_time, main_class, sub_class, generation, rarity, starting_price, profession, fishing, foraging, gardening, mining, level, summons, max_summons, strength, agility, endurance, wisdom, dexterity, vitality, intelligence, luck, boost1, boost2 = row

    profession_to_points = {'fishing': fishing, 'foraging': foraging, 'gardening': gardening, 'mining': mining}

    if profession_to_points[profession] < 10:
      continue

    time_diff = humanize.naturaltime(datetime.now() - datetime.fromtimestamp(int(start_time))).replace('minutes', 'min').replace('seconds', 'sec')

    stat_boost = {stat: '' for stat in STAT_TO_ABBREV.keys()}
    stat_boost[ABBREV_TO_STAT[boost1]] += '+'
    stat_boost[ABBREV_TO_STAT[boost2]] += '%'

    if ARGS.endpoint is EndpointType.APIV6:
      main_class = APIV6_NUM_TO_PROF[int(main_class)]
      sub_class = APIV6_NUM_TO_PROF[int(sub_class)]

    print(color(TABLE_FMT.format(
      id,
      token_id,
      time_diff,
      main_class,
      sub_class,
      generation,
      rarity,
      int(starting_price)/1e18,
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
      f'{luck}{stat_boost["luck"]}'
    ), RARITY_TO_COLOR[int(rarity)]))

  time.sleep(ARGS.refresh)


if __name__ == '__main__':
  LOG.debug('Watching open hero sales...')

  while True:
    try:
      clear()
      LOG.info(f'refresh interval: {ARGS.refresh}s')

      auctions = get_open_auctions(min_price=ARGS.min_price*JEWEL_MULTIPLIER, max_price=ARGS.max_price*JEWEL_MULTIPLIER, limit=ARGS.limit)
      auctions_df = pd.json_normalize(auctions)

      LOG.debug(f'Available data ({len(auctions_df.columns)}): ' + ', '.join(list(auctions_df.columns)))

      match_df = run_matching(auctions_df)
      print_table(match_df)
    except KeyboardInterrupt:
      print()
      LOG.info('CTRL-C Caught, shutting down')
      exit()

# TODO: improvements
# - webapp with filters and real-time updates
# - notifications on new entries to your filter settings
# - twitter bot notifications on undervalued floor heros (by profession, combat when that comes online, questing gains, etc.)
# - incorporate more advanced community knowledge
#   - allow class filtering by numerical score (total base stats from albus) for profession
#   - account for genetics

# I think this has long-term potential as heros become more important down the road (h/t jewelcast)
