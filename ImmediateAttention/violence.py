

class Violence:
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
        alert = 0

        print('Starting Script')

        for comment in self.subreddit.stream.comments():
            the_text = comment.body.lower()
            if 'kill yourself' in the_text:
                alert = 1
            elif 'kill them' in the_text:
                alert = 1
            elif 'kill him' in the_text:
                alert = 1
            elif 'kill her' in the_text:
                alert = 1
            elif ' kys ' in the_text:
                alert = 1
            elif 'just die' in the_text:
                alert = 1
            elif 'you die' in the_text:
                alert = 1
            elif 'get raped' in the_text:
                alert = 1
            if alert:
                print('Found match')
                pretext = "Possible violation of reddit violence/harassment policy found"
                self.webHook.post_submission_link(username=comment.author.name, title="Permalink",
                                                  permalink=comment.permalink, pretext=pretext,
                                                  color="danger", channel=self.settings.SLACK_DANGER_CHANNEL)
                alert = 0
