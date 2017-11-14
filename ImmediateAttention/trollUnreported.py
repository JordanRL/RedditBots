import praw
import SlackWebHook
import settings

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
alert = 0

print('Starting Script')

for comment in subreddit.stream.comments():
    if firstPass:
        print('Inside the stream')
        message = "Now monitoring for people replying to trolls instead of reporting them."
        pretext = "ActualBernieBot Status Message"
        SlackWebHookBot.post_status(pretext=pretext, text=message, channel='bot-notifications')
        firstPass = 0
    theText = comment.body.lower()
    if 'troll' in theText:
        alert = 1
    elif 'shill' in theText:
        alert = 1
    elif 'go back to' in theText:
        alert = 1
    if alert:
        if comment.author.name not in modlist:
            print('Found match')
            pretext = "This person might be replying to a troll instead of reporting them"
            SlackWebHookBot.post_submission_link(username=comment.author.name, title="Permalink",
                                                 permalink=comment.permalink+'?context=5', pretext=pretext, color="warning",
                                                 channel="bot-notifications")
        alert = 0
