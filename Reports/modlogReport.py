from datetime import timedelta
from datetime import datetime


class ModlogReport:
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

    def compile_weekly_report(self):
        today = datetime.now()
        one_week_ago = today + timedelta(days=-7)
        start = datetime(year=one_week_ago.year, month=one_week_ago.month, day=one_week_ago.day)
        end = datetime(year=today.year, month=today.month, day=today.day)

        start_ts = start.timestamp()
        end_ts = end.timestamp()

