import asyncio
import config
import logging
from typing import Union
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s (%(filename)s) - %(message)s')

try:
    from discord.ext import commands
    from discord import (
        __version__ as __discord__,
        Intents,
        Activity,
        ActivityType,
        Guild,
        Embed,
        Interaction,
        PrivilegedIntentsRequired,
        LoginFailure,
        NotFound
    )
    import aiosqlite
except ModuleNotFoundError:
    logging.fatal('Missing required dependencies.')
    exit(0)


class GamBot(commands.Bot):
    def __init__(self):
        super().__init__(
            intents=Intents.default(),
            command_prefix=None,
            help_command=None,
            activity=Activity(type=ActivityType.custom, name=config.ACTIVITY)
        )
        self.db = None

    @property
    def _token(self):
        return config.TOKEN

    @property
    def _colour_info(self):
        return hex(int(config.COLOUR_INFO, 16))

    @property
    def _colour_success(self):
        return hex(int(config.COLOUR_SUCCESS, 16))

    @property
    def _colour_error(self):
        return hex(int(config.COLOUR_ERROR, 16))

    def _bot_colour(self, guild: Union[Guild, None]):
        if guild:
            return guild.get_member(self.user.id).colour
        return 0xffffff

    async def format_db(self):
        await self.db.execute(
            'create table if not exists user_data (id integer, money integer, gold integer, xp integer, daily_claimed '
            'integer, cons_dailies integer, blacklisted integer, premium integer)')
        await self.db.execute(
            'create table if not exists inventories (user_id integer, money_pack_s integer, money_pack_m integer, '
            'money_pack_l integer, gold_pack_s integer, gold_pack_m integer, gold_pack_l integer, jackpot_pack integer,'
            ' payout_boost_c integer, payout_boost_r integer, payout_boost_e integer, xp_boost_c integer, xp_boost_r '
            'integer, xp_boost_e integer)')
        await self.db.execute(
            'create table if not exists achievements (user_id integer, bj_max integer, bj_sevens integer, rou_mil '
            'integer, rou_zero integer, poker_sf integer, poker_max integer, hl_max integer, hl_streak integer, '
            'slot_jack integer, spin_jack integer, lott_win integer, scratch_win integer, million integer, billion '
            'integer, legend integer)')
        await self.db.execute(
            'create table if not exists active_boosts (user_id integer, booster_type text, payout_mult numeric, xp_mult'
            ' numeric, lasts_until integer)')
        await self.db.execute(
            'create table if not exists daily_shop (item_1 text, item_2 text, item_3 text, item_4 text, item_5 text, '
            'item_6 text)')
        await self.db.commit()

    @staticmethod
    async def ephemeral_response(interaction: Interaction, reply: str, colour: int):
        await interaction.response.send_message(embed=Embed(colour=colour, description=reply), ephemeral=True)

    async def setup_hook(self) -> None:
        logging.info('Setting up database...')

        self.db = await aiosqlite.connect(Path(__file__).with_name('data.db'))
        await self.db.execute('PRAGMA journal_mode=wal')
        await self.format_db()

        logging.info(f'Logging in as {self.user} (ID: {self.user.id})...')

        try:
            self.owner_ids = set(int(user_id) for user_id in config.OWNERS.split(','))
            logging.info('Owners: ' + ''.join([(await self.fetch_user(user_id)).name for user_id in self.owner_ids]))
        except (ValueError, NotFound):
            logging.fatal('Unknown/invalid owner ID(s) passed.')
            exit(0)

    def run_bot(self):
        async def runner():
            async with self:
                try:
                    await self.start(self._token)
                except LoginFailure:
                    logging.fatal('Invalid token passed.')
                except PrivilegedIntentsRequired:
                    logging.fatal('Privileged intents are being requested that have not '
                                  'been explicitly enabled in the developer portal..')

        async def cancel_tasks():
            try:
                await self.db.commit()
                await self.db.close()
            except AttributeError:
                pass

        try:
            asyncio.run(runner())
        except (KeyboardInterrupt, SystemExit):
            logging.info("Received signal to terminate bot and event loop.")
        finally:
            logging.info('Cleaning up tasks and connections...')
            asyncio.run(cancel_tasks())
            logging.info('Done. Have a nice day!')


if __name__ == '__main__':

    if __discord__ == '2.1.0':
        bot = GamBot()
        bot.run_bot()

    else:
        logging.fatal('The incorrect version of discord.py has been installed.')
        logging.fatal('Current Version: {}'.format(__discord__))
        logging.fatal('Required: 2.1.0')
