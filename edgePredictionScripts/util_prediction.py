import random
import networkx as nx

from gensim.models import Word2Vec


def random_walk(graph: nx.Graph, node, n_steps=5):
    path = [str(node)]
    target_node = node
    if not list(nx.all_neighbors(graph, target_node)):
        return path

    for _ in range(n_steps):
        target_node = random.choice(list(nx.all_neighbors(graph, target_node)))
        # make sure target node has neighbours
        while not list(nx.all_neighbors(graph, target_node)):
            target_node = random.choice(list(nx.all_neighbors(graph, target_node)))
        path.append(str(target_node))

    return path


def get_walk_paths(graph: nx.Graph, n_paths=10, walk_steps=5, node_identifier="player_"):
    walk_paths = []
    considered_nodes = [node for node in graph.nodes() if str(node).startswith(node_identifier)]
    for node in considered_nodes:
        for _ in range(n_paths):
            walk_paths.append(random_walk(graph, node, n_steps=walk_steps))
    return walk_paths


def word2vec_model(walk_paths):
    word2vec = Word2Vec(window=4, sg=1, hs=0, negative=10, alpha=0.03, min_alpha=0.0001, seed=42)
    word2vec.build_vocab(walk_paths, progress_per=2)
    word2vec.train(walk_paths, total_examples=word2vec.corpus_count, epochs=20, report_delay=1)
    return word2vec
