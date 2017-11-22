import time


class HighReports:
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
        mod_list = self.settings.SUBREDDIT_MODLIST

        threshold_danger = self.settings.SUBREDDIT_REPORT_THRESHOLD_DANGER
        threshold_notice = self.settings.SUBREDDIT_REPORT_THRESHOLD_NOTICE

        print('Starting Script')

        recorded_reports = {}

        while True:
            for item in self.subreddit.mod.reports(limit=None):
                if (item.author.name not in mod_list) and (not item.ignore_reports) and (not item.approved):
                    if item.name not in recorded_reports:
                        recorded_reports[item.name] = {
                            "num_reports": item.num_reports,
                            "user_reports": item.user_reports,
                            "mod_reports": item.mod_reports,
                            "sent_danger": 0,
                            "sent_notice": 0
                        }
                    if item.num_reports > threshold_danger and not recorded_reports[item.name]['sent_danger']:
                        pretext = "This item has received more than "+str(threshold_danger)+" reports without being approved or ignored."
                        self.webHook.post_submission_link(username=item.author.name, title='Permalink',
                                                          permalink=item.permalink+'?context=5', pretext=pretext,
                                                          color='danger', channel=self.settings.SLACK_SUBREDDIT_CHANNEL)
                        recorded_reports[item.name]["sent_danger"] = 1
                    if item.num_reports > threshold_notice and not recorded_reports[item.name]['sent_notice']:
                        pretext = "A new report has been received."
                        self.webHook.post_submission_link(username=item.author.name, title='Permalink',
                                                          permalink=item.permalink+'?context=5', pretext=pretext,
                                                          color='warning', channel=self.settings.SLACK_SUBREDDIT_CHANNEL)
                        recorded_reports[item.name]["sent_notice"] = 1

            time.sleep(5)
