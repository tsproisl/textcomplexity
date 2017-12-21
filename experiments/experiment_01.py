#!/usr/bin/env python3

import collections
import json
import os
import statistics

from complexity_measures import vocabulary_richness


def read_directory_gutenberg(directoryname, metadatafile, yearfile):
    tokens = {}
    author_title_to_year = collections.defaultdict(dict)
    ids = set()
    with open(yearfile) as f:
        next(f)
        for line in f:
            fields = line.rstrip().split("\t")
            author = fields[2]
            title = fields[3]
            if len(fields) == 8:
                year = fields[7]
                author_title_to_year[author][title] = int(year)
    with open(metadatafile) as f:
        next(f)
        for line in f:
            fields = line.rstrip().split("\t")
            author = fields[2]
            title = fields[3]
            if (author in author_title_to_year) and (title in author_title_to_year[author]) and (1789 <= author_title_to_year[author][title] <= 1914):
                ids.add(fields[0])
    for filename in os.listdir(directoryname):
        if not filename.endswith(".txt"):
            continue
        file_id, _ = filename.split(".", maxsplit=1)
        if file_id not in ids:
            continue
        with open(os.path.join(directoryname, filename)) as f:
            tokens[file_id] = [line.rstrip() for line in f if line != "\n"]
    return tokens


def run_experiment(tokens, measure, window_size):
    results = []
    for file_id in sorted(tokens.keys()):
        toks = tokens[file_id]
        results.extend(vocabulary_richness.bootstrap(toks, measure=measure, window_size=window_size, raw=True))
    return statistics.mean(results), vocabulary_richness._sttr_ci(results)


def run_mattr(tokens, window_size):
    results = []
    for file_id in sorted(tokens.keys()):
        toks = tokens[file_id]
        results.append(vocabulary_richness.mattr(toks, window_size=window_size))
    return statistics.mean(results), vocabulary_richness._sttr_ci(results)


def main():
    tokens = read_directory_gutenberg("/data/Thomas/Kallimachos/Gutenberg_ed13_tokenized",
                                      "/data/Thomas/Kallimachos/meta_gutenberg_ed13_native_speakers.csv",
                                      "experiment_01.d/Gutenberg_ed13_meta.csv")
    # measures = ["type_token_ratio", "guiraud_r", "herdan_c",
    #             "dugast_k", "maas_a2", "dugast_u", "tuldava_ln", "brunet_w",
    #             "cttr", "summer_s", "sichel_s", "michea_m", "honore_h",
    #             "herdan_vm", "orlov_z", "entropy", "yule_k", "simpson_d", "hdd",
    #             "mtld"]
    # No orlov_z:
    measures = ["type_token_ratio", "guiraud_r", "herdan_c",
                "dugast_k", "maas_a2", "dugast_u", "tuldava_ln",
                "brunet_w", "cttr", "summer_s", "sichel_s",
                "michea_m", "honore_h", "herdan_vm", "entropy",
                "yule_k", "simpson_d", "hdd", "mtld"]
    window_sizes = list(range(1000, 10001, 1000))
    results = {m: {w: None} for m in measures for w in window_sizes}
    # results["mattr"] = {w: None for w in window_sizes}
    for measure in measures:
        for window_size in window_sizes:
            print("Run %s, window size %d" % (measure, window_size))
            mean, ci = run_experiment(tokens, measure, window_size)
            results[measure][window_size] = (mean, ci)
    # for window_size in window_sizes:
    #     mean, ci = run_mattr(tokens, window_size)
    #     results["mattr"][window_size] = (mean, ci)
    with open("experiment_01.d/results.json", mode="w") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
