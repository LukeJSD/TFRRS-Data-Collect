import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from AthleteTfrrs import Athlete

class Conference:
    def __init__(self, ID):
        # Construct the url and make the request
        url_stub = "http://www.tfrrs.org/leagues/{}.html".format(
            ID
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


    def getAllTeamURLs(self):
        links = self.soup.find_all("a")
        url_tags = []

        # Pull the url tail for each team page
        for link in links:
            link = str(link)
            if "//www.tfrrs.org/teams/" in link:
                link = link[34: link.index(".html")]
                url_tags.append(link)
        return url_tags


    def getMensTeams(self):
        teams = {}

        for tag in self.AllTeamURLs:
            if '_m_' == tag[10:13]:
                name = tag[13:].replace('_', ' ')
                state = tag[:2]
                teams[name] = state

        return teams


    def getWomensTeams(self):
        teams = {}

        for tag in self.AllTeamURLs:
            if '_f_' == tag[10:13]:
                name = tag[13:].replace('_', ' ')
                state = tag[:2]
                teams[name] = state

        return teams


    def initialize(self):
        self.dfs = pd.read_html(self.HTML)
        self.soup = BeautifulSoup(self.HTML, "html5lib")
        self.AllTeamURLs = self.getAllTeamURLs()
        self.MensTeams = self.getMensTeams()
        self.WomensTeams = self.getWomensTeams()

        return None


def d2_conference_IDs():
    return {
        1383 : 'Conference Carolinas',
        1384 : 'GLIAC',
        1385 : 'GLVC',
        1386 : 'GNAC',
        1387 : 'MIAA',
        1388 : 'Northeast-10',
        1389 : 'Northern Sun',
        1390 : 'Rocky Mountain AC',
        1391 : 'WVIAC',     # No teams on page
        1392 : 'Lone Star',
        # 1393 : 'SIAC', # Unsure
        1394 : 'CCAA'
    }
