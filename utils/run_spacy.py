#!/usr/bin/env python3

import argparse
import os

import requests
import spacy
import spacy.about
import spacy.cli.download
from wasabi import msg


def arguments():
    shortcuts = get_json(spacy.about.__shortcuts__, "available shortcuts")
    parser = argparse.ArgumentParser(description="Parse input texts to CONLL-U format using spaCy.")
    parser.add_argument("-l", "--language", choices=sorted(shortcuts.keys()), required=True, help="Input language.")
    parser.add_argument("-o", "--output-dir", type=os.path.abspath, default=".", help="Output directory. Default: Current directory.")
    parser.add_argument("TEXT", type=argparse.FileType("r", encoding="utf-8"), nargs="+", help="Input text files. Paths to files or \"-\" for STDIN.")
    return parser.parse_args()


def get_json(url, desc):
    r = requests.get(url)
    if r.status_code != 200:
        msg.fail(
            "Server error ({})".format(r.status_code),
            "Couldn't fetch {}. Please find a model for your spaCy "
            "installation (v{}), and download it manually. For more "
            "details, see the documentation: "
            "https://spacy.io/usage/models".format(desc, spacy.about.__version__),
            exits=1,
        )
    return r.json()


def main():
    args = arguments()
    spacy.cli.download(args.language)
    nlp = spacy.load(args.language)
    for fh in args.TEXT:
        filename = os.path.basename(fh.name)
        text = fh.read()
        doc = nlp(text)
        with open(os.path.join(args.output_dir, filename + ".conllu"), mode="w", encoding="utf-8") as out:
            for sentence in doc.sents:
                for id_, token in enumerate(sentence, start=1):
                    if token.is_space:
                        continue
                    if id_ == 1:
                        offset = token.i - id_
                    deprel = token.dep_
                    head = token.head.i
                    if head == token.i:
                        head = 0
                        deprel = "root"
                    else:
                        head -= offset
                    out.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(id_, token.text, token.lemma_, token.pos_, token.tag_, "_", head, deprel, "_", "_"))
                out.write("\n")


if __name__ == "__main__":
    main()
