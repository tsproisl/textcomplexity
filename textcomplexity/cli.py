#!/usr/bin/env python3

import argparse
import collections
import functools
import itertools
import json

from textcomplexity import surface, sentence, dependency, constituency
from textcomplexity.text import Text
from textcomplexity.utils import conllu, custom_tsv, misc

Result = collections.namedtuple("Result", ["name", "value", "stdev", "length", "length_stdev"])


def arguments():
    parser = argparse.ArgumentParser(description="Compute a variety of linguistic and stylistic complexity measures.")
    parser.add_argument("--sur", action="store_true", help="Compute surface-based complexity measures")
    parser.add_argument("--sent", action="store_true", help="Compute sentence-based complexity measures")
    parser.add_argument("--dep", action="store_true", help="Compute dependency-based complexity measures")
    parser.add_argument("--const", action="store_true", help="Compute constituent-based complexity measures")
    parser.add_argument("--all-measures", action="store_true", help="Compute ALL applicable complexity measures (instead of only a sensible subset)")
    parser.add_argument("--lang", choices=["de_negra", "none"], default="none", help="Input language and parsing scheme. Some constituent-based complexity measures are only defined for certain languages or parsing schemes. Default: none (i.e. only compute language-independent measures).")
    parser.add_argument("--ignore-punct", action="store_true", help="Ignore punctuation (currently only implemented for surface-based complexity measures)")
    parser.add_argument("--punct-tag", action="append", help="Part-of-speech tag used for punctuation. Can be used multiple times to specify multiple tags, e.g. --punct-tag $. --punct-tag $, (Default: --punct-tag PUNCT)")
    parser.add_argument("--window-size", default=1000, type=int, help="Window size for vocabulary-based complexity measures (default: 1000)")
    parser.add_argument("-i", "--input-format", choices=["conllu", "tsv"], required=True, help="Format of the input files.")
    parser.add_argument("-o", "--output-format", choices=["json", "tsv"], default="json", help="Format for outputting the results.")
    parser.add_argument("TEXT", type=argparse.FileType("r", encoding="utf-8"), nargs="+", help="Input files. Paths to files or \"-\" for STDIN. Input files need to be text files in CoNLL-U format or in our custom format with six tab-separated columns and an empty line after each sentence. Missing values can be replaced with an underscore (_). Examples for both input formats can be found in README.md")
    return parser.parse_args()


def surface_based(tokens, window_size, all_measures):
    """"""
    results = []
    measures = [(surface.type_token_ratio, "type-token ratio", True),
                (surface.guiraud_r, "Guiraud's R", False),
                (surface.herdan_c, "Herdan's C", False),
                (surface.dugast_k, "Dugast's k", False),
                (surface.maas_a2, "Maas' a²", False),
                (surface.dugast_u, "Dugast's U", False),
                (surface.tuldava_ln, "Tuldava's LN", False),
                (surface.brunet_w, "Brunet's W", False),
                (surface.cttr, "CTTR", False),
                (surface.summer_s, "Summer's S", False),
                (surface.sichel_s, "Sichel's S", True),
                (surface.michea_m, "Michéa's M", False),
                (surface.honore_h, "Honoré's H", True),
                (surface.entropy, "Entropy", True),
                (surface.evenness, "Evenness", True),
                (surface.yule_k, "Yule's K", False),
                (surface.simpson_d, "Simpson's D", True),
                (surface.herdan_vm, "Herdan's Vm", False),
                (surface.hdd, "HD-D", True),
                (surface.average_token_length, "average token length", True),
                (surface.orlov_z, "Orlov's Z", True)]
    for measure, name, subset in measures:
        if all_measures or subset:
            name += " (disjoint windows)"
            mean, stdev, _ = misc.bootstrap(measure, tokens, window_size, strategy="spread")
            results.append(Result(name, mean, stdev, None, None))
    text = Text.from_tokens(tokens)
    mattr = surface.mattr(text, window_size)
    results.append(Result("type-token ratio (moving windows)", mattr, None, None, None))
    mtld = surface.mtld(text)
    results.append(Result("MTLD", mtld, None, None, None))
    return results


