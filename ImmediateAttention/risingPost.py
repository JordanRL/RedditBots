import time


class RisingPost:
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
        self.stickyPost = open("PostTemplates/risingPostSticky.txt").read()
        self.reddit = reddit
        self.subreddit = subreddit
        self.webHook = slack_hook
        self.settings = settings
        self.stickyPost = self.stickyPost.replace('{{rules_date}}', 'November 8th, 2017')

    def main(self):
        flair_meta_id = self.settings.SUBREDDIT_META_FLAIR_ID

        print('Starting Script')

        recorded_posts = {}

        while True:
            all_sub = self.reddit.subreddit('all')
            position = 1
            for item in all_sub.hot(limit=200):
                if self.subreddit.display_name.lower() == item.subreddit.display_name.lower():
                    pretext = None
                    color = None
                    channel = None
                    if item.name not in recorded_posts:
                        recorded_posts[item.name] = {
                            "top25": 0,
                            "top100": 0,
                            "top200": 0,
                            "highest-position": 1000,
                            "last-process-time": time.time(),
                            "last-score": 0,
                            "last-position": 0,
                            "sticky-post-made": 0
                        }
                    if position < 25 and not recorded_posts[item.name]["top25"]:
                        print('Top 25 post')
                        pretext = "This post *has reached the front page* of r/all (#"+str(position)+")"
                        color = "warning"
                        channel = self.settings.SLACK_DANGER_CHANNEL
                        recorded_posts[item.name]["top25"] = 1
                        recorded_posts[item.name]["top100"] = 1
                        recorded_posts[item.name]["top200"] = 1
                    elif position < 100 and not recorded_posts[item.name]["top100"]:
                        print('Top 100 post')
                        pretext = "This post is now *top 100* on r/all (#"+str(position)+")"
                        color = "warning"
                        channel = self.settings.SLACK_SUBREDDIT_CHANNEL
                        recorded_posts[item.name]["top100"] = 1
                        recorded_posts[item.name]["top200"] = 1
                    elif not recorded_posts[item.name]["top200"]:
                        print('Top 200 post')
                        pretext = "This post is now *top 200* on r/all (#"+str(position)+")"
                        color = "good"
                        channel = self.settings.SLACK_SUBREDDIT_CHANNEL
                        recorded_posts[item.name]["top200"] = 1
                    if not recorded_posts[item.name]["sticky-post-made"]:
                        sticky_comment = item.reply(self.stickyPost)
                        sticky_comment.mod.approve()
                        sticky_comment.mod.distinguish(how='yes',sticky=True)
                        sticky_comment.mod.ignore_reports()
                        recorded_posts[item.name]["sticky-post-made"] = 1
                    if pretext is not None and color is not None and channel is not None:
                        self.webHook.post_submission_link(username=item.author.name, title=item.title,
                                                          permalink=item.permalink, pretext=pretext,
                                                          color=color, channel=channel)
                    if recorded_posts[item.name]["highest-position"] > position:
                        recorded_posts[item.name]["highest-position"] = position
                        item.flair.select(flair_meta_id, 'r/all #'+str(position))
                position = position + 1
            time.sleep(60)
