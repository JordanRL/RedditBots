import praw
import settings
from pprint import pprint


reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)
subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)

for modlog in subreddit.mod.log(action='unbanuser',limit=5):
    pprint(vars(modlog))
