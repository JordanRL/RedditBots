# This script is copyright 2018 Jordan LeDoux and may not be used or distributed without permission

import praw
import settings
import calendar
import SlackWebHook
import sys
from datetime import datetime


reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)
HookBot = SlackWebHook.WebHook(settings=settings)

if len(sys.argv) > 0:
    runCommand = sys.argv[1]
else:
    runCommand = None

if runCommand is not None and runCommand == 'dryrun':
    status_text = 'ActualBernieBot is about to compile the weekly transparency report in *dryrun* mode'
else:
    status_text = 'ActualBernieBot is about to compile the weekly transparency report and post it to the subreddit'

HookBot.post_status(
    'ActualBernieBot Status Message',
    status_text,
    settings.SLACK_STATUS_CHANNEL
)


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
                'approvals': 0,
                'flair': 0,
                'sticky': 0,
                'other': 0
            },
            'activity': {
                'top_post': None,
                'top_comment': None,
                'most_discussed': None,
                'total_posts': 0,
                'total_comments': 0
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
            'approvals': 0,
            'flair': 0,
            'sticky': 0,
            'other': 0
        },
        'activity': {
            'top_post': None,
            'top_comment': None,
            'most_discussed': None,
            'total_posts': 0,
            'total_comments': 0
        }
    }

end_utc_ts = calendar.timegm(weekly_data[1]['days'][0]['date'].timetuple())
start_utc_ts = calendar.timegm(weekly_data[0]['days'][0]['date'].timetuple())
count = 0

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
        elif log_entry.action == 'approvelink' or log_entry.action == 'approvecomment':
            weekly_data[1]['days'][log_dt.weekday()]['actions']['approvals'] += 1
            weekly_data[1]['actions']['approvals'] += 1
        elif log_entry.action == 'editflair':
            weekly_data[1]['days'][log_dt.weekday()]['actions']['flair'] += 1
            weekly_data[1]['actions']['flair'] += 1
        elif log_entry.action == 'sticky' or log_entry.action == 'unsticky':
            weekly_data[1]['days'][log_dt.weekday()]['actions']['sticky'] += 1
            weekly_data[1]['actions']['sticky'] += 1
        else:
            weekly_data[1]['days'][log_dt.weekday()]['actions']['other'] += 1
            weekly_data[1]['actions']['other'] += 1
        weekly_data[1]['days'][log_dt.weekday()]['actions']['total'] += 1
        weekly_data[1]['actions']['total'] += 1
    else:
        break

print(str(count)+' Log Entries Processed')
sub_count = 0
com_count = 0

for submission in subreddit.new(limit=1000):
    sub_count += 1
    sub_dt = datetime.utcfromtimestamp(submission.created_utc)
    if submission.created_utc > start_utc_ts:
        continue
    if submission.created_utc > end_utc_ts:
        weekly_data[1]['activity']['total_posts'] += 1
        weekly_data[1]['days'][sub_dt.weekday()]['activity']['total_posts'] += 1
        if weekly_data[1]['activity']['top_post'] is None:
            weekly_data[1]['activity']['top_post'] = submission
        elif weekly_data[1]['activity']['top_post'].score < submission.score:
            weekly_data[1]['activity']['top_post'] = submission
        if weekly_data[1]['days'][sub_dt.weekday()]['activity']['top_post'] is None:
            weekly_data[1]['days'][sub_dt.weekday()]['activity']['top_post'] = submission
        elif weekly_data[1]['days'][sub_dt.weekday()]['activity']['top_post'].score < submission.score:
            weekly_data[1]['days'][sub_dt.weekday()]['activity']['top_post'] = submission
        if weekly_data[1]['activity']['most_discussed'] is None:
            weekly_data[1]['activity']['most_discussed'] = submission
        elif weekly_data[1]['activity']['most_discussed'].score < submission.num_comments:
            weekly_data[1]['activity']['most_discussed'] = submission
        if weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'] is None:
            weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'] = submission
        elif weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'].score < submission.num_comments:
            weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'] = submission
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            com_count += 1
            com_dt = datetime.utcfromtimestamp(comment.created_utc)
            if comment.created_utc > start_utc_ts:
                continue
            if comment.created_utc > end_utc_ts:
                if weekly_data[1]['activity']['top_comment'] is None:
                    weekly_data[1]['activity']['top_comment'] = comment
                elif weekly_data[1]['activity']['top_comment'].score < comment.score:
                    weekly_data[1]['activity']['top_comment'] = comment
                if weekly_data[1]['days'][com_dt.weekday()]['activity']['top_comment'] is None:
                    weekly_data[1]['days'][com_dt.weekday()]['activity']['top_comment'] = comment
                elif weekly_data[1]['days'][com_dt.weekday()]['activity']['top_comment'].score < comment.score:
                    weekly_data[1]['days'][com_dt.weekday()]['activity']['top_comment'] = comment
                weekly_data[1]['activity']['total_comments'] += 1
                weekly_data[1]['days'][com_dt.weekday()]['activity']['total_comments'] += 1
            else:
                continue
    else:
        break

