#!/usr/bin/env python3

import argparse
import gzip
import os
import re


def arguments():
    """"""
    parser = argparse.ArgumentParser(description="Analyze the detailed output of KenLM (-v word)")
    parser.add_argument("-o", "--outprefix", type=os.path.abspath, help="Prefix for output files")
    parser.add_argument("DIR", type=os.path.abspath, help="The input directory")
    args = parser.parse_args()
    return args


def main():
    sent_total_re = re.compile(r"^Total: (-?[0-9.]+) OOV: (\d+)$")
    args = arguments()
    with gzip.open(args.outprefix + "_token_dist.tsv.gz", mode="wt") as o_token, gzip.open(args.outprefix + "_sentence_dist.tsv.gz", mode="wt") as o_sentence, gzip.open(args.outprefix + "_file_dist.tsv.gz", mode="wt") as o_file:
        o_file.write("\t".join(("filename", "tokens", "oov", "perplexity_inc_oov", "perplexity_ex_oov")) + "\n")
        o_sentence.write("\t".join(("filename", "sentence_number", "length", "oov", "log10prob", "perplexity")) + "\n")
        o_token.write("\t".join(("filename", "token_number", "word", "log10prob", "perplexity")) + "\n")
        for filename in sorted(os.listdir(args.DIR)):
            if filename.endswith(".csv"):
                with open(os.path.join(args.DIR, filename)) as f:
                    lines = [l.rstrip() for l in f.readlines()]
                    n_tokens = lines.pop()
                    oov = lines.pop()
                    perplexity_ex_oov = lines.pop()
                    perplexity_inc_oov = lines.pop()
                    n_tokens = n_tokens.split("\t")[-1]
                    oov = oov.split("\t")[-1]
                    perplexity_ex_oov = perplexity_ex_oov.split("\t")[-1]
                    perplexity_inc_oov = perplexity_inc_oov.split("\t")[-1]
                    o_file.write("\t".join((filename, n_tokens, oov, perplexity_inc_oov, perplexity_ex_oov)) + "\n")
                    token_number = 0
                    for sentence_number, sentence in enumerate(lines, start=1):
                        tokens = sentence.split("\t")
                        sentence_total = tokens.pop()
                        m = sent_total_re.search(sentence_total)
                        assert m
                        sentence_log10prob = m.group(1)
                        sentence_oov = m.group(2)
                        sentence_length = len(tokens)
                        sentence_perplexity = 10 ** (- float(sentence_log10prob)/sentence_length)
                        o_sentence.write("\t".join((filename, str(sentence_number), str(sentence_length), sentence_oov, sentence_log10prob, str(sentence_perplexity))))
                        o_sentence.write("\n")
                        for token in tokens:
                            token_number += 1
                            word, rest = token.rsplit("=", maxsplit=1)
                            type_id, ngram_length, log10prob = rest.split(" ")
                            perplexity = 10 ** (- float(log10prob))
                            o_token.write("\t".join((filename, str(token_number), word, log10prob, str(perplexity))))
                            o_token.write("\n")


if __name__ == "__main__":
    main()
