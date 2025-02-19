from deck import Deck
from hand import Hand
from configparser import ConfigParser
import players
from prettytable import PrettyTable
import json
import logging
from django.utils.text import slugify
import os
import sys
import datetime


def get_logfile_absolute_path(path: str = None):
    if path is None:
        path = os.getcwd() + "/logs"
    if not os.path.exists(path):
        os.makedirs(path)
    time_component = slugify(str(datetime.datetime.now().strftime("%m-%d-%Y--%H-%M-%S")))
    return f"{path}/6NimmtEngine-{time_component}.log"


class Main:
    columns = None
    deck = None
    config = None
    logger = None

    player_list = None

    SHOW_GAME = False
    WAIT_FOR_MODERATOR = False
    GAMES_TO_PLAY = 1

    data = {
        "player_names": [],
        "games": []
    }

    def __init__(self):
        # Logging Junk
        self.logger = logging.getLogger("6NimmtEngine")
        self.logger.setLevel(logging.DEBUG)
        logging_file_handler = logging.FileHandler(get_logfile_absolute_path())
        logging_file_handler.setLevel(logging.DEBUG)
        logging_stream_handler = logging.StreamHandler(sys.stdout)
        logging_stream_handler.setLevel(logging.INFO)

        logging_formatter = logging.Formatter(
            fmt='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S'
        )

        logging_file_handler.setFormatter(logging_formatter)
        logging_stream_handler.setFormatter(logging_formatter)

        self.logger.addHandler(logging_file_handler)
        self.logger.addHandler(logging_stream_handler)

        self.logger.info("Starting 6Nimmt Engine")

        self.player_list = [players.RandomPlay(), players.LowestHighest(), players.HighestLowest(),
                            players.LowestHighestSwap()]

        # Read the config file
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.logger.info("Read config file successfully")

        # Get SHOW_GAME variable from config
        if int(self.config["game"]["show"]) == 1:
            self.logger.info("Game is set to be shown in console - WARNING this may cause lag")
            self.SHOW_GAME = True

        # Get WAIT_FOR_MODERATOR variable from config
        if int(self.config["game"]["wait_for_moderator"]) == 1:
            self.logger.info("Game is set to wait for moderator input between rounds")
            self.WAIT_FOR_MODERATOR = True

        # Get GAMES_TO_PLAY variable from config
        self.GAMES_TO_PLAY = int(self.config["engine"]["games_to_play"])

        for i in range(self.GAMES_TO_PLAY):
            self.logger.info(f"Game Number {i} - Setting up")
            self.setup_game()
            self.logger.info("Running the game")
            winner = self.game()
            self.logger.info(f"Winner determined - {winner.name} - Building data output")
            list_of_players_in_game = []
            for player in self.player_list:
                list_of_players_in_game.append({
                    "name": player.name,
                    "score": player.score
                })
            self.data["games"].append({
                "game": i,
                "winner": winner.name,
                "winner_score": winner.score,
                "players": list_of_players_in_game
            })

            self.logger.info("Resetting players to default")
            for player in self.player_list:
                # Sneaky addition of player names into the data file as the for loop can be used.
                if player.name not in self.data["player_names"]:
                    self.data["player_names"].append(player.name)
                player.reset()

        self.logger.info("Writing data to datafile.json")
        with open("datafile.json", "w") as f:
            f.write(json.dumps(self.data))

        self.logger.info("Done!")

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

    def game(self) -> players.Player:
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


if __name__ == "__main__":
    Main()
