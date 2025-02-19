from hand import Hand
from card import Card


class Player:
    hand: Hand = None
    name: str = None
    score: int = 0

    def __init__(self, name: str):
        self.name = name

    def set_hand(self, hand: Hand):
        self.hand = hand

    def turn(self, game_board, previous_round_played_cards: list) -> Card:
        return Card(0, 0)

    def add_to_score(self, score: int):
        self.score += score

    def take_selected_row(self, game_board, current_round_played_cards: list) -> int:
        return 0

    def reset(self):
        self.score = 0
        self.hand = None
