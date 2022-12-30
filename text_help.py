import crescent

import views


plugin = crescent.Plugin()

@plugin.include
@crescent.command(name='send', description='Отправить сообщение')
class Send:
    title = crescent.option(str, description='Заголовок сообщения')
    description = crescent.option(str, description='Содержание сообщения')

    async def callback(self, ctx: crescent.Context):
        await ctx.respond(
                embed=views.MyEmbed(
                    title=self.title, description=self.description,
                    user=ctx.user
                )
        )
