import sys
import os
import SlackWebHook
import signal
import praw
import settings
sys.path.append(os.path.abspath('./ImmediateAttention'))
sys.path.append(os.path.abspath('./BrigadeMonitor'))
import mentionMonitor
import submissionMonitor
import dailyquote
import highReports
import risingPost
import trollUnreported
import violence
import scoreTracking

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
    else:
        print('Unknown Bot: '+runCommand)
except KeyboardInterrupt:
    print('Stopping bot')
    HookBot.post_warning(pretext=status_message,
                         text='The bot "'+runCommand+'" is being shut down',
                         channel=settings.SLACK_STATUS_CHANNEL)
    sys.exit(1)
except:
    print('Unexpected error: ', sys.exc_info()[0])
    HookBot.post_danger(pretext=status_message,
                        text='The bot "'+runCommand+'" has experienced an error',
                        channel=settings.SLACK_STATUS_CHANNEL)
    raise
