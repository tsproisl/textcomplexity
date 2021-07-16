#!/usr/bin/env python3

import argparse
import json
import os

import stanza
from stanza.utils.conll import CoNLL
import stanza.resources.common


def arguments():
    stanza_resources_path = os.path.join(stanza.resources.common.DEFAULT_MODEL_DIR, "resources.json")
    if not os.path.isfile(stanza_resources_path):
        stanza.resources.common.download_resources_json(stanza.resources.common.DEFAULT_MODEL_DIR, stanza.resources.common.DEFAULT_RESOURCES_URL, None, stanza.resources.common.DEFAULT_RESOURCES_VERSION)
    stanza_resources = json.load(open(stanza_resources_path))
    parser = argparse.ArgumentParser(description="Parse input texts to CONLL-U format using stanza.")
    parser.add_argument("-l", "--language", choices=sorted(stanza_resources.keys()), required=True, help="Input language.")
    parser.add_argument("-o", "--output-dir", type=os.path.abspath, default=".", help="Output directory. Default: Current directory.")
    parser.add_argument("TEXT", type=argparse.FileType("r", encoding="utf-8"), nargs="+", help="Input text files. Paths to files or \"-\" for STDIN.")
    return parser.parse_args()


def main():
    args = arguments()
    stanza.download(args.language)
    nlp = stanza.Pipeline(args.language, processors="tokenize,mwt,pos,lemma,depparse")
    for fh in args.TEXT:
        filename = os.path.basename(fh.name)
        text = fh.read()
        doc = nlp(text)
        dicts = doc.to_dict()
        conll = CoNLL.convert_dict(dicts)
        with open(os.path.join(args.output_dir, filename + ".conllu"), mode="w", encoding="utf-8") as out:
            for sentence in conll:
                out.write("\n".join(("\t".join(token) for token in sentence)))
                out.write("\n\n")


if __name__ == "__main__":
    main()
