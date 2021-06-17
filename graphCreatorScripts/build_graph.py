from collections import defaultdict
import csv
import pickle
import random

import networkx as nx

# formatting strings for different node types
node_player = "player_{}"
node_game_purchased = "purchased_{}"
node_game_played = "played_{}"


def tripartite_graph(connect_games=True):
    graph = nx.Graph()

    players_list, games_list = games_players_list()
    datadict = steam_dict()

    for g in games_list:
        # add once for purchased group and once for played group
        graph.add_node(node_game_purchased.format(g))
        graph.add_node(node_game_played.format(g))
        if connect_games:
            graph.add_edge(node_game_purchased.format(g), node_game_played.format(g))
    for player in players_list:
        player_node = node_player.format(player)
        graph.add_node(player_node)
        for game in datadict[player]:
            if datadict[player][game]["status"] == "play":
                game_node = node_game_played.format(game)
            elif datadict[player][game]["status"] == "purchase":
                game_node = node_game_purchased.format(game)
            else:
                print("Unknown game status:", datadict[player][game]["status"])
                return -1
            assert player_node in graph.nodes() and game_node in graph.nodes()
            graph.add_edge(player_node, game_node)
    return graph


def tripartite_remove_edges(n_remove=0):
    graph = tripartite_graph()
    removing_edges = [(u, v) for u, v in graph.edges() if str(v).startswith("player_")]

    # if number of edges to remove not set, remove 1/3 of edges
    if n_remove == 0:
        to_remove = int(len(graph.edges()) / 3)
    else:
        to_remove = n_remove

    removed = set()
    while len(removed) < to_remove:
        removing_edge = random.choice(removing_edges)
        while removing_edge in removed:
            removing_edge = random.choice(removing_edges)
        graph.remove_edges_from([removing_edge])
        removed.add(removing_edge)

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
