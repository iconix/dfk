from datetime import datetime
import logging
import os
from subprocess import call
import sys
import time

from colors import color
import humanize
import pandas as pd
import requests

from dfk.auctions.sale.sale_auctions import get_open_auctions

APIV6_NUM_TO_PROF = {
  0: 'Warrior', 1: 'Knight', 2: 'Thief', 3: 'Archer', 4: 'Priest', 5: 'Wizard', 6: 'Monk', 7: 'Pirate',
  16: 'Paladin', 17: 'DarkKnight', 18: 'Summoner', 19: 'Ninja',
  24: 'Dragoon', 25: 'Sage', 28: 'DreadKnight'
}
APIV6_PROF_TO_NUM = { v: k for k,v in APIV6_NUM_TO_PROF.items() }

# TODO: allow class filtering by numerical score (total base stats from albus) for profession
FORAGING_PROFS = ('Sage', 'Summoner', 'DarkKnight', 'Ninja', 'Archer', 'Dragoon', 'Wizard', 'Priest')
FORAGING_STATS = ('DEX', 'INT')

FISHING_PROFS = ('Ninja', 'Thief', 'Sage', 'Dragoon', 'Pirate')
FISHING_STATS = ('LCK', 'AGI')

GARDENING_PROFS = ('Sage', 'Paladin', 'Summoner', 'Priest', 'Wizard', 'Dragoon') #, 'DarkKnight', 'Monk', 'Knight')
GARDENING_STATS = ('WIS', 'VIT')

MINING_PROFS = ('Paladin', 'Dragoon', 'DarkKnight', 'Knight', 'Warrior', 'Pirate') #, 'Archer', 'Monk', 'Thief')
MINING_STATS = ('STR', 'END')

# APIv6
FORAGING_PROFS = [str(APIV6_PROF_TO_NUM[p]) for p in FORAGING_PROFS]
FISHING_PROFS = [str(APIV6_PROF_TO_NUM[p]) for p in FISHING_PROFS]
GARDENING_PROFS = [str(APIV6_PROF_TO_NUM[p]) for p in GARDENING_PROFS]
MINING_PROFS = [str(APIV6_PROF_TO_NUM[p]) for p in MINING_PROFS]

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

MIN_PRICE = 1000000000000000000   # 1 JEWEL
MAX_PRICE = 80000000000000000000  # 50 JEWELS
QUERY_LIMIT = 500
QUERY_OFFSET = 0

GRAPHQL = 'http://graph3.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'
# note: `open` data is faulty so filter is imperfect (this may be what people mean by "the tavern's broken")
GRAPHQL_WHERE = f'{{open: true, startingPrice_lt: "{MAX_PRICE}"}}'

APIV6 = 'https://us-central1-defi-kingdoms-api.cloudfunctions.net/query_heroes'

REFRESH_S = 30
TABLE_FMT = '{:<6} {:<6} {:<12} {:<10} {:<10} {:<3} {:<4} {:<8} {:<16} {:<5} {:<8} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4} {:<4}'

LOG = logging.getLogger('DFK-auctions')
log_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
LOG.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)


def clear():
    # check and make call for specific operating system
    _ = call('clear' if os.name =='posix' else 'cls', shell=True)


def query_auctions():
  #LOG.info('Using GraphQL endpoint ' + GRAPHQL)
  #auctions = get_open_auctions(GRAPHQL, skip=QUERY_OFFSET, count=QUERY_LIMIT, where=GRAPHQL_WHERE)

  LOG.info('Using DFK endpoint ' + APIV6)
  # TODO(nadja): helper for apiv6
  r = requests.post(APIV6, json={
    'limit': QUERY_LIMIT,
    'params': [{'field': 'saleprice', 'operator': '>=', 'value': MIN_PRICE}, {'field': 'saleprice', 'operator': '<=', 'value': MAX_PRICE}],
    #'params': [{'field': 'id', 'operator': '=', 'value': '42361'}],
    'offset': QUERY_OFFSET,
    'order': {'orderBy': 'saleprice', 'orderDir': 'asc'}
  })
  if r.status_code != 200:
      raise Exception("HTTP error " + str(r.status_code) + ": " + r.text)
  auctions = r.json()

  return auctions


