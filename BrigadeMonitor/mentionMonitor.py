import praw
import settings
import SlackWebHook

reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)

subredditMulti = reddit.subreddit('The_Donald+Enough_Sanders_Spam+WayOfTheBern')
SlackWebHookBot = SlackWebHook.WebHook()

firstPass = 1

print('Starting Script')

for comment in subredditMulti.stream.comments():
    if firstPass:
        print('Inside the stream')
        pretextStart = 'Brigade Monitor now watching these subreddits for brigading comments'
        textStart = 'Monitoring: The_Donald, Enough_Sanders_Spam, WayOfTheBern'
        SlackWebHookBot.post_status(pretext=pretextStart, text=textStart, channel='bot-notifications')
        firstPass = 0
    theText = comment.body.lower()
    if settings.REDDIT_SUBREDDIT in theText:
        print('Found Match')
        message = 'Possible Brigading From /r/'+comment.subreddit.display_name
        SlackWebHookBot.post_submission_link(username=comment.author.name, title='Permalink',
                                             permalink=comment.permalink+'?context=5', pretext=message, color='warning',
                                             channel='danger-room')
