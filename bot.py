import os

import hikari
import miru
import crescent

from database import database
import offer_event
import give_role


TOKEN = os.environ['DISCORD_TOKEN']
bot = crescent.Bot(TOKEN)
miru.install(bot)

bot.plugins.load('text_help')
bot.plugins.load('offer_event')
bot.plugins.load('give_role')

@bot.include
@crescent.command(name='config-embed-color')
class ConfigEmbedColor:
    color = crescent.option(str, description='Цвет, используемый в сообщениях')
    async def callback(self, ctx: crescent.Context):
        database.update('config', embed_color=self.color)
        await ctx.respond('Конфигурация обновлена', flags=hikari.MessageFlag.EPHEMERAL)


@bot.include
@crescent.event
async def on_interaction(event: hikari.InteractionCreateEvent):
    interaction = event.interaction
    if not isinstance(interaction, hikari.ComponentInteraction):
        return

    if category := database.select(
            'offer_channels', 'category_id',
            channel_id=interaction.message.channel_id,
            message_id=interaction.message.id
    ):
        await offer_event.on_interaction(category[0][0], interaction)
    elif database.select(
            'give_role_channels', 
            channel_id=interaction.message.channel_id, 
            message_id=interaction.message.id
    ):
        await give_role.on_interaction(interaction)


database.check_db_exists()
bot.run()
