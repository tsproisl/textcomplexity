#!/usr/bin/env python3

import argparse
import itertools
import logging
import os

from complexity_measures import dependency_based
from complexity_measures import vocabulary_richness
from complexity_measures import utils


def arguments():
    parser = argparse.ArgumentParser("Complexity of CoreNLP output in CoNLL format")
    parser.add_argument("--skip", type=int, default=5, help="Percent of text to skip at the beginning and end of a file")
    parser.add_argument("INDIR", type=os.path.abspath, help="Input directory")
    return parser.parse_args()


def lengths(tokens):
    atl, atl_stdev = vocabulary_richness.average_token_length_characters(tokens)
    print("\t", atl, sep="", end="")
    asl, asl_stdev = vocabulary_richness.average_sentence_length(tokens)
    print("\t", asl, sep="", end="")
    aslc, aslc_stdev = vocabulary_richness.average_sentence_length_characters(tokens)
    print("\t", aslc, sep="", end="")


def vocabulary_measures(tokens, measures, window_size=5000):
    tokens = list(itertools.chain.from_iterable(tokens))
    for measure in measures:
        try:
            score, ci = vocabulary_richness.bootstrap(tokens, measure=measure, window_size=window_size, ci=True)
        except:
            score, ci = "", ""
        print("\t", score, sep="", end="")


def dispersion_measures(tokens, window_size=5000, parts=10):
    dp, dp_norm = vocabulary_measures.gries_dp(tokens, window_size, parts)
    print("\t", dp_norm, sep="", end="")
    kld = vocabulary_measures.kl_divergence(tokens, window_size, parts)
    print("\t", kld, sep="", end="")


def dependency_measures(graphs, measures):
    sentences = len(graphs)
    graphs = [g for g in graphs if g is not None]
    logging.warn("Ignored %d sentences without sensible dependency analyses." % (sentences - len(graphs)))
    for measure, name in measures:
        score, stdev = measure(graphs)
        print("\t", score, sep="", end="")


def main():
    args = arguments()
    print("\t".join("filename word_length sentence_length sentence_length_characters ttr honore_h mtld dp_norm kl_divergence density dependency_distance dependents_per_word".split()))
    lexical = ["type_token_ratio", "honore_h", "mtld"]
    depbased = [(dependency_based.average_average_dependency_distance, "average_dependency_distance"),
                (dependency_based.average_dependents_per_word,         "dependents_per_word")]
    for filename in os.listdir(args.INDIR):
        print(filename, sep="", end="")
        with open(filename, encoding="utf-8") as f:
            with open(os.path.join(args.INDIR, filename), encoding="utf-8") as f:
                lines = f.readlines()
                n_lines = len(lines)
                skip = int(args.skip * n_lines / 100)
                lines = lines[skip:n_lines - skip]
                tokens, lemmas, pos, graphs = zip(*utils.read_conll(lines, ignore_punct=True, warnings=True))
                lengths(tokens)
                vocabulary_measures(tokens, lexical, args.window_size)
                dispersion_measures(tokens, len(tokens), 10)
                dependency_measures(graphs)
                print()


if __name__ == "__main__":
    main()
