import praw
import settings
import calendar
import SlackWebHook
import pprint
from datetime import datetime


reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)

for submission in subreddit.top():
    pprint.pprint(vars(submission))
    break