print(str(sub_count)+' Submissions Processed')
print(str(com_count)+' Comments Processed')

actions_table = '|  Day  |  Bans  |  Unbans  |  Removals  |  Approvals  |  Flair  |  Sticky  |  Other  |  **Total**  |\n'
actions_table = actions_table + '|---|---|---|---|---|---|---|---|---|\n'
traffic_table = '|  Day  | Uniques  |  Views  |  Subs  |\n'
traffic_table = traffic_table + '|---|---|---|---|\n'
activity_table = '|  Day  | # Posts  |  # Comments  |  Top Post | Top Comment | Most Discussed |\n'
activity_table = activity_table + '|---|---|---|---|---|---|\n'
total_uniques = 0
total_views = 0
total_subs = 0
for day, info in weekly_data[1]['days'].items():
    if day == 0:
        actions_table = actions_table + '|  Monday  |  '
        traffic_table = traffic_table + '|  Monday  |  '
        activity_table = activity_table + '|  Monday  |  '
    elif day == 1:
        actions_table = actions_table + '|  Tuesday  |  '
        traffic_table = traffic_table + '|  Tuesday  |  '
        activity_table = activity_table + '|  Tuesday  |  '
    elif day == 2:
        actions_table = actions_table + '|  Wednesday  |  '
        traffic_table = traffic_table + '|  Wednesday  |  '
        activity_table = activity_table + '|  Wednesday  |  '
    elif day == 3:
        actions_table = actions_table + '|  Thursday  |  '
        traffic_table = traffic_table + '|  Thursday  |  '
        activity_table = activity_table + '|  Thursday  |  '
    elif day == 4:
        actions_table = actions_table + '|  Friday  |  '
        traffic_table = traffic_table + '|  Friday  |  '
        activity_table = activity_table + '|  Friday  |  '
    elif day == 5:
        actions_table = actions_table + '|  Saturday  |  '
        traffic_table = traffic_table + '|  Saturday  |  '
        activity_table = activity_table + '|  Saturday  |  '
    elif day == 6:
        actions_table = actions_table + '|  Sunday  |  '
        traffic_table = traffic_table + '|  Sunday  |  '
        activity_table = activity_table + '|  Sunday  |  '

    actions_table = actions_table + str(info['actions']['bans']) + '  |  '
    actions_table = actions_table + str(info['actions']['unbans']) + '  |  '
    actions_table = actions_table + str(info['actions']['removals']) + '  |  '
    actions_table = actions_table + str(info['actions']['approvals']) + '  |  '
    actions_table = actions_table + str(info['actions']['flair']) + '  |  '
    actions_table = actions_table + str(info['actions']['sticky']) + '  |  '
    actions_table = actions_table + str(info['actions']['other']) + '  |  '
    actions_table = actions_table + str(info['actions']['total']) + '  |\n'

    traffic_table = traffic_table + str(info['uniques']) + '  |  '
    traffic_table = traffic_table + str(info['views']) + '  |  '
    traffic_table = traffic_table + str(info['subs']) + '  |\n'

    activity_table = activity_table + str(info['activity']['total_posts']) + ' | '
    activity_table = activity_table + str(info['activity']['total_comments']) + ' | '
    activity_table = activity_table + ' [Post](https://www.reddit.com'+info['activity']['top_post'].permalink+') Score: '+str(info['activity']['top_post'].score)+' | '
    activity_table = activity_table + ' [Comment](https://www.reddit.com'+info['activity']['top_comment'].permalink+') Score: '+str(info['activity']['top_comment'].score)+' | '
    activity_table = activity_table + ' [Most Discussed](https://www.reddit.com'+info['activity']['most_discussed'].permalink+') Comments: '+str(info['activity']['most_discussed'].num_comments)+' |\n'

    if day == 6:
        actions_table = actions_table + '|  **Totals**  |  '+str(weekly_data[1]['actions']['bans'])+'  |  '+str(weekly_data[1]['actions']['unbans'])+'  |  '+str(weekly_data[1]['actions']['removals'])+'  |  '+str(weekly_data[1]['actions']['approvals'])+'  |  '+str(weekly_data[1]['actions']['flair'])+'  |  '+str(weekly_data[1]['actions']['sticky'])+'  |  '+str(weekly_data[1]['actions']['other'])+'  |  '+str(weekly_data[1]['actions']['total'])+'  |\n'
        traffic_table = traffic_table + '|  **Totals**  |  '+str(weekly_data[1]['uniques'])+'  |  '+str(weekly_data[1]['views'])+'  |  '+str(weekly_data[1]['subs'])+'  |\n'
        activity_table = activity_table + '| **Totals** | '
        activity_table = activity_table + str(weekly_data[1]['activity']['total_posts']) + ' | '
        activity_table = activity_table + str(weekly_data[1]['activity']['total_comments']) + ' | '
        activity_table = activity_table + ' [Post](https://www.reddit.com' + weekly_data[1]['activity']['top_post'].permalink + ') Score: ' + str(weekly_data[1]['activity']['top_post'].score) + ' | '
        activity_table = activity_table + ' [Comment](https://www.reddit.com' + weekly_data[1]['activity']['top_comment'].permalink + ') Score: ' + str(weekly_data[1]['activity']['top_comment'].score) + ' | '
        activity_table = activity_table + ' [Most Discussed](https://www.reddit.com' + weekly_data[1]['activity']['most_discussed'].permalink + ') Comments: ' + str(weekly_data[1]['activity']['most_discussed'].num_comments) + ' |\n'

