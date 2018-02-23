import sys
import os
import SlackWebHook
import signal
import praw
import settings
import pprint
sys.path.append(os.path.abspath('./ImmediateAttention'))
sys.path.append(os.path.abspath('./BrigadeMonitor'))
sys.path.append(os.path.abspath('./Inspector'))
sys.path.append(os.path.abspath('./Helpers'))
sys.path.append(os.path.abspath('./Reports'))
import mentionMonitor
import submissionMonitor
import dailyquote
import highReports
import risingPost
import trollUnreported
import violence
import scoreTracking
import inspectorKarma
import inspectorKarmaBern
import inspectorTest
import userNotes
import modlogReport

reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)

HookBot = SlackWebHook.WebHook(settings=settings)

runCommand = sys.argv[1]
if len(sys.argv) > 2:
    option = sys.argv[2]
else:
    option = 0
status_message = settings.BOT_NAME+' Status Message'

user_notes = userNotes.UserNotes(reddit, subreddit, HookBot, settings)

def exit_gracefully(signum, frame):
    print('Unexpected error: ', sys.exc_info()[0])
    HookBot.post_danger(pretext=status_message, text='The bot "'+runCommand+'" has been stopped by the OS',
                        channel=settings.SLACK_STATUS_CHANNEL)


signal.signal(signal.SIGTERM, exit_gracefully)

try:
    if runCommand == "dailyquote":
        runClass = dailyquote.DailyQuote(HookBot, settings, option)
        runClass.main()
    elif runCommand == "highReports":
        pretext = status_message
        text = settings.BOT_NAME+" is now monitoring the modqueue for reports"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = highReports.HighReports(reddit, subreddit, HookBot, settings)
        runClass.main()
    elif runCommand == "risingPost":
        pretext = status_message
        text = settings.BOT_NAME+" is now monitoring r/all for posts from r/"+settings.REDDIT_SUBREDDIT
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = risingPost.RisingPost(reddit, subreddit, HookBot, settings)
        runClass.main()
    elif runCommand == "trollUnreported":
        pretext = status_message
        text = settings.BOT_NAME+" is now monitoring for replies to trolls"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = trollUnreported.TrollUnreported(reddit, subreddit, HookBot, settings)
        runClass.main()
    elif runCommand == "violence":
        pretext = status_message
        text = settings.BOT_NAME+" is now monitoring for violations of reddit's violence policy"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = violence.Violence(reddit, subreddit, HookBot, settings)
        runClass.main()
    elif runCommand == "mentionMonitor":
        pretext = status_message
        text = settings.BOT_NAME+" is now monitoring for possible brigading comments"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = mentionMonitor.MentionMonitor(reddit, subreddit, HookBot, settings)
        runClass.main()
    elif runCommand == "submissionMonitor":
        pretext = status_message
        text = settings.BOT_NAME+" is now monitoring for possible brigading posts"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = submissionMonitor.SubmissionMonitor(reddit, subreddit, HookBot, settings)
        runClass.main()
    elif runCommand == "scoreTracking":
        pretext = status_message
        text = settings.BOT_NAME+" is now monitoring r/"+settings.REDDIT_SUBREDDIT+" for posts quickly getting upvotes"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = scoreTracking.ScoreTracking(reddit, subreddit, HookBot, settings)
        runClass.main()
    elif runCommand == "inspector":
        pretext = status_message
        text = settings.BOT_NAME+" is now running Inspector to watch for comments to report from problem subs"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = inspectorKarma.InspectorKarma(reddit, subreddit, HookBot, settings, user_notes)
        runClass.main()
    elif runCommand == "inspectorBern":
        runClass = inspectorTest.InspectorTest(reddit, subreddit, HookBot, settings, user_notes)
        runClass.main()
    elif runCommand == "monitorBans":
        pretext = status_message
        text = settings.BOT_NAME + " is now monitoring the mod log for bans"
        HookBot.post_status(pretext, text, settings.SLACK_STATUS_CHANNEL)
        runClass = modlogReport.ModlogReport(reddit, subreddit, HookBot, settings, user_notes)
        runClass.post_bans()
    elif runCommand == "testLog":
        logs = subreddit.mod.log(action='banuser', limit=5)
        for log in logs:
            pprint.pprint(log.mod)
    elif runCommand == "testVote":
        HookBot.post_complex_message_with_actions(
            'writingtoss',
            'A vote to ban *writingtoss* has been called by *IrrationalTsunami*',
            'Please select an option after reviewing the information below; for more information please see the threaded discussion',
            [
                {
                    'title': 'Duration',
                    'value': 'Permanent',
                    'short': True
                },
                {
                    'title': 'Vote Length',
                    'value': '24 Hours',
                    'short': True
                },
                {
                    'title': 'Votes Needed',
                    'value': '3',
                    'short': True
                },
                {
                    'title': 'Account Age',
                    'value': '5 years',
                    'short': True
                },
                {
                    'title': 'Rules Cited',
                    'value': '1, 2, 5, 7a',
                    'short': True
                },
                {
                    'title': 'Karma Report',
                    'value': 'T_D: 233 | WotB: 102 | ESS: 1194',
                    'short': True
                },
                {
                    'title': 'Ban Vote Called By',
                    'value': 'IrrationalTsunami',
                    'short': True
                },
                {
                    'title': 'User Being Considered',
                    'value': 'writingtoss',
                    'short': True
                },
                {
                    'title': 'Ban Reason',
                    'value': 'There are lots of reasons I could think of. The best reasons. Tremendous reasons.',
                    'short': False
                },
                {
                    'title': 'Link To Context',
                    'value': 'https://www.reddit.com/r/SandersForPresident/comments/6zogc2/town_hall_community_guidelines_revision_clinton/dmy8br5/?context=3',
                    'short': False
                }
            ],
            'danger',
            'bot-notifications',
            [
                {
                    'name': 'ban',
                    'text': 'Permaban (Requested)',
                    'type': 'button',
                    'value': 'permaban',
                    'style': 'danger',
                    'confirm': {
                        "title": "Are you sure?",
                        "text": "This will permanently ban this user if the vote passes.",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                },
                {
                    'name': 'ban',
                    'text': 'Tempban (Default: 2 Days)',
                    'type': 'button',
                    'value': 'tempban'
                },
                {
                    'name': 'ban',
                    'text': 'Warn Via PM (Using Cited Rules)',
                    'type': 'button',
                    'value': 'warn'
                },
                {
                    'name': 'ban',
                    'text': 'No Action',
                    'type': 'button',
                    'value': 'none'
                }
            ]
        )
    else:
        print('Unknown Bot: '+runCommand)
except KeyboardInterrupt:
    print('Stopping bot')
    if runCommand != "inspectorBern":
        HookBot.post_warning(pretext=status_message,
                             text='The bot "'+runCommand+'" is being shut down',
                             channel=settings.SLACK_STATUS_CHANNEL)
    sys.exit(1)
except:
    print('Unexpected error: ', sys.exc_info()[0])
    if runCommand != "inspectorBern":
        HookBot.post_danger(pretext=status_message,
                            text='The bot "'+runCommand+'" has experienced an error',
                            channel=settings.SLACK_STATUS_CHANNEL)
    raise
