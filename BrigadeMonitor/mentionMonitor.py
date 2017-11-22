

class MentionMonitor:
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
        subreddit_multi = self.reddit.subreddit('+'.join(self.settings.SUBREDDIT_PROBLEM_SUBS))
        print('Starting Script')

        for comment in subreddit_multi.stream.comments():
            the_text = comment.body.lower()
            if self.subreddit.display_name.lower() in the_text:
                print('Found Match')
                message = 'Possible Brigading From /r/'+comment.subreddit.display_name
                self.webHook.post_submission_link(username=comment.author.name, title='Permalink',
                                                  permalink=comment.permalink+'?context=5', pretext=message,
                                                  color='warning', channel=self.settings.SLACK_ALERT_CHANNEL)
