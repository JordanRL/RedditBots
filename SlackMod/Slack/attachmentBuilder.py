import time


class Attachment:
    def __init__(self, text, fallback):
        self.pretext = ""
        self.text = text
        self.fallback = fallback
        self.color = ""
        self.author_name = ""
        self.author_link = ""
        self.author_icon = ""
        self.title = ""
        self.title_link = ""
        self.image_url = ""
        self.thumb_url = ""
        self.footer = ""
        self.footer_icon = ""
        self.ts = time.time()
        self.fields = []

    def link(self, title, url):
        self.title = title
        self.title_link = url

    def author(self, author_name, author_link="", author_icon=""):
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon

    def content(self, text, pretext="", fallback=""):
        self.text = text
        self.pretext = pretext
        self.fallback = fallback

    def color(self, color):
        self.color = color

    def image(self, image, thumb=""):
        self.image_url = image
        self.thumb_url = thumb

    def footer(self, footer, icon=""):
        self.footer = footer
        self.footer_icon = icon

    def add_field(self, title, value, short=True):
        self.fields.append({
            "title": title,
            "value": value,
            "short": short
        })

    def can_transport(self):
        if self.pretext != "" and self.text != "":
            return True
        else:
            return False

    def transport(self):
        attachment = {
            "text": self.text,
            "fallback": self.fallback
        }

        if self.pretext:
            attachment['pretext'] = self.pretext
        if self.color:
            attachment['color'] = self.color
        if self.author_name:
            attachment['author_name'] = self.author_name
        if self.author_link:
            attachment['author_link'] = self.author_link
        if self.author_icon:
            attachment['author_icon'] = self.author_icon
        if self.title:
            attachment['title'] = self.title
        if self.title_link:
            attachment['title_link'] = self.title_link
        if self.image_url:
            attachment['image_url'] = self.image_url
        if self.thumb_url:
            attachment['thumb_url'] = self.thumb_url
        if self.footer:
            attachment['footer'] = self.footer
        if self.footer_icon:
            attachment['footer_icon'] = self.footer_icon
        if len(self.fields) > 0:
            attachment['fields'] = self.fields

        return attachment
