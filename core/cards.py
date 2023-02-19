from random import choice


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
