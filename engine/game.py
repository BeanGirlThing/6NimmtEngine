import logging

from engine import Deck
from engine import Hand
from engine import Card
from players import Player
class Game(object):
    deck = None
    columns = None
    logger = None

    def __init__(self, game_number: int):
        logging.getLogger(f"6NimmtEngine.Game {game_number}")

    def setup_game(self):
        self.logger.debug("Generating deck & shuffling")
        self.deck = Deck()
        self.deck.shuffle()
        self.columns = []

        self.logger.debug("Draw the initial cards for the 4 columns")
        for i in range(0, 4):
            self.columns.append([self.deck.deal()])

        self.logger.debug("Generating player hands")
        hands = []
        for i in range(0, len(self.player_list)):
            hands.append(Hand())
        for i in range(0, 10):
            for j in range(0, len(hands)):
                hands[j].add_card(self.deck.deal())

        self.logger.debug("Passing hands to players")
        for i, player in enumerate(self.player_list):
            player.set_hand(hands[i])

        if self.SHOW_GAME:
            self.display_table()
        if self.WAIT_FOR_MODERATOR:
            input("(Press Enter To Start Game)")

    def game(self) -> Player:
        played_cards = []
        for i in range(0, 10):
            self.logger.debug(f"Round {i}")
            previous_round_played_cards = []
            if played_cards:
                previous_round_played_cards = played_cards
            played_cards = []
            self.logger.debug("Running the turn method within the bots")
            for player_index, player in enumerate(self.player_list):
                played_cards.append((player_index, player.turn(self.columns, previous_round_played_cards)))

            self.logger.debug("Sorting and processing played cards")
            played_cards.sort(key=lambda individual_card: individual_card[1].value, reverse=False)
            for player_index, card_played in played_cards:
                column_to_place = None
                column_difference = 0

                # Determine whether card played is lower than all columns, if not, which column does it follow
                for j, column in enumerate(self.columns):
                    if card_played.value > column[len(column) - 1].value:
                        if column_to_place is None:
                            column_to_place = j
                            column_difference = card_played.value - column[len(column) - 1].value
                        else:
                            if column_difference > card_played.value - column[len(column) - 1].value:
                                column_to_place = j
                                column_difference = card_played.value - column[len(column) - 1].value

                # Handle card played being lower than all columns
                if column_to_place is None:
                    selected_column = self.player_list[player_index].take_selected_row(self.columns, played_cards)
                    for card in self.columns[selected_column]:
                        self.player_list[player_index].add_to_score(card.score)

                    self.columns[selected_column] = [card_played]

                else:
                    # Handle card placed into column being 6th
                    if len(self.columns[column_to_place]) == 5:
                        for card in self.columns[column_to_place]:
                            self.player_list[player_index].add_to_score(card.score)
                        self.columns[column_to_place] = [card_played]
                    else:
                        # If all other handles are not run, the card can be placed into the column without consequence
                        self.columns[column_to_place].append(card_played)
            if self.SHOW_GAME:
                print("Table")
                self.display_table()
                print("Played Cards For Round")
                self.display_played(played_cards)
                print("Current Player Scores")
                self.display_player_scores()
            if self.WAIT_FOR_MODERATOR:
                input("(Enter to Continue)")

        # Determine the winner
        self.logger.info("Game Over - Determining a winner")
        lowest_score = None
        for player in self.player_list:
            if lowest_score is None:
                lowest_score = player
            else:
                if lowest_score.score > player.score:
                    lowest_score = player
        return lowest_score

    def display_table(self):
        table = PrettyTable()
        table.field_names = ["1", "2", "3", "4"]
        for i in range(0, 6):
            row = []
            for column in self.columns:
                if len(column) - 1 < i:
                    row.append(" ")
                else:
                    row.append(f"V{column[i].value} S{column[i].score}")
            table.add_row(row, divider=True)
        print(table)

    def display_played(self, played_cards):
        table = PrettyTable()
        player_names = []
        list_of_cards = []
        for card in played_cards:
            player_names.append(self.player_list[card[0]].name)
            list_of_cards.append(f"V{card[1].value} S{card[1].score}")
        table.field_names = player_names
        table.add_row(list_of_cards)
        print(table)

    def display_player_scores(self):
        table = PrettyTable()
        player_names = []
        player_scores = []
        for player in self.player_list:
            player_names.append(player.name)
            player_scores.append(player.score)
        table.field_names = player_names
        table.add_row(player_scores)
        print(table)
