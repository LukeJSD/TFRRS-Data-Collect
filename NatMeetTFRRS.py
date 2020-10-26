import pandas as pd
import requests
from bs4 import BeautifulSoup


class Meet:
    def __init__(self, ID, Name):
        # Construct the url and make the request
        url_stub = "http://www.tfrrs.org/results/xc/{}/{}".format(
            ID, Name.replace(' ', '_')
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }
        response = requests.get(url_stub, headers=headers)

        # If the reponse succeeded
        if response.status_code < 300 and response.status_code >= 200:
            # panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace('colspan="100%"', 'colspan="3"')
            self.initialize()

        # If the response failed
        else:
            self.HTML = None
            raise Exception("Could not retrieve", response.status_code)


    def getAthleteInfo(self):
        athletes = {
            'F' : {},
            'M' : {}
        }
        rows = self.soup.find_all('tr')

        # Pull the url tail for each team page
        for row in rows:
            temp = []
            if 'tfrrs.org/athletes/' in str(row):
                for link in row.find_all("a"):
                    if "tfrrs.org/athletes/" in str(link):
                        link_id = str(link)[33: str(link).index(".html")]
                        name = link.text
                        last, first = name.split(', ')[:2]
                        name = first + " " + last
                        temp.append(name)
                        temp.append(link_id)
                    if "tfrrs.org/teams/" in str(link):
                        team = str(link)[47: str(link).index(".html")].replace('_', ' ')
                        gender = str(link)[45].upper()
                        temp.append(team)
                athletes[gender][link_id] = temp

        return athletes


    def initialize(self):
        self.dfs = pd.read_html(self.HTML)
        self.soup = BeautifulSoup(self.HTML, "html5lib")
        self.AthleteInfo = self.getAthleteInfo()

        return None


def nat_meet_ids():
    return {
        'NCAA Division II Cross Country Championships' : {
            2019: 16713,
            2018: 15037,
            2017: 13406,
            2016: 11246,
            2015: 9348,
            2014: 7658,
            2013: 6221,
            2012: 4796,
        }
    }
