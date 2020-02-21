#!/usr/bin/env python3

import argparse
import itertools
import os

from complexity_measures import compression, utils


def arguments():
    parser = argparse.ArgumentParser("Window-based compression")
    parser.add_argument("-o", "--outfile", type=os.path.abspath, required=True, help="Output file")
    parser.add_argument("FILE", nargs="+", type=os.path.abspath, help="Input file")
    args = parser.parse_args()
    return args


def main():
    args = arguments()
    with open(args.outfile, mode="w", encoding="utf-8") as f_out:
        f_out.write("\t".join(("filename", "tokens", "window_500", "window_1000", "window_5000", "window_10000", "whole_text")) + "\n")
        for infile in args.FILE:
            with open(infile, encoding="utf-8") as f_in:
                sentences = utils.get_sentences(f_in)
                tokens = list(itertools.chain.from_iterable(itertools.chain.from_iterable(sentences)))
                gzip500, gzip1000, gzip5000, gzip10000 = "", "", "", ""
                if len(tokens) >= 500:
                    gzip500 = compression.bootstrap(tokens, measure="gzip", window_size=500, ci=False)
                if len(tokens) >= 1000:
                    gzip1000 = compression.bootstrap(tokens, measure="gzip", window_size=1000, ci=False)
                if len(tokens) >= 5000:
                    gzip5000 = compression.bootstrap(tokens, measure="gzip", window_size=5000, ci=False)
                if len(tokens) >= 10000:
                    gzip10000 = compression.bootstrap(tokens, measure="gzip", window_size=10000, ci=False)
                gzip_total = compression.gzip_compression(tokens)
                f_out.write("\t".join((os.path.basename(infile), str(len(tokens)), str(gzip500), str(gzip1000), str(gzip5000), str(gzip10000), str(gzip_total))) + "\n")


if __name__ == "__main__":
    main()
