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

reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)

HookBot = SlackWebHook.WebHook()

runCommand = sys.argv[1]


def exit_gracefully():
    print('Unexpected error: ', sys.exc_info()[0])
    HookBot.post_danger(pretext='ActualBernieBot Status Message',
                        text='The bot "'+runCommand+'" has been stopped by the OS', channel='bot-notifications')


signal.signal(signal.SIGTERM, exit_gracefully)

try:
    if runCommand == "dailyquote":
        runClass = dailyquote.DailyQuote(HookBot)
        runClass.main()
    elif runCommand == "highReports":
        pretext = "ActualBernieBot Status Message"
        text = "ActualBernieBot is now monitoring the modqueue for reports"
        HookBot.post_status(pretext, text, 'bot-notifications')
        runClass = highReports.HighReports(reddit, subreddit, HookBot)
        runClass.main()
    elif runCommand == "risingPost":
        pretext = "ActualBernieBot Status Message"
        text = "ActualBernieBot is now monitoring r/all for posts from r/"+settings.REDDIT_SUBREDDIT
        HookBot.post_status(pretext, text, 'bot-notifications')
        runClass = risingPost.RisingPost(reddit, subreddit, HookBot)
        runClass.main()
    elif runCommand == "trollUnreported":
        pretext = "ActualBernieBot Status Message"
        text = "ActualBernieBot is now monitoring for replies to trolls"
        HookBot.post_status(pretext, text, 'bot-notifications')
        runClass = trollUnreported.TrollUnreported(reddit, subreddit, HookBot)
        runClass.main()
    elif runCommand == "violence":
        pretext = "ActualBernieBot Status Message"
        text = "ActualBernieBot is now monitoring for violations of reddit's violence policy"
        HookBot.post_status(pretext, text, 'bot-notifications')
        runClass = violence.Violence(reddit, subreddit, HookBot)
        runClass.main()
    elif runCommand == "mentionMonitor":
        pretext = "ActualBernieBot Status Message"
        text = "ActualBernieBot is now monitoring for possible brigading comments"
        HookBot.post_status(pretext, text, 'bot-notifications')
        runClass = mentionMonitor.MentionMonitor(reddit, subreddit, HookBot)
        runClass.main()
    elif runCommand == "submissionMonitor":
        pretext = "ActualBernieBot Status Message"
        text = "ActualBernieBot is now monitoring for possible brigading posts"
        HookBot.post_status(pretext, text, 'bot-notifications')
        runClass = submissionMonitor.SubmissionMonitor(reddit, subreddit, HookBot)
        runClass.main()
    else:
        print('Unknown Bot: '+runCommand)
except KeyboardInterrupt:
    print('Stopping bot')
    HookBot.post_warning(pretext='ActualBernieBot Status Message',
                         text='The bot "'+runCommand+'" is being shut down', channel='bot-notifications')
    sys.exit(1)
except:
    print('Unexpected error: ', sys.exc_info()[0])
    HookBot.post_danger(pretext='ActualBernieBot Status Message',
                        text='The bot "'+runCommand+'" has experienced an error', channel='bot-notifications')
    raise
