#!/usr/bin/env python3

import logging

import pandas as pd

from complexity_measures import dependency_based
from complexity_measures import utils


def main():
    metadata = pd.read_csv("/ccl/projects/Kallimachos/low_high_brow_corpus/metadaten.tsv", sep="\t", header=0, index_col=0)
    print("\t".join("ID genre brow sentence_id average_dependency_distance closeness_centrality outdegree_centralization closeness_centralization sentence_length dependents_per_word longest_shortest_path punctuation dependency_distances".split()))
    for idx, text in metadata.iterrows():
        genre = text["genre"]
        if text["brow"] == "high":
            genre = "high"
        # with open("/ccl/projects/Kallimachos/low_high_brow_corpus/all_by_id/%s.jtf" % text["ID"]) as f:
        #     sentences = list(utils.read_jtf_graphs(f))
        try:
            with open("/ccl/projects/Kallimachos/low_high_brow_corpus_v2/all_by_id/%s.txt.csv" % text["ID"]) as f:
                sentences = list(utils.read_txt_csv_graphs(f))
        except FileNotFoundError:
            logging.warn("File not found: %s.txt.csv" % text["ID"])
            continue
        # for g in sentences:
        for g, tree in sentences:
            # print(tree)
            sentence_id = g.graph["sentence_id"]
            dd = dependency_based.dependency_distances(g)
            if len(dd) > 0:
                dd = ",".join(map(str, dd))
            else:
                dd = 0
            add = dependency_based.average_dependency_distance(g)
            length = dependency_based.sentence_length(g)
            cc = dependency_based.closeness_centrality(g)
            odc = dependency_based.outdegree_centralization(g)
            ccentr = dependency_based.closeness_centralization(g)
            lsp = dependency_based.longest_shortest_path(g)
            dpw = dependency_based.dependents_per_word(g)
            pps = dependency_based.punctuation_per_sentence(g)
            print("\t".join(map(str, (text["ID"], genre, text["brow"], sentence_id, add, cc, odc, ccentr, length, dpw, lsp, pps, dd))))


if __name__ == "__main__":
    main()
