
class InspectorKarmaBern:
    def __init__(self, reddit, subreddit, slack_hook, settings, user_notes):
        """

        :param reddit:
        :type reddit: praw.Reddit
        :param subreddit:
        :type subreddit: praw.Reddit.subreddit
        :param slack_hook:
        :type slack_hook: SlackWebHook.WebHook
        :param settings:
        :type settings: settings
        :param user_notes:
        :type user_notes: userNotes.UserNotes
        """
        self.reddit = reddit
        self.subreddit = subreddit
        self.webHook = slack_hook
        self.settings = settings
        self.karmaWatch = [
            'wayofthebern'
        ]
        self.identifiedUsers = []
        self.karmaLimit = 500
        self.whitelist = [
            'The1stCitizenOfTheIn'
        ]
        self.notes = user_notes

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
                if not self.notes.has_note(comment.author.name, 'Good Contributor'):
                    comment.report('Inspector has flagged this comment because the user frequents WayOfTheBern')
                    print('Bad Karma Found: '+comment.author.name)
                    if not self.notes.has_note(comment.author.name, 'ABB: WotB Flagged'):
                        self.notes.add_note(comment.author.name, 'ABB: WotB Flagged', 'mod_note')
                        print('Added Usernote: '+comment.author.name)
