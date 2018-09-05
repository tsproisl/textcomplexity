#!/usr/bin/env python3

import pandas as pd

from complexity_measures import syntactic_complexity
from complexity_measures import utils


def main():
    metadata = pd.read_csv("/ccl/projects/Kallimachos/low_high_brow_corpus/metadaten.tsv", sep="\t", header=0, index_col=0)
    dependency_distance, dependency_distance_stdev = [], []
    closeness_centrality, closeness_centrality_stdev = [], []
    outdegree_centralization, outdegree_centralization_stdev = [], []
    closeness_centralization, closeness_centralization_stdev = [], []
    sentence_length, sentence_length_stdev = [], []
    deps_per_word, deps_per_word_stdev = [], []
    longest_shortest_path, longest_shortest_path_stdev = [], []
    punctuation_per_sentence, punctuation_per_sentence_stdev = [], []
    punctuation_per_token = []
    for idx, text in metadata.iterrows():
        with open("/ccl/projects/Kallimachos/low_high_brow_corpus/all_by_id/%s.jtf" % text["ID"]) as f:
            sentence_graphs = list(utils.read_jtf_graphs(f))
        add, add_stdev = syntactic_complexity.average_average_dependency_distance(sentence_graphs)
        cc, cc_stdev = syntactic_complexity.average_closeness_centrality(sentence_graphs)
        odc, odc_stdev = syntactic_complexity.average_outdegree_centralization(sentence_graphs)
        ccentr, ccentr_stdev = syntactic_complexity.average_closeness_centralization(sentence_graphs)
        asl, asl_stdev = syntactic_complexity.average_sentence_length(sentence_graphs)
        dpw, dpw_stdev = syntactic_complexity.average_dependents_per_word(sentence_graphs)
        lsp, lsp_stdev = syntactic_complexity.average_longest_shortest_path(sentence_graphs)
        pps, pps_stdev = syntactic_complexity.average_punctuation_per_sentence(sentence_graphs)
        ppt = syntactic_complexity.average_punctuation_per_token(sentence_graphs)
        dependency_distance.append(add)
        dependency_distance_stdev.append(add_stdev)
        closeness_centrality.append(cc)
        closeness_centrality_stdev.append(cc_stdev)
        outdegree_centralization.append(odc)
        outdegree_centralization_stdev.append(odc_stdev)
        closeness_centralization.append(ccentr)
        closeness_centralization_stdev.append(ccentr_stdev)
        sentence_length.append(asl)
        sentence_length_stdev.append(asl_stdev)
        deps_per_word.append(dpw)
        deps_per_word_stdev.append(dpw_stdev)
        longest_shortest_path.append(lsp)
        longest_shortest_path_stdev.append(lsp_stdev)
        punctuation_per_sentence.append(pps)
        punctuation_per_sentence_stdev.append(pps_stdev)
        punctuation_per_token.append(ppt)
    metadata["dependency_distance"] = dependency_distance
    metadata["dependency_distance_stdev"] = dependency_distance_stdev
    metadata["closeness_centrality"] = closeness_centrality
    metadata["closeness_centrality_stdev"] = closeness_centrality_stdev
    metadata["outdegree_centralization"] = outdegree_centralization
    metadata["outdegree_centralization_stdev"] = outdegree_centralization_stdev
    metadata["closeness_centralization"] = closeness_centralization
    metadata["closeness_centralization_stdev"] = closeness_centralization_stdev
    metadata["average_sentence_length"] = sentence_length
    metadata["average_sentence_length_stdev"] = sentence_length_stdev
    metadata["dependents_per_word"] = deps_per_word
    metadata["dependents_per_word_stdev"] = deps_per_word_stdev
    metadata["longest_shortest_path"] = longest_shortest_path
    metadata["longest_shortest_path_stdev"] = longest_shortest_path_stdev
    metadata["punctuation_per_sentence"] = punctuation_per_sentence
    metadata["punctuation_per_sentence_stdev"] = punctuation_per_sentence_stdev
    metadata["punctuation_per_token"] = punctuation_per_token
    metadata.to_csv("/ccl/projects/Kallimachos/low_high_brow_corpus/metadaten_syntactic_complexity.tsv", sep="\t")


if __name__ == "__main__":
    main()