if __name__ == '__main__':
    LOG.debug('Recent sale auctions:')
    clear()
    while True:
      auctions = query_auctions()
      auctions_df = pd.json_normalize(auctions)
      LOG.debug(f'Available data ({len(auctions_df.columns)}): ' + ', '.join(list(auctions_df.columns)))

      '''
      # GRAPHQL keys
      profession_key = 'tokenId.profession'
      mainclass_key = 'tokenId.mainClass'
      subclass_key = 'tokenId.subClass'
      statboost1_key = 'tokenId.statBoost1'
      statboost2_key = 'tokenId.statBoost2'
      startedat_key = 'startedAt'
      startingprice_key = 'startingPrice'
      saleid_key = 'id'
      heroid_key = 'tokenId.id'
      generation_key = 'tokenId.generation'
      rarity_key = 'tokenId.rarity'
      fishing_key = 'tokenId.fishing'
      foraging_key = 'tokenId.foraging'
      gardening_key = 'tokenId.gardening'
      mining_key = 'tokenId.mining'
      level_key = 'tokenId.level'
      summons_key = 'tokenId.summons'
      maxsummons_key = 'tokenId.maxSummons'
      strength_key = 'tokenId.strength'
      agility_key = 'tokenId.agility'
      endurance_key = 'tokenId.endurance'
      wisdom_key = 'tokenId.wisdom'
      dexterity_key = 'tokenId.dexterity'
      vitality_key = 'tokenId.vitality'
      intelligence_key = 'tokenId.intelligence'
      luck_key = 'tokenId.luck'
      '''

      # APIv6 keys
      profession_key = 'profession'
      mainclass_key = 'mainclass'
      subclass_key = 'subclass'
      statboost1_key = 'statboost1'
      statboost2_key = 'statboost2'
      startedat_key = 'saleauction_startedat'
      startingprice_key = 'saleauction_startingprice'
      saleid_key = 'saleauction'
      heroid_key = 'id'
      generation_key = 'generation'
      rarity_key = 'rarity'
      fishing_key = 'fishing'
      foraging_key = 'foraging'
      gardening_key = 'gardening'
      mining_key = 'mining'
      level_key = 'level'
      summons_key = 'summons'
      maxsummons_key = 'maxsummons'
      strength_key = 'strength'
      agility_key = 'agility'
      endurance_key = 'endurance'
      wisdom_key = 'wisdom'
      dexterity_key = 'dexterity'
      vitality_key = 'vitality'
      intelligence_key = 'intelligence'
      luck_key = 'luck'

      # TODO(nadja): growth/growthp/growths?

      # TODO: should subclass be included here?
      # foraging_match = ((auctions_df[profession_key] == 'foraging') & (auctions_df[mainclass_key].isin(FORAGING_PROFS) | auctions_df[subclass_key].isin(FORAGING_PROFS)) & (auctions_df[statboost1_key].isin(FORAGING_STATS) | auctions_df[statboost2_key].isin(FORAGING_STATS)))
      # fishing_match = ((auctions_df[profession_key] == 'fishing') & (auctions_df[mainclass_key].isin(FISHING_PROFS) | auctions_df[subclass_key].isin(FISHING_PROFS)) & (auctions_df[statboost1_key].isin(FISHING_STATS) | auctions_df[statboost2_key].isin(FISHING_STATS)))
      # gardening_match = ((auctions_df[profession_key] == 'gardening') & (auctions_df[mainclass_key].isin(GARDENING_PROFS) | auctions_df[subclass_key].isin(GARDENING_PROFS)) & (auctions_df[statboost1_key].isin(GARDENING_STATS) | auctions_df[statboost2_key].isin(GARDENING_STATS)))
      # mining_match = ((auctions_df[profession_key] == 'mining') & (auctions_df[mainclass_key].isin(MINING_PROFS) | auctions_df[subclass_key].isin(MINING_PROFS)) & (auctions_df[statboost1_key].isin(MINING_STATS) | auctions_df[statboost2_key].isin(MINING_STATS)))
      foraging_match = ((auctions_df[profession_key] == 'foraging') & (auctions_df[mainclass_key].isin(FORAGING_PROFS)) & (auctions_df[statboost1_key].isin(FORAGING_STATS) | auctions_df[statboost2_key].isin(FORAGING_STATS)))
      fishing_match = ((auctions_df[profession_key] == 'fishing') & (auctions_df[mainclass_key].isin(FISHING_PROFS)) & (auctions_df[statboost1_key].isin(FISHING_STATS) | auctions_df[statboost2_key].isin(FISHING_STATS)))
      gardening_match = ((auctions_df[profession_key] == 'gardening') & (auctions_df[mainclass_key].isin(GARDENING_PROFS)) & (auctions_df[statboost1_key].isin(GARDENING_STATS) | auctions_df[statboost2_key].isin(GARDENING_STATS)))
      mining_match = ((auctions_df[profession_key] == 'mining') & (auctions_df[mainclass_key].isin(MINING_PROFS)) & (auctions_df[statboost1_key].isin(MINING_STATS) | auctions_df[statboost2_key].isin(MINING_STATS)))

      # TODO: unit tests
      auctions_df = auctions_df.loc[foraging_match | fishing_match | gardening_match | mining_match].sort_values(startedat_key, ascending=False) #.sort_values(startingprice_key)

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
      for _, row in auctions_df[[saleid_key, heroid_key, startedat_key, mainclass_key, subclass_key, generation_key, rarity_key, startingprice_key, profession_key, fishing_key, foraging_key, gardening_key, mining_key, level_key, summons_key, maxsummons_key, strength_key, agility_key, endurance_key, wisdom_key, dexterity_key, vitality_key, intelligence_key, luck_key, statboost1_key, statboost2_key]].iterrows():
        id, token_id, start_time, main_class, sub_class, generation, rarity, starting_price, profession, fishing, foraging, gardening, mining, level, summons, max_summons, strength, agility, endurance, wisdom, dexterity, vitality, intelligence, luck, boost1, boost2 = row

        profession_to_points = {'fishing': fishing, 'foraging': foraging, 'gardening': gardening, 'mining': mining}

        if profession_to_points[profession] < 10:
          continue

        time_diff = humanize.naturaltime(datetime.now() - datetime.fromtimestamp(int(start_time))).replace('minutes', 'min').replace('seconds', 'sec')

        stat_boost = {stat: '' for stat in STAT_TO_ABBREV.keys()}
        stat_boost[ABBREV_TO_STAT[boost1]] += '+'
        stat_boost[ABBREV_TO_STAT[boost2]] += '%'

        print(color(TABLE_FMT.format(
          id,
          token_id,
          time_diff,
          APIV6_NUM_TO_PROF[int(main_class)], #main_class,
          APIV6_NUM_TO_PROF[int(sub_class)], #sub_class,
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

      time.sleep(REFRESH_S)
      clear()

# TODO: improvements
# - webapp with filters and real-time updates
# - notifications on new entries to your filter settings
# - twitter bot notifications on undervalued floor heros (by profession, combat when that comes online, questing gains, etc.)
# - incorporate more advanced community knowledge (e.g., genetics)

# I think this has potential down the road because heros will become more important down the road (h/t jewelcast)
