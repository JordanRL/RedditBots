import time
import prawcore
import pprint


class InspectorKarma:
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
        self.notes = user_notes

    def main(self):
        subreddit = self.reddit.subreddit('sandersforpresident')
        print('Starting Script')
        self.whitelist = self.whitelist + self.settings.SUBREDDIT_MODLIST

        for sub_name in self.karmaWatch:
            self.karmaMods[sub_name] = self.reddit.subreddit(sub_name).moderator()

        while True:
            try:
                for comment in subreddit.stream.comments():
                    for sub_name, modlist in self.karmaMods.items():
                        if comment.author.name in modlist and not self.notes.has_note(comment.author.name, 'ABB: '+self.karmaAbbr[sub_name]+' Mod'):
                            self.notes.add_note(comment.author.name, 'ABB: '+self.karmaAbbr[sub_name]+' Mod', 'mod_note')
                    if self.notes.has_note(comment.author.name, 'Good Contributor') and comment.author.name not in self.whitelist:
                        self.whitelist.append(comment.author.name)
                    else:
                        self.karmaTotal = {
                            'the_donald': 0,
                            'enough_sanders_spam': 0,
                            'wayofthebern': 0,
                            'theredpill': 0
                        }
                        if comment.author.name not in self.whitelist:
                            report = 0
                            if comment.author.name in self.identifiedUsers:
                                old_time = self.identifiedUsersTime[comment.author.name]
                                diff_time = time.time() - old_time
                                if int(diff_time) < 86400:
                                    report = 1
                                else:
                                    self.identifiedUsers.remove(comment.author.name)
                            if report == 0:
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
                            if report == 1:
                                karma_report = self.identifiedUsersKarma[comment.author.name]
                                comment.report('Inspector: Bad Karma ['+karma_report+']')
                                print('Report Made: '+comment.author.name+' ['+karma_report+']')
                            self.make_user_note(author=comment.author.name)
            except prawcore.exceptions.NotFound:
                print('Not found exception, waiting 30 seconds then restarting.')
                time.sleep(30)
                continue
            except prawcore.exceptions.ResponseException:
                pprint.pprint(vars(prawcore.exceptions.ResponseException))
                raise prawcore.exceptions.ResponseException

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
                    self.notes.add_note(author, note_text, 'mod_note')
                    print('Added Usernote (' + self.karmaAbbr[note_sub] + '): ' + author)
            for abuse_sub in self.subAbuse:
                note_text = 'ABB: '+self.karmaAbbr[abuse_sub]+' Flagged'
                if self.karmaTotal[abuse_sub] > self.karmaNoteLimit and not self.notes.has_note(author, note_text):
                    self.notes.add_note(author, note_text, 'abuse_watch')
                    print('Added Usernote (' + self.karmaAbbr[abuse_sub] + '): ' + author)
