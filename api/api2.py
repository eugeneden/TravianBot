import random
import atexit
import time

from typing import NewType
from pathlib import Path
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

Coordinates = NewType('Coordinates', tuple[int, int])
Troops = NewType('Troops', dict[str, int])


class Api:
    def __init__(self, base_path: Path, settings: ConfigParser):
        self.server = settings.get('connection', 'server')
        self.domain = settings.get('connection', 'domain')
        self.user = settings.get('connection', 'username')
        self.password = settings.get('connection', 'password')
        self.url = f'https://{self.server}.travian.{self.domain}/'
        log_path = str(base_path.joinpath('logs/geckodriver.log'))
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(
            options=options,
            service_log_path=log_path,
        )
        self.browser.implicitly_wait(3)
        atexit.register(self.browser.quit)

    def open(self, path: str = ''):
        self.browser.get(self.url + path)

    @staticmethod
    def sleep():
        time.sleep(random.randint(1312, 2853) // 1000)

    def login(self):
        self.open()
        login_field = self.browser.find_element_by_name('name')
        login_field.send_keys(self.user)
        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys(self.password)
        cookies = self.browser.find_element_by_id(
            'CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll'
        )
        self.sleep()
        cookies.click()
        self.sleep()
        self.browser.find_element_by_name('s1').click()
        self.sleep()

    def set_village(self, village_id: int):
        self.open(f'dorf1.php?newdid={village_id}&')
        self.sleep()

    def get_actual_units_by_tier(self) -> Troops:
        """From troops page. Does not work if you support other villages."""
        self.open('build.php?id=39&gid=16&tt=1')
        self.sleep()
        tds = self.browser.find_elements_by_css_selector(
            'table.troop_details:last-child > tbody:nth-child(3) > tr:nth-child(1) > td.unit'
        )
        result = {}
        for i, td in enumerate(tds, 1):
            result[f't{i}'] = int(td.get_attribute('innerText'))
        return Troops(result)

    def get_actual_units_by_tier_(self) -> Troops:
        """From home page"""
        url: str = self.browser.current_url.split('?')[0]
        if not url.endswith('dorf1.php'):
            self.open('dorf1.php')
            self.sleep()

        tiers = []
        images = self.browser.find_elements_by_css_selector('table#troops img.unit')
        for img in images:
            klas = img.get_attribute('class')
            tier: str = klas.split(' ')[-1].replace('u2', 't')
            tiers.append(tier)

        tds = self.browser.find_elements_by_css_selector('table#troops td.num')
        nums = []
        for td in tds:
            nums.append(int(td.get_attribute('innerText')))

        return Troops(dict(zip(tiers, nums)))

    def send_attack(self, coord: tuple, troops: dict, mode: int = 4):
        """
        :param coord: (0, 0)
        :param troops: {'t1': 100, 't2': 100}
        :param mode:
            2 - Подкрепление
            3 - Атака: обычная
            4 - Атака: набег
        :return: None
        """
        self.open('build.php?id=39&gid=16&tt=2')
        self.sleep()

        for tier, count in troops.items():
            f = self.browser.find_element_by_name(f'troops[0][{tier}]')
            f.send_keys(str(count))

        mode_fields = self.browser.find_elements_by_name('c')
        for field in mode_fields:
            if int(field.get_property('value')) == mode:
                field.click()

        x_field = self.browser.find_element_by_id('xCoordInput')
        x_field.send_keys(str(coord[0]))
        y_field = self.browser.find_element_by_id('yCoordInput')
        y_field.send_keys(str(coord[1]))

        self.browser.find_element_by_id('btn_ok').click()
        self.sleep()
        self.browser.find_element_by_id('btn_ok').click()
        self.sleep()
