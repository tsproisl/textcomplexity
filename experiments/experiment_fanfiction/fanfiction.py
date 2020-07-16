#!/usr/bin/env python3

import argparse
import itertools
import logging
import os
import statistics

from complexity_measures import dependency_based
from complexity_measures import vocabulary_richness
from complexity_measures import utils


logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def arguments():
    parser = argparse.ArgumentParser("Complexity of CoreNLP output in CoNLL format")
    parser.add_argument("--skip", type=int, default=0, help="Percent of text to skip at the beginning and end of a file (default: 0)")
    parser.add_argument("--window-size", type=int, default=5000, help="Window size (default: 5000)")
    parser.add_argument("INDIR", type=os.path.abspath, help="Input directory")
    return parser.parse_args()


def lengths(tokens):
    atl, atl_stdev = vocabulary_richness.average_token_length_characters(itertools.chain.from_iterable(tokens))
    print("\t", atl, sep="", end="")
    asl, asl_stdev = vocabulary_richness.average_sentence_length(tokens)
    print("\t", asl, sep="", end="")
    aslc, aslc_stdev = vocabulary_richness.average_sentence_length_characters(tokens)
    print("\t", aslc, sep="", end="")


def vocabulary_measures(tokens, measures, window_size=5000):
    tokens = [t.lower() for t in itertools.chain.from_iterable(tokens)]
    for measure in measures:
        try:
            score = vocabulary_richness.bootstrap(tokens, measure=measure, window_size=window_size, ci=False)
        except:
            score, ci = "", ""
        print("\t", score, sep="", end="")


def dispersion_measures(tokens, window_size=5000, parts=10):
    tokens = [t.lower() for t in itertools.chain.from_iterable(tokens)]
    dp, dp_norm = vocabulary_richness.gries_dp(tokens, window_size, parts)
    print("\t", dp_norm, sep="", end="")
    kld = vocabulary_richness.kl_divergence(tokens, window_size, parts)
    print("\t", kld, sep="", end="")


def density(lemmas, pos, window_size=5000):
    """Proportion of content words."""
    nonverb_tags = set("JJ JJR JJS NN NNS NNP NNPS RB RBR RBS".split())
    verb_tags = set("VB VBD VBG VBN VBP VBZ".split())
    verb_lemmas = set("be do have".split())
    lemmas = list(itertools.chain.from_iterable(lemmas))
    pos = list(itertools.chain.from_iterable(pos))
    lemma_pos = list(zip(lemmas, pos))
    densities = []
    for i in range(int(len(lemma_pos) / window_size)):  # ignore last partial chunk
        chunk = lemma_pos[i * window_size:(i * window_size) + window_size]
        filtered = [(l, p) for l, p in chunk if (p in nonverb_tags) or ((p in verb_tags) and (l.lower() not in verb_lemmas))]
        densities.append(len(filtered) / window_size)
    if len(densities) == 1:
        print("\t", densities[0], sep="", end="")
    else:
        print("\t", statistics.mean(densities), sep="", end="")


def dependency_measures(graphs, measures):
    sentences = len(graphs)
    graphs = [g for g in graphs if g is not None]
    if sentences - len(graphs) > 0:
        logging.warn("Ignored %d sentences without sensible dependency analyses." % (sentences - len(graphs)))
    if len(graphs) == 0:
        print("\t", sep="", end="")
        return
    for measure, name in measures:
        score, stdev = measure(graphs)
        print("\t", score, sep="", end="")


def main():
    args = arguments()
    # print("\t".join("filename tokens word_length sentence_length sentence_length_characters ttr honore_h mtld dp_norm kl_divergence density dependency_distance dependents_per_word".split()))
    lexical = ["type_token_ratio", "honore_h", "mtld"]
    depbased = [(dependency_based.average_average_dependency_distance, "average_dependency_distance"),
                (dependency_based.average_dependents_per_word,         "dependents_per_word")]
    for filename in os.listdir(args.INDIR):
        size = os.path.getsize(os.path.join(args.INDIR, filename))
        logging.info("%s (%d)" % (filename, size))
        if size == 0:
            continue
        with open(os.path.join(args.INDIR, filename), encoding="utf-8") as f:
            lines = f.readlines()
            n_lines = len(lines)
            skip = int(args.skip * n_lines / 100)
            lines = lines[skip:n_lines - skip]
            tokens, lemmas, pos, graphs = zip(*utils.read_conll(lines, ignore_punct=True, warnings=True))
            n_tokens = len(list(itertools.chain.from_iterable(tokens)))
            if n_tokens < 5000:
                continue
            print(filename, sep="", end="")
            print("\t", n_tokens, sep="", end="")
            # lengths(tokens)
            # vocabulary_measures(tokens, lexical, args.window_size)
            # dispersion_measures(tokens, len(tokens), 10)
            density(lemmas, pos, len(tokens))
            # dependency_measures(graphs, depbased)
            print()


if __name__ == "__main__":
    main()
