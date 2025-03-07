from card import Card


class Hand(object):
    cards = None

    def __init__(self):
        self.cards = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def remove_card(self, index) -> Card:
        return self.cards.pop(index)
