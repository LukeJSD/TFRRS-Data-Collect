import AthleteTfrrs as ath
import TeamTfrrs as tms
import ConferenceTfrrs as con
import NatMeetTFRRS as nat
import pandas as pd
import time
import numpy as np

team_2_conf = {
        'M' : {},
        'F' : {}
    }
existing_athletes = set()


def prog_bar(percent, string, time=None, start=False):
    prog = int((percent / 0.05) + 0.01)
    if len(string) == prog:
        if start:
            print(f'| -------------------- | {percent:.2f} - {time:.4f}')
        return string
    while len(string) < prog:
        string += '#'
    remain = ''
    for left in range(20-prog):
        remain += '-'
    print('|', string + remain, f'| {percent:.2f} - {time:.4f}')
    return string


def handleTmStr(tm):
    out = tm.replace('.', '')
    out = out.replace('(', '')
    out = out.replace(')', '')
    return out


def handleAthName(string):
    if ', ' in string:
        sep = string.split(', ')
        return ' '.join(sep)
    else:
        return string


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
    subdic1 = dic1[gender]
    print('write from conferences')
    cf = 0
    for conference, team in subdic1.items():
        cf += 1
        print(conference, f'{cf}/{len(subdic1)}')
        for teamName, athletes in team.items():
            s = len(athletes)
            times = []
            t0 = time.time()
            string = ''
            for j, athlete in enumerate(athletes):
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
                t1 = time.time()
                times.append(t1 - t0)
                string = prog_bar(j / s, string, time=np.mean(np.array([times])), start=(j == 0))
                t0 = t1
    conferences = team_2_conf[gender]
    ls = dic2[gender]
    print('write from meets')
    s = len(ls)
    times = []
    t0 = time.time()
    string = ''
    for j, athlete in enumerate(ls):
        athlete_info = athlete.getAthleteInfo()
        for meet_id, meet_info in athlete.getMeets().items():
            for event, data in meet_info['Results'].items():
                try:
                    form_school = handleTmStr(athlete_info['School'])
                    conference = conferences[form_school]
                except:
                    conference = None
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
        t1 = time.time()
        times.append(t1 - t0)
        string = prog_bar(j / s, string, time=np.mean(np.array([times])), start=(j == 0))
        t0 = t1
    print('Write file')
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
        conf_obj = con.Conference(conf_id)
        conferences[conf_name] = conf_obj
        for mtm in conf_obj.MensTeams:
            team_2_conf['M'][mtm] = conf_name
        for ftm in conf_obj.WomensTeams:
            team_2_conf['F'][ftm] = conf_name
    print(team_2_conf)
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
        print(f'{i+1}/{len(nat_athletes)}')
        for g, athletes in nat_meet.AthleteInfo.items():
            gender = g.upper()
            unique_athletes = set(athletes) - existing_athletes
            s = len(unique_athletes)
            times = []
            t0 = time.time()
            string = ''
            for j, id in enumerate(unique_athletes):
                athlete = athletes[id]
                name, id, tm = athlete
                formated_name = handleAthName(name)
                tm_url_name = handleTmStr(tm)
                existing_athletes.add(id)
                athlete = ath.Athlete(
                    id, tm_url_name, formated_name
                )
                all_athletes[gender].append(athlete)
                existing_athletes.add(id)
                t1 = time.time()
                times.append(t1-t0)
                string = prog_bar(j/s, string, time=np.mean(np.array([times])), start=(j==0))
                t0 = t1
    return all_athletes


def main():
    t_start = time.time()
    ath_conf = athletes_from_conf()
    print(time.time()-t_start)
    ath_meet = athletes_from_meet()
    print(time.time()-t_start)
    write_athlete_results(ath_conf, ath_meet, 'M')
    write_athlete_results(ath_conf, ath_meet, 'F')
    print(time.time()-t_start)
    print('Done')


if __name__ == '__main__':
    main()
