from players.Player import Player
from card import Card
from hand import Hand


class LowestHighest(Player):
    """
    Author: @BeanGal
    Description: Sorts hand when received in ascending order, then plays cards in that order
    """

    def __init__(self):
        super().__init__("Lowest -> Highest")

    def set_hand(self, hand: Hand):
        hand.cards.sort(key=lambda card: card.value, reverse=False)
        self.hand = hand

    def turn(self, game_board, previous_round_played_cards: list) -> Card:
        return self.hand.remove_card(0)

    def take_selected_row(self, game_board, current_round_played_cards: list) -> int:
        # Always take the lowest scoring column
        lowest_score_index = None
        lowest_score = None
        for i, column in enumerate(game_board):
            column_score = 0
            for card in column:
                column_score += card.score

            if lowest_score is None:
                lowest_score = column_score
                lowest_score_index = i
            else:
                if lowest_score > column_score:
                    lowest_score = column_score
                    lowest_score_index = i

        return lowest_score_index