def sentence_based(sentences, punct_tags):
    """"""
    results = []
    pps = functools.partial(sentence.punctuation_per_sentence, punctuation=punct_tags)
    ppt = functools.partial(sentence.punctuation_per_token, punctuation=punct_tags)
    slw = functools.partial(sentence.sentence_length_words, punctuation=punct_tags)
    measures_with_punct = [(slw, "average sentence length (words)"),
                           (pps, "punctuation per sentence")]
    measures_wo_punct = [(sentence.sentence_length_tokens, "average sentence length (tokens)"),
                         (sentence.sentence_length_characters, "average sentence length (characters)")]
    if punct_tags:
        measures = measures_with_punct + measures_wo_punct
        results.append(Result("punctuation per token", ppt(sentences), None, None, None))
    else:
        measures = measures_wo_punct
    for measure, name in measures:
        value, stdev = measure(sentences)
        results.append(Result(name, value, stdev, None, None))
    return results


def pos_based(sentences, window_size, punct_tags, name_tags, open_tags):
    """"""
    # TODO
    pass


def dependency_based(graphs):
    """"""
    results = []
    measures = [(dependency.average_dependency_distance, "average dependency distance"),
                (dependency.closeness_centrality, "closeness centrality"),
                (dependency.outdegree_centralization, "outdegree centralization"),
                (dependency.closeness_centralization, "closeness centralization"),
                (dependency.longest_shortest_path, "longest shortest path"),
                (dependency.dependents_per_word, "dependents per word")]
    for measure, name in measures:
        value, stdev = measure(graphs)
        results.append(Result(name, value, stdev, None, None))
    return results


def constituency_based(trees, lang):
    """"""
    results = []
    measures_with_length = [(constituency.t_units, "t-units"),
                            (constituency.complex_t_units, "complex t-units"),
                            (constituency.clauses, "clauses"),
                            (constituency.dependent_clauses, "dependent clauses"),
                            (constituency.nps, "noun phrases"),
                            (constituency.vps, "verb phrases"),
                            (constituency.pps, "prepositional phrases"),
                            (constituency.coordinate_phrases, "coordinate phrases")]
    measures_wo_length = [(constituency.constituents, "constituents"),
                          (constituency.constituents_wo_leaves, "non-terminal constituents"),
                          (constituency.height, "parse tree height")]
    if lang == "de_negra":
        for measure, name in measures_with_length:
            value, stdev, length, length_sd = measure(trees)
            results.append(Result(name, value, stdev, length, length_sd))
    for measure, name in measures_wo_length:
        value, stdev = measure(trees)
        results.append(Result(name, value, stdev, None, None))
    return results


def main():
    """"""
    args = arguments()
    if not any((args.sur, args.sent, args.dep, args.const)):
        args.sur = True
        args.sent = True
        args.dep = True
        args.const = True
    punct_tags = args.punct_tag
    if punct_tags is None:
        punct_tags = ["PUNCT"]
    punct_tags = set(punct_tags)
    all_results = {}
    for i, f in enumerate(args.TEXT):
        tokens, tagged, graphs, ps_trees = None, None, None, None
        if args.input_format == "conllu":
            tokens, tagged, graphs = zip(*conllu.read_conllu_sentences(f, ignore_punct=args.ignore_punct, punct_tags=punct_tags))
            tokens = list(itertools.chain.from_iterable(tokens))
        elif args.input_format == "tsv":
            tokens, tagged, graphs, ps_trees = zip(*custom_tsv.read_tsv_sentences(f, ignore_punct=args.ignore_punct, punct_tags=punct_tags))
            tokens = list(itertools.chain.from_iterable(tokens))
        results = []
        if args.sur and tokens is not None:
            results.extend(surface_based(tokens, args.window_size, args.all_measures))
        if args.sent and tagged is not None:
            results.extend(sentence_based(tagged, punct_tags))
        if args.dep and graphs is not None:
            results.extend(dependency_based(graphs))
        if args.const and ps_trees is not None:
            results.extend(constituency_based(ps_trees, args.lang))
        all_results[f.name] = {}
        for r in results:
            all_results[f.name][r.name] = {"value": r.value}
            if r.stdev is not None:
                all_results[f.name][r.name]["stdev"] = r.stdev
            if r.length is not None:
                all_results[f.name][r.name]["length"] = r.length
                all_results[f.name][r.name]["length stdev"] = r.length_stdev
        if args.output_format == "tsv":
            if i == 0:
                print("filename", end="\t")
                print("\t".join([r.name for r in results]))
            print(f.name, end="\t")
            print("\t".join([str(r.value) for r in results]))
    if args.output_format == "json":
        print(json.dumps(all_results, ensure_ascii=False, indent=4))
