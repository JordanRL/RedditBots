

class MentionMonitor:
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

        for comment in subredditMulti.stream.comments():
            theText = comment.body.lower()
            if self.subreddit.display_name.lower() in theText:
                print('Found Match')
                message = 'Possible Brigading From /r/'+comment.subreddit.display_name
                self.webHook.post_submission_link(username=comment.author.name, title='Permalink',
                                                  permalink=comment.permalink+'?context=5', pretext=message,
                                                  color='warning', channel='danger-room')
