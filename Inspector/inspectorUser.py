import time
import prawcore
import pprint


class InspectorUser:
    def __init__(self, reddit, redditUser, slack_hook, settings):
        """

        :param reddit:
        :type reddit: praw.Reddit
        :param redditUser:
        :type redditUser: praw.Reddit.redditor
        :param slack_hook:
        :type slack_hook: SlackWebHook.WebHook
        :param settings:
        :type settings: settings
        """
        self.reddit = reddit
        self.redditUser = redditUser
        self.webHook = slack_hook
        self.settings = settings
        self.karmaTotal = {
            'the_donald': 0,
            'enough_sanders_spam': 0,
            'wayofthebern': 0,
            'theredpill': 0
        }
        self.karmaAbbr = {
            'the_donald': 'T_D',
            'enough_sanders_spam': 'ESS',
            'wayofthebern': 'WotB',
            'theredpill': 'TRP'
        }
        self.karmaHistory = {}
        self.karmaWatch = [
            'the_donald',
            'enough_sanders_spam',
            'wayofthebern',
            'theredpill'
        ]
        self.karmaMods = {}
        self.subNote = [
            'wayofthebern'
        ]
        self.subAbuse = [
            'the_donald',
            'enough_sanders_spam',
            'theredpill'
        ]
        self.identifiedUsers = []
        self.identifiedUsersKarma = {}
        self.identifiedUsersTime = {}
        self.karmaLimit = 500
        self.karmaNoteLimit = 250
        self.whitelist = [
            'The1stCitizenOfTheIn'
        ]

    def main(self):
        for comment in self.redditUser.comments.new(limit=None):
            sub_name = comment.subreddit.display_name.lower()
            if sub_name in self.karmaWatch:
                self.karmaTotal[sub_name] += comment.score
            if sub_name in self.karmaHistory:
                self.karmaHistory[sub_name] += comment.score
            else:
                self.karmaHistory[sub_name] = comment.score

        print('Karma History Inspected for '+self.redditUser.name)

        for sub, karma in self.karmaHistory.items():
            print(sub+': '+str(karma))
