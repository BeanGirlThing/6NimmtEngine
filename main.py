from configparser import ConfigParser
import players
import logging
from django.utils.text import slugify
import os
import sys
import datetime
import enlighten
from itertools import combinations
from dataCollector import DataCollector
import multiprocessing
from engine.game import Game
import copy

import enlightenMpWrapper

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
    data_collector = None

    player_list = None

    SHOW_GAME = False
    WAIT_FOR_MODERATOR = False
    GAMES_TO_PLAY = 1

    CPU_CORES = None
    MULTIPROCESSING_ENABLE = False

    data = {
        "player_names": [],
        "games": []
    }

    def __init__(self):
        # Create the manager for the progress bars (First method, so it catches stdout)
        enlighten_manager = enlighten.get_manager()

        self.setup_logging()
        self.logger.info("Starting 6Nimmt Engine")

        self.player_list = [
            players.RandomPlay(),
            players.LowestHighest(),
            players.HighestLowest(),
            players.LowestHighestSwap(),
            players.RandomPlay(),
            players.RandomPlay()
        ]

        # Read the config file
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.logger.debug("Read config file successfully")

        # Initialise the Data Collector
        self.data_collector = DataCollector()

        self.configuration_groups = []

        for group in combinations(self.player_list, int(self.config["game"]["players"])):
            self.configuration_groups.append(group)

        self.data_collector.get_configurations(self.configuration_groups)

        # Get MULTIPROCESSING_ENABLE from config
        if int(self.config["engine"]["multiprocessing"]) == 1:
            self.logger.info("Multiprocessing is enabled")
            self.MULTIPROCESSING_ENABLE = True

        self.CPU_CORES = multiprocessing.cpu_count()

        # Get GAMES_TO_PLAY variable from config
        self.GAMES_TO_PLAY = int(self.config["engine"]["games_to_play"])
        self.data_collector = self.GAMES_TO_PLAY

        status_bar = enlighten_manager.status_bar(status_format=u'{fill}Engine Running{fill}{elapsed}', color='black_on_white', justify=enlighten.Justify.CENTER, autorefresh=True)
        configuration_info = enlighten_manager.status_bar(color="black_on_white", justify=enlighten.Justify.CENTER)
        configuration_progress_bars = []

        # We have Number of Cores
        # We have Number of Games that need to run
        # We need to create a number of processes (Multiprocessing) to the number of Cores, and below the number of configurations
            # A game object must be created for each of these processes

        # Create the game objects for each configuration group
        unique_players_configuration_group = []
        for i, group in enumerate(self.configuration_groups):
            configuration = []
            # Ensure a new instance of the player is created for each configuration
            for j, player in enumerate(group):
                configuration.append(copy.deepcopy(player))
            unique_players_configuration_group.append(configuration)
        self.configuration_groups = unique_players_configuration_group

        list_of_games = []
        game_processes = []
        for i, configuration in enumerate(self.configuration_groups):
            list_of_games.append(Game(i, configuration, enlighten_manager, self.config))
            list_of_games[i].setup_game()
            game_processes.append(multiprocessing.Process(target=list_of_games[i].game, args=()))


        enlighten_manager = enlightenMpWrapper.Server()
        status_bar = enlighten_manager.status_bar('Engine Running', color='black_on_white', justify=enlighten.Justify.CENTER)

        for game in game_processes:
            game.start()


        # for i in range(0, len(list(self.configuration_groups))):
        #     configuration_progress_bars.append(enlighten_manager.counter(total=self.GAMES_TO_PLAY, desc=f"Configuration {i}/{len(list(self.configuration_groups))}", unit="games", color="green"))
        #
        # for configuration_number, configuration in enumerate(list(self.configuration_groups)):
        #     configuration_info.update(f"Configuration: {', '.join(bot.name for bot in configuration)}", force=True)
        #     for i in range(self.GAMES_TO_PLAY):
        #         self.logger.debug(f"Game Number {i} - Setting up")
        #         self.setup_game(configuration)
        #         self.logger.debug("Running the game")
        #         winner = self.game(configuration)
        #         self.logger.debug(f"Winner determined - {winner.name} - Building data output")
        #         list_of_players_in_game = []
        #         for player in configuration:
        #             list_of_players_in_game.append({
        #                 "name": player.name,
        #                 "score": player.score
        #             })
        #         self.data["games"].append({
        #             "game": i,
        #             "winner": winner.name,
        #             "winner_score": winner.score,
        #             "players": list_of_players_in_game
        #         })
        #
        #         self.logger.debug("Resetting players to default")
        #         for player in configuration:
        #             # Sneaky addition of player names into the data file as the for loop can be used.
        #             if player.name not in self.data["player_names"]:
        #                 self.data["player_names"].append(player.name)
        #             player.reset()
        #
        #         configuration_progress_bars[configuration_number].update()
        #
        #     self.logger.debug("Writing data to datafile.json")
        #     with open("datafile.json", "w") as f:
        #         f.write(json.dumps(self.data))
        #
        self.logger.info("Done!")
        status_bar.color = "black_on_green"
        status_bar.update("Engine Done!")
        enlighten_manager.stop()
        print("\n")

    def setup_logging(self):
        #logging_file_handler = logging.FileHandler(get_logfile_absolute_path())
        #logging_file_handler.setLevel(logging.DEBUG)
        logging_stream_handler = logging.StreamHandler(sys.stdout)
        logging_stream_handler.setLevel(logging.INFO)

        logging_formatter = logging.Formatter(
            fmt='[%(asctime)s][%(levelname)s][%(name)s] - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S'
        )

        #logging_file_handler.setFormatter(logging_formatter)
        logging_stream_handler.setFormatter(logging_formatter)

        self.logger = logging.getLogger("6NimmtEngine")
        self.logger.setLevel(logging.DEBUG)

        #self.logger.addHandler(logging_file_handler)
        self.logger.addHandler(logging_stream_handler)


if __name__ == "__main__":
    Main()
