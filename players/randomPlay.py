from players.Player import Player
from engine.card import Card
import random


class RandomPlay(Player):
    """
    Author: @BeanGal
    Description: Plays cards at random from hand
    """

    def __init__(self):
        super().__init__("Random")

    def turn(self, game_board, previous_round_played_cards: list) -> Card:
        return self.hand.remove_card(random.randint(0, len(self.hand.cards)-1))

    def take_selected_row(self, game_board, current_round_played_cards: list) -> int:
        # Random play takes a random column ¯\_(ツ)_/¯
        return random.randint(0,3)