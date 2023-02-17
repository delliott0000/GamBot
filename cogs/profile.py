from main import GamBot
from discord.ext import (
    commands
)
from discord import (
    app_commands,
    Interaction,
    User,
    Embed,
    HTTPException,
    NotFound
)
from config import (
    rank_mapping,
    achievements_mapping,
)
from math import floor, sqrt


class Profile(commands.Cog):
    def __init__(self, bot: GamBot):
        self.bot = bot

    @app_commands.command(name='profile', description='View your own or another user\'s GamBot profile.')
    @app_commands.describe(user='Whose profile would you like to view?')
    async def profile(self, interaction: Interaction, user: User = None):
        if not user:
            user = interaction.user
        elif await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ That user is a bot.')
            return

        profile_embed = Embed(colour=self.bot.colour(interaction.guild), description=user.mention)
        profile_embed.set_author(name='GamBot Profile', icon_url=self.bot.user.avatar)
        profile_embed.set_thumbnail(url=user.avatar if user.avatar else user.default_avatar)

        profile_embed.add_field(name='💸 Total Money:',
                                value=f'> `${await self.bot.money(user):,}`')
        profile_embed.add_field(name='<:gold:1058395878190223380> Total Gold:',
                                value=f'> `{await self.bot.gold(user):,}`')
        profile_embed.add_field(name='♦ Total XP:',
                                value=f'> `{await self.bot.xp(user):,}`')

        rank = await self.bot.rank(user)
        try:
            profile_embed.add_field(
                name='🥇 Rank:', value=f'> `Rank {rank} ({rank_mapping[rank]})`', inline=False)
        except KeyError:
            profile_embed.add_field(
                name='🥇 Rank:', value=f'> `Rank {rank} (Legend)`', inline=False)

        profile_embed.add_field(
            name='🎲 Payout Multiplier:', value=f'> `x{round(await self.bot.pay_mult(user), 2)}`', inline=True)
        profile_embed.add_field(
            name='💡 XP Multiplier:', value=f'> `x{round(await self.bot.xp_mult(user), 2)}`', inline=True)

        profile_embed.add_field(name='💎 Premium:',
                                value=f'> `{await self.bot.has_premium(user)}`', inline=False)
        profile_embed.add_field(name='📅 Daily Claimed:',
                                value=f'> `{await self.bot.daily_claimed(user)}`', inline=True)
        profile_embed.add_field(name='📌 Consecutive Dailies:',
                                value=f'> `{await self.bot.cons_dailies(user):,}`', inline=True)

        await interaction.response.send_message(embed=profile_embed)

    @app_commands.command(name='achievements', description='View your own or another user\'s GamBot achievements.')
    @app_commands.describe(user='Whose achievements would you like to view?')
    async def achievements(self, interaction: Interaction, user: User = None):
        if not user:
            user = interaction.user
        elif await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ That user is a bot.')
            return

        data = await self.bot.achievements(user)

        achievements_embed = Embed(
            colour=self.bot.colour(interaction.guild),
            description=f'{user.mention} **(Total Achievements: `{len([a[1] for a in data.items() if a[1]])}/15`)**')
        achievements_embed.set_author(name='GamBot Achievements', icon_url=self.bot.user.avatar)

        for a in data:
            achievements_embed.add_field(
                name=achievements_mapping[a][0],
                value=f'> {achievements_mapping[a][1]}\n**Earned: {"🏆" if data[a] else "❌"}**')

        await interaction.response.send_message(embed=achievements_embed)

    @app_commands.command(name='leaderboard', description='View the richest and highest-ranking GamBot users!')
    @app_commands.describe(view='Which leaderboard would you like to view?')
    @app_commands.checks.cooldown(1, 60)
    @app_commands.choices(view=[
        app_commands.Choice(name='Money', value='Money'),
        app_commands.Choice(name='Gold', value='Gold'),
        app_commands.Choice(name='XP', value='XP')])
    async def leaderboard(self, interaction: Interaction, view: app_commands.Choice[str]):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        await interaction.response.defer(thinking=True)

        data = await self.bot.leaderboard(view.name)
        if len(data) > 10:
            data = data[:10]

        leaderboard_embed = Embed(colour=self.bot.colour(interaction.guild), description='**Top 10 Users**')
        leaderboard_embed.set_author(name=f'💎 👑 GamBot {view.name} Leaderboard 👑 💎', icon_url=self.bot.user.avatar)

        medals_mapping = {0: '🥇', 1: '🥈', 2: '🥉', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '', 9: ''}
        format_mapping = {'Money': ('$', ''), 'Gold': ('', ' Gold'), 'XP': ('', ' XP (Rank <rank>)')}

        for item in data:

            try:
                user = await self.bot.fetch_user(item[0])
            except (HTTPException, NotFound):
                user = '`UNKNOWN USER`'

            user_rank = floor(sqrt(item[1] / 8561) + 1)
            leaderboard_embed.add_field(
                name=f'#{data.index(item) + 1}: {user} {medals_mapping[data.index(item)]}',
                value=f'`{format_mapping[view.value][0]}{item[1]:,}'
                      f'{format_mapping[view.value][1]}`'.replace('<rank>', str(user_rank)),
                inline=False)

        await interaction.edit_original_response(embed=leaderboard_embed)


async def setup(bot: GamBot):
    await bot.add_cog(Profile(bot))
