import time


class ScoreTracking:
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
        print('Starting Script')

        recorded_posts = {}

        while True:
            this_sub = self.reddit.subreddit(self.settings.REDDIT_SUBREDDIT)
            for item in this_sub.new(limit=100):
                pretext = None
                text = None
                color = None
                channel = None
                if item.name not in recorded_posts:
                    recorded_posts[item.name] = {
                        'per-hour-250': 0,
                        'per-hour-500': 0,
                        'per-hour-1000': 0,
                        'per-hour-2500': 0,
                        'per-hour-5000': 0,
                        'last-time': time.time(),
                        'last-score': 0,
                        'time-history': [],
                        'score-history': []
                    }
                if recorded_posts[item.name]['last-score'] > 0:
                    score_diff = item.score - recorded_posts[item.name]['last-score']
                    time_diff = time.time() - recorded_posts[item.name]['last-time']
                    score_per_sec = score_diff / time_diff
                    score_per_hour = score_per_sec * 60 * 60
                    score_per_hour = int(round(score_per_hour))
                    if score_per_hour > 250 and recorded_posts[item.name]['per-hour-250'] == 0:
                        pretext = 'This submission is getting at least 250 net upvotes per hour'
                        text = 'It could quickly become a popular post'
                        color = 'warning'
                        channel = self.settings.SLACK_SUBREDDIT_CHANNEL
                        recorded_posts[item.name]['per-hour-250'] = 1
                    if score_per_hour > 500 and recorded_posts[item.name]['per-hour-500'] == 0:
                        pretext = 'This submission is getting at least 500 net upvotes per hour'
                        text = 'It will quickly become a popular post'
                        color = 'warning'
                        channel = self.settings.SLACK_SUBREDDIT_CHANNEL
                        recorded_posts[item.name]['per-hour-500'] = 1
                    if score_per_hour > 1000 and recorded_posts[item.name]['per-hour-1000'] == 0:
                        pretext = 'This submission is getting at least 1000 net upvotes per hour'
                        text = 'It could quickly reach r/all'
                        color = 'warning'
                        channel = self.settings.SLACK_SUBREDDIT_CHANNEL
                        recorded_posts[item.name]['per-hour-1000'] = 1
                    if score_per_hour > 2500 and recorded_posts[item.name]['per-hour-2500'] == 0:
                        pretext = 'This submission is getting at least 2500 net upvotes per hour'
                        text = 'It will quickly reach r/all'
                        color = 'warning'
                        channel = self.settings.SLACK_SUBREDDIT_CHANNEL
                        recorded_posts[item.name]['per-hour-2500'] = 1
                    if score_per_hour > 5000 and recorded_posts[item.name]['per-hour-5000'] == 0:
                        pretext = 'This submission is getting at least 5000 net upvotes per hour'
                        text = 'It could quickly reach the front page of r/all'
                        color = 'danger'
                        channel = self.settings.SLACK_DANGER_CHANNEL
                        recorded_posts[item.name]['per-hour-5000'] = 1
                    if pretext is not None and text is not None and color is not None and channel is not None:
                        fields = [
                            {
                                'title': 'Upvotes Per Hour',
                                'value': score_per_hour,
                                'short': True
                            }
                        ]
                        self.webHook.post_complex_link(username=item.author.name, title=item.title,
                                                       permalink=item.permalink, pretext=pretext,
                                                       text=text, fields=fields, color=color, channel=channel)
                    recorded_posts[item.name]['time-history'].append(recorded_posts[item.name]['last-time'])
                    recorded_posts[item.name]['score-history'].append(recorded_posts[item.name]['last-score'])
                recorded_posts[item.name]['last-time'] = time.time()
                recorded_posts[item.name]['last-score'] = item.score
            time.sleep(60)