date_range = weekly_data[1]['days'][0]['date'].strftime('%b %d')+' - '+weekly_data[1]['days'][6]['date'].strftime('%b %d')

log_report = open("PostTemplates/modLogReport.txt").read()
log_report = log_report.replace('{{mod_activity}}', actions_table)
log_report = log_report.replace('{{traffic_report}}', traffic_table)
log_report = log_report.replace('{{activity_report}}', activity_table)
log_report = log_report.replace('{{date_range}}', date_range)

if runCommand is not None and runCommand == 'dryrun':
    print(log_report)
    HookBot.post_status(
        'ActualBernieBot Status Message',
        'ActualBernieBot compiled the transparency report in *dryrun* mode, so it was note posted to the subreddit',
        settings.SLACK_STATUS_CHANNEL
    )
else:
    report_submission = subreddit.submit(title='Weekly Mod Transparency Report: '+date_range, selftext=log_report)

    report_submission.disable_inbox_replies()
    report_submission.flair.select(settings.SUBREDDIT_META_FLAIR_ID, 'Transparency')
    report_submission.mod.approve()
    report_submission.mod.distinguish()
    report_submission.mod.sticky(state=True, bottom=True)
    report_submission.mod.ignore_reports()

    HookBot.post_submission_link(
        username=report_submission.author.name, title=report_submission.title,
        permalink=report_submission.permalink, pretext='The transparency report has been compiled and posted',
        color='good', channel=settings.SLACK_STATUS_CHANNEL
    )
