

class InspectorKarma:
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
        self.karmaWatch = [
            'the_donald',
            'enough_sanders_spam'
        ]
        self.identifiedUsers = []
        self.karmaLimit = 500
        self.whitelist = [
            'The1stCitizenOfTheIn'
        ]

    def main(self):
        subreddit = self.reddit.subreddit('sandersforpresident')
        print('Starting Script')

        for comment in subreddit.stream.comments():
            report = 0
            if comment.author.name in self.identifiedUsers:
                report = 1
            else:
                karmaTotal = 0
                for authorComment in comment.author.comments.new(limit=None):
                    if authorComment.subreddit.display_name.lower() in self.karmaWatch:
                        karmaTotal += authorComment.score
                if karmaTotal > self.karmaLimit:
                    report = 1
                    self.identifiedUsers.append(comment.author.name)
            if report == 1 and comment.author.name not in self.whitelist:
                comment.report('Inspector has flagged this comment for coming from a user with bad karma')
                print('Bad Karma Found: '+comment.author.name)