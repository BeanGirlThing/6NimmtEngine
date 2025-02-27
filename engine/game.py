import multiprocessing

from engine.deck import Deck
from engine.hand import Hand
from prettytable import PrettyTable
import logging
from enlighten import Manager
from players import Player

class Game(object):
    configuration = []
    game_number = None
    enlighten_manager = None

    program_config = None

    SHOW_GAME = False
    WAIT_FOR_MODERATOR = False

    GAMES_TO_PLAY = None

    deck = None
    columns = None

    def __init__(self, configuration_number: int, configuration: list, enlighten_manager: Manager, program_config):
        self.configuration = configuration
        self.program_config = program_config
        self.game_number = configuration_number
        self.enlighten_manager = enlighten_manager

        # Get SHOW_GAME variable from config
        if int(self.program_config["game"]["show"]) == 1:
            self.SHOW_GAME = True

        # Get WAIT_FOR_MODERATOR variable from config
        if int(self.program_config["game"]["wait_for_moderator"]) == 1:
            self.WAIT_FOR_MODERATOR = True

        self.GAMES_TO_PLAY = int(self.program_config["engine"]["games_to_play"])

    def setup_game(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.columns = []

        for i in range(0, 4):
            self.columns.append([self.deck.deal()])
        hands = []
        for i in range(0, len(self.configuration)):
            hands.append(Hand())
        for i in range(0, 10):
            for j in range(0, len(hands)):
                hands[j].add_card(self.deck.deal())

        for i, player in enumerate(self.configuration):
            player.set_hand(hands[i])

        if self.SHOW_GAME:
            self.display_table()
        if self.WAIT_FOR_MODERATOR:
            input("(Press Enter To Start Game)")

    def game(self):
        progress_bar = self.enlighten_manager.counter(total=self.GAMES_TO_PLAY,
                                  desc=f"Configuration {self.game()}/{len(list(self.configuration))}", unit="games",
                                  color="green")
        played_cards = []
        for i in range(0, 10):
            previous_round_played_cards = []
            if played_cards:
                previous_round_played_cards = played_cards
            played_cards = []
            for player_index, player in enumerate(self.configuration):
                played_cards.append((player_index, player.turn(self.columns, previous_round_played_cards, round_number=i)))

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
                    selected_column = self.configuration[player_index].take_selected_row(self.columns, played_cards)
                    for card in self.columns[selected_column]:
                        self.configuration[player_index].add_to_score(card.score)

                    self.columns[selected_column] = [card_played]

                else:
                    # Handle card placed into column being 6th
                    if len(self.columns[column_to_place]) == 5:
                        for card in self.columns[column_to_place]:
                            self.configuration[player_index].add_to_score(card.score)
                        self.columns[column_to_place] = [card_played]
                    else:
                        # If all other handles are not run, the card can be placed into the column without consequence
                        self.columns[column_to_place].append(card_played)
            if self.SHOW_GAME:
                print("Table")
                self.display_table()
                print("Played Cards For Round")
                self.display_played(played_cards, self.configuration)
                print("Current Player Scores")
                self.display_player_scores(self.configuration)
            if self.WAIT_FOR_MODERATOR:
                input("(Enter to Continue)")

            progress_bar.update()

        # Determine the winner
        lowest_score = None
        for player in self.configuration:
            if lowest_score is None:
                lowest_score = player
            else:
                if lowest_score.score > player.score:
                    lowest_score = player
        return None

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

    def display_played(self, played_cards, configuration):
        table = PrettyTable()
        player_names = []
        list_of_cards = []
        for card in played_cards:
            player_names.append(configuration[card[0]].name)
            list_of_cards.append(f"V{card[1].value} S{card[1].score}")
        table.field_names = player_names
        table.add_row(list_of_cards)
        print(table)

    def display_player_scores(self, configuration):
        table = PrettyTable()
        player_names = []
        player_scores = []
        for player in configuration:
            player_names.append(player.name)
            player_scores.append(player.score)
        table.field_names = player_names
        table.add_row(player_scores)
        print(table)