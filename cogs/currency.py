from main import GamBot
from discord.ext import (
    commands
)
from discord import (
    app_commands,
    Interaction,
    User
)
from math import floor
from random import randint


class Currency(commands.Cog):
    def __init__(self, bot: GamBot):
        self.bot = bot

    @app_commands.command(name='balance', description='View your own or another user\'s $ balance.')
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

    @app_commands.command(name='gold', description='View your own or another user\'s gold balance.')
    @app_commands.describe(user='Whose gold would you like to view?')
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
            interaction, f'{user.mention}\'s total gold is `{(await self.bot.gold(user)):,}` Gold.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='xp', description='View your own or another user\'s XP count.')
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

        xp = await self.bot.xp(user)
        rank = await self.bot.rank(user)
        await self.bot.response(
            interaction, f'{user.mention}\'s total XP is `{xp:,} XP (rank {rank})`.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='gift', description='Gift some money to another user.')
    @app_commands.describe(user='Who would you like to gift money to?', amount='How much money would you like to give?')
    async def gift(self, interaction: Interaction, user: User, amount: int):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot or user == interaction.user:
            await self.bot.bad_response(interaction, '❌ Pick another user.')
            return
        elif not 1 <= amount <= await self.bot.money(interaction.user):
            await self.bot.bad_response(interaction, '❌ Pick a valid, affordable amount of money.')
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=amount * -1)
        await self.bot.edit_balances(interaction, user, money_d=amount)

        await self.bot.response(
            interaction, f'***Gifted `${amount:,}` to {user.mention}!***', self.bot.colour(interaction.guild))

    @app_commands.command(name='daily', description='Claim your daily reward!')
    async def daily(self, interaction: Interaction):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif await self.bot.daily_claimed(interaction.user):
            await self.bot.bad_response(interaction, '❌ You\'ve already claimed today\'s daily reward.')
            return

        cons_dailies = await self.bot.cons_dailies(interaction.user)
        money = floor(randint(25000, 30000) * await self.bot.pay_mult(interaction.user) * (1.01 ** cons_dailies))
        xp = floor(randint(500, 750) * await self.bot.xp_mult(interaction.user) * (1.01 ** cons_dailies))
        await self.bot.edit_balances(interaction, interaction.user, money_d=money, xp_d=xp)
        await self.bot.add_daily(interaction.user)

        await self.bot.response(
            interaction, f'***Claimed `${money:,}` and `{xp:,} XP`!***', self.bot.colour(interaction.guild))


async def setup(bot: GamBot):
    await bot.add_cog(Currency(bot))
