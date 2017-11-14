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

firstPass = 1
alert = 0

print('Starting Script')

for comment in subreddit.stream.comments():
    if firstPass:
        print('Inside the stream')
        message = "Now monitoring for possible calls to violence."
        pretext = "ActualBernieBot Status Message"
        SlackWebHookBot.post_status(pretext=pretext, text=message, channel='bot-notifications')
        firstPass = 0
    theText = comment.body.lower()
    if 'kill yourself' in theText:
        alert = 1
    elif 'kill them' in theText:
        alert = 1
    elif 'kill him' in theText:
        alert = 1
    elif 'kill her' in theText:
        alert = 1
    elif ' kys ' in theText:
        alert = 1
    if alert:
        print('Found match')
        pretext = "Possible violation of reddit violence policy found"
        SlackWebHookBot.post_submission_link(username=comment.author.name, title="Permalink", permalink=comment.permalink, pretext=pretext, color="danger", channel="danger-room")
        alert = 0
