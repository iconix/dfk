import logging
from typing import Dict, List

from dfk.apps.apibase import *
from dfk.auctions.sale import sale_auctions

LOG = logging.getLogger(__name__)

ENDPOINT = 'http://graph3.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'

PROFESSION_KEY = 'tokenId.profession'
MAINCLASS_KEY = 'tokenId.mainClass'
SUBCLASS_KEY = 'tokenId.subClass'
STATBOOST1_KEY = 'tokenId.statBoost1'
STATBOOST2_KEY = 'tokenId.statBoost2'
STARTEDAT_KEY = 'startedAt'
STARTINGPRICE_KEY = 'startingPrice'
SALEID_KEY = 'id'
HEROID_KEY = 'tokenId.id'
GENERATION_KEY = 'tokenId.generation'
RARITY_KEY = 'tokenId.rarity'
FISHING_KEY = 'tokenId.fishing'
FORAGING_KEY = 'tokenId.foraging'
GARDENING_KEY = 'tokenId.gardening'
MINING_KEY = 'tokenId.mining'
LEVEL_KEY = 'tokenId.level'
SUMMONS_KEY = 'tokenId.summons'
MAXSUMMONS_KEY = 'tokenId.maxSummons'
STRENGTH_KEY = 'tokenId.strength'
AGILITY_KEY = 'tokenId.agility'
ENDURANCE_KEY = 'tokenId.endurance'
WISDOM_KEY = 'tokenId.wisdom'
DEXTERITY_KEY = 'tokenId.dexterity'
VITALITY_KEY = 'tokenId.vitality'
INTELLIGENCE_KEY = 'tokenId.intelligence'
LUCK_KEY = 'tokenId.luck'


def get_open_auctions(min_price: int = 1*JEWEL_MULTIPLIER, max_price: int = 9999999*JEWEL_MULTIPLIER, limit: int = 1000) -> List[Dict]:
  """
  """
  LOG.info(f'Using APIV5 endpoint {ENDPOINT}')

  # note: "the tavern's broken" on this endpoint often - hence, api v6
  where = f'{{open: true, startingPrice_gte: "{min_price}", startingPrice_lte: "{max_price}"}}'
  return sale_auctions.get_open_auctions(graphql_address=ENDPOINT, count=limit, where=where)
