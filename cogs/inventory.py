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
from config import emoji_cost_mapping, pack_mapping, boost_mapping
from random import randint, choice


class Inventory(commands.Cog):
    def __init__(self, bot: GamBot):
        self.bot = bot

    @app_commands.command(name='inventory', description='View your own or another user\'s GamBot inventory.')
    @app_commands.describe(user='Whose profile would you like to view?')
    async def inventory(self, interaction: Interaction, user: User = None):
        if not user:
            user = interaction.user
        elif await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ That user is a bot.')
            return

        data = await self.bot.inventory(user)

        inventory_embed = Embed(colour=self.bot.colour(interaction.guild), description=user.mention)
        inventory_embed.set_author(name='GamBot Inventory', icon_url=self.bot.user.avatar)
        inventory_embed.set_thumbnail(url=user.avatar if user.avatar else user.default_avatar)

        for item in data:
            inventory_embed.add_field(
                name=f'{emoji_cost_mapping[item][0]} {item}s',
                value=f'> `{data[item]:,} {item.split(" ")[-1]}s`')

        await interaction.response.send_message(embed=inventory_embed)

    @app_commands.command(name='boosts', description='View your own or another user\'s currently-active boosts.')
    @app_commands.describe(user='Whose boosts would you like to view?')
    async def boosts(self, interaction: Interaction, user: User = None):
        if not user:
            user = interaction.user
        elif await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif user.bot:
            await self.bot.bad_response(interaction, '❌ That user is a bot.')
            return

        data = await self.bot.boosts(user)

        boosts_embed = Embed(colour=self.bot.colour(interaction.guild), description=user.mention)
        boosts_embed.set_author(name='GamBot Boosts', icon_url=self.bot.user.avatar)
        boosts_embed.set_thumbnail(url=user.avatar if user.avatar else user.default_avatar)

        for item in data:
            if item[1] == 'Premium':
                boost_title = f'💎 Premium'
            else:
                boost = [b for b in boost_mapping if boost_mapping[b][0] == item[1]][0]
                boost_title = f'{emoji_cost_mapping[boost][0]} {boost}'
            boosts_embed.add_field(name=boost_title, value=f'> **Expires: <t:{item[4]}:f>**', inline=False)
        if not data:
            boosts_embed.add_field(name='No Boosts', value='❌ This user does not have any active boosters!')

        await interaction.response.send_message(embed=boosts_embed)

    @app_commands.command(name='boost', description='Use one of your boosters for a temporary increase in payouts/XP!')
    @app_commands.describe(booster='What type of booster would you like to use?')
    @app_commands.choices(booster=[app_commands.Choice(name='Common Payout Booster', value='Common Payout Booster'),
                                   app_commands.Choice(name='Rare Payout Booster', value='Rare Payout Booster'),
                                   app_commands.Choice(name='Epic Payout Booster', value='Epic Payout Booster'),
                                   app_commands.Choice(name='Common XP Booster', value='Common XP Booster'),
                                   app_commands.Choice(name='Rare XP Booster', value='Rare XP Booster'),
                                   app_commands.Choice(name='Epic XP Booster', value='Epic XP Booster')])
    async def boost(self, interaction: Interaction, booster: app_commands.Choice[str]):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return

        booster_count = (await self.bot.inventory(interaction.user))[booster.name]

        if booster_count < 1:
            await self.bot.bad_response(interaction, '❌ You don\'t have any boosters of that type.')
            return
        await self.bot.edit_inventory(interaction.user, booster.name, -1)
        await self.bot.add_boost(interaction.user, booster.name)
        await self.bot.response(interaction, f'`{booster.name}` used!', self.bot.colour(interaction.guild))

    @app_commands.command(name='open', description='Open a pack to claim a reward!')
    @app_commands.describe(pack='What type of pack would you like to open?')
    @app_commands.choices(pack=[app_commands.Choice(name='Small Money Pack', value='Small Money Pack'),
                                app_commands.Choice(name='Medium Money Pack', value='Medium Money Pack'),
                                app_commands.Choice(name='Large Money Pack', value='Large Money Pack'),
                                app_commands.Choice(name='Small Gold Pack', value='Small Gold Pack'),
                                app_commands.Choice(name='Medium Gold Pack', value='Medium Gold Pack'),
                                app_commands.Choice(name='Large Gold Pack', value='Large Gold Pack'),
                                app_commands.Choice(name='Jackpot Pack', value='Jackpot Pack')])
    async def open(self, interaction: Interaction, pack: app_commands.Choice[str]):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return

        pack_count = (await self.bot.inventory(interaction.user))[pack.name]

        if pack_count < 1:
            await self.bot.bad_response(interaction, '❌ You don\'t have any packs of that type.')
            return
        await self.bot.edit_inventory(interaction.user, pack.name, -1)

        money_reward = randint(pack_mapping[pack.name][1], pack_mapping[pack.name][2])
        gold_reward = randint(pack_mapping[pack.name][3], pack_mapping[pack.name][4])
        await self.bot.edit_balances(interaction, interaction.user, money_d=money_reward, gold_d=gold_reward)

        money_reward_str = f'\n***Money Reward: `${money_reward:,}`.***' if money_reward else ''
        gold_reward_str = f'\n***Gold Reward: `{gold_reward:,} Gold`.***' if gold_reward else ''

        bonus_reward_str = ''
        if pack.name == 'Jackpot Pack':
            bonus_booster = choice(list(boost_mapping))
            await self.bot.edit_inventory(interaction.user, bonus_booster, 1)
            bonus_reward_str = f'\n***Bonus Reward: `1x {bonus_booster}`!***'

        await self.bot.response(
            interaction, f'`{pack.name}` opened!\n{money_reward_str}{gold_reward_str}{bonus_reward_str}',
            self.bot.colour(interaction.guild))

    @app_commands.command(name='shop', description='View what\'s currently for sale in the daily item shop.')
    async def shop(self, interaction: Interaction):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return

        shop_embed = Embed(
            colour=self.bot.colour(interaction.guild), title='Currently For Sale:',
            description=f'**Resets on <t:{self.bot.next_reset_time}:F>**')
        shop_embed.set_author(name='GamBot Daily Shop', icon_url=self.bot.user.avatar)

        daily_shop = await self.bot.item_shop()

        for item in daily_shop:
            shop_embed.add_field(
                name=f'{emoji_cost_mapping[item][0]} {item}', value=f'> **Cost:** `{emoji_cost_mapping[item][1]} Gold`')

        await interaction.response.send_message(embed=shop_embed)

    @app_commands.command(name='buy', description='Buy an item from the item shop.')
    @app_commands.describe(item='What type of item would you like to buy?')
    @app_commands.describe(amount='How many would you like to buy?')
    async def buy(self, interaction: Interaction, item: str, amount: int = 1):
        if await self.bot.is_blacklisted(interaction.user):
            await self.bot.blacklisted_response(interaction)
            return
        elif item not in await self.bot.item_shop():
            await self.bot.bad_response(interaction, '❌ Invalid item.')
            return
        elif amount < 1:
            await self.bot.bad_response(interaction, '❌ Invalid amount.')
            return
        elif await self.bot.gold(interaction.user) < amount * emoji_cost_mapping[item][1]:
            await self.bot.bad_response(interaction, '❌ You cannot afford that purchase.')
            return

        await self.bot.edit_balances(interaction, interaction.user, gold_d=emoji_cost_mapping[item][1] * -1 * amount)
        await self.bot.edit_inventory(interaction.user, item, amount)
        await self.bot.response(interaction, f'Purchased `{amount}x {item}`!', self.bot.colour(interaction.guild))

    @buy.autocomplete('item')
    async def buy_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        item_list = []
        for item in await self.bot.item_shop():
            if current.lower() in item.lower():
                item_list.append(app_commands.Choice(name=item, value=item))
        return item_list


async def setup(bot: GamBot):
    await bot.add_cog(Inventory(bot))
