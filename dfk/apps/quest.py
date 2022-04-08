# milestone 1: dashboard of your heros questing
#   - stamina remaining
#   - time to full stamina
#   - questing or not
#   - time left questing

# milestone 2: quest bot

from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import auto, Enum
import logging
import os
from subprocess import call
import sys
import time
from typing import Dict, List

from colors import color

from dfk.hero import get_hero, get_users_heroes
from dfk.quest import Quest
from dfk.quest.utils import utils as quest_utils

REFRESH = 15  # seconds
WALLET = ''
RPC_SERVER = 'https://api.harmony.one'

BASE_TABLE_FMT = '{:<6} {:<14} {:<8}'
QUEST_TABLE_FMT = BASE_TABLE_FMT + ' {:<9} {:<15}'
REGEN_TABLE_FMT = BASE_TABLE_FMT + ' {:<14} {:<11} {:<14} {:<11}'

LOG_FMT = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
LOG = logging.getLogger('DFK-quest')
LOG.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO, format=LOG_FMT, stream=sys.stdout)


class QuestStatus(Enum):
    QUESTING = auto()
    REGENERATING = auto()


@dataclass
class BaseHero:
    id: int
    professions: Dict[str, int]
    current_stamina: int
    total_stamina: int
    stamina_full_at_time: timedelta

    @property
    def max_profession(self) -> str:
        # TODO: this is not necessarily the hero's genetic profession tho
        return max(self.professions, key=self.professions.get)

    @property
    def time_to_full(self) -> timedelta:
        precise_delta = datetime.fromtimestamp(self.stamina_full_at_time) - datetime.now()
        return precise_delta - timedelta(microseconds=precise_delta.microseconds)


@dataclass
class QuestingHero(BaseHero):
    quest_complete_at_time: float  # timestamp
    _tick_per_stamina: int = 10  # TODO: assumes genetic profession; its 12 for non-genetic profession

    # TODO: use time_to_full to adjust current_stamina?

    @property
    def time_left(self) -> timedelta:
        return timedelta(seconds=int(self.quest_complete_at_time - time.time()))

    @property
    def status(self) -> QuestStatus:
        return QuestStatus.QUESTING

    @property
    def completed(self) -> bool:
        # n.b., quirk of negative timedeltas
        return self.time_left.days < 0

    # TODO: this should know which profession is being quested


