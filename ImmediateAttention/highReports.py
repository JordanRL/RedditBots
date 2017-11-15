import time


class HighReports:
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
        modlist = [
            'JordanLeDoux',
            'GalacticSoap',
            'Chartis',
            'neurocentrix',
            '2ply',
            '9AD-',
            'aranurea',
            'GravityCat1',
            'ActualBernieBot'
            'writingtoss',
            'scriggities',
            'IrrationalTsunami'
        ]

        thresholdDanger = 1
        thresholdNotice = 0

        print('Starting Script')

        recordedReports = {}

        while True:
            for item in self.subreddit.mod.reports(limit=None):
                if (item.author.name not in modlist) and (not item.ignore_reports) and (not item.approved):
                    if item.num_reports > thresholdDanger:
                        if (item.name not in recordedReports) or (not recordedReports[item.name]['notify_volume']):
                            pretext = "This item has received more than "+str(thresholdDanger)+" reports without being approved or ignored."
                            self.webHook.post_submission_link(username=item.author.name, title='Permalink',
                                                              permalink=item.permalink+'?context=5', pretext=pretext,
                                                              color='danger', channel='danger-room')
                            recordedReports[item.name] = {
                                "num_reports": item.num_reports,
                                "user_reports": item.user_reports,
                                "mod_reports": item.mod_reports,
                                "notify_volume": 1
                            }
                    if item.num_reports > thresholdNotice:
                        pretext = "A new report has been received."
                        self.webHook.post_submission_link(username=item.author.name, title='Permalink',
                                                          permalink=item.permalink+'?context=5', pretext=pretext,
                                                          color='danger', channel='bot-notifications')
                        if item.name not in recordedReports:
                            recordedReports[item.name] = {
                                "num_reports": item.num_reports,
                                "user_reports": item.user_reports,
                                "mod_reports": item.mod_reports,
                                "notify_volume": 0
                            }
            time.sleep(5)
