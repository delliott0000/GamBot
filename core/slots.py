from main import GamBot
from discord import (
    ui,
    Interaction,
    Button,
    ButtonStyle,
    Embed
)
from config import slot_num_to_emote as s_n_e


class SlotsView(ui.View):
    def __init__(self, bot: GamBot, interaction: Interaction):
        super().__init__(timeout=120)
        self.bot = bot
        self.interaction = interaction

    @ui.button(label='View Payouts', emoji=s_n_e[0], style=ButtonStyle.grey)
    async def payouts(self, interaction: Interaction, button: Button):
        payouts_embed = Embed(
            colour=self.bot.colour(interaction.guild),
            title='Slots and Payouts',
            description=f'{s_n_e[1]} {s_n_e[1]} {s_n_e[1]} = Your Bet x1\n'
                        f'{s_n_e[2]} {s_n_e[2]} {s_n_e[2]} = Your Bet x2\n'
                        f'{s_n_e[3]} {s_n_e[3]} {s_n_e[3]} = Your Bet x3\n'
                        f'{s_n_e[4]} {s_n_e[4]} {s_n_e[4]} = Your Bet x5\n'
                        f'{s_n_e[5]} {s_n_e[5]} {s_n_e[5]} = Your Bet x8\n'
                        f'{s_n_e[6]} {s_n_e[6]} {s_n_e[6]} = Your Bet x10\n'
                        f'{s_n_e[7]} {s_n_e[7]} {s_n_e[7]} = Your Bet x25\n'
                        f'{s_n_e[8]} {s_n_e[0]} {s_n_e[0]} = Your Bet x5\n'
                        f'{s_n_e[8]} {s_n_e[8]} {s_n_e[0]} = Your Bet x15\n'
                        f'{s_n_e[8]} {s_n_e[8]} {s_n_e[8]} = Your Bet x50\n'
                        f'{s_n_e[9]} {s_n_e[9]} {s_n_e[9]} = Your Bet x100')
        payouts_embed.set_author(name='Slots', icon_url=self.bot.user.avatar)
        await interaction.response.send_message(embed=payouts_embed, ephemeral=True)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user == self.interaction.user:
            return True
        await self.bot.bad_response(interaction, '❌ This is not your game.')
        return False

    async def on_timeout(self):
        self.payouts.disabled = True
        await self.interaction.edit_original_response(view=self)