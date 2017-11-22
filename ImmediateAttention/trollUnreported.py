

class TrollUnreported:
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

    def main(self):
        mod_list = self.settings.SUBREDDIT_MODLIST
        alert = 0

        print('Starting Script')

        for comment in self.subreddit.stream.comments():
            the_text = comment.body.lower()
            if 'troll' in the_text:
                alert = 1
            elif 'shill' in the_text:
                alert = 1
            elif 'go back to' in the_text:
                alert = 1
            if alert:
                if comment.author.name not in mod_list:
                    print('Found match')
                    pretext = "This person might be replying to a troll instead of reporting them"
                    self.webHook.post_submission_link(username=comment.author.name, title="Permalink",
                                                      permalink=comment.permalink+'?context=5', pretext=pretext,
                                                      color="warning", channel=self.settings.SLACK_ALERT_CHANNEL)
                alert = 0
