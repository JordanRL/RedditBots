import time


class Attachment:
    def __init__(self, text, fallback):
        self.pretext = None
        self.text = text
        self.fallback = fallback
        self.color = None
        self.author_name = None
        self.author_link = None
        self.author_icon = None
        self.title = None
        self.title_link = None
        self.image_url = None
        self.thumb_url = None
        self.footer = None
        self.footer_icon = None
        self.ts = time.time()
        self.fields = []
        self.actions = []

    def set_link(self, title, url):
        self.title = title
        self.title_link = url
        return self

    def set_author(self, author_name, author_link=None, author_icon=None):
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon
        return self

    def set_content(self, text, pretext=None, fallback=None):
        self.text = text
        self.pretext = pretext
        self.fallback = fallback
        return self

    def set_color(self, color):
        self.color = color
        return self

    def set_image(self, image, thumb=None):
        self.image_url = image
        self.thumb_url = thumb
        return self

    def set_footer(self, footer, icon=None):
        self.footer = footer
        self.footer_icon = icon
        return self

    def add_field(self, title, value, short=True):
        self.fields.append({
            "title": title,
            "value": value,
            "short": short
        })
        return self

    def add_action(self, name, text, type, value, style=None, confirm=None):
        action = {
            "name": name,
            "text": text,
            "type": type,
            "value": value
        }
        if style is not None:
            action["style"] = style
        if confirm is not None:
            if "title" in confirm and "text" in confirm and "ok_text" in confirm and "dismiss_text" in confirm:
                action["confirm"] = confirm
        self.actions.append(action)
        return self

    def can_transport(self):
        if self.pretext != "" and self.text != "":
            return True
        else:
            return False

    def transport(self):
        attachment = {
            "text": self.text,
            "fallback": self.fallback,
            "mrkdwn_in": ["pretext", "text", "fields"]
        }

        if self.pretext is not None:
            attachment['pretext'] = self.pretext
        if self.color is not None:
            attachment['color'] = self.color
        if self.author_name is not None:
            attachment['author_name'] = self.author_name
        if self.author_link is not None:
            attachment['author_link'] = self.author_link
        if self.author_icon is not None:
            attachment['author_icon'] = self.author_icon
        if self.title is not None:
            attachment['title'] = self.title
        if self.title_link is not None:
            attachment['title_link'] = self.title_link
        if self.image_url is not None:
            attachment['image_url'] = self.image_url
        if self.thumb_url is not None:
            attachment['thumb_url'] = self.thumb_url
        if self.footer is not None:
            attachment['footer'] = self.footer
        if self.footer_icon is not None:
            attachment['footer_icon'] = self.footer_icon
        if len(self.fields) > 0:
            attachment['fields'] = self.fields
        if len(self.actions) > 0:
            attachment['actions'] = self.actions

        return attachment