@dataclass
class RegeneratingHero(BaseHero):
    _tick_per_stamina: int = 20

    # TODO: stamina_per_attempt assumes max profession is aligned with genetic professsion;
    # if unaligned, this should be 7
    _stamina_per_attempt = 5  # for fishing and foraging

    # source: https://twitter.com/0xAccess/status/1486446145626857483
    _gardening_stam_ideal = 15  # for 3 rune + 1 green egg + 1 jackpot chances
    # _mining_stam_ideal = 10  # for 2 rune + 1 yellow egg chance  # TODO: need 15 stam for jewel mining jackpot
    _mining_stam_ideal = 20  # for 4 rune + 2 yellow egg chances

    @property
    def status(self) -> QuestStatus:
        return QuestStatus.REGENERATING

    @property
    def time_to_max_prof(self) -> timedelta:
        td = None
        if self.max_profession == 'gardening' and self.current_stamina < self._gardening_stam_ideal:
            td = timedelta(minutes=(self._gardening_stam_ideal-self.current_stamina-1)*self._tick_per_stamina)

        if self.max_profession == 'mining' and self.current_stamina < self._mining_stam_ideal:
            td = timedelta(minutes=(self._mining_stam_ideal-self.current_stamina-1)*self._tick_per_stamina)

        fishing_foraging_stam_ideal = self.total_stamina - (self.total_stamina % self._stamina_per_attempt)
        if self.max_profession in ('fishing', 'foraging') and \
            self.current_stamina < fishing_foraging_stam_ideal:
            td = timedelta(minutes=(fishing_foraging_stam_ideal-self.current_stamina-1)*self._tick_per_stamina)

        if td is None:
            return timedelta(seconds=0)

        # using time_to_full to make the above estimate more precise
        extra_minutes = ((self.time_to_full.seconds // 60) % 60) % self._tick_per_stamina
        extra_seconds = self.time_to_full.seconds % 60

        td += timedelta(minutes=extra_minutes, seconds=extra_seconds)

        return td


    @property
    def regenerated(self) -> bool:
        return self.current_stamina == self.total_stamina

    @property
    def ready_for_max_profession(self) -> bool:
        if self.max_profession == 'gardening' and \
            self.current_stamina >= self._gardening_stam_ideal:
            return True

        if self.max_profession == 'mining' and \
            self.current_stamina >= self._mining_stam_ideal:
            return True

        if self.max_profession in ('fishing', 'foraging') and \
            self.current_stamina >= self.total_stamina - (self.total_stamina % self._stamina_per_attempt):
            return True

        return False


def clear() -> None:
    # TODO: share with hero.py app
    _ = call('clear' if os.name =='posix' else 'cls', shell=True)


def timedelta_to_str(td: timedelta) -> str:
    if td.days < 0:
        # n.b., time 'expired'
        return '-' + str(timedelta() - td)
    else:
        return str(td)


def print_quest_status(quest: Quest, hero_ids: List[int]):
    quest_heroes: List[QuestingHero] = []
    regen_heroes: List[RegeneratingHero] = []

    for hero_id in hero_ids:
        raw_quest = quest.get_hero_quest(hero_id)
        quest_info = quest_utils.human_readable_quest(raw_quest)

        current_stam = quest.get_current_stamina(hero_id)
        hero = get_hero(hero_id, quest.rpc_address)
        professions = hero.get('professions', {})
        total_stam = hero.get('stats', {}).get('stamina', 0)
        stamina_full_at = hero.get('state', {}).get('staminaFullAt')

        if quest_info:
            quest_heroes.append(
                QuestingHero(
                    id=hero_id,
                    professions=professions,
                    current_stamina=current_stam,
                    total_stamina=total_stam,
                    quest_complete_at_time=quest_info['completeAtTime'],
                    stamina_full_at_time=stamina_full_at  # TODO: can't trust it during questing as-is
                )
            )
        else:
            regen_heroes.append(
                RegeneratingHero(
                    id=hero_id,
                    professions=professions,
                    current_stamina=current_stam,
                    total_stamina=total_stam,
                    stamina_full_at_time=stamina_full_at
                )
            )

    # TODO: provide local times option, in addition to time deltas

    clear()
    print(f'Last Refresh: {datetime.now()}')
    print('QUESTING...')

    print(color(QUEST_TABLE_FMT.format(
        'heroId',
        'maxProfession',
        'stamina',
        'timeLeft',
        'readyForPickup'
    ), style='underline'))
    for hero in quest_heroes:
        print(color(QUEST_TABLE_FMT.format(
            hero.id,
            hero.max_profession,
            f'{hero.current_stamina}/{hero.total_stamina}',
            timedelta_to_str(hero.time_left),
            'Y' if hero.completed else ''
        ), fg='green' if hero.completed else None))

    print()
    print('REGENERATING...')

    print(color(REGEN_TABLE_FMT.format(
        'heroId',
        'maxProfession',
        'stamina',
        '~timeToMaxProf',
        'timeToFull',
        'readyForMaxProf',
        'regenerated',
    ), style='underline'))
    for hero in regen_heroes:
        fg_color = None
        if hero.regenerated:
            fg_color = 'darkorchid'
        elif hero.ready_for_max_profession:
            fg_color = 'green'

        print(color(REGEN_TABLE_FMT.format(
            hero.id,
            hero.max_profession,
            f'{hero.current_stamina}/{hero.total_stamina}',
            timedelta_to_str(hero.time_to_max_prof),
            timedelta_to_str(hero.time_to_full),
            'Y' if hero.ready_for_max_profession else '',
            'Y' if hero.regenerated else '',
        ), fg=fg_color))

    time.sleep(REFRESH)


if __name__ == '__main__':
    LOG.info('Using RPC server ' + RPC_SERVER)

    quest = Quest(RPC_SERVER, LOG)
    hero_ids = sorted(get_users_heroes(WALLET, quest.rpc_address))

    while True:
        try:
            print_quest_status(quest, hero_ids)
        except KeyboardInterrupt:
            print()
            LOG.info('CTRL-C Caught, shutting down')
            exit()
        except Exception as e:
            LOG.warning(e)
            time.sleep(5)
