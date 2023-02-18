from main import GamBot
from discord.ext import (
    commands
)
from discord import (
    app_commands,
    Interaction,
    User,
    Embed
)
from datetime import timedelta
from time import time
from math import floor
import logging


class Utility(commands.Cog):
    def __init__(self, bot: GamBot):
        self.bot = bot
        self.time = time()

    @app_commands.command(name='ping', description='Check the bot\'s current latency.')
    async def ping(self, interaction: Interaction):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        await self.bot.response(
            interaction, f'***Pong! Latency: `{round(self.bot.latency, 3)}s`***', self.bot.colour(interaction.guild))

    @app_commands.command(name='uptime', description='Check the bot\'s current uptime.')
    async def uptime(self, interaction: Interaction):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        await self.bot.response(interaction,
                                f'***Current uptime: `{timedelta(seconds=floor(time() - self.time))}`***\n\n'
                                f'***Online since: <t:{floor(self.time)}:F>***', self.bot.colour(interaction.guild))

    @app_commands.command(name='help', description='View information on GamBot\'s commands and features.')
    async def help(self, interaction: Interaction, command: str = None):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif command and command not in [cmd.name for cmd in self.bot.app_commands]:
            await self.bot.bad_response(interaction, f'❌ Command `{command}` not found.')
            return

        if command:
            app_command = [cmd for cmd in self.bot.app_commands if cmd.name == command][0]

            help_embed = Embed(
                colour=self.bot.colour(interaction.guild),
                title=f'{app_command.name.capitalize()} Command',
                description=app_command.mention)
            help_embed.set_author(name='GamBot Help Menu', icon_url=self.bot.user.avatar)
            help_embed.set_footer(text='Use /help to view all commands.')
            help_embed.add_field(name='Description', value=app_command.description,  inline=False)

            opt_map = {True: '', False: 'opt'}
            help_embed.add_field(
                name='Usage',
                value=f'`/{app_command.name} '
                      f'{" ".join([f"{opt_map[option.required]}<{option.name}>" for option in app_command.options])}`',
                inline=False)

        else:
            help_embed = Embed(
                colour=self.bot.colour(interaction.guild),
                title='All Commands')
            help_embed.set_author(name='GamBot Help Menu', icon_url=self.bot.user.avatar)
            help_embed.set_footer(text='Use /help <command> for more info on a single command.')

            for cog in self.bot.cogs:
                cog_app_commands = self.bot.get_cog(cog).get_app_commands()
                app_cmds = [cmd for cmd in self.bot.app_commands if cmd.name in [c.name for c in cog_app_commands]]
                help_embed.add_field(name=cog, value=" ".join([cmd.mention for cmd in app_cmds]), inline=False)

        await interaction.response.send_message(embed=help_embed, ephemeral=True)

    @help.autocomplete('command')
    async def help_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        item_list = []
        for item in [cmd.name for cmd in self.bot.app_commands]:
            if current.lower() in item.lower() and len(item_list) < 25:
                item_list.append(app_commands.Choice(name=item, value=item))
        return item_list

    @app_commands.command(name='editbal', description='Edit another user\'s money, gold or XP balance.')
    @app_commands.describe(user='Whose balance do you want to edit?')
    @app_commands.describe(bal_type='Which balance type do you wish to edit?')
    @app_commands.describe(amount='By how much do you wish to edit this user\'s balance?')
    @app_commands.choices(bal_type=[app_commands.Choice(name='Money', value='Money'),
                                    app_commands.Choice(name='Gold', value='Gold'),
                                    app_commands.Choice(name='XP', value='XP')])
    async def editbal(self, interaction: Interaction, user: User, bal_type: app_commands.Choice[str], amount: int):
        if interaction.user.id not in self.bot.owner_ids:
            await self.bot.bad_response(interaction, '❌ This command is owner-only.')
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ This user is a bot.')
            return

        await self.bot.edit_balances(
            interaction, user,
            money_d=amount if bal_type.name == "Money" else 0,
            gold_d=amount if bal_type.name == "Gold" else 0,
            xp_d=amount if bal_type.name == "XP" else 0)
        await self.bot.response(
            interaction, f'Edited {user.mention}\'s balance by `{"$" if bal_type.name == "Money" else ""}{amount:,}'
                         f'{f" {bal_type.name}" if bal_type.name != "Money" else ""}`.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='editinv', description='Edit another user\'s GamBot inventory.')
    @app_commands.describe(user='Whose inventory do you want to edit?')
    @app_commands.describe(item_type='Which item type do you wish to edit?')
    @app_commands.describe(amount='By how much do you wish to edit this user\'s item count?')
    @app_commands.choices(item_type=[app_commands.Choice(name='Small Money Pack', value='Small Money Pack'),
                                     app_commands.Choice(name='Medium Money Pack', value='Medium Money Pack'),
                                     app_commands.Choice(name='Large Money Pack', value='Large Money Pack'),
                                     app_commands.Choice(name='Small Gold Pack', value='Small Gold Pack'),
                                     app_commands.Choice(name='Medium Gold Pack', value='Medium Gold Pack'),
                                     app_commands.Choice(name='Large Gold Pack', value='Large Gold Pack'),
                                     app_commands.Choice(name='Jackpot Pack', value='Jackpot Pack'),
                                     app_commands.Choice(name='Common Payout Booster', value='Common Payout Booster'),
                                     app_commands.Choice(name='Rare Payout Booster', value='Rare Payout Booster'),
                                     app_commands.Choice(name='Epic Payout Booster', value='Epic Payout Booster'),
                                     app_commands.Choice(name='Common XP Booster', value='Common XP Booster'),
                                     app_commands.Choice(name='Rare XP Booster', value='Rare XP Booster'),
                                     app_commands.Choice(name='Epic XP Booster', value='Epic XP Booster')
                                     ])
    async def editinv(self, interaction: Interaction, user: User, item_type: app_commands.Choice[str], amount: int):
        if interaction.user.id not in self.bot.owner_ids:
            await self.bot.bad_response(interaction, '❌ This command is owner-only.')
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ This user is a bot.')
            return

        await self.bot.edit_inventory(user, item_type.name, amount)
        await self.bot.response(
            interaction, f'Edited {user.mention}\'s inventory by `{amount}x {item_type.name}`.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='addpremium', description='Give another user GamBot premium.')
    @app_commands.describe(user='Who would you like to give premium to?')
    @app_commands.describe(duration='How long would you like them to have premium for?')
    async def addpremium(self, interaction: Interaction, user: User, duration: str):
        if interaction.user.id not in self.bot.owner_ids:
            await self.bot.bad_response(interaction, '❌ This command is owner-only.')
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ This user is a bot.')
            return

        try:
            duration_mapping = {'m': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'y': 31536000}
            resolved_duration = int(duration[:-1]) * duration_mapping[duration[-1:].lower()]
        except (KeyError, ValueError):
            resolved_duration = 0
        if not 60 <= resolved_duration:
            await self.bot.bad_response(interaction, '❌ Please specify a valid duration')
            return

        await self.bot.add_premium(user, resolved_duration)
        await self.bot.response(
            interaction, f'Gave `{timedelta(seconds=resolved_duration)}` of premium to {user.mention}.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='blacklist', description='Toggles the blacklisting of a GamBot user.')
    @app_commands.describe(user='Who would you like to blacklist?')
    async def blacklist(self, interaction: Interaction, user: User):
        if interaction.user.id not in self.bot.owner_ids:
            await self.bot.bad_response(interaction, '❌ This command is owner-only.')
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ This user is a bot.')
            return

        await self.bot.toggle_blacklist(user)
        await self.bot.response(
            interaction, f'{user.mention} has been {"" if await self.bot.is_blacklisted(user) else "un"}blacklisted.',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='wipedata', description='Wipes the specified user\'s GamBot data.')
    @app_commands.describe(user='Whose data do you want to wipe?')
    async def wipedata(self, interaction: Interaction, user: User):
        if interaction.user.id not in self.bot.owner_ids:
            await self.bot.bad_response(interaction, '❌ This command is owner-only.')
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ This user is a bot.')
            return

        await self.bot.wipe(user.id)
        await self.bot.response(
            interaction, f'Successfully wiped {user.mention}\'s data.', self.bot.colour(interaction.guild))

    @app_commands.command(name='terminate', description='Terminates the bot process.')
    async def terminate(self, interaction: Interaction):
        if interaction.user.id not in self.bot.owner_ids:
            await self.bot.bad_response(interaction, '❌ This command is owner-only.')
            return
        logging.info('Received signal to terminate bot and event loop.')
        await self.bot.response(interaction, 'Bot process terminated.', self.bot.colour(interaction.guild))
        await self.bot.close()


async def setup(bot: GamBot):
    await bot.add_cog(Utility(bot))
