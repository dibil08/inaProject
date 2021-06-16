from collections import defaultdict
import csv
import pickle

import networkx as nx


def tripartite_graph():
    graph = nx.Graph()

    players_list, games_list = games_players_list()
    datadict = steam_dict()

    for g1 in games_list:
        # negative id for purchased games nodes, positive id for played games
        graph.add_node(-g1)
        graph.add_node(g1)
        graph.add_edge(-g1, g1)
    for player in players_list:
        graph.add_node(player)
        for game in datadict[player]:
            if datadict[player][game]["status"] == "play":
                game_node = game
            elif datadict[player][game]["status"] == "purchase":
                game_node = -game
            else:
                print("Unknown game status")
                return -1
            assert player in graph.nodes() and game_node in graph.nodes
            graph.add_edge(player, game_node)
    return graph


def games_players_list():
    players = set()
    games = set()

    with open("../data/gameToId.pkl", "rb") as pickle_file:
        game_to_id = pickle.load(pickle_file)

    with open("../data/steam-200k.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            player, game, game_status, time, _ = row
            try:
                games.add(game_to_id[game])
                players.add(player)
            except KeyError:
                # skip at this game as game id not known
                continue

    # convert sets to lists and return them sorted
    return sorted(list(players)), sorted(list(games))


def steam_dict():
    datadict = defaultdict(lambda: defaultdict(dict))

    with open("../data/gameToId.pkl", "rb") as pickle_file:
        game_to_id = pickle.load(pickle_file)

    with open("../data/steam-200k.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            player, game, game_status, time, _ = row
            try:
                game_id = game_to_id[game]
            except KeyError:
                # skip at this game as game id not known
                continue

            datadict[player][game_id] = {
                "game_id": game_id, "game_name": game,
                "status": game_status, "playtime": time
            }

    return datadict
