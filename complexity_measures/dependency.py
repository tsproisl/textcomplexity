#!/usr/bin/env python3

import functools
import statistics

import networkx

from complexity_measures import utils


# -----------------
#  Sentence length
# -----------------
def sentence_length_words(sentence_graphs):
    """Mean sentence length in words; also returns the standard
    deviation.

    """
    return utils.average_measure(_sentence_length_words, sentence_graphs)


def _sentence_length_words(g):
    """Sentence length in words."""
    return len(g)


def sentence_length_characters(sentence_graphs):
    """Mean sentence length in characters; also returns the standard
    deviation. Sentence length in characters is the sum of token
    lengths plus number of token boundaries, i.e. we assume a space
    between all tokens.

    """
    return utils.average_measure(_sentence_length_characters, sentence_graphs)


def _sentence_length_characters(g):
    """Sentence length in characters."""
    tokens = [l["token"] for v, l in g.nodes(data=True)]
    token_lengths = [len(t) for t in tokens]
    return sum(token_lengths) + len(token_lengths) - 1


# ---------------------
#  Dependency distance
# ---------------------
def average_dependency_distance(sentence_graphs):
    """Oya (2011)"""
    return utils.average_measure(_average_dependency_distance, sentence_graphs)


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
    return utils.average_measure(_closeness_centrality, sentence_graphs)


def _closeness_centrality(g):
    """Closeness centrality of the root vertex, i.e. the inverse of the
    average length of the shortest paths from the root to all other
    vertices. Used by Oya (2012).

    """
    if len(g) > 1:
        root = [v for v, l in g.nodes(data=True) if "root" in l][0]
        return networkx.algorithms.centrality.closeness_centrality(g, root, reverse=True)
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
    return utils.average_measure(_outdegree_centralization, sentence_graphs)


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
    return utils.average_measure(_closeness_centralization, sentence_graphs)


def _closeness_centralization(g):
    """Closeness centralization of the graph (Freeman, 1978). Return
    values range between 0 and 1. 1 means all other vertices are
    dependent on the root vertex. Used by Oya (2012).

    """
    if len(g) > 1:
        cc = networkx.algorithms.centrality.closeness_centrality(g, reverse=True).values()
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
    return utils.average_measure(_longest_shortest_path, sentence_graphs)


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
    return utils.average_measure(_dependents_per_word, sentence_graphs)


def _dependents_per_word(g):
    """Average number of dependents per word."""
    outdegrees = [deg for v, deg in g.out_degree()]
    return statistics.mean(outdegrees)


# -------------
#  Punctuation
# -------------
def punctuation_per_sentence(sentence_graphs, punctuation):
    """Number of punctuation tokens per sentence (according to
    `punctuation`, a set of part-of-speech tags).

    """
    pps = functools.partial(_punctuation_per_sentence, punctuation=punctuation)
    return utils.average_measure(pps, sentence_graphs)


def _punctuation_per_sentence(g, punctuation):
    return len([v for v, l in g.nodes(data=True) if l["pos"] in punctuation])


def punctuation_per_token(sentence_graphs, punctuation):
    """Number of punctuation tokens per token (according to `punctuation`,
    a set of part-of-speech tags).

    """
    punct, tokens = 0, 0
    for g in sentence_graphs:
        punct += _punctuation_per_sentence(g, punctuation)
        tokens += len(g)
    return punct / tokens
