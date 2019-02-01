from datetime import timedelta
from datetime import datetime
import time


class UnbanReport:
    def __init__(self, reddit, subreddit, slack_hook, settings):
        """

        :param reddit:
        :type reddit: praw.Reddit
        :param subreddit:
        :type subreddit: praw.Reddit.subreddit
        :param slack_hook:
        :type slack_hook: SlackWebHook.WebHook
        :param settings:
        :type settings: settings
        """
        self.reddit = reddit
        self.subreddit = subreddit
        self.webHook = slack_hook
        self.settings = settings
        self.bans = []

    def main(self):
        print('Starting Script')
        for ban in self.subreddit.mod.log(action='unbanuser', limit=100):
            ban_datetime = datetime.utcfromtimestamp(ban.created_utc)
            print('Unban: '+ban.target_author+' by '+ban.mod.name+' on '+str(ban_datetime.month)+'-'+str(ban_datetime.day)+'-'+str(ban_datetime.year))
