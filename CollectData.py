import AthleteTfrrs as ath
import TeamTfrrs as tms
import ConferenceTfrrs as con
import NatMeetTFRRS as nat
import numpy as np
import pandas as pd


def handleTmStr(tm):
    out = tm.replace('.', '')
    return out


def handleAthName(string):
    if ', ' in string:
        sep = string.split(', ')
        return ' '.join(sep)


def write_athlete_results(dic1, dic2, gender):
    header = [
        'Name',
        'Grade',
        'Year',
        'School',
        'Conference',
        'Meet_ID',
        'Meet_Name',
        'Meet_Start',
        'Meet_End',
        'Event',
        'Mark',
        'Place',
        'Prelim/Final'
    ]
    table_list = []
    subdic = dic1[gender]
    for conference, team in subdic.items():
        for teamName, athletes in team.items():
            for athlete in athletes:
                athlete_info = athlete.getAthleteInfo()
                for meet_id, meet_info in athlete.getMeets().items():
                    for event, data in meet_info['Results'].items():
                        row = [
                            athlete_info['Name'],
                            athlete_info['Grade'],
                            athlete_info['Year'],
                            athlete_info['School'],
                            conference,
                            meet_id,
                            meet_info['Meet Name'],
                            meet_info['Start Date'],
                            meet_info['End Date'],
                            event,
                            data[0],
                            data[1],
                            data[2]
                        ]
                        table_list.append(row)
    ls = dic2[gender]
    for athlete in ls:
        athlete_info = athlete.getAthleteInfo()
        for meet_id, meet_info in athlete.getMeets().items():
            for event, data in meet_info['Results'].items():
                row = [
                    athlete_info['Name'],
                    athlete_info['Grade'],
                    athlete_info['Year'],
                    athlete_info['School'],
                    conference,
                    meet_id,
                    meet_info['Meet Name'],
                    meet_info['Start Date'],
                    meet_info['End Date'],
                    event,
                    data[0],
                    data[1],
                    data[2]
                ]
                table_list.append(row)
    pd.DataFrame(
        data=table_list,
        columns=header
    ).to_csv(
        f'{gender}_athlete_results.csv',
        index=False
    )


def write_team_top_marks(dic, gender):
    header = [
        'Team',
        'Conference',
        'Event',
        'Athlete',
        'Athlete_ID',
        'Year',
        'Mark'
    ]
    table_list = []
    subdic1 = dic[gender]
    for conf, teams in subdic1.items():
        for teamName, team in teams.items():
            tp = team.getTopMarks(True)
            for i in range(len(tp['EVENT'])):
                row = [
                    teamName,
                    conf,
                    tp['EVENT'][i],
                    tp['ATHLETE/SQUAD'][i],
                    tp['Athlete ID'][i],
                    tp['YEAR'][i],
                    tp['TIME/MARK'][i]
                ]
                table_list.append(row)
    pd.DataFrame(
        data=table_list,
        columns=header
    ).to_csv(
        f'{gender}_top_marks.csv',
        index=False
    )


def athletes_from_conf():
    conferences = {}
    for conf_id, conf_name in con.d2_conference_IDs().items():
        conferences[conf_name] = con.Conference(conf_id)
    ret_tms = {'M' : {}, 'F' : {}}
    ret_ath = {'M' : {}, 'F' : {}}
    for gender in ['M', 'F']:
        print(gender)
        for conf, conf_obj in conferences.items():
            print(conf, end=': ')
            ret_tms[gender][conf] = {}
            ret_ath[gender][conf] = {}
            teams = conf_obj.MensTeams if gender == 'M' else conf_obj.WomensTeams
            for tm, st in teams.items():
                print(tm, end=', ')
                tm_url_name = handleTmStr(tm)
                try:
                    curr_team = tms.Team(
                        st, gender, tm_url_name.replace(' ', '_')
                    )
                except Exception as e:
                    print('\n', e)
                    print(tm, gender, end='\n\t\t\t')
                    continue
                ath_IDs = curr_team.AthleteIDs
                ret_tms[gender][conf][tm] = curr_team
                ret_ath[gender][conf][tm] = []
                for name, id in ath_IDs.items():
                    existing_athletes.add(id)
                    formated_name = handleAthName(name)
                    try:
                        athlete = ath.Athlete(
                            id,
                            tm_url_name,
                            formated_name
                        )
                    except Exception as e:
                        print(e)
                        print(name, end='\n\t\t\t')
                        continue
                    ret_ath[gender][conf][tm].append(athlete)
            print()
        print(f'{gender} Athlete Results Loaded')
    return ret_ath


def athletes_from_meet():
    nat_athletes = []
    print('Meets')
    for meetname, years in nat.nat_meet_ids().items():
        for year, id in years.items():
            print(year, end=', ')
            meet = nat.Meet(id, meetname)
            nat_athletes.append(meet)
    all_athletes = {
        'M' : [],
        'F' : []
    }
    print('\nAthletes')
    for i, nat_meet in enumerate(nat_athletes):
        print(f'{i}/{nat_athletes}', end=', ')
        for g, athletes in nat_meet.AthleteInfo.items():
            gender = g.upper()
            for athlete in athletes:
                name, id, tm = athlete
                formated_name = handleAthName(name)
                tm_url_name = handleTmStr(tm)
                if not set([id]).issubet(existing_athletes):
                    existing_athletes.add(id)
                    athlete = ath.Athlete(
                        id, tm_url_name, formated_name
                    )
                    all_athletes[gender].append(athlete)
    return all_athletes


def main():
    global existing_athletes
    existing_athletes = set()
    ath_conf = athletes_from_conf()
    ath_meet = athletes_from_meet()
    write_athlete_results(ath_conf, ath_meet, 'M')


if __name__ == '__main__':
    main()
