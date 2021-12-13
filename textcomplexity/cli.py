#!/usr/bin/env python3

import argparse
import collections
import functools
import itertools
import json
import os

from textcomplexity import surface, sentence, pos, dependency, constituency
from textcomplexity.text import Text
from textcomplexity.utils import conllu, custom_tsv, misc

Result = collections.namedtuple("Result", ["name", "value", "stdev", "length", "length_stdev"])


def arguments():
    presets = {"lexical_core": "type_token_ratio evenness gini_based_dispersion rarity lexical_density average_token_length".split(),
               "core": "sentence_length_tokens sentence_length_words punctuation_per_sentence average_dependency_distance closeness_centrality dependents_per_word".split(),
               "extended_core": "sichel_s honore_h simpson_d constituents_wo_leaves height t_units".split(),
               "all": ["all measures"]}
    parser = argparse.ArgumentParser(description="Compute a variety of linguistic and stylistic complexity measures.")
    parser.add_argument("--preset", choices=["lexical_core", "core", "extended_core", "all"], default="core", help="Predefined subset of measures to compute (default: core). lexical_core: {" + f"{', '.join(presets['lexical_core'])}" + "}; core: lexical_core + {" + f"{', '.join(presets['core'])}" + "}; extended_core: core + {" + f"{', '.join(presets['extended_core'])}" + "}; all: all measures")
    parser.add_argument("--all-measures", action="store_true", help="Compute ALL applicable complexity measures (instead of only a sensible subset)")
    parser.add_argument("--lang", choices=["de", "en", "other", "none"], default="none", help="Input language. Some complexity measures depend on language-specific part-of-speech tags (specified in the XPOS column of CoNLL-U files) or constituency parsing schemes. If you want to compute these measures for languages other than English or German, specify \"other\" and provide a language definition file via --lang-def. Default: none (i.e. only compute language-independent measures).")
    parser.add_argument("--lang-def", type=os.path.abspath, help="Language definition file in JSON format. Examples can be found in README.md")
    parser.add_argument("--ignore-punct", action="store_true", help="Ignore punctuation for surface-based and pos-based complexity measures (using the part-of-speech tags defined via --lang and --lang-def)")
    parser.add_argument("--ignore-case", action="store_true", help="Ignore case for surface-based and pos-based complexity measures")
    parser.add_argument("--window-size", default=1000, type=int, help="Window size for vocabulary-based complexity measures (default: 1000)")
    parser.add_argument("-i", "--input-format", choices=["conllu", "tsv"], required=True, help="Format of the input files.")
    parser.add_argument("-o", "--output-format", choices=["json", "tsv"], default="json", help="Format for outputting the results (default: json).")
    parser.add_argument("TEXT", type=argparse.FileType("r", encoding="utf-8"), nargs="+", help="Input files. Paths to files or \"-\" for STDIN. Input files need to be text files in CoNLL-U format or in our custom format with six tab-separated columns and an empty line after each sentence. Missing values can be replaced with an underscore (_). Examples for both input formats can be found in README.md")
    return parser.parse_args()


