# This script is copyright 2018 Jordan LeDoux and may not be used or distributed without permission

import praw
import settings
import calendar
import SlackWebHook
import sys
from datetime import datetime
from datetime import timedelta
from datetime import timezone


reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)
HookBot = SlackWebHook.WebHook(settings=settings)

if len(sys.argv) > 1:
    runCommand = sys.argv[1]
    if len(sys.argv) > 2:
        otherSub = sys.argv[2]
    else:
        otherSub = None
else:
    runCommand = None
    otherSub = None

if runCommand is not None and runCommand == 'dryrun':
    status_text = 'ActualBernieBot is about to compile the weekly transparency report in *dryrun* mode'
elif runCommand is not None and runCommand == 'othersub' and otherSub is not None:
    status_text = 'ActualBernieBot is about to compile an activity report for a different subreddit: r/'+otherSub
    subreddit = reddit.subreddit(otherSub)
    print('Report for another sub selected, some data not collected')
else:
    status_text = 'ActualBernieBot is about to compile the weekly transparency report and post it to the subreddit'

HookBot.post_status(
    'ActualBernieBot Status Message',
    status_text,
    settings.SLACK_STATUS_CHANNEL
)

submitters = {}
commenters = {}

build_week = True
current_dt = datetime.utcnow()
process_dt = datetime(year=current_dt.year, month=current_dt.month, day=current_dt.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

weekly_data = {}
week_num = 0
day_step = timedelta(days=-1)
print('Building Week Object')
while build_week:
    if process_dt.weekday() == 6:
        week_num += 1
    if week_num == 2:
        build_week = False
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

    weekly_data[week_num]['days'][process_dt.weekday()] = {
        'uniques': 0,
        'views': 0,
        'subs': 0,
        'date': process_dt,
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

    process_dt = process_dt + day_step

print('Week Object Built')
end_utc_ts = calendar.timegm(weekly_data[1]['days'][0]['date'].timetuple())
start_utc_ts = calendar.timegm(weekly_data[0]['days'][0]['date'].timetuple())

week_num = 0
if runCommand is None or runCommand == 'dryrun':
    print('Processing Subreddit Traffic')
    traffic = subreddit.traffic()
    for day in traffic['day']:
        day_dt = datetime.utcfromtimestamp(day[0])
        day_uniques = day[1]
        day_views = day[2]
        day_subs = day[3]

        if day_dt.weekday() == 6:
            week_num += 1
        if week_num == 2:
            break
        weekly_data[week_num]['uniques'] += day_uniques
        weekly_data[week_num]['views'] += day_views
        weekly_data[week_num]['subs'] += day_subs
        weekly_data[week_num]['days'][day_dt.weekday()]['uniques'] += day_uniques
        weekly_data[week_num]['days'][day_dt.weekday()]['views'] += day_views
        weekly_data[week_num]['days'][day_dt.weekday()]['subs'] += day_subs

    print('Subreddit Traffic Processed')
    count = 0
    print('Processing Subreddit Modlog')

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

print('Processing Subreddit Activity')

for submission in subreddit.new(limit=1000):
    sub_count += 1
    sub_dt = datetime.utcfromtimestamp(submission.created_utc)
    if sub_count % 10 == 0:
        print(str(sub_count)+' Submissions Processed So Far')
    if submission.created_utc > start_utc_ts:
        continue
    if submission.created_utc > end_utc_ts:
        if submission.author is not None:
            if submission.author.name not in submitters:
                submitters[submission.author.name] = 0
            submitters[submission.author.name] += 1
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
        elif weekly_data[1]['activity']['most_discussed'].num_comments < submission.num_comments:
            weekly_data[1]['activity']['most_discussed'] = submission
        if weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'] is None:
            weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'] = submission
        elif weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'].num_comments < submission.num_comments:
            weekly_data[1]['days'][sub_dt.weekday()]['activity']['most_discussed'] = submission
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if comment.author is not None:
                if comment.author.name not in commenters:
                    commenters[comment.author.name] = 0
                commenters[comment.author.name] += 1
            com_count += 1
            com_dt = datetime.utcfromtimestamp(comment.created_utc)
            if com_count % 50 == 0:
                print(str(com_count)+' Comments Processed So Far')
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

sorted_commenters = {}
for commenter, comment_count in sorted(commenters.items(), key=lambda x:x[1], reverse=True):
    sorted_commenters[commenter] = comment_count
sorted_submitters = {}
for poster, post_count in sorted(submitters.items(), key=lambda x:x[1], reverse=True):
    sorted_submitters[poster] = post_count

print('Top 5 Submitters')
t5count = 1
t5post = ''
for submitter, submission_count in sorted_submitters.items():
    if t5count > 5:
        break
    print(str(submitter) + ': ' + str(submission_count))
    t5post = t5post + str(t5count) + '. ' + str(submitter) + ': ' + str(submission_count) + '\n'
    t5count += 1

print('Top 5 Commenters')
t5count = 1
t5com = ''
for commenter, comment_count in sorted_commenters.items():
    if t5count > 5:
        break
    print(str(commenter) + ': ' + str(comment_count))
    t5com = t5com + str(t5count) + '. ' + str(commenter) + ': ' + str(comment_count) + '\n'
    t5count += 1

print('Compiling Reports')
activity_table = '|  Day  | # Posts  |  # Comments  |  Top Post | Top Comment | Most Discussed |\n'
activity_table = activity_table + '|---|---|---|---|---|---|\n'

for day, info in weekly_data[1]['days'].items():
    if day == 0:
        activity_table = activity_table + '|  Monday  |  '
    elif day == 1:
        activity_table = activity_table + '|  Tuesday  |  '
    elif day == 2:
        activity_table = activity_table + '|  Wednesday  |  '
    elif day == 3:
        activity_table = activity_table + '|  Thursday  |  '
    elif day == 4:
        activity_table = activity_table + '|  Friday  |  '
    elif day == 5:
        activity_table = activity_table + '|  Saturday  |  '
    elif day == 6:
        activity_table = activity_table + '|  Sunday  |  '

    activity_table = activity_table + '{:,}'.format(info['activity']['total_posts']) + ' | '
    activity_table = activity_table + '{:,}'.format(info['activity']['total_comments']) + ' | '
    activity_table = activity_table + ' [Post](https://www.reddit.com' + info['activity']['top_post'].permalink + ') Score: ' + '{:,}'.format(info['activity']['top_post'].score) + ' | '
    activity_table = activity_table + ' [Comment](https://www.reddit.com' + info['activity']['top_comment'].permalink + ') Score: ' + '{:,}'.format(info['activity']['top_comment'].score) + ' | '
    activity_table = activity_table + ' [Most Discussed](https://www.reddit.com' + info['activity']['most_discussed'].permalink + ') Comments: ' + '{:,}'.format(info['activity']['most_discussed'].num_comments) + ' |\n'

    if day == 6:
        activity_table = activity_table + '| **Totals** | '
        activity_table = activity_table + '{:,}'.format(weekly_data[1]['activity']['total_posts']) + ' | '
        activity_table = activity_table + '{:,}'.format(weekly_data[1]['activity']['total_comments']) + ' | '
        activity_table = activity_table + ' [Post](https://www.reddit.com' + weekly_data[1]['activity']['top_post'].permalink + ') Score: ' + '{:,}'.format(weekly_data[1]['activity']['top_post'].score) + ' | '
        activity_table = activity_table + ' [Comment](https://www.reddit.com' + weekly_data[1]['activity']['top_comment'].permalink + ') Score: ' + '{:,}'.format(weekly_data[1]['activity']['top_comment'].score) + ' | '
        activity_table = activity_table + ' [Most Discussed](https://www.reddit.com' + weekly_data[1]['activity']['most_discussed'].permalink + ') Comments: ' + '{:,}'.format(weekly_data[1]['activity']['most_discussed'].num_comments) + ' |\n'

date_range = weekly_data[1]['days'][0]['date'].strftime('%b %d') + ' - ' + weekly_data[1]['days'][6]['date'].strftime('%b %d')

if runCommand is None or runCommand == 'dryrun':
    actions_table = '|  Day  |  Bans  |  Unbans  |  Removals  |  Approvals  |  Flair  |  Sticky  |  Other  |  **Total**  |\n'
    actions_table = actions_table + '|---|---|---|---|---|---|---|---|---|\n'
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

        actions_table = actions_table + '{:,}'.format(info['actions']['bans']) + '  |  '
        actions_table = actions_table + '{:,}'.format(info['actions']['unbans']) + '  |  '
        actions_table = actions_table + '{:,}'.format(info['actions']['removals']) + '  |  '
        actions_table = actions_table + '{:,}'.format(info['actions']['approvals']) + '  |  '
        actions_table = actions_table + '{:,}'.format(info['actions']['flair']) + '  |  '
        actions_table = actions_table + '{:,}'.format(info['actions']['sticky']) + '  |  '
        actions_table = actions_table + '{:,}'.format(info['actions']['other']) + '  |  '
        actions_table = actions_table + '{:,}'.format(info['actions']['total']) + '  |\n'

        traffic_table = traffic_table + '{:,}'.format(info['uniques']) + '  |  '
        traffic_table = traffic_table + '{:,}'.format(info['views']) + '  |  '
        traffic_table = traffic_table + '{:,}'.format(info['subs']) + '  |\n'

        if day == 6:
            actions_table = actions_table + '|  **Totals**  |  '+'{:,}'.format(weekly_data[1]['actions']['bans'])+'  |  '+'{:,}'.format(weekly_data[1]['actions']['unbans'])+'  |  '+'{:,}'.format(weekly_data[1]['actions']['removals'])+'  |  '+'{:,}'.format(weekly_data[1]['actions']['approvals'])+'  |  '+'{:,}'.format(weekly_data[1]['actions']['flair'])+'  |  '+'{:,}'.format(weekly_data[1]['actions']['sticky'])+'  |  '+'{:,}'.format(weekly_data[1]['actions']['other'])+'  |  '+'{:,}'.format(weekly_data[1]['actions']['total'])+'  |\n'
            traffic_table = traffic_table + '|  **Totals**  |  '+'{:,}'.format(weekly_data[1]['uniques'])+'  |  '+'{:,}'.format(weekly_data[1]['views'])+'  |  '+'{:,}'.format(weekly_data[1]['subs'])+'  |\n'

    log_report = open("PostTemplates/modLogReport.txt").read()
    log_report = log_report.replace('{{mod_activity}}', actions_table)
    log_report = log_report.replace('{{traffic_report}}', traffic_table)
    log_report = log_report.replace('{{activity_report}}', activity_table)
    log_report = log_report.replace('{{date_range}}', date_range)
else:
    log_report = None

if runCommand is not None and runCommand == 'dryrun' and log_report is not None:
    print(log_report)
    HookBot.post_status(
        'ActualBernieBot Status Message',
        'ActualBernieBot compiled the transparency report in *dryrun* mode, so it was not posted to the subreddit',
        settings.SLACK_STATUS_CHANNEL
    )
elif runCommand is not None and runCommand == 'othersub' and otherSub is not None:
    print(activity_table)
    posts_per_day = weekly_data[1]['activity']['total_posts']/7
    comments_per_day = weekly_data[1]['activity']['total_comments']/7
    avg_com_per_post = weekly_data[1]['activity']['total_comments']/weekly_data[1]['activity']['total_posts']
    HookBot.post_complex_message(
        pretext='Activity report for r/'+str(otherSub)+' compiled',
        text='Activity report for '+str(date_range),
        fields=[
            {
                'title': 'Total Posts',
                'value': '{:,}'.format(weekly_data[1]['activity']['total_posts']),
                'short': True
            },
            {
                'title': 'Total Comments',
                'value': '{:,}'.format(weekly_data[1]['activity']['total_comments']),
                'short': True
            },
            {
                'title': 'Best Post Score',
                'value': '{:,}'.format(weekly_data[1]['activity']['top_post'].score),
                'short': True
            },
            {
                'title': 'Best Comment Score',
                'value': '{:,}'.format(weekly_data[1]['activity']['top_comment'].score),
                'short': True
            },
            {
                'title': 'Posts Per Day',
                'value': '{:.2f}'.format(posts_per_day),
                'short': True
            },
            {
                'title': 'Comments Per Day',
                'value': '{:.2f}'.format(comments_per_day),
                'short': True
            },
            {
                'title': 'Comments Per Post',
                'value': '{:.2f}'.format(avg_com_per_post),
                'short': True
            },
            {
                'title': 'Most Discussed Post',
                'value': '{:,}'.format(weekly_data[1]['activity']['most_discussed'].num_comments)+' Comments',
                'short': True
            },
            {
                'title': 'Top 5 Submitters',
                'value': t5post,
                'short': False
            },
            {
                'title': 'Top 5 Commenters',
                'value': t5com,
                'short': False
            }
        ],
        color='good',
        channel=settings.SLACK_STATUS_CHANNEL
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
