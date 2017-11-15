import time


class RisingPost:
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
        flairMetaId = '03bb0c60-6103-11e7-9f5a-0ec41b29461a'

        print('Starting Script')

        recordedPosts = {}

        while True:
            all_sub = self.reddit.subreddit('all')
            position = 1
            for item in all_sub.hot(limit=200):
                if self.subreddit.display_name.lower() == item.subreddit.display_name.lower():
                    pretext = None
                    color = None
                    channel = None
                    if item.name not in recordedPosts:
                        recordedPosts[item.name] = {
                            "top25": 0,
                            "top100": 0,
                            "top200": 0,
                            "highest-position": 1000
                        }
                    if position < 25 and not recordedPosts[item.name]["top25"]:
                        print('Top 25 post')
                        pretext = "This post *has reached the front page* of r/all (#"+str(position)+")"
                        color = "warning"
                        channel = "danger-room"
                        recordedPosts[item.name]["top25"] = 1
                        recordedPosts[item.name]["top100"] = 1
                        recordedPosts[item.name]["top200"] = 1
                    elif position < 100 and not recordedPosts[item.name]["top100"]:
                        print('Top 100 post')
                        pretext = "This post is now *top 100* on r/all (#"+str(position)+")"
                        color = "warning"
                        channel = "bot-notifications"
                        recordedPosts[item.name]["top100"] = 1
                        recordedPosts[item.name]["top200"] = 1
                    elif not recordedPosts[item.name]["top200"]:
                        print('Top 200 post')
                        pretext = "This post is now *top 200* on r/all (#"+str(position)+")"
                        color = "good"
                        channel = "bot-notifications"
                        recordedPosts[item.name]["top200"] = 1
                    if pretext is not None and color is not None and channel is not None:
                        self.webHook.post_submission_link(username=item.author.name, title=item.title,
                                                          permalink=item.permalink, pretext=pretext,
                                                          color=color, channel=channel)
                    if recordedPosts[item.name]["highest-position"] > position:
                        recordedPosts[item.name]["highest-position"] = position
                        item.flair.select(flairMetaId, 'r/all #'+str(position))
                position = position + 1
            time.sleep(60)
