#!/usr/bin/env python3

import pandas as pd

from complexity_measures import vocabulary_richness
from complexity_measures import utils


def main():
    metadata = pd.read_csv("/ccl/projects/Kallimachos/low_high_brow_corpus_v2/metadata.tsv", sep="\t", header=0, index_col=0)
    print("\t".join("id filename genre sttr ci".split()))
    for idx, text in metadata.iterrows():
        print(idx, "\t".join(text), sep="\t", end="")
        with open("/ccl/projects/Kallimachos/low_high_brow_corpus_v2/%s" % text["filename"]) as f:
            tokens = [t[6] for s in utils.read_txt_csv_sentences(f) for t in s]
        sttr, ci = vocabulary_richness.bootstrap(tokens, measure="type_token_ratio", window_size=1000, ci=True)
        print("\t%s\t%s" % (sttr, ci))


if __name__ == "__main__":
    main()
