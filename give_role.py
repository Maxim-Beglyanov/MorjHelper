from datetime import date

import hikari
import crescent
import miru

from database import database


plugin = crescent.Plugin()

count = 10
def add_type_roles(cls):
    for i in range(1, count+1):
        role_name = 'role_'+str(i)
        setattr(cls, role_name, crescent.option(hikari.Role, name=role_name, default=None))
        emoji_name = 'emoji_'+str(i)
        setattr(cls, emoji_name, crescent.option(str, name=emoji_name, default=''))
    return cls

@plugin.include
@crescent.command(name='setup-give-role')
@add_type_roles
class SetupGiveRole:
    async def callback(self, ctx: crescent.Context):
        view = miru.View()
        roles = []
        for i in range(1, count+1):
            if role := getattr(self, 'role_'+str(i)):
                emoji = getattr(self, 'emoji_'+str(i))
                view.add_item(miru.Button(label=role.name, emoji=emoji, custom_id=str(i)))
                roles.append((i, role.id))
        message = await ctx.respond('Выберите роль', ensure_message=True, components=view)
        database.insert(
                'give_role_channels',
                channel_id=message.channel_id, 
                message_id=message.id
        )
        database.insert('give_roles', [(message.id, i, role_id) for i, role_id in roles], many=True)
        await view.start(message)
        view.stop()

async def on_interaction(specialty_role_id, interaction: hikari.ComponentInteraction):
    roles = set(interaction.member.get_roles())
    guild = interaction.get_guild()
    if (specialty_role := guild.get_role(specialty_role_id)) in roles:
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, 
            f'Вы имеете роль {specialty_role.name}',
            flags=hikari.MessageFlag.EPHEMERAL
        )
        return
    if give_time := database.select(
        'given_user_roles', 'give_time',
        give_role_message_id=interaction.message.id,
        user_id=interaction.user.id
    ):
        give_time = date.fromisoformat(give_time[0][0])
        days = (date.today()-give_time).days
        if days >= 7:
            database.delete(
                    'given_user_roles', 
                    give_role_message_id=interaction.message.id, 
                    user_id=interaction.user.id
            )
        else:
            await interaction.create_initial_response(
                    hikari.ResponseType.MESSAGE_CREATE,
                    f'Вы не можете поменять роль еще {7-days} дней',
                    flags=hikari.MessageFlag.EPHEMERAL
            )
            return

    for role in database.select(
            'give_roles', 'role_id button_id',
            give_role_message_id=interaction.message.id
    ):
        button_id = role[1]
        role = guild.get_role(role[0])
        if interaction.custom_id == button_id:
            roles.add(role)
        else:
            roles.discard(role)
    await interaction.app.rest.edit_member(guild.id, interaction.user, roles=roles)
    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE, 
        'Роль выдана', flags=hikari.MessageFlag.EPHEMERAL
    )
    database.insert(
        'given_user_roles', 
        give_role_message_id=interaction.message.id, 
        user_id=interaction.user.id, 
        give_time=date.today()
    )
