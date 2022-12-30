import hikari

from database import database


class MyEmbed(hikari.Embed):
    def __init__(self, *, title, description, user: hikari.User):
        color = database.select('config', 'embed_color')[0][0]
        super().__init__(title=title, description=description, color=color)
        if user:
            self.set_author(name=user.username, icon=user.make_avatar_url())
