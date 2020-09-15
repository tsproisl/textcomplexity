#!/usr/bin/env python3

import nltk
import nltk_tgrep

from complexity_measures.utils import misc


def t_units(trees):
    return misc.average_measure_and_length(_t_units, trees)


def _t_units(tree):
    """A t-unit is “one main clause plus any subordinate clause or
    nonclausal structure that is attached to or embedded in it” (Hunt
    1970: 4).

    We operationalize it as an S node that is immediately dominated
    either by TOP or by a CS node that is immediately dominated by
    TOP. S = sentence, CS = coordinated sentence.

    """
    return _tgrep_count_and_lengths(tree, "S > (CS > TOP) | > TOP")


def complex_t_units(trees):
    return misc.average_measure_and_length(_complex_t_units, trees)


def _complex_t_units(tree):
    """A complex T-unit is one that contains a dependent clause (Casanave
    1994).

    We operationalize it as a t-unit that dominates an S node.

    """
    return _tgrep_count_and_lengths(tree, "(S > (CS > TOP) | > TOP) << S")


def clauses(trees):
    return misc.average_measure_and_length(_clauses, trees)


def _clauses(tree):
    """A clause is defined as a structure with a subject and a finite verb
    (Hunt 1965, Polio 1997).

    We operationalize it as an S node, since that is defined as “a
    finite verb + its dependents”.
    (http://www.coli.uni-saarland.de/projects/sfb378/negra-corpus/knoten.html#S).

    """
    return _tgrep_count_and_lengths(tree, "S")


def dependent_clauses(trees):
    return misc.average_measure_and_length(_dependent_clauses, trees)


def _dependent_clauses(tree):
    """A clause that is immediately dominated by another clause."""
    return _tgrep_count_and_lengths(tree, "S > S")


def nps(trees):
    return misc.average_measure_and_length(_nps, trees)


def _nps(tree):
    """Number and lengths of NPs."""
    return _tgrep_count_and_lengths(tree, "NP")


def vps(trees):
    return misc.average_measure_and_length(_vps, trees)


def _vps(tree):
    """Number and lengths of VPs."""
    return _tgrep_count_and_lengths(tree, "VP")


def pps(trees):
    return misc.average_measure_and_length(_pps, trees)


def _pps(tree):
    """Number and lengths of PPs."""
    return _tgrep_count_and_lengths(tree, "PP")


def coordinate_phrases(trees):
    return misc.average_measure_and_length(_coordinate_phrases, trees)


def _coordinate_phrases(tree):
    """Only adjective, adverb, noun, and verb phrases are counted in
    coordinate phrases (Cooper 1976).

    """
    return _tgrep_count_and_lengths(tree, "CAP|CAVP|CNP|CVP")


def constituents(trees):
    return misc.average_measure(_constituents, trees)


def _constituents(tree):
    """Number of constituents."""
    return len(list(tree.subtrees()))


def constituents_wo_leaves(trees):
    return misc.average_measure(_constituents_wo_leaves, trees)


def _constituents_wo_leaves(tree):
    """Number of constituents (not counting leaves)."""
    return len(list(tree.subtrees())) - len(tree.leaves())


def height(trees):
    return misc.average_measure(_height, trees)


def _height(tree):
    """Height of the parse tree."""
    return tree.height()


def _tgrep_count_and_lengths(tree, pattern):
    """Number and lengths of constituent"""
    result = nltk_tgrep.tgrep_nodes(tree, pattern)
    result = [r for r in result if isinstance(r, nltk.tree.ParentedTree)]
    lengths = [len(r.leaves()) for r in result]
    return len(result), lengths
