import os
import asyncio
import logging
from typing import Optional
from pathlib import Path
from math import floor, sqrt
from time import strftime
from random import sample, choice, randint
from datetime import date, datetime, timedelta
from re import fullmatch

from config import (
    achievements_mapping,
    pack_mapping,
    boost_mapping,
    TOKEN,
    OWNERS,
    ACTIVITY,
    INVITE, SUPPORT, VOTE,
    START_CASH, START_GOLD,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s (%(filename)s) - %(message)s')

try:
    from discord.ext import commands, tasks
    from discord import (
        __version__ as __discord__,
        app_commands,
        utils,
        Intents,
        Activity,
        ActivityType,
        Guild,
        Message,
        Embed,
        User,
        Color,
        Interaction,
        PrivilegedIntentsRequired,
        LoginFailure,
        NotFound,
        Forbidden,
        HTTPException
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
            activity=Activity(type=ActivityType.playing, name=ACTIVITY)
        )
        self.db = None

        self.invite = INVITE
        self.support = SUPPORT
        self.vote = VOTE

        self.app_commands = []

        self.next_daily_reset = floor(datetime.combine(date.today(), datetime.min.time()).timestamp()) + 86400
        self.next_weekly_reset = floor(datetime.combine(date.today(), datetime.min.time()).timestamp()) + 86400

        self.tree.on_error = self.cog_app_command_error

    @property
    def _token(self):
        return TOKEN

    def colour(self, guild: Optional[Guild]):
        try:
            return guild.get_member(self.user.id).colour
        except AttributeError:
            return 0xffffff

    @staticmethod
    def time_now():
        return floor(utils.utcnow().timestamp())

    @staticmethod
    async def response(interaction: Interaction, reply: str, colour: int, ephemeral: bool = False):
        await interaction.response.send_message(embed=Embed(colour=colour, description=reply), ephemeral=ephemeral)

    async def bad_response(self, interaction: Interaction, reply: str):
        await self.response(interaction, reply, Color.red(), True)

    async def blacklisted_response(self, interaction: Interaction):
        await self.bad_response(interaction, '❌ You\'ve been blacklisted from using this bot.')

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
        await self.db.execute(
            'create table if not exists lott_tickets (id integer)')
        await self.db.execute(
            'create table if not exists lott_data (money_pool integer, bi_1 text, bc_1 integer, bi_2 text, '
            'bc_2 integer, bi_3 text, bc_3 integer, prev_winner integer, prev_winnings integer)')
        await self.db.commit()

    async def user_data(self, user: User) -> tuple:
        cursor = await self.db.execute('SELECT * FROM user_data WHERE id = ?', (user.id,))
        data = await cursor.fetchone()
        if not data:
            data = (user.id, int(START_CASH), int(START_GOLD), 0, 1.0, 1.0, 0, 0, 0, 0)
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

    async def edit_balances(self, interaction: Optional[Interaction], user: User,
                            money_d: int = 0, gold_d: int = 0, xp_d: int = 0) -> None:
        old_rank = await self.rank(user)

        new_money = await self.money(user) + money_d
        new_gold = await self.gold(user) + gold_d
        new_xp = await self.xp(user) + xp_d

        await self.db.execute('UPDATE user_data SET money = ?, gold = ?, xp = ? WHERE id = ?',
                              (new_money, new_gold, new_xp, user.id))
        await self.db.commit()

        new_rank = await self.rank(user)

        if new_rank > old_rank:
            await self.edit_inventory(user, 'Small Gold Pack', 1)
            try:
                await interaction.channel.send(f'***{user.mention} has just reached rank {new_rank}!***\n'
                                               f'***They\'ve been awarded `x1 Small Gold Pack`.***')
            except Forbidden as error:
                logging.warning(error)
            except AttributeError:
                pass

        if money_d > 0 and new_money > 1000000:
            await self.add_achievement(interaction, user, 'mill')
        if money_d > 0 and new_money > 1000000000:
            await self.add_achievement(interaction, user, 'bill')
        if new_rank >= 9:
            await self.add_achievement(interaction, user, 'legend')

    async def pay_mult(self, user: User) -> float:
        return (await self.user_data(user))[4] + ((await self.rank(user)) - 1) / 50

    async def xp_mult(self, user: User) -> float:
        return (await self.user_data(user))[5]

    async def edit_pay_mult(self, user: User, pay_mult_d: float) -> None:
        pay_mult = (await self.pay_mult(user)) + pay_mult_d
        await self.db.execute('UPDATE user_data SET pay_mult = ? WHERE id = ?', (pay_mult, user.id))
        await self.db.commit()

    async def edit_xp_mult(self, user: User, xp_mult_d: float) -> None:
        xp_mult = (await self.xp_mult(user)) + xp_mult_d
        await self.db.execute('UPDATE user_data SET xp_mult = ? WHERE id = ?', (xp_mult, user.id))
        await self.db.commit()

    async def daily_claimed(self, user: User) -> bool:
        return True if (await self.user_data(user))[6] else False

    async def cons_dailies(self, user: User) -> int:
        return (await self.user_data(user))[7]

    async def add_daily(self, user: User) -> None:
        cons_dailies = (await self.cons_dailies(user)) + 1
        await self.db.execute('UPDATE user_data SET daily_claimed = ?, cons_dailies = ? WHERE id = ?',
                              (1, cons_dailies, user.id))
        await self.db.commit()

    async def is_blacklisted(self, user: User) -> bool:
        return True if (await self.user_data(user))[8] else False

    async def toggle_blacklist(self, user: User) -> None:
        blacklisted = 0 if await self.is_blacklisted(user) else 1
        await self.db.execute('UPDATE user_data SET blacklisted = ? WHERE id = ?', (blacklisted, user.id))
        await self.db.commit()

    async def has_premium(self, user: User) -> bool:
        return True if (await self.user_data(user))[9] else False

    async def add_premium(self, user: User, duration: int) -> None:
        if await self.has_premium(user):
            lasts_until = [b for b in await self.boosts(user) if b[1] == 'Premium'][0][4] + duration
            await self.db.execute('UPDATE active_boosts SET lasts_until = ? WHERE id = ? AND boost_type = ?',
                                  (lasts_until, user.id, 'Premium'))
        else:
            await self.db.execute('UPDATE user_data SET premium = ? WHERE id = ?', (1, user.id))
            await self.edit_pay_mult(user, 0.10)
            await self.edit_xp_mult(user, 0.25)
            await self.db.execute('INSERT INTO active_boosts (id, boost_type, pay_mult, xp_mult, lasts_until) '
                                  'VALUES (?, ?, ?, ?, ?)',
                                  (user.id, 'Premium', 0.10, 0.25, self.time_now() + duration))
        await self.db.commit()

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

    async def edit_inventory(self, user: User, item: str, amount: int) -> None:
        count = (await self.inventory(user))[item] + amount
        try:
            await self.db.execute(f'UPDATE inventories SET {pack_mapping[item][0]} = ? WHERE id = ?', (count, user.id))
        except KeyError:
            await self.db.execute(f'UPDATE inventories SET {boost_mapping[item][0]} = ? WHERE id = ?', (count, user.id))
        await self.db.commit()

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

    async def add_achievement(self, interaction: Optional[Interaction], user: User, achievement: str) -> None:
        if (await self.achievements(user))[achievement]:
            return
        await self.db.execute(f'UPDATE achievements SET {achievement} = ? WHERE id = ?', (1, user.id))
        await self.db.commit()

        try:
            await interaction.channel.send(
                f'**{user.mention} just earned the achievement: `{achievements_mapping[achievement][0]}`!**\n'
                f'**They win `$100,000` and an XP bonus!**')
        except Forbidden as error:
            logging.warning(error)
        except AttributeError:
            pass

        await self.edit_balances(interaction, user, money_d=100000, xp_d=5000)

    async def boosts(self, user: User) -> list:
        cursor = await self.db.execute('SELECT * FROM active_boosts WHERE id = ?', (user.id,))
        data = await cursor.fetchall()
        return data

    async def add_boost(self, user: User, boost_type: str) -> None:
        boost = boost_mapping[boost_type]
        existing = [b for b in await self.boosts(user) if b[1] == boost[0]]
        if existing:
            new_lasts_until = existing[0][4] + boost[3]
            await self.db.execute('UPDATE active_boosts SET lasts_until = ? WHERE id = ? AND boost_type = ?',
                                  (new_lasts_until, user.id, boost[0]))
        else:
            await self.edit_pay_mult(user, boost[1])
            await self.edit_xp_mult(user, boost[2])
            await self.db.execute('INSERT INTO active_boosts (id, boost_type, pay_mult, xp_mult, lasts_until) '
                                  'VALUES (?, ?, ?, ?, ?)',
                                  (user.id, boost[0], boost[1], boost[2], self.time_now() + boost[3]))
        await self.db.commit()

    async def lott_tickets(self) -> list:
        cursor = await self.db.execute('SELECT id FROM lott_tickets')
        data = await cursor.fetchall()
        return [entry[0] for entry in data]

    async def add_lott_ticket(self, user: User) -> None:
        await self.db.execute('INSERT INTO lott_tickets (id) VALUES (?)', (user.id,))
        await self.db.commit()

    async def lott_data(self) -> tuple:
        cursor = await self.db.execute('SELECT * FROM lott_data')
        return await cursor.fetchone()

    async def item_shop(self):
        cursor = await self.db.execute('SELECT * FROM daily_shop')
        return await cursor.fetchone()

    async def leaderboard(self, lb_type: str):
        cursor = await self.db.execute(f'SELECT id, {lb_type.lower()} FROM user_data')
        data = await cursor.fetchall()
        return sorted(data, key=lambda x: x[1], reverse=True)

    async def wipe(self, user_id: int):
        await self.db.execute('DELETE FROM user_data WHERE id = ?', (user_id,))
        await self.db.execute('DELETE FROM achievements WHERE id = ?', (user_id,))
        await self.db.execute('DELETE FROM inventories WHERE id = ?', (user_id,))
        await self.db.execute('DELETE FROM active_boosts WHERE id = ?', (user_id,))
        await self.db.commit()
        logging.info(f'Wiped data associated with user ID: {user_id}')

    @tasks.loop(seconds=30)
    async def update_data(self):
        await self.wait_until_ready()

        cursor = await self.db.execute(f'SELECT * FROM active_boosts WHERE lasts_until < {self.time_now()}')
        expired_boosts = await cursor.fetchall()
        await self.db.execute(f'DELETE FROM active_boosts WHERE lasts_until < {self.time_now()}')

        for boost in expired_boosts:

            try:
                user = await self.fetch_user(boost[0])
            except (NotFound, HTTPException):
                await self.wipe(boost[0])
                continue

            await self.edit_pay_mult(user, boost[2] * -1)
            await self.edit_xp_mult(user, boost[3] * -1)

            if boost[1] == 'Premium':
                await self.db.execute('UPDATE user_data SET premium = ? WHERE id = ?', (0, user.id))

            await asyncio.sleep(0.1)

        await self.db.commit()

    @tasks.loop(seconds=10)
    async def wait_for_rotation(self):
        if strftime('%H:%M') == '00:00':
            self.daily_reset.start()
            self.weekly_reset.start()
            self.wait_for_rotation.stop()
            logging.info('Daily & weekly rotations started!')

    @tasks.loop(hours=24)
    async def daily_reset(self):
        cursor = await self.db.execute('SELECT id, daily_claimed FROM user_data')
        data = await cursor.fetchall()

        for entry in data:
            if not entry[1]:
                await self.db.execute('UPDATE user_data SET cons_dailies = ? WHERE id = ?', (0, entry[0]))
        await self.db.execute('UPDATE user_data SET daily_claimed = ?', (0,))

        new_items = tuple(sample(list(boost_mapping) + list(pack_mapping), 6))

        cursor = await self.db.execute('SELECT * FROM daily_shop')
        if await cursor.fetchone():
            await self.db.execute('UPDATE daily_shop SET item_1 = ?, item_2 = ?, item_3 = ?, item_4 = ?, item_5 = ?, '
                                  'item_6 = ?', new_items)
        else:
            await self.db.execute('INSERT INTO daily_shop (item_1, item_2, item_3, item_4, item_5, item_6) VALUES '
                                  '(?, ?, ?, ?, ?, ?)', new_items)

        await self.db.commit()

        self.next_daily_reset = floor(datetime.combine(date.today(), datetime.min.time()).timestamp()) + 86400

    @tasks.loop(hours=168)
    async def weekly_reset(self):
        cursor = await self.db.execute('SELECT id FROM user_data WHERE premium = ?', (1,))
        premium_users = await cursor.fetchall()

        for entry in premium_users:
            try:
                user = await self.fetch_user(entry[0])
            except (NotFound, HTTPException):
                await self.wipe(entry[0])
                continue

            await self.edit_inventory(user, 'Large Money Pack', 1)
            await self.edit_inventory(user, 'Medium Gold Pack', 1)
            await asyncio.sleep(0.1)

        lott_tickets = await self.lott_tickets()
        lott_data = await self.lott_data()

        try:
            winner = await self.fetch_user(choice(lott_tickets))
            total_winnings = lott_data[0] + len(lott_tickets) * 5000
        except (NotFound, HTTPException, TypeError, IndexError):
            winner = None
            total_winnings = 0

        if winner and total_winnings:

            await self.edit_balances(None, winner, money_d=total_winnings)
            await self.add_achievement(None, winner, 'lott_win')

            t1_threshold = lott_data[0] * 6
            t2_threshold = lott_data[0] * 16
            t3_threshold = lott_data[0] * 40

            if total_winnings >= t1_threshold:
                await self.edit_inventory(winner, lott_data[1], lott_data[2])
            if total_winnings >= t2_threshold:
                await self.edit_inventory(winner, lott_data[3], lott_data[4])
            if total_winnings >= t3_threshold:
                await self.edit_inventory(winner, lott_data[5], lott_data[6])

        await self.db.execute('DELETE FROM lott_tickets')
        await self.db.execute('DELETE FROM lott_data')

        new_lottery_data = (
            randint(100, 500) * 10000,
            choice(['Rare XP Booster', 'Rare Payout Booster', 'Small Gold Pack']), randint(1, 5),
            choice(['Epic XP Booster', 'Epic Payout Booster', 'Medium Gold Pack']), randint(1, 5),
            choice(['Large Gold Pack', 'Jackpot Pack']), randint(1, 3),
            winner.id if winner else 0, total_winnings)

        await self.db.execute(
            'INSERT INTO lott_data (money_pool, bi_1, bc_1, bi_2, bc_2, bi_3, bc_3, prev_winner, prev_winnings) VALUES '
            '(?, ?, ?, ?, ?, ?, ?, ?, ?)', new_lottery_data)

        await self.db.commit()

        self.next_weekly_reset = floor(datetime.combine(date.today(), datetime.min.time()).timestamp()) + 604800

    def assist_embed(self, guild: Optional[Guild]):
        assist_embed = Embed(
            colour=self.colour(guild),
            title=f'♦ {self.user.name} ♦',
            description='Hello! I\'m a bot built to play fun games such as Blackjack, Roulette, Poker and more. '
                        'I also feature a built-in currency system, profiles, XP/ranking and many more features.\n\n'
                        '**Use `/help` to view a full list of my commands. Popular commands include:\n'
                        '`/blackjack, /roulette, /higherorlower, /daily, /profile` . . .\n'
                        'and the list goes on!\n\n'
                        'Please ensure I have the following permissions enabled:\n'
                        '`View Channels, Send Messages (In Threads), Embed Links, Use External Emojis`.**\n\n'
                        f'[Invite Me]({self.invite}) | [Support Server]({self.support}) | [Vote For Me]({self.vote})')
        return assist_embed

    async def on_message(self, message: Message):
        if fullmatch(rf'<@{self.user.id}>', message.content):
            try:
                await message.channel.send(embed=self.assist_embed(message.guild))
            except Forbidden:
                pass

    async def on_guild_join(self, guild: Guild):
        logging.info(f'Joined {guild.name} (now in {len(self.guilds):,} total guilds)')
        for channel in guild.channels:
            if channel == guild.system_channel:
                try:
                    await channel.send(embed=self.assist_embed(guild))
                except Forbidden:
                    pass
                break

    async def cog_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await self.bad_response(
                interaction, f'❌ You\'re on cooldown. Try again in `{timedelta(seconds=floor(error.retry_after))}`.')

        elif isinstance(error, app_commands.BotMissingPermissions):
            await self.bad_response(
                interaction,
                f'❌ Bot missing required permissions: `{"".join(error.missing_permissions).replace("_", " ")}`.')

        else:
            await self.bad_response(interaction, f'An unexpected error occurred: {str(error)}')
            logging.error(f'An unexpected error occurred: {str(error)}')

    async def setup_hook(self) -> None:
        logging.info('Setting up database...')

        self.db = await aiosqlite.connect(Path(__file__).with_name('data.db'))
        await self.db.execute('PRAGMA journal_mode=wal')
        await self.format_db()

        logging.info('Starting background tasks...')
        self.update_data.start()
        self.wait_for_rotation.start()

        logging.info('Syncing commands...')
        self.app_commands = await self.tree.sync()

        logging.info(f'Logging in as {self.user} (ID: {self.user.id})...')

        try:
            self.owner_ids = set(int(user_id) for user_id in OWNERS.split(','))
            logging.info('Owner(s): ' + ''.join([(await self.fetch_user(user_id)).name for user_id in self.owner_ids]))
        except (ValueError, NotFound):
            logging.fatal('Unknown/Invalid owner ID(s) passed.')
            exit(0)

    def run_bot(self):
        async def runner():
            async with self:

                try:
                    for filename in os.listdir('./cogs'):
                        if filename.endswith('.py'):
                            try:
                                await self.load_extension(f'cogs.{filename[:-3]}')
                            except (commands.ExtensionFailed, commands.NoEntryPointError):
                                logging.warning(f'Extension {filename} could not be loaded...')
                except FileNotFoundError as err:
                    logging.fatal(err)
                    logging.fatal('Ensure the cogs folder is in the same working directory as main.py and try again.')
                    exit()

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
            self.update_data.stop()
            self.wait_for_rotation.stop()
            self.daily_reset.stop()
            self.weekly_reset.stop()

        try:
            asyncio.run(runner())
        except (KeyboardInterrupt, SystemExit):
            logging.info('Received signal to terminate bot and event loop.')
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
