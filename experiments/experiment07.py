#!/usr/bin/env python3

import collections
import sys

import pandas as pd

from complexity_measures import dependency_based
from complexity_measures import constituent_based
from complexity_measures import vocabulary_richness
from complexity_measures import utils


def main():
    metadata = pd.read_csv("/ccl/projects/Kallimachos/low_high_brow_corpus_v2/metadata.tsv", sep="\t", header=0, index_col=0)
    dep_based = [dependency_based.average_average_dependency_distance,
                 dependency_based.average_closeness_centrality,
                 dependency_based.average_outdegree_centralization,
                 dependency_based.average_closeness_centralization,
                 dependency_based.average_sentence_length,
                 dependency_based.average_sentence_length_characters,
                 dependency_based.average_sentence_length_syllables,
                 dependency_based.average_dependents_per_word,
                 dependency_based.average_longest_shortest_path,
                 dependency_based.average_punctuation_per_sentence]
    const_based = [constituent_based.average_t_units,
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
    lexical = ["type_token_ratio", "guiraud_r", "herdan_c",
               "dugast_k", "maas_a2", "dugast_u", "tuldava_ln",
               "brunet_w", "cttr", "summer_s", "sichel_s",
               "michea_m", "honore_h", "herdan_vm", "entropy",
               "yule_k", "simpson_d", "hdd", "mtld"]
    word_length = [vocabulary_richness.average_token_length_characters,
                   vocabulary_richness.average_token_length_syllables]
    header = "id filename genre type_token_ratio type_token_ratio_ci guiraud_r guiraud_r_ci herdan_c herdan_c_ci dugast_k dugast_k_ci maas_a2 maas_a2_ci dugast_u dugast_u_ci tuldava_ln tuldava_ln_ci brunet_w brunet_w_ci cttr cttr_ci summer_s summer_s_ci sichel_s sichel_s_ci michea_m michea_m_ci honore_h honore_h_ci herdan_vm herdan_vm_ci entropy entropy_ci yule_k yule_k_ci simpson_d simpson_d_ci hdd hdd_ci mtld mtld_ci word_length_char word_length_char_stdev word_length_syll word_length_syll_stdev dependency_distance dependency_distance_stdev closeness_centrality closeness_centrality_stdev outdegree_centralization outdegree_centralization_stdev closeness_centralization closeness_centralization_stdev average_sentence_length average_sentence_length_stdev average_sentence_length_char average_sentence_length_char_stdev average_sentence_length_syll average_sentence_length_syll_stdev dependents_per_word dependents_per_word_stdev longest_shortest_path longest_shortest_path_stdev punctuation_per_sentence punctuation_per_sentence_stdev t_units t_units_stdev t_units_length t_units_length_stdev complex_t_units complex_t_units_stdev complex_t_units_length complex_t_units_length_stdev clauses clauses_stdev clauses_length clauses_length_stdev dependent_clauses dependent_clauses_stdev dependent_clauses_length dependent_clauses_length_stdev nps nps_stdev nps_length nps_length_stdev vps vps_stdev vps_length vps_length_stdev pps pps_stdev pps_length pps_length_stdev coordinate_phrases coordinate_phrases_stdev coordinate_phrases_length coordinate_phrases_length_stdev constituents constituents_stdev constituents_wo_leaves constituents_wo_leaves_stdev height height_stdev".split()
    pos = ["``", ",", ":", ".", "''", "(", ")", "$", "$,", "$.", "$(", "#", "ADJ", "ADJA", "ADJD", "ADV", "APPO", "APPR", "APPRART", "APZR", "ART", "CARD", "CC", "CD", "DT", "EX", "FM", "HYPH", "IN", "ITJ", "JJ", "JJR", "JJS", "KOKOM", "KON", "KOUI", "KOUS", "LS", "MD", "NE", "NN", "NNP", "NNPS", "NNS", "PAV", "PDAT", "PDS", "PDT", "PIAT", "PIS", "PPER", "PPOSAT", "PPOSS", "PRELAT", "PRELS", "PRF", "PRP", "PRP$", "PTKA", "PTKANT", "PTKNEG", "PTKVZ", "PTKZU", "PWAT", "PWAV", "PWS", "RB", "RBR", "RBS", "RP", "SYM", "TO", "TRUNC", "UH", "VAFIN", "VAIMP", "VAINF", "VAPP", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "VMFIN", "VMINF", "VMPP", "VVFIN", "VVIMP", "VVINF", "VVIZU", "VVPP", "WDT", "WP", "WRB", "XY"]
    print("\t".join(header + pos))
    for idx, text in metadata.iterrows():
        print(text["filename"], file=sys.stderr)
        with open("/ccl/projects/Kallimachos/low_high_brow_corpus_v2/%s" % text["filename"]) as f:
            dep_trees, const_trees = zip(*utils.read_txt_csv_graphs(f))
        print(idx, "\t".join(text), sep="\t", end="")
        tokens = [l["token"] for t in dep_trees for v, l in t.nodes(data=True)]
        for measure in lexical:
            score, ci = vocabulary_richness.bootstrap(tokens, measure=measure, window_size=5000, ci=True)
            print("", score, ci, sep="\t", end="")
        for wl in word_length:
            score, stdev = wl(tokens)
            print("", score, stdev, sep="\t", end="")
        for db in dep_based:
            score, stdev = db(dep_trees)
            print("", score, stdev, sep="\t", end="")
        for cb in const_based:
            result = cb(const_trees)
            if isinstance(result, tuple):
                result = "\t".join(str(r) for r in result)
            print("", result, sep="\t", end="")
        tags = collections.Counter(l["pos"] for t in dep_trees for v, l in t.nodes(data=True))
        for p in pos:
            print("", tags[p] / len(tokens), sep="\t", end="")
        print()


if __name__ == "__main__":
    main()
