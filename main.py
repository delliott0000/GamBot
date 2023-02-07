import asyncio
import config
import logging
from typing import Union
from pathlib import Path
from math import floor, sqrt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s (%(filename)s) - %(message)s')

try:
    from discord.ext import commands
    from discord import (
        __version__ as __discord__,
        utils,
        Intents,
        Activity,
        ActivityType,
        Guild,
        Embed,
        User,
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

    @staticmethod
    def _time_now():
        return floor(utils.utcnow().timestamp())

    @staticmethod
    async def ephemeral_response(interaction: Interaction, reply: str, colour: int):
        await interaction.response.send_message(embed=Embed(colour=colour, description=reply), ephemeral=True)

    async def format_db(self):
        await self.db.execute(
            'create table if not exists user_data (id integer, money integer, gold integer, xp integer, pay_mult real, '
            'xp_mult real, daily_claimed integer, cons_dailies integer, blacklisted integer, premium integer)')
        await self.db.execute(
            'create table if not exists inventories (id integer, money_pack_s integer, money_pack_m integer, '
            'money_pack_l integer, gold_pack_s integer, gold_pack_m integer, gold_pack_l integer, jackpot_pack integer,'
            ' pay_boost_c integer, pay_boost_r integer, pay_boost_e integer, xp_boost_c integer, xp_boost_r integer, '
            'xp_boost_e integer)')
        await self.db.execute(
            'create table if not exists achievements (id integer, bj_max integer, bj_sevens integer, rou_mil integer, '
            'rou_zero integer, poker_sf integer, poker_max integer, hl_max integer, hl_str integer, slot_jack integer, '
            'spin_jack integer, lott_win integer, scrat_win integer, mill integer, bill integer, legend integer)')
        await self.db.execute(
            'create table if not exists active_boosts (id integer, boost_type text, pay_mult real, xp_mult real, '
            'lasts_until integer)')
        await self.db.execute(
            'create table if not exists daily_shop (item_1 text, item_2 text, item_3 text, item_4 text, item_5 text, '
            'item_6 text)')
        await self.db.commit()

    async def user_data(self, user: User) -> tuple:
        cursor = await self.db.execute('SELECT * FROM user_data WHERE id = ?', (user.id,))
        data = await cursor.fetchall()
        if not data:
            data = (user.id, config.START_CASH, config.START_GOLD, 0, 1.0, 1.0, 0, 0, 0, 0)
            await self.db.execute('INSERT INTO user_data (id, money, gold, xp, pay_mult, xp_mult, daily_claimed, '
                                  'cons_dailies, blacklisted, premium) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
            await self.db.commit()
        return data

    async def money(self, user: User) -> int:
        return (await self.user_data(user))[1]

    async def gold(self, user: User) -> int:
        return (await self.user_data(user))[2]

    async def xp(self, user: User) -> int:
        return (await self.user_data(user))[3]

    async def rank(self, user: User) -> int:
        return floor(sqrt((await self.xp(user)) / 8561) + 1)

    async def pay_mult(self, user: User) -> float:
        return (await self.user_data(user))[4] + ((await self.rank(user)) - 1) / 50

    async def xp_mult(self, user: User) -> float:
        return (await self.user_data(user))[5]

    async def daily_claimed(self, user: User) -> bool:
        return True if (await self.user_data(user))[6] else False

    async def cons_dailies(self, user: User) -> int:
        return (await self.user_data(user))[7]

    async def is_blacklisted(self, user: User) -> bool:
        return True if (await self.user_data(user))[8] else False

    async def has_premium(self, user: User) -> bool:
        return True if (await self.user_data(user))[9] else False

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
            logging.fatal('Unknown/Invalid owner ID(s) passed.')
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
