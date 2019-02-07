#!/usr/bin/env python3

import collections

import pandas as pd

from complexity_measures import utils


def main():
    tags = "$, $. $( ADJA ADJD ADV APPO APPR APPRART APZR ART CARD FM ITJ KOKOM KON KOUI KOUS NE NN PAV PDAT PDS PIAT PIS PPER PPOSAT PPOSS PRELAT PRELS PRF PTKA PTKANT PTKNEG PTKVZ PTKZU PWAT PWAV PWS TRUNC VAFIN VAIMP VAINF VAPP VMFIN VMINF VMPP VVFIN VVIMP VVINF VVIZU VVPP XY".split()
    metadata = pd.read_csv("/ccl/projects/Kallimachos/low_high_brow_corpus/metadaten.tsv", sep="\t", header=0, index_col=0)
    print("\t".join("ID genre brow".split() + tags))
    for idx, text in metadata.iterrows():
        genre = text["genre"]
        if text["brow"] == "high":
            genre = "high"
        with open("/ccl/projects/Kallimachos/low_high_brow_corpus/all_by_id/%s.jtf" % text["ID"]) as f:
            sentence_graphs = list(utils.read_jtf_graphs(f))
        n = 0
        tagfreq = collections.Counter()
        for sentence in sentence_graphs:
            n += len(sentence)
            tagfreq.update([d for v, d in sentence.nodes(data="pos")])
        print("\t".join([str(text["ID"]), genre, text["brow"]] + [str(tagfreq[t] / n) for t in tags]))


if __name__ == "__main__":
    main()
