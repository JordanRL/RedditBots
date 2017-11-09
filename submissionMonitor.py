import praw
import settings
import requests
import json

reddit = praw.Reddit(client_id=settings.REDDIT_CLIENT_ID,
                     client_secret=settings.REDDIT_CLIENT_SECRET,
                     password=settings.REDDIT_PASSWORD,
                     username=settings.REDDIT_USERNAME,
                     user_agent=settings.REDDIT_USER_AGENT)

subredditMulti = reddit.subreddit('The_Donald+Enough_Sanders_Spam+WayOfTheBern')

firstPass = 1

print('Starting Script')

for submission in subredditMulti.stream.submissions():
    if firstPass:
        print('Inside the stream')
        headersStart = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        urlStart = 'https://hooks.slack.com/services/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'
        messageStart = 'Brigade Monitor now watching these subreddits for submissions: The_Donald, Enough_Sanders_Spam, WayOfTheBern'
        payloadStartObj = {"attachments": [{"text": messageStart, "color": "good"}]}
        payloadStart = json.dumps(payloadStartObj)
        requests.post(urlStart, data=payloadStart, headers=headersStart)
        firstPass = 0
    theText = submission.url.lower()
    if settings.REDDIT_SUBREDDIT in theText:
        print('Found Match')
        message = 'Likely Brigading From /r/' + submission.subreddit.display_name
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        url = 'https://hooks.slack.com/services/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'
        payloadObj = {"attachments":
            [
                {
                    "pretext": message,
                    "color": "danger",
                    "author_name": submission.author.name,
                    "author_link": "https://www.reddit.com/user/" + submission.author.name,
                    "title": submission.title,
                    "title_link": 'https://www.reddit.com' + submission.permalink
                }
            ]
        }
        payload = json.dumps(payloadObj)
        requests.post(url, data=payload, headers=headers)
