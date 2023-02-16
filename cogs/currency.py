from discord.ext import (
    commands
)
from discord import (
    app_commands,
    Interaction,
    User
)
from main import GamBot


class Currency(commands.Cog):
    def __init__(self, bot: GamBot):
        self.bot = bot

    @app_commands.command(name='balance', description='View your own or another user\'s GamBot $ balance.')
    @app_commands.describe(user='Whose balance would you like to view?')
    async def balance(self, interaction: Interaction, user: User = None):
        if not user:
            user = interaction.user
        elif await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ That user is a bot.')
            return

        await self.bot.response(
            interaction, f'{user.mention}\'s total balance is `${(await self.bot.money(user)):,}`.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='gold', description='View your own or another user\'s GamBot gold balance.')
    @app_commands.describe(user='Whose gold balance would you like to view?')
    async def gold(self, interaction: Interaction, user: User = None):
        if not user:
            user = interaction.user
        elif await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ That user is a bot.')
            return

        await self.bot.response(
            interaction, f'{user.mention}\'s total gold balance is `{(await self.bot.gold(user)):,}`.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='xp', description='View your own or another user\'s GamBot XP count.')
    @app_commands.describe(user='Whose XP count would you like to view?')
    async def xp(self, interaction: Interaction, user: User = None):
        if not user:
            user = interaction.user
        elif await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ That user is a bot.')
            return

        await self.bot.response(
            interaction, f'{user.mention}\'s total XP is `{(await self.bot.xp(user)):,}`.',
            self.bot.colour(interaction.guild))


async def setup(bot: GamBot):
    await bot.add_cog(Currency(bot))
