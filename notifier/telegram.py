import requests


class Telegram:
    def __init__(self, settings):
        self.settings = settings

    def send(self, message):
        token = self.settings.get('telegram', 'CRIER_BOT_API_TOKEN')
        url = 'http://crierbot.appspot.com/{}/send?message={}'
        requests.get(url.format(token, message))
