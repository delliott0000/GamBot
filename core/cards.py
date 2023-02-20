from main import GamBot
from discord import (
    ui,
    Interaction,
    Button,
    ButtonStyle,
    Embed,
    User,
    Member
)
from config import (
    higher_lower_emotes as hl_emotes,
    cards_to_emotes as c_emotes,
    blackjack_emotes as bj_emotes,
    poker_emotes
)
from random import choice
from math import floor
from typing import Union
from itertools import combinations as combos


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

        Embed.__init__(self, colour=bot.colour(interaction.guild),
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

    async def on_timeout(self):
        self.higher.disabled = True
        self.lower.disabled = True
        self.cash_out.disabled = True
        self.add_field(name='Timed Out!', value='🕐 You ran out of time to play!', inline=False)
        await self.interaction.edit_original_response(embed=self, view=self)


class Blackjack(ui.View, Embed, Cards):
    def __init__(self, bot: GamBot, interaction: Interaction, bet: int):
        ui.View.__init__(self, timeout=120)

        Cards.__init__(self)
        for i in range(2):
            self.deal_card(self.p1)
            self.deal_card(self.dealer)

        Embed.__init__(self, colour=bot.colour(interaction.guild))
        self.set_author(name='Blackjack', icon_url=bot.user.avatar)

        self.bot = bot
        self.interaction = interaction
        self.bet = bet

    @staticmethod
    def bj_eval(hand: list):
        total = 0
        ace_11s = 0
        for card in hand:
            if card in range(1, 33):
                total += (card + 7) // 4
            elif card in range(33, 49):
                total += 10
            else:
                total += 11
                ace_11s += 1
        while ace_11s and total > 21:
            ace_11s -= 1
            total -= 10
        return total

    def update_embed(self, dealer_known: bool = False):
        self.remove_field(0)
        self.remove_field(0)
        self.description = f'{self.interaction.user.mention} **(Total Bet: `${self.bet:,}`)**'
        self.add_field(
            name=f'Your Cards | {self.bj_eval(self.p1)} Points', value=''.join([c_emotes[card] for card in self.p1]))
        self.add_field(
            name=f'Dealer\'s Cards | ' + (f'{self.bj_eval(self.dealer)}' if dealer_known else
                                          f'{self.bj_eval(self.dealer[:-1])} + X') + ' Points', inline=False,
            value=''.join([c_emotes[card] for card in self.dealer]) if dealer_known else
            ''.join([c_emotes[card] for card in self.dealer[:-1]]) + c_emotes[0])

    async def update_button(self):
        self.double.disabled = not (self.bj_eval(self.p1) in range(9, 12) and len(self.p1) == 2 and
                                    await self.bot.money(self.interaction.user) >= self.bet)

    async def end_game(self):
        self.stop()

        if self.bj_eval(self.p1) > 21:
            self.update_embed()
            self.add_field(value='😖 You went bust, best be careful next time!',
                           name='Loser!', inline=False)
            await self.interaction.edit_original_response(embed=self, view=None)
            return

        while self.bj_eval(self.dealer) < 17:
            self.deal_card(self.dealer)

        self.update_embed(dealer_known=True)

        if self.bj_eval(self.dealer) > 21:
            winnings = floor(self.bet * await self.bot.pay_mult(self.interaction.user))
            xp_gain = floor(self.bet * await self.bot.xp_mult(self.interaction.user) / 100)
            self.add_field(value=f'😁 The dealer went bust, you win `${winnings:,}`.',
                           name='Winner!', inline=False)
            winnings += self.bet

        elif self.bj_eval(self.p1) == self.bj_eval(self.dealer):
            winnings = self.bet
            xp_gain = 0
            self.add_field(value=f'🧐 You both scored the same amounts of points. Your bet will be returned.',
                           name='Tie!', inline=False)

        elif self.bj_eval(self.p1) > self.bj_eval(self.dealer):
            winnings = floor(self.bet * await self.bot.pay_mult(self.interaction.user))
            xp_gain = floor(self.bet * await self.bot.xp_mult(self.interaction.user) / 100)
            self.add_field(value=f'💎 You scored higher than the dealer! You win `${winnings:,}`.',
                           name='Winner!', inline=False)
            winnings += self.bet

        else:
            winnings = 0
            xp_gain = 0
            self.add_field(value='😢 The dealer scored higher, you lose!',
                           name='Loser!', inline=False)

        await self.bot.edit_balances(self.interaction, self.interaction.user, money_d=winnings, xp_d=xp_gain)
        await self.interaction.edit_original_response(embed=self, view=None)

        if self.bj_eval(self.p1) == 21 and [(card + 7) // 4 for card in self.p1] == [7, 7, 7]:
            await self.bot.add_achievement(self.interaction, self.interaction.user, 'bj_sevens')
        if self.bet >= 200000 and (self.bj_eval(self.dealer) > 21 or self.bj_eval(self.p1) > self.bj_eval(self.dealer)):
            await self.bot.add_achievement(self.interaction, self.interaction.user, 'bj_max')

    @ui.button(label='Draw', emoji=bj_emotes['draw'], style=ButtonStyle.green)
    async def draw(self, interaction: Interaction, button: Button):
        await interaction.response.defer()
        self.deal_card(self.p1)

        if self.bj_eval(self.p1) >= 21:
            await self.end_game()

        else:
            self.update_embed()
            await self.update_button()
            await self.interaction.edit_original_response(embed=self, view=self)

    @ui.button(label='Stand', emoji=bj_emotes['stand'], style=ButtonStyle.red)
    async def stand(self, interaction: Interaction, button: Button):
        await interaction.response.defer()

        await self.end_game()

    @ui.button(label='Double Down', emoji=bj_emotes['dd'], style=ButtonStyle.blurple)
    async def double(self, interaction: Interaction, button: Button):
        await interaction.response.defer()

        await self.bot.edit_balances(interaction, interaction.user, money_d=self.bet * -1)
        self.bet *= 2
        self.deal_card(self.p1)

        await self.end_game()

    async def interaction_check(self, interaction: Interaction):
        if interaction.user == self.interaction.user:
            return True
        await self.bot.bad_response(interaction, '❌ This is not your game.')
        return False

    async def on_timeout(self):
        self.draw.disabled = True
        self.stand.disabled = True
        self.double.disabled = True
        self.add_field(name='Timed Out!', value='🕐 You ran out of time to play!', inline=False)
        await self.interaction.edit_original_response(embed=self, view=self)


class PokerLobby(ui.View, Embed):
    def __init__(self, bot: GamBot, interaction: Interaction, start_bet: int):
        ui.View.__init__(self, timeout=120)

        Embed.__init__(self, colour=bot.colour(interaction.guild), title='Waiting For Players...',
                       description=f'Poker requires 2-4 players to begin. Starting bet is `${start_bet:,}` each. '
                                   'Claim a seat to join in, or click \'Start\' as the host to begin the game!\n\n'
                                   '**Game will automatically be cancelled after 2 minutes!**')
        self.set_author(name='Poker', icon_url=bot.user.avatar)
        self.set_thumbnail(url='https://cdn.discordapp.com/emojis/950441600201392178.webp?size=128&quality=lossless')

        self.bot = bot
        self.interaction = interaction
        self.start_bet = start_bet

        self.u1 = interaction.user
        self.u2 = None
        self.u3 = None
        self.u4 = None
        self.update_embed()

    def update_embed(self):
        self.remove_field(0)
        self.add_field(name='Players:', value=f'Player 1: {self.interaction.user.mention} **(Host)**\n'
                                              f'Player 2: {self.u2.mention if self.u2 else "`None`"}\n'
                                              f'Player 3: {self.u3.mention if self.u3 else "`None`"}\n'
                                              f'Player 4: {self.u4.mention if self.u4 else "`None`"}')

    def update_buttons(self):
        self.start.disabled = not self.u2 and not self.u3 and not self.u4
        self.seat_2.disabled = bool(self.u2)
        self.seat_3.disabled = bool(self.u3)
        self.seat_4.disabled = bool(self.u4)

    async def cancel_game(self):
        self.stop()
        self.remove_field(0)
        self.title = 'Game Cancelled!'
        self.description = '**Run `/poker` again to set up a new game.**'
        await self.interaction.edit_original_response(embed=self, view=None)

    @ui.button(label='Start Game', emoji=poker_emotes['start'], style=ButtonStyle.green, disabled=True)
    async def start(self, interaction: Interaction, button: Button):
        if interaction.user != self.interaction.user:
            await self.bot.bad_response(interaction, '❌ You\'re not the host of this game.')
            return

        for user in [self.u1, self.u2, self.u3, self.u4]:
            if user:
                await self.bot.edit_balances(interaction, user, money_d=self.start_bet * -1)

        await interaction.response.defer()
        poker_game = Poker(self.bot, self.interaction, self.start_bet, self.u1, self.u2, self.u3, self.u4)
        await self.interaction.edit_original_response(embed=poker_game, view=poker_game)
        self.stop()

    @ui.button(label='Seat 2', emoji=poker_emotes['seat'], style=ButtonStyle.blurple)
    async def seat_2(self, interaction: Interaction, button: Button):
        if interaction.user in [self.u1, self.u2, self.u3, self.u4]:
            await self.bot.bad_response(interaction, '❌ You\'re already in this game.')
            return
        elif await self.bot.money(interaction.user) < self.start_bet:
            await self.bot.bad_response(interaction, f'❌ Bets for this poker game start at `${self.start_bet:,}`.')
            return

        await interaction.response.defer()
        self.u2 = interaction.user
        self.update_embed()
        self.update_buttons()
        await self.interaction.edit_original_response(embed=self, view=self)

    @ui.button(label='Seat 3', emoji=poker_emotes['seat'], style=ButtonStyle.blurple)
    async def seat_3(self, interaction: Interaction, button: Button):
        if interaction.user in [self.u1, self.u2, self.u3, self.u4]:
            await self.bot.bad_response(interaction, '❌ You\'re already in this game.')
            return
        elif await self.bot.money(interaction.user) < self.start_bet:
            await self.bot.bad_response(interaction, f'❌ Bets for this poker game start at `${self.start_bet:,}`.')
            return

        await interaction.response.defer()
        self.u3 = interaction.user
        self.update_embed()
        self.update_buttons()
        await self.interaction.edit_original_response(embed=self, view=self)

    @ui.button(label='Seat 4', emoji=poker_emotes['seat'], style=ButtonStyle.blurple)
    async def seat_4(self, interaction: Interaction, button: Button):
        if interaction.user in [self.u1, self.u2, self.u3, self.u4]:
            await self.bot.bad_response(interaction, '❌ You\'re already in this game.')
            return
        elif await self.bot.money(interaction.user) < self.start_bet:
            await self.bot.bad_response(interaction, f'❌ Bets for this poker game start at `${self.start_bet:,}`.')
            return

        await interaction.response.defer()
        self.u4 = interaction.user
        self.update_embed()
        self.update_buttons()
        await self.interaction.edit_original_response(embed=self, view=self)

    @ui.button(label='Cancel Game', emoji=poker_emotes['cancel'], style=ButtonStyle.red)
    async def cancel(self, interaction: Interaction, button: Button):
        if interaction.user != self.interaction.user:
            await self.bot.bad_response(interaction, '❌ You\'re not the host of this game.')
            return
        await self.cancel_game()

    async def interaction_check(self, interaction: Interaction):
        if not await self.bot.is_blacklisted(interaction.user):
            return True
        await self.bot.blacklisted_response(interaction)
        return False

    async def on_timeout(self):
        await self.cancel_game()


class Poker(ui.View, Embed, Cards):
    def __init__(self, bot: GamBot, interaction: Interaction, start_bet: int,
                 u1: Union[Member, User, None], u2: Union[Member, User, None],
                 u3: Union[Member, User, None], u4: Union[Member, User, None]):
        ui.View.__init__(self, timeout=240)

        Cards.__init__(self)
        for i in range(2):
            self.deal_card(self.p1)
            self.deal_card(self.p2)
            self.deal_card(self.p3)
            self.deal_card(self.p4)
        for i in range(5):
            self.deal_card(self.dealer)

        self.player_mapping = {}
        for user in [u1, u2, u3, u4]:
            if user:
                cards = self.__getattribute__(f'p{[u1, u2, u3, u4].index(user) + 1}')
                best_hand = self.compare_hands([list(combo) + cards for combo in combos(self.dealer, 3)])
                self.player_mapping[user] = {
                    'cards': cards, 'bet': start_bet, 'vote': False, 'folded': False, 'best_hand': best_hand}

        Embed.__init__(self, colour=bot.colour(interaction.guild), title='Let\'s Play!',
                       description=f'**Player 1:** {u1.mention if u1 else "`None`"}\n'
                                   f'**Player 2:** {u2.mention if u2 else "`None`"}\n'
                                   f'**Player 3:** {u3.mention if u3 else "`None`"}\n'
                                   f'**Player 4:** {u4.mention if u4 else "`None`"}')
        self.set_author(name='Poker', icon_url=bot.user.avatar)
        self.set_thumbnail(url='https://cdn.discordapp.com/emojis/950441600201392178.webp?size=128&quality=lossless')

        self.bot = bot
        self.interaction = interaction
        self.start_bet = start_bet
        self.max_bet = start_bet * 8
        self.phase = 0

        self.update_embed()

        self.hand_mapping = {1: 'High Card', 2: 'Pair', 3: '2 Pairs', 4: '3 Of A Kind', 5: 'Straight', 6: 'Flush',
                             7: 'Full House', 8: '4 Of A Kind', 9: 'Straight Flush', 10: 'Royal Flush'}

    def update_embed(self):
        for i in range(7):
            self.remove_field(0)
        self.add_field(
            name='Table Cards:',
            value=c_emotes[0] * 5 if not self.phase else
            ''.join([c_emotes[card] for card in self.dealer[:self.phase + 2]]) + c_emotes[0] * (3 - self.phase),
            inline=False)
        for player in self.player_mapping:
            self.add_field(
                name=f'{player.name}{" [Folded]" if self.player_mapping[player]["folded"] else ""}:',
                value=f'Total Bet: `${self.player_mapping[player]["bet"]:,}`')
        self.add_field(
            name='Total:',
            value=f'Betting pool: `${sum([self.player_mapping[p]["bet"] for p in self.player_mapping]):,}`',
            inline=False)
        vote_y = len([p for p in self.player_mapping if self.player_mapping[p]['vote']
                      and not self.player_mapping[p]['folded']])
        vote_n = len([p for p in self.player_mapping if not self.player_mapping[p]['vote']
                      and not self.player_mapping[p]['folded']])
        self.add_field(
            name='Votes To Play On:',
            value=f'{poker_emotes["start"] * vote_y + poker_emotes["cancel"] * vote_n} **({vote_y}/{vote_y+vote_n})**',
            inline=False)

    def update_button(self):
        self.progress.disabled = bool(len(set(self.player_mapping[player]['bet'] for player in self.player_mapping))-1)

    async def update_bet(self, interaction: Interaction, bet_delta: int):
        if await self.bot.money(interaction.user) < bet_delta:
            await self.bot.bad_response(interaction, '❌ You can\'t afford that bet.')
            return
        elif self.player_mapping[interaction.user]['bet'] + bet_delta > self.max_bet:
            await self.bot.bad_response(interaction, f'❌ The maximum bet for this game is `${self.max_bet:,}`.')
            return

        await interaction.response.defer()

        await self.bot.edit_balances(interaction, interaction.user, money_d=bet_delta * -1)
        self.player_mapping[interaction.user]['bet'] += bet_delta
        for user in self.player_mapping:
            self.player_mapping[user]['vote'] = False

        self.update_embed()
        self.update_button()
        await self.interaction.edit_original_response(embed=self, view=self)

    @staticmethod
    def full_hand_eval(hand: list):
        hand.sort(reverse=True)
        hand_vals = [(card + 7) // 4 for card in hand]
        hand_vals.sort(reverse=True)

        def check_straight_flush():
            if check_flush() and hand_vals == [14, 13, 12, 11, 10]:
                return [10] + [0] * 5
            elif check_flush() and hand_vals == [14, 5, 4, 3, 2]:
                return [9, 5] + [0] * 4
            elif check_flush() and check_straight():
                return [9, max(hand_vals)] + [0] * 4
            return

        def check_four():
            if len(set(hand_vals[:-1])) == 1 or len(set(hand_vals[1:])) == 1:
                return [8, hand_vals[1]] + [0] * 4
            return

        def check_full_house():
            if len(set(hand_vals[0:3])) == 1 and len(set(hand_vals[3:])) == 1:
                return [7, hand_vals[0], hand_vals[3]] + hand[:3]
            elif len(set(hand_vals[0:2])) == 1 and len(set(hand_vals[2:])) == 1:
                return [7, hand_vals[3], hand_vals[0]] + hand[2:]
            return

        def check_flush():
            suits = {card % 4 for card in hand}
            if len(suits) == 1:
                return [6] + hand_vals
            return

        def check_straight():
            if len(set(hand_vals)) == 5 and max(set(hand_vals)) - min(set(hand_vals)) == 4:
                return [5, max(set(hand_vals))] + hand[:4]
            elif set(hand_vals) == {14, 2, 3, 4, 5}:
                return [5, 5] + hand[1:]
            return

        def check_three():
            if len(set(hand_vals[:3])) == 1:
                return [4, hand_vals[0], hand_vals[3], hand_vals[4]] + hand[:2]
            elif len(set(hand_vals[1:4])) == 1:
                return [4, hand_vals[1], hand_vals[0], hand_vals[4]] + hand[1:3]
            elif len(set(hand_vals[2:])) == 1:
                return [4, hand_vals[2], hand_vals[0], hand_vals[1]] + hand[2:4]
            return

        def check_two_pair():
            if hand_vals[0] == hand_vals[1] and hand_vals[2] == hand_vals[3]:
                return [3, hand_vals[0], hand_vals[2], hand_vals[4]] + hand[:2]
            elif hand_vals[0] == hand_vals[1] and hand_vals[3] == hand_vals[4]:
                return [3, hand_vals[0], hand_vals[3], hand_vals[2]] + hand[:2]
            elif hand_vals[1] == hand_vals[2] and hand_vals[3] == hand_vals[4]:
                return [3, hand_vals[1], hand_vals[3], hand_vals[0]] + hand[1:3]
            return

        def check_pair():
            if hand_vals[0] == hand_vals[1]:
                return [2, hand_vals[0], hand_vals[2], hand_vals[3], hand_vals[4], hand[0]]
            elif hand_vals[1] == hand_vals[2]:
                return [2, hand_vals[1], hand_vals[0], hand_vals[3], hand_vals[4], hand[1]]
            elif hand_vals[2] == hand_vals[3]:
                return [2, hand_vals[2], hand_vals[0], hand_vals[1], hand_vals[4], hand[2]]
            elif hand_vals[3] == hand_vals[4]:
                return [2, hand_vals[3], hand_vals[0], hand_vals[1], hand_vals[2], hand[3]]
            return

        def check_high_card():
            return [1] + hand_vals

        return (check_straight_flush() or check_four() or check_full_house() or check_flush() or check_straight() or
                check_three() or check_two_pair() or check_pair() or check_high_card())

    def compare_hands(self, hands: list):
        best_hand = [0] * 5
        best_hand_data = [0] * 6
        for hand in hands:
            current_data = self.full_hand_eval(hand)
            if current_data[0] < best_hand_data[0]:
                pass
            elif current_data[0] == best_hand_data[0] and current_data[1] < best_hand_data[1]:
                pass
            elif current_data[0] == best_hand_data[0] and current_data[1] == best_hand_data[1] and \
                    current_data[2] < best_hand_data[2]:
                pass
            elif current_data[0] == best_hand_data[0] and current_data[1] == best_hand_data[1] and \
                    current_data[2] == best_hand_data[2] and current_data[3] < best_hand_data[3]:
                pass
            elif current_data[0] == best_hand_data[0] and current_data[1] == best_hand_data[1] and \
                    current_data[2] == best_hand_data[2] and current_data[3] == best_hand_data[3] and \
                    current_data[4] < best_hand_data[4]:
                pass
            elif current_data[0] == best_hand_data[0] and current_data[1] == best_hand_data[1] and \
                    current_data[2] == best_hand_data[2] and current_data[3] == best_hand_data[3] and \
                    current_data[4] == best_hand_data[4] and current_data[5] < best_hand_data[5]:
                pass
            else:
                best_hand = hand
                best_hand_data = current_data
        return best_hand

    async def end_game(self, by_fold: bool = False):
        self.stop()

        self.remove_field(-1)
        for player in self.player_mapping:
            self.add_field(
                name=f'{player.name}\'s Hand:',
                value=''.join([c_emotes[card] for card in self.player_mapping[player]["best_hand"]]) +
                      f' **({self.hand_mapping[self.full_hand_eval(self.player_mapping[player]["best_hand"])[0]]})**')

        potential_winners = {
            p: self.player_mapping[p]['best_hand'] for p in self.player_mapping if not self.player_mapping[p]['folded']}
        winning_hand = self.compare_hands([potential_winners[player] for player in potential_winners])
        winner = [player for player in potential_winners if potential_winners[player] == winning_hand][0]

        winnings = sum([self.player_mapping[p]["bet"] for p in self.player_mapping])
        await self.bot.edit_balances(self.interaction, winner, money_d=winnings)

        self.add_field(
            name=f'Winner: {winner.name}!', inline=False,
            value=f'💎 {winner.mention} won by {"having the best hand" if not by_fold else "making the others fold"}! '
                  f'They win `${winnings:,}`!')

        await self.interaction.edit_original_response(embed=self, view=None)

        if winnings >= 1000000:
            await self.bot.add_achievement(self.interaction, winner, 'poker_max')
        if self.full_hand_eval(winning_hand)[0] >= 9:
            await self.bot.add_achievement(self.interaction, winner, 'poker_sf')

    @ui.button(label='View Your Cards', emoji=c_emotes[0], style=ButtonStyle.grey)
    async def view_cards(self, interaction: Interaction, button: Button):
        await interaction.response.send_message(
            ''.join([c_emotes[card] for card in self.player_mapping[interaction.user]['cards']]), ephemeral=True)

    @ui.button(label='Play On', emoji=poker_emotes['start'], style=ButtonStyle.green)
    async def progress(self, interaction: Interaction, button: Button):
        if self.player_mapping[interaction.user]['vote']:
            await self.bot.bad_response(interaction, '❌ You\'ve already voted to play on.')
            return

        await interaction.response.defer()
        self.player_mapping[interaction.user]['vote'] = True

        if False in [self.player_mapping[p]['vote'] for p in self.player_mapping
                     if not self.player_mapping[p]['folded']]:
            self.update_embed()
            await self.interaction.edit_original_response(embed=self)
            return

        for player in self.player_mapping:
            self.player_mapping[player]['vote'] = False

        if self.phase == 3:
            await self.end_game()
            return

        self.phase += 1
        self.update_embed()
        await self.interaction.edit_original_response(embed=self)

    @ui.button(label='Place Small Bet', emoji=poker_emotes['small_bet'], style=ButtonStyle.blurple)
    async def small_bet(self, interaction: Interaction, button: Button):
        await self.update_bet(interaction, self.start_bet // 5)

    @ui.button(label='Place Large Bet', emoji=poker_emotes['big_bet'], style=ButtonStyle.blurple)
    async def big_bet(self, interaction: Interaction, button: Button):
        await self.update_bet(interaction, self.start_bet)

    @ui.button(label='Fold', emoji=poker_emotes['cancel'], style=ButtonStyle.red)
    async def fold(self, interaction: Interaction, button: Button):
        self.player_mapping[interaction.user]['folded'] = True

        if len([p for p in self.player_mapping if not self.player_mapping[p]['folded']]) == 1:
            await self.end_game(by_fold=True)
            return

        await interaction.response.defer()
        self.update_embed()
        self.update_button()
        await self.interaction.edit_original_response(embed=self, view=self)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user not in self.player_mapping:
            await self.bot.bad_response(interaction, '❌ This is not your game.')
            return False
        elif self.player_mapping[interaction.user]['folded']:
            await self.bot.bad_response(interaction, '❌ You have already folded.')
            return False
        return True

    async def on_timeout(self):
        self.view_cards.disabled = True
        self.progress.disabled = True
        self.small_bet.disabled = True
        self.big_bet.disabled = True
        self.fold.disabled = True

        if True in [self.player_mapping[player]['vote'] for player in self.player_mapping]:
            refunded_players = [player for player in self.player_mapping if self.player_mapping[player]['vote']]
        else:
            refunded_players = [player for player in self.player_mapping if self.player_mapping[player]['bet'] ==
                                max([self.player_mapping[p]['bet'] for p in self.player_mapping])]

        for player in refunded_players:
            await self.bot.edit_balances(self.interaction, player, self.player_mapping[player]['bet'])

        self.add_field(
            name='🕐 Game Expired!',
            value=f'Refunding the following player(s): '
                  f'`{", ".join([player.name for player in refunded_players]) if refunded_players else "None"}`',
            inline=False)
        await self.interaction.edit_original_response(embed=self, view=self)
