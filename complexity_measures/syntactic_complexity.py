#!/usr/bin/env python3

import statistics

import networkx

from complexity_measures import utils


def average_sentence_length(sentence_graphs):
    """Oya (2011)"""
    lengths = []
    for g in sentence_graphs:
        lengths.append(len(g))
    return statistics.mean(lengths), statistics.stdev(lengths)


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
        else:
            add.append(0)
    return statistics.mean(add), statistics.stdev(add)


def closeness_centrality(sentence_graphs):
    """Closeness centrality of the root vertex, i.e. the inverse of the
    average length of the shortest paths from the root to all other
    vertices. Used by Oya (2012).

    """
    embeddedness = []
    for g in sentence_graphs:
        if len(g) > 1:
            root = [v for v, l in g.nodes(data=True) if "root" in l][0]
            cc = networkx.algorithms.centrality.closeness_centrality(g, root, reverse=True)
            embeddedness.append(cc)
        else:
            embeddedness.append(1)
    return statistics.mean(embeddedness), statistics.stdev(embeddedness)


def outdegree_centralization(sentence_graphs):
    """Outdegree centralization of the graph (Freeman, 1978). Return
    values range between 0 and 1. 1 means all other vertices are
    dependent on the root vertex. Used by Oya (2012).

    """
    centralization = []
    for g in sentence_graphs:
        if len(g) > 1:
            out_degrees = [deg for v, deg in g.out_degree()]
            max_out_degree = max(out_degrees)
            # for directed graphs, the denominator should be n² - 2n + 1
            # instead of n² - 3n + 2
            centr = sum(max_out_degree - deg for deg in out_degrees) / (len(g) ** 2 - 2 * len(g) + 1)
            assert centr <= 1
            centralization.append(centr)
        else:
            centralization.append(1)
    return statistics.mean(centralization), statistics.stdev(centralization)


def closeness_centralization(sentence_graphs):
    """Closeness centralization of the graph (Freeman, 1978). Return
    values range between 0 and 1. 1 means all other vertices are
    dependent on the root vertex. Used by Oya (2012).

    """
    centralization = []
    for g in sentence_graphs:
        if len(g) > 1:
            cc = networkx.algorithms.centrality.closeness_centrality(g, reverse=True).values()
            max_cc = max(cc)
            # for directed graphs, the denominator should be n - 1
            # instead of (n² - 3n + 2)/(2n - 3)
            centr = sum(max_cc - c for c in cc) / (len(g) - 1)
            assert centr <= 1
            centralization.append(centr)
        else:
            centralization.append(1)
    return statistics.mean(centralization), statistics.stdev(centralization)


def longest_shortest_path(sentence_graphs):
    """Longest shortest path from the root vertex, i.e. depth of the
    tree.

    """
    lsp = []
    for g in sentence_graphs:
        if len(g) > 1:
            root = [v for v, l in g.nodes(data=True) if "root" in l][0]
            lsp.append(max(networkx.algorithms.shortest_path_length(g, source=root).values()))
        else:
            lsp.append(0)
    return statistics.mean(lsp), statistics.stdev(lsp)


def dependents_per_word(sentence_graphs):
    """Average number of dependents per word."""
    deps = []
    for g in sentence_graphs:
        outdegrees = [deg for v, deg in g.out_degree()]
        deps.append(statistics.mean(outdegrees))
    return statistics.mean(deps), statistics.stdev(deps)
