from main import GamBot
from discord.ext import (
    commands
)
from discord import (
    app_commands,
    Interaction,
    Embed,
    NotFound,
    HTTPException
)
from config import (
    wheel_mapping,
    slot_num_to_emote,
    roulette_listings as r_l,
    rou_nums_to_emotes as r_n_e
)
from core.slots import SlotsView
from core.scratch import ScratchCard
from core.cards import (
    HigherOrLower,
    Blackjack,
    PokerLobby
)
from random import (
    choice,
    choices,
    randint
)
from asyncio import sleep
from math import floor


class Games(commands.Cog):
    def __init__(self, bot: GamBot):
        self.bot = bot

    @app_commands.command(name='coinflip', description='Flip a coin and bet on the outcome.')
    @app_commands.describe(result='Which side would you like to bet on?', bet='How much would you like to bet?')
    @app_commands.choices(result=[
        app_commands.Choice(name='Heads', value='Heads'),
        app_commands.Choice(name='Tails', value='Tails')])
    async def coinflip(self, interaction: Interaction, result: app_commands.Choice[str], bet: int):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif not 1 <= bet <= 100000:
            await self.bot.bad_response(interaction, '❌ Bets must be between `$1` and `$100,000`.')
            return
        elif await self.bot.money(interaction.user) < bet:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that bet.')
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=bet * -1)
        real_result = choice(['Heads', 'Tails'])

        result_embed = Embed(
            colour=self.bot.colour(interaction.guild),
            description=f'{interaction.user.mention} **(Total Bet: `${bet:,}`)**')
        result_embed.set_author(name='Coin Flip', icon_url=self.bot.user.avatar)
        result_embed.add_field(name='Prediction:', value=f'> `{result.value}`', inline=False)
        result_embed.add_field(name='Result:', value=f'> `{real_result}`', inline=False)

        if real_result == result.value:
            winnings = floor(bet * await self.bot.pay_mult(interaction.user))
            xp_gain = floor(bet * await self.bot.xp_mult(interaction.user) / 100)
            await self.bot.edit_balances(interaction, interaction.user, money_d=winnings + bet, xp_d=xp_gain)
            result_embed.add_field(name='Winner!', value=f'💎 You win `${winnings:,}`!', inline=False)
        else:
            result_embed.add_field(name='Loser!', value=f'😢 Better luck next time!', inline=False)

        await interaction.response.send_message(embed=result_embed)

    @app_commands.command(name='slots', description='Test your luck on the slots machine!')
    @app_commands.describe(bet='How much would you like to bet?')
    async def slots(self, interaction: Interaction, bet: int):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif not 1 <= bet <= 100000:
            await self.bot.bad_response(interaction, '❌ Bets must be between `$1` and `$100,000`.')
            return
        elif await self.bot.money(interaction.user) < bet:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that bet.')
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=bet * -1)

        slot_e = Embed(
            colour=self.bot.colour(interaction.guild),
            description=f'{interaction.user.mention} **(Total Bet: `${bet:,}`)**')
        slot_e.set_author(name='Slot Machine', icon_url=self.bot.user.avatar)
        slot_e.set_thumbnail(url='https://cdn.discordapp.com/emojis/1037198961552920596.webp?size=128&quality=lossless')
        slot_e.add_field(name='Spinning...', value='Slots are spinning, good luck!')
        await interaction.response.send_message(embed=slot_e)

        await sleep(3)

        results = []
        for n in range(3):
            results.append(choices(range(1, 10), [20, 18, 16, 14, 12, 10, 7, 2, 1])[0])

        winnings_mult = 0
        if results in [[1, 1, 1], [2, 2, 2], [3, 3, 3]]:
            winnings_mult = results[0]
        elif results == [4, 4, 4]:
            winnings_mult = 5
        elif results == [5, 5, 5]:
            winnings_mult = 8
        elif results == [6, 6, 6]:
            winnings_mult = 10
        elif results == [7, 7, 7]:
            winnings_mult = 25
        elif results == [9, 9, 9]:
            winnings_mult = 100
            await self.bot.add_achievement(interaction, interaction.user, 'slot_jack')
        else:
            eights_count = len([result for result in results if result == 8])
            if eights_count == 1:
                winnings_mult = 5
            elif eights_count == 2:
                winnings_mult = 15
            elif eights_count == 3:
                winnings_mult = 50

        winnings = floor(bet * winnings_mult * await self.bot.pay_mult(interaction.user))
        xp_gain = floor(bet * winnings_mult * await self.bot.xp_mult(interaction.user) / 100)

        slot_e.remove_field(0)
        slot_e.add_field(
            name='Results:', value=''.join([slot_num_to_emote[result] for result in results]), inline=False)

        if winnings:
            await self.bot.edit_balances(interaction, interaction.user, money_d=winnings + bet, xp_d=xp_gain)
            slot_e.add_field(name='Winner!', value=f'💎 You won `${"{:,}".format(winnings)}`!', inline=False)
        else:
            slot_e.add_field(name='Loser!', value=f'😔 You won nothing this time. Try again!', inline=False)

        await interaction.edit_original_response(embed=slot_e, view=SlotsView(self.bot, interaction))

    @app_commands.command(name='scratchcard', description='Purchase a scratch card and try to win a prize!')
    @app_commands.describe(tier='Which tier of card do you want to buy?')
    @app_commands.choices(tier=[
        app_commands.Choice(name='Common', value='10000'),
        app_commands.Choice(name='Uncommon', value='17500'),
        app_commands.Choice(name='Rare', value='25000'),
        app_commands.Choice(name='Epic', value='45000'),
        app_commands.Choice(name='Legendary', value='125000')])
    async def scratchcard(self, interaction: Interaction, tier: app_commands.Choice[str]):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif await self.bot.money(interaction.user) < int(tier.value):
            await self.bot.bad_response(
                interaction, f'❌ {tier.name} scratch cards cost `${int(tier.value):,}`. You cannot afford one.')
            return

        await self.bot.edit_balances(interaction, interaction.user, int(tier.value) * -1)

        scratch_card = ScratchCard(self.bot, interaction, tier)
        await interaction.response.send_message(embed=scratch_card, view=scratch_card)

    @app_commands.command(name='spin', description='Spin the lucky wheel for a reward!')
    @app_commands.checks.cooldown(1, 3600)
    async def spin(self, interaction: Interaction):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return

        spin_e = Embed(colour=self.bot.colour(interaction.guild), description=interaction.user.mention)
        spin_e.set_author(name='Lucky Wheel', icon_url=self.bot.user.avatar)
        spin_e.set_thumbnail(url='https://cdn.discordapp.com/emojis/991767526683988030.webp?size=128&quality=lossless')
        spin_e.add_field(name='Spinning...', value='The lucky wheel is spinning, good luck!')
        await interaction.response.send_message(embed=spin_e)

        await sleep(3)

        result = choices(range(1, 7), [250, 100, 40, 15, 5, 1])[0]

        colour = wheel_mapping[result][0]
        thumbnail_url = wheel_mapping[result][1]
        interval = (wheel_mapping[result][2], wheel_mapping[result][3])

        winnings = floor(randint(interval[0], interval[1]) * await self.bot.pay_mult(interaction.user))
        xp_gain = floor(winnings * await self.bot.xp_mult(interaction.user) / 100)

        await self.bot.edit_balances(interaction, interaction.user, money_d=winnings, xp_d=xp_gain)

        bonus_item = None
        if colour == 'gold':
            bonus_item = choice(['Epic XP Booster', 'Epic Payout Booster'])
            await self.bot.edit_inventory(interaction.user, bonus_item, 1)
            await self.bot.add_achievement(interaction, interaction.user, 'spin_jack')

        spin_e.set_thumbnail(url=thumbnail_url)
        spin_e.remove_field(0)
        spin_e.add_field(
            name='Winner!',
            value=f'The wheel landed on {colour}. You win `${winnings:,}`!\n\n'
                  f'{f"Bonus Item: `1x {bonus_item}`!" if bonus_item else ""}')

        await interaction.edit_original_response(embed=spin_e)

    @app_commands.command(name='roulette', description='Spin the roulette wheel and place a bet!')
    @app_commands.describe(item='What would you like to bet on?', bet='How much money would you like to bet?')
    async def roulette(self, interaction: Interaction, item: str, bet: int):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif not 1 <= bet <= 100000:
            await self.bot.bad_response(interaction, '❌ Bets must be between `$1` and `$100,000`.')
            return
        elif await self.bot.money(interaction.user) < bet:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that bet.')
            return
        elif item not in r_l:
            await self.bot.bad_response(interaction, '❌ Invalid bet type.')
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=bet * -1)

        rou_s = Embed(
            colour=self.bot.colour(interaction.guild),
            description=f'{interaction.user.mention} **(Total Bet: `${bet:,}`)**')
        rou_s.set_author(name='Roulette', icon_url=self.bot.user.avatar)
        rou_s.set_thumbnail(url='https://cdn.discordapp.com/emojis/1044575898076201023.webp?size=128&quality=lossless')
        rou_s.add_field(name='Spinning...', value='Ball is rolling, good luck!')
        await interaction.response.send_message(embed=rou_s)

        await sleep(3)
        result = randint(0, 36)

        rou_s.remove_field(0)
        rou_s.add_field(name='Result', value=f'> Ball landed on {r_n_e[result]}!', inline=False)

        if result in r_l[item]:
            winnings = floor(bet * await self.bot.pay_mult(interaction.user) * (36 / len(r_l[item]) - 1))
            xp_gain = floor(bet * await self.bot.xp_mult(interaction.user) * (36 / len(r_l[item]) - 1) / 100)

            await self.bot.edit_balances(interaction, interaction.user, money_d=winnings + bet, xp_d=xp_gain)
            rou_s.add_field(name='Winner!', value=f'💎 You won `${winnings:,}`!', inline=False)

            if winnings >= 1000000:
                await self.bot.add_achievement(interaction, interaction.user, 'rou_mil')
            if result == 0 and bet >= 25000:
                await self.bot.add_achievement(interaction, interaction.user, 'rou_zero')

        else:
            rou_s.add_field(name='Loser!', value='😢 You lost, better luck next time!', inline=False)

        await interaction.edit_original_response(embed=rou_s)

    @app_commands.command(name='higherorlower', description='Guess whether the next card will be higher or lower! '
                                                            'Remember, Spades > Hearts > Diamonds > Clubs.')
    @app_commands.describe(bet='How much money would you like to bet?')
    async def higherorlower(self, interaction: Interaction, bet: int):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif not 1 <= bet <= 100000:
            await self.bot.bad_response(interaction, '❌ Bets must be between `$1` and `$100,000`.')
            return
        elif await self.bot.money(interaction.user) < bet:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that bet.')
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=bet * -1)

        hl_game = HigherOrLower(self.bot, interaction, bet)
        await interaction.response.send_message(embed=hl_game, view=hl_game)

    @app_commands.command(name='blackjack', description='Start a game of Blackjack against the dealer.')
    @app_commands.describe(bet='How much money would you like to bet?')
    async def blackjack(self, interaction: Interaction, bet: int):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif not 1 <= bet <= 100000:
            await self.bot.bad_response(interaction, '❌ Bets must be between `$1` and `$100,000`.')
            return
        elif await self.bot.money(interaction.user) < bet:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that bet.')
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=bet * -1)

        bj_game = Blackjack(self.bot, interaction, bet)
        bj_game.update_embed(dealer_known=True)

        if bj_game.bj_eval(bj_game.p1) == 21 and bj_game.bj_eval(bj_game.dealer) == 21:
            winnings = bet
            xp_gain = 0
            bj_game.add_field(
                name='Tie!', value=f'🧐 You and the dealer both got blackjack. You bet will be returned.', inline=False)

        elif bj_game.bj_eval(bj_game.p1) == 21:
            winnings = floor(1.5 * bet * await self.bot.pay_mult(interaction.user))
            xp_gain = floor(1.5 * bet * await self.bot.xp_mult(interaction.user) / 100)
            bj_game.add_field(name='Winner!', value=f'🤑 Blackjack! You `${winnings:,}!`', inline=False)
            winnings += bet

        elif bj_game.bj_eval(bj_game.dealer) == 21:
            winnings = 0
            xp_gain = 0
            bj_game.add_field(name='Loser!', value=f'😭 Dealer got a blackjack, better luck next time!', inline=False)

        else:
            bj_game.update_embed()
            await bj_game.update_button()
            await interaction.response.send_message(embed=bj_game, view=bj_game)
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=winnings, xp_d=xp_gain)
        await interaction.response.send_message(embed=bj_game)

    @app_commands.command(name='poker', description='Start a game of Poker against your friends.')
    @app_commands.describe(bet='What would you like the starting bet to be?')
    async def poker(self, interaction: Interaction, bet: int = 25000):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif not 10000 <= bet <= 100000 or bet % 5:
            await self.bot.bad_response(
                interaction, '❌ Starting bets must be a multiple of `5` and be between `$10,000` and `$100,000`.')
            return
        elif await self.bot.money(interaction.user) < bet:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that bet.')
            return

        pl = PokerLobby(self.bot, interaction, bet)
        await interaction.response.send_message(embed=pl, view=pl)

    @app_commands.command(name='lottery', description='View the state of the currently ongoing lottery draw!')
    @app_commands.checks.cooldown(1, 10)
    async def lottery(self, interaction: Interaction):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return

        lott_data = await self.bot.lott_data()

        if not lott_data:
            await self.bot.bad_response(interaction, '❌ The lottery is temporarily unavailable, try again later.')
            return

        total_tickets = len(await self.bot.lott_tickets())
        winnings = lott_data[0] + total_tickets * 5000

        try:
            prev_winner = await self.bot.fetch_user(lott_data[7])
        except (NotFound, HTTPException):
            prev_winner = None

        lott_e = Embed(
            colour=self.bot.colour(interaction.guild),
            description=f'**Ends on <t:{self.bot.next_weekly_reset}:F>**')
        lott_e.set_author(name=f'Global Lottery', icon_url=self.bot.user.avatar)
        lott_e.set_thumbnail(url='https://cdn.discordapp.com/emojis/991767526683988030.webp?size=128&quality=lossless')

        lott_e.add_field(name='💸 Prize Pool:', value=f'> `${winnings:,}`')
        lott_e.add_field(name='🎟️ Total Tickets Sold:', value=f'> `{total_tickets:,}`', inline=False)

        item_data = [lott_data[1], lott_data[2], 6], [lott_data[3], lott_data[4], 16], [lott_data[5], lott_data[6], 40]
        display = [slot_num_to_emote[3], slot_num_to_emote[5], slot_num_to_emote[6]]
        for entry in item_data:
            lott_e.add_field(
                name=f'{display[item_data.index(entry)]} Bonus Item {item_data.index(entry) + 1}:',
                value=f'> `{entry[1]}x {entry[0]}`' if winnings >= lott_data[0] * entry[2] else
                f'> `[Locked]`')

        lott_e.add_field(
            name=f'{slot_num_to_emote[1]} Previous Winner:',
            value=f'> `{prev_winner.name if prev_winner else "[Unknown User]"} (${lott_data[8]:,})`',
            inline=False)

        await interaction.response.send_message(embed=lott_e)

    @app_commands.command(name='buytickets', description='Purchase lottery tickets for a chance to win!')
    @app_commands.describe(amount='How many tickets would you like to get?')
    async def buytickets(self, interaction: Interaction, amount: int = 1):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif not 1 <= amount <= 100:
            await self.bot.bad_response(interaction, '❌ Please enter a number from `1` to `100`.')
            return
        elif await self.bot.money(interaction.user) < 5000 * amount:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that purchase.')
            return
        elif not await self.bot.lott_data():
            await self.bot.bad_response(interaction, '❌ The lottery is temporarily unavailable, try again later.')
            return

        await self.bot.edit_balances(interaction, interaction.user, money_d=10000 * amount * -1)

        for i in range(amount):
            await self.bot.add_lott_ticket(interaction.user)
        await self.bot.response(
            interaction, f'**Purchased `{amount}` lottery tickets for `{amount * 5000:,}`! Good luck!**',
            self.bot.colour(interaction.guild))

    @roulette.autocomplete('item')
    async def rou_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        item_list = []
        for item in r_l:
            if current.lower() in item.lower() and len(item_list) < 25:
                item_list.append(app_commands.Choice(name=item, value=item))
        return item_list


async def setup(bot: GamBot):
    await bot.add_cog(Games(bot))
