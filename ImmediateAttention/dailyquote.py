import random


class DailyQuote:
    def __init__(self, slack_hook, settings, option=0):
        """
        :param slack_hook: The SlackWebHook class
        :type slack_hook: SlackWebHook.WebHook
        :param settings:
        :type settings: settings
        """
        self.quoteList = open("bernieQuotes.txt").readlines()
        self.webHook = slack_hook
        self.settings = settings
        self.option = int(option)

    def main(self):
        if self.option > 0:
            quote = self.quoteList[(self.option-1)].strip()
        else :
            quote = random.choice(self.quoteList).strip()

        self.webHook.post_status(pretext="Here is a Bernie Sanders quote to remind us why we do this.",
                                 text="_"+quote+"_\n-*Bernie Sanders*", channel=self.settings.SLACK_SOCIAL_CHANNEL)
