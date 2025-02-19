import json
from math import floor

class SimpleDataParser:
    PLAYER_NAMES = []
    win_count = {}

    def __init__(self):
        with open("datafile.json", "r") as f:
            data = json.load(f)

        self.PLAYER_NAMES = data["player_names"]

        for player in self.PLAYER_NAMES:
            self.win_count[player] = 0

        game_total = 0
        for game in data["games"]:
            self.win_count[game["winner"]] += 1
            game_total += 1

        print(f"{game_total} Games were played\n")
        for player in self.PLAYER_NAMES:
            print(f"{player}:")
            print(f"Won: {self.win_count[player]}")
            print(f"Winrate: {round((self.win_count[player] / game_total) * 100, 2)}%\n")





if __name__ == '__main__':
    SimpleDataParser()