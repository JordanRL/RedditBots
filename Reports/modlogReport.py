from datetime import timedelta
from datetime import datetime
import time


class ModlogReport:
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
        self.user_notes = user_notes
        self.bans = []

    def compile_weekly_report(self):
        today = datetime.now()
        one_week_ago = today + timedelta(days=-7)
        start = datetime(year=one_week_ago.year, month=one_week_ago.month, day=one_week_ago.day)
        end = datetime(year=today.year, month=today.month, day=today.day)

        start_ts = start.timestamp()
        end_ts = end.timestamp()

    def post_bans(self):
        print('Starting Script')
        while 1:
            for ban in self.subreddit.mod.log(action='banuser', limit=2):
                if ban.id not in self.bans:
                    ban_datetime = datetime.utcfromtimestamp(ban.created_utc)
                    print('New ban found by '+ban.mod.name)
                    self.bans.append(ban.id)
                    if ban.details == 'permanent':
                        pre_text = 'This user has been permanently banned by '+ban.mod.name+' :banhammer:'
                        note_text = 'ABB: Permabanned by '+ban.mod.name+' on '+str(ban_datetime.month)+'-'+str(ban_datetime.day)+'-'+str(ban_datetime.year)
                        note_type = 'permanently_banned'
                        duration = 'Permanent'
                    elif ban.details == 'changed to permanent':
                        pre_text = 'This ban has been changed from temporary to permanent by '+ban.mod.name+' :timer_clock: :arrow_right: :banhammer:'
                        note_text = 'ABB: Extended to permaban by '+ban.mod.name+' on '+str(ban_datetime.month)+'-'+str(ban_datetime.day)+'-'+str(ban_datetime.year)
                        note_type = 'permanently_banned'
                        duration = 'Extended to Permanent'
                    else:
                        note_text = 'ABB: Tempbanned by '+ban.mod.name+' on '+str(ban_datetime.month)+'-'+str(ban_datetime.day)+'-'+str(ban_datetime.year)
                        note_type = 'banned'
                        if ban.details == '1 days':
                            duration = '1 day'
                        else:
                            duration = ban.details
                        pre_text = 'This user has been temporarily banned by '+ban.mod.name+' for '+duration+' :timer_clock:'
                    main_text = 'Please ensure that this ban was in order'
                    fields = [
                        {
                            'title': 'Duration',
                            'value': duration,
                            'short': True
                        },
                        {
                            'title': 'Banned By',
                            'value': ban.mod.name,
                            'short': True
                        },
                        {
                            'title': 'Ban Note',
                            'value': ban.description,
                            'short': False
                        }
                    ]
                    self.webHook.post_user_link_with_fields(username=ban.target_author,
                                                            text=main_text,
                                                            pretext=pre_text,
                                                            channel='discipline-review',
                                                            color='danger',
                                                            fields=fields
                                                            )
                    if not self.user_notes.has_note(ban.target_author, note_text):
                        self.user_notes.add_note(ban.target_author, note_text, note_type)
            time.sleep(60)
