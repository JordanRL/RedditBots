

class SubmissionMonitor:
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
        subredditMulti = self.reddit.subreddit('The_Donald+Enough_Sanders_Spam+WayOfTheBern')
        print('Starting Script')

        for submission in subredditMulti.stream.submissions():
            theText = submission.url.lower()
            if self.subreddit.display_name.lower() in theText:
                print('Found Match')
                message = 'Likely Brigading From /r/' + submission.subreddit.display_name
                self.webHook.post_submission_link(username=submission.author.name, title=submission.title,
                                                  permalink=submission.permalink, pretext=message,
                                                  color='danger', channel='danger-room')
