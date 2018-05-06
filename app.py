import time
from multiprocessing import Pool
from configparser import ConfigParser
from api import TravianApi
from utils import get_distance, printl, shake_list


INIT_TROOPS_SPEED = {
            'Egyptians': {
                't1': 14 / 3600,
                't2': 12 / 3600,
                't3': 14 / 3600,
                't4': 32 / 3600,
                't5': 30 / 3600,
                't6': 20 / 3600
            }
        }


class FarmData:
    troops = {}
    start_coords = tuple()
    destination = tuple()
    race = ''
    max_n = 0

    def __init__(self, troops: dict, start_coords: tuple, destination: tuple, race: str, max_n: int):
        self.troops = troops
        self.destination = destination
        self.start_coords = start_coords
        self.race = race
        self.max_n = max_n

    @property
    def distance(self):
        return get_distance(self.start_coords, self.destination)

    @property
    def troops_time(self):
        return max([round(self.distance / INIT_TROOPS_SPEED[self.race][tt], 0) + 1 for tt in self.troops])

    def __repr__(self):
        return 'FarmData(troops=%s, destination=%s, troops_time=%s)' % (str(self.troops),
                                                                        str(self.destination), str(self.troops_time))


class Farm:
    settings = ConfigParser()
    settings.read('config/config.ini')

    api = TravianApi(
        domain=settings.get('connection', 'domain'),
        server=settings.get('connection', 'server'),
        user=settings.get('connection', 'username'),
        password=settings.get('connection', 'password')
    )

    def __init__(self):
        self.stable_id = 38
        self.barracks_id = 32

        self.main_village = (158, 26)

        self.farm_troops = {'Ополченцы': 't1', 'Колесницы Решефа': 't6', 'Служители Аш': 't2',
                            'Стражники Анхура': 't5', 'Воины с хопешем': 't3'}

        self.farm_list = shake_list(list({
            (155, 37), (149, 40), (156, 47), (158, 47), (156, 22), (158, 19), (162, 45)
        }))

    def run(self, n=5):
        printl('--------------Main-start--------')

        available_troops = self.get_available_farm_troops()

        _a = {}
        for t in available_troops:
            _n = int(available_troops[t]) // len(self.farm_list)
            _a[t] = _n

        printl('Available troops: ', available_troops)

        farm_list = [
            FarmData(troops={'t5': _a.get('t5', 0), 't6': _a.get('t6', 0)}, start_coords=self.main_village,
                     destination=crds, race='Egyptians', max_n=n) for crds in self.farm_list
        ]

        printl('Farm list: ', farm_list)

        printl('--------------Start-pool--------')

        with Pool(len(self.farm_list)) as p:
            p.map(self.farm, farm_list)

        printl('--------------Main-end----------')

    def farm(self, farm_data: FarmData):
        printl('--------------Worker-start------', farm_data.destination)
        for _ in range(farm_data.max_n):
            if self.api.send_attack(farm_data.destination, **farm_data.troops):
                printl('Error sending troops to %s, wait for 5 min and retry...' % str(farm_data.destination))
                time.sleep(300)
                continue
            printl('Success: ', farm_data)
            time.sleep(farm_data.troops_time * 2)
        printl('--------------Worker-end--------')

    def get_available_farm_troops(self):
        actual_troops = self.api.get_actual_units()
        available_troops = {}
        troops_for_farm = {self.farm_troops.get(k, k): v for k, v in actual_troops.items()}
        for k, v in self.farm_troops.items():
            if troops_for_farm.get(v):
                available_troops[v] = troops_for_farm[v]
        return available_troops


if __name__ == '__main__':
    try:
        bot = Farm()
        bot.api.set_village(9554)
        print(bot.api.list_report())
        # bot.run()
    except KeyboardInterrupt:
        exit(0)
