import pandas as pd
import requests
import re
import numpy as np
from bs4 import BeautifulSoup


def season(start, end, meet_name):
    def month2Num(m):
        if m.isnumeric():   return m
        numToMonth = {
            "Jan" : 1,
            "Feb" : 2,
            "Mar" : 3,
            "Apr" : 4,
            "May": 5,
            "Jun" : 6,
            "Jul" : 7,
            "Aug" : 8,
            "Sep" : 9,
            "Oct" : 10,
            "Nov" : 11,
            "Dec" : 12,
        }
        return numToMonth[m]
    # data format: "mon dy, year"
    assert len(start.split(' ')) == 3
    assert len(end.split(' ')) == 3
    sm, sd, sy = [int(month2Num(s)) for s in start.replace(',', '').split(' ')]
    em, ed, ey = [int(month2Num(e)) for e in end.replace(',', '').split(' ')]
    for season in ['Indoor', 'Outdoor', 'Cross Country']:
        if season in meet_name: return sy, season
    if (sm == 12 and 'Cross Country' not in meet_name):  return sy+1, 'Indoor'
    elif (sm >= 8 and em <= 12):  return sy, 'Cross Country'
    elif (sm >= 1 and em < 3) or (sm == 3 and ed <= 15):  return sy, 'Indoor'
    elif (sm == 3 and ed > 15) or (sm > 3 and em <= 5): return sy, 'Outdoor'
    else:   return sy, 'Out of Season'


def parseEventMark(mark):
    # try to make pandas use float to avoid importing all of numpy
    if isinstance(mark, np.float64) or isinstance(mark, float):
        return float(mark)

    if isinstance(mark, np.int64) or isinstance(mark, int):
        return int(mark)

    # Some results are just the float
    if mark.isalpha():
        return mark

    # Possible edge case - false start with wind
    if "FS" in mark:
        return "FS"

    # possibly irrelevant
    elif mark.replace(".", "").isnumeric():
        return float(mark)

    else:
        # Don't want feet conversion or wind right now
        endChars = ["m", "W", "w", "(", "W"]
        for char in endChars:
            if char in mark:
                try:
                    return float(mark[0 : mark.index(char)])
                except:
                    return mark[0 : mark.index(char)]

    # Unaccounted for
    return mark


def grade_index(ls):
    for i, e in enumerate(ls):
        if 'FR-' in e or 'SO-' in e or 'JR-' in e or 'SR-' in e or 'REDSHIRT/' in e:
            return i
    return -1


def parseEventName(name):
    cleaned = str(name).replace("  ", " ") if name != "10000" else "10,000"
    return cleaned.replace(".0", "")


