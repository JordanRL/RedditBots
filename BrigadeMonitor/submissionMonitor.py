

class SubmissionMonitor:
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

        for submission in subreddit_multi.stream.submissions():
            the_text = submission.url.lower()
            if self.subreddit.display_name.lower() in the_text:
                print('Found Match')
                message = 'Likely Brigading From /r/' + submission.subreddit.display_name
                self.webHook.post_submission_link(username=submission.author.name, title=submission.title,
                                                  permalink=submission.permalink, pretext=message,
                                                  color='danger', channel=self.settings.SLACK_DANGER_CHANNEL)
