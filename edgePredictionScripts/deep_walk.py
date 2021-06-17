from graphCreatorScripts import build_graph
from collections import defaultdict
import util_prediction as up
import time
import numpy as np
from scipy import stats


def deep_walk_model(graph, walk_steps=5, walk_paths=10):
    paths = up.get_walk_paths(graph, n_paths=walk_paths, walk_steps=walk_steps)
    return up.word2vec_model(paths)


global_start = time.time()


print("Creating tripartite graphs")
partial_tripartite = build_graph.tripartite_remove_edges()
original_tripartite = build_graph.tripartite_graph()
partial_tripartite_edges = set(partial_tripartite.edges())
original_tripartite_edges = set(original_tripartite.edges())

players, games = build_graph.games_players_list()

player_not_owned = defaultdict(set)
player_similarities = defaultdict(list)
player_compare_truth = defaultdict(list)

print("Retrieving not owned games for each player")
for player in players:
    for game_sim_pair in games:
        node_player = build_graph.node_player.format(player)
        node_game_purchased = build_graph.node_game_purchased.format(game_sim_pair)
        node_game_played = build_graph.node_game_played.format(game_sim_pair)
        if (node_game_purchased, node_player) not in partial_tripartite_edges and\
                (node_game_played, node_player) not in partial_tripartite_edges:
            player_not_owned[node_player].add(game_sim_pair)


print("Creating deep walk model")
start = time.time()
deep_walk = deep_walk_model(partial_tripartite, walk_steps=10)
end = time.time()
print("Done. Time elapsed (s):", end - start)

print("Retrieving similarities for not owned games")
start = time.time()
i = 0
num_players = len(players)
for player in player_not_owned:
    for game_sim_pair in player_not_owned[player]:
        game_played = build_graph.node_game_played.format(game_sim_pair)
        game_purchased = build_graph.node_game_purchased.format(game_sim_pair)
        # get similarities if game in vocabulary, otherwise set sim to 0
        try:
            played_sim = deep_walk.wv.similarity(player, game_played)
        except KeyError:
            played_sim = 0
        try:
            purchased_sim = deep_walk.wv.similarity(player, game_purchased)
        except KeyError:
            purchased_sim = 0
        player_similarities[player].append((game_played, played_sim))
        player_similarities[player].append((game_purchased, purchased_sim))
    print("    sorting results (player {}/{})".format(i, num_players))
    i += 1
    player_similarities[player].sort(key=lambda x: x[1], reverse=True)
end = time.time()
print("Done. Time elapsed (s):", end - start)


print("Checking ground truth in original graph")
for player in player_similarities:
    # check only top 100 similarities
    for game_sim_pair in player_similarities[player][:100]:
        is_present = (game_sim_pair[0], player) in original_tripartite_edges
        player_compare_truth[player].append((game_sim_pair, is_present))

all_num_true = []
for player in player_compare_truth:
    num_true = len([pair for pair in player_compare_truth[player] if pair[1]])
    all_num_true.append(num_true)

min_true = np.min(all_num_true)
max_true = np.max(all_num_true)
mean_true = np.mean(all_num_true)
median_true = np.median(all_num_true)
mode_true = stats.mode(all_num_true)

print("STATISTICS FOR EXISTING EDGES OUT OF TOP 100 SIMILAR:")
print("min:", min_true)
print("max:", max_true)
print("mean:", mean_true)
print("median:", median_true)
print("mode:", mode_true)


global_end = time.time()

print("TOTAL TIME ELAPSED (s):", global_end - global_start)
