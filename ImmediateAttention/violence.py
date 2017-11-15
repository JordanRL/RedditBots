

class Violence:
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
        alert = 0

        print('Starting Script')

        for comment in self.subreddit.stream.comments():
            theText = comment.body.lower()
            if 'kill yourself' in theText:
                alert = 1
            elif 'kill them' in theText:
                alert = 1
            elif 'kill him' in theText:
                alert = 1
            elif 'kill her' in theText:
                alert = 1
            elif ' kys ' in theText:
                alert = 1
            elif 'just die' in theText:
                alert = 1
            elif 'you die' in theText:
                alert = 1
            elif 'get raped' in theText:
                alert = 1
            if alert:
                print('Found match')
                pretext = "Possible violation of reddit violence policy found"
                self.webHook.post_submission_link(username=comment.author.name, title="Permalink",
                                                  permalink=comment.permalink, pretext=pretext,
                                                  color="danger", channel="danger-room")
                alert = 0
