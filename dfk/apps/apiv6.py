import logging
import requests
from typing import Dict, List

from dfk.apps.apibase import *

LOG = logging.getLogger(__name__)

ENDPOINT = 'https://us-central1-defi-kingdoms-api.cloudfunctions.net/query_heroes'

APIV6_NUM_TO_CLASS = {
    0: 'Warrior', 1: 'Knight', 2: 'Thief', 3: 'Archer', 4: 'Priest', 5: 'Wizard', 6: 'Monk', 7: 'Pirate',
    16: 'Paladin', 17: 'DarkKnight', 18: 'Summoner', 19: 'Ninja',
    24: 'Dragoon', 25: 'Sage', 28: 'DreadKnight'
}
APIV6_CLASS_TO_NUM = { v: k for k,v in APIV6_NUM_TO_CLASS.items() }

# convert to v6 numerical format
PROFESSIONS_MAP['foraging']['class'] = {str(APIV6_CLASS_TO_NUM[p]) for p in PROFESSIONS_MAP['foraging']['class']}
PROFESSIONS_MAP['fishing']['class'] = {str(APIV6_CLASS_TO_NUM[p]) for p in PROFESSIONS_MAP['fishing']['class']}
PROFESSIONS_MAP['gardening']['class'] = {str(APIV6_CLASS_TO_NUM[p]) for p in PROFESSIONS_MAP['gardening']['class']}
PROFESSIONS_MAP['mining']['class'] = {str(APIV6_CLASS_TO_NUM[p]) for p in PROFESSIONS_MAP['mining']['class']}

CLASSES = {str(n) for n in APIV6_NUM_TO_CLASS.keys()}

PROFESSION_KEY = 'profession'
MAINCLASS_KEY = 'mainclass'
SUBCLASS_KEY = 'subclass'
STATBOOST1_KEY = 'statboost1'
STATBOOST2_KEY = 'statboost2'
STARTEDAT_KEY = 'saleauction_startedat'
STARTINGPRICE_KEY = 'saleauction_startingprice'
SALEID_KEY = 'saleauction'
HEROID_KEY = 'id'
GENERATION_KEY = 'generation'
RARITY_KEY = 'rarity'
FISHING_KEY = 'fishing'
FORAGING_KEY = 'foraging'
GARDENING_KEY = 'gardening'
MINING_KEY = 'mining'
LEVEL_KEY = 'level'
SUMMONS_KEY = 'summons'
MAXSUMMONS_KEY = 'maxsummons'
STRENGTH_KEY = 'strength'
AGILITY_KEY = 'agility'
ENDURANCE_KEY = 'endurance'
WISDOM_KEY = 'wisdom'
DEXTERITY_KEY = 'dexterity'
VITALITY_KEY = 'vitality'
INTELLIGENCE_KEY = 'intelligence'
LUCK_KEY = 'luck'


def get_open_auctions(min_price: int = 1*JEWEL_MULTIPLIER, max_price: int = 9999999*JEWEL_MULTIPLIER, limit: int = 1000, pj_filter: bool = False) -> List[Dict]:
    LOG.info(f'Using APIV6 endpoint {ENDPOINT}')

    payload = {
        'limit': limit,

        'params': [
            {'field': 'saleprice', 'operator': '>=', 'value': min_price},
            {'field': 'saleprice', 'operator': '<=', 'value': max_price},
        ],

        # bias towards the freshest auctions
        'order': {'orderBy': 'saleauction', 'orderDir': 'desc'},

        # n.b., helpful filter type
        #'params': [{'field': 'id', 'operator': '=', 'value': '42361'}],

        # n.b., `orderby: saleprice`` tends to result in more stale listings, for some reason
        #'order': {'orderBy': 'saleprice', 'orderDir': 'asc'},
    }

    if pj_filter:
        payload['params'].append({'field': 'pjstatus', 'operator': '=', 'value': 'SURVIVED'})

    r = requests.post(ENDPOINT, json=payload)

    if r.status_code != 200:
        raise Exception("HTTP error " + str(r.status_code) + ": " + r.text)

    return r.json()
