import AthleteTfrrs as ath
import pandas as pd
import time
import csv

t_o = time.time()
with open('all_athlete_results.csv', 'w') as f:
    writer = csv.writer(f)
    header = [
            'Name',
            'Athlete ID',
            'Gender',
            'Grade',
            'Academic_Year',
            'School',
            'Conference',
            'Meet_ID',
            'Meet_Name',
            'Meet_Start',
            'Meet_End',
            'Year',
            'Season',
            'Event',
            'Mark',
            'Place',
            'Prelim/Final'
        ]
    writer.writerow(header)
    # table_list = []
    m = 1
    for i in range(3500000, 8000000):
        t = int(time.time()-t_o)
        if t%(60*m)==0 and t != 0:
            m += 1
            print(f'{i}: {t/60} minutes')
        try:
            athlete = ath.Athlete(f"{i}")
            athlete_info = athlete.getAthleteInfo()
        except:
            continue
        for meet_id, meet_info in athlete.getMeets().items():
            for event, data in meet_info['Results'].items():
                row = [
                    athlete_info['Name'],
                    athlete.athlete_id,
                    athlete_info['Gender'],
                    athlete_info['Grade'],
                    athlete_info['Year'],
                    athlete_info['School'],
                    'conference',
                    meet_id,
                    meet_info['Meet Name'],
                    meet_info['Start Date'],
                    meet_info['End Date'],
                    meet_info['Year'],
                    meet_info['Season'],
                    event,
                    data[0],
                    data[1],
                    data[2]
                ]
                writer.writerow(row)
                '''table_list.append(row)
    pd.DataFrame(
            data=table_list,
            columns=header
        ).to_csv(
            f'all_athlete_results.csv',
            index=False
        )'''
print((time.time()-t_o)/60)
