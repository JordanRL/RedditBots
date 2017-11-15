

class TrollUnreported:
    def __init__(self, reddit, subreddit, slack_hook):
        """

        :param reddit:
        :type reddit: praw.Reddit
        :param subreddit:
        :type subreddit: praw.Reddit.subreddit
        :param slack_hook:
        :type slack_hook: SlackWebHook.WebHook
        """
        self.reddit = reddit
        self.subreddit = subreddit
        self.webHook = slack_hook

    def main(self):
        modlist = [
            'JordanLeDoux',
            'GalacticSoap',
            'Chartis',
            'neurocentrix',
            '2ply',
            '9AD-',
            'aranurea',
            'GravityCat1',
            'ActualBernieBot'
            'writingtoss',
            'scriggities',
            'IrrationalTsunami'
        ]
        alert = 0

        print('Starting Script')

        for comment in self.subreddit.stream.comments():
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
                    self.webHook.post_submission_link(username=comment.author.name, title="Permalink",
                                                      permalink=comment.permalink+'?context=5', pretext=pretext,
                                                      color="warning", channel="bot-notifications")
                alert = 0
