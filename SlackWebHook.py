
import requests
import json


class WebHook(object):
    def __init__(self, settings):
        """

        :param settings:
        :type settings: settings
        """
        self.hooks = settings.SLACK_CHANNEL_LIST
        self.bot_name = settings.BOT_NAME

    def post_status(self, pretext, text, channel):
        payload = {
            "attachments": [
                {
                    "pretext": pretext,
                    "text": text,
                    "color": "good",
                    "mrkdwn_in": ["pretext", "text", "fields"],
                    "footer": "Provided By "+self.bot_name
                }
            ]
        }
        payload_json = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payload_json, headers=headers)

    def post_warning(self, pretext, text, channel):
        payload = {
            "attachments": [
                {
                    "pretext": pretext,
                    "text": text,
                    "color": "warning",
                    "mrkdwn_in": ["pretext", "text", "fields"],
                    "footer": "Provided By "+self.bot_name
                }
            ]
        }
        payload_json = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payload_json, headers=headers)

    def post_danger(self, pretext, text, channel):
        payload = {
            "attachments": [
                {
                    "pretext": pretext,
                    "text": text,
                    "color": "danger",
                    "mrkdwn_in": ["pretext", "text", "fields"],
                    "footer": "Provided By "+self.bot_name
                }
            ]
        }
        payload_json = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payload_json, headers=headers)

    def post_user_link(self, username, pretext, text, color, channel):
        payload = {
            "attachments": [
                {
                    "author_name": username,
                    "author_link": "https://www.reddit.com/user/" + username,
                    "pretext": pretext,
                    "text": text,
                    "color": color,
                    "mrkdwn_in": ["pretext", "text", "fields"],
                    "footer": "Provided By "+self.bot_name
                }
            ]
        }
        payload_json = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payload_json, headers=headers)

    def post_user_link_with_fields(self, username, pretext, text, color, channel, fields):
        payload = {
            "attachments": [
                {
                    "author_name": username,
                    "author_link": "https://www.reddit.com/user/" + username,
                    "pretext": pretext,
                    "text": text,
                    "fields": fields,
                    "color": color,
                    "mrkdwn_in": ["pretext", "text", "fields"],
                    "footer": "Provided By "+self.bot_name
                }
            ]
        }
        payload_json = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payload_json, headers=headers)

    def post_submission_link(self, username, title, permalink, pretext, color, channel):
        payload = {
            "attachments": [
                {
                    "author_name": username,
                    "author_link": "https://www.reddit.com/user/" + username,
                    "title": title,
                    "title_link": 'https://www.reddit.com' + permalink,
                    "pretext": pretext,
                    "color": color,
                    "mrkdwn_in": ["pretext", "text", "fields"],
                    "footer": "Provided By "+self.bot_name
                }
            ]
        }
        payload_json = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payload_json, headers=headers)

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
                    "color": color,
                    "mrkdwn_in": ["pretext", "text", "fields"],
                    "footer": "Provided By "+self.bot_name
                }
            ]
        }
        payload_json = json.dumps(payload)
        headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
        requests.post(self.hooks[channel], data=payload_json, headers=headers)
