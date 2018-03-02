

class InspectorShadowban:
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
        self.banlist = [
            'FThumb'
        ]

    def main(self):
        subreddit = self.reddit.subreddit('sandersforpresident')
        print('Starting Script')

        for comment in subreddit.stream.comments():
            if comment.author.name in self.banlist:
                comment.mod.remove()
                print('Shadowbanned Comment From: '+comment.author.name)