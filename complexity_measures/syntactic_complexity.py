#!/usr/bin/env python3

import statistics

import networkx

import utils


def average_dependency_distance(sentence_graphs):
    """Oya (2011)"""
    add = []
    for g in sentence_graphs:
        distances, edges = 0, 0
        for s, t in g.edges(data=False):
            edges += 1
            distances += abs(s - t)
        if edges > 0:
            add.append(distances/edges)
    return statistics.mean(add), statistics.stdev(add)


def embeddedness(sentence_graphs):
    """Oya (2011) mentions closeness centrality of the root vertex as a
    syntactic complexity measure called embeddedness. We use the
    inverse of the closeness centrality, i.e. the average length of
    the shortest paths from the root to all other vertices.

    """
    embeddedness = []
    for g in sentence_graphs:
        if len(g.nodes()) > 1:
            root = [v for v, l in g.nodes(data=True) if "root" in l][0]
            cc = networkx.algorithms.centrality.closeness_centrality(g, root, reverse=True)
            embeddedness.append(1/cc)
    return statistics.mean(embeddedness), statistics.stdev(embeddedness)


if __name__ == "__main__":
    # with open("/ccl/projects/Kallimachos/low_high_brow_corpus/Schemaliteratur/processed/4391.William Voltz_Das.txt.jtf") as f:
    with open("../4391.William Voltz_Das.txt.jtf") as f:
        sentence_graphs = list(utils.read_jtf_graphs(f))
        print("%.4f (stdev: %.4f)" % average_dependency_distance(sentence_graphs))
        print("%.4f (stdev: %.4f)" % embeddedness(sentence_graphs))
