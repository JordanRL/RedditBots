import json
import base64
import zlib
import time
import pprint


class UserNotes:
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
        self.reasons = [
            "mod_note",
            "good_contributor",
            "abuse_watch",
            "permanently_banned",
            "recently_unbanned",
            "banned",
            "official_warning",
            "spam_watch",
        ]

    def add_note(self, user, note, note_type):
        usernote_page = self.subreddit.wiki['usernotes']
        usernote_content = usernote_page.content_md
        usernote_obj = json.loads(usernote_content)
        unpacked_notes = json.loads(
            zlib.decompress(
                base64.b64decode(usernote_obj['blob'])
            ).decode()
        )
        mods = usernote_obj['constants']['users']
        if 'ActualBernieBot' in mods:
            mod_pos = mods.index('ActualBernieBot')
        else:
            mods.append('ActualBernieBot')
            mod_pos = mods.index('ActualBernieBot')
            usernote_obj['constants']['users'] = mods
        if user in unpacked_notes:
            unpacked_notes[user]['ns'].insert(0, {
                'n': note,
                't': int(time.time()),
                'm': mod_pos,
                'l': '',
                'w': self.reasons.index(note_type)
            })
        else:
            unpacked_notes[user] = {
                'ns': [{
                    'n': note,
                    't': int(time.time()),
                    'm': mod_pos,
                    'l': '',
                    'w': self.reasons.index(note_type)
                }]
            }
        packed_notes = base64.b64encode(
            zlib.compress(
                json.dumps(unpacked_notes).encode()
            )
        )
        usernote_obj['blob'] = packed_notes.decode()
        packed_page = json.dumps(usernote_obj)
        usernote_page.edit(packed_page)

    def has_note(self, user, note):
        usernote_page = self.subreddit.wiki['usernotes']
        usernote_content = usernote_page.content_md
        usernote_obj = json.loads(usernote_content)
        unpacked_notes = json.loads(
            zlib.decompress(
                base64.b64decode(usernote_obj['blob'])
            ).decode()
        )
        if user in unpacked_notes:
            for noteObj in unpacked_notes[user]['ns']:
                if noteObj['n'] == note:
                    return True
        return False
