from main import GamBot
from discord import (
    ui,
    Interaction,
    Button,
    ButtonStyle,
    Embed
)
from config import (
    higher_lower_emotes as hl_emotes,
    cards_to_emotes as c_emotes
)
from random import choice
from math import floor


class Cards:
    def __init__(self):
        self.deck = [i for i in range(1, 53)]
        self.dealer = []
        self.p1 = []
        self.p2 = []
        self.p3 = []
        self.p4 = []

    def deal_card(self, hand: list):
        card = choice(self.deck)
        self.deck.remove(card)
        hand.append(card)


class HigherOrLower(ui.View, Embed, Cards):
    def __init__(self, bot: GamBot, interaction: Interaction, bet: int):
        ui.View.__init__(self, timeout=120)

        Cards.__init__(self)
        for i in range(2):
            self.deal_card(self.p1)

        Embed.__init__(
            self,
            colour=bot.colour(interaction.guild),
            description=f'{interaction.user.mention} **(Total Bet: `${bet:,}`)**')
        self.set_author(name='Higher Or Lower', icon_url=bot.user.avatar)

        self.update_embed()
        self.update_button()

        self.bot = bot
        self.interaction = interaction
        self.bet = bet

    def update_embed(self):
        self.remove_field(0)
        self.add_field(name=f'Current Card: {c_emotes[self.p1[-2]]}',
                       value=''.join([c_emotes[card] for card in self.p1[:-1]]) + c_emotes[0])

    def update_button(self):
        self.cash_out.disabled = bool((len(self.p1) - 1) % 5)

    async def player_loss(self):
        self.stop()
        self.add_field(
            name='Loser!', value=f'The next card was {c_emotes[self.p1[-1]]}. Better luck next time!', inline=False)
        await self.interaction.edit_original_response(embed=self, view=None)

    @ui.button(label='Higher!', emoji=hl_emotes['higher'], style=ButtonStyle.blurple)
    async def higher(self, interaction: Interaction, button: Button):
        await interaction.response.defer()

        if self.p1[-1] < self.p1[-2]:
            await self.player_loss()
            return

        self.deal_card(self.p1)
        self.update_embed()
        self.update_button()
        await self.interaction.edit_original_response(embed=self, view=self)

        if len(self.p1) >= 26:
            await self.bot.add_achievement(interaction, interaction.user, 'hl_str')

    @ui.button(label='Lower!', emoji=hl_emotes['lower'], style=ButtonStyle.blurple)
    async def lower(self, interaction: Interaction, button: Button):
        await interaction.response.defer()

        if self.p1[-1] > self.p1[-2]:
            await self.player_loss()
            return

        self.deal_card(self.p1)
        self.update_embed()
        self.update_button()
        await self.interaction.edit_original_response(embed=self, view=self)

        if len(self.p1) >= 26:
            await self.bot.add_achievement(interaction, interaction.user, 'hl_str')

    @ui.button(label='Cash Out', emoji=hl_emotes['walk'], style=ButtonStyle.green)
    async def cash_out(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        self.stop()

        payout = floor(self.bet * await self.bot.pay_mult(interaction.user) * (2 ** ((len(self.p1) // 5) - 1)))
        xp_gain = floor((self.bet * await self.bot.xp_mult(interaction.user) * (2 ** ((len(self.p1) // 5) - 1))) / 100)
        await self.bot.edit_balances(interaction, interaction.user, money_d=payout + self.bet, xp_d=xp_gain)

        self.add_field(name='Winner!', value=f'💎 You win `${payout:,}`!', inline=False)
        await self.interaction.edit_original_response(embed=self, view=None)

        if payout >= 800000:
            await self.bot.add_achievement(interaction, interaction.user, 'hl_max')

    async def interaction_check(self, interaction: Interaction):
        if interaction.user == self.interaction.user:
            return True
        await self.bot.bad_response(interaction, '❌ This is not your game.')
        return False

    async def on_timeout(self) -> None:
        self.stop()
        self.higher.disabled = True
        self.lower.disabled = True
        self.cash_out.disabled = True
        self.add_field(name='Timed Out!', value='🕐 You ran out of time to play!', inline=False)
        await self.interaction.edit_original_response(embed=self, view=self)
