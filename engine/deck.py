from card import Card
from random import shuffle


class NotEnoughCardsError(Exception):
    def __init__(self, message):
        self.message = message


class Deck(object):
    deck_list = None

    def __init__(self):
        self.deck_list = []

        for i in range(1, 105):
            score = 1
            if "5" in str(i):
                score = 2
            if i % 10 == 0:
                score = 3
            if 10 <= i <= 99:
                if list(str(i))[0] == list(str(i))[1]:
                    score = 5
            if i == 55:
                score = 7

            self.deck_list.append(Card(i, score))

    def shuffle(self):
        shuffle(self.deck_list)

    def deal(self):
        if len(self.deck_list) == 0:
            raise NotEnoughCardsError("Deck is empty")
        return self.deck_list.pop()