def surface_based(tokens, window_size, preset):
    """"""
    results = []
    gbd = functools.partial(surface.gini_based_dispersion, exclude_hapaxes=True)
    ebd = functools.partial(surface.evenness_based_dispersion, exclude_hapaxes=True)
    measures = [(surface.type_token_ratio, "type-token ratio", True, True, True),
                (surface.guiraud_r, "Guiraud's R", False, False, False),
                (surface.herdan_c, "Herdan's C", False, False, False),
                (surface.dugast_k, "Dugast's k", False, False, False),
                (surface.maas_a2, "Maas' a²", False, False, False),
                (surface.dugast_u, "Dugast's U", False, False, False),
                (surface.tuldava_ln, "Tuldava's LN", False, False, False),
                (surface.brunet_w, "Brunet's W", False, False, False),
                (surface.cttr, "CTTR", False, False, False),
                (surface.summer_s, "Summer's S", False, False, False),
                (surface.sichel_s, "Sichel's S", False, False, True),
                (surface.michea_m, "Michéa's M", False, False, False),
                (surface.honore_h, "Honoré's H", False, False, True),
                (surface.entropy, "entropy", False, False, False),
                (surface.evenness, "evenness", True, True, True),
                (surface.jarvis_evenness, "Jarvis's evenness", False, False, False),
                (surface.yule_k, "Yule's K", False, False, False),
                (surface.simpson_d, "Simpson's D", False, False, True),
                (surface.herdan_vm, "Herdan's Vm", False, False, False),
                (surface.hdd, "HD-D", False, False, False),
                (surface.average_token_length, "average token length", True, True, True),
                (surface.orlov_z, "Orlov's Z", False, False, False),
                (gbd, "Gini-based dispersion", True, True, True),
                (ebd, "evenness-based dispersion", True, True, True),
                ]
    for measure, name, lexical_core, core, extended_core in measures:
        if (preset == "lexical_core" and lexical_core) or (preset == "core" and core) or (preset == "extended_core" and extended_core) or (preset == "all"):
            name += " (disjoint windows)"
            mean, stdev, _ = misc.bootstrap(measure, tokens, window_size, strategy="spread")
            results.append(Result(name, mean, stdev, None, None))
    if preset == "all":
        text = Text.from_tokens(tokens)
        mattr = surface.mattr(text, window_size)
        results.append(Result("type-token ratio (moving windows)", mattr, None, None, None))
        mtld = surface.mtld(text)
        results.append(Result("MTLD", mtld, None, None, None))
    return results


def sentence_based(sentences, punct_tags, preset):
    """"""
    results = []
    pps = functools.partial(sentence.punctuation_per_sentence, punctuation=punct_tags)
    ppt = functools.partial(sentence.punctuation_per_token, punctuation=punct_tags)
    slw = functools.partial(sentence.sentence_length_words, punctuation=punct_tags)
    measures_with_punct = [(slw, "average sentence length (words)", False, True, True),
                           (pps, "punctuation per sentence", False, True, True)]
    measures_wo_punct = [(sentence.sentence_length_tokens, "average sentence length (tokens)", False, True, True),
                         (sentence.sentence_length_characters, "average sentence length (characters)", False, False, False)]
    if punct_tags:
        measures = measures_with_punct + measures_wo_punct
        if preset == "all":
            results.append(Result("punctuation per token", ppt(sentences), None, None, None))
    else:
        measures = measures_wo_punct
    for measure, name, lexical_core, core, extended_core in measures:
        if (preset == "lexical_core" and lexical_core) or (preset == "core" and core) or (preset == "extended_core" and extended_core) or (preset == "all"):
            value, stdev = measure(sentences)
            results.append(Result(name, value, stdev, None, None))
    return results


def pos_based(tokens, punct_tags, name_tags, open_tags, reference_frequency_list, preset):
    """"""
    results = []
    lexd = functools.partial(pos.lexical_density, open_tags=open_tags)
    rar = functools.partial(pos.rarity, reference_frequency_list=reference_frequency_list, open_tags_ex_names=(open_tags - name_tags))
    measures = []
    if open_tags:
        measures.append((lexd, "lexical density", True, True, True))
    if reference_frequency_list:
        measures.append((rar, "rarity", True, True, True))
    text = Text.from_tokens(tokens)
    for measure, name, lexical_core, core, extended_core in measures:
        if (preset == "lexical_core" and lexical_core) or (preset == "core" and core) or (preset == "extended_core" and extended_core) or (preset == "all"):
            results.append(Result(name, measure(text), None, None, None))
    return results


def dependency_based(graphs, preset):
    """"""
    results = []
    measures = [(dependency.average_dependency_distance, "average dependency distance", False, True, True),
                (dependency.closeness_centrality, "closeness centrality", False, True, True),
                (dependency.outdegree_centralization, "outdegree centralization", False, False, False),
                (dependency.closeness_centralization, "closeness centralization", False, False, False),
                (dependency.longest_shortest_path, "longest shortest path", False, False, False),
                (dependency.dependents_per_word, "dependents per word", False, True, True)]
    for measure, name, lexical_core, core, extended_core in measures:
        if (preset == "lexical_core" and lexical_core) or (preset == "core" and core) or (preset == "extended_core" and extended_core) or (preset == "all"):
            value, stdev = measure(graphs)
            results.append(Result(name, value, stdev, None, None))
    return results


