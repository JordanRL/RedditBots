import random


class DailyQuote:
    def __init__(self, slack_hook):
        """
        :param slack_hook: The SlackWebHook class
        :type slack_hook: SlackWebHook.WebHook
        """
        self.quoteList = open("bernieQuotes.txt").readlines()
        self.webHook = slack_hook

    def main(self):
        quote = random.choice(self.quoteList).strip()

        self.webHook.post_status(pretext="Here is a Bernie Sanders quote to remind us why we do this.",
                                 text="_"+quote+"_\n-*Bernie Sanders*", channel="random")
