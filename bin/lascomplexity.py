#!/usr/bin/env python3

import argparse
import itertools
import logging

from complexity_measures import dependency_based
from complexity_measures import constituent_based
from complexity_measures import vocabulary_richness
from complexity_measures import utils


def arguments():
    parser = argparse.ArgumentParser(description="An averaged perceptron part-of-speech tagger")
    parser.add_argument("-v", "--voc", action="store_true", help="Compute vocabulary-based complexity measures")
    parser.add_argument("-d", "--dep", action="store_true", help="Compute dependency-based complexity measures")
    parser.add_argument("-c", "--const", action="store_true", help="Compute constituent-based complexity measures")
    parser.add_argument("--ignore-punct", action="store_true", help="Ignore punctuation (currently only implemented for vocabulary-based complexity measures)")
    parser.add_argument("--only-robust", action="store_true", help="Use only robust vocabulary-based complexity measures that can cope with very small window sizes")
    parser.add_argument("--window-size", default=5000, type=int, help="Window size for vocabulary-based complexity measures (default: 5000)")
    parser.add_argument("TEXT", type=argparse.FileType("r", encoding="utf-8"), help="Input file. Path to a file or \"-\" for STDIN. A CoNLL-style text file with six tab-separated columns and an empty line after each sentence. The columns are: word index, word, part-of-speech tag, index of dependency head, dependency relation, phrase structure tree. Missing values can be replaced with an underscore (_).")
    return parser.parse_args()


def vocabulary_measures(tokens, window_size=5000, only_robust=False):
    """"""
    tokens = list(itertools.chain.from_iterable(tokens))
    lexical = ["type_token_ratio", "guiraud_r", "herdan_c",
               "dugast_k", "maas_a2", "dugast_u", "tuldava_ln",
               "brunet_w", "cttr", "summer_s", "sichel_s",
               "michea_m", "honore_h", "herdan_vm", "entropy",
               "yule_k", "simpson_d", "hdd", "mtld"]
    robust_lexical = ["type_token_ratio", "guiraud_r", "herdan_c",
               "dugast_k", "maas_a2", "tuldava_ln",
               "brunet_w", "cttr", "summer_s", "sichel_s",
               "honore_h", "entropy",
               "yule_k", "simpson_d", "hdd"]
    measures = lexical
    if only_robust:
        measures = robust_lexical
    word_length = [vocabulary_richness.average_token_length_characters,
                   vocabulary_richness.average_token_length_syllables]
    word_length_names = ["average_token_length_characters", "average_token_length_syllables"]
    for measure in measures:
        score, ci = vocabulary_richness.bootstrap(tokens, measure=measure, window_size=window_size, ci=True)
        print(measure, score, ci, sep="\t")
    for wl, wl_name in zip(word_length, word_length_names):
        score, stdev = wl(tokens)
        print(wl_name, score, stdev, sep="\t")


def dependency_measures(graphs):
    """"""
    sentences = len(graphs)
    graphs = [g for g in graphs if g is not None]
    logging.warn("Ignored %d sentences without sensible dependency analyses." % (sentences - len(graphs)))
    measures = [dependency_based.average_average_dependency_distance,
                dependency_based.average_closeness_centrality,
                dependency_based.average_outdegree_centralization,
                dependency_based.average_closeness_centralization,
                dependency_based.average_dependents_per_word,
                dependency_based.average_longest_shortest_path,
                # TODO: move to own function and operate on tokens
                dependency_based.average_sentence_length,
                dependency_based.average_sentence_length_characters,
                dependency_based.average_sentence_length_syllables,
                dependency_based.average_punctuation_per_sentence]
    names = ["average_dependency_distance",
             "closeness_centrality",
             "outdegree_centralization",
             "closeness_centralization",
             "dependents_per_word",
             "longest_shortest_path",
             "sentence_length",
             "sentence_length_characters",
             "sentence_length_syllables",
             "punctuation_per_sentence"]
    for measure, name in zip(measures, names):
        score, stdev = measure(graphs)
        print(name, score, stdev, sep="\t")


