import os

import requests
from dotenv import load_dotenv

load_dotenv()


class WikiApi:
    S = requests.Session()
    URL = "https://uz.wikipedia.org/w/api.php"
    last_pages_limit = "10"
    last_pages_limit_edits = "25"

    def __init__(self):
        self.login_request()

    def get_token(self):
        PARAMS_0 = {
            'action': "query",
            'meta': "tokens",
            'type': "login",
            'format': "json"
        }
        R = self.S.get(url=self.URL, params=PARAMS_0)
        DATA = R.json()
        LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
        return LOGIN_TOKEN

    def login_request(self):
        PARAMS_1 = {
            'action': "login",
            'lgname': os.getenv("WIKI_LOGIN"),
            'lgpassword': os.getenv("WIKI_PASS"),
            'lgtoken': self.get_token(),
            'format': "json"
        }
        R = self.S.post(self.URL, data=PARAMS_1)
        DATA = R.json()
        return DATA

    def get_new_pages(self) -> dict:
        N_PAGES_PARAMS = {
            "rcprop": "title|timestamp|sizes|user|ids",
            "rctype": "new",
            "list": "recentchanges",
            "action": "query",
            "rclimit": self.last_pages_limit,
            "uselang": "uz",
            "format": "json",
        }

        R = self.S.get(url=self.URL, params=N_PAGES_PARAMS)

        DATA = R.json()

        # RECENTCHANGES = DATA['query']['recentchanges']

        # for rc in RECENTCHANGES:
        #     print(str(rc['title']))
        return DATA

    def get_last_edits(self) -> dict:
        """Fetches the last 20 edits made on Wikipedia pages."""
        EDITS_PARAMS = {
            "rcprop": "title|timestamp|sizes|user|ids",
            "rctype": "edit",  # Specifies that we want to fetch edit changes
            "list": "recentchanges",
            "action": "query",
            "rclimit": self.last_pages_limit_edits,  # Limit the results to the last 20 edits
            "uselang": "uz",
            "format": "json",
        }

        R = self.S.get(url=self.URL, params=EDITS_PARAMS)
        DATA = R.json()
        return DATA
