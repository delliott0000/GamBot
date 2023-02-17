from main import GamBot
from discord.ext import (
    commands
)
from discord import (
    app_commands,
    Interaction,
    Embed
)
from config import (
    wheel_mapping,
    slot_num_to_emote,
    roulette_listings as r_l,
    rou_nums_to_emotes as r_n_e
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
    async def coinflip(self, interaction: Interaction, result: str, bet: int):
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
        result_embed.add_field(name='Prediction:', value=f'> `{result}`', inline=False)
        result_embed.add_field(name='Result:', value=f'> `{real_result}`', inline=False)

        if real_result == result:
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
            else:
                winnings_mult = 0

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

        await interaction.edit_original_response(embed=slot_e)

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

    @roulette.autocomplete('item')
    async def rou_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        item_list = []
        for item in r_l:
            if current.lower() in item.lower() and len(item_list) < 25:
                item_list.append(app_commands.Choice(name=item, value=item))
        return item_list


async def setup(bot: GamBot):
    await bot.add_cog(Games(bot))
