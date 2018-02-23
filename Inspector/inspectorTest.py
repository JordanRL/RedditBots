import time


class InspectorTest:
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
        """
        self.reddit = reddit
        self.subreddit = subreddit
        self.webHook = slack_hook
        self.settings = settings
        self.karmaTotal = {
            'the_donald': 0
        }
        self.karmaAbbr = {
            'the_donald': 'T_D'
        }
        self.karmaWatch = [
            'the_donald'
        ]
        self.karmaMods = {}
        self.subNote = []
        self.subAbuse = [
            'the_donald'
        ]
        self.identifiedUsers = []
        self.identifiedUsersKarma = {}
        self.identifiedUsersTime = {}
        self.karmaLimit = 500
        self.karmaNoteLimit = 250
        self.whitelist = [
            'The1stCitizenOfTheIn'
        ]
        self.safeUsers = []
        self.notes = user_notes

    def main(self):
        subreddit = self.reddit.subreddit('wayofthebern')
        print('Starting Script')
        self.whitelist = self.whitelist + self.settings.SUBREDDIT_MODLIST

        for sub_name in self.karmaWatch:
            self.karmaMods[sub_name] = self.reddit.subreddit(sub_name).moderator()

        for comment in subreddit.stream.comments():
            print('Processing Comment From '+comment.author.name)
            self.karmaTotal = {
                'the_donald': 0
            }
            if comment.author.name not in self.whitelist and comment.author.name not in self.safeUsers:
                report = 0
                if comment.author.name in self.identifiedUsers:
                    report = 1
                else:
                    karma_aggregate = 0
                    for authorComment in comment.author.comments.new(limit=None):
                        sub_name = authorComment.subreddit.display_name.lower()
                        if sub_name in self.karmaWatch:
                            self.karmaTotal[sub_name] += authorComment.score
                            karma_aggregate += authorComment.score
                    if karma_aggregate > self.karmaLimit:
                        report = 1
                        self.identifiedUsers.append(comment.author.name)
                        self.identifiedUsersKarma[comment.author.name] = self.make_karma_report()
                        self.identifiedUsersTime[comment.author.name] = time.time()
                    else:
                        self.safeUsers.append(comment.author.name)
                if report == 1:
                    karma_report = self.identifiedUsersKarma[comment.author.name]
                    print('Comment Found: '+comment.author.name+' ['+karma_report+']')

    def make_karma_report(self):
        report_string = ''
        for sub in self.karmaWatch:
            if self.karmaTotal[sub] > 0:
                if report_string == '':
                    report_string = self.karmaAbbr[sub]+': '+str(self.karmaTotal[sub])
                else:
                    report_string = report_string+' | '+self.karmaAbbr[sub]+': '+str(self.karmaTotal[sub])
        return report_string

    def make_user_note(self, author, bad_sub=None):
        if bad_sub is not None:
            if self.karmaTotal[bad_sub] > self.karmaNoteLimit:
                if not self.notes.has_note(author, 'ABB: '+self.karmaAbbr[bad_sub]+' Flagged'):
                    note_type = 'mod_note'
                    if bad_sub in self.subAbuse:
                        note_type = 'abuse_watch'
                    self.notes.add_note(author, 'ABB: '+self.karmaAbbr[bad_sub]+' Flagged', note_type)
                    print('Added Usernote ('+self.karmaAbbr[bad_sub]+'): ' + author)
        else:
            for note_sub in self.subNote:
                note_text = 'ABB: '+self.karmaAbbr[note_sub]+' Flagged'
                if self.karmaTotal[note_sub] > self.karmaNoteLimit and not self.notes.has_note(author, note_text):
                    print('Added Usernote (' + self.karmaAbbr[note_sub] + '): ' + author)
            for abuse_sub in self.subNote:
                note_text = 'ABB: '+self.karmaAbbr[abuse_sub]+' Flagged'
                if self.karmaTotal[abuse_sub] > self.karmaNoteLimit and not self.notes.has_note(author, note_text):
                    print('Added Usernote (' + self.karmaAbbr[abuse_sub] + '): ' + author)
