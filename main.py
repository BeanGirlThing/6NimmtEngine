from engine.deck import Deck
from engine.hand import Hand
from configparser import ConfigParser
import players
from prettytable import PrettyTable
import json
import logging
from django.utils.text import slugify
import os
import sys
import datetime
import enlighten


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
        self.setup_logging()

        self.logger.info("Starting 6Nimmt Engine")

        self.player_list = [
            players.RandomPlay(),
            players.LowestHighest(),
            players.HighestLowest(),
            players.LowestHighestSwap()
        ]

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

        enlighten_manager = enlighten.get_manager()
        status_bar = enlighten_manager.status_bar('Engine Running', color='black_on_white', justify=enlighten.Justify.CENTER)
        engine_progress_bar = enlighten_manager.counter(total=self.GAMES_TO_PLAY, desc="Configuration", unit="games", color="green")

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

            engine_progress_bar.update()

        self.logger.info("Writing data to datafile.json")
        with open("datafile.json", "w") as f:
            f.write(json.dumps(self.data))

        self.logger.info("Done!")
        status_bar.color = "black_on_green"
        status_bar.update("Engine Done!")
        enlighten_manager.stop()
        print("\n")

    def setup_logging(self):
        logging_file_handler = logging.FileHandler(get_logfile_absolute_path())
        logging_file_handler.setLevel(logging.DEBUG)
        logging_stream_handler = logging.StreamHandler(sys.stdout)
        logging_stream_handler.setLevel(logging.WARNING)

        logging_formatter = logging.Formatter(
            fmt='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S'
        )

        logging_file_handler.setFormatter(logging_formatter)
        logging_stream_handler.setFormatter(logging_formatter)

        self.logger = logging.getLogger("6NimmtEngine")
        self.logger.setLevel(logging.DEBUG)

        self.logger.addHandler(logging_file_handler)
        self.logger.addHandler(logging_stream_handler)

if __name__ == "__main__":
    Main()
