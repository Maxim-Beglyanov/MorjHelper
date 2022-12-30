import hikari
import miru
import crescent

from database import database


plugin = crescent.Plugin()

@plugin.include
@crescent.command(name="setup-offer", description="Создать канал для создания предложений ивентов")
class SetupOffer:
    category = crescent.option(hikari.GuildCategory, description="Канал, в котором люди будут создавать временные каналы")
    title = crescent.option(str, description="Название канала")

    async def callback(self, ctx: crescent.Context):
        channel = await ctx.guild.create_text_channel(self.title, category=self.category.id)
        view = miru.View()
        view.add_item(miru.Button(label='Предложить ивент', style=hikari.ButtonStyle.SUCCESS))
        message = await channel.send(self.title, components=view)
        database.insert(
                'offer_channels', 
                category_id=self.category.id, channel_id=channel.id, message_id=message.id
        )
        await view.start(message)
        view.stop()
        await ctx.respond('Канал создан', flags=hikari.MessageFlag.EPHEMERAL)

async def on_interaction(category_id, specialty_role_id, interaction: hikari.ComponentInteraction):
    if database.select(
            'users_channels', 
            user_id=interaction.user.id, 
            offer_message_id=interaction.message.id
    ):
        await interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE, 
                'Вы уже создали канал',
                flags=hikari.MessageFlag.EPHEMERAL
        )
        return

    guild = interaction.get_guild()
    specialty_role = guild.get_role(specialty_role_id)
    everyone = None
    for role in guild.get_roles().values():
        if role.name == '@everyone':
            everyone = role
            break
    category = guild.get_channel(category_id)
    permissions = (
            hikari.Permissions.VIEW_CHANNEL
            | hikari.Permissions.SEND_MESSAGES
            | hikari.Permissions.MANAGE_MESSAGES
            | hikari.Permissions.MENTION_ROLES
    )
    permissions = (
            hikari.PermissionOverwrite(
                id=interaction.user.id,
                type=hikari.PermissionOverwriteType.MEMBER,
                allow=permissions
            ),
            hikari.PermissionOverwrite(
                id=specialty_role.id,
                type=hikari.PermissionOverwriteType.ROLE,
                allow=permissions
            ),
            hikari.PermissionOverwrite(
                id=everyone.id,
                type=hikari.PermissionOverwriteType.ROLE,
                deny=hikari.Permissions.VIEW_CHANNEL
            )
    )
    channel = await guild.create_text_channel(
            'предложение '+interaction.user.username, category=category,
            permission_overwrites=permissions
    )
    await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, 
            'Предложение создано', flags=hikari.MessageFlag.EPHEMERAL
    )
    await channel.send('@everyone', mentions_everyone=True)
    database.insert(
            'users_channels', 
            user_id=interaction.user.id, channel_id=channel.id,
            offer_message_id=interaction.message.id
    )

@plugin.include
@crescent.event
async def on_delete_channel(event: hikari.GuildChannelDeleteEvent):
    channel = event.channel
    database.delete('users_channels', channel_id=channel.id)
