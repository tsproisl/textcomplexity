#!/usr/bin/env python3

import itertools
import statistics

import nltk_tgrep


# Average number of CONSTITUENTs per sentence (NP, VP, PP, SBAR)

# Average length of CONSTITUENT (NP, VP, PP)

# Average number of constituents per sentence

# NUR = FRAG?

# Lu 2010


def t_units(tree):
    """A t-unit is “one main clause plus any subordinate clause or
    nonclausal structure that is attached to or embedded in it” (Hunt
    1970: 4).

    We operationalize it as an S node that is immediately dominated
    either by TOP or by a CS node that is immediately dominated by
    TOP. S = sentence, CS = coordinated sentence.

    """
    result = nltk_tgrep.tgrep_nodes(tree, "S > (CS > TOP) | > TOP")
    lengths = [r.leaves() for r in result]
    return len(result), lengths


def clauses(tree):
    """A clause is defined as a structure with a subject and a finite verb
    (Hunt 1965, Polio 1997).

    We operationalize it as an S node, since that is defined as “a
    finite verb + its dependents”.
    (http://www.coli.uni-saarland.de/projects/sfb378/negra-corpus/knoten.html#S).

    """
    return _single_constituent(tree, "S")


def nps(tree):
    """Number and lengths of NPs."""
    return _single_constituent(tree, "NP")


def vps(tree):
    """Number and lengths of VPs."""
    return _single_constituent(tree, "VP")


def pps(tree):
    """Number and lengths of PPs."""
    return _single_constituent(tree, "PP")


def constituents(tree):
    """Number of constituents."""
    return len(list(tree.subtrees()))


def constituents_wo_leaves(tree):
    """Number of constituents (not counting leaves)."""
    return len(list(tree.subtrees())) - len(tree.leaves())


def _single_constituent(tree, constituent):
    """Number and lenghts of constituent"""
    result = nltk_tgrep.tgrep_nodes(tree, constituent)
    lengths = [r.leaves() for r in result]
    return len(result), lengths
