import os
from slackclient import SlackClient
from attachmentBuilder import Attachment


class SlackMessenger:
    def __init__(self, slack_client: SlackClient=None):
        if slack_client is None:
            self.client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
        else:
            self.client = slack_client
        self.channel = None
        self.text = None
        self.attachments = []
        self.as_user = None
        self.icon_emoji = None
        self.icon_url = None
        self.link_names = None
        self.mrkdwn = None
        self.parse = None
        self.reply_broadcast = None
        self.thread_ts = None
        self.unfurl_links = None
        self.unfurl_media = None
        self.username = None

    def set_channel(self, channel):
        self.channel = channel
        return self

    def set_text(self, text):
        self.text = text
        return self

    def add_attachment(self, attachment: Attachment):
        self.attachments.append(attachment.transport())
        return self

    def post_attachment(self, attachment: Attachment, channel):
        self.attachments = [
            attachment.transport()
        ]
        return self.set_channel(channel).send_message()

    def post_reply(self, channel, thread_ts, text=None, attachment: Attachment=None):
        self.thread_ts = thread_ts
        if text is not None:
            self.set_text(text)
        if attachment is not None:
            self.add_attachment(attachment)
        return self.set_channel(channel).send_message()

    def send_message(self):
        if self.text is None and len(self.attachments) == 0:
            return False
        if self.channel is None:
            return False
        api_args = {
            "channel": self.channel
        }
        if self.text is not None:
            api_args["text"] = self.text
        if len(self.attachments) > 0:
            api_args["attachments"] = self.attachments
        result = self.client.api_call(
            'chat.postMessage',
            **api_args
        )
        self.reset_self()
        if result["ok"]:
            return True
        else:
            return False

    def reset_self(self):
        self.channel = None
        self.text = None
        self.attachments = []
        self.as_user = None
        self.icon_emoji = None
        self.icon_url = None
        self.link_names = None
        self.mrkdwn = None
        self.parse = None
        self.reply_broadcast = None
        self.thread_ts = None
        self.unfurl_links = None
        self.unfurl_media = None
        self.username = None