class Athlete:
    def __init__(self, ID, school="", name=""):
        self.athlete_id = ID
        # Make the URL
        url = "https://www.tfrrs.org/athletes/" + ID + "/"
        if school:
            url += school + "/"
        if name:
            url += name.replace(" ", "_")

        # Get the response
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.102 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        # Create the attributes and leave them blank
        self.data = None
        self.soup = None
        self.dfs = None

        # Handle the response
        if response.status_code < 300 and response.status_code >= 200:
            # panda's read_html doesn't accept percent colspan arguments
            self.HTML = response.text.replace('colspan="100%"', 'colspan="3"')
        else:
            self.HTML = None
            raise Exception("Could not retrieve", response.status_code)

    def getAthleteInfo(self):
        if not self.soup:
            self.soup = BeautifulSoup(self.HTML, "html5lib")

        # Use beautifulsoup to find the proper section and extract the text
        athleteInfo = (
            self.soup.find("div", class_="panel-heading")
            .get_text()
            .replace("\n", "")
            .strip()
        )
        athleteInfo = " ".join(athleteInfo.split())
        athleteInfo = athleteInfo.replace("RED SHIRT", "REDSHIRT")

        # Format the text into a usable list
        athleteInfo = athleteInfo.split()
        grd = grade_index(athleteInfo)
        if grd != -1:
            grade, year = (
                athleteInfo[grd].split("/")
                if "REDSHIRT" in athleteInfo[grd]
                else athleteInfo[grd].split("-")
            )
            team = ' '.join([e for e in athleteInfo[grd+1:]])
            name = ' '.join([e for e in athleteInfo[:grd]])
            athleteInfo[0] = name
        else:
            grade, year = (
                ' Unknown',
                '0'
            )
            if len(athleteInfo) == 3:
                team = athleteInfo[-1]
            else:
                team = ' '.join([e for e in athleteInfo[2:]])
            athleteInfo[0] = athleteInfo[0] + " " + athleteInfo[1]
        athleteInfo[1] = grade[1:]
        athleteInfo[2] = year[:-1]

        gender = 'n'
        links = Test.soup.find_all("a")
        # Pull the meet ID from href URLs
        for link in links:
            if re.search('href="//www.tfrrs.org/teams/', str(link)):
                gender = str(link)[42]

        # Put it into data
        return {
            "Name": athleteInfo[0],
            "Grade": athleteInfo[1],
            "Year": int(athleteInfo[2])
            if athleteInfo[2].isnumeric()
            else athleteInfo[2],
            "School": team,
            "Gender": gender
        }


    def getPersonalRecords(self):
        # If not created already get the dataframes
        if not self.dfs:
            self.dfs = pd.read_html(self.HTML)
        # Check for no personal records
        if len(self.dfs) == 0:
            return {"Has not competed": None}
        df = self.dfs[0]

        # Create the np array to fill in
        numLeft = sum(pd.notnull(df.iloc[:, 0]))
        numRight = sum(pd.notnull(df.iloc[:, 2]))
        numEvents = numLeft + numRight
        PRs = np.empty([numEvents, 2], dtype=object)

        # Fill in the array
        for i in range(df.shape[0]):
            PRs[i, 0] = df.iloc[i, 0]
            PRs[i, 1] = df.iloc[i, 1]

            if pd.notnull(df.iloc[i, 2]):
                PRs[i + numLeft, 0] = df.iloc[i, 2]
                PRs[i + numLeft, 1] = df.iloc[i, 3]

        # Convert to dataframe
        PRs = pd.DataFrame(PRs)
        PRs.columns = ["Event", "Mark"]

        # Clean up the dataframe
        PRs["Mark"] = PRs["Mark"].apply(lambda mark: parseEventMark(mark))
        for i in range(len(PRs)):
            if PRs["Event"][i] in ("HEP", "PENT", "DEC"):  # make this neater
                PRs["Mark"][i] = int(PRs["Mark"][i])
        PRs.set_index("Event", inplace=True)
        PRs.index = [parseEventName(event) for event in PRs.index]

        # Put it into data
        #   ["Mark"] used since column name persists
        return PRs.to_dict()["Mark"]

    def getAll(self):
        if self.HTML:
            # Setup
            data = self.getAthleteInfo()

            # Get athlete info
            data["Personal Records"] = self.getPersonalRecords()

            # Meet results
            data["Meet Results"] = self.getMeets()

            # Return
            return data

        else:
            raise Exception("No HTML loaded. Retry with a different ID")

    # TODO: Get XC ids and make sure everything is right
    def getMeetIds(self):
        if not self.soup:
            self.soup = BeautifulSoup(self.HTML, "html5lib")
        links = self.soup.find_all("a")
        IDs = set()

        # Pull the meet ID from href URLs
        for link in links:
            if re.search('href="//www.tfrrs.org/results/', str(link)):
                link = str(link)
                if '/xc/' in link:
                    id = link[link.find('/results/') + 12:link.find('/results/') + 17]
                else:
                    id = link[link.find('/results/') + 9:link.find('/results/') + 14]
                IDs.add(id)
        IDs = [a for a in IDs]

        return IDs

    def getOneMeet(self, df, ID):
        # Get meet name and date
        dateStart = re.search(self.dateRegex, df.columns[0]).start()
        Meet = df.columns[0][:dateStart].rstrip()
        Date = df.columns[0][dateStart:]
        startDate, endDate = self.parseDates(Date)

        # JSON the meet info
        meetInfo = {}
        meetInfo["Meet Name"] = Meet
        meetInfo["Start Date"] = startDate
        meetInfo["End Date"] = endDate
        season_year, season_type = season(startDate, endDate, Meet)
        meetInfo['Year'] = season_year
        meetInfo['Season'] = season_type

        # Add a column and rename columns
        df = pd.concat(
            [df, pd.DataFrame(np.empty([df.shape[0], 1], dtype=object))], axis=1
        )
        df.columns = ["Event", "Mark", "Place", "Round"]

        # Fix up the dataframe
        df["Mark"] = df["Mark"].apply(lambda mark: parseEventMark(mark))
        df["Place"] = df["Place"].fillna("N/A")

        # TODO // Clean this up if possible
        df["Round"] = [
            "F" if "(F)" in row else ("P" if "(P)" in row else "N/A")
            for row in df["Place"]
        ]

        def onlyNumber(place):
            # Remove last four digits (the round details) and take only digits
            number = ""
            if not (place[-3] == '(' and place[-1] == ')'):
                place += ' (R)'
            for char in place[0:-4]:
                if not char.isalpha():
                    number += char
                else:
                    return int(number)

        df["Place"] = [row if row == "N/A" else onlyNumber(row) for row in df["Place"]]

        df.set_index("Event", inplace=True)
        df.index = [str(event) for event in df.index]

        # JSON to meet results
        meetInfo["Results"] = {}
        for i in range(0, df.shape[0]):
            meetInfo["Results"][df.index[i]] = df.iloc[i, :].to_list()

        # add into data
        return meetInfo

    def getMeets(self):
        if not self.dfs:
            self.dfs = pd.read_html(self.HTML)
        if len(self.dfs) == 0:
            return {}
        dfs = self.dfs[1:]

        # Since more than meet results are read in, use regex to determine when they stop
        self.dateRegex = "[A-Z][a-z]{2} \d{1,2}(-\d{1,2}){0,1},"
        firstNonResult = [
            True if (re.search(self.dateRegex, df.columns[0])) else False
            for df in dfs
        ].index(False)

        # Get the meet IDs ahead of time and pass that to the JSON creating function
        IDs = self.getMeetIds()

        # Loop getting the meets
        meetData = {}
        for df, ID in zip(dfs[:firstNonResult], IDs):
            meetData[ID] = self.getOneMeet(df, ID)

        return meetData

    def timesCompetedPerEvent(self):
        meetData = self.getMeets()
        if not meetData:
            return {}

        timesCompeted = {}
        for meet in meetData.values():
            # data seems to only get one if prelims and finals are ran same day
            for event in np.unique(list(meet["Results"].keys())):
                timesCompeted[event] = (
                    1 if event not in timesCompeted else timesCompeted[event] + 1
                )

        return timesCompeted

    def parseDates(self, Date):
        if "/" in Date:

            def chunkToFormat(chunk):
                month, day = chunk.split("/")
                numToMonth = {
                    "01": "Jan",
                    "02": "Feb",
                    "03": "Mar",
                    "04": "Apr",
                    "05": "May",
                    "06": "Jun",
                    "07": "Jul",
                    "08": "Aug",
                    "09": "Sep",
                    "10": "Oct",
                    "11": "Nov",
                    "12": "Dec",
                }
                month = numToMonth[month]
                return month + " " + day

            dashIndex = Date.index("-")
            year = Date[-4:]
            chunk = Date[: dashIndex - 1]
            return chunkToFormat(chunk) + ", " + year, Date[dashIndex + 2 :]

        elif "-" in Date:
            Month = Date[: Date.index(" ")]
            Year = Date[-4:]
            Days = Date.split(" ")[1].replace(",", "").split("-")
            return (
                Month + " " + Days[0] + ", " + Year,
                Month + " " + Days[1] + ", " + Year,
            )

        else:
            return Date, Date


if __name__ == "__main__":
    Test = Athlete("6603636", "Colorado Mines", "Luke Julian")
    print(Test.getAthleteInfo())

