
import requests
import json


class WebHook(object):
    def __init__(self):
        super(WebHook, self).__init__()
        self.hooks = {
            "bot-notifications": "https://hooks.slack.com/services/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",
            "danger-room": "https://hooks.slack.com/services/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"
        }

    def post_status(self, pretext, text, channel):
        payload = {
            "attachments": [
                {
                    "pretext": pretext,
                    "text": text,
                    "color": "good"
                }
            ]
        }
        payloadJSON = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payloadJSON, headers=headers)

    def post_warning(self, pretext, text, channel):
        payload = {
            "attachments": [
                {
                    "pretext": pretext,
                    "text": text,
                    "color": "warning"
                }
            ]
        }
        payloadJSON = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payloadJSON, headers=headers)

    def post_danger(self, pretext, text, channel):
        payload = {
            "attachments": [
                {
                    "pretext": pretext,
                    "text": text,
                    "color": "danger"
                }
            ]
        }
        payloadJSON = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payloadJSON, headers=headers)

    def post_user_link(self, username, pretext, text, color, channel):
        payload = {
            "attachments": [
                {
                    "author_name": username,
                    "author_link": "https://www.reddit.com/user/" + username,
                    "pretext": pretext,
                    "text": text,
                    "color": color
                }
            ]
        }
        payloadJSON = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payloadJSON, headers=headers)

    def post_submission_link(self, username, title, permalink, pretext, color, channel):
        payload = {
            "attachments": [
                {
                    "author_name": username,
                    "author_link": "https://www.reddit.com/user/" + username,
                    "title": title,
                    "title_link": 'https://www.reddit.com' + permalink,
                    "pretext": pretext,
                    "color": color
                }
            ]
        }
        payloadJSON = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payloadJSON, headers=headers)

    def post_complex_link(self, username, title, permalink, pretext, text, fields, color, channel):
        payload = {
            "attachments": [
                {
                    "author_name": username,
                    "author_link": "https://www.reddit.com/user/" + username,
                    "title": title,
                    "title_link": 'https://www.reddit.com' + permalink,
                    "pretext": pretext,
                    "text": text,
                    "fields": fields,
                    "color": color
                }
            ]
        }
        payloadJSON = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payloadJSON, headers=headers)
