#!/usr/bin/env python3

import itertools
import statistics

import nltk
import nltk_tgrep


def _average_statistic_with_lengths(statistic, trees):
    """Calculate the statistic for every sentence and return mean and
    standard deviation."""
    results = [statistic(t) for t in trees]
    counts, lengths = zip(*results)
    lengths = list(itertools.chain.from_iterable(lengths))
    return statistics.mean(counts), statistics.stdev(counts), statistics.mean(lengths), statistics.stdev(lengths)


def _average_statistic_wo_lengths(statistic, trees):
    """Calculate the statistic for every sentence and return mean and
    standard deviation."""
    results = [statistic(t) for t in trees]
    return statistics.mean(results), statistics.stdev(results)


def average_t_units(trees):
    return _average_statistic_with_lengths(t_units, trees)


def t_units(tree):
    """A t-unit is “one main clause plus any subordinate clause or
    nonclausal structure that is attached to or embedded in it” (Hunt
    1970: 4).

    We operationalize it as an S node that is immediately dominated
    either by TOP or by a CS node that is immediately dominated by
    TOP. S = sentence, CS = coordinated sentence.

    """
    return _tgrep_count_and_lengths(tree, "S > (CS > TOP) | > TOP")


def average_complex_t_units(trees):
    return _average_statistic_with_lengths(complex_t_units, trees)


def complex_t_units(tree):
    """A complex T-unit is one that contains a dependent clause (Casanave
    1994).

    We operationalize it as a t-unit that dominates an S node.

    """
    return _tgrep_count_and_lengths(tree, "(S > (CS > TOP) | > TOP) << S")


def average_clauses(trees):
    return _average_statistic_with_lengths(clauses, trees)


def clauses(tree):
    """A clause is defined as a structure with a subject and a finite verb
    (Hunt 1965, Polio 1997).

    We operationalize it as an S node, since that is defined as “a
    finite verb + its dependents”.
    (http://www.coli.uni-saarland.de/projects/sfb378/negra-corpus/knoten.html#S).

    """
    return _tgrep_count_and_lengths(tree, "S")


def average_dependent_clauses(trees):
    return _average_statistic_with_lengths(dependent_clauses, trees)


def dependent_clauses(tree):
    """A clause that is immediately dominated by another clause."""
    return _tgrep_count_and_lengths(tree, "S > S")


def average_nps(trees):
    return _average_statistic_with_lengths(nps, trees)


def nps(tree):
    """Number and lengths of NPs."""
    return _tgrep_count_and_lengths(tree, "NP")


def average_vps(trees):
    return _average_statistic_with_lengths(vps, trees)


def vps(tree):
    """Number and lengths of VPs."""
    return _tgrep_count_and_lengths(tree, "VP")


def average_pps(trees):
    return _average_statistic_with_lengths(pps, trees)


def pps(tree):
    """Number and lengths of PPs."""
    return _tgrep_count_and_lengths(tree, "PP")


def average_coordinate_phrases(trees):
    return _average_statistic_with_lengths(coordinate_phrases, trees)


def coordinate_phrases(tree):
    """Only adjective, adverb, noun, and verb phrases are counted in
    coordinate phrases (Cooper 1976).

    """
    return _tgrep_count_and_lengths(tree, "CAP|CAVP|CNP|CVP")


def average_constituents(trees):
    return _average_statistic_wo_lengths(constituents, trees)


def constituents(tree):
    """Number of constituents."""
    return len(list(tree.subtrees()))


def average_constituents_wo_leaves(trees):
    return _average_statistic_wo_lengths(constituents_wo_leaves, trees)


def constituents_wo_leaves(tree):
    """Number of constituents (not counting leaves)."""
    return len(list(tree.subtrees())) - len(tree.leaves())


def average_height(trees):
    return _average_statistic_wo_lengths(height, trees)


def height(tree):
    """Height of the parse tree."""
    return tree.height()


def _tgrep_count_and_lengths(tree, pattern):
    """Number and lenghts of constituent"""
    result = nltk_tgrep.tgrep_nodes(tree, pattern)
    result = [r for r in result if isinstance(r, nltk.tree.ParentedTree)]
    lengths = [len(r.leaves()) for r in result]
    return len(result), lengths
