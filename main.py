import asyncio
import logging
from typing import Optional
from pathlib import Path
from math import floor, sqrt
from config import (
    achievements_mapping,
    pack_mapping,
    boost_mapping,
    TOKEN,
    OWNERS,
    ACTIVITY,
    START_CASH, START_GOLD,
    COLOUR_INFO, COLOUR_ERROR, COLOUR_SUCCESS
)

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
        NotFound,
        Forbidden
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
            activity=Activity(type=ActivityType.watching, name=ACTIVITY)
        )
        self.db = None

    @property
    def _token(self):
        return TOKEN

    @property
    def _colour_info(self):
        return hex(int(COLOUR_INFO, 16))

    @property
    def _colour_success(self):
        return hex(int(COLOUR_SUCCESS, 16))

    @property
    def _colour_error(self):
        return hex(int(COLOUR_ERROR, 16))

    def _bot_colour(self, guild: Optional[Guild]):
        if guild:
            return guild.get_member(self.user.id).colour
        return 0xffffff

    @staticmethod
    def _now():
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
        data = await cursor.fetchone()
        if not data:
            data = (user.id, START_CASH, START_GOLD, 0, 1.0, 1.0, 0, 0, 0, 0)
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

    async def inventory(self, user: User) -> dict:
        cursor = await self.db.execute('SELECT * FROM inventories WHERE id = ?', (user.id,))
        data = await cursor.fetchone()
        if not data:
            data = (user.id,) + (0,) * 13
            await self.db.execute(
                'INSERT INTO inventories (id, money_pack_s, money_pack_m, money_pack_l, gold_pack_s, gold_pack_m, '
                'gold_pack_l, jackpot_pack, pay_boost_c, pay_boost_r, pay_boost_e, xp_boost_c, xp_boost_r, xp_boost_e) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
            await self.db.commit()
        return {'Common Payout Booster': data[8], 'Rare Payout Booster': data[9], 'Epic Payout Booster': data[10],
                'Common XP Booster': data[11], 'Rare XP Booster': data[12], 'Epic XP Booster': data[13],
                'Small Money Pack': data[1], 'Medium Money Pack': data[2], 'Large Money Pack': data[3],
                'Small Gold Pack': data[4], 'Medium Gold Pack': data[5], 'Large Gold Pack': data[6],
                'Jackpot Pack': data[7]}

    async def achievements(self, user: User) -> dict:
        cursor = await self.db.execute('SELECT * FROM achievements WHERE id = ?', (user.id,))
        data = await cursor.fetchone()
        if not data:
            data = (user.id,) + (0,) * 15
            await self.db.execute(
                'INSERT INTO achievements (id, bj_max, bj_sevens, rou_mil, rou_zero, poker_sf, poker_max, hl_max, '
                'hl_str, slot_jack, spin_jack, lott_win, scrat_win, mill, bill, legend) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
            await self.db.commit()
        return {
            'bj_max': data[1], 'bj_sevens': data[2], 'rou_mil': data[3], 'rou_zero': data[4], 'poker_sf': data[5],
            'poker_max': data[6], 'hl_max': data[7], 'hl_str': data[8], 'slot_jack': data[9], 'spin_jack': data[10],
            'lott_win': data[11], 'scrat_win': data[12], 'mill': data[13], 'bill': data[14], 'legend': data[15]}

    async def boosts(self, user: User) -> list:
        cursor = await self.db.execute('SELECT * FROM active_boosts WHERE id = ?', (user.id,))
        data = await cursor.fetchall()
        return data

    async def edit_balances(self, interaction: Interaction, user: User,
                            money_d: int = 0, gold_d: int = 0, xp_d: int = 0) -> None:
        old_rank = await self.rank(user)

        new_money = await self.money(user) + money_d
        new_gold = await self.gold(user) + gold_d
        new_xp = await self.xp(user) + xp_d

        await self.db.execute('UPDATE user_data SET money = ?, gold = ?, xp = ? WHERE id = ?',
                              (new_money, new_gold, new_xp, user.id))
        await self.db.commit()

        new_rank = await self.rank(user)
        if new_rank != old_rank:
            try:
                await interaction.channel.send(f'***{user.mention} has just reached rank {new_rank}!***\n'
                                               f'***They\'ve been awarded `x1 Small Gold Pack`.***')
            except Forbidden as error:
                logging.warning(error)

    async def edit_pay_mult(self, user: User, pay_mult_d: float):
        pay_mult = (await self.pay_mult(user)) + pay_mult_d
        await self.db.execute('UPDATE user_data SET pay_mult = ? WHERE id = ?', (pay_mult, user.id))
        await self.db.commit()

    async def edit_xp_mult(self, user: User, xp_mult_d: float):
        xp_mult = (await self.xp_mult(user)) + xp_mult_d
        await self.db.execute('UPDATE user_data SET xp_mult = ? WHERE id = ?', (xp_mult, user.id))
        await self.db.commit()

    async def edit_inventory(self, user: User, item: str, amount: int):
        count = (await self.inventory(user))[item] + amount
        try:
            await self.db.execute(f'UPDATE inventories SET {pack_mapping[item][0]} = ? WHERE id = ?', (count, user.id))
        except KeyError:
            await self.db.execute(f'UPDATE inventories SET {boost_mapping[item][0]} = ? WHERE id = ?', (count, user.id))
        await self.db.commit()

    async def add_achievement(self, interaction: Interaction, user: User, achievement: str):
        if (await self.achievements(user))[achievement]:
            return
        await self.db.execute(f'UPDATE achievements SET {achievement} = ? WHERE id = ?', (1, user.id))
        await self.db.commit()
        try:
            await interaction.channel.send(
                f'{user.mention} just earned the achievement: `{achievements_mapping[achievement]}`. '
                f'They win `$100,000` and an XP bonus!')
        except Forbidden as error:
            logging.warning(error)
        await self.edit_balances(interaction, user, money_d=100000, xp_d=5000)

    async def setup_hook(self) -> None:
        logging.info('Setting up database...')

        self.db = await aiosqlite.connect(Path(__file__).with_name('data.db'))
        await self.db.execute('PRAGMA journal_mode=wal')
        await self.format_db()

        logging.info(f'Logging in as {self.user} (ID: {self.user.id})...')

        try:
            self.owner_ids = set(int(user_id) for user_id in OWNERS.split(','))
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