def constituency_based(trees, de_negra, preset):
    """"""
    results = []
    measures_with_length = [(constituency.t_units, "t-units", False, False, True),
                            (constituency.complex_t_units, "complex t-units", False, False, False),
                            (constituency.clauses, "clauses", False, False, False),
                            (constituency.dependent_clauses, "dependent clauses", False, False, False),
                            (constituency.nps, "noun phrases", False, False, False),
                            (constituency.vps, "verb phrases", False, False, False),
                            (constituency.pps, "prepositional phrases", False, False, False),
                            (constituency.coordinate_phrases, "coordinate phrases", False, False, False)]
    measures_wo_length = [(constituency.constituents, "constituents", False, False, False),
                          (constituency.constituents_wo_leaves, "non-terminal constituents", False, False, True),
                          (constituency.height, "parse tree height", False, False, True)]
    if de_negra:
        for measure, name, lexical_core, core, extended_core in measures_with_length:
            if (preset == "lexical_core" and lexical_core) or (preset == "core" and core) or (preset == "extended_core" and extended_core) or (preset == "all"):
                value, stdev, length, length_sd = measure(trees)
                results.append(Result(name, value, stdev, length, length_sd))
    for measure, name, lexical_core, core, extended_core in measures_wo_length:
        if (preset == "lexical_core" and lexical_core) or (preset == "core" and core) or (preset == "extended_core" and extended_core) or (preset == "all"):
            value, stdev = measure(trees)
            results.append(Result(name, value, stdev, None, None))
    return results


def read_language_definition(filename):
    """"""
    with open(filename, encoding="utf-8") as f:
        ld = json.load(f)
    return ld["language"], set(ld["punctuation"]), set(ld["proper_names"]), set(ld["open_classes"]), set([(t, f) for t, f in ld["most_common"]])


def main():
    """"""
    args = arguments()
    language, punct_tags, name_tags, open_tags, reference_frequency_list = "none", set(), set(), set(), set()
    if args.lang == "de":
        language, punct_tags, name_tags, open_tags, reference_frequency_list = read_language_definition(os.path.join(os.path.dirname(os.path.abspath(__file__)), "de.json"))
    elif args.lang == "en":
        language, punct_tags, name_tags, open_tags, reference_frequency_list = read_language_definition(os.path.join(os.path.dirname(os.path.abspath(__file__)), "en.json"))
    elif args.lang == "other":
        assert args.lang_def is not None, "If you set --lang=other, then you must provide a language definition file via --lang-def"
        language, punct_tags, name_tags, open_tags, reference_frequency_list = read_language_definition(args.lang_def)
    if args.ignore_case:
        reference_frequency_list = set([(w.lower(), t) for w, t in reference_frequency_list])
    if args.ignore_punct:
        assert args.lang != "none", "You can only use --ignore-punct if you specify the input language via --lang (and --lang-def, if necessary)"
        assert punct_tags, "You can only use --ignore-punct if you specify a list of part-of-speech tags that indicate punctuation"
    all_results = {}
    for i, f in enumerate(args.TEXT):
        tokens, sentences, graphs, ps_trees = None, None, None, None
        if args.input_format == "conllu":
            sentences, graphs = zip(*conllu.read_conllu_sentences(f, ignore_case=args.ignore_case))
            tokens = list(itertools.chain.from_iterable(sentences))
        elif args.input_format == "tsv":
            sentences, graphs, ps_trees = zip(*custom_tsv.read_tsv_sentences(f, ignore_case=args.ignore_case))
            tokens = list(itertools.chain.from_iterable(sentences))
        if args.ignore_punct and tokens is not None:
            tokens = [t for t in tokens if t.pos not in punct_tags]
        results = []
        results.extend(surface_based(tokens, args.window_size, args.preset))
        results.extend(pos_based(tokens, punct_tags, name_tags, open_tags, reference_frequency_list, args.preset))
        results.extend(sentence_based(sentences, punct_tags, args.preset))
        results.extend(dependency_based(graphs, args.preset))
        if ps_trees is not None:
            # We assume that German constituency trees follow the
            # NEGRA parsing scheme
            de_negra = args.lang == "de"
            results.extend(constituency_based(ps_trees, de_negra, args.preset))
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
