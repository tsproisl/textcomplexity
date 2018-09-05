#!/usr/bin/env python3

import pandas as pd

from complexity_measures import syntactic_complexity
from complexity_measures import utils


def main():
    metadata = pd.read_csv("/ccl/projects/Kallimachos/low_high_brow_corpus/metadaten.tsv", sep="\t", header=0, index_col=0)
    print("\t".join("ID genre brow sentence_id average_dependency_distance closeness_centrality outdegree_centralization closeness_centralization sentence_length dependents_per_word longest_shortest_path punctuation dependency_distances".split()))
    for idx, text in metadata.iterrows():
        genre = text["genre"]
        if text["brow"] == "high":
            genre = "high"
        with open("/ccl/projects/Kallimachos/low_high_brow_corpus/all_by_id/%s.jtf" % text["ID"]) as f:
            sentence_graphs = list(utils.read_jtf_graphs(f))
        for sentence in sentence_graphs:
            sentence_id = sentence.graph["sentence_id"]
            dd = syntactic_complexity.dependency_distances(sentence)
            if len(dd) > 0:
                dd = ",".join(map(str, dd))
            else:
                dd = 0
            add = syntactic_complexity.average_dependency_distance(sentence)
            length = syntactic_complexity.sentence_length(sentence)
            cc = syntactic_complexity.closeness_centrality(sentence)
            odc = syntactic_complexity.outdegree_centralization(sentence)
            ccentr = syntactic_complexity.closeness_centralization(sentence)
            lsp = syntactic_complexity.longest_shortest_path(sentence)
            dpw = syntactic_complexity.dependents_per_word(sentence)
            pps = syntactic_complexity.punctuation_per_sentence(sentence)
            print("\t".join(map(str, (text["ID"], genre, text["brow"], sentence_id, add, cc, odc, ccentr, length, dpw, lsp, pps, dd))))


if __name__ == "__main__":
    main()
