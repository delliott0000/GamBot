from main import GamBot
from discord import (
    app_commands,
    ui,
    Interaction,
    ButtonStyle,
    Embed
)
from random import randint
from config import slot_num_to_emote as s_n_e


class ScratchCard(ui.View, Embed):
    def __init__(self, bot: GamBot, interaction: Interaction, tier: app_commands.Choice):
        ui.View.__init__(self, timeout=120)

        Embed.__init__(self, colour=bot.colour(interaction.guild),
                       description=f'{interaction.user.mention} **(Tier: `{tier.name}`)**')
        self.set_author(name='Scratch Card', icon_url=bot.user.avatar)
        self.add_field(name='How To Win:',
                       value=f'{s_n_e[8]} Click the buttons to uncover what\'s underneath! '
                             'Get 3 of the same item in a row horizontally, vertically or diagonally to win a prize!')

        self.bot = bot
        self.interaction = interaction
        self.tier = tier

        self.results = {}
        for i in range(1, 10):
            self.results[i] = randint(1, 9)
            self.results[i] += {'Common': -2, 'Uncommon': -1, 'Rare': 0, 'Epic': 1, 'Legendary': 2}[tier.name]
            if self.results[i] < 1:
                self.results[i] = 1
            elif self.results[i] > 9:
                self.results[i] = 9
            self.add_item(ScratchButton((i - 1) // 3, s_n_e[self.results[i]]))

    async def end_game(self):
        self.stop()
        for item in self.children:
            item.disabled = True

        gem_won = 0
        for array in [[1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 4, 7], [2, 5, 8], [3, 6, 9], [1, 5, 9], [3, 5, 7]]:
            if len(set([self.results[i] for i in array])) == 1 and self.results[array[0]] > gem_won:
                gem_won = self.results[array[0]]

        reward = {1: 'Common XP Booster', 2: 'Common Payout Booster', 3: 'Rare XP Booster',
                  4: 'Rare Payout Booster', 5: 'Small Gold Pack', 6: 'Epic XP Booster',
                  7: 'Epic Payout Booster', 8: 'Medium Gold Pack', 9: 'Large Gold Pack', 0: None}[gem_won]
        item_quantity = {'Common': 1, 'Uncommon': 1, 'Rare': 2, 'Epic': 2, 'Legendary': 3}[self.tier.name]

        if reward:
            await self.bot.edit_inventory(self.interaction.user, reward, item_quantity)
        if reward == 'Large Gold Pack':
            await self.bot.add_achievement(self.interaction, self.interaction.user, 'scrat_win')

        self.remove_field(0)
        self.add_field(
            name='Winner!' if reward else 'Loser!',
            value=s_n_e[gem_won] + (f' You win: `{item_quantity}x {reward}`!'if reward else
                                    ' You didn\'t win anything this time, try again!'))

        await self.interaction.edit_original_response(embed=self, view=self)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user == self.interaction.user:
            return True
        await self.bot.bad_response(interaction, '❌ This is not your scratch card.')
        return False


class ScratchButton(ui.Button):
    def __init__(self, row: int, gem: str):
        super().__init__(label='\u200b', emoji=s_n_e[0], style=ButtonStyle.grey, row=row)
        self.gem = gem
        self.scratched = False

    async def callback(self, interaction: Interaction):
        if self.scratched:
            await interaction.response.defer()
            return

        self.scratched = True
        self.style = ButtonStyle.blurple
        self.emoji = self.gem
        await interaction.response.edit_message(view=self.view)

        if False not in [item.scratched for item in self.view.children]:
            await self.view.end_game()
