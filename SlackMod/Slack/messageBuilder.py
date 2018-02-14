import attachmentBuilder
import json


class Message:
    def __init__(self):
        self.attachment = attachmentBuilder.Attachment(text="", fallback="")
        self.text = ""
        self.colorPicker = {
            "good": "good",
            "warning": "warning",
            "danger": "danger",
            "grey": "#AAAAAA",
            "blue": "#4B6BFF"
        }

    def attach(self):
        return self.attachment

    def set_color(self, color):
        if color in self.colorPicker:
            self.attachment.color(color=self.colorPicker[color])
        else:
            self.attachment.color(color=color)

    def compile(self):
        message = {}

        if self.text != "":
            message['text'] = self.text
        if self.attachment.can_transport():
            message['attachment'] = self.attachment.transport()

        compiled_message = json.dumps(message)

        return compiled_message
