import praw
import settings
import os
import calendar
import pprint
from datetime import datetime


reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)


traffic = subreddit.traffic()

weekly_data = {}
week_num = 0
for day in traffic['day']:
    day_dt = datetime.utcfromtimestamp(day[0])
    day_uniques = day[1]
    day_views = day[2]
    day_subs = day[3]

    if day_dt.weekday() == 6:
        week_num += 1
    if week_num == 2:
        break
    if week_num not in weekly_data:
        weekly_data[week_num] = {
            'uniques': 0,
            'views': 0,
            'subs': 0,
            'days': {
                0: {},
                1: {},
                2: {},
                3: {},
                4: {},
                5: {},
                6: {}
            },
            'actions': {
                'total': 0,
                'removals': 0,
                'bans': 0,
                'unbans': 0,
                'other': 0
            }
        }

    weekly_data[week_num]['uniques'] += day_uniques
    weekly_data[week_num]['views'] += day_views
    weekly_data[week_num]['subs'] += day_subs
    weekly_data[week_num]['days'][day_dt.weekday()] = {
        'uniques': day_uniques,
        'views': day_views,
        'subs': day_subs,
        'date': day_dt,
        'actions': {
            'total': 0,
            'removals': 0,
            'bans': 0,
            'unbans': 0,
            'other': 0
        }
    }

done = False
last = None
end_utc_ts = calendar.timegm(weekly_data[1]['days'][0]['date'].timetuple())
start_utc_ts = calendar.timegm(weekly_data[0]['days'][0]['date'].timetuple())
count = 0
last_date = ''

for log_entry in subreddit.mod.log(limit=5000):
    count += 1
    log_dt = datetime.utcfromtimestamp(log_entry.created_utc)
    if log_entry.created_utc > start_utc_ts:
        continue
    if log_entry.created_utc > end_utc_ts:
        if log_entry.action == 'banuser':
            weekly_data[1]['days'][log_dt.weekday()]['actions']['bans'] += 1
            weekly_data[1]['actions']['bans'] += 1
        elif log_entry.action == 'unbanuser':
            weekly_data[1]['days'][log_dt.weekday()]['actions']['unbans'] += 1
            weekly_data[1]['actions']['unbans'] += 1
        elif log_entry.action == 'removelink':
            weekly_data[1]['days'][log_dt.weekday()]['actions']['removals'] += 1
            weekly_data[1]['actions']['removals'] += 1
        elif log_entry.action == 'removecomment':
            weekly_data[1]['days'][log_dt.weekday()]['actions']['removals'] += 1
            weekly_data[1]['actions']['removals'] += 1
        else:
            weekly_data[1]['days'][log_dt.weekday()]['actions']['other'] += 1
            weekly_data[1]['actions']['other'] += 1
        weekly_data[1]['days'][log_dt.weekday()]['actions']['total'] += 1
        weekly_data[1]['actions']['total'] += 1
    else:
        break

print(str(count)+' Log Entries Processed')

actions_table = '|  Day  |  Bans  |  Unbans  |  Removals  |  Other  |  **Total**  |\n'
actions_table = actions_table + '|---|---|---|---|---|---|\n'
traffic_table = '|  Day  | Uniques  |  Views  |  Subs  |\n'
traffic_table = traffic_table + '|---|---|---|---|\n'
total_uniques = 0
total_views = 0
total_subs = 0
for day, info in weekly_data[1]['days'].items():
    if day == 0:
        actions_table = actions_table + '|  Monday  |  '
        traffic_table = traffic_table + '|  Monday  |  '
    elif day == 1:
        actions_table = actions_table + '|  Tuesday  |  '
        traffic_table = traffic_table + '|  Tuesday  |  '
    elif day == 2:
        actions_table = actions_table + '|  Wednesday  |  '
        traffic_table = traffic_table + '|  Wednesday  |  '
    elif day == 3:
        actions_table = actions_table + '|  Thursday  |  '
        traffic_table = traffic_table + '|  Thursday  |  '
    elif day == 4:
        actions_table = actions_table + '|  Friday  |  '
        traffic_table = traffic_table + '|  Friday  |  '
    elif day == 5:
        actions_table = actions_table + '|  Saturday  |  '
        traffic_table = traffic_table + '|  Saturday  |  '
    elif day == 6:
        actions_table = actions_table + '|  Sunday  |  '
        traffic_table = traffic_table + '|  Sunday  |  '

    actions_table = actions_table + str(info['actions']['bans']) + '  |  '
    actions_table = actions_table + str(info['actions']['unbans']) + '  |  '
    actions_table = actions_table + str(info['actions']['removals']) + '  |  '
    actions_table = actions_table + str(info['actions']['other']) + '  |  '
    actions_table = actions_table + str(info['actions']['total']) + '  |\n'

    traffic_table = traffic_table + str(info['uniques']) + '  |  '
    traffic_table = traffic_table + str(info['views']) + '  |  '
    traffic_table = traffic_table + str(info['subs']) + '  |\n'

    if day == 6:
        actions_table = actions_table + '|  **Totals**  |  '+str(weekly_data[1]['actions']['bans'])+'  |  '+str(weekly_data[1]['actions']['unbans'])+'  |  '+str(weekly_data[1]['actions']['removals'])+'  |  '+str(weekly_data[1]['actions']['other'])+'  |  '+str(weekly_data[1]['actions']['total'])+'  |\n'
        traffic_table = traffic_table + '|  **Totals**  |  '+str(weekly_data[1]['uniques'])+'  |  '+str(weekly_data[1]['views'])+'  |  '+str(weekly_data[1]['subs'])+'  |\n'

date_range = weekly_data[1]['days'][0]['date'].strftime('%b %d')+' - '+weekly_data[1]['days'][6]['date'].strftime('%b %d')

log_report = open("PostTemplates/modLogReport.txt").read()
log_report = log_report.replace('{{mod_activity}}', actions_table)
log_report = log_report.replace('{{traffic_report}}', traffic_table)
log_report = log_report.replace('{{date_range}}', date_range)

report_submission = subreddit.submit(
    title='Weekly Mod Transparency Report: '+date_range,
    selftext=log_report,
    flair_id=settings.SUBREDDIT_META_FLAIR_ID,
    flair_text='Transparency',
    send_replies=False
)

report_submission.mod.approve()
report_submission.mod.distinguish()
report_submission.mod.sticky(state=True, bottom=True)
report_submission.mod.ignore_reports()
