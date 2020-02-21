#!/usr/bin/env python3

import gzip
import math
import statistics


def gzip_compression(tokens):
    """gzip compression (compressed size / original size)"""
    original = " ".join(tokens).encode("utf-8")
    compressed = gzip.compress(original)
    return len(compressed) / len(original)


def _sttr_ci(results):
    """calculate the confidence interval for sttr """
    return 1.96 * statistics.stdev(results) / math.sqrt(len(results))


def bootstrap(tokens, measure='gzip', window_size=1000, ci=False, raw=False):
    """calculate bootstrap for compression measures
    as explained in Evert et al. 2017.
    :param ci:  additionally calculate and return the confidence interval, returns a tuple
    :param raw:  return the raw results
    """
    results = []
    measures = dict(gzip=gzip_compression)
    func = measures[measure]
    for i in range(int(len(tokens) / window_size)):  # ignore last partial chunk
        chunk = tokens[i * window_size:(i * window_size) + window_size]
        result = func(chunk)
        results.append(result)
    if raw:
        return results
    if ci:
        return (statistics.mean(results), _sttr_ci(results))
    return statistics.mean(results)
