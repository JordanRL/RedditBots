import praw
import SlackWebHook
import settings
from pprint import pprint
import time

reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)

subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)
SlackWebHookBot = SlackWebHook.WebHook()

modlist = [
    'JordanLeDoux',
    'GalacticSoap',
    'Chartis',
    'neurocentrixx',
    '2ply',
    '9AD-',
    'aranurea',
    'GravityCat1',
    'ActualBernieBot'
    'writingtoss',
    'scriggities',
    'IrrationalTsunami'
]

firstPass = 1
thresholdDanger = 1
thresholdNotice = 0

print('Starting Script')

recordedReports = {}

while True:
    if firstPass:
        print('Inside the loop')
        message = "Now monitoring the modqueue for items with several reports"
        pretext = "ActualBernieBot Status Message"
        SlackWebHookBot.post_status(pretext=pretext, text=message, channel='bot-notifications')
        firstPass = 0
    for item in subreddit.mod.reports(limit=None):
        if (item.author.name not in modlist) and (not item.ignore_reports) and (not item.approved):
            if item.num_reports > thresholdDanger:
                if item.name not in recordedReports:
                    pretext = "This item has received more than "+str(thresholdDanger)+" reports without being approved or ignored."
                    SlackWebHookBot.post_submission_link(username=item.author.name, title='Permalink',
                                                     permalink=item.permalink+'?context=5', pretext=pretext,
                                                     color='danger', channel='danger-room')
                    recordedReports[item.name] = {
                        "num_reports": item.num_reports,
                        "user_reports": item.user_reports,
                        "mod_reports": item.mod_reports
                    }
    time.sleep(5)
