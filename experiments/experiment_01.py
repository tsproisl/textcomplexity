#!/usr/bin/env python3

import collections
import gzip
import json
import os
import regex as re
import statistics
import warnings

from textcomplexity import vocabulary_richness


def read_directory_gutenberg(directoryname, metadatafile, yearfile, filter_punctuation=False):
    tokens = {}
    author_title_to_year = collections.defaultdict(dict)
    ids = set()
    id_to_metadata = {}
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
                id_to_metadata[fields[0]] = {"author": author, "title": title, "year": author_title_to_year[author][title]}
    for filename in os.listdir(directoryname):
        if not filename.endswith(".txt"):
            continue
        file_id, _ = filename.split(".", maxsplit=1)
        if file_id not in ids:
            continue
        with open(os.path.join(directoryname, filename)) as f:
            local_tokens = [line.rstrip() for line in f if line != "\n"]
            if filter_punctuation:
                local_tokens = [token for token in local_tokens if not re.search(r"^\p{P}+$", token)]
            if len(local_tokens) >= 10000:
                tokens[file_id] = local_tokens
            else:
                warnings.warn("Skip %s (%d tokens)" % (filename, len(local_tokens)))
    return tokens, id_to_metadata


def read_directory_tagged_stemmed_lemmatized(directoryname, filter_punctuation=False):
    texts = {}
    authors = []
    tokens = {}
    filename_to_metadata = {}
    for filename in os.listdir(directoryname):
        if not filename.endswith(".txt.gz"):
            continue
        author, title = filename.split("_")
        filename_to_metadata[filename] = {"author": author, "title": title, "year": 0}
        with gzip.open(os.path.join(directoryname, filename), mode="rt") as f:
            local_tokens = [line.rstrip().split("\t")[0] for line in f if line != "\n"]
            if filter_punctuation:
                local_tokens = [token for token in local_tokens if not re.search(r"^\p{P}+$", token)]
            if len(local_tokens) >= 10000:
                tokens[filename] = local_tokens
            else:
                warnings.warn("Skip %s (%d tokens)" % (filename, len(local_tokens)))
    return tokens, filename_to_metadata


def run_experiment(tokens, measure, window_size):
    results = []
    per_file_results = []
    for file_id in sorted(tokens.keys()):
        toks = tokens[file_id]
        local_results = vocabulary_richness.bootstrap(toks, measure=measure, window_size=window_size, raw=True)
        results.extend(local_results)
        per_file_results.append(statistics.mean(local_results))
    return statistics.mean(results), vocabulary_richness._sttr_ci(results), per_file_results


def run_mattr(tokens, window_size):
    results = []
    for file_id in sorted(tokens.keys()):
        toks = tokens[file_id]
        results.append(vocabulary_richness.mattr(toks, window_size=window_size))
    return statistics.mean(results), vocabulary_richness._sttr_ci(results)


def create_tsv_file(filename, tokens, id_to_metadata, measures, window_sizes):
    with open(filename, mode="w") as f:
        f.write("\t".join(("fold_counter", "fold_size", "file_id", "author", "title", "year")))
        f.write("\t")
        f.write("\t".join(measures))
        f.write("\n")
        fold_counter = 0
        for file_id in sorted(tokens.keys()):
            toks = tokens[file_id]
            author = id_to_metadata[file_id]["author"]
            title = id_to_metadata[file_id]["title"]
            year = id_to_metadata[file_id]["year"]
            for window_size in window_sizes:
                per_ws_results = []
                for measure in measures:
                    local_results = vocabulary_richness.bootstrap(toks, measure=measure, window_size=window_size, raw=True)
                    per_ws_results.append(local_results)
                for per_fold_results in zip(*per_ws_results):
                    f.write("\t".join((str(fold_counter), str(window_size), file_id, author, title, str(year))))
                    f.write("\t")
                    f.write("\t".join((str(_) for _ in per_fold_results)))
                    f.write("\n")
                    fold_counter += 1


