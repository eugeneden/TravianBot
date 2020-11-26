import re
import random
import time
from bs4 import BeautifulSoup
from robobrowser import RoboBrowser
# from .buildings import *


class TravianApi:

    def __init__(self, user, password, server, domain):
        self.browser = RoboBrowser(history=True, parser='html.parser', user_agent='User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0')
        self.browser.open('https://www.travian.net/')
        self.server = server.strip()
        self.domain = domain
        self.user = user
        self.password = password

    @staticmethod
    def sleep():
        time.sleep(abs(random.normalvariate(1.21, 1)))

    def logout(self):
        url = 'https://%s.travian.%s/logout.php' % (self.server, self.domain)
        self.browser.open(url)

    def login(self):
        url = 'https://%s.travian.%s/' % (self.server, self.domain)
        self.browser.open(url)
        logging_form = self.browser.get_form(action='/login.php')
        logging_form.fields['password'].value = self.password
        logging_form.fields['name'].value = self.user
        self.browser.submit_form(logging_form)

    def get_race(self):
        race = 'Ошибка определения'
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        try:
            self.open_page(url)
            race_img = self.browser.find('img', {'class': 'nation'})
            if race_img:
                race = race_img.attrs['alt']
        except:
            pass

        return race

    def show_actual_page(self):
        page = self.browser.parsed
        print(page)

    def list_villages(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        villages = []
        for item in self.browser.find('div', {'id': 'sidebarBoxVillagelist'}).find('div', {'class': 'innerBox content'}).find_all('li'):
            name = item.find('a').find('div', {'class': 'name'}).getText()
            id_ = re.search(r"\?.+=(\d+)&", item.find('a')['href']).group(1)
            villages.append(Village(name, id_))
        return villages

    def set_village(self, village_id):
        url = 'https://%s.travian.%s/dorf1.php?newdid=%s&' % (self.server, self.domain, village_id)
        self.open_page(url)

    def show_available_units(self, solar_id):
        url = 'https://%s.travian.%s/build.php?id=%s' % (self.server, self.domain, solar_id)
        self.open_page(url)
        soup = BeautifulSoup(str(self.browser.parsed), 'html.parser')
        units = soup.find('div', {'class': 'buildActionOverview trainUnits'}).find_all('div', {'class': 'details'})
        _u = []
        for item in units:
            name = item.find('div', {'class': 'tit'}).find('img')['alt']
            quant_available = item.find('a', {'onclick': re.compile(r"div.details")}).getText()
            _u.append((name, quant_available))
        return _u

    def get_actual_units(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        troops = {}
        for item in self.browser.find('table', {'id': 'troops'}).find_all('tr'):
            try:
                troops[item.find('td', {'class': 'un'}).getText()] = item.find('td', {'class': 'num'}).getText()
            except:
                pass
        return troops

    def get_actual_units_by_tier(self):
        url = 'https://%s.travian.%s/build.php?tt=1&gid=16' % (self.server, self.domain)
        self.open_page(url)
        dic = {'t1': 0, 't2': 0, 't3': 0, 't4': 0, 't5': 0, 't6': 0, 't7': 0, 't8': 0, 't9': 0, 't10': 0}
        for item in self.browser.find_all('tbody', {'class': 'units last'}):
            troops = item.find_all('td')
            dic['t1'] += int(troops[0].getText())
            dic['t2'] += int(troops[1].getText())
            dic['t3'] += int(troops[2].getText())
            dic['t4'] += int(troops[3].getText())
            dic['t5'] += int(troops[4].getText())
            dic['t6'] += int(troops[5].getText())
            dic['t7'] += int(troops[6].getText())
            dic['t8'] += int(troops[7].getText())
            dic['t9'] += int(troops[8].getText())
            dic['t10'] += int(troops[9].getText())
        return dic

    def get_village_units_by_tier(self):
        url = 'https://%s.travian.%s/build.php?tt=1&gid=16' % (self.server, self.domain)
        self.open_page(url)
        dic = {'t1': 0, 't2': 0, 't3': 0, 't4': 0, 't5': 0, 't6': 0, 't7': 0, 't8': 0, 't9': 0, 't10': 0}
        troops = self.browser.find('table', {'class': 'troop_details'}).find_all('tbody', {'class': 'units last'})[
            0].find_all('td')
        dic['t1'] += int(troops[0].getText())
        dic['t2'] += int(troops[1].getText())
        dic['t3'] += int(troops[2].getText())
        dic['t4'] += int(troops[3].getText())
        dic['t5'] += int(troops[4].getText())
        dic['t6'] += int(troops[5].getText())
        dic['t7'] += int(troops[6].getText())
        dic['t8'] += int(troops[7].getText())
        dic['t9'] += int(troops[8].getText())
        dic['t10'] += int(troops[9].getText())
        return dic

    def create_units(self, solar_id, t1=0, t2=0, t3=0, t4=0, t5=0, t6=0, t7=0, t8=0, t9=0, t10=0):
        url = 'https://%s.travian.%s/build.php?id=%s' % (self.server, self.domain, solar_id)
        self.login()
        self.open_page(url)
        search_form = self.browser.get_form(action='build.php?id=%s' % solar_id)

        dic = {'t1': t1, 't2': t2, 't4': t4, 't5': t5, 't6': t6, 't7': t7, 't8': t8, 't9': t9, 't10': t10, 't3': t3}
        for key, value in dic.items():
            try:
                search_form.fields[key].value = value
            except:
                pass
        self.browser.submit_form(search_form)

    def send_attack(self, coord, mode='4', t1=0, t2=0, t3=0, t4=0, t5=0, t6=0, t7=0, t8=0, t9=0, t10=0, **kwargs):
        url = 'https://%s.travian.%s/build.php?id=39&gid=16&tt=2' % (self.server, self.domain)
        self.open_page(url)

        search_form = self.browser.get_form(action='/build.php?gid=16&tt=2')
        dic = {'t1': t1, 't2': t2, 't3': t3, 't4': t4, 't5': t5, 't6': t6, 't7': t7, 't8': t8, 't9': t9, 't10': t10}
        for key, value in dic.items():
            try:
                search_form.fields[key].value = value
            except Exception:
                pass

        search_form.fields['x'].value = coord[0]
        search_form.fields['y'].value = coord[1]
        search_form.fields['c'].value = mode

        self.sleep()
        self.browser.submit_form(search_form)
        search_form = self.browser.get_form(action='/build.php?gid=16&tt=2')

        self.sleep()
        self.browser.submit_form(search_form, submit='a')  # TODO rewrite it with Selenium

    def get_next_atack(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        soup = BeautifulSoup(str(self.browser.parsed), 'html.parser')
        seconds = soup.find('table', {'id': 'movements'}).find('span', {'class': 'timer'})['value']
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)

        print('%s -> %d:%02d:%02d' % (seconds, h, m, s))

    def open_page(self, url, mlya=0):
        try:
            self.browser.open(url)
        except Exception as err:
            if mlya == 3:
                raise Exception('Не удалось открыть страницу: %s, ошибка: %s' % url, str(err))
            self.login()
            self.open_page(url, mlya + 1)

    def is_busy(self):
        if self.actual_queue() == "Empty queue":
            return False
        else:
            return True

    def actual_queue(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        try:
            soup = BeautifulSoup(str(self.browser.parsed), 'html.parser')
            queue = soup.find('div', {'class': 'boxes buildingList'}).find_all('li')
            for item in queue:
                soup = BeautifulSoup(str(item), 'html.parser')
                div_name = soup.find('div', {'class': 'name'})
                print(div_name.getText().replace('"', '').strip())
                div_duration = soup.find('div', {'class': 'buildDuration'})
                print(div_duration.getText().replace('"', '').replace('\t', '').strip())
                return "%s | %s" % (div_name.getText().replace('"', '').replace('\t', '').strip(),
                                    div_duration.getText().replace('"', '').strip())
        except:
            return "Empty queue"

    def busy_until(self):
        out = self.actual_queue()
        if out != "Empty queue":
            build, time = out.split('|')
            ftr = [3600, 60, 1]
            hour = re.match('(.*) h', time).group(1)
            return sum([a * b for a, b in zip(ftr, map(int, hour.split(':')))])

    def build_resource(self, resource_id):
        if not self.is_busy():
            try:
                self.open_page('https://%s.travian.%s/build.php?id=%s' % (self.server, self.domain, resource_id))
                onclick = self.browser.select('.green.build')[0].attrs['onclick']
                print(onclick)
                link = re.match(".*'(.*)'.*", onclick).group(1)
                print(link)
                if link != 'disabled':
                    url = 'https://%s.travian.%s/%s' % (self.server, self.domain, link)
                    self.open_page(url)
                else:
                    raise Exception('Level 1')
            except:
                return "Unavailable"
        else:
            return "Full queue"

    def show_avilable_building(self, solar_id, category_id=1):
        self.open_page(
            'https://%s.travian.%s/build.php?id=%s&category=%s' % (self.server, self.domain, solar_id, category_id))
        soup = BeautifulSoup(str(self.browser.parsed), 'html.parser')
        buildings = soup.find(id="build").find_all('div', {'class': 'buildingWrapper'})
        for item in buildings:
            try:
                soup = BeautifulSoup(str(item), 'html.parser')
                label = soup.find('h2').getText().strip()
                link = re.match(".*'(.*)'.*", soup.find("button", {'class': 'green new'}).attrs["onclick"]).group(1)
                print('%s -> %s' % (re.findall('\d+', link)[1], label))
            except:
                pass

    def get_solar_id_by_building_id(self, building_id):
        self.open_page('https://%s.travian.%s/dorf2.php' % (self.server, self.domain))
        soup = BeautifulSoup(str(self.browser.parsed), 'html.parser')
        solar = soup.find('div', 'g{}'.format(building_id))
        if solar:
            for _class in solar.attrs['class']:
                a = re.match(r'^a(\d{1,2})$', _class)
                if a:
                    return int(a.group(1))

    def build_building(self, building_id):
        try:
            solar_id = self.get_solar_id_by_building_id(building_id)
            self.open_page('https://%s.travian.%s/build.php?id=%s&category=1' % (self.server, self.domain, solar_id))
            soup = BeautifulSoup(str(self.browser.parsed), 'html.parser')
            code = re.findall('c=.*\Z', re.match(".*'(.*)'.*",
                                                 soup.find("button", {'class': 'green new'}).attrs["onclick"]).group(
                1))[0][2:]

            self.open_page('https://%s.travian.%s/dorf2.php?a=%s&id=%s&c=%s' % (
            self.server, self.domain, building_id, solar_id, code))
            return 'Ok'
        except:
            return 'Unavailable'

    def upgrade_building(self, solar_id):
        try:
            self.open_page('https://%s.travian.%s/build.php?id=%s' % (self.server, self.domain, solar_id))
            soup = BeautifulSoup(str(self.browser.parsed), 'html.parser')
            link = re.match(".*'(.*)'.*", soup.find("button", {'class': 'green build'}).attrs["onclick"]).group(1)
            url = 'https://%s.travian.%s/%s' % (self.server, self.domain, link)
            self.open_page(url)
        except:
            return "Unavailable"

    def get_actual_production(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        production = self.browser.find(id="production").find_all("tr")
        for item in production:
            soup = BeautifulSoup(str(item), 'html.parser')
            res = soup.find("td", {'class': 'res'})
            if res != None:
                resource = res.getText().strip()
            amo = soup.find("td", {'class': 'num'})
            if amo != None:
                ammount = amo.getText().strip()
            if res != None and amo != None:
                print('%s -> %s' % (resource, ammount))

    def map_resources(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        resource_map = self.browser.find(id="rx").find_all("area")
        for item in resource_map:
            try:
                print('%s -> %s' % (re.findall('\d+\Z', item['href'])[0], item['alt']))
            except:
                pass

    def map_buildings(self):
        url = 'https://%s.travian.%s/dorf2.php' % (self.server, self.domain)
        self.open_page(url)
        building_map = self.browser.find(id="clickareas").find_all("area")
        for item in building_map:
            try:
                print('%s -> %s' % (re.findall('\d+\Z', item['href'])[0],
                                    item['alt'].split('||')[0].replace('<span class="level">', '').replace('</span>',
                                                                                                           '')))
            except:
                pass

    def actual_resources(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        actual_resources = self.browser.find(id="stockBar").find_all("li")
        actual_resources_list = []
        for item in actual_resources:
            soup = BeautifulSoup(str(item), 'html.parser')
            res = None
            amo = None
            res = soup.find("img", {'src': 'img/x.gif'})
            if res != None:
                resource = res['alt'].strip()
            amo = soup.find("span", {'class': 'value'})
            if amo != None:
                ammount = amo.getText().strip()
            if res != None and amo != None:
                print('%s -> %s' % (resource, ammount))
                actual_resources_list.append(Resource(resource, ammount))
        return actual_resources_list

    def get_alliance(self, alliance_id):
        tribes = {'tribe1': 'Romans',
                  'tribe2': 'Teutons',
                  'tribe3': 'Gauls',
                  'tribe4': '',
                  'tribe5': '',
                  'tribe6': 'Egypthians',
                  'tribe7': 'Huns'}
        url = 'https://%s.travian.%s/allianz.php?aid=%s' % (self.server, self.domain, alliance_id)
        self.open_page(url)
        contain = self.browser.find('div', {'id': 'details'}).find_all('tr')
        info = {}
        for item in contain:
            tag = item.find('th').getText()
            data = item.find('td').getText()
            info[tag] = data
        url = 'https://%s.travian.%s/allianz.php?aid=%s&action=members' % (self.server, self.domain, alliance_id)

        self.open_page(url)
        contain = self.browser.find('table', {'class': 'allianceMembers'}).find_all('tr')
        members = []
        for item in contain:
            try:

                tribe = tribes[item.find('td', {'class': 'tribe'}).find('div')['class'][1]]
                name = item.find('td', {'class': 'player'}).find('a').getText()
                online = item.find('td', {'class': 'player'}).find('img')['title']
                population = item.find('td', {'class': 'population'}).getText()
                villages = item.find('td', {'class': 'villages'}).getText()
                members.append(User(name, tribe, online, population, villages))
            except:
                print("Exception")
                pass

        return Alliance(info, members)

    def show_land(self, coord_x, coord_y):
        url = 'https://%s.travian.%s/position_details.php?x=%s&y=%s' % (self.server, self.domain, coord_x, coord_y)
        self.open_page(url)

        if self.browser.find('div', {'id': 'map_details'}) == None:
            return "Wildernes"
        else:
            if self.browser.find('div', {'id': 'map_details'}).find('table', {'id': 'village_info'}) == None:
                return "Abandoned valley"
            else:
                village_info = self.browser.find('div', {'id': 'map_details'}).find('table',
                                                                                    {'id': 'village_info'}).find_all(
                    'tr')
                data = {}
                for item in village_info:
                    data[item.find('th').getText()] = item.find('td').getText()
                if self.browser.find('div', {'id': 'tileDetails'}).find('div', {'class': 'options'}).find('span', {
                    'class': 'a arrow disabled'}) == None:
                    data['Raidable'] = True
                    data['Until_safe'] = ''
                else:
                    if self.browser.find('div', {'id': 'tileDetails'}).find('div', {'class': 'options'}).find('span', {
                        'class': 'a arrow disabled'}).getText() != "Send troops.":
                        data['Raidable'] = True
                        data['Until_safe'] = ''
                    else:
                        data['Raidable'] = False
                        data['Until_safe'] = re.search('until (.*)',
                                                       self.browser.find('div', {'id': 'tileDetails'}).find('div', {
                                                           'class': 'options'}).find('span',
                                                                                     {'class': 'a arrow disabled'})[
                                                           'title']).group(1)

                return data

    def send_resources(self, coord, r1=0, r2=0, r3=0, r4=0):
        url = 'https://ts80.travian.com/build.php?t=5&id=31'
        self.open_page(url)
        ajax = re.match(".* = \'(.*)\'", self.browser.find('script').getText().split('\n')[1]).group(1)
        data = {'cmd': 'prepareMarketplace',
                'r1': r1,
                'r2': r2,
                'r3': r3,
                'r4': r4,
                'dname': '',
                'x': coord[0],
                'y': coord[1],
                'id': self.browser.find('form').find('input', {'id': 'id'})['value'],
                't': self.browser.find('form').find('input', {'id': 't'})['value'],
                'x2': '1',
                'ajaxToken': ajax}
        response = self.browser.session.post("https://ts80.travian.com/ajax.php?cmd=prepareMarketplace", data=data)
        soup = BeautifulSoup(response.json()['response']['data']['formular'], 'html.parser')
        resp = {}
        for item in soup.find_all('input'):
            resp[item['id']] = item['value']
        resp['r1'] = r1
        resp['r2'] = r2
        resp['r3'] = r3
        resp['r4'] = r4
        resp['ajaxToken'] = ajax
        response = self.browser.session.post("https://ts80.travian.com/ajax.php?cmd=prepareMarketplace", data=resp)

    def list_report(self):
        url = 'https://%s.travian.%s/berichte.php' % (self.server, self.domain)
        self.open_page(url)
        reports = {}
        for item in self.browser.find('table', {'id': 'overview'}).find('tbody').find_all('tr'):
            if item.find('img', {'alt': 'Не прочитано'}) != None:
                tag = item.find('div', {'class': ''}).find('a').getText()
                link = item.find('div', {'class': ''}).find('a')['href']
                reports[tag] = link
        return reports

    def help(self):
        methods = '''Methods:
        loggin(user, pasword)
        actual_queue()
        build_resource(resource_id)
        show_avilable_building(solar_id,category_id=1)
        build_building(solar_id, building_id)
        upgrade_building(solar_id)
        get_actual_production()
        map_resources()
        map_buildings()
        actual_resources()
'''
        return (methods)

    def get_movements(self):
        url = 'https://%s.travian.%s/dorf1.php' % (self.server, self.domain)
        self.open_page(url)
        movements = {'income': {}, 'outcome': {}}
        classes = ('a1', 'a2', 'd1', 'd2', 'adventure')
        for item in self.browser.find('table', {'id': 'movements'}).find_all('tr'):
            try:
                movement_type = item.find('th', {'class': "troopMovements header"}).getText().strip()[:-1]
                continue
            except:
                pass

            for _class in classes:
                try:
                    if movement_type == 'Приходящие войска':
                        movements['income'][item.find('span', {'class': _class}).getText()] = item.find(
                            'span', {'class': 'timer'}).getText()
                    else:
                        movements['outcome'][item.find('span', {'class': _class}).getText()] = item.find(
                            'span', {'class': 'timer'}).getText()
                except:
                    pass

        return movements


class Resource:
    def __init__(self, resource, amount):
        self.resource = resource
        self.amount = amount


class Alliance:
    def __init__(self, info, members):
        self.info = info
        self.members = members


class Report:
    def __init__(self, atack, defense):
        self.atack = atack
        self.defense = defense


class User:
    def __init__(self, name, tribe, online, population, villages):
        self.name = name
        self.tribe = tribe
        self.online = online
        self.population = population
        self.villages = villages


class Village:
    def __init__(self, name, id_):
        self.id = id_
        self.name = name

    def __repr__(self):
        return 'Village("{}", {})'.format(self.name, self.id)

    __str__ = __repr__
