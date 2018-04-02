import json
import re


class InspectorKarma:
    def __init__(self, reddit, subreddit, slack_hook, settings, user_notes):
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
        self.notes = user_notes

    def main(self):
        subreddit = self.subreddit
        print('Starting Script')
        blacklist = json.loads(subreddit.wiki['blacklist'])

        for submission in subreddit.stream.submissions():
            