def main():
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

    # Gutenberg
    tokens, id_to_metadata = read_directory_gutenberg("/data/Thomas/Kallimachos/Gutenberg_ed13_tokenized",
                                                      "/data/Thomas/Kallimachos/meta_gutenberg_ed13_native_speakers.csv",
                                                      "experiment_01.d/Gutenberg_ed13_meta.csv")
    create_tsv_file("experiment_01.d/results_gutenberg.tsv", tokens, id_to_metadata, measures, window_sizes)

    # Gutenberg without punctuation
    tokens, id_to_metadata = read_directory_gutenberg("/data/Thomas/Kallimachos/Gutenberg_ed13_tokenized",
                                                      "/data/Thomas/Kallimachos/meta_gutenberg_ed13_native_speakers.csv",
                                                      "experiment_01.d/Gutenberg_ed13_meta.csv", filter_punctuation=True)
    create_tsv_file("experiment_01.d/results_gutenberg_no_punctuation.tsv", tokens, id_to_metadata, measures, window_sizes)

    # Delta DE
    tokens, id_to_metadata = read_directory_tagged_stemmed_lemmatized("/home/ccl/spthproi/Documents/Arbeit/kallimachos/authorship/data/corpus_DE_tagged_stemmed_lemmatized")
    create_tsv_file("experiment_01.d/results_delta_de.tsv", tokens, id_to_metadata, measures, window_sizes)

    # Delta DE without punctuation
    tokens, id_to_metadata = read_directory_tagged_stemmed_lemmatized("/home/ccl/spthproi/Documents/Arbeit/kallimachos/authorship/data/corpus_DE_tagged_stemmed_lemmatized", filter_punctuation=True)
    create_tsv_file("experiment_01.d/results_delta_de_no_punctuation.tsv", tokens, id_to_metadata, measures, window_sizes)

    # Delta EN
    tokens, id_to_metadata = read_directory_tagged_stemmed_lemmatized("/home/ccl/spthproi/Documents/Arbeit/kallimachos/authorship/data/corpus_EN_tagged_stemmed_lemmatized")
    create_tsv_file("experiment_01.d/results_delta_en.tsv", tokens, id_to_metadata, measures, window_sizes)

    # Delta EN without punctuation
    tokens, id_to_metadata = read_directory_tagged_stemmed_lemmatized("/home/ccl/spthproi/Documents/Arbeit/kallimachos/authorship/data/corpus_EN_tagged_stemmed_lemmatized", filter_punctuation=True)
    create_tsv_file("experiment_01.d/results_delta_en_no_punctuation.tsv", tokens, id_to_metadata, measures, window_sizes)

    # Delta FR
    tokens, id_to_metadata = read_directory_tagged_stemmed_lemmatized("/home/ccl/spthproi/Documents/Arbeit/kallimachos/authorship/data/corpus_FR_tagged_stemmed_lemmatized")
    create_tsv_file("experiment_01.d/results_delta_fr.tsv", tokens, id_to_metadata, measures, window_sizes)

    # Delta FR without punctuation
    tokens, id_to_metadata = read_directory_tagged_stemmed_lemmatized("/home/ccl/spthproi/Documents/Arbeit/kallimachos/authorship/data/corpus_FR_tagged_stemmed_lemmatized", filter_punctuation=True)
    create_tsv_file("experiment_01.d/results_delta_fr_no_punctuation.tsv", tokens, id_to_metadata, measures, window_sizes)

    # results = {m: {w: {} for w in window_sizes} for m in measures}
    # # results["mattr"] = {w: None for w in window_sizes}
    # for measure in measures:
    #     for window_size in window_sizes:
    #         print("Run %s, window size %d" % (measure, window_size))
    #         mean, ci, per_file_means = run_experiment(tokens, measure, window_size)
    #         results[measure][window_size]["mean"] = mean
    #         results[measure][window_size]["ci"] = ci
    #         results[measure][window_size]["per_file_means"] = per_file_means
    # # for window_size in window_sizes:
    # #     mean, ci = run_mattr(tokens, window_size)
    # #     results["mattr"][window_size] = (mean, ci)
    # with open("experiment_01.d/results.json", mode="w") as fh:
    #     json.dump(results, fh, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
