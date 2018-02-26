import json
import os
from slackclient import SlackClient


class SlackAPI:
    def __init__(self, settings, channels, users):
        self.client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        self.settings = settings
        self.channels = channels
        self.users = users

    def interactive_message(self, attachments, fields, actions):
        self.client.api_call(
            'chat.postMessage',
            attachments=attachments
        )
