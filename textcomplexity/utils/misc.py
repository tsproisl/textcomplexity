#!/usr/bin/env python3

import functools
import itertools
import math
import statistics

import numpy
import scipy.special


def confidence_interval(results):
    return 1.96 * statistics.stdev(results) / math.sqrt(len(results))


@functools.lru_cache(maxsize=1024)
def betaln(a, b):
    return scipy.special.betaln(a, b)


@functools.lru_cache(maxsize=1024)
def hypergeom_pmf(k, M, n, N):
    tot, good = M, n
    bad = tot - good
    result = (betaln(good+1, 1) + betaln(bad+1, 1) + betaln(tot-N+1, N+1) -
              betaln(k+1, good-k+1) - betaln(N-k+1, bad-N+k+1) -
              betaln(tot+1, 1))
    return numpy.exp(result)


def geom_pmf(k, p):
    return numpy.power(1-p, k-1) * p


def average_measure(measure, sentences):
    """Calculate the measure for every sentence and return mean and
    standard deviation.

    """
    results = [measure(s) for s in sentences]
    return statistics.mean(results), statistics.stdev(results)


def average_measure_and_length(measure, sentences):
    """Calculate the measure for every sentence and return mean and
    standard deviation of the measure and mean and standard deviation
    of the lengths.

    """
    results = [measure(s) for s in sentences]
    scores, lengths = zip(*results)
    lengths = list(itertools.chain.from_iterable(lengths))
    return statistics.mean(scores), statistics.stdev(scores), statistics.mean(lengths), statistics.stdev(lengths)
