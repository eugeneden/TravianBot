import logging
import sys
import time

from dataclasses import dataclass
from pathlib import Path
from threading import Lock, Thread
from configparser import ConfigParser

from api import TravianApi, Coordinates, Troops
from utils import get_distance, shake_list

logging.basicConfig(
    format=u'%(asctime)s | %(name)s | %(levelname)s '
           u'| %(module)s.py:%(lineno)s | %(message)s',
    level=logging.INFO,
    stream=sys.stdout,
)

urllib_logger = logging.getLogger('urllib3.connectionpool')
urllib_logger.setLevel(logging.ERROR)


class Race:
    GALS = 'gals'
    EGYPTIANS = 'egyptians'


INIT_TROOPS_SPEED = {
    Race.GALS: {
        't1': 7 / 3600,
        't2': 6 / 3600,
        't4': 19 / 3600,
        't5': 16 / 3600,
        't6': 13 / 3600,
    },
    Race.EGYPTIANS: {
        't1': 14 / 3600,
        't2': 12 / 3600,
        't3': 14 / 3600,
        't4': 32 / 3600,
        't5': 30 / 3600,
        't6': 20 / 3600
    }
}


@dataclass(frozen=True)
class FarmData:
    troops: Troops
    start_coords: Coordinates
    destination: Coordinates
    race: str

    @property
    def distance(self):
        return get_distance(self.start_coords, self.destination)

    @property
    def troops_time(self):
        return max([
            round(
                self.distance / INIT_TROOPS_SPEED[self.race][tt], 0
            ) + 1 for tt in self.troops
        ])

    def __repr__(self):
        return 'FarmData(troops={}, destination={})'.format(
            self.troops, self.destination,
        )


class Farm:
    def __init__(self):
        self.main_village = (-15, -85)
        self.farm_troops = {
            't4',
        }
        self.farm_list = shake_list(list({
            (-18, -84),
            (-11, -86),
            (-12, -88),
            (-19, -89),
            (-12, -90),
            (-21, -89),
            (-9, -90),
            (-7, -87),
            (-21, -79),
            (-24, -77),
            (-21, -74),
            (-29, -85),
            (-1, -90),
            (0, -87),
            (0, -89),
            (-31, -84),
            (0, -91),
            (-30, -77),
            (-33, -84),
            (3, -89),
            (3, -91),
            (-33, -76),
            (-34, -78),
            (-31, -72),
            (1, -71),
            (-19, -64),
            (7, -85),
            (-26, -65),
            (-23, -62),
            (-14, -60),
            (10, -88),
            (-41, -78),
            (-6, -59),
            (-9, -58),
            (-3, -60),
            (11, -73),
            (-15, -55),
            (-34, -63),
            (-44, -79),
            (-37, -64),
            (16, -86),
            (16, -83),
            (16, -90),
            (-18, -117),
            (-34, -59),
            (18, -85),
            (-17, -52),
            (18, -88),
            (8, -61),
        }))

        ignored = {
            (3, -82), (-19, -85), (-18, -69), (6, -90), (-35, -69),
        }
        for i in ignored:
            try:
                self.farm_list.remove(i)
            except ValueError:
                pass

        base_path = Path(__file__).parent
        settings = ConfigParser()
        settings.read(base_path.joinpath('config/config.ini'))
        self.api = TravianApi(base_path, settings)
        logging.info('Logging in...')
        self.api.login()

    def run(self):
        logging.info('Getting available units info...')
        available_troops = self._get_available_troops()
        logging.info('Available troops: %s', available_troops)
        if not available_troops:
            logging.error('Not enough units. Exit...')
            return
        logging.info('Farm list size: %s', len(self.farm_list))
        farm_list = self._get_farm_list(available_troops, Race.GALS)

        print('Used troops:', sum(map(lambda x: sum(x.troops.values()), farm_list)))

        lock = Lock()
        for i, data in enumerate(farm_list, 1):
            Thread(target=self._farm, args=(data, lock, i)).start()

    def _farm(self, data: FarmData, lock: Lock, num: int):
        while True:
            farm_time = data.troops_time * 2 + 1
            lock.acquire()
            try:
                available_troops = self._get_available_troops()
                for tier, count in data.troops.items():
                    if available_troops.get(tier, 0) < count:
                        pause = 30
                        logging.info(f'{num} | Sent: {data.destination} {data.troops} '
                                     f'No available troops! | Sleeping for {pause} seconds...')
                        break
                else:
                    self.api.send_attack(data.destination, data.troops)
                    pause = farm_time
                    logging.info(
                        f'{num} | Sent: {data.destination} {data.troops} | Sleeping for {data.troops_time} seconds...'
                    )
            except Exception:
                logging.exception('__FARM__')
                pause = 60
            finally:
                lock.release()
            
            time.sleep(pause)

    def _get_available_troops(self) -> Troops:
        actual_troops = self.api.get_actual_units_by_tier()
        troops = {
            k: v for k, v in actual_troops.items() if k in self.farm_troops and v
        }
        return Troops(troops)

    @staticmethod
    def _group_units(available, size) -> dict:
        return {t: available[t] // size for t in available}

    @staticmethod
    def _group(available, size):
        res = []
        for i in range(size):
            _a = Farm._group_units(available, size - i)

            avail_copy = {k: v for k, v in available.items()}
            for tier, count in avail_copy.items():
                avail_copy[tier] = count - _a.get(tier, 0)

            available = avail_copy
            res.append(_a)
        return res

    def _get_farm_list(self, available: Troops, race: str) -> list[FarmData]:
        troops = self._group(available, len(self.farm_list))
        res = []
        for i, coords in enumerate(self.farm_list):
            res.append(FarmData(
                troops=Troops(troops[i]),
                start_coords=Coordinates(self.main_village),
                destination=Coordinates(coords),
                race=race,
            ))
        return res


if __name__ == '__main__':
    try:
        bot = Farm()
        bot.api.set_village(22824)
        bot.run()
    except KeyboardInterrupt:
        logging.info('Exiting...')
        exit(0)
    except Exception:
        logging.exception('MAIN')