def constituent_measures(trees):
    """"""
    sentences = len(trees)
    trees = [t for t in trees if t is not None]
    logging.warn("Ignored %d sentences without sensible phrase structure trees." % (sentences - len(trees)))
    measures = [constituent_based.average_t_units,
                constituent_based.average_complex_t_units,
                constituent_based.average_clauses,
                constituent_based.average_dependent_clauses,
                constituent_based.average_nps,
                constituent_based.average_vps,
                constituent_based.average_pps,
                constituent_based.average_coordinate_phrases,
                constituent_based.average_constituents,
                constituent_based.average_constituents_wo_leaves,
                constituent_based.average_height]
    names = ["t_units",
             "complex_t_units",
             "clauses",
             "dependent_clauses",
             "nps",
             "vps",
             "pps",
             "coordinate_phrases",
             "constituents",
             "constituents_wo_leaves",
             "height"]
    for measure, name in zip(measures, names):
        result = measure(trees)
        if len(result) == 4:
            print(name, result[0], result[1], sep="\t")
            print("%s_length" % name, result[2], result[3], sep="\t")
        elif len(result) == 2:
            print(name, result[0], result[1], sep="\t")
        else:
            logging.warn("I expected either two or four elements!")


def main():
    args = arguments()
    if not any((args.voc, args.dep, args.const)):
        args.voc = True
        args.dep = True
        args.const = True
    tokens, graphs, trees = zip(*utils.read_tsv(args.TEXT, args.voc, args.dep, args.const, args.ignore_punct))
    print("measure", "score", "stdev/ci", sep="\t")
    if args.voc:
        vocabulary_measures(tokens, args.window_size, args.only_robust)
    if args.dep:
        dependency_measures(graphs)
    if args.const:
        constituent_measures(trees)
    # header = "id filename genre type_token_ratio type_token_ratio_ci guiraud_r guiraud_r_ci herdan_c herdan_c_ci dugast_k dugast_k_ci maas_a2 maas_a2_ci dugast_u dugast_u_ci tuldava_ln tuldava_ln_ci brunet_w brunet_w_ci cttr cttr_ci summer_s summer_s_ci sichel_s sichel_s_ci michea_m michea_m_ci honore_h honore_h_ci herdan_vm herdan_vm_ci entropy entropy_ci yule_k yule_k_ci simpson_d simpson_d_ci hdd hdd_ci mtld mtld_ci word_length_char word_length_char_stdev word_length_syll word_length_syll_stdev dependency_distance dependency_distance_stdev closeness_centrality closeness_centrality_stdev outdegree_centralization outdegree_centralization_stdev closeness_centralization closeness_centralization_stdev average_sentence_length average_sentence_length_stdev average_sentence_length_char average_sentence_length_char_stdev average_sentence_length_syll average_sentence_length_syll_stdev dependents_per_word dependents_per_word_stdev longest_shortest_path longest_shortest_path_stdev punctuation_per_sentence punctuation_per_sentence_stdev t_units t_units_stdev t_units_length t_units_length_stdev complex_t_units complex_t_units_stdev complex_t_units_length complex_t_units_length_stdev clauses clauses_stdev clauses_length clauses_length_stdev dependent_clauses dependent_clauses_stdev dependent_clauses_length dependent_clauses_length_stdev nps nps_stdev nps_length nps_length_stdev vps vps_stdev vps_length vps_length_stdev pps pps_stdev pps_length pps_length_stdev coordinate_phrases coordinate_phrases_stdev coordinate_phrases_length coordinate_phrases_length_stdev constituents constituents_stdev constituents_wo_leaves constituents_wo_leaves_stdev height height_stdev".split()


if __name__ == "__main__":
    main()
