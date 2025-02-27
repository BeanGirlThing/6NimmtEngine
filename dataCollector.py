
class DataCollector(object):
    configurations = None
    games_to_play_per_configuration = 0

    current_game = None


    def __init__(self):
        pass

    def get_configurations(self, configurations):
        self.configurations = configurations

    def get_games_to_play_per_configuration(self, count: int):
        self.games_to_play_per_configuration = count

    def new_game(self, initial_table: list):
        self.current_game = Game(initial_table)

    def round(self, table: list, played_cards: list):
        self.current_game.round(table, played_cards)

class Game(object):
    initial_table = None
    round_counter = 0
    game = {}

    def __init__(self, columns):
        self.initial_table = columns

    def round(self, table: list, played_cards: list):
        table_
