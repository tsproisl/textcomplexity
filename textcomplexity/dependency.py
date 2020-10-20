#!/usr/bin/env python3

import functools
import statistics

import networkx

from textcomplexity.utils import misc


# ---------------------
#  Dependency distance
# ---------------------
def average_dependency_distance(sentence_graphs):
    """Oya (2011)"""
    return misc.average_measure(_average_dependency_distance, sentence_graphs)


def _average_dependency_distance(g):
    """Oya (2011)"""
    distances = _dependency_distances(g)
    if len(distances) > 0:
        return statistics.mean(distances)
    else:
        return 0


def _dependency_distances(g):
    """Return all dependency distances."""
    distances = []
    for s, t in g.edges(data=False):
        distances.append(abs(s - t))
    return distances


# ----------------------
#  Closeness centrality
# ----------------------
def closeness_centrality(sentence_graphs):
    """Closeness centrality of the root vertex, i.e. the inverse of the
    average length of the shortest paths from the root to all other
    vertices. Used by Oya (2012).

    """
    return misc.average_measure(_closeness_centrality, sentence_graphs)


def _closeness_centrality(g):
    """Closeness centrality of the root vertex, i.e. the inverse of the
    average length of the shortest paths from the root to all other
    vertices. Used by Oya (2012).

    """
    if len(g) > 1:
        root = [v for v, l in g.nodes(data=True) if "root" in l][0]
        return networkx.algorithms.centrality.closeness_centrality(g.reverse(), root)
    else:
        return 1


# --------------------------
#  Outdegree centralization
# --------------------------
def outdegree_centralization(sentence_graphs):
    """Outdegree centralization of the graph (Freeman, 1978). Return
    values range between 0 and 1. 1 means all other vertices are
    dependent on the root vertex. Used by Oya (2012).

    """
    return misc.average_measure(_outdegree_centralization, sentence_graphs)


def _outdegree_centralization(g):
    """Outdegree centralization of the graph (Freeman, 1978). Return
    values range between 0 and 1. 1 means all other vertices are
    dependent on the root vertex. Used by Oya (2012).

    """
    if len(g) > 1:
        out_degrees = [deg for v, deg in g.out_degree()]
        max_out_degree = max(out_degrees)
        # for directed graphs, the denominator should be n² - 2n + 1
        # instead of n² - 3n + 2
        centr = sum(max_out_degree - deg for deg in out_degrees) / (len(g) ** 2 - 2 * len(g) + 1)
        assert centr <= 1
        return centr
    else:
        return 1


# --------------------------
#  Closeness centralization
# --------------------------
def closeness_centralization(sentence_graphs):
    """Closeness centralization of the graph (Freeman, 1978). Return
    values range between 0 and 1. 1 means all other vertices are
    dependent on the root vertex. Used by Oya (2012).

    """
    return misc.average_measure(_closeness_centralization, sentence_graphs)


def _closeness_centralization(g):
    """Closeness centralization of the graph (Freeman, 1978). Return
    values range between 0 and 1. 1 means all other vertices are
    dependent on the root vertex. Used by Oya (2012).

    """
    if len(g) > 1:
        cc = networkx.algorithms.centrality.closeness_centrality(g.reverse()).values()
        max_cc = max(cc)
        # for directed graphs, the denominator should be n - 1
        # instead of (n² - 3n + 2)/(2n - 3)
        centr = sum(max_cc - c for c in cc) / (len(g) - 1)
        assert centr <= 1
        return centr
    else:
        return 1


# -----------------------
#  Longest shortest path
# -----------------------
def longest_shortest_path(sentence_graphs):
    """Longest shortest path from the root vertex, i.e. depth of the
    tree.

    """
    return misc.average_measure(_longest_shortest_path, sentence_graphs)


def _longest_shortest_path(g):
    """Longest shortest path from the root vertex, i.e. depth of the
    tree.

    """
    if len(g) > 1:
        root = [v for v, l in g.nodes(data=True) if "root" in l][0]
        return max(networkx.algorithms.shortest_path_length(g, source=root).values())
    else:
        return 0


# ---------------------
#  Dependents per word
# ---------------------
def dependents_per_word(sentence_graphs):
    return misc.average_measure(_dependents_per_word, sentence_graphs)


def _dependents_per_word(g):
    """Average number of dependents per word."""
    outdegrees = [deg for v, deg in g.out_degree()]
    return statistics.mean(outdegrees)
